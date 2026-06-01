"""Short-wavelength bending probe (Einstein test #3, k-scan variant).

Purpose
-------
Test whether the 100x gap between the scalar DER-QNG-045 prediction
(alpha ~ 10 rad) and the measured alpha ~ 1e-2 rad in CPU-078 /
DER-QNG-044 Test 3f is explained by EIKONAL BREAKDOWN.

Reasoning:
  - Test 3f baseline: k_pkt = pi/4 -> lambda = 8 lu, ring R = 4 lu.
    lambda > R, so pulse is in diffraction regime, not geometric
    optics. The scalar prediction assumes eikonal, so the 100x gap may
    simply reflect that the scalar formula is outside its domain.
  - DER-QNG-046 scalar prediction scales as 1/omega^2 = 1/(c_phi*k)^2.
    Doubling k divides predicted alpha by ~4.
  - Eikonal test:
      k = pi/4   (lambda = 8 > R)  <- baseline; scalar prediction fails
      k = pi/2   (lambda = 4 ~ R)  <- boundary regime
      k = 3pi/4  (lambda ~ 2.7 < R) <- geometric optics should hold

  HYPOTHESIS EIKONAL: as k grows, measured alpha -> scalar prediction.
  HYPOTHESIS REAL PHYSICS: measured alpha stays O(1e-2) irrespective
    of k (gap is not diffraction).

Protocol: identical to qng_v8_bending_probe.py except we scan k.

VERDICT
-------
  alpha(k=pi/2)  / alpha_scalar_th(k=pi/2)  in (0.5, 2.0)?  eikonal OK
  alpha(k=3pi/4) / alpha_scalar_th(k=3pi/4) in (0.5, 2.0)?  eikonal OK
  Both NO -> gap is real physics (amplitude modulation or back-react)
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
    """DER-QNG-046 scalar prediction (no cos(phi_bg) cancellation assumed,
    because CPU-080 showed the ring has no 2pi winding).

    alpha_scalar = -(g / (2 mu_phi omega^2)) *
                    integral Delta(x, y_c+b, z_c) * d_y Delta(x, y_c+b, z_c) dx

    where Delta = SIGMA_M_REF - sigma_m.
    """
    sm = cp.asnumpy(ring_state['sm']).reshape(L, L, L)
    delta = SIGMA_M_REF - sm
    y_path = int(round(y_c + b))
    xs = np.arange(int(x_src), int(x_det) + 1)
    # d_y Delta along path
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
    print("Einstein test #3 (k-scan): BENDING vs EIKONAL REGIME")
    print("  Tests whether 100x alpha gap (Test 3f) is diffraction")
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
    A_pkt     = 0.05

    y_center = 0.5 * L
    xd_int = int(round(x_detect))
    zd_int = int(round(z_line))

    # Parameter grid
    k_list = [float(np.pi / 4.0),
              float(np.pi / 2.0),
              float(3.0 * np.pi / 4.0)]
    b_list = [4, 6]

    xc, yc, zc = make_coords(L)

    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  c_phi = {C_PHI:.5f}   (c_phi^2 = BETA_PHI/(6 mu_phi))")
    print(f"  Source x={x_source}  Detect x={x_detect}  path={path_len:.1f}")
    print(f"  Pulse: sigma={sigma_pkt}  A={A_pkt}")
    print(f"  k_list  = {[f'{k:.3f}' for k in k_list]}  (lambda = {[f'{2*np.pi/k:.2f}' for k in k_list]})")
    print(f"  b_list  = {b_list}")
    print()

    # Load cached ring
    print("[0] Load cached ring L=28 R=4")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    ring loaded, M_ring = {M_ring0:.2f}")
    print()

    results = []
    for k_pkt in k_list:
        lam = 2.0 * np.pi / k_pkt
        omega = C_PHI * k_pkt
        print(f"=== k = {k_pkt:.4f}  (lambda = {lam:.2f}, omega = {omega:.4f}) ===")

        for b in b_list:
            y_pulse = y_center + b
            print(f"  --- b = {b}  (pulse y = {y_pulse:.1f}) ---")

            y_det_list = np.arange(int(round(y_pulse)) - 7,
                                   int(round(y_pulse)) + 8)
            y_det_list = y_det_list % L
            y_det_float = y_det_list.astype(float)
            det_idx = xd_int + y_det_list * L + zd_int * L * L
            det_idx_cp = cp.asarray(det_idx)

            # Vacuum run
            vac_state = make_state(L, phi_init=None)
            inject_pulse(vac_state, xc, yc, zc, x_source, y_pulse, z_line,
                         sigma_pkt, k_pkt, A_pkt)
            t_vac, phi_vac = evolve_record_plane(vac_state, nb_idx, T_track,
                                                 det_idx_cp, sample_every,
                                                 verbose=True,
                                                 label=f'vac k={k_pkt:.2f} b={b}')
            ip_vac, tp_vac, amp_vac = find_arrival_time(t_vac, phi_vac,
                                                         y_det_float, y_pulse)
            yc_vac = centroid_y(phi_vac[ip_vac], y_det_float)
            print(f"      vac  peak t={tp_vac:.2f}  amp={amp_vac:.4f}  "
                  f"y_c={yc_vac:.4f}")

            # Ring-only baseline
            s_bg = clone_state(ring_state)
            _, phi_bg = evolve_record_plane(s_bg, nb_idx, T_track,
                                             det_idx_cp, sample_every,
                                             verbose=True,
                                             label=f'bg k={k_pkt:.2f} b={b}')

            # Ring + pulse
            s_rp = clone_state(ring_state)
            inject_pulse(s_rp, xc, yc, zc, x_source, y_pulse, z_line,
                         sigma_pkt, k_pkt, A_pkt)
            t_rp, phi_rp = evolve_record_plane(s_rp, nb_idx, T_track,
                                                det_idx_cp, sample_every,
                                                verbose=True,
                                                label=f'r+p k={k_pkt:.2f} b={b}')

            phi_pulse_ring = phi_rp - phi_bg
            ip_r, tp_r, amp_r = find_arrival_time(t_rp, phi_pulse_ring,
                                                   y_det_float, y_pulse)
            yc_ring = centroid_y(phi_pulse_ring[ip_r], y_det_float)

            Dy = yc_ring - yc_vac
            alpha_meas = Dy / path_len

            # Theory prediction (DER-QNG-046 scalar, no cancellation)
            alpha_th = scalar_alpha_prediction(k_pkt, b, ring_state, L, R,
                                               x_source, x_detect,
                                               y_center, z_line)

            print(f"      ring peak t={tp_r:.2f}  amp={amp_r:.4f}  "
                  f"y_c={yc_ring:.4f}")
            print(f"      Dy={Dy:+.4f}  alpha_meas={alpha_meas:+.4e}  "
                  f"alpha_scalar_th={alpha_th:+.4e}  "
                  f"ratio={alpha_meas/alpha_th if abs(alpha_th)>1e-20 else float('nan'):+.4f}")
            print()

            results.append({
                'k': k_pkt, 'lambda': lam, 'b': b,
                'omega': omega,
                'tp_vac': tp_vac, 'amp_vac': amp_vac, 'yc_vac': yc_vac,
                'tp_ring': tp_r, 'amp_ring': amp_r, 'yc_ring': yc_ring,
                'Dy': Dy,
                'alpha_meas': alpha_meas,
                'alpha_scalar_th': alpha_th,
                'ratio': alpha_meas / alpha_th if abs(alpha_th) > 1e-20 else float('nan'),
            })

    # --- Report ---
    print("=" * 90)
    print("K-SCAN BENDING RESULTS")
    print("=" * 90)
    print(f"{'k':>8} {'lambda':>8} {'b':>4} {'alpha_meas':>15} "
          f"{'alpha_scalar_th':>18} {'ratio':>10} {'verdict':>15}")
    print("-" * 90)
    for r in results:
        rat = r['ratio']
        if abs(rat) < 0.1:
            verd = 'DIFFRACTION'
        elif 0.5 < abs(rat) < 2.0:
            verd = 'EIKONAL_OK'
        elif 2.0 < abs(rat) < 5.0:
            verd = 'ENHANCED'
        else:
            verd = 'MISMATCH'
        print(f"{r['k']:>8.4f} {r['lambda']:>8.2f} {r['b']:>4} "
              f"{r['alpha_meas']:>+15.4e} {r['alpha_scalar_th']:>+18.4e} "
              f"{rat:>+10.4f} {verd:>15}")

    # Hypothesis evaluation
    print()
    print("=" * 90)
    print("HYPOTHESIS EVALUATION")
    print("=" * 90)
    # Take b=4 as the primary column
    for k in k_list:
        r_k = [r for r in results if abs(r['k'] - k) < 1e-9 and r['b'] == 4]
        if not r_k:
            continue
        r = r_k[0]
        print(f"  k={k:.3f}: lambda={r['lambda']:.2f}  "
              f"alpha_meas={r['alpha_meas']:+.3e}  "
              f"alpha_scalar_th={r['alpha_scalar_th']:+.3e}  ratio={r['ratio']:+.3f}")
    print()
    print("If ratio(k) -> 1 as k grows: eikonal hypothesis confirmed (100x gap = diffraction).")
    print("If ratio(k) stays far from 1: gap is real physics (amplitude mod. or back-react).")

    # Save
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-bending-k-scan-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'T_track': T_track, 'c_phi': C_PHI,
        'path_len': path_len,
        'k_list': k_list, 'b_list': b_list,
        'results': results,
        'hyp_eikonal_confirmed_k_pi_2': (
            any(abs(r['k'] - np.pi/2) < 1e-9 and 0.5 < abs(r['ratio']) < 2.0
                for r in results if r['b'] == 4)
        ),
        'hyp_eikonal_confirmed_k_3pi_4': (
            any(abs(r['k'] - 3*np.pi/4) < 1e-9 and 0.5 < abs(r['ratio']) < 2.0
                for r in results if r['b'] == 4)
        ),
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
