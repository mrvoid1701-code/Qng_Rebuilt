"""GPU-034: L-scan on R=4 orbital attractor to test ⟨L⟩=660 invariance.

At fixed R=4, runs the orbital-attractor probe at L∈{L} and writes
traces.npz with full kinetic components. Downstream analysis computes
E_char = 2⟨T_kin⟩ − ⟨H⟩ and checks L-scaling (intensive vs extensive).

Usage:
    py tests/gpu/qng_v8_L_scan_probe.py --L 20
    py tests/gpu/qng_v8_L_scan_probe.py --L 24

Output:
    07_validation/audits/qng-v8-L-scan-R4-L{L}-v1/traces.npz
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
    yoshida4_step, hamiltonian_v8, DT,
    SIGMA_G_REF, SIGMA_M_REF, CHI_DECAY_V7,
    G_V_COUPLE, MU_PHI, BETA_PHI, BETA_G, BETA_M, ALPHA, K_BACK, MU_M,
    ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

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


def r_eff(state, L, xg, yg, zg, com_xyz):
    cx, cy, cz = com_xyz
    sm = cp.asnumpy(state['sm']).reshape(L, L, L)
    def_field = np.maximum(SIGMA_M_REF - sm, 0.0)
    W = def_field.sum()
    if W < 1e-10:
        return 0.0
    r2 = (xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2
    return float(np.sqrt((def_field * r2).sum() / W))


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
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--R", type=int, default=4)
    ap.add_argument("--T_run", type=float, default=2000.0)
    args = ap.parse_args()

    L = args.L
    R = args.R
    T_P1 = 300.0
    T_P2 = 1000.0
    T_run = args.T_run
    sample_every_lu = 10.0

    audit = ROOT / "07_validation" / "audits" / f"qng-v8-L-scan-R{R}-L{L}-v1"
    audit.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"GPU-034: L-scan probe  L={L}, R={R}")
    print("=" * 80)
    print(f"  T_P1={T_P1}, T_P2={T_P2}, T_run={T_run}, DT={DT}")
    print(f"  audit: {audit}")

    t0 = time.time()
    state, nb_idx = form_ring_cached(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT)
    print(f"  Ring formation: {time.time()-t0:.1f}s")
    M_init = float(ring_mass_deficit(state['sm']))
    print(f"  Initial M_ring = {M_init:.2f}")

    xg, yg, zg = lattice_coords(L)

    n_steps = int(T_run / DT)
    sample_every = max(1, int(sample_every_lu / DT))

    times, H_arr = [], []
    Tg_arr, Tm_arr, Tp_arr, Vc_arr = [], [], [], []
    M_arr, r_eff_arr, com_z_arr = [], [], []

    t0 = time.time()
    for step in range(n_steps + 1):
        if step % sample_every == 0:
            t_lu = step * DT
            c = com(state, L, xg, yg, zg)
            if c is None:
                print(f"  COM lost at t={t_lu:.2f}; aborting")
                break
            Tg, Tm, Tp, Vc, Htot = hamiltonian_components(state, nb_idx)
            times.append(t_lu)
            H_arr.append(Htot)
            Tg_arr.append(Tg); Tm_arr.append(Tm); Tp_arr.append(Tp); Vc_arr.append(Vc)
            M_arr.append(float(ring_mass_deficit(state['sm'])))
            r_eff_arr.append(r_eff(state, L, xg, yg, zg, c[:3]))
            com_z_arr.append(c[2])
        if step < n_steps:
            state = yoshida4_step(state, DT, nb_idx,
                                    channel_f=True, k_gm=0.0,
                                    exact_a=EXACT_A_MODE)

    print(f"  Run: {time.time()-t0:.1f}s ({len(times)} samples)")

    times = np.array(times)
    H_arr = np.array(H_arr)
    Tg_arr = np.array(Tg_arr); Tm_arr = np.array(Tm_arr); Tp_arr = np.array(Tp_arr)
    Vc_arr = np.array(Vc_arr)
    M_arr = np.array(M_arr)
    r_eff_arr = np.array(r_eff_arr)
    com_z_arr = np.array(com_z_arr)

    np.savez(audit / "traces.npz",
             times=times, H=H_arr,
             T_g=Tg_arr, T_m=Tm_arr, T_phi=Tp_arr, V_couple=Vc_arr,
             M_ring=M_arr, r_eff=r_eff_arr, com_z=com_z_arr)

    # Quick E_char computation (warm samples only)
    warm = times > 500.0
    Tkin = Tg_arr[warm] + Tm_arr[warm] + Tp_arr[warm]
    H_mean = float(H_arr[warm].mean())
    T_mean = float(Tkin.mean())
    E_char = 2 * T_mean - H_mean
    M_mean = float(M_arr[warm].mean())
    N = L ** 3

    print()
    print(f"  ===== Results L={L} R={R} =====")
    print(f"  N_warm samples = {int(warm.sum())}")
    print(f"  <H>      = {H_mean:12.2f}")
    print(f"  <T_kin>  = {T_mean:12.2f}")
    print(f"  E_char   = 2<T> - <H>  = {E_char:12.2f}")
    print(f"  <M_ring> = {M_mean:12.2f}")
    print(f"  E_char/N = {E_char/N:.6f} (intensive per node)")
    print(f"  E_char/L^3 = {E_char/L**3:.6f}")
    print(f"  E_char/L^2 = {E_char/L**2:.6f}")
    print(f"  E_char/L   = {E_char/L:.6f}")
    print(f"  H/N      = {H_mean/N:.6f}")

    with open(audit / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'N_warm': int(warm.sum()),
            'H_mean': H_mean, 'T_mean': T_mean, 'E_char': E_char,
            'M_ring_mean': M_mean,
            'E_char_per_N': E_char / N,
            'reference_L28_E_char': 660.00,
        }, f, indent=2)


if __name__ == "__main__":
    main()
