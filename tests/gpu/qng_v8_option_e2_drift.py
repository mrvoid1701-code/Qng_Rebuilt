"""Option E^2 drift diagnostic: perturbed initial state so H0 != 0.

option_e2_probe.py reported drift ~7e12 because H0 is exactly zero at t=0
(sigma_g=sg_ref, sm=sm_ref, chi=0, pi=0, V_couple=0 on unperturbed ring).
Relative drift formula divides by max(|H0|, 1e-12), producing the artifact.

This probe adds a small Gaussian perturbation to (sm, pi_m, pi_phi) so H0
carries a finite physical scale, then measures absolute and relative drift.

Expected (Yoshida 4th-order symplectic):
    |dH/H| <~ O(dt^4)  with bounded oscillation, NOT secular growth.
    At dt=0.025 with our parameters -> |drift| should be well under 1%.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

# Reuse Option E^2 overrides
import qng_v8_option_e2_probe  # installs overrides on import
import qng_v8_canonical_gpu as v8
from qng_v8_canonical_gpu import (
    SIGMA_G_REF, SIGMA_M_REF,
    build_nb, init_phi_single_ring, make_state,
    yoshida4_step, SIGMA_G_MIN_ABORT,
)


def probe_perturbed(dt, L=16, R=4, t_max=20.0, seed=42, tag=""):
    nsteps = int(t_max / dt)
    nb = build_nb(L)
    phi0 = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi0)

    # Small perturbation so H0 carries a physical scale.
    rng = cp.random.RandomState(seed)
    state['sm']     += 0.01 * rng.standard_normal(state['sm'].shape, dtype=cp.float32)
    state['pi_m']   += 0.01 * rng.standard_normal(state['pi_m'].shape, dtype=cp.float32)
    state['pi_phi'] += 0.01 * rng.standard_normal(state['pi_phi'].shape, dtype=cp.float32)

    H0 = v8.hamiltonian_v8(state, nb)
    sg_min0 = float(cp.min(state['sg']))

    H_trace = [H0]
    t_trace = [0.0]
    sample = max(1, nsteps // 20)

    t0 = time.time()
    for s in range(1, nsteps + 1):
        state = yoshida4_step(state, dt, nb, k_gm=0.0,
                              damping_gamma=0.0, v_couple_on=True)
        if s % sample == 0 or s == nsteps:
            H_trace.append(v8.hamiltonian_v8(state, nb))
            t_trace.append(s * dt)

    wall = time.time() - t0
    H_final = H_trace[-1]
    H_max = max(H_trace)
    H_min = min(H_trace)
    drift_rel = (H_final - H0) / abs(H0) if abs(H0) > 1e-8 else float('nan')
    oscillation = (H_max - H_min) / abs(H0) if abs(H0) > 1e-8 else float('nan')

    return {
        'tag': tag, 'dt': dt, 'L': L,
        'H0': H0, 'H_final': H_final,
        'H_max': H_max, 'H_min': H_min,
        'drift_abs': H_final - H0,
        'drift_rel': drift_rel,
        'oscillation_rel': oscillation,
        'sg_min0': sg_min0,
        'sg_min_final': float(cp.min(state['sg'])),
        'wall': wall,
    }


def main():
    print("=" * 78)
    print("Option E^2 drift diagnostic (perturbed IC, seed=42)")
    print("=" * 78)
    print(f"  Perturbation: N(0, 0.01) on sm, pi_m, pi_phi")
    print(f"  Integrator:   Yoshida 4th-order symplectic")
    print(f"  Expected:     |drift_rel| ~ O(dt^4), bounded oscillation, no secular growth")
    print()

    configs = [
        (0.025, 16, "L=16, dt=0.025"),
        (0.010, 16, "L=16, dt=0.010"),
        (0.005, 16, "L=16, dt=0.005"),
        (0.025, 32, "L=32, dt=0.025"),
    ]

    results = []
    for dt, L, tag in configs:
        print(f"  [{tag}]")
        r = probe_perturbed(dt, L=L, R=4, t_max=20.0, tag=tag)
        results.append(r)
        print(f"     wall={r['wall']:.1f}s  H0={r['H0']:.4e}  H_final={r['H_final']:.4e}")
        print(f"     drift_abs={r['drift_abs']:+.3e}  drift_rel={r['drift_rel']:+.3e}  "
              f"oscillation={r['oscillation_rel']:+.3e}")
        print(f"     sg_min0={r['sg_min0']:.4f}  sg_min_final={r['sg_min_final']:.4f}")
        print()

    print("=" * 78)
    print("VERDICT")
    print("=" * 78)

    # Order-of-accuracy check on L=16
    L16 = [r for r in results if r['L'] == 16]
    drifts = [abs(r['drift_rel']) for r in L16]
    print("L=16 drift ratios (should scale ~dt^4 -> factor ~625 between dt=0.025 and dt=0.005):")
    if drifts[0] > 1e-12 and drifts[2] > 1e-12:
        ratio = drifts[0] / drifts[2]
        print(f"  |drift(dt=0.025)| / |drift(dt=0.005)| = {ratio:.1f}")
        print(f"  (perfect 4th-order would give 625; good symplectic: 100-1000)")

    max_drift = max(abs(r['drift_rel']) for r in results)
    max_osc   = max(abs(r['oscillation_rel']) for r in results)

    print()
    print(f"Max |drift_rel|      = {max_drift:.3e}")
    print(f"Max |oscillation_rel| = {max_osc:.3e}")
    print()

    if max_drift < 0.01 and max_osc < 0.05:
        print("OPTION E^2 DRIFT CONFIRMED BOUNDED:")
        print("  - Secular drift < 1% over t=20 (symplectic integrator working).")
        print("  - Oscillation bounded < 5% (physical, not numerical).")
        print("  -> Option E^2 is numerically sound. DER-QNG-042 amendment CONFIRMED.")
    elif max_drift < 0.05:
        print("OPTION E^2 ACCEPTABLE: drift < 5%, integrator stable.")
        print("  -> Amendment can proceed; note drift in audit.")
    else:
        print(f"OPTION E^2 DRIFT HIGH: {max_drift:.3e}")
        print("  -> Investigate integrator / dt before amendment.")


if __name__ == "__main__":
    main()
