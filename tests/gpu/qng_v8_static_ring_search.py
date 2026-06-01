"""v8 Static-ring search via gradient-flow relaxation.

Pre-registration: QNG-GPU-024d.

Purpose
-------
GPU-024c verdict H_NO_EQUILIBRIUM says the cached ring (formed under
v7 gradient flow) does NOT satisfy F_sm_v8 = 0 AND F_phi_v8 = 0.
Under v8 symplectic evolution, any nonzero force integrates into
pi_m, pi_phi and the ring dissolves.

This probe attempts to find the TRUE v8 static ring (if it exists):
  1. Start from cached ring (sm, phi), set pi_m=pi_phi=0
  2. Apply v8 gradient flow:
       sm  += dt_relax * F_sm_v8(sm, phi)
       phi += dt_relax * F_phi_v8(sm, phi)
  3. Monitor ||F_sm||, ||F_phi||, M_ring, ring profile sharpness
  4. Converge when ||F|| drops below threshold OR ring dissolves

Possible outcomes:
  - Converges to ring-like stationary solution -> v8 admits static ring;
    the cached state was the wrong IC. Re-cache and rerun all bending.
  - Converges to trivial vacuum (sm=sm_ref, phi=0) -> v8 3D has NO
    nontrivial ring equilibrium; dimension hypothesis promoted.
  - Diverges / oscillates -> gradient flow unstable for this config.
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
    SIGMA_M_REF, SIGMA_G_REF,
    force_sm_v8, force_phi_v8, ring_mass_deficit,
    wrap_gpu,
)
from qng_v8_ring_cache import form_ring_cached


def force_norms(sg, sm, phi, nb_idx, channel_f=True):
    F_sm  = force_sm_v8(sg, sm, phi, nb_idx, channel_f=channel_f)
    F_phi = force_phi_v8(sg, sm, phi, nb_idx)
    return (float(cp.sqrt(cp.mean(F_sm ** 2))),
            float(cp.sqrt(cp.mean(F_phi ** 2))),
            float(cp.max(cp.abs(F_sm))),
            float(cp.max(cp.abs(F_phi))))


def ring_shape_metric(sm, sm_cached):
    """RMS drift from cached ring profile."""
    diff = cp.asnumpy(sm - sm_cached)
    return float(np.sqrt((diff ** 2).mean())) / float(SIGMA_M_REF)


def main():
    print("=" * 80)
    print("QNG-GPU-024d: v8 STATIC-RING SEARCH VIA GRADIENT FLOW")
    print("  Does v8 admit a nontrivial static ring equilibrium?")
    print("=" * 80)

    L = 28; R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"  cached M_ring = {M0:.4f}")

    sg, sm, chi, phi = (ring_state['sg'], ring_state['sm'],
                         ring_state['chi'], ring_state['phi'])
    sm_cached = sm.copy()

    print("\n[Step 0] Force norms on cached ring (v8 with Channel F):")
    rms_sm, rms_phi, max_sm, max_phi = force_norms(sg, sm, phi, nb_idx,
                                                    channel_f=True)
    print(f"    ||F_sm||_RMS  = {rms_sm:.6e}   max|F_sm|  = {max_sm:.6e}")
    print(f"    ||F_phi||_RMS = {rms_phi:.6e}   max|F_phi| = {max_phi:.6e}")

    print("\n[Step 0b] Force norms on cached ring (v8 WITHOUT Channel F):")
    rms_sm0, rms_phi0, max_sm0, max_phi0 = force_norms(sg, sm, phi, nb_idx,
                                                       channel_f=False)
    print(f"    ||F_sm||_RMS  = {rms_sm0:.6e}   max|F_sm|  = {max_sm0:.6e}")
    print(f"    ||F_phi||_RMS = {rms_phi0:.6e}   max|F_phi| = {max_phi0:.6e}")

    # Main relaxation loop
    dt_relax = 0.05
    N_ITER = 5000
    LOG_EVERY = 100

    print(f"\n[Relax] dt_relax={dt_relax}  N_ITER={N_ITER}")
    print("  Using channel_f=False (cleanest v8 Hamiltonian for steady-state)")
    print(f"  {'iter':>6} {'M_ring':>10} {'||F_sm||':>12} {'||F_phi||':>12} {'RMS_drift':>10}")

    hist = []
    t0 = time.time()
    for it in range(N_ITER + 1):
        if it % LOG_EVERY == 0:
            rms_sm, rms_phi, _, _ = force_norms(sg, sm, phi, nb_idx,
                                                 channel_f=False)
            M = float(cp.sum(SIGMA_M_REF - sm))
            shape = ring_shape_metric(sm, sm_cached)
            hist.append({'iter': it, 'M_ring': M, 'F_sm_rms': rms_sm,
                         'F_phi_rms': rms_phi, 'shape_rms': shape})
            print(f"  {it:>6} {M:>10.4f} {rms_sm:>12.4e} {rms_phi:>12.4e} {shape:>10.4e}")
            if rms_sm < 1e-6 and rms_phi < 1e-6:
                print("  CONVERGED (||F|| < 1e-6)")
                break
            if abs(M) < 1.0:
                print("  RING DISSOLVED (|M_ring| < 1)")
                break
        if it == N_ITER:
            break

        # Gradient flow step (channel_f=False for cleanest Hamiltonian)
        F_sm  = force_sm_v8(sg, sm, phi, nb_idx, channel_f=False)
        F_phi = force_phi_v8(sg, sm, phi, nb_idx)
        sm  = cp.clip(sm + dt_relax * F_sm, 0.0, 1.0)
        phi = wrap_gpu(phi + dt_relax * F_phi)

    wall = time.time() - t0
    print(f"\n  Relaxation complete: {wall:.1f}s")

    final_M = float(cp.sum(SIGMA_M_REF - sm))
    final_shape = ring_shape_metric(sm, sm_cached)
    final_rms_sm, final_rms_phi, _, _ = force_norms(sg, sm, phi, nb_idx,
                                                     channel_f=False)

    # Verdict
    if final_rms_sm < 1e-4 and final_rms_phi < 1e-4 and abs(final_M) > 50:
        verdict = "H_STATIC_RING_FOUND"
    elif abs(final_M) < 1.0:
        verdict = "H_NO_NONTRIVIAL_EQUILIBRIUM"
    elif final_rms_sm > 1e-2:
        verdict = "H_RELAXATION_DIVERGED"
    else:
        verdict = "H_INCONCLUSIVE"

    print("\n" + "=" * 80)
    print("STATIC RING SEARCH SUMMARY")
    print("=" * 80)
    print(f"  Initial M_ring  = {M0:.4f}")
    print(f"  Final   M_ring  = {final_M:.4f}")
    print(f"  Final ||F_sm||  = {final_rms_sm:.6e}")
    print(f"  Final ||F_phi|| = {final_rms_phi:.6e}")
    print(f"  Final shape RMS drift = {final_shape:.4e}")
    print(f"  VERDICT: {verdict}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-static-ring-search-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'dt_relax': dt_relax, 'N_ITER': N_ITER,
        'M_ring_initial': M0,
        'F_cached_v8_chF':    {'rms_sm': rms_sm,  'rms_phi': rms_phi,
                                'max_sm': max_sm,  'max_phi': max_phi},
        'F_cached_v8_noChF':  {'rms_sm': rms_sm0, 'rms_phi': rms_phi0,
                                'max_sm': max_sm0, 'max_phi': max_phi0},
        'relaxation_history': hist,
        'M_ring_final': final_M,
        'shape_rms_final': final_shape,
        'F_final': {'rms_sm': final_rms_sm, 'rms_phi': final_rms_phi},
        'verdict': verdict,
        'runtime_sec': wall,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Save relaxed state if converged (for re-cache)
    if verdict == "H_STATIC_RING_FOUND":
        np.savez(outdir / "relaxed_ring_state.npz",
                 sg=cp.asnumpy(sg), sm=cp.asnumpy(sm),
                 chi=cp.asnumpy(chi), phi=cp.asnumpy(phi))
        print(f"  Saved relaxed ring state.")

    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
