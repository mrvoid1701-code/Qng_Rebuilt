"""Ring stability diagnostic: which Hamiltonian term drives the chaos?

Pre-registration: QNG-GPU-024b.

Purpose
-------
GPU-024 showed cached ring is metastable under full Phase-2 dynamics.
Localize the driver: V_couple, chi_decay, or Channel F (untestable
without code mod)?

Three runs at s=1.0:
  A: v_couple_on=True,  chi_decay=0.020   (control, = GPU-024 s=1.0)
  B: v_couple_on=True,  chi_decay=0.0     (chi_decay off)
  C: v_couple_on=False, chi_decay=0.0     (coupling off)

Channel F is always active (baked into compute_sm_force_v8).
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
    SIGMA_M_REF, CHI_DECAY_V7,
    yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
DT_SAMPLE = 10.0


def make_coords_3d(L):
    idx = cp.arange(L * L * L, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def compute_metrics(state, sm_initial):
    sm = state['sm']
    delta = SIGMA_M_REF - sm
    M_ring = float(delta.sum())
    diff = cp.asnumpy(sm) - sm_initial
    rms = float(np.sqrt((diff ** 2).mean())) / float(SIGMA_M_REF)
    return M_ring, rms


def run_config(ring_state_base, nb_idx, label, v_couple_on, chi_decay,
               n_steps, sample_every_step):
    print(f"=== Config {label}: v_couple_on={v_couple_on}  chi_decay={chi_decay} ===")
    state = clone_state(ring_state_base)
    sm_initial = cp.asnumpy(state['sm']).copy()
    M0, rms0 = compute_metrics(state, sm_initial)
    print(f"      t=0:  M_ring={M0:.4f}  rms_drift={rms0:.4e}")

    times = [0.0]
    M_hist = [M0]
    rms_hist = [rms0]

    t0 = time.time()
    for step in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=v_couple_on,
                              chi_decay=chi_decay)
        if step % sample_every_step == 0:
            t_lu = step * DT
            M, rms = compute_metrics(state, sm_initial)
            times.append(t_lu)
            M_hist.append(M)
            rms_hist.append(rms)
            if step % (sample_every_step * 5) == 0:
                print(f"      t={t_lu:6.1f}: M={M:.4f}  rms={rms:.4e}")

    wall = time.time() - t0
    times = np.array(times); M_hist = np.array(M_hist); rms_hist = np.array(rms_hist)
    M_min, M_max = M_hist.min(), M_hist.max()
    dM_rel = (M_max - M_min) / M_hist[0]
    rms_max = rms_hist.max()
    print(f"    evolved {label}: {n_steps} steps ({wall:.1f}s)")
    print(f"      summary {label}:")
    print(f"         M_ring range: [{M_min:.4f}, {M_max:.4f}]  rel drift {dM_rel*100:.3f}%")
    print(f"         max RMS drift = {rms_max*100:.3f}% of SIGMA_M_REF")
    print()

    return {
        'label': label,
        'v_couple_on': v_couple_on,
        'chi_decay': chi_decay,
        'times_lu': times.tolist(),
        'M_ring_hist': M_hist.tolist(),
        'rms_drift_hist': rms_hist.tolist(),
        'M_ring_rel_drift': float(dM_rel),
        'rms_drift_max': float(rms_max),
    }


def main():
    print("=" * 80)
    print("QNG-GPU-024b: RING STABILITY DIAGNOSTIC")
    print("  Localize the chaos driver: V_couple, chi_decay, or Channel F")
    print("=" * 80)

    L = 28
    R = 4
    T_track = 250.0
    sample_every_step = int(DT_SAMPLE / DT)

    print(f"  L={L}  R={R}  T_track={T_track} lu  DT={DT}")
    print(f"  sample every {DT_SAMPLE} lu ({sample_every_step} steps)")
    print()

    print("[0] Load cached ring L=28 R=4")
    ring_state_base, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                                verbose=True)
    M_ring0_base = float(ring_mass_deficit(ring_state_base['sm']))
    print(f"    base cached M_ring = {M_ring0_base:.2f}")
    print()

    n_steps = int(T_track / DT)

    configs = [
        ('A_control', True, CHI_DECAY_V7),
        ('B_chi_off', True, 0.0),
        ('C_coupling_off', False, 0.0),
    ]

    results = {}
    for label, v_couple, chi in configs:
        results[label] = run_config(ring_state_base, nb_idx, label,
                                    v_couple, chi, n_steps, sample_every_step)

    # Verdict logic
    STABLE_THRESH = 0.05  # 5% M_ring rel drift

    drift_A = results['A_control']['M_ring_rel_drift']
    drift_B = results['B_chi_off']['M_ring_rel_drift']
    drift_C = results['C_coupling_off']['M_ring_rel_drift']

    chaos_A = drift_A >= STABLE_THRESH
    chaos_B = drift_B >= STABLE_THRESH
    chaos_C = drift_C >= STABLE_THRESH

    if chaos_A and chaos_B and not chaos_C:
        verdict = 'H_V_COUPLE_DRIVER'
    elif chaos_A and not chaos_B and not chaos_C:
        verdict = 'H_CHI_DECAY_DRIVER'
    elif chaos_A and chaos_B and chaos_C:
        # Differ trajectories implies INTRINSIC; similar implies Channel F
        # crude test: max difference in M_ring_hist normalized
        M_B = np.array(results['B_chi_off']['M_ring_hist'])
        M_C = np.array(results['C_coupling_off']['M_ring_hist'])
        if len(M_B) == len(M_C):
            traj_diff = float(np.mean(np.abs(M_B - M_C)) / np.mean(M_B))
            if traj_diff < 0.1:
                verdict = 'H_CHANNEL_F_DRIVER'
            else:
                verdict = 'H_INTRINSIC'
            results['_traj_diff_B_vs_C'] = traj_diff
        else:
            verdict = 'H_CHANNEL_F_DRIVER'
    else:
        verdict = 'H_ANOMALOUS'

    print("=" * 90)
    print("RING STABILITY DIAGNOSTIC SUMMARY")
    print("=" * 90)
    print(f"{'config':>16} {'v_couple':>10} {'chi_decay':>12} {'drift %':>12} {'max RMS %':>12}")
    print("-" * 70)
    for label, _, _ in configs:
        r = results[label]
        print(f"{label:>16} {str(r['v_couple_on']):>10} {r['chi_decay']:>12.4f} "
              f"{r['M_ring_rel_drift']*100:>12.3f} {r['rms_drift_max']*100:>12.3f}")
    print()
    print(f"VERDICT: {verdict}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-ring-stability-diag-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'T_track': T_track, 'DT': DT,
        'DT_sample_lu': DT_SAMPLE,
        'M_ring_base': M_ring0_base,
        'results': results,
        'verdict': verdict,
        'stable_threshold_rel_drift': STABLE_THRESH,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
