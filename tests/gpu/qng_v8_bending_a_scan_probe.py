"""Pulse-amplitude scan (A-scan) at fixed (k=3pi/4, b=6).

Pre-registration: QNG-GPU-021 (DER-QNG-046 promotion sub-item 2a).

Purpose
-------
The k-scan (audit qng-v8-bending-k-scan-v1) showed that at b=6
(out-of-core) the bending magnitude recovers in eikonal limit but the
SIGN disagrees with the scalar DER-QNG-046 prediction across all k.
This A-scan tests three candidate mechanisms by their pulse-amplitude
scaling:

  H1: O(A^2) back-reaction        -> slope ~ 2 in log|alpha_resid| vs log(A)
  H2: linear amplitude/kinetic    -> slope ~ 1
  H3: mixed                       -> slope in [1.3, 1.7] or low R^2
  H4: sign flip across A range    -> VOID

Protocol identical to qng_v8_bending_k_scan_probe.py except we fix
k=3pi/4, b=6 and scan A in {0.025, 0.050, 0.100}.

Optimization: ring-bg evolution is A-independent so it is run once
and reused.

VERDICT
-------
  slope in [1.7, 2.3] AND R^2 > 0.95 -> H1 back-reaction
  slope in [0.7, 1.3] AND R^2 > 0.95 -> H2 linear/kinetic
  slope in [1.3, 1.7] OR  R^2 < 0.95 -> H3 mixed
  sign(alpha_meas) flips across A    -> H4 VOID
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    SIGMA_M_REF, BETA_PHI, MU_PHI, G_V_COUPLE, K_BACK, CHI_DECAY_V7,
    build_nb, make_state, yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
C_PHI_SQ = float(BETA_PHI) / (6.0 * float(MU_PHI))
C_PHI    = float(np.sqrt(C_PHI_SQ))


def make_coords(L):
    N = L * L * L
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def inject_pulse(state, xc, yc, zc, x0, y0, z0, sigma, k, A):
    omega = C_PHI * k
    env = cp.exp(-(((xc - x0) ** 2 + (yc - y0) ** 2 + (zc - z0) ** 2)
                   / (2.0 * sigma ** 2)))
    cos_part = cp.cos(k * (xc - x0))
    sin_part = cp.sin(k * (xc - x0))
    state['phi'] = state['phi'] + A * env * cos_part
    state['pi_phi'] = state['pi_phi'] - MU_PHI * omega * A * env * sin_part


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def evolve_record_plane(state, nb_idx, T, det_idx_array, sample_every,
                        verbose=False, label=''):
    n = int(T / DT)
    t_rec = []
    phi_rec = []
    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_rec.append(s * DT)
            phi_rec.append(cp.asnumpy(state['phi'][det_idx_array]))
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    t_rec.append(n * DT)
    phi_rec.append(cp.asnumpy(state['phi'][det_idx_array]))
    if verbose:
        print(f"    evolved {label}: {n} steps ({time.time()-t0:.1f}s)", flush=True)
    return np.array(t_rec), np.array(phi_rec)


def centroid_y(phi_plane, y_coords):
    w = phi_plane ** 2
    s = w.sum()
    if s < 1e-20:
        return float('nan')
    return float((y_coords * w).sum() / s)


def find_arrival_time(t, phi_plane, y_coords, y_expected):
    intensity = np.sqrt((phi_plane ** 2).sum(axis=1))
    window = 3
    smoothed = np.convolve(intensity, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(smoothed))
    return i_peak, float(t[i_peak]), float(smoothed[i_peak])


def scalar_alpha_prediction(k_pkt, b, ring_state, L, R, x_src, x_det,
                            y_c, z_c):
    """DER-QNG-046 scalar prediction (A-independent — sanity check).

    alpha_scalar = -(g / (2 mu_phi omega^2)) *
                    integral Delta(x, y_c+b, z_c) * d_y Delta(x, y_c+b, z_c) dx

    where Delta = SIGMA_M_REF - sigma_m.
    """
    sm = cp.asnumpy(ring_state['sm']).reshape(L, L, L)
    delta = SIGMA_M_REF - sm
    y_path = int(round(y_c + b))
    xs = np.arange(int(x_src), int(x_det) + 1)
    delta_plus = delta[xs, (y_path + 1) % L, int(z_c)]
    delta_minus = delta[xs, (y_path - 1) % L, int(z_c)]
    dy_delta = 0.5 * (delta_plus - delta_minus)
    delta_on_path = delta[xs, y_path, int(z_c)]
    integrand = delta_on_path * dy_delta
    I = float(np.trapz(integrand, xs.astype(float)))
    omega = C_PHI * k_pkt
    alpha = -(float(G_V_COUPLE) / (2.0 * float(MU_PHI) * omega * omega)) * I
    return alpha


def main():
    print("=" * 80)
    print("QNG-GPU-021: A-SCAN at fixed (k=3pi/4, b=6)")
    print("  Discriminate O(A^2) back-reaction vs linear amplitude/kinetic")
    print("=" * 80)

    L = 28
    R = 4
    T_track = 250.0
    DT_sample = 1.0
    sample_every = int(DT_sample / DT)

    x_source = 4.0
    x_detect = L - 4.0
    path_len = x_detect - x_source
    z_line   = 0.5 * L
    sigma_pkt = 2.0

    y_center = 0.5 * L
    xd_int = int(round(x_detect))
    zd_int = int(round(z_line))

    # FIXED parameters (committed pre-run)
    k_pkt = float(3.0 * np.pi / 4.0)
    b = 6
    A_list = [0.025, 0.050, 0.100]

    lam = 2.0 * np.pi / k_pkt
    omega = C_PHI * k_pkt

    xc, yc, zc = make_coords(L)

    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  c_phi = {C_PHI:.5f}   (c_phi^2 = BETA_PHI/(6 mu_phi))")
    print(f"  Source x={x_source}  Detect x={x_detect}  path={path_len:.1f}")
    print(f"  Pulse: sigma={sigma_pkt}  k={k_pkt:.4f}  lambda={lam:.2f}  omega={omega:.4f}")
    print(f"  b = {b}  (FIXED, out-of-core)")
    print(f"  A_list = {A_list}")
    print()

    # Load cached ring
    print("[0] Load cached ring L=28 R=4")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    ring loaded, M_ring = {M_ring0:.2f}")
    print()

    # Detector setup
    y_pulse = y_center + b
    y_det_list = np.arange(int(round(y_pulse)) - 7,
                           int(round(y_pulse)) + 8)
    y_det_list = y_det_list % L
    y_det_float = y_det_list.astype(float)
    det_idx = xd_int + y_det_list * L + zd_int * L * L
    det_idx_cp = cp.asarray(det_idx)

    # Scalar prediction is A-independent — compute once
    alpha_scalar_th = scalar_alpha_prediction(k_pkt, b, ring_state, L, R,
                                               x_source, x_detect,
                                               y_center, z_line)
    print(f"[scalar] alpha_scalar_th = {alpha_scalar_th:+.4e}  (A-independent)")
    print()

    # Ring-bg evolution: A-independent, run ONCE and reuse
    print("[bg] Ring-only background evolution (A-independent, single run)")
    s_bg = clone_state(ring_state)
    _, phi_bg = evolve_record_plane(s_bg, nb_idx, T_track,
                                     det_idx_cp, sample_every,
                                     verbose=True,
                                     label=f'bg b={b}')
    print()

    # Per-A scan
    results = []
    for A_pkt in A_list:
        print(f"=== A = {A_pkt:.4f} ===")

        # Vacuum run (A-dependent because pulse amplitude scales linearly)
        vac_state = make_state(L, phi_init=None)
        inject_pulse(vac_state, xc, yc, zc, x_source, y_pulse, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        t_vac, phi_vac = evolve_record_plane(vac_state, nb_idx, T_track,
                                             det_idx_cp, sample_every,
                                             verbose=True,
                                             label=f'vac A={A_pkt:.3f}')
        ip_vac, tp_vac, amp_vac = find_arrival_time(t_vac, phi_vac,
                                                     y_det_float, y_pulse)
        yc_vac = centroid_y(phi_vac[ip_vac], y_det_float)
        print(f"      vac  peak t={tp_vac:.2f}  amp={amp_vac:.4f}  y_c={yc_vac:.4f}")

        # Ring + pulse
        s_rp = clone_state(ring_state)
        inject_pulse(s_rp, xc, yc, zc, x_source, y_pulse, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        t_rp, phi_rp = evolve_record_plane(s_rp, nb_idx, T_track,
                                            det_idx_cp, sample_every,
                                            verbose=True,
                                            label=f'r+p A={A_pkt:.3f}')

        phi_pulse_ring = phi_rp - phi_bg
        ip_r, tp_r, amp_r = find_arrival_time(t_rp, phi_pulse_ring,
                                               y_det_float, y_pulse)
        yc_ring = centroid_y(phi_pulse_ring[ip_r], y_det_float)

        Dy = yc_ring - yc_vac
        alpha_meas = Dy / path_len

        # Scalar prediction at THIS A — should equal alpha_scalar_th
        # (it is A-independent by construction; we keep one number)
        alpha_resid = alpha_meas - alpha_scalar_th

        print(f"      ring peak t={tp_r:.2f}  amp={amp_r:.4f}  y_c={yc_ring:.4f}")
        print(f"      Dy={Dy:+.4f}  alpha_meas={alpha_meas:+.4e}  "
              f"alpha_resid={alpha_resid:+.4e}")
        print()

        results.append({
            'A': A_pkt,
            'tp_vac': tp_vac, 'amp_vac': amp_vac, 'yc_vac': yc_vac,
            'tp_ring': tp_r, 'amp_ring': amp_r, 'yc_ring': yc_ring,
            'Dy': Dy,
            'alpha_meas': alpha_meas,
            'alpha_scalar_th': alpha_scalar_th,
            'alpha_resid': alpha_resid,
        })

    # --- Slope analysis ---
    print("=" * 90)
    print("A-SCAN BENDING RESULTS")
    print("=" * 90)
    print(f"{'A':>8} {'alpha_meas':>15} {'alpha_resid':>15} "
          f"{'sign':>6}")
    print("-" * 90)
    for r in results:
        sgn = '+' if r['alpha_meas'] > 0 else '-'
        print(f"{r['A']:>8.4f} {r['alpha_meas']:>+15.4e} "
              f"{r['alpha_resid']:>+15.4e} {sgn:>6}")
    print()

    # H4 check first
    signs = [np.sign(r['alpha_meas']) for r in results]
    if not (all(s > 0 for s in signs) or all(s < 0 for s in signs)):
        verdict = 'H4_VOID_SIGN_FLIP'
        slope = float('nan')
        r2 = float('nan')
        print(f"VERDICT: {verdict} — sign(alpha_meas) flips across A range")
    else:
        # Log-log fit on |alpha_resid|
        A_arr = np.array([r['A'] for r in results])
        a_resid_arr = np.array([abs(r['alpha_resid']) for r in results])
        log_A = np.log(A_arr)
        log_a = np.log(a_resid_arr)
        # least-squares slope
        slope, intercept = np.polyfit(log_A, log_a, 1)
        # R^2
        a_pred = slope * log_A + intercept
        ss_res = np.sum((log_a - a_pred) ** 2)
        ss_tot = np.sum((log_a - log_a.mean()) ** 2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')

        print(f"  Log-log fit: slope = {slope:+.3f}   R^2 = {r2:.4f}")

        if r2 < 0.95:
            verdict = 'H3_MIXED_LOW_R2'
        elif 1.7 <= slope <= 2.3:
            verdict = 'H1_BACK_REACTION'
        elif 0.7 <= slope <= 1.3:
            verdict = 'H2_LINEAR_KINETIC'
        elif 1.3 < slope < 1.7:
            verdict = 'H3_MIXED'
        else:
            verdict = f'H3_UNUSUAL_SLOPE_{slope:+.2f}'

        print(f"VERDICT: {verdict}")

    print()
    print("=" * 90)
    print("HYPOTHESIS EVALUATION")
    print("=" * 90)
    print("  H1 (back-reaction O(A^2)): slope in [1.7, 2.3], R^2 > 0.95")
    print("  H2 (linear/kinetic mode):  slope in [0.7, 1.3], R^2 > 0.95")
    print("  H3 (mixed/saturated):      slope in [1.3, 1.7] or R^2 < 0.95")
    print("  H4 (VOID):                 sign(alpha_meas) flips")

    # Save
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-bending-a-scan-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'T_track': T_track, 'c_phi': C_PHI,
        'path_len': path_len,
        'k_pkt': k_pkt, 'b': b,
        'A_list': A_list,
        'M_ring': M_ring0,
        'alpha_scalar_th': alpha_scalar_th,
        'results': results,
        'slope_log_log': float(slope) if 'slope' in dir() else float('nan'),
        'R_squared': float(r2) if 'r2' in dir() else float('nan'),
        'verdict': verdict,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
