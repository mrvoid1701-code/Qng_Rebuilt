"""Bending angle probe for v8 rings (Einstein test #3, the 1911-vs-1915 test).

THIS IS THE DECISIVE TEST.  Einstein abandoned his 1911 scalar-c theory
because it predicts half the light deflection that GR does.  The bending
angle is the only observable that cleanly separates a scalar gravity
theory (factor 0.87") from a true tensor metric theory (factor 1.75"):

  alpha_1911 = (1 / c_phi^2) * integ d_y[m^2(x,b)/k^2] dx
  alpha_GR   = 2 * alpha_1911   (factor 2 from spatial metric curvature)

Protocol (cached L=28 R=4 ring, pulse parallel to +x):
  - Pulse source: (x=4, y=y_c + b, z=y_c) with sigma=2, k=pi/4, A=0.05
  - Detector PLANE at x = L-4, y in [y_pulse - 7, y_pulse + 7] (15 nodes)
  - Record phi(x_det, y_det[i], z_c) over time for each detector node
  - At envelope peak time, extract TRANSVERSE CENTROID:
        y_centroid = sum(y * |phi(y)|^2) / sum(|phi(y)|^2)
  - Deflection Dy = y_centroid_ring - y_centroid_vacuum
  - Deflection angle alpha = Dy / (x_det - x_source)

Quick-look version (L=28 cached):
  - Use cached L=28 R=4 ring (no formation cost).
  - Scan b in {3, 4, 6, 8}.  Per b: 1 vacuum + 1 ring+pulse tracking.
  - ~5 min/run -> ~40 min total.

VERDICT (per-b):
  Measure ratio r = alpha_measured / alpha_theory_1911
    r ~ 0.0:  no bending (null result; need larger amplitude)
    r ~ 1.0:  EINSTEIN 1911 dead-end confirmed (scalar-c gravity)
    r ~ 2.0:  EINSTEIN 1915 / GR confirmed (tensor metric)
    r else:   genuinely new physics (neither)
"""
from __future__ import annotations

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
    """Evolve and record phi at ALL detector nodes (y-array) over time.

    det_idx_array: shape (n_det,)  raveled indices (cupy)
    Returns (t_rec, phi_rec[t, det]).
    """
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
        print(f"    evolved {label}: {n} steps ({time.time()-t0:.1f}s)")
    return np.array(t_rec), np.array(phi_rec)


def centroid_y(phi_plane, y_coords):
    """Transverse centroid weighted by |phi|^2."""
    w = phi_plane ** 2
    s = w.sum()
    if s < 1e-20:
        return float('nan')
    return float((y_coords * w).sum() / s)


def find_arrival_time(t, phi_plane, y_coords, y_expected):
    """Return time index when pulse envelope magnitude peaks at detector.

    Uses max over detectors and time of |phi|.
    """
    # Collapse across detectors: take L2 norm at each t
    intensity = np.sqrt((phi_plane ** 2).sum(axis=1))
    # Smooth slightly
    window = 3
    smoothed = np.convolve(intensity, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(smoothed))
    return i_peak, float(t[i_peak]), float(smoothed[i_peak])


def main():
    print("=" * 80)
    print("Einstein test #3: BENDING ANGLE (1911 vs 1915)")
    print("  THE decisive test per Einstein himself")
    print("=" * 80)

    L = 28
    R = 4
    T_track = 250.0
    DT_sample = 1.0
    sample_every = int(DT_sample / DT)

    # Geometry
    x_source = 4.0
    x_detect = L - 4.0
    path_len = x_detect - x_source
    z_line   = 0.5 * L
    sigma_pkt = 2.0
    k_pkt     = np.pi / 4.0
    A_pkt     = 0.05

    # Detector plane setup: 15 y-nodes around expected pulse y
    y_center = 0.5 * L
    xd_int = int(round(x_detect))
    zd_int = int(round(z_line))

    # b list: radial impact parameter (pulse at y = y_center + b)
    b_list = [3, 4, 6, 8]

    # Theoretical 1911 predictions from CPU script:
    theory_1911_bending = {
        # b: (alpha_rad from linear scalar theory)
        3: 7.63e-01,   # UNRELIABLE — eikonal breaks at small b
        4: -5.65e-01,
        6: -2.86e-01,
        8: -4.12e+00,  # periodic artifact
    }

    xc, yc, zc = make_coords(L)

    # Print header
    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  c_phi = {C_PHI:.5f}")
    print(f"  Source x={x_source}  Detect x={x_detect}  path={path_len:.1f}")
    print(f"  Pulse: sigma={sigma_pkt}  k={k_pkt:.3f}  A={A_pkt}")
    print()

    # --- Ring (cached) ---
    print("[0] Load cached ring L=28 R=4")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    ring loaded, M_ring = {M_ring0:.2f}")
    print()

    # --- Scan b ---
    results = []
    for b in b_list:
        y_pulse = y_center + b
        print(f"--- b = {b}  (pulse y = {y_pulse:.1f}) ---")

        # Detector y-array: ±7 around pulse, 15 nodes
        y_det_list = np.arange(int(round(y_pulse)) - 7,
                               int(round(y_pulse)) + 8)  # 15 ints
        # Periodic clamp
        y_det_list = y_det_list % L
        y_det_float = y_det_list.astype(float)

        # Detector raveled indices: x=xd_int, y=y_det_list, z=zd_int
        det_idx = xd_int + y_det_list * L + zd_int * L * L
        det_idx_cp = cp.asarray(det_idx)

        # --- Vacuum run ---
        vac_state = make_state(L, phi_init=None)
        inject_pulse(vac_state, xc, yc, zc, x_source, y_pulse, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        t_vac, phi_vac = evolve_record_plane(vac_state, nb_idx, T_track,
                                             det_idx_cp, sample_every,
                                             verbose=True,
                                             label=f'vac b={b}')
        ip_vac, tp_vac, amp_vac = find_arrival_time(t_vac, phi_vac,
                                                     y_det_float, y_pulse)
        yc_vac = centroid_y(phi_vac[ip_vac], y_det_float)
        print(f"    vac   peak at t={tp_vac:.2f}  amp={amp_vac:.4f}  "
              f"y_centroid={yc_vac:.4f}")

        # --- Ring-only baseline ---
        s_bg = clone_state(ring_state)
        _, phi_bg = evolve_record_plane(s_bg, nb_idx, T_track,
                                         det_idx_cp, sample_every,
                                         verbose=True,
                                         label=f'ring_only b={b}')

        # --- Ring + pulse ---
        s_rp = clone_state(ring_state)
        inject_pulse(s_rp, xc, yc, zc, x_source, y_pulse, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        t_rp, phi_rp = evolve_record_plane(s_rp, nb_idx, T_track,
                                            det_idx_cp, sample_every,
                                            verbose=True,
                                            label=f'ring+pulse b={b}')

        # Subtract background (ring-only) to isolate pulse-in-ring
        phi_pulse_ring = phi_rp - phi_bg
        ip_r, tp_r, amp_r = find_arrival_time(t_rp, phi_pulse_ring,
                                               y_det_float, y_pulse)
        yc_ring = centroid_y(phi_pulse_ring[ip_r], y_det_float)

        Dy = yc_ring - yc_vac
        alpha_meas = Dy / path_len

        print(f"    ring  peak at t={tp_r:.2f}  amp={amp_r:.4f}  "
              f"y_centroid={yc_ring:.4f}")
        print(f"    -> Dy = {Dy:+.4f} nodes   alpha_meas = {alpha_meas:+.4e} rad")
        print()

        results.append({
            'b': b, 'y_pulse': y_pulse, 'y_det': y_det_float,
            'tp_vac': tp_vac, 'yc_vac': yc_vac,
            'tp_ring': tp_r, 'yc_ring': yc_ring,
            'Dy': Dy, 'alpha_meas': alpha_meas,
            't_vec': t_vac,
            'phi_vac_plane_at_peak': phi_vac[ip_vac],
            'phi_ring_plane_at_peak': phi_pulse_ring[ip_r],
        })

    # --- Report ---
    print("=" * 80)
    print("BENDING RESULTS")
    print("=" * 80)
    print(f"{'b':>4} {'Dy (nodes)':>14} {'alpha_meas':>16} "
          f"{'alpha_1911':>16} {'ratio':>10} {'verdict':>15}")
    print("-" * 80)
    for r in results:
        a_th = theory_1911_bending.get(r['b'], float('nan'))
        if abs(a_th) > 1e-20:
            ratio = r['alpha_meas'] / a_th
            if abs(ratio) < 0.1:
                verd = 'NULL'
            elif 0.7 < abs(ratio) < 1.3:
                verd = '1911'
            elif 1.7 < abs(ratio) < 2.3:
                verd = 'GR 1915'
            else:
                verd = 'NEITHER'
        else:
            ratio = float('nan')
            verd = 'no theory'
        print(f"{r['b']:>4} {r['Dy']:>+14.5f} {r['alpha_meas']:>+16.5e} "
              f"{a_th:>+16.5e} {ratio:>+10.3f} {verd:>15}")

    # Save raw data
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / "bending_probe_signals.npz",
             L=L, R=R, path_len=path_len, c_phi=C_PHI,
             b_list=np.array(b_list),
             Dy=np.array([r['Dy'] for r in results]),
             alpha_meas=np.array([r['alpha_meas'] for r in results]),
             y_centroid_vac=np.array([r['yc_vac'] for r in results]),
             y_centroid_ring=np.array([r['yc_ring'] for r in results]),
             # Store per-b detection plane phi envelopes
             **{f'phi_vac_plane_b{r["b"]}': r['phi_vac_plane_at_peak']
                for r in results},
             **{f'phi_ring_plane_b{r["b"]}': r['phi_ring_plane_at_peak']
                for r in results})

    print(f"\n  Signals saved to {outdir / 'bending_probe_signals.npz'}")
    print()
    print("=" * 80)
    print("OVERALL VERDICT")
    print("=" * 80)
    dy_values = [abs(r['Dy']) for r in results]
    max_dy = max(dy_values)
    if max_dy < 0.05:
        print(f"NULL RESULT: max |Dy| = {max_dy:.4f} nodes < 0.05 noise floor")
        print("  -> bending not detectable at L=28.  Need L=40 + higher amplitude.")
    else:
        print(f"BENDING DETECTED: max |Dy| = {max_dy:.4f} nodes over "
              f"{path_len:.0f}-node path")
        print(f"  -> alpha_max = {max_dy/path_len:.4e} rad")
        print()
        print("  Compare per-b ratio in table above:")
        print("    ratio ~ 1.0  -> 1911 dead-end (scalar-c gravity)")
        print("    ratio ~ 2.0  -> GR 1915 (metric curvature, Eddington)")
        print("    ratio ~ other-> genuinely new physics")


if __name__ == "__main__":
    main()
