"""Ring self-distortion probe on post-cache rescaled rings.

Pre-registration: QNG-GPU-024 (DER-QNG-046 saturation, candidate #3).

Purpose
-------
After GPU-023 ruled out candidate #1 (detector window clipping),
candidate #3 (ring self-distortion from non-equilibrium post-cache
rescaling) is the leading suspect for GPU-022 saturation.

Direct test: evolve post-cache rescaled ring alone (no pulse) for
T_track=250 lu, monitor structural drift. If s=1.4 ring drifts
significantly while s=1.0 stays stable, candidate #3 confirmed.

Metrics per sample:
  M_ring(t)        = sum(SIGMA_M_REF - sigma_m)  [global deficit]
  r_CM(t)          = Sigma r Delta / Sigma Delta [center of mass]
  RMS_drift(t)     = sqrt(mean((sigma_m(t) - sigma_m(0))^2)) / SIGMA_M_REF

VERDICT
-------
  s=1.4: any metric >= 5% or r_CM_drift >= 0.5 lu AND s=1.0 all <1% / <0.1 lu
                                                    -> H_DISTORTION_CONFIRMED
  s=1.4: all metrics < 2% and r_CM < 0.2 lu          -> H_DISTORTION_REJECTED
  s=1.4: metric in (2%, 5%) or r_CM in (0.2, 0.5)    -> H_DISTORTION_PARTIAL
  numerical divergence                                -> H_VOID
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
DT_SAMPLE = 10.0  # lu — measure drift every 10 lu


def make_coords_3d(L):
    idx = cp.arange(L * L * L, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def scale_deficit(state, s):
    state['sm'] = SIGMA_M_REF - s * (SIGMA_M_REF - state['sm'])
    return state


def compute_metrics(state, sm_initial, xc, yc, zc):
    """Return (M_ring, r_CM_x, r_CM_y, r_CM_z, rms_drift)."""
    sm = state['sm']
    delta = SIGMA_M_REF - sm
    M_ring = float(delta.sum())
    if M_ring > 1e-12:
        rx = float((xc * delta).sum() / M_ring)
        ry = float((yc * delta).sum() / M_ring)
        rz = float((zc * delta).sum() / M_ring)
    else:
        rx = ry = rz = float('nan')
    diff = cp.asnumpy(sm) - sm_initial
    rms = float(np.sqrt((diff ** 2).mean())) / float(SIGMA_M_REF)
    return M_ring, rx, ry, rz, rms


def main():
    print("=" * 80)
    print("QNG-GPU-024: RING STABILITY PROBE (candidate #3)")
    print("  Measure M_ring, r_CM, RMS drift during T_track=250 lu on scaled rings")
    print("=" * 80)

    L = 28
    R = 4
    T_track = 250.0
    s_list = [0.7, 1.0, 1.4]
    sample_every_step = int(DT_SAMPLE / DT)

    xc, yc, zc = make_coords_3d(L)

    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  sample every {DT_SAMPLE} lu ({sample_every_step} steps)")
    print(f"  s_list = {s_list}")
    print()

    print("[0] Load cached ring L=28 R=4")
    ring_state_base, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                                verbose=True)
    M_ring0_base = float(ring_mass_deficit(ring_state_base['sm']))
    print(f"    base cached M_ring = {M_ring0_base:.2f}")
    print()

    n_steps = int(T_track / DT)

    all_results = {}
    for s_scale in s_list:
        print(f"=== s = {s_scale:.2f} ===")
        state = clone_state(ring_state_base)
        scale_deficit(state, s_scale)
        sm_initial = cp.asnumpy(state['sm']).copy()
        M0, rx0, ry0, rz0, rms0 = compute_metrics(state, sm_initial, xc, yc, zc)
        print(f"      t=0:  M_ring={M0:.4f}  r_CM=({rx0:.4f},{ry0:.4f},{rz0:.4f})  rms_drift={rms0:.4e}")

        times = [0.0]
        M_hist = [M0]
        rx_hist, ry_hist, rz_hist = [rx0], [ry0], [rz0]
        rms_hist = [rms0]

        t0 = time.time()
        for step in range(1, n_steps + 1):
            state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                                  chi_decay=CHI_DECAY_V7)
            if step % sample_every_step == 0:
                t_lu = step * DT
                M, rx, ry, rz, rms = compute_metrics(state, sm_initial, xc, yc, zc)
                times.append(t_lu)
                M_hist.append(M)
                rx_hist.append(rx); ry_hist.append(ry); rz_hist.append(rz)
                rms_hist.append(rms)
                if step % (sample_every_step * 5) == 0:
                    print(f"      t={t_lu:6.1f}: M={M:.4f}  r_CM=({rx:.4f},{ry:.4f},{rz:.4f})  rms={rms:.4e}")

        wall = time.time() - t0
        print(f"    evolved s={s_scale:.2f}: {n_steps} steps ({wall:.1f}s)")

        times = np.array(times)
        M_hist = np.array(M_hist)
        rx_hist = np.array(rx_hist); ry_hist = np.array(ry_hist); rz_hist = np.array(rz_hist)
        rms_hist = np.array(rms_hist)

        M_max = M_hist.max(); M_min = M_hist.min()
        dM_rel = (M_max - M_min) / M_hist[0]
        dr_CM = float(np.sqrt((rx_hist[-1] - rx_hist[0]) ** 2 +
                              (ry_hist[-1] - ry_hist[0]) ** 2 +
                              (rz_hist[-1] - rz_hist[0]) ** 2))
        rms_max = rms_hist.max()

        print(f"      summary s={s_scale:.2f}:")
        print(f"         M_ring  range: [{M_min:.4f}, {M_max:.4f}]  rel drift {dM_rel*100:.3f}%")
        print(f"         |dr_CM| = {dr_CM:.4f} lu")
        print(f"         max RMS drift = {rms_max*100:.3f}% of SIGMA_M_REF")
        print()

        all_results[s_scale] = {
            's': s_scale,
            'times_lu': times.tolist(),
            'M_ring_hist': M_hist.tolist(),
            'r_CM_x_hist': rx_hist.tolist(),
            'r_CM_y_hist': ry_hist.tolist(),
            'r_CM_z_hist': rz_hist.tolist(),
            'rms_drift_hist': rms_hist.tolist(),
            'M_ring_rel_drift': float(dM_rel),
            'r_CM_total_drift': float(dr_CM),
            'rms_drift_max': float(rms_max),
        }

    # Verdict logic
    r_10 = all_results[1.0]
    r_14 = all_results[1.4]

    # Check for divergence (NaN)
    if any(not np.isfinite(v) for v in
           [r_14['M_ring_rel_drift'], r_14['r_CM_total_drift'], r_14['rms_drift_max']]):
        verdict = 'H_VOID_DIVERGENCE'
    else:
        s14_any_big = (r_14['M_ring_rel_drift'] >= 0.05 or
                       r_14['r_CM_total_drift'] >= 0.5 or
                       r_14['rms_drift_max'] >= 0.05)
        s10_all_tiny = (r_10['M_ring_rel_drift'] < 0.01 and
                        r_10['r_CM_total_drift'] < 0.1 and
                        r_10['rms_drift_max'] < 0.01)
        s14_all_small = (r_14['M_ring_rel_drift'] < 0.02 and
                         r_14['r_CM_total_drift'] < 0.2 and
                         r_14['rms_drift_max'] < 0.02)
        s14_partial = ((0.02 <= r_14['M_ring_rel_drift'] < 0.05) or
                       (0.2 <= r_14['r_CM_total_drift'] < 0.5) or
                       (0.02 <= r_14['rms_drift_max'] < 0.05))

        if s14_any_big and s10_all_tiny:
            verdict = 'H_DISTORTION_CONFIRMED'
        elif s14_all_small:
            verdict = 'H_DISTORTION_REJECTED'
        elif s14_partial:
            verdict = 'H_DISTORTION_PARTIAL'
        else:
            verdict = 'H_DISTORTION_MIXED'

    print("=" * 90)
    print("RING STABILITY SUMMARY")
    print("=" * 90)
    print(f"{'s':>5} {'M rel drift%':>14} {'|dr_CM| lu':>14} {'max RMS %':>14}")
    print("-" * 60)
    for s_scale in s_list:
        r = all_results[s_scale]
        print(f"{s_scale:>5.2f} {r['M_ring_rel_drift']*100:>14.4f} "
              f"{r['r_CM_total_drift']:>14.4f} "
              f"{r['rms_drift_max']*100:>14.4f}")
    print()
    print(f"VERDICT: {verdict}")
    print()
    print("=" * 90)
    print("HYPOTHESIS EVALUATION")
    print("=" * 90)
    print("  H_DISTORTION_CONFIRMED: s=1.4 has metric >=5% or r_CM >=0.5, s=1.0 all <1% / <0.1")
    print("  H_DISTORTION_REJECTED:  s=1.4 all <2% and r_CM <0.2")
    print("  H_DISTORTION_PARTIAL:   s=1.4 metric in [2%, 5%) or r_CM in [0.2, 0.5)")
    print("  H_VOID:                 numerical divergence")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-ring-stability-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'T_track': T_track, 'DT': DT,
        'DT_sample_lu': DT_SAMPLE,
        's_list': s_list,
        'M_ring_base': M_ring0_base,
        'results': all_results,
        'verdict': verdict,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
