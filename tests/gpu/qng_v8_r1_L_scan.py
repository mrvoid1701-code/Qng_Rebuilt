"""QNG-GPU-034: L-scaling of single-ring orbital attractor.

Einstein+Tesla falsifier: if <M>_t basin is a cavity eigenmode (box
artifact), the dominant period T_dom should scale linearly with L.

Reference: GPU-031f (L=20, R=4) gave T_dom = 185 lu.
Prediction (box-locked k=1 mode): T(L) = L/c_phi with c_phi = 0.1080
  L=20: T_pred = 185.2 lu  (MATCHES observation!)
  L=32: T_pred = 296.3 lu
  L=16: T_pred = 148.1 lu

Test: run single ring R=4 on L=32, compare measured T_dom to 296.3.

Kill condition (box-locked):
  abs(T_meas/T_pred - 1) < 0.10 => basin is cavity mode, NOT particle
Alive condition (intrinsic):
  T_meas ≈ 185 lu regardless of L => ring has intrinsic period
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
C_PHI = np.sqrt(0.01167)  # KG dispersion c, from DER-QNG-044

# reference (L=20, R=4)
GPU_031F_T = 185.0
GPU_031F_MEAN = 309.45


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, default=32)
    parser.add_argument("--R", type=int, default=4)
    parser.add_argument("--T_P1", type=float, default=300.0)
    parser.add_argument("--T_P2", type=float, default=5000.0)
    parser.add_argument("--DT", type=float, default=0.025)
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-r1-L-scan-v1")
    args = parser.parse_args()

    L = args.L
    R = args.R
    T_P1 = args.T_P1
    T_P2 = args.T_P2
    DT = args.DT

    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    m_sample_every = int(1.0 / DT)
    H_sample_every = 100

    T_pred = L / C_PHI

    outdir = ROOT / "07_validation" / "audits" / f"{args.audit_name}-L{L}"
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"QNG-GPU-034: L-scaling test, L={L} R={R}")
    print("=" * 80)
    print(f"\n  Reference (L=20): T_dom = {GPU_031F_T} lu, <M>_t = {GPU_031F_MEAN}")
    print(f"  Prediction (box-locked k=1): T_pred(L={L}) = L/c_phi = {T_pred:.2f} lu")
    print(f"  T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")

    # Phase 1
    print(f"\n  [Phase 1] v_couple_on=False, exact_a='r1'")
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

    # Phase 2
    print(f"\n  [Phase 2] v_couple_on=True, exact_a='r1', T={T_P2} lu")
    state, t_p2, m_p2, h_p2, wall_p2 = run_phase_sampled(
        state, nb_idx, n2, DT,
        v_couple_on=True, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)

    stats = analyze_m_series(t_p2, m_p2, ring_thresh=RING_THRESH)
    T_meas = stats['dominant_period_lu']
    ratio_to_pred = T_meas / T_pred if T_pred > 0 else float('inf')
    ratio_to_ref = T_meas / GPU_031F_T

    print("\n" + "=" * 80)
    print(f"L-SCALING VERDICT")
    print("=" * 80)
    print(f"  T_measured                = {T_meas:.2f} lu")
    print(f"  T_predicted (box-locked)  = {T_pred:.2f} lu")
    print(f"  T_ref (L=20)              = {GPU_031F_T:.2f} lu")
    print(f"  ratio T_meas/T_pred       = {ratio_to_pred:+.3f}")
    print(f"  ratio T_meas/T_ref        = {ratio_to_ref:+.3f}")
    print(f"  <M>_t                     = {stats['mean_all']:+.3f}")
    print(f"  <M>_t/<M>_ref             = {stats['mean_all']/GPU_031F_MEAN:+.3f}")
    print(f"  convergence_rel           = {stats['convergence_rel']:.4f}")

    # Verdict
    if abs(ratio_to_pred - 1.0) < 0.10:
        verdict = "BOX_LOCKED"
        interp = ("Basin is a cavity k=1 eigenmode. <M>_t is NOT a particle mass. "
                  "Ring is a box-size artifact.")
    elif abs(ratio_to_ref - 1.0) < 0.10:
        verdict = "INTRINSIC_RING"
        interp = ("T_meas ~ L=20 reference. Ring has intrinsic period independent "
                  "of L. Multi-vortex hypothesis revived as L-independent.")
    else:
        verdict = "INCONCLUSIVE"
        interp = (f"T_meas not matching either prediction. May be other cavity "
                  f"mode (k=2: {L/(C_PHI)/2:.1f} lu, k=3: {L/(C_PHI)/3:.1f} lu) "
                  f"or genuinely novel physics.")

    print(f"\n  Verdict: {verdict}")
    print(f"  Interpretation: {interp}")

    # Save
    np.savez(outdir / "m_series.npz", t_p2=t_p2, m_p2=m_p2)
    np.savez(outdir / "final_state.npz",
             sm=cp.asnumpy(state['sm']), phi=cp.asnumpy(state['phi']),
             pi_m=cp.asnumpy(state['pi_m']), pi_phi=cp.asnumpy(state['pi_phi']))

    def _json_safe(v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        return v

    stats_json = {k: _json_safe(v) for k, v in stats.items()}

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'c_phi': float(C_PHI),
            'T_measured': float(T_meas),
            'T_predicted_box_k1': float(T_pred),
            'T_ref_L20': float(GPU_031F_T),
            'ratio_to_pred': float(ratio_to_pred),
            'ratio_to_ref': float(ratio_to_ref),
            'mean_all': float(stats['mean_all']),
            'mean_ref_L20': float(GPU_031F_MEAN),
            'verdict': verdict,
            'interpretation': interp,
            'stats': stats_json,
            'p2_h_samples_end': h_p2[-5:] if len(h_p2) >= 5 else h_p2,
            'wall_p1_s': wall_p1, 'wall_p2_s': wall_p2,
        }, f, indent=2)

    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
