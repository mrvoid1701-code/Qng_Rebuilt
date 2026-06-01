"""GPU-042: β_φ-scan probe to test ⟨L⟩/N ∝ β_φ conjecture.

Runs the orbital-attractor probe at L=28, R=4, varying β_φ. All other
params held at v8 defaults. Downstream analysis checks if ⟨L⟩ = N·β_φ/2
holds, or if a different functional form is required.

Usage:
    py tests/gpu/qng_v8_beta_phi_scan.py --beta_phi 0.03
    py tests/gpu/qng_v8_beta_phi_scan.py --beta_phi 0.12

Note: changing β_φ also changes c_φ = √(β_φ/(3μ_φ)) which affects the
Lorentz-matching DER-QNG-042-prereqs §3.3. For this probe we keep μ_φ
fixed to isolate the β_φ dependence; effectively varies c_φ too.

Output:
    07_validation/audits/qng-v8-beta-phi-scan-{beta}-v1/traces.npz
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

import qng_v8_canonical_gpu as qng
from qng_v8_canonical_gpu import (
    yoshida4_step, hamiltonian_v8, DT,
    SIGMA_G_REF, SIGMA_M_REF, CHI_DECAY_V7,
    G_V_COUPLE, MU_PHI, BETA_G, BETA_M, ALPHA, K_BACK, MU_M,
    ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_raw

EXACT_A_MODE = 'r1'


def lattice_coords(L):
    xs = np.arange(L)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    return xg, yg, zg


def com(state, L, xg, yg, zg):
    sm = cp.asnumpy(state['sm']).reshape(L, L, L)
    def_field = np.maximum(SIGMA_M_REF - sm, 0.0)
    W = def_field.sum()
    if W < 1e-10:
        return None
    cx = (def_field * xg).sum() / W
    cy = (def_field * yg).sum() / W
    cz = (def_field * zg).sum() / W
    return cx, cy, cz, W


def hamiltonian_components(state, nb_idx):
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    T_g = (K_BACK / 2.0) * float(cp.sum(chi * chi))
    T_m = (1.0 / (2.0 * MU_M)) * float(cp.sum(pi_m * pi_m))
    T_phi = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))
    V_c = (G_V_COUPLE / 2.0) * float(
        cp.sum((SIGMA_M_REF - sm) ** 2 * (1.0 - cp.cos(phi))))
    H_total = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                                     exact_a=EXACT_A_MODE))
    return T_g, T_m, T_phi, V_c, H_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beta_phi", type=float, required=True)
    ap.add_argument("--L", type=int, default=28)
    ap.add_argument("--R", type=int, default=4)
    ap.add_argument("--T_run", type=float, default=2000.0)
    args = ap.parse_args()

    # Override β_φ at module level (yoshida4_step reads BETA_PHI from module)
    qng.BETA_PHI = args.beta_phi
    beta_phi = args.beta_phi

    L = args.L; R = args.R
    T_P1 = 300.0; T_P2 = 1000.0
    T_run = args.T_run
    sample_every_lu = 10.0

    audit = ROOT / "07_validation" / "audits" / f"qng-v8-beta-phi-scan-{beta_phi:.3f}-v1"
    audit.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"GPU-042: beta_phi-scan  beta_phi={beta_phi}, L={L}, R={R}")
    print("=" * 80)
    c_phi_new = float(np.sqrt(beta_phi / (3.0 * MU_PHI)))
    print(f"  c_phi_derived = {c_phi_new:.5f}")
    print(f"  audit: {audit}")

    # Skip cache: BETA_PHI override is at module level but cache key
    # was snapshot at import time. Re-form fresh for each beta_phi.
    t0 = time.time()
    state, nb_idx = form_ring_raw(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT)
    print(f"  Ring formation: {time.time()-t0:.1f}s")
    M_init = float(ring_mass_deficit(state['sm']))
    print(f"  Initial M_ring = {M_init:.2f}")

    xg, yg, zg = lattice_coords(L)

    n_steps = int(T_run / DT)
    sample_every = max(1, int(sample_every_lu / DT))

    times, H_arr = [], []
    Tg_arr, Tm_arr, Tp_arr, Vc_arr = [], [], [], []
    M_arr = []

    t0 = time.time()
    for step in range(n_steps + 1):
        if step % sample_every == 0:
            t_lu = step * DT
            c = com(state, L, xg, yg, zg)
            if c is None:
                print(f"  COM lost at t={t_lu:.2f}; aborting")
                break
            Tg, Tm, Tp, Vc, Htot = hamiltonian_components(state, nb_idx)
            times.append(t_lu); H_arr.append(Htot)
            Tg_arr.append(Tg); Tm_arr.append(Tm); Tp_arr.append(Tp); Vc_arr.append(Vc)
            M_arr.append(float(ring_mass_deficit(state['sm'])))
        if step < n_steps:
            state = yoshida4_step(state, DT, nb_idx,
                                    channel_f=True, k_gm=0.0,
                                    exact_a=EXACT_A_MODE)

    print(f"  Run: {time.time()-t0:.1f}s ({len(times)} samples)")

    times = np.array(times); H_arr = np.array(H_arr)
    Tg_arr = np.array(Tg_arr); Tm_arr = np.array(Tm_arr); Tp_arr = np.array(Tp_arr)
    Vc_arr = np.array(Vc_arr); M_arr = np.array(M_arr)

    np.savez(audit / "traces.npz",
             times=times, H=H_arr, T_g=Tg_arr, T_m=Tm_arr, T_phi=Tp_arr,
             V_couple=Vc_arr, M_ring=M_arr, beta_phi=beta_phi)

    warm = times > 500.0
    Tkin = Tg_arr[warm] + Tm_arr[warm] + Tp_arr[warm]
    H_mean = float(H_arr[warm].mean()); T_mean = float(Tkin.mean())
    E_char = 2 * T_mean - H_mean
    N = L ** 3

    print(f"\n  ===== Results beta_phi={beta_phi}, L={L}, R={R} =====")
    print(f"  <H>     = {H_mean:12.2f}")
    print(f"  <T_kin> = {T_mean:12.2f}")
    print(f"  E_char  = {E_char:12.3f}")
    print(f"  E_char / N  = {E_char/N:.6f}  (intensive density)")
    print(f"  beta_phi/2  = {beta_phi/2:.6f}  (prediction if ⟨L⟩ = N·β_φ/2)")
    print(f"  ratio  = {(E_char/N) / (beta_phi/2):.4f}")

    with open(audit / "report.json", "w") as f:
        json.dump({
            'beta_phi': beta_phi, 'L': L, 'R': R,
            'H_mean': H_mean, 'T_mean': T_mean, 'E_char': E_char,
            'E_char_per_N': E_char / N,
            'prediction_N_betaphi_over_2': N * beta_phi / 2.0,
            'ratio_measured_over_pred': E_char / (N * beta_phi / 2.0),
        }, f, indent=2)


if __name__ == "__main__":
    main()
