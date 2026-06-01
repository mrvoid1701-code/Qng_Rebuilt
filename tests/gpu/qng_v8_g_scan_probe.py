"""QNG-GPU-020 g-scan probe.

After qng_v8_stability_probe showed sigma_g systematically collapses to 0
at t_phys ~= 1.5 for single ring (L=16, R=4) regardless of dt/damping, the
diagnosis is that V_couple = g*sigma_g*(1-cos phi) is structurally unbalanced
against Channel A (ALPHA=0.005). The gradient -dV/dsigma_g = -g*(1-cos phi)
is always <= 0 on any phi != 0 configuration (a ring).

This probe scans g in the Stage A gate window [0.190, 0.276] (bound by
m_phi = sqrt(g*sigma_g_ref/mu_phi) in [0.323, 0.395]) at L=32 to see if
any g keeps sigma_g above SIGMA_G_MIN_ABORT = 0.025 on a single ring.

If no g in the allowed window survives -> DER-QNG-042 structurally incompatible
with topological ring configurations. Requires re-derivation.
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
    SIGMA_G_REF, MU_PHI,
    build_nb, init_phi_single_ring, make_state,
    yoshida4_step,
    SIGMA_G_MIN_ABORT,
)


def probe_ring(g_value, L=32, R=4, dt=0.025, t_max=100.0):
    """Run single-ring v8 with V_couple coupling g_value, track sg_min trajectory."""
    v8.G_V_COUPLE = g_value
    nsteps = int(t_max / dt)

    nb = build_nb(L)
    phi0 = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi0)

    sample_every = max(1, nsteps // 100)
    sg_min_trace = [float(cp.min(state['sg']))]
    t_trace = [0.0]
    first_breach_step = None

    t0 = time.time()
    for s in range(1, nsteps + 1):
        state = yoshida4_step(state, dt, nb, k_gm=0.0,
                              damping_gamma=0.0, v_couple_on=True)
        if cp.any(cp.isnan(state['sg'])) or cp.any(cp.isnan(state['sm'])):
            return {'g': g_value, 'nan_step': s, 'sg_min_trace': sg_min_trace,
                    't_trace': t_trace, 'first_breach_step': first_breach_step,
                    'wall': time.time() - t0}
        if s % sample_every == 0 or s == nsteps:
            sg_min = float(cp.min(state['sg']))
            sg_min_trace.append(sg_min)
            t_trace.append(s * dt)
            if sg_min < SIGMA_G_MIN_ABORT and first_breach_step is None:
                first_breach_step = s

    return {
        'g': g_value,
        'nan_step': None,
        'sg_min_trace': sg_min_trace,
        't_trace': t_trace,
        'first_breach_step': first_breach_step,
        'first_breach_time': first_breach_step * dt if first_breach_step else None,
        'sg_min_final': sg_min_trace[-1],
        'sg_min_overall': min(sg_min_trace),
        'wall': time.time() - t0,
    }


def m_phi_of(g):
    return np.sqrt(g * SIGMA_G_REF / MU_PHI)


def main():
    print("=" * 76)
    print("QNG-GPU-020 g-scan probe (single ring, L=32, R=4, dt=0.025, T=100)")
    print("=" * 76)
    print(f"  Stage A gate: m_phi in [0.323, 0.395]")
    print(f"  -> g window: [0.190, 0.276]")
    print(f"  SIGMA_G_MIN_ABORT = {SIGMA_G_MIN_ABORT}")
    print()

    g_values = [0.190, 0.220, 0.276]
    results = []

    for g in g_values:
        mphi = m_phi_of(g)
        print(f"--- g={g:.3f}  (m_phi={mphi:.3f}) ---")
        r = probe_ring(g)
        results.append(r)
        if r['nan_step'] is not None:
            print(f"  NaN at step {r['nan_step']}  (t={r['nan_step']*0.025:.2f})")
        elif r['first_breach_step'] is not None:
            t_br = r['first_breach_step'] * 0.025
            print(f"  sg_min breach at step {r['first_breach_step']} (t={t_br:.2f})")
            print(f"  sg_min final = {r['sg_min_final']:.4f}")
            print(f"  sg_min overall = {r['sg_min_overall']:.4f}")
        else:
            print(f"  SURVIVED FULL T=100 without breach")
            print(f"  sg_min overall = {r['sg_min_overall']:.4f}")
        print(f"  wall: {r['wall']:.1f}s")
        print()

    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    any_survive = any(r['nan_step'] is None and r['first_breach_step'] is None
                      for r in results)
    if any_survive:
        stable = [r for r in results if r['nan_step'] is None and r['first_breach_step'] is None]
        best = max(stable, key=lambda r: r['sg_min_overall'])
        print(f"STABLE config found: g={best['g']}  sg_min_overall={best['sg_min_overall']:.4f}")
        print(f"-> Retune GPU-020 prereg to use this g, re-derive m_phi and re-run.")
    else:
        no_nan = [r for r in results if r['nan_step'] is None]
        if no_nan:
            latest = max(no_nan, key=lambda r: r['first_breach_step'])
            t_br = latest['first_breach_step'] * 0.025
            print(f"ALL breached sigma_g_min. Best delay: g={latest['g']} at t={t_br:.2f}")
        else:
            earliest_nan = min(results, key=lambda r: r['nan_step'])
            print(f"ALL produced NaN. Earliest: g={earliest_nan['g']} at step={earliest_nan['nan_step']}")
        print("-> DER-QNG-042 V_couple form is structurally incompatible with rings.")
        print("-> Requires re-derivation: alternative V_couple form OR lift Stage A gate.")


if __name__ == "__main__":
    main()
