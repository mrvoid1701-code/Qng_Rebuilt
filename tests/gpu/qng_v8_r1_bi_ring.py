"""QNG-GPU-032: bi-ring binding probe under R1 orbital.

Background: GPU-031g showed v8 R1 orbital attractor is R-insensitive
(R=3/R=4/R=5 all give <M>_t ~ 310). User hypothesis (2026-04-21):
particles = BOUND STATES of multiple vortex-rings, not single rings.
A lone ring is a constituent, not a particle — hence universal basin.

This probe tests the multi-vortex hypothesis by forming TWO rings with
opposite chirality (W+W-, attractive per CPU-049) at separation d=6
on an L=24 lattice, then running the R1 orbital protocol. The ring
mass deficit is global (sum over all nodes), so M_ring counts the
total deficit of both rings simultaneously.

Predictions:
  * If lone ring = constituent (user hypothesis):
    <M_total>_t != 2 * 310 = 620. Binding energy appears as deviation.
    Bound state may have DIFFERENT orbital basin mean, period, duty.
  * If each ring is independent:
    <M_total>_t ~ 620 (simple sum), same orbital period, no binding
    signature.

Runtime (L=24): ~75 min total (~4300s Phase 2 + 180s Phase 1).

Usage:
    py tests/gpu/qng_v8_r1_bi_ring.py
    py tests/gpu/qng_v8_r1_bi_ring.py --d 8 --same_chirality
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
    build_nb, make_state, init_phi_two_rings, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    SIGMA_M_REF, CHI_DECAY_V7, MU_M, MU_PHI,
)

from qng_v8_r1_long_time import run_phase_sampled, analyze_m_series, RING_THRESH

EXACT_A_MODE = 'r1'
# GPU-031f single-ring reference
GPU_031F_R4_MEAN = 309.45


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, default=24,
                        help="lattice side (default 24 to fit 2 rings)")
    parser.add_argument("--R", type=int, default=4,
                        help="ring radius each (default 4)")
    parser.add_argument("--d", type=int, default=6,
                        help="separation between ring centers (default 6)")
    parser.add_argument("--same_chirality", action='store_true',
                        help="W+W+ (repulsive); default is W+W- attractive")
    parser.add_argument("--T_P1", type=float, default=300.0)
    parser.add_argument("--T_P2", type=float, default=5000.0)
    parser.add_argument("--DT", type=float, default=0.025)
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-r1-bi-ring-v1")
    args = parser.parse_args()

    L = args.L
    R = args.R
    d = args.d
    same_chirality = args.same_chirality
    T_P1 = args.T_P1
    T_P2 = args.T_P2
    DT = args.DT

    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    m_sample_every = int(1.0 / DT)
    H_sample_every = 100

    chirality_tag = "W+W+" if same_chirality else "W+W-"
    outdir = ROOT / "07_validation" / "audits" / args.audit_name
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"QNG-GPU-032: bi-ring binding probe")
    print("=" * 80)
    print(f"\n  L={L}, R={R}, d={d}, chirality={chirality_tag}")
    print(f"  T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")
    print(f"  exact_a={EXACT_A_MODE!r}")
    print(f"  GPU-031f single-ring ref = {GPU_031F_R4_MEAN}")
    print(f"  Two-ring unbound prediction = {2*GPU_031F_R4_MEAN}")

    # --- Phase 1 ---
    print(f"\n  [Phase 1] v_couple_on=False, exact_a='r1', 2 rings {chirality_tag}")
    nb_idx = build_nb(L)
    phi_ic = init_phi_two_rings(L, R, d, same_chirality=same_chirality)
    state = make_state(L, phi_init=phi_ic)

    state, t_p1, m_p1, h_p1, wall_p1 = run_phase_sampled(
        state, nb_idx, n1, DT,
        v_couple_on=False, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)
    M_p1 = float(ring_mass_deficit(state['sm']))
    print(f"    end P1: M_total={M_p1:+.3f}  wall={wall_p1:.1f}s")

    # --- Phase 2 ---
    print(f"\n  [Phase 2] v_couple_on=True, exact_a='r1', T={T_P2} lu")
    state, t_p2, m_p2, h_p2, wall_p2 = run_phase_sampled(
        state, nb_idx, n2, DT,
        v_couple_on=True, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)

    # --- Analysis ---
    print("\n" + "=" * 80)
    print(f"PHASE 2 M_total ANALYSIS ({chirality_tag} at d={d})")
    print("=" * 80)
    stats = analyze_m_series(t_p2, m_p2, ring_thresh=RING_THRESH)
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k:28s} = {v:+.4g}")
        else:
            print(f"  {k:28s} = {v}")

    # --- Binding analysis ---
    print("\n" + "=" * 80)
    print("BINDING ANALYSIS")
    print("=" * 80)
    mean_total = stats['mean_all']
    mean_second_half = stats['mean_second_half']
    unbound_pred = 2 * GPU_031F_R4_MEAN
    delta_total = mean_total - unbound_pred
    delta_second = mean_second_half - unbound_pred
    frac_total = delta_total / unbound_pred
    frac_second = delta_second / unbound_pred

    print(f"  <M_total>_t (all)     = {mean_total:+.3f}")
    print(f"  <M_total>_t (2nd-half)= {mean_second_half:+.3f}")
    print(f"  Unbound prediction    = {unbound_pred:+.3f}")
    print(f"  Delta (all)           = {delta_total:+.3f}  ({frac_total:+.2%})")
    print(f"  Delta (2nd-half)      = {delta_second:+.3f}  ({frac_second:+.2%})")

    # Verdict
    # Binding signature: |delta_second| > 10% of unbound_pred
    # AND convergence_rel < 10% (orbit converging or close to it)
    abs_frac = abs(frac_second)
    converged = stats['convergence_rel'] < 0.10

    if not converged:
        verdict = "INCONCLUSIVE_NOT_CONVERGED"
    elif abs_frac > 0.30:
        verdict = "STRONG_BINDING" if frac_second < 0 else "STRONG_REPULSION"
    elif abs_frac > 0.10:
        verdict = "MILD_BINDING" if frac_second < 0 else "MILD_REPULSION"
    elif abs_frac > 0.05:
        verdict = "WEAK_DEVIATION"
    else:
        verdict = "UNBOUND_SUM"

    print(f"\n  Verdict: {verdict}")
    print(f"\n  Interpretation:")
    if verdict in ("STRONG_BINDING", "MILD_BINDING"):
        print("    Bound state exists — binding energy detected.")
        print("    Multi-vortex hypothesis SUPPORTED.")
    elif verdict in ("STRONG_REPULSION", "MILD_REPULSION"):
        print("    Rings repel (mass > 2x single). Unexpected for W+W-.")
        print("    Multi-vortex hypothesis ANOMALOUS.")
    elif verdict == "UNBOUND_SUM":
        print("    <M_total>_t ~ 2 x single ring. No binding.")
        print("    Multi-vortex hypothesis NOT supported at this (R, d).")
    else:
        print("    Result inconclusive; may need T=10000 lu or different d.")

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
            'L': L, 'R': R, 'd': d,
            'same_chirality': same_chirality,
            'chirality_tag': chirality_tag,
            'T_P1': T_P1, 'T_P2': T_P2, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'gpu_031f_r4_mean_single': GPU_031F_R4_MEAN,
            'unbound_prediction': unbound_pred,
            'mean_total_all': float(mean_total),
            'mean_total_second_half': float(mean_second_half),
            'delta_all': float(delta_total),
            'delta_second_half': float(delta_second),
            'frac_total': float(frac_total),
            'frac_second_half': float(frac_second),
            'verdict': verdict,
            'stats': stats_json,
            'p2_h_samples_end': h_p2[-5:] if len(h_p2) >= 5 else h_p2,
            'wall_p1_s': wall_p1, 'wall_p2_s': wall_p2,
        }, f, indent=2)

    print(f"\n  Report: {outdir / 'report.json'}")
    print(f"  Final:  {outdir / 'final_state.npz'}")
    print(f"  Series: {outdir / 'm_series.npz'}")


if __name__ == "__main__":
    main()
