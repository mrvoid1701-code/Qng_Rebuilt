"""QNG-GPU-029 pilot v2: v8-native small-amplitude IC — does v8 admit a bounded orbit
starting from a clean small perturbation around the v8 vacuum?

Pilot v1 failed G1 + G2 on the cached L=28 R=4 ring: the v7 Channel-F ring is
NOT near any v8 equilibrium, so putting it into pure symplectic dynamics is a
violent quench (M swings +500/-358; H grows 300%; DT=0.025 too coarse).

Pilot v2 starts instead from the TRUE v8 vacuum and adds a small-amplitude,
localized perturbation that co-locates a sigma_m dip and a 2pi phi winding.
This is the minimal topological excitation that could become a breather:
V_couple = (g/2)*Delta^2*(1-cos phi) is active and nonzero around the ring,
phi has unit winding, and amplitudes are small enough to stay in the
linear regime.

Three IC variants (same cheap 5-min pilot each):
  (A) dip only, phi=0 (decoupled limit — sets baseline for pure KG dispersal)
  (B) dip + 2pi winding at R=2 (tight ring, strong local coupling)
  (C) dip + 2pi winding at R=4 (matches cached ring topology, weaker)

Three gates per variant:
  G1 boundedness:     min(M_ring) > -5  AND max(M_ring) < 50  (stays localized)
  G2 H conservation:  |dH/H_0| < 5%  over T=200 lu  (numerics healthy)
  G3 persistence:     M_ring(T=200) > 0.2 * M_ring(T=10)  (not dispersed)

Smaller DT=0.01 (vs pilot v1's 0.025).
Shorter T=200 lu (pilot speed, still resolves several oscillation cycles).
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
    SIGMA_G_REF, SIGMA_M_REF,
    yoshida4_step,
    hamiltonian_v8,
    ring_mass_deficit,
    ring_radius,
    centered_coords,
    build_nb,
)


def build_ic(L, variant, R_ring, dip_amp, core_rho):
    """Build initial state: vacuum + Gaussian sigma_m dip + optional 2pi phi winding.

    variant in {'A_dip_only', 'B_ring_R2', 'C_ring_R4'}.
    dip_amp: size of sigma_m deficit (< SIGMA_M_REF).
    core_rho: Gaussian width of the dip envelope (transverse to ring plane).
    """
    N = L ** 3
    dx_np, dy_np, dz_np = centered_coords(L)
    dx = cp.asarray(dx_np.ravel(), dtype=cp.float32)
    dy = cp.asarray(dy_np.ravel(), dtype=cp.float32)
    dz = cp.asarray(dz_np.ravel(), dtype=cp.float32)
    rho = cp.sqrt(dx * dx + dy * dy)

    # sigma_m dip: Gaussian in (rho-R_ring, z) around the nominal ring curve
    if variant == 'A_dip_only':
        r_eff = cp.sqrt(dx * dx + dy * dy + dz * dz)
        dip_profile = cp.exp(-0.5 * (r_eff / core_rho) ** 2)
    else:
        dist_curve_sq = (rho - R_ring) ** 2 + dz * dz
        dip_profile = cp.exp(-0.5 * dist_curve_sq / (core_rho * core_rho))

    sm = SIGMA_M_REF - dip_amp * dip_profile
    sg = SIGMA_G_REF * cp.ones(N, dtype=cp.float32)
    chi = cp.zeros(N, dtype=cp.float32)

    if variant == 'A_dip_only':
        phi = cp.zeros(N, dtype=cp.float32)
    else:
        # 2pi winding around the ring curve: phi = arctan2(dz, rho - R_ring)
        phi = cp.arctan2(dz, rho - R_ring)

    pi_m = cp.zeros(N, dtype=cp.float32)
    pi_phi = cp.zeros(N, dtype=cp.float32)

    return {'sg': sg, 'sm': sm, 'chi': chi, 'phi': phi,
            'pi_m': pi_m, 'pi_phi': pi_phi}


def autocorr(x, max_lag):
    x = np.asarray(x) - np.mean(x)
    var = np.var(x)
    if var < 1e-14:
        return np.ones(max_lag + 1)
    acf = np.empty(max_lag + 1)
    for k in range(max_lag + 1):
        acf[k] = 1.0 if k == 0 else np.mean(x[:-k] * x[k:]) / var
    return acf


def run_variant(L, variant, nb_idx, R_ring, dip_amp, core_rho, DT, T_PHYS, sample_every, log_every):
    state = build_ic(L, variant, R_ring, dip_amp, core_rho)
    M0 = ring_mass_deficit(state['sm'])
    H0 = hamiltonian_v8(state, nb_idx)
    print(f"\n=== variant={variant}  R_ring={R_ring}  dip_amp={dip_amp}  core_rho={core_rho} ===")
    print(f"  M_0 = {M0:.4f}   H_0 = {H0:.4f}")
    N_STEPS = int(round(T_PHYS / DT))
    STRIDE = int(round(sample_every / DT))

    t_hist = [0.0]
    M_hist = [float(M0)]
    H_hist = [float(H0)]
    sm_min_hist = [float(cp.min(state['sm']))]
    sm_max_hist = [float(cp.max(state['sm']))]
    phi_std_hist = [float(cp.std(state['phi']))]
    R_hist = [ring_radius(state['sm'], L)]

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=0.0, damping_gamma=0.0, chi_decay=0.0,
            v_couple_on=True, channel_f=False,
        )
        if step % STRIDE == 0:
            t_phys = step * DT
            M = float(ring_mass_deficit(state['sm']))
            H = float(hamiltonian_v8(state, nb_idx))
            Rr = ring_radius(state['sm'], L)
            smn = float(cp.min(state['sm']))
            smx = float(cp.max(state['sm']))
            pst = float(cp.std(state['phi']))
            t_hist.append(t_phys)
            M_hist.append(M)
            H_hist.append(H)
            R_hist.append(Rr)
            sm_min_hist.append(smn)
            sm_max_hist.append(smx)
            phi_std_hist.append(pst)
            if step % (log_every * STRIDE) == 0:
                dH = (H - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
                print(f"  t={t_phys:6.1f}  M={M:8.3f}  H={H:8.3f}  dH/H={dH:+.2e}  "
                      f"R={Rr:5.2f}  sm=[{smn:.3f},{smx:.3f}]  phi_std={pst:.3f}")
    wall = time.time() - t0
    print(f"  wall = {wall:.1f}s")

    # Gates
    M_arr = np.asarray(M_hist)
    H_arr = np.asarray(H_hist)
    M_min, M_max = float(np.min(M_arr)), float(np.max(M_arr))
    dH_max = float(np.max(np.abs(H_arr - H0) / abs(H0))) if abs(H0) > 1e-10 else float('inf')
    M_at_10 = float(M_hist[2]) if len(M_hist) > 2 else float(M_hist[-1])
    M_final = float(M_hist[-1])
    persistence_ratio = M_final / M_at_10 if abs(M_at_10) > 1e-6 else 0.0

    G1 = (M_min > -5.0) and (M_max < 50.0)
    G2 = dH_max < 0.05
    G3 = persistence_ratio > 0.2

    print(f"  G1 bounded  [{M_min:.3f},{M_max:.3f}]  {'PASS' if G1 else 'FAIL'}")
    print(f"  G2 H drift  {dH_max:.2e}                {'PASS' if G2 else 'FAIL'}")
    print(f"  G3 persist  ratio={persistence_ratio:.2f}  {'PASS' if G3 else 'FAIL'}")

    # ACF post-transient
    n_trans = max(1, len(M_arr) // 5)
    M_win = M_arr[n_trans:]
    acf = autocorr(M_win, len(M_win) // 2) if len(M_win) > 4 else np.array([1.0])

    return {
        'variant': variant, 'R_ring': R_ring, 'dip_amp': dip_amp, 'core_rho': core_rho,
        'M_0': float(M0), 'H_0': float(H0),
        'M_min': M_min, 'M_max': M_max, 'dH_max': dH_max,
        'persistence_ratio': persistence_ratio,
        'G1': G1, 'G2': G2, 'G3': G3,
        'all_pass': G1 and G2 and G3,
        'runtime_sec': wall,
        't_samples': [float(x) for x in t_hist],
        'M_samples': [float(x) for x in M_hist],
        'H_samples': [float(x) for x in H_hist],
        'R_samples': [float(x) for x in R_hist],
        'sm_min_samples': [float(x) for x in sm_min_hist],
        'sm_max_samples': [float(x) for x in sm_max_hist],
        'phi_std_samples': [float(x) for x in phi_std_hist],
        'acf_post_transient': acf.tolist(),
    }


def main():
    print("=" * 80)
    print("QNG-GPU-029 pilot v2: v8-native small-amplitude IC")
    print("=" * 80)

    L = 28
    N = L ** 3
    nb_idx = build_nb(L)
    print(f"  L={L}  N={N}  z=6 cubic")

    DT = 0.01
    T_PHYS = 200.0
    SAMPLE_EVERY = 2.0
    LOG_EVERY = 5  # every LOG_EVERY samples

    DIP_AMP = 0.10
    CORE_RHO = 1.5

    variants = [
        ('A_dip_only', 0.0),
        ('B_ring_R2',  2.0),
        ('C_ring_R4',  4.0),
    ]

    results = []
    for label, R in variants:
        r = run_variant(L, label, nb_idx, R, DIP_AMP, CORE_RHO,
                        DT, T_PHYS, SAMPLE_EVERY, LOG_EVERY)
        results.append(r)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for r in results:
        flag = "ALL_PASS" if r['all_pass'] else "FAIL"
        print(f"  {r['variant']:15s}  M=[{r['M_min']:7.3f},{r['M_max']:7.3f}]  "
              f"dH={r['dH_max']:.1e}  pers={r['persistence_ratio']:+.2f}  [{flag}]")

    any_pass = any(r['all_pass'] for r in results)
    verdict = 'V8_NATIVE_ORBIT_FOUND' if any_pass else 'NO_V8_NATIVE_ORBIT'
    print(f"\n  VERDICT: {verdict}")
    print("=" * 80)

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-orbit-pilot-v2"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'DT': DT, 'T_PHYS': T_PHYS,
            'dip_amp': DIP_AMP, 'core_rho': CORE_RHO,
            'variants': results, 'verdict': verdict,
        }, f, indent=2)
    print(f"  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
