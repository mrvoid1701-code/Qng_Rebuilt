"""QNG-GPU-030e: sanity test for Audit Finding #12.

Finding #12: `drive_chi_v7style` is NOT the canonical Hamilton equation
  dchi/dt = -dH/dsigma_g; it is a v7-legacy gradient-flow mix with
  DELTA_CHI=0.20 as an "effective alpha" (40x ALPHA=0.005). In the v8
  context we want to know: with k_gm turned on and chi initialized
  non-zero, how much does H drift under Yoshida4?

Setup:
  - Cached L=28 R=4 ring (Phase 1 + Phase 2).
  - Perturb chi to chi_0 = amp * sin(3x/L) * cos(5y/L) (non-uniform,
    small-amplitude, zero mean to avoid sigma_g global pumping).
  - k_gm = 0.1, CHI_DECAY = 0 (to isolate non-canonical drive — any H
    drift is from CHI_REL + DELTA_CHI cross-terms not matching
    -dE/dsigma_g).
  - T = 20 lu, DT = 0.01, channel_f = True, v_couple on.
  - Monitor: patched hamiltonian_v8 (now includes E_phi, E_chi, E_coupling).

Predict:
  - If the drive were canonical, |dH/H| should match the Channel-A residual
    (~6%, from the F_A approximation; c.f. GPU-030d).
  - Excess over 6% is attributable to Finding #12.

Output:
  - 07_validation/audits/qng-v8-chi-canonical-sanity-v1/report.json
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    hamiltonian_v8, yoshida4_step, K_BACK,
)
from qng_v8_ring_cache import form_ring_cached


def perturb_chi(L, amp=0.05):
    xs = cp.arange(L).astype(cp.float64)
    X, Y, Z = cp.meshgrid(xs, xs, xs, indexing='ij')
    # non-uniform, zero-mean modulation
    field = amp * cp.sin(3.0 * X / L * 2 * math.pi) * cp.cos(5.0 * Y / L * 2 * math.pi)
    return field.reshape(-1).astype(cp.float64)


def main():
    print("=" * 80)
    print("QNG-GPU-030e: (sigma_g, chi) non-canonical drive sanity test")
    print("=" * 80)

    L = 28
    R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=False)
    N = L ** 3

    K_GM = 0.1
    CHI_DECAY = 0.0
    DT = 0.01
    T_PHYS = 20.0
    N_STEPS = int(round(T_PHYS / DT))
    LOG_LU = 2.0
    STRIDE = int(round(LOG_LU / DT))
    CHI_AMP = 0.05

    chi0 = perturb_chi(L, amp=CHI_AMP)
    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    chi0.copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }

    print(f"  L={L}, R={R}, K_GM={K_GM}, CHI_DECAY={CHI_DECAY}")
    print(f"  chi_0: mean={float(chi0.mean()):+.4e}, rms={float(cp.sqrt((chi0**2).mean())):.4e}")
    print(f"  T_phys={T_PHYS}, DT={DT}, N_steps={N_STEPS}")

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM)
    print(f"  H_0 = {H0:+.4f}")
    print()
    print(f"  {'t':>5s}  {'H':>12s}  {'dH/H0':>12s}  {'max|chi|':>10s}  {'<sg>':>10s}")

    log = [{'t': 0.0, 'H': H0, 'dH_over_H0': 0.0,
            'max_chi': float(cp.max(cp.abs(state['chi']))),
            'mean_sg': float(cp.mean(state['sg']))}]

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=K_GM, damping_gamma=0.0, chi_decay=CHI_DECAY,
            v_couple_on=True, channel_f=True,
        )
        if step % STRIDE == 0:
            t_phys = step * DT
            H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM)
            dH = (H - H0) / abs(H0)
            mc = float(cp.max(cp.abs(state['chi'])))
            sgm = float(cp.mean(state['sg']))
            log.append({'t': t_phys, 'H': H, 'dH_over_H0': dH,
                        'max_chi': mc, 'mean_sg': sgm})
            print(f"  {t_phys:5.1f}  {H:+12.3f}  {dH:+12.2e}  {mc:10.4f}  {sgm:10.4f}",
                  flush=True)

    wall = time.time() - t0
    print(f"\n  wall = {wall:.1f}s")

    # -- Verdict --
    dH_final = log[-1]['dH_over_H0']
    abs_dH = abs(dH_final)

    # Reference: GPU-030d residual (k_gm=0, chi=0) was ~6%.
    GPU030D_BASELINE = 0.061

    excess = abs_dH - GPU030D_BASELINE

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  |dH/H0| at T={T_PHYS}: {abs_dH:.3e}")
    print(f"  GPU-030d baseline (k_gm=0, chi=0, Channel A residual): {GPU030D_BASELINE:.3e}")
    print(f"  Excess attributable to (sigma_g, chi) non-canonical + k_gm cross-coupling:")
    print(f"    excess = {excess:+.3e}")

    if abs_dH < 2.0 * GPU030D_BASELINE:
        diag = ("Finding #12 impact is SMALL (<2x baseline) in this mode. "
                "Non-canonical chi drive does not dominate energy budget "
                "when k_gm is modest and chi is small-amplitude.")
    elif abs_dH < 5.0 * GPU030D_BASELINE:
        diag = ("Finding #12 impact is MODERATE (2-5x baseline). "
                "Worth formalizing the chi evolution equation "
                "(decision document R5) but does not invalidate Einstein "
                "correspondence probes at current scan amplitudes.")
    else:
        diag = ("Finding #12 impact is LARGE (>5x baseline). "
                "The (sigma_g, chi) sector is the dominant non-canonical leak. "
                "Einstein correspondence probes should be re-run with a "
                "chi initial perturbation audit.")
    print(f"\n  Diagnosis: {diag}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-chi-canonical-sanity-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'K_GM': K_GM, 'CHI_DECAY': CHI_DECAY,
            'CHI_AMP': CHI_AMP, 'DT': DT, 'T_PHYS': T_PHYS,
            'H0': H0, 'dH_final_over_H0': dH_final,
            'gpu030d_baseline': GPU030D_BASELINE,
            'excess_over_baseline': excess,
            'diagnosis': diag,
            'log': log,
        }, f, indent=2)
    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
