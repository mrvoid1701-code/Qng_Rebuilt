"""QNG-GPU-029 pilot: is the cached ring a bounded orbit under v8 symplectic?

Pilot for Scenario A: run cached L=28 R=4 ring under v8 Yoshida4 for T=500 lu
(no damping, no gradient flow). Sample M_ring, H_v8, sigma_m extrema, phi
extrema, ring_radius. Check three necessary conditions before committing to
5000-lu full analysis.

Gates:
  G1 boundedness:     min(M_ring) > 10  AND  max(M_ring) < 1000
  G2 H conservation:  |dH/H_0| < 1%  over T=500 lu
  G3 autocorrelation: M_ring(t) ACF decays to <0.3 within T/2
                       (quasi-periodic / finite-memory orbit, not ergodic)

All pass    -> launch full 5000 lu probe
G1 fail     -> ring dissolves or explodes; Scenario A needs different IC
G2 fail     -> shrink DT, retest
G3 fail     -> swap Poincare/Floquet for Lyapunov spectrum
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
    SIGMA_M_REF,
    yoshida4_step,
    hamiltonian_v8,
    ring_mass_deficit,
    ring_radius,
)
from qng_v8_ring_cache import form_ring_cached


def autocorr(x, max_lag):
    """Normalised autocorrelation of a 1D array up to max_lag."""
    x = np.asarray(x) - np.mean(x)
    var = np.var(x)
    if var < 1e-14:
        return np.ones(max_lag + 1)
    acf = np.empty(max_lag + 1)
    for k in range(max_lag + 1):
        if k == 0:
            acf[k] = 1.0
        else:
            acf[k] = np.mean(x[:-k] * x[k:]) / var
    return acf


def main():
    print("=" * 80)
    print("QNG-GPU-029 pilot: bounded-orbit check on cached L=28 R=4 ring")
    print("=" * 80)

    L = 28
    R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=True)
    M0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"  cached M_ring = {M0:.4f}")

    # Initial state with zero momenta (pure position-space IC, matches CPU-074 convention)
    N = L ** 3
    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    ring_state['chi'].copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float32),
        'pi_phi': cp.zeros(N, dtype=cp.float32),
    }

    DT = 0.025
    T_PHYS = 500.0
    N_STEPS = int(round(T_PHYS / DT))     # 20000 substeps
    SAMPLE_EVERY = 5.0                    # lu
    SAMPLE_STRIDE = int(round(SAMPLE_EVERY / DT))  # 200 substeps

    # Full v8, Channel F OFF (cleanest configuration, matches GPU-024c E + GPU-028 d control)
    CHANNEL_F = False
    V_COUPLE_ON = True
    K_GM = 0.0
    CHI_DECAY = 0.0   # turn off to match GPU-024c E (pure symplectic)

    print(f"  config: v8 Yoshida4, DT={DT}, T={T_PHYS} lu ({N_STEPS} substeps)")
    print(f"  V_couple={V_COUPLE_ON}, Channel F={CHANNEL_F}, "
          f"k_gm={K_GM}, chi_decay={CHI_DECAY}")

    H0 = hamiltonian_v8(state, nb_idx)
    M_hist = [M0]
    H_hist = [H0]
    R_hist = [ring_radius(state['sm'], L)]
    sm_min_hist = [float(cp.min(state['sm']))]
    phi_std_hist = [float(cp.std(state['phi']))]
    t_hist = [0.0]

    print(f"  H_0 = {H0:.4f}")
    print(f"  sample stride = every {SAMPLE_EVERY} lu ({SAMPLE_STRIDE} substeps)")
    print()

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=K_GM, damping_gamma=0.0, chi_decay=CHI_DECAY,
            v_couple_on=V_COUPLE_ON, channel_f=CHANNEL_F,
        )
        if step % SAMPLE_STRIDE == 0:
            t_phys = step * DT
            M = ring_mass_deficit(state['sm'])
            H = hamiltonian_v8(state, nb_idx)
            Rr = ring_radius(state['sm'], L)
            smn = float(cp.min(state['sm']))
            pst = float(cp.std(state['phi']))
            t_hist.append(t_phys)
            M_hist.append(M)
            H_hist.append(H)
            R_hist.append(Rr)
            sm_min_hist.append(smn)
            phi_std_hist.append(pst)
            if step % (10 * SAMPLE_STRIDE) == 0:
                dH = (H - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
                print(f"  t={t_phys:6.1f}  M={M:8.3f}  H={H:8.3f}  "
                      f"dH/H={dH:+.2e}  R={Rr:.2f}  sm_min={smn:.3f}  "
                      f"phi_std={pst:.3f}")

    wall = time.time() - t0
    print(f"\n  wall = {wall:.1f}s")

    # -------- Gate evaluation --------
    M_arr = np.asarray(M_hist)
    H_arr = np.asarray(H_hist)
    t_arr = np.asarray(t_hist)

    M_min = float(np.min(M_arr))
    M_max = float(np.max(M_arr))
    dH_max = float(np.max(np.abs(H_arr - H0) / abs(H0))) if abs(H0) > 1e-10 else float('inf')

    G1_lo = 10.0
    G1_hi = 1000.0
    G1_pass = (M_min > G1_lo) and (M_max < G1_hi)

    G2_thresh = 0.01
    G2_pass = dH_max < G2_thresh

    # ACF on post-transient window (skip first 20% = 100 lu transient)
    n_transient = len(M_arr) // 5
    M_window = M_arr[n_transient:]
    max_lag = len(M_window) // 2
    acf = autocorr(M_window, max_lag)
    # G3: ACF drops below 0.3 at some lag within window
    below_thresh = np.where(np.abs(acf) < 0.3)[0]
    G3_decay_lag = int(below_thresh[0]) if below_thresh.size > 0 else -1
    G3_pass = (G3_decay_lag > 0) and (G3_decay_lag < max_lag)

    # -------- Decision --------
    print("\n" + "=" * 80)
    print("GATES")
    print("=" * 80)
    print(f"  G1 boundedness:        M in [{M_min:.3f}, {M_max:.3f}] "
          f"(need [>{G1_lo}, <{G1_hi}])  -> {'PASS' if G1_pass else 'FAIL'}")
    print(f"  G2 H conservation:     max |dH/H| = {dH_max:.3e} "
          f"(need <{G2_thresh})            -> {'PASS' if G2_pass else 'FAIL'}")
    print(f"  G3 ACF decay:          lag to |ACF|<0.3 = {G3_decay_lag} "
          f"samples (need finite)          -> {'PASS' if G3_pass else 'FAIL'}")

    all_pass = G1_pass and G2_pass and G3_pass
    verdict = 'LAUNCH_FULL_5000LU' if all_pass else 'ABORT_AND_REVIEW'

    print(f"\n  VERDICT: {verdict}")
    print("=" * 80)

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-orbit-pilot-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'DT': DT, 'T_PHYS': T_PHYS,
            'channel_f': CHANNEL_F, 'v_couple_on': V_COUPLE_ON,
            'k_gm': K_GM, 'chi_decay': CHI_DECAY,
            'M_0': M0, 'H_0': H0,
            'M_min': M_min, 'M_max': M_max, 'dH_max': dH_max,
            'G3_decay_lag_samples': G3_decay_lag,
            'G1_pass': G1_pass, 'G2_pass': G2_pass, 'G3_pass': G3_pass,
            'verdict': verdict,
            'runtime_sec': wall,
            't_samples':    [float(x) for x in t_hist],
            'M_samples':    [float(x) for x in M_hist],
            'H_samples':    [float(x) for x in H_hist],
            'R_samples':    [float(x) for x in R_hist],
            'sm_min_samples': [float(x) for x in sm_min_hist],
            'phi_std_samples': [float(x) for x in phi_std_hist],
            'acf_M_post_transient': acf.tolist(),
        }, f, indent=2)
    print(f"  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
