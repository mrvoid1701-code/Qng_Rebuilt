"""Tesla gauge-invariance probe — does chi act as U(1) gauge connection?

Hypothesis (tesla-mind, symmetry-hunt-v8.md 2026-04-20):
  psi_m = sigma_m * exp(i*phi) is a complex matter scalar.
  chi is the U(1) connection (time component).
  Gauge transformation: psi_m -> exp(i*alpha(x,t)) * psi_m
                        phi    -> phi + alpha(x,t)
                        chi    -> chi - (d_t alpha)/K_BACK
  sigma_g, sigma_m: gauge-invariant (magnitudes).

If v8 IS U(1)-gauge invariant, observables M_ring and H_v8 must be
alpha-invariant up to numerical noise (< 0.1%).

Test protocol:
  1. Form ring R=4 (Phase 1 + Phase 2, short).
  2. Take snapshot state S at end of P2.
  3. For each alpha configuration, build gauged state S' by
     - phi' = phi + alpha(x, 0)
     - chi' = chi - (d_t alpha at t=0) / K_BACK
  4. Evolve S and S' for 200 more lu under standard v8 dynamics.
  5. Compare M_ring(S_ev) vs M_ring(S'_ev) and H(S_ev) vs H(S'_ev).

Four test cases:
  (A) alpha = 0                          [baseline — obviously invariant]
  (B) alpha = 2*pi                       [trivial winding: exactly invariant]
  (C) alpha = 0.5 (rigid global)         [global U(1) test]
  (D) alpha(x) = 0.5*cos(2*pi*x/L)       [local spatial U(1) test]

VERDICT:
  - All match baseline < 0.1%:        v8 is locally U(1) gauge invariant.
    Tesla hypothesis CONFIRMED.
  - Only (A), (B) match; (C), (D) fail: V_couple explicitly breaks U(1).
    Tesla hypothesis FALSIFIED for current v8.
  - (C) matches but (D) fails:        global U(1) yes, local no.
    chi is Hamiltonian conjugate only, not a gauge field.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

import qng_v8_canonical_gpu as v8
from qng_v8_canonical_gpu import (
    SIGMA_G_REF, SIGMA_M_REF, K_BACK, CHI_DECAY_V7,
    yoshida4_step, hamiltonian_v8, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def apply_gauge(state, alpha, dt_alpha_at_0):
    """S' = (sg, sm, chi - dt_alpha/K_BACK, phi + alpha). Returns new state."""
    out = clone_state(state)
    out['phi'] = out['phi'] + alpha
    out['chi'] = out['chi'] - dt_alpha_at_0 / float(K_BACK)
    return out


def evolve(state, nb_idx, T, verbose=False, label=''):
    n = int(T / DT)
    for _ in range(n):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    if verbose:
        print(f"    evolved {label}: {n} steps done")
    return state


def compare(state_a, state_b, nb_idx, label_b):
    Ma = ring_mass_deficit(state_a['sm'])
    Mb = ring_mass_deficit(state_b['sm'])
    Ha = hamiltonian_v8(state_a, nb_idx)
    Hb = hamiltonian_v8(state_b, nb_idx)
    dM = (Mb - Ma) / max(abs(Ma), 1e-12)
    dH = (Hb - Ha) / max(abs(Ha), 1e-12)
    # Field-level L2 distance (per node)
    dsm = float(cp.sqrt(cp.mean((state_b['sm'] - state_a['sm']) ** 2)))
    dsg = float(cp.sqrt(cp.mean((state_b['sg'] - state_a['sg']) ** 2)))
    return {
        'label': label_b,
        'M_a': Ma, 'M_b': Mb, 'dM_frac': dM,
        'H_a': Ha, 'H_b': Hb, 'dH_frac': dH,
        'dsm_rms': dsm, 'dsg_rms': dsg,
    }


def main():
    print("=" * 80)
    print("Tesla gauge-invariance probe (U(1) symmetry test)")
    print("=" * 80)
    print(f"  K_BACK={K_BACK}  CHI_DECAY={CHI_DECAY_V7}")
    print(f"  Hypothesis: psi_m = sm*exp(i*phi); phi -> phi + alpha(x,t),")
    print(f"              chi -> chi - d_t alpha / K_BACK.")
    print()

    L = 20
    R = 4
    T_P3 = 200.0   # extra evolution after gauge transform
    N = L * L * L

    # --- Form ring ---
    print(f"[1] Forming ring L={L}, R={R} (P1=300, P2=500 lu) [cache-backed]")
    ref_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=500.0,
                                          verbose=True)
    M_ref = ring_mass_deficit(ref_state['sm'])
    H_ref = hamiltonian_v8(ref_state, nb_idx)
    print(f"  Post-P2 state: M_ring={M_ref:.4f}  H={H_ref:.4f}")
    print()

    # --- Evolve baseline ---
    print(f"[2] Baseline evolution (+{T_P3:.0f} lu, no gauge) ...")
    t0 = time.time()
    baseline = evolve(clone_state(ref_state), nb_idx, T_P3)
    print(f"    wall={time.time()-t0:.1f}s")
    M_base = ring_mass_deficit(baseline['sm'])
    H_base = hamiltonian_v8(baseline, nb_idx)
    print(f"    baseline_evolved: M={M_base:.4f}  H={H_base:.4f}")
    print()

    # --- Coordinate helper for spatial alpha ---
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)

    # --- Gauge test cases ---
    cases = []
    # (B) Trivial winding: alpha = 2*pi everywhere, d_t alpha = 0
    cases.append(("B: alpha = 2*pi (trivial)",
                  cp.full(N, 2.0 * cp.pi, dtype=cp.float64),
                  cp.zeros(N, dtype=cp.float64)))
    # (C) Rigid global: alpha = 0.5 everywhere, d_t alpha = 0
    cases.append(("C: alpha = 0.5 (rigid global)",
                  cp.full(N, 0.5, dtype=cp.float64),
                  cp.zeros(N, dtype=cp.float64)))
    # (D) Local spatial: alpha(x) = 0.5*cos(2*pi*x/L), d_t alpha = 0
    alpha_D = 0.5 * cp.cos(2.0 * cp.pi * x / L)
    cases.append(("D: alpha = 0.5*cos(2pi x/L) (local spatial)",
                  alpha_D,
                  cp.zeros(N, dtype=cp.float64)))
    # (E) Time-only: alpha(t) = 0.5*sin(0.1*t) so alpha(0)=0, d_t alpha(0)=0.05
    cases.append(("E: alpha(t) = 0.5*sin(0.1 t), d_t alpha(0)=0.05",
                  cp.zeros(N, dtype=cp.float64),
                  cp.full(N, 0.05, dtype=cp.float64)))

    print(f"[3] Gauge cases ({len(cases)} runs, +{T_P3:.0f} lu each)")
    print(f"{'case':<44} {'dM/M':>12} {'dH/H':>12} {'dsm_rms':>10}  verdict")
    print("-" * 90)

    results = []
    for lbl, alpha, dt_alpha in cases:
        t0 = time.time()
        s_gauged = apply_gauge(ref_state, alpha, dt_alpha)
        s_ev = evolve(s_gauged, nb_idx, T_P3)
        cmp = compare(baseline, s_ev, nb_idx, lbl)
        results.append(cmp)
        ok = abs(cmp['dM_frac']) < 1e-3 and abs(cmp['dH_frac']) < 1e-3
        verdict = 'INVARIANT' if ok else 'BROKEN   '
        print(f"{lbl:<44} {cmp['dM_frac']*100:>11.4f}% "
              f"{cmp['dH_frac']*100:>11.4f}% {cmp['dsm_rms']:>10.2e}  {verdict}  "
              f"({time.time()-t0:.1f}s)")

    # --- Verdict ---
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)

    B_ok = abs(results[0]['dM_frac']) < 1e-3 and abs(results[0]['dH_frac']) < 1e-3
    C_ok = abs(results[1]['dM_frac']) < 1e-3 and abs(results[1]['dH_frac']) < 1e-3
    D_ok = abs(results[2]['dM_frac']) < 1e-3 and abs(results[2]['dH_frac']) < 1e-3
    E_ok = abs(results[3]['dM_frac']) < 1e-3 and abs(results[3]['dH_frac']) < 1e-3

    if B_ok and C_ok and D_ok and E_ok:
        print("FULL U(1) GAUGE INVARIANCE CONFIRMED. Tesla hypothesis PASS.")
        print("  -> chi acts as U(1)_g connection.")
        print("  -> psi_m = sigma_m*exp(i*phi) is a genuine complex scalar field.")
        print("  -> v8 action is locally gauge invariant.")
    elif B_ok and C_ok and not D_ok:
        print("GLOBAL U(1) OK, LOCAL U(1) BROKEN.")
        print("  -> chi is NOT a true gauge connection (no spatial components).")
        print("  -> v8 has global phase symmetry only.")
        print("  -> Tesla hypothesis PARTIAL (global U(1)_g survives, local fails).")
    elif B_ok and not C_ok:
        print("V_COUPLE EXPLICITLY BREAKS U(1). Tesla hypothesis FALSIFIED for v8.")
        print("  -> V_couple = (g/2)*deficit^2*(1-cos phi) is not gauge covariant.")
        print("  -> Only trivial winding alpha=2*pi*n preserves the action.")
        print("  -> Fix would require replacing V_couple with |psi|^2-only potentials")
        print("     plus cavity quantization for mass generation.")
    else:
        print("UNEXPECTED PATTERN. Investigate per-case output.")

    print()
    print("Observables (reference):")
    print(f"  H_ref (pre-gauge)           = {H_ref:.4f}")
    print(f"  M_ref (pre-gauge)           = {M_ref:.4f}")
    print(f"  H_baseline (+{T_P3:.0f} lu)          = {H_base:.4f}")
    print(f"  M_baseline (+{T_P3:.0f} lu)          = {M_base:.4f}")


if __name__ == "__main__":
    main()
