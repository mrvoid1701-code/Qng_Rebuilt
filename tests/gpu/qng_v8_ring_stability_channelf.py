"""Ring stability — is Channel F the chaos driver?

Pre-registration: QNG-GPU-024c.

Purpose
-------
GPU-024b showed:
  - chi_decay has zero effect (A=B byte-identical)
  - V_couple off changes trajectory but doesn't stabilize
  - Channel F was the only untested term

This probe tests Channel F hypothesis via newly-added channel_f flag
in yoshida4_step:

  D: v_couple_on=True,  chi_decay=CHI_DECAY_V7, channel_f=False
     (cleanest v8 minus Channel F — physical measurement-mode candidate)
  E: v_couple_on=False, chi_decay=0,            channel_f=False
     (all non-linear couplings off — pure ALPHA+BETA_M diffusion +
      V_couple-less kinetic sector; null test)

Verdict:
  D stable (<5% drift) -> H_CHANNEL_F_DRIVER (Channel F confirmed);
    Phase-3 measurement mode is v_couple_on=True + channel_f=False
  D chaotic, E stable  -> H_MIXED (Channel F + V_couple both required);
    no clean measurement mode in v8 3D
  D chaotic, E chaotic -> H_NO_EQUILIBRIUM; ring does not admit a stable
    fixed point under v8 3D Hamiltonian; re-opens NOTE-QNG-014 + dimension
    question
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
               channel_f, n_steps, sample_every_step):
    print(f"=== Config {label}: v_couple_on={v_couple_on}  chi_decay={chi_decay}  channel_f={channel_f} ===")
    state = clone_state(ring_state_base)
    sm_initial = cp.asnumpy(state['sm']).copy()
    M0, rms0 = compute_metrics(state, sm_initial)
    print(f"      t=0:  M_ring={M0:.4f}  rms_drift={rms0:.4e}")

    times = [0.0]; M_hist = [M0]; rms_hist = [rms0]

    t0 = time.time()
    for step in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=v_couple_on,
                              chi_decay=chi_decay,
                              channel_f=channel_f)
        if step % sample_every_step == 0:
            t_lu = step * DT
            M, rms = compute_metrics(state, sm_initial)
            times.append(t_lu); M_hist.append(M); rms_hist.append(rms)
            if step % (sample_every_step * 5) == 0:
                print(f"      t={t_lu:6.1f}: M={M:.4f}  rms={rms:.4e}")

    wall = time.time() - t0
    times = np.array(times); M_hist = np.array(M_hist); rms_hist = np.array(rms_hist)
    M_min, M_max = M_hist.min(), M_hist.max()
    dM_rel = (M_max - M_min) / M_hist[0] if M_hist[0] != 0 else float('nan')
    rms_max = rms_hist.max()
    print(f"    evolved {label}: {n_steps} steps ({wall:.1f}s)")
    print(f"      summary {label}:")
    print(f"         M_ring range: [{M_min:.4f}, {M_max:.4f}]  rel drift {dM_rel*100:.3f}%")
    print(f"         max RMS drift = {rms_max*100:.3f}% of SIGMA_M_REF")
    print()

    return {
        'label': label, 'v_couple_on': v_couple_on, 'chi_decay': chi_decay,
        'channel_f': channel_f,
        'times_lu': times.tolist(),
        'M_ring_hist': M_hist.tolist(),
        'rms_drift_hist': rms_hist.tolist(),
        'M_ring_rel_drift': float(dM_rel),
        'rms_drift_max': float(rms_max),
    }


def main():
    print("=" * 80)
    print("QNG-GPU-024c: RING STABILITY - CHANNEL F HYPOTHESIS TEST")
    print("  D: full v8 minus Channel F       (physical measurement-mode candidate)")
    print("  E: everything nonlinear off       (null test)")
    print("=" * 80)

    L = 28; R = 4; T_track = 250.0
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
        ('D_ChF_off',   True,  CHI_DECAY_V7, False),
        ('E_all_off',   False, 0.0,          False),
    ]

    results = {}
    for label, v_couple, chi, ch_f in configs:
        results[label] = run_config(ring_state_base, nb_idx, label,
                                    v_couple, chi, ch_f,
                                    n_steps, sample_every_step)

    STABLE_THRESH = 0.05
    D_stable = results['D_ChF_off']['M_ring_rel_drift'] < STABLE_THRESH
    E_stable = results['E_all_off']['M_ring_rel_drift'] < STABLE_THRESH

    if D_stable:
        verdict = 'H_CHANNEL_F_DRIVER'
    elif not D_stable and E_stable:
        verdict = 'H_MIXED'
    elif not D_stable and not E_stable:
        verdict = 'H_NO_EQUILIBRIUM'
    else:
        verdict = 'H_ANOMALOUS'

    print("=" * 90)
    print("CHANNEL F HYPOTHESIS SUMMARY")
    print("=" * 90)
    print(f"{'config':>14} {'v_couple':>10} {'chi_decay':>10} {'ch_f':>6} {'drift %':>12} {'max RMS %':>12}")
    print("-" * 74)
    for label, _, _, _ in configs:
        r = results[label]
        print(f"{label:>14} {str(r['v_couple_on']):>10} {r['chi_decay']:>10.4f} "
              f"{str(r['channel_f']):>6} {r['M_ring_rel_drift']*100:>12.3f} "
              f"{r['rms_drift_max']*100:>12.3f}")
    print()
    print(f"VERDICT: {verdict}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-ring-stability-channelf-v1"
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
