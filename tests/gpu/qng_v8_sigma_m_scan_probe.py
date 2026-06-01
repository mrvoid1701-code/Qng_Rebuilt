"""sigma_m-deficit scan at fixed (k=3pi/4, b=6, A=0.05).

Pre-registration: QNG-GPU-022 (DER-QNG-046 promotion sub-item 2b).

Purpose
-------
A-scan (QNG-GPU-021) ruled out O(A^2) back-reaction (H1) and linear
kinetic-mode coupling (H2) as the b>R bending residual source:
alpha_resid was measured A-independent. Two candidates survive:

  H_tensorial: DER-QNG-046 sections 1-4 full tensorial EOM
               -> alpha_resid scales as s^2  (slope = 2)
  H_path     : path-curvature feedback on scalar section 13
               -> alpha_resid scales as s^4  (slope = 4)
  H_mixed    : slope in (2, 4)
  H_VOID     : sign flip or noise

Scaling protocol: rescale cached ring deficit
  sigma_m -> SIGMA_M_REF - s*(SIGMA_M_REF - sigma_m)
while keeping other fields unchanged. This scales Delta(x) -> s*Delta(x).

Subtraction (phi_pulse = phi_rp - phi_bg) cancels ring relaxation
dynamics that common to bg and r+p runs.

VERDICT
-------
  slope in [1.7, 2.3] AND R^2 > 0.95  -> H_tensorial
  slope in [3.7, 4.3] AND R^2 > 0.95  -> H_path
  slope in [2.3, 3.7]                 -> H_mixed
  R^2 < 0.95                          -> H_mixed_noisy
  sign(alpha_resid) flips             -> H_VOID
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


def scale_deficit(state, s):
    """In-place: sigma_m -> SIGMA_M_REF - s*(SIGMA_M_REF - sigma_m)."""
    state['sm'] = SIGMA_M_REF - s * (SIGMA_M_REF - state['sm'])
    return state


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
    """DER-QNG-046 scalar prediction on the CURRENT (possibly scaled)
    ring state."""
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
    print("QNG-GPU-022: sigma_m-SCAN at fixed (k=3pi/4, b=6, A=0.05)")
    print("  Discriminate tensorial section 1-4 (slope=2) vs path-curvature (slope=4)")
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
    A_pkt = 0.050
    s_list = [0.7, 1.0, 1.4]

    lam = 2.0 * np.pi / k_pkt
    omega = C_PHI * k_pkt

    xc, yc, zc = make_coords(L)

    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  c_phi = {C_PHI:.5f}   (c_phi^2 = BETA_PHI/(6 mu_phi))")
    print(f"  Source x={x_source}  Detect x={x_detect}  path={path_len:.1f}")
    print(f"  Pulse: sigma={sigma_pkt}  k={k_pkt:.4f}  lambda={lam:.2f}  "
          f"omega={omega:.4f}  A={A_pkt}")
    print(f"  b = {b}  (FIXED, out-of-core)")
    print(f"  s_list = {s_list}  (deficit scaling)")
    print()

    # Load cached ring
    print("[0] Load cached ring L=28 R=4")
    ring_state_base, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                                verbose=True)
    M_ring0 = float(ring_mass_deficit(ring_state_base['sm']))
    print(f"    ring loaded, M_ring_base = {M_ring0:.2f}")
    print()

    # Detector setup
    y_pulse = y_center + b
    y_det_list = np.arange(int(round(y_pulse)) - 7,
                           int(round(y_pulse)) + 8)
    y_det_list = y_det_list % L
    y_det_float = y_det_list.astype(float)
    det_idx = xd_int + y_det_list * L + zd_int * L * L
    det_idx_cp = cp.asarray(det_idx)

    # Vacuum run - s-independent, run ONCE and reuse
    print("[vac] Vacuum-only run (s-independent, single run)")
    vac_state = make_state(L, phi_init=None)
    inject_pulse(vac_state, xc, yc, zc, x_source, y_pulse, z_line,
                 sigma_pkt, k_pkt, A_pkt)
    t_vac, phi_vac = evolve_record_plane(vac_state, nb_idx, T_track,
                                         det_idx_cp, sample_every,
                                         verbose=True, label='vac')
    ip_vac, tp_vac, amp_vac = find_arrival_time(t_vac, phi_vac,
                                                 y_det_float, y_pulse)
    yc_vac = centroid_y(phi_vac[ip_vac], y_det_float)
    print(f"      vac  peak t={tp_vac:.2f}  amp={amp_vac:.4f}  y_c={yc_vac:.4f}")
    print()

    # Scalar prediction at s=1 (sanity reference)
    alpha_scalar_s1 = scalar_alpha_prediction(k_pkt, b, ring_state_base,
                                               L, R, x_source, x_detect,
                                               y_center, z_line)
    print(f"[scalar ref] alpha_scalar_th(s=1) = {alpha_scalar_s1:+.4e}")
    print()

    # Per-s scan
    results = []
    for s_scale in s_list:
        print(f"=== s = {s_scale:.2f} ===")

        # Scale the ring deficit, keep nb_idx (geometry unchanged)
        ring_state_s = clone_state(ring_state_base)
        scale_deficit(ring_state_s, s_scale)
        M_ring_s = float(ring_mass_deficit(ring_state_s['sm']))
        print(f"      M_ring(s={s_scale}) = {M_ring_s:.2f}  "
              f"(ratio {M_ring_s/M_ring0:.3f})")

        # Scalar prediction on SCALED ring
        alpha_scalar_s = scalar_alpha_prediction(k_pkt, b, ring_state_s,
                                                  L, R, x_source, x_detect,
                                                  y_center, z_line)
        # Algebraic sanity: alpha_scalar ~ s^2 * alpha_scalar_s1
        expected_s2 = s_scale ** 2
        scalar_ratio = alpha_scalar_s / alpha_scalar_s1 if abs(alpha_scalar_s1) > 1e-20 else float('nan')
        dev = abs(scalar_ratio - expected_s2) / max(expected_s2, 1e-12)
        print(f"      alpha_scalar_th(s) = {alpha_scalar_s:+.4e}  "
              f"(ratio vs s=1: {scalar_ratio:.4f}  expected {expected_s2:.4f}  dev {dev*100:.2f}%)")

        # Ring-only bg evolution (s-dependent due to scaled ring)
        s_bg = clone_state(ring_state_s)
        _, phi_bg = evolve_record_plane(s_bg, nb_idx, T_track,
                                         det_idx_cp, sample_every,
                                         verbose=True,
                                         label=f'bg s={s_scale:.2f}')

        # Ring + pulse
        s_rp = clone_state(ring_state_s)
        inject_pulse(s_rp, xc, yc, zc, x_source, y_pulse, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        t_rp, phi_rp = evolve_record_plane(s_rp, nb_idx, T_track,
                                            det_idx_cp, sample_every,
                                            verbose=True,
                                            label=f'r+p s={s_scale:.2f}')

        phi_pulse_ring = phi_rp - phi_bg
        ip_r, tp_r, amp_r = find_arrival_time(t_rp, phi_pulse_ring,
                                               y_det_float, y_pulse)
        yc_ring = centroid_y(phi_pulse_ring[ip_r], y_det_float)

        Dy = yc_ring - yc_vac
        alpha_meas = Dy / path_len
        alpha_resid = alpha_meas - alpha_scalar_s

        print(f"      ring peak t={tp_r:.2f}  amp={amp_r:.4f}  y_c={yc_ring:.4f}")
        print(f"      Dy={Dy:+.4f}  alpha_meas={alpha_meas:+.4e}  "
              f"alpha_resid={alpha_resid:+.4e}")
        print()

        results.append({
            's': s_scale,
            'M_ring': M_ring_s,
            'alpha_scalar_th': alpha_scalar_s,
            'scalar_s2_deviation': dev,
            'tp_vac': tp_vac, 'amp_vac': amp_vac, 'yc_vac': yc_vac,
            'tp_ring': tp_r, 'amp_ring': amp_r, 'yc_ring': yc_ring,
            'Dy': Dy,
            'alpha_meas': alpha_meas,
            'alpha_resid': alpha_resid,
        })

    # --- Slope analysis ---
    print("=" * 90)
    print("sigma_m-SCAN BENDING RESULTS")
    print("=" * 90)
    print(f"{'s':>6} {'M_ring':>10} {'alpha_scalar':>15} {'alpha_meas':>15} "
          f"{'alpha_resid':>15}")
    print("-" * 90)
    for r in results:
        print(f"{r['s']:>6.2f} {r['M_ring']:>10.2f} "
              f"{r['alpha_scalar_th']:>+15.4e} "
              f"{r['alpha_meas']:>+15.4e} {r['alpha_resid']:>+15.4e}")
    print()

    # Algebraic sanity across scan
    max_dev = max(r['scalar_s2_deviation'] for r in results if r['s'] != 1.0)
    print(f"  scalar s^2 sanity: max deviation = {max_dev*100:.2f}%  "
          f"(spec: <1%)")

    if max_dev > 0.01:
        verdict = 'VOID_SCALAR_S2_SANITY'
        slope = float('nan')
        r2 = float('nan')
        print(f"VERDICT: {verdict} - algebraic sanity failed")
    else:
        # H_VOID: sign flip check on alpha_resid
        signs = [np.sign(r['alpha_resid']) for r in results]
        if not (all(x > 0 for x in signs) or all(x < 0 for x in signs)):
            verdict = 'H_VOID_SIGN_FLIP'
            slope = float('nan')
            r2 = float('nan')
            print(f"VERDICT: {verdict} - sign(alpha_resid) flips across s range")
        else:
            # Log-log fit on |alpha_resid|
            s_arr = np.array([r['s'] for r in results])
            a_resid_arr = np.array([abs(r['alpha_resid']) for r in results])
            log_s = np.log(s_arr)
            log_a = np.log(a_resid_arr)
            slope, intercept = np.polyfit(log_s, log_a, 1)
            a_pred = slope * log_s + intercept
            ss_res = np.sum((log_a - a_pred) ** 2)
            ss_tot = np.sum((log_a - log_a.mean()) ** 2)
            r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')

            print(f"  Log-log fit: slope = {slope:+.3f}   R^2 = {r2:.4f}")

            if r2 < 0.95:
                verdict = 'H_MIXED_NOISY_LOW_R2'
            elif 1.7 <= slope <= 2.3:
                verdict = 'H_TENSORIAL'
            elif 3.7 <= slope <= 4.3:
                verdict = 'H_PATH_CURVATURE'
            elif 2.3 < slope < 3.7:
                verdict = 'H_MIXED'
            else:
                verdict = f'H_UNUSUAL_SLOPE_{slope:+.2f}'

            print(f"VERDICT: {verdict}")

    print()
    print("=" * 90)
    print("HYPOTHESIS EVALUATION")
    print("=" * 90)
    print("  H_tensorial (section 1-4 EOM):    slope in [1.7, 2.3], R^2 > 0.95")
    print("  H_path (path-curvature feedback): slope in [3.7, 4.3], R^2 > 0.95")
    print("  H_mixed:                          slope in [2.3, 3.7]")
    print("  H_mixed_noisy:                    R^2 < 0.95")
    print("  H_VOID:                           sign(alpha_resid) flips")

    # Save
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-sigma-m-scan-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'T_track': T_track, 'c_phi': C_PHI,
        'path_len': path_len,
        'k_pkt': k_pkt, 'b': b, 'A_pkt': A_pkt,
        's_list': s_list,
        'M_ring_base': M_ring0,
        'alpha_scalar_s1_ref': alpha_scalar_s1,
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
