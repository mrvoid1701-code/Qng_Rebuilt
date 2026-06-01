"""QNG-CPU-074 / DER-QNG-050 regression: does exact F_A shift M_ring?

Question: under DER-QNG-050 exact Channel A, does the canonical T_P2=1000
M_ring value at L=20 R=4 shift significantly vs the CPU-074 baseline
(728.92) computed with the uniform-sigma_m approximation?

Protocol:
  - Form R=4 ring at L=20 via the canonical three-phase protocol twice:
    (i)  approx mode:  exact_a=False  (baseline, matches CPU-074)
    (ii) exact mode:   exact_a=True   (DER-QNG-050)
  - Report M_ring at T_P2=300, 500, 700, 1000; diff vs CPU-074 canonical.

Interpretation:
  * |dM_ring|/M_0 < 5 %   -> DER-QNG-038 baryon ladder largely preserved
  * 5 % - 20 %            -> recalibration needed (a_M shifts by same fraction)
  * > 20 %                -> baryon identification must be redone end-to-end

Note: this is L=20 not L=28 (GPU-031c cache) because CPU-074 values were
measured at L=20. For phase-space orbit comparison, see GPU-031c.
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
    ring_mass_deficit, SIGMA_M_REF, CHI_DECAY_V7,
)

CPU_074_CANONICAL = {3: 474.15, 4: 728.92, 5: 954.88}


def form_ring_and_sample(L, R, T_P1, T_P2, DT, exact_a,
                         sample_times=(300.0, 500.0, 700.0, 1000.0),
                         verbose=True):
    """Form ring and record M_ring at the requested T_P2 snapshots."""
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT)
    results = {}
    t0 = time.time()

    for _ in range(n1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                              chi_decay=CHI_DECAY_V7, exact_a=exact_a)

    sample_steps = {int(round(T / DT)): T for T in sample_times}
    max_step = max(sample_steps.keys())

    for s in range(1, max_step + 1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7, exact_a=exact_a)
        if s in sample_steps:
            M = float(ring_mass_deficit(state['sm']))
            results[sample_steps[s]] = M
            if verbose:
                print(f"    T_P2={sample_steps[s]:6.1f} lu   M_ring={M:9.4f}")

    wall = time.time() - t0
    if verbose:
        print(f"    wall {wall/60:.1f} min")
    return results, wall


def main():
    print("=" * 80)
    print("QNG-CPU-074 regression: DER-QNG-050 exact_a impact on M_ring")
    print("=" * 80)

    L = 20
    R = 4
    T_P1 = 300.0
    T_P2_MAX = 1000.0
    DT = 0.025

    outdir = ROOT / "07_validation" / "audits" / "qng-der050-mring-regression-v1"
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n  L={L}, R={R}, T_P1={T_P1}, T_P2_max={T_P2_MAX}, DT={DT}")
    print(f"  CPU-074 canonical M_ring @ T_P2=1000 = {CPU_074_CANONICAL[R]}")

    print("\n  [approx] exact_a=False (baseline, uniform-sigma_m F_A)")
    approx_M, wall_a = form_ring_and_sample(L, R, T_P1, T_P2_MAX, DT,
                                             exact_a=False)

    print("\n  [exact ] exact_a=True  (DER-QNG-050)")
    exact_M, wall_e = form_ring_and_sample(L, R, T_P1, T_P2_MAX, DT,
                                            exact_a=True)

    print("\n" + "=" * 80)
    print("COMPARISON (L=20 R=4)")
    print("=" * 80)
    print(f"  {'T_P2':>6s}  {'approx':>10s}  {'exact':>10s}  "
          f"{'diff':>10s}  {'rel %':>8s}")
    rows = []
    for T in sorted(approx_M.keys()):
        a = approx_M[T]
        e = exact_M[T]
        d = e - a
        r = 100.0 * d / max(abs(a), 1e-10)
        rows.append({'T_P2': T, 'approx': a, 'exact': e, 'diff': d, 'rel_pct': r})
        print(f"  {T:6.1f}  {a:10.4f}  {e:10.4f}  {d:+10.4f}  {r:+8.2f}")

    final_rel = rows[-1]['rel_pct']
    if abs(final_rel) < 5.0:
        verdict = "H_PRESERVED"
        diag = (f"|dM_ring/M| = {abs(final_rel):.2f}% at T_P2=1000. "
                "DER-QNG-038 baryon ladder survives DER-QNG-050 without "
                "recalibration.")
    elif abs(final_rel) < 20.0:
        verdict = "H_RECAL_NEEDED"
        diag = (f"|dM_ring/M| = {abs(final_rel):.2f}% at T_P2=1000. "
                "a_M must be rescaled; nucleon/delta families still match "
                "qualitatively.")
    else:
        verdict = "H_LADDER_BROKEN"
        diag = (f"|dM_ring/M| = {abs(final_rel):.2f}% at T_P2=1000. "
                "Baryon identification must be redone end-to-end under "
                "the exact canonical action.")

    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2_max': T_P2_MAX, 'DT': DT,
            'cpu_074_canonical_M_ring': CPU_074_CANONICAL[R],
            'wall_approx_min': wall_a / 60,
            'wall_exact_min':  wall_e / 60,
            'samples': rows,
            'verdict': verdict,
            'diagnosis': diag,
        }, f, indent=2)
    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
