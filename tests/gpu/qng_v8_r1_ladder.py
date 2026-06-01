"""QNG-GPU-031g: baryon ladder under R1 orbital interpretation.

Follow-up to GPU-031f (T_P2=5000 lu, R=4, H_ORBITAL_ATTRACTOR verdict,
<M_ring>_t = +309.45). Tests whether the baryon resonance ladder
structure (DER-QNG-038) holds under the orbital reinterpretation.

Usage:
    py tests/gpu/qng_v8_r1_ladder.py --R 5
    py tests/gpu/qng_v8_r1_ladder.py --R 3 --T_P2 5000

Protocol (per R value):
  P1 (T=300 lu, v_couple=False) — phi vortex
  P2 (T=5000 lu, v_couple=True) — orbital run, fine sampling

Prediction under orbital interpretation with a_M_orbital = 3.03 MeV/unit:
    R   expected <M>_t   baryon match
    3   ?                ? (unidentified)
    4   309.45 (given)   N(938)     ✓ (calibration)
    5   406             Δ(1232)    needs 406.6 (ratio 1.313)
    6   499             N*(1520)   needs 501.7 (ratio 1.621)
    7   561             Δ(1700)    needs 561.2 (ratio 1.813)

If observed <M>_t ratios match these targets to <5%, DER-QNG-038 is
*fully recovered* under orbital interpretation and Gap 11 is resolved.

Verdicts:
  * LADDER_MATCH: ratio to R=4 matches CPU-074 ratio within 5%
  * LADDER_BROKEN: ratio > 5% from CPU-074 ratio
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    SIGMA_M_REF, CHI_DECAY_V7, MU_M, MU_PHI,
)

from qng_v8_r1_long_time import run_phase_sampled, analyze_m_series, RING_THRESH

EXACT_A_MODE = 'r1'
GPU_031F_R4_MEAN = 309.45  # <M_ring>_t at R=4 from GPU-031f

# CPU-074 gradient-flow canonical values (for ladder ratio reference)
CPU_074_M = {
    3: 474.15,
    4: 728.92,
    5: 954.88,
    # R=6, R=7 not in CPU-074; use observation
}

# Baryon resonance targets (MeV)
BARYON_TARGETS = {
    3: None,       # unidentified under CPU-074
    4: 938.272,    # proton
    5: 1232.0,     # Δ(1232)
    6: 1520.0,     # N*(1520)
    7: 1700.0,     # Δ(1700)
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--R", type=int, required=True,
                        choices=[3, 4, 5, 6, 7],
                        help="ring radius (integer lattice units)")
    parser.add_argument("--L", type=int, default=20,
                        help="lattice side (default 20)")
    parser.add_argument("--T_P1", type=float, default=300.0)
    parser.add_argument("--T_P2", type=float, default=5000.0)
    parser.add_argument("--DT", type=float, default=0.025)
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-r1-ladder-v1")
    args = parser.parse_args()

    R = args.R
    L = args.L
    T_P1 = args.T_P1
    T_P2 = args.T_P2
    DT = args.DT

    if R >= L // 2:
        print(f"WARNING: R={R} with L={L} leaves buffer {(L-2*R)//2} — "
              "edge effects may matter", flush=True)

    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    m_sample_every = int(1.0 / DT)
    H_sample_every = 100

    outdir = ROOT / "07_validation" / "audits" / args.audit_name / f"R{R}"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"QNG-GPU-031g: R1 ladder probe R={R}")
    print("=" * 80)
    print(f"\n  L={L}, R={R}, T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")
    print(f"  exact_a={EXACT_A_MODE!r}")
    print(f"  CPU-074 ref (R={R}) = "
          f"{CPU_074_M.get(R, 'N/A')}")
    if BARYON_TARGETS.get(R) is not None:
        print(f"  Baryon target (R={R}) = {BARYON_TARGETS[R]} MeV")

    # --- Phase 1 ---
    print("\n  [Phase 1] v_couple_on=False, exact_a='r1'")
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)

    state, t_p1, m_p1, h_p1, wall_p1 = run_phase_sampled(
        state, nb_idx, n1, DT,
        v_couple_on=False, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)
    M_p1 = float(ring_mass_deficit(state['sm']))
    print(f"    end P1: M_ring={M_p1:+.3f}  wall={wall_p1:.1f}s")

    # --- Phase 2 ---
    print(f"\n  [Phase 2] v_couple_on=True, exact_a='r1', T={T_P2} lu")
    state, t_p2, m_p2, h_p2, wall_p2 = run_phase_sampled(
        state, nb_idx, n2, DT,
        v_couple_on=True, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)

    # --- Analysis ---
    print("\n" + "=" * 80)
    print(f"PHASE 2 M_ring ANALYSIS (R={R})")
    print("=" * 80)
    stats = analyze_m_series(t_p2, m_p2, ring_thresh=RING_THRESH)
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k:28s} = {v:+.4g}")
        else:
            print(f"  {k:28s} = {v}")

    # --- Ladder ratio analysis ---
    print("\n" + "=" * 80)
    print("LADDER RATIO vs GPU-031f R=4")
    print("=" * 80)
    mean_this = stats['mean_all']
    ratio_orbital = mean_this / GPU_031F_R4_MEAN
    cpu074_this = CPU_074_M.get(R)
    cpu074_R4 = CPU_074_M[4]
    if cpu074_this is not None:
        ratio_cpu074 = cpu074_this / cpu074_R4
        ratio_rel_diff = abs(ratio_orbital - ratio_cpu074) / abs(ratio_cpu074)
    else:
        ratio_cpu074 = None
        ratio_rel_diff = None

    print(f"  <M_ring>_t (R={R})  = {mean_this:+.3f}")
    print(f"  <M_ring>_t (R=4)  = {GPU_031F_R4_MEAN:+.3f}")
    print(f"  Orbital ratio     = {ratio_orbital:.4f}")
    if ratio_cpu074 is not None:
        print(f"  CPU-074 ratio     = {ratio_cpu074:.4f}")
        print(f"  Relative diff     = {ratio_rel_diff:.2%}")

    # Baryon mass under orbital a_M
    a_M_orbital = 938.272 / GPU_031F_R4_MEAN  # MeV/unit
    predicted_mass = a_M_orbital * mean_this
    print(f"\n  a_M_orbital       = {a_M_orbital:.4f} MeV/unit")
    print(f"  Predicted mass    = {predicted_mass:.1f} MeV")
    target = BARYON_TARGETS.get(R)
    if target is not None:
        mass_rel_diff = abs(predicted_mass - target) / target
        print(f"  Target (R={R})     = {target:.1f} MeV")
        print(f"  Mass rel diff     = {mass_rel_diff:.2%}")
    else:
        mass_rel_diff = None

    # --- Verdict ---
    if stats['convergence_rel'] < 0.05 and stats['duty_cycle_ring'] > 0.10:
        orbital_valid = True
    else:
        orbital_valid = False

    if ratio_rel_diff is not None:
        if ratio_rel_diff < 0.05:
            ladder_verdict = "LADDER_MATCH"
        elif ratio_rel_diff < 0.10:
            ladder_verdict = "LADDER_CLOSE"
        else:
            ladder_verdict = "LADDER_BROKEN"
    else:
        ladder_verdict = "LADDER_NO_CPU074_REF"

    print(f"\n  Orbital validity  : {'OK' if orbital_valid else 'FAIL'}")
    print(f"  Ladder verdict    : {ladder_verdict}")

    # --- Save artifacts ---
    np.savez(outdir / "final_state.npz",
             sm=cp.asnumpy(state['sm']), phi=cp.asnumpy(state['phi']),
             pi_m=cp.asnumpy(state['pi_m']), pi_phi=cp.asnumpy(state['pi_phi']))
    np.savez(outdir / "m_series.npz",
             t_p1=t_p1, m_p1=m_p1, t_p2=t_p2, m_p2=m_p2)

    def _json_safe(v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        return v

    stats_json = {k: _json_safe(v) for k, v in stats.items()}

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'gpu_031f_r4_mean': GPU_031F_R4_MEAN,
            'cpu_074_this': cpu074_this,
            'cpu_074_R4': cpu074_R4,
            'orbital_mean_this': float(mean_this),
            'orbital_ratio': float(ratio_orbital),
            'cpu074_ratio': ratio_cpu074,
            'ratio_rel_diff': ratio_rel_diff,
            'a_M_orbital_MeV_per_unit': float(a_M_orbital),
            'predicted_mass_MeV': float(predicted_mass),
            'baryon_target_MeV': target,
            'mass_rel_diff': mass_rel_diff,
            'orbital_valid': orbital_valid,
            'ladder_verdict': ladder_verdict,
            'stats': stats_json,
            'p2_h_samples_end': h_p2[-5:] if len(h_p2) >= 5 else h_p2,
            'wall_p1_s': wall_p1, 'wall_p2_s': wall_p2,
        }, f, indent=2)

    print(f"\n  Report: {outdir / 'report.json'}")
    print(f"  Final:  {outdir / 'final_state.npz'}")
    print(f"  Series: {outdir / 'm_series.npz'}")


if __name__ == "__main__":
    main()
