"""GPU-039: R-universality probe for action invariant.

Parametric version of GPU-038 (qng_v8_particle_probe.py). Runs the orbital
attractor probe at user-specified ring radius R and writes traces to a
dedicated audit directory per R. Downstream action analysis (program beta
verification) reads traces.npz from this directory.

Usage:
    py tests/gpu/qng_v8_particle_probe_R.py --R 3
    py tests/gpu/qng_v8_particle_probe_R.py --R 5

Outputs:
    07_validation/audits/qng-v8-particle-probe-R{R}-v1/report.json
    07_validation/audits/qng-v8-particle-probe-R{R}-v1/traces.npz
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
    cx = cy = cz = (L - 1) / 2.0
    return xg, yg, zg, cx, cy, cz


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


def ang_mom_z(state, L, xg, yg, zg, com_xyz):
    cx, cy, cz = com_xyz
    phi = cp.asnumpy(state['phi']).reshape(L, L, L)
    pi_phi = cp.asnumpy(state['pi_phi']).reshape(L, L, L)
    dphi_dx, dphi_dy, dphi_dz = np.gradient(phi)
    dphi_dx = np.mod(dphi_dx + np.pi, 2 * np.pi) - np.pi
    dphi_dy = np.mod(dphi_dy + np.pi, 2 * np.pi) - np.pi
    Lz_phi = float(np.sum(((xg - cx) * dphi_dy - (yg - cy) * dphi_dx)
                           * pi_phi))
    return Lz_phi


def phi_winding_z(state, L, R_ring, com_xyz):
    cx, cy, cz = com_xyz
    phi = cp.asnumpy(state['phi']).reshape(L, L, L)
    iz = int(round(cz))
    n_samples = 32
    angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
    phis = []
    for a in angles:
        x = cx + R_ring * np.cos(a)
        y = cy + R_ring * np.sin(a)
        ix = int(round(x)) % L
        iy = int(round(y)) % L
        phis.append(phi[ix, iy, iz])
    dphis = np.diff(phis + [phis[0]])
    dphis = np.mod(dphis + np.pi, 2 * np.pi) - np.pi
    return float(np.sum(dphis) / (2 * np.pi))


def hamiltonian_components(state, nb_idx):
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    T_g   = (K_BACK / 2.0)   * float(cp.sum(chi * chi))
    T_m   = (1.0 / (2.0 * MU_M))   * float(cp.sum(pi_m * pi_m))
    T_phi = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))
    V_c = (G_V_COUPLE / 2.0) * float(
        cp.sum((SIGMA_M_REF - sm) ** 2 * (1.0 - cp.cos(phi))))
    H_total = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                                     exact_a=EXACT_A_MODE))
    return T_g, T_m, T_phi, V_c, H_total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, required=True,
                    help="Ring radius (3, 4, 5, ...)")
    ap.add_argument("--L", type=int, default=28)
    ap.add_argument("--T_run", type=float, default=2000.0)
    args = ap.parse_args()

    L = args.L
    R = args.R
    T_P1 = 300.0
    T_P2 = 1000.0
    T_run = args.T_run
    sample_every_lu = 10.0

    audit = ROOT / "07_validation" / "audits" / f"qng-v8-particle-probe-R{R}-v1"
    audit.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"GPU-039: R-universality probe  R={R}")
    print("=" * 80)
    print(f"  L={L}, R={R}, P1={T_P1}, P2={T_P2}")
    print(f"  T_run={T_run} lu, DT={DT}, sample every {sample_every_lu} lu")
    print(f"  audit: {audit}")

    state, nb_idx = form_ring_cached(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT)
    print(f"  Initial M_ring = {float(ring_mass_deficit(state['sm'])):.2f}")

    xg, yg, zg, cx_geom, cy_geom, cz_geom = lattice_coords(L)

    com0 = com(state, L, xg, yg, zg)
    print(f"  Initial COM = ({com0[0]:.2f}, {com0[1]:.2f}, {com0[2]:.2f}), "
          f"W_def_initial = {com0[3]:.2f}")

    n_steps = int(T_run / DT)
    sample_every = max(1, int(sample_every_lu / DT))

    times, M_ring_arr, H_arr = [], [], []
    T_g_arr, T_m_arr, T_phi_arr, V_c_arr = [], [], [], []
    com_x_arr, com_y_arr, com_z_arr = [], [], []
    r_eff_arr, Lz_phi_arr, winding_arr = [], [], []

    def record(t):
        c = com(state, L, xg, yg, zg)
        if c is None:
            return
        cx, cy, cz, W = c
        times.append(t)
        M_ring_arr.append(float(ring_mass_deficit(state['sm'])))
        Tg, Tm, Tp, Vc, H = hamiltonian_components(state, nb_idx)
        H_arr.append(H)
        T_g_arr.append(Tg); T_m_arr.append(Tm); T_phi_arr.append(Tp)
        V_c_arr.append(Vc)
        com_x_arr.append(cx); com_y_arr.append(cy); com_z_arr.append(cz)
        r_eff_arr.append(r_eff(state, L, xg, yg, zg, (cx, cy, cz)))
        Lz_phi_arr.append(ang_mom_z(state, L, xg, yg, zg, (cx, cy, cz)))
        winding_arr.append(phi_winding_z(state, L, R, (cx, cy, cz)))

    record(0.0)

    t_start = time.time()
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        if s % sample_every == 0:
            record(s * DT)
        if s % (n_steps // 10) == 0:
            frac = s / n_steps
            elapsed = time.time() - t_start
            eta = elapsed * (1 - frac) / max(frac, 1e-3)
            print(f"    {frac*100:.0f}% done  elapsed={elapsed:.0f}s  "
                  f"eta={eta:.0f}s  M_ring={M_ring_arr[-1]:.2f}  "
                  f"H={H_arr[-1]:.3f}")

    wall = time.time() - t_start

    t_arr = np.array(times)
    warm = t_arr > 500.0
    if warm.sum() < 10:
        warm = np.ones(len(t_arr), dtype=bool)

    def stats(arr, mask):
        a = np.asarray(arr)[mask]
        return {'mean': float(a.mean()), 'std': float(a.std()),
                'min': float(a.min()), 'max': float(a.max())}

    summary = {
        'M_ring': stats(M_ring_arr, warm), 'H': stats(H_arr, warm),
        'T_g': stats(T_g_arr, warm), 'T_m': stats(T_m_arr, warm),
        'T_phi': stats(T_phi_arr, warm), 'V_couple': stats(V_c_arr, warm),
        'r_eff': stats(r_eff_arr, warm), 'Lz_phi': stats(Lz_phi_arr, warm),
        'phi_winding': stats(winding_arr, warm),
        'com_x': stats(com_x_arr, warm), 'com_y': stats(com_y_arr, warm),
        'com_z': stats(com_z_arr, warm),
    }

    print("\n" + "=" * 80)
    print(f"PARTICLE PROPERTIES R={R}  (t > 500 lu, wall={wall:.0f}s)")
    print("=" * 80)
    for k, s in summary.items():
        print(f"  {k:12s}  mean={s['mean']:+.4e}  std={s['std']:.3e}  "
              f"range=[{s['min']:.4e},{s['max']:.4e}]")

    with open(audit / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'T_run': T_run,
            'sample_every_lu': sample_every_lu,
            'n_samples_total': len(times),
            'n_samples_warm': int(warm.sum()),
            'g': G_V_COUPLE, 'mu_phi': MU_PHI, 'mu_m': MU_M,
            'beta_phi': BETA_PHI, 'beta_g': BETA_G, 'beta_m': BETA_M,
            'sigma_m_ref': SIGMA_M_REF, 'sigma_g_ref': SIGMA_G_REF,
            'summary': summary, 'wall_s': wall,
        }, f, indent=2)
    np.savez(audit / "traces.npz",
             times=t_arr,
             M_ring=np.array(M_ring_arr), H=np.array(H_arr),
             T_g=np.array(T_g_arr), T_m=np.array(T_m_arr),
             T_phi=np.array(T_phi_arr), V_couple=np.array(V_c_arr),
             com_x=np.array(com_x_arr), com_y=np.array(com_y_arr),
             com_z=np.array(com_z_arr),
             r_eff=np.array(r_eff_arr),
             Lz_phi=np.array(Lz_phi_arr),
             phi_winding=np.array(winding_arr))
    print(f"\n  Report: {audit / 'report.json'}")


if __name__ == "__main__":
    main()
