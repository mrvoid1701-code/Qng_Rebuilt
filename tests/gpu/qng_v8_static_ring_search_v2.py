"""v8 Static-ring search v2 — extended + V_couple-free variant.

GPU-024d v1 showed the cached ring monotonically dissolves to vacuum
under v8 gradient flow (176.85 -> 19.09 in 5000 iter, still dropping).
v2 confirms:
  - (A) Extended relaxation to N=30000 (does it reach vacuum?)
  - (B) Relaxation with V_couple artificially zeroed
        (does removing sine-Gordon preserve ring topology?)

If (B) preserves a nontrivial ring but (A) dissolves -> V_couple
(the sine-Gordon Z vacuum) is the specific culprit. The ring ontology
is compatible with v8 kinetic structure; incompatible only with
V_couple as currently formulated.
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
    SIGMA_M_REF, ALPHA, BETA_M, BETA_PHI,
    nb_mean, phi_wmean_gpu, wrap_gpu,
    ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached


def F_sm_nocouple(sm, phi, nb_idx):
    """F_sm with V_couple zeroed, Channel F also off (cleanest)."""
    smb = nb_mean(sm, nb_idx)
    return ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm)


def F_phi_nocouple(sm, phi, nb_idx):
    """F_phi with V_couple zeroed."""
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    return BETA_PHI * wrap_gpu(pm - phi)


def F_sm_full(sm, phi, nb_idx, g):
    """F_sm with V_couple, no Channel F."""
    smb = nb_mean(sm, nb_idx)
    base = ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm)
    deficit = SIGMA_M_REF - sm
    F_couple = g * deficit * (1.0 - cp.cos(phi))
    return base + F_couple


def F_phi_full(sm, phi, nb_idx, g):
    """F_phi with V_couple."""
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    return BETA_PHI * wrap_gpu(pm - phi) - 0.5 * g * (deficit * deficit) * cp.sin(phi)


def force_rms(F):
    return float(cp.sqrt(cp.mean(F ** 2)))


def relax(sm_init, phi_init, nb_idx, label, force_fns, dt_relax, N_ITER,
          log_every):
    sm = sm_init.copy()
    phi = phi_init.copy()
    sm_cached = sm.copy()
    F_sm_fn, F_phi_fn = force_fns

    M0 = float(cp.sum(SIGMA_M_REF - sm))
    print(f"\n=== {label} === dt_relax={dt_relax}  N_ITER={N_ITER}")
    print(f"  init M_ring = {M0:.4f}")
    print(f"  {'iter':>6} {'M_ring':>10} {'||F_sm||':>12} {'||F_phi||':>12}")

    hist = []
    t0 = time.time()
    for it in range(N_ITER + 1):
        if it % log_every == 0:
            F_sm = F_sm_fn(sm, phi, nb_idx)
            F_phi = F_phi_fn(sm, phi, nb_idx)
            rms_sm = force_rms(F_sm)
            rms_phi = force_rms(F_phi)
            M = float(cp.sum(SIGMA_M_REF - sm))
            hist.append({'iter': it, 'M': M, 'F_sm': rms_sm, 'F_phi': rms_phi})
            print(f"  {it:>6} {M:>10.4f} {rms_sm:>12.4e} {rms_phi:>12.4e}")
            if rms_sm < 1e-7 and rms_phi < 1e-7:
                print("  CONVERGED")
                break
            if abs(M) < 0.1:
                print("  FULLY DISSOLVED")
                break
        if it == N_ITER:
            break
        F_sm = F_sm_fn(sm, phi, nb_idx)
        F_phi = F_phi_fn(sm, phi, nb_idx)
        sm = cp.clip(sm + dt_relax * F_sm, 0.0, 1.0)
        phi = wrap_gpu(phi + dt_relax * F_phi)

    wall = time.time() - t0
    M_final = float(cp.sum(SIGMA_M_REF - sm))
    F_sm_final = force_rms(F_sm_fn(sm, phi, nb_idx))
    F_phi_final = force_rms(F_phi_fn(sm, phi, nb_idx))
    diff = cp.asnumpy(sm - sm_cached)
    shape_rms = float(np.sqrt((diff ** 2).mean())) / float(SIGMA_M_REF)

    print(f"  --- FINAL: M={M_final:.4f}  ||F_sm||={F_sm_final:.4e}  "
          f"||F_phi||={F_phi_final:.4e}  shape={shape_rms:.4e}  ({wall:.1f}s)")

    return {
        'label': label,
        'M_initial': M0,
        'M_final': M_final,
        'F_sm_final': F_sm_final,
        'F_phi_final': F_phi_final,
        'shape_rms_final': shape_rms,
        'history': hist,
        'runtime_sec': wall,
    }, sm, phi


def main():
    print("=" * 80)
    print("QNG-GPU-024d v2: EXTENDED RELAXATION + V_COUPLE-FREE VARIANT")
    print("=" * 80)

    from qng_v8_canonical_gpu import G_V_COUPLE
    g = G_V_COUPLE  # default 0.22

    L = 28; R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0,
                                           verbose=True)
    M0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"  cached M_ring = {M0:.4f}")

    sm_init = ring_state['sm']
    phi_init = ring_state['phi']

    dt_relax = 0.05
    N_ITER = 30000
    LOG_EVERY = 2000

    # Run A: full V_couple, no Channel F, extended
    force_fns_A = (
        lambda sm, phi, nb: F_sm_full(sm, phi, nb, g),
        lambda sm, phi, nb: F_phi_full(sm, phi, nb, g),
    )
    result_A, sm_A, phi_A = relax(sm_init, phi_init, nb_idx,
                                   "A: v8 full (V_couple on, ChF off)",
                                   force_fns_A, dt_relax, N_ITER, LOG_EVERY)

    # Run B: V_couple OFF (G_V_COUPLE = 0), no Channel F
    force_fns_B = (
        F_sm_nocouple,
        F_phi_nocouple,
    )
    result_B, sm_B, phi_B = relax(sm_init, phi_init, nb_idx,
                                   "B: V_couple OFF (g=0, ChF off)",
                                   force_fns_B, dt_relax, N_ITER, LOG_EVERY)

    # Verdict
    STABLE_M = 50.0   # "ring survives"
    DISSOLVED_M = 1.0

    def classify(M):
        if M >= STABLE_M: return "SURVIVES"
        if M < DISSOLVED_M: return "DISSOLVED"
        return "SHRUNK"

    A_state = classify(result_A['M_final'])
    B_state = classify(result_B['M_final'])

    if A_state == "DISSOLVED" and B_state == "SURVIVES":
        verdict = "H_V_COUPLE_IS_CULPRIT"
    elif A_state == "SURVIVES":
        verdict = "H_STATIC_V8_RING_FOUND"
    elif A_state == "DISSOLVED" and B_state == "DISSOLVED":
        verdict = "H_NO_RING_IN_ANY_REGIME"
    elif A_state == "SHRUNK" or B_state == "SHRUNK":
        verdict = "H_PARTIAL_SURVIVAL"
    else:
        verdict = "H_ANOMALOUS"

    print("\n" + "=" * 80)
    print("STATIC RING SEARCH v2 SUMMARY")
    print("=" * 80)
    print(f"  A (V_couple on, g={g}): M_init={result_A['M_initial']:.2f}  "
          f"M_final={result_A['M_final']:.2f}  [{A_state}]")
    print(f"  B (V_couple OFF, g=0): M_init={result_B['M_initial']:.2f}  "
          f"M_final={result_B['M_final']:.2f}  [{B_state}]")
    print(f"  VERDICT: {verdict}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-static-ring-search-v2"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R, 'g': g, 'dt_relax': dt_relax, 'N_ITER': N_ITER,
        'M_cached': M0,
        'result_A_Vcouple_on': result_A,
        'result_B_Vcouple_off': result_B,
        'A_state': A_state,
        'B_state': B_state,
        'verdict': verdict,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    if verdict in ("H_STATIC_V8_RING_FOUND", "H_V_COUPLE_IS_CULPRIT"):
        np.savez(outdir / "relaxed_state_A.npz",
                 sm=cp.asnumpy(sm_A), phi=cp.asnumpy(phi_A))
        np.savez(outdir / "relaxed_state_B.npz",
                 sm=cp.asnumpy(sm_B), phi=cp.asnumpy(phi_B))
        print(f"  Saved relaxed states.")

    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
