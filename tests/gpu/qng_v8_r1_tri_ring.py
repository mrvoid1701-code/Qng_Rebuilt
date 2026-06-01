"""QNG-GPU-033: tri-ring binding probe under R1 orbital.

Three vortex-rings arranged in equilateral triangle (XY plane at z=L/2).
Tests user's multi-vortex fusion hypothesis (2026-04-21) at N=3:
baryon analog = three-ring bound state (qqq in QCD terminology).

Background:
  * GPU-032 (bi-ring W+W- d=4) showed LJ-like attractor with mass
    defect -15.4% vs 2x single (strong binding).
  * Skyrme model: B=1 nucleon = single skyrmion; B>1 = bound
    multi-skyrmion. Bilson-Thompson HELON: baryons = braided triples.
  * If user hypothesis is correct, tri-ring should show a DIFFERENT
    mass basin than bi-ring or single — with a stable/converging
    <M_total>_t indicating bound state.

Geometry:
  Three ring centers at equilateral triangle vertices:
    c_i = c_mid + d_tri * (cos(2pi*i/3), sin(2pi*i/3), 0)
  All rings in XZ-symmetry orientation (same as bi-ring script).
  Chirality pattern controlled by --pattern (e.g. "+++", "++-", "+-+").

Predictions:
  * "+++" (all W+): if topological repulsion dominates, <M_total>_t
    >> 3 * 310 = 930 (repulsion like W+W+).
  * "++-" (mixed): expected similar to bi-ring binding plus one free.
  * Convergence: if bound, convergence_rel < 10% within T=5000.
  * If <M_total>_t >> 930 or non-converging → unbound/unstable
    composite.

Runtime (L=24, T_P2=5000): ~60 min Phase 2 + 3 min Phase 1.

Usage:
    py tests/gpu/qng_v8_r1_tri_ring.py
    py tests/gpu/qng_v8_r1_tri_ring.py --d 4 --pattern "++-"
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
    build_nb, make_state, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    centered_coords,
    SIGMA_M_REF, CHI_DECAY_V7, MU_M, MU_PHI,
)

from qng_v8_r1_long_time import run_phase_sampled, analyze_m_series, RING_THRESH

EXACT_A_MODE = 'r1'
GPU_031F_R4_MEAN = 309.45  # single-ring R=4 orbital mean


def init_phi_three_rings(L, R, d, pattern="+++"):
    """Three rings at equilateral-triangle vertices in XY plane, z=L/2.

    Ring axes are all along X (same as bi-ring). Triangle circumradius =
    d/sqrt(3). Each ring's chirality determined by pattern[i] ('+' or '-').

    pattern: length-3 string of '+'/'-' chars, e.g. '+++', '++-', '+-+'.
    """
    assert len(pattern) == 3 and all(c in '+-' for c in pattern)
    # triangle circumradius (vertex-to-center distance) such that
    # vertex-to-vertex distance equals d (equilateral triangle)
    r_tri = d / np.sqrt(3.0)
    cx_mid = L / 2.0
    cy_mid = L / 2.0

    phi_total = None
    for i, sign_char in enumerate(pattern):
        theta = 2.0 * np.pi * i / 3.0
        cx = cx_mid + r_tri * np.cos(theta)
        cy = cy_mid + r_tri * np.sin(theta)
        dx, dy, dz = centered_coords(L, cx=cx, cy=cy)
        rho = np.sqrt(dy * dy + dz * dz)
        phi_i = np.arctan2(dx, rho - R)
        if sign_char == '-':
            phi_i = -phi_i
        phi_total = phi_i if phi_total is None else (phi_total + phi_i)
    return cp.asarray(phi_total.ravel())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, default=24)
    parser.add_argument("--R", type=int, default=4)
    parser.add_argument("--d", type=int, default=4,
                        help="triangle edge length (default 4, bi-ring minimum)")
    parser.add_argument("--pattern", type=str, default="+++",
                        help='chirality pattern, e.g. "+++" or "++-"')
    parser.add_argument("--T_P1", type=float, default=300.0)
    parser.add_argument("--T_P2", type=float, default=5000.0)
    parser.add_argument("--DT", type=float, default=0.025)
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-r1-tri-ring-v1")
    args = parser.parse_args()

    L = args.L
    R = args.R
    d = args.d
    pattern = args.pattern
    T_P1 = args.T_P1
    T_P2 = args.T_P2
    DT = args.DT

    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    m_sample_every = int(1.0 / DT)
    H_sample_every = 100

    outdir = ROOT / "07_validation" / "audits" / args.audit_name
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"QNG-GPU-033: tri-ring binding probe")
    print("=" * 80)
    print(f"\n  L={L}, R={R}, d={d}, pattern='{pattern}'")
    print(f"  T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")
    print(f"  exact_a={EXACT_A_MODE!r}")
    print(f"  GPU-031f single-ring ref = {GPU_031F_R4_MEAN}")
    print(f"  Three-ring unbound prediction = {3*GPU_031F_R4_MEAN}")

    # --- Phase 1 ---
    print(f"\n  [Phase 1] v_couple_on=False, exact_a='r1', 3 rings {pattern}")
    nb_idx = build_nb(L)
    phi_ic = init_phi_three_rings(L, R, d, pattern=pattern)
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
    print(f"PHASE 2 M_total ANALYSIS (pattern={pattern} at d={d})")
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
    unbound_pred = 3 * GPU_031F_R4_MEAN
    delta_total = mean_total - unbound_pred
    delta_second = mean_second_half - unbound_pred
    frac_total = delta_total / unbound_pred
    frac_second = delta_second / unbound_pred

    print(f"  <M_total>_t (all)     = {mean_total:+.3f}")
    print(f"  <M_total>_t (2nd-half)= {mean_second_half:+.3f}")
    print(f"  Unbound prediction    = {unbound_pred:+.3f}  (3 x {GPU_031F_R4_MEAN})")
    print(f"  Delta (all)           = {delta_total:+.3f}  ({frac_total:+.2%})")
    print(f"  Delta (2nd-half)      = {delta_second:+.3f}  ({frac_second:+.2%})")

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
            'pattern': pattern,
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
