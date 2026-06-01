"""Weak Equivalence Principle probe for v8 rings (Einstein test #3).

Einstein's WEP: all bodies in the same gravitational field experience the
same acceleration, independent of mass or internal composition.

v8 test:
  - Form ring R (R=3 or R=5) in center of L=24 box.
  - Apply uniform external "gravitational" gradient via pi_m kick:
      pi_m_i += dt * g_ext * (x_i - L/2)/L
    Sign chosen so rings drift toward -x if g_ext > 0.
    The potential is V_ext = -(g_ext/L) * sum(x * (SIGMA_M_REF - sm));
    force per node on sm is d(pi_m)/dt = -g_ext * (x-L/2)/L.
  - Track ring centroid X_c(t) = sum((SIGMA_M_REF - sm) * x) / M_ring.
  - Fit X_c(t) to parabola: X_c = X_0 + V_0*t + 0.5*a*t^2.
  - Compare a(R=3) vs a(R=5).

VERDICT:
  |a(3) - a(5)| / mean(a) < 10%  -> WEP PASS (Einstein-compatible)
                         > 10%  -> WEP FAIL (ring size affects free fall)

Implementation note: We split external kick from internal yoshida4 step via
Strang splitting: half-kick -> yoshida4 -> half-kick.  This preserves 2nd
order accuracy even though yoshida4 itself is 4th.
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
    SIGMA_M_REF, K_BACK, CHI_DECAY_V7,
    yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025


def ring_centroid_x(sm, x_coords, L):
    """Return center-of-deficit X_c = sum(deficit * x) / sum(deficit).

    Uses the minimum-image convention on a periodic lattice by first
    shifting so the box is centered on the largest-deficit cell.
    Simpler: since ring stays near L/2 for short drifts we just use direct x.
    """
    deficit = SIGMA_M_REF - sm
    M = cp.sum(deficit)
    if float(M) < 1e-12:
        return float('nan')
    Xc = cp.sum(deficit * x_coords) / M
    return float(Xc)


def evolve_with_ext(state, nb_idx, T, x_coords, L, g_ext, sample_every,
                    verbose=False, label=''):
    """Evolve under v8 + external uniform gradient, sampling X_c periodically.

    External force (Strang split):
      pi_m += 0.5 * dt * F_ext
      yoshida4_step(...)
      pi_m += 0.5 * dt * F_ext
    where F_ext_i = -g_ext * (x_i - L/2) / L.
    """
    n = int(T / DT)
    F_ext = -g_ext * (x_coords - 0.5 * L) / L   # shape (N,)
    half_kick = 0.5 * DT * F_ext

    t_samples = []
    Xc_samples = []
    M_samples = []

    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_samples.append(s * DT)
            Xc_samples.append(ring_centroid_x(state['sm'], x_coords, L))
            M_samples.append(float(ring_mass_deficit(state['sm'])))
        # Half kick
        state['pi_m'] = state['pi_m'] + half_kick
        # Yoshida full step
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=0.0)   # conservative during probe
        # Half kick
        state['pi_m'] = state['pi_m'] + half_kick
    # Final sample
    t_samples.append(n * DT)
    Xc_samples.append(ring_centroid_x(state['sm'], x_coords, L))
    M_samples.append(float(ring_mass_deficit(state['sm'])))

    wall = time.time() - t0
    if verbose:
        print(f"    evolved {label}: {n} steps done ({wall:.1f}s)")
    return state, np.array(t_samples), np.array(Xc_samples), np.array(M_samples)


def fit_quadratic(t, x):
    """Fit x(t) = X_0 + V_0*t + 0.5*a*t^2. Return (X_0, V_0, a)."""
    coeffs = np.polyfit(t, x, 2)
    a2, a1, a0 = coeffs
    return a0, a1, 2.0 * a2


def run_case(L, R, g_ext, x_coords, T_track=300.0, sample_every=40):
    print(f"\n--- R={R}, g_ext={g_ext:+.4f} ---")
    state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=500.0,
                                      verbose=True)
    M_ring0 = float(ring_mass_deficit(state['sm']))
    Xc0 = ring_centroid_x(state['sm'], x_coords, L)
    print(f"  Pre-track: M_ring={M_ring0:.2f}  X_c={Xc0:.4f}")

    _, t, Xc, M = evolve_with_ext(state, nb_idx, T_track, x_coords, L,
                                  g_ext=g_ext, sample_every=sample_every,
                                  verbose=True, label=f"R={R} g={g_ext}")
    # Fit
    X0, V0, a = fit_quadratic(t, Xc)
    print(f"  Fit:  X_0={X0:.4f}  V_0={V0:+.6f}  a={a:+.6e}")
    print(f"  Final: M_ring={M[-1]:.2f}  (drift {(M[-1]-M[0])/M[0]*100:+.2f}%)")

    # Diagnostic: print X_c at a few times
    idx_samples = [0, len(t)//4, len(t)//2, 3*len(t)//4, len(t)-1]
    for i in idx_samples:
        print(f"    t={t[i]:6.1f}  X_c={Xc[i]:.4f}  M={M[i]:.2f}")
    return {'R': R, 'g_ext': g_ext, 't': t, 'Xc': Xc, 'M': M,
            'X0': X0, 'V0': V0, 'a': a, 'M_ring0': M_ring0}


def main():
    print("=" * 80)
    print("Einstein test #3: Weak Equivalence Principle (WEP)")
    print("=" * 80)
    print(f"  K_BACK={K_BACK}  CHI_DECAY=0 (conservative probe)")
    print(f"  Question: does a(R=3) = a(R=5) in same external gradient?")
    print()

    L = 24
    g_ext = 0.02
    T_track = 300.0
    sample_every = 40   # every 1 lu

    # Coordinate helper
    N = L * L * L
    idx = cp.arange(N, dtype=cp.int64)
    x_coords = (idx % L).astype(cp.float64)

    print(f"  L={L}  g_ext={g_ext}  T_track={T_track} lu")
    print()

    results = []

    # For each R, do two runs: baseline (g=0) and gravity (g_ext).
    # a_true = a_gravity - a_baseline (isolate external response)
    for R in [3, 5]:
        print(f"\n{'='*60}")
        print(f"Case R={R}")
        print(f"{'='*60}")
        res_base = run_case(L, R, g_ext=0.0, x_coords=x_coords,
                            T_track=T_track, sample_every=sample_every)
        res_grav = run_case(L, R, g_ext=g_ext, x_coords=x_coords,
                            T_track=T_track, sample_every=sample_every)
        results.append({'R': R, 'base': res_base, 'grav': res_grav})

    # --- WEP Analysis ---
    print()
    print("=" * 80)
    print("WEP ANALYSIS")
    print("=" * 80)
    print(f"{'R':>3} {'a_baseline':>14} {'a_gravity':>14} {'a_ext=grav-base':>18} "
          f"{'V0_base':>12} {'V0_grav':>12}")
    print("-" * 80)
    a_ext_list = []
    for r in results:
        a_base = r['base']['a']
        a_grav = r['grav']['a']
        a_ext = a_grav - a_base
        a_ext_list.append(a_ext)
        print(f"{r['R']:>3} {a_base:>14.5e} {a_grav:>14.5e} {a_ext:>18.5e} "
              f"{r['base']['V0']:>12.5e} {r['grav']['V0']:>12.5e}")

    a3, a5 = a_ext_list
    a_mean = 0.5 * (a3 + a5)
    rel_diff = abs(a3 - a5) / max(abs(a_mean), 1e-12)
    print()
    print(f"  a_ext(R=3) = {a3:+.5e}")
    print(f"  a_ext(R=5) = {a5:+.5e}")
    print(f"  |a(3) - a(5)| / mean = {rel_diff*100:.2f}%")
    print()
    print("Theory for Newtonian uniform gravity:")
    print(f"  a_expected_sign = -g_ext = {-g_ext:+.4f}  (force per unit deficit)")
    print()
    if rel_diff < 0.10:
        print("WEP PASS: ring acceleration is INDEPENDENT of R within 10%.")
        print("  -> v8 respects Einstein's Weak Equivalence Principle.")
        print("  -> 'Gravitational mass' = 'inertial mass' for v8 rings.")
    elif rel_diff < 0.25:
        print("WEP MARGINAL: 10-25% R-dependence. Possibly numerical.")
        print("  -> Run larger L or longer T_track to confirm.")
    else:
        print("WEP FAIL: ring size affects free-fall acceleration significantly.")
        print("  -> v8 rings do NOT obey Einstein's equivalence principle.")
        print("  -> Possible cause: ring self-field contributes to inertia")
        print("     differently than to gravitational coupling.")


if __name__ == "__main__":
    main()
