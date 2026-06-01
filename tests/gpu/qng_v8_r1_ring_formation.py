"""QNG-GPU-031e: Ring formation under DER-QNG-051 Option R1 (pure-XY E_phi).

Background: GPU-031c/d showed DER-QNG-036 §2.4 E_phi with sigma_m weighting
has no bounded ground state under canonical dynamics (DER-QNG-051): the
back-reaction F_sm_XY = +(2 beta_DER/z) * R_k * cos(phi_k - Theta_k)
drives sigma_m -> 1 everywhere, dissolving any ring.

Option R1: drop sigma_m weights in E_phi,
    E_phi_R1 = -(beta_R1 / z) * sum_{i, j~i} cos(phi_i - phi_j)
with beta_R1 = BETA_PHI/2 so F_A_R1 matches the uniform-sm approx in
the small-angle limit. sigma_m decouples from E_phi (dE_phi/dsigma_m = 0),
so no F_XY_sm term.

Question: under R1, can the Phase-1+2 protocol still produce a ring, and is
it stable over Phase-2 run-time?

Verdicts:
  * H_R1_RING_FORMS:  M_ring(t=1000) within +-20% of CPU-074 baseline
                      and drift < 20%. sigma_m weight in E_phi was
                      decorative; DER-QNG-038 baryon ladder candidate for
                      reinstatement under R1 action.
  * H_R1_RING_SHIFTED: ring forms but M_ring differs substantially; a_M
                       must be recalibrated.
  * H_R1_NO_RING:     M_ring(t=1000) < 10, i.e. ring never formed or
                       dissolved before P2 ends. Indicates the sigma_m
                       weighting was essential for the ring mechanism;
                       R4 (v9 unification) locked.

Protocol: same L=20 R=4 three-phase formation used for GPU-031d, but
exact_a='r1' throughout.
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
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    SIGMA_M_REF, CHI_DECAY_V7, MU_M, MU_PHI,
)

CPU_074_R4 = 728.92
EXACT_A_MODE = 'r1'


def run_phase(state, nb_idx, n_steps, DT, v_couple_on, exact_a,
              sample_every=None, verbose=True):
    t0 = time.time()
    samples = []
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=v_couple_on, chi_decay=CHI_DECAY_V7,
                              exact_a=exact_a)
        if sample_every is not None and s % sample_every == 0:
            t_phys = s * DT
            M = float(ring_mass_deficit(state['sm']))
            H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                               exact_a=exact_a)
            sm_min = float(cp.min(state['sm']))
            sm_max = float(cp.max(state['sm']))
            T_m = float((1.0/(2.0*MU_M))*cp.sum(state['pi_m']**2))
            T_phi = float((1.0/(2.0*MU_PHI))*cp.sum(state['pi_phi']**2))
            samples.append({'t': t_phys, 'M_ring': M, 'H': H,
                           'sm_min': sm_min, 'sm_max': sm_max,
                           'T_m': T_m, 'T_phi': T_phi})
            if verbose:
                print(f"    t={t_phys:6.1f}  M={M:+9.3f}  H={H:+10.2f}  "
                      f"sm=[{sm_min:.3f},{sm_max:.3f}]  "
                      f"T_m={T_m:8.3f} T_phi={T_phi:8.3f}", flush=True)
    wall = time.time() - t0
    return state, samples, wall


def main():
    print("=" * 80)
    print("QNG-GPU-031e: ring formation under DER-QNG-051 Option R1 (pure XY)")
    print("=" * 80)

    L = 20
    R = 4
    T_P1 = 300.0
    T_P2 = 1000.0
    DT = 0.025
    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-r1-ring-formation-v1"
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n  L={L}, R={R}, T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")
    print(f"  exact_a={EXACT_A_MODE!r} (pure XY, no sigma_m weights in E_phi)")
    print(f"  CPU-074 R=4 canonical (approx) M_ring = {CPU_074_R4:.2f}")

    # --- Phase 1: phi vortex ---
    print("\n  [Phase 1] v_couple_on=False, exact_a='r1'")
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)

    M0 = float(ring_mass_deficit(state['sm']))
    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)
    print(f"    init:  M_ring={M0:+.3f}  H={H0:+.3f}")
    state, p1_samples, wall_p1 = run_phase(state, nb_idx, n1, DT,
                                          v_couple_on=False,
                                          exact_a=EXACT_A_MODE,
                                          sample_every=n1 // 3, verbose=True)
    M_p1 = float(ring_mass_deficit(state['sm']))
    print(f"    end P1: M_ring={M_p1:+.3f}  wall={wall_p1:.1f}s")

    # --- Phase 2: ring formation (or not) ---
    print("\n  [Phase 2] v_couple_on=True, exact_a='r1'")
    sample_every_2 = int(100.0 / DT)  # every 100 lu
    state, p2_samples, wall_p2 = run_phase(state, nb_idx, n2, DT,
                                          v_couple_on=True,
                                          exact_a=EXACT_A_MODE,
                                          sample_every=sample_every_2,
                                          verbose=True)

    final_M = float(ring_mass_deficit(state['sm']))
    final_H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                             exact_a=EXACT_A_MODE)

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    print(f"  End-of-run M_ring       = {final_M:+.3f}")
    print(f"  End-of-run H            = {final_H:+.3f}")
    print(f"  CPU-074 approx baseline = {CPU_074_R4:.3f}")
    print(f"  Relative diff vs CPU-074: {100.0*(final_M-CPU_074_R4)/CPU_074_R4:+.2f}%")

    p2_Ms = [s['M_ring'] for s in p2_samples]
    m_late = p2_Ms[-5:] if len(p2_Ms) >= 5 else p2_Ms
    drift_pct = 100.0 * (max(m_late) - min(m_late)) / max(abs(np.mean(m_late)), 1e-10)

    if abs(final_M) < 10.0:
        verdict = "H_R1_NO_RING"
        diag = ("No ring formed under R1. sigma_m weighting in E_phi was "
                "essential for the ring mechanism. R4 (v9 unification) locked.")
    elif abs(final_M - CPU_074_R4) / CPU_074_R4 < 0.2 and drift_pct < 20.0:
        verdict = "H_R1_RING_FORMS"
        diag = (f"Ring forms under R1 with |dM|<20%. sigma_m weighting in "
                f"E_phi was decorative; DER-QNG-038 baryon ladder candidate "
                f"for reinstatement. a_M shift "
                f"{100.0*(final_M-CPU_074_R4)/CPU_074_R4:+.1f}%.")
    elif drift_pct > 50.0:
        verdict = "H_R1_RING_UNSTABLE"
        diag = (f"Ring forms but M_ring drifts {drift_pct:.1f}% over last "
                f"500 lu; no stable equilibrium under R1.")
    else:
        verdict = "H_R1_RING_SHIFTED"
        diag = (f"Ring forms with different M_ring; a_M must be recalibrated. "
                f"Drift {drift_pct:.1f}% suggests orbital motion.")

    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    np.savez(outdir / "final_state.npz",
             sm=cp.asnumpy(state['sm']), phi=cp.asnumpy(state['phi']),
             pi_m=cp.asnumpy(state['pi_m']), pi_phi=cp.asnumpy(state['pi_phi']))

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'cpu_074_canonical_M_ring': CPU_074_R4,
            'final_M_ring': final_M,
            'final_H': final_H,
            'p1_samples': p1_samples,
            'p2_samples': p2_samples,
            'late_drift_pct': drift_pct,
            'verdict': verdict,
            'diagnosis': diag,
            'wall_p1_s': wall_p1, 'wall_p2_s': wall_p2,
        }, f, indent=2)
    print(f"\n  Report:      {outdir / 'report.json'}")
    print(f"  Final state: {outdir / 'final_state.npz'}")


if __name__ == "__main__":
    main()
