"""Quick CPU analysis of GPU-032a/b/c bi-ring final states + GPU-031f single ring.

Computes:
  (A) Energy decomposition per term at final time for d in {3, 4, 6} + single
  (B) Ring width (lambda_ring) from sigma_m profile radial fit
  (D) LJ profile plot: Delta_mass(d), Delta_H(d)

All CPU-only (numpy). Reads final_state.npz files.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# v8 parameters (mirror qng_v8_canonical_gpu.py)
SIGMA_G_REF = 0.5
SIGMA_M_REF = 0.5
ALPHA       = 0.005
BETA_G      = 0.35
BETA_M      = 0.35
BETA_PHI    = 0.06
DELTA_CHI   = 0.20
CHI_REL     = 0.35
GAMMA_PHI   = 0.10
K_BACK      = 0.10
G_V_COUPLE  = 0.22
MU_M        = BETA_M / (K_BACK * BETA_G)        # 10.0
MU_PHI      = 2.0 * BETA_PHI * SIGMA_M_REF**2 / (K_BACK * BETA_G)  # 0.857


def build_nb_cpu(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg,
        ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg,
        xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + ((zg - 1) % L),
        xg * L * L + yg * L + ((zg + 1) % L),
    ], axis=1).astype(np.int32)
    return nb


def disorder_cpu(phi, nb):
    pnb = phi[nb]
    dphi = phi[:, None] - pnb
    dphi = (dphi + np.pi) % (2*np.pi) - np.pi
    return np.mean(np.abs(dphi), axis=1)


def nb_mean_cpu(f, nb):
    return f[nb].mean(axis=1)


def decompose_h_r1(state, L, k_gm=0.0, channel_f=True):
    """R1 pure-XY E_phi form (DER-QNG-051 Option R1). k_gm=0 in GPU-032 runs.

    NPZ files from qng_v8_r1_* only save (sm, phi, pi_m, pi_phi). Under R1 with
    k_gm=0, sg and chi are inert -> default to reference values.
    """
    sm   = state['sm'].ravel()
    phi  = state['phi'].ravel()
    pi_m = state['pi_m'].ravel()
    pi_phi = state['pi_phi'].ravel()
    N = sm.shape[0]
    # Defaults for inert sectors
    sg  = state['sg'].ravel() if 'sg'  in state else np.full(N, SIGMA_G_REF, dtype=np.float64)
    chi = state['chi'].ravel() if 'chi' in state else np.zeros(N, dtype=np.float64)
    nb = build_nb_cpu(L)
    z = nb.shape[1]

    T_g   = (K_BACK / 2.0)   * float(np.sum(chi * chi))
    T_m   = (1.0 / (2.0 * MU_M))   * float(np.sum(pi_m * pi_m))
    T_phi = (1.0 / (2.0 * MU_PHI)) * float(np.sum(pi_phi * pi_phi))

    E_A_g = (ALPHA / 2.0) * float(np.sum((sg - SIGMA_G_REF) ** 2))
    E_A_m = (ALPHA / 2.0) * float(np.sum((sm - SIGMA_M_REF) ** 2))

    sg_nb = sg[nb]; sm_nb = sm[nb]
    dsg = sg[:, None] - sg_nb
    dsm = sm[:, None] - sm_nb
    E_B_g = (BETA_G / (4.0 * z)) * float(np.sum(dsg * dsg))
    E_B_m = (BETA_M / (4.0 * z)) * float(np.sum(dsm * dsm))

    # R1: E_phi pure-XY
    phi_nb = phi[nb]
    cos_dphi = np.cos(phi[:, None] - phi_nb)
    beta_R1 = BETA_PHI / 2.0
    E_phi_A = -(beta_R1 / z) * float(np.sum(cos_dphi))

    # chi cross-terms (zero if chi=0)
    sgb = nb_mean_cpu(sg, nb)
    E_chi_rel   = -(CHI_REL / 2.0) * float(np.sum(chi * (sg - sgb)))
    E_chi_delta = -DELTA_CHI       * float(np.sum(chi * (SIGMA_G_REF - sg)))

    E_cpl = k_gm * float(np.sum((SIGMA_M_REF - sm) * (SIGMA_G_REF - sg))) if k_gm else 0.0

    deficit = SIGMA_M_REF - sm
    V_cp = 0.5 * G_V_COUPLE * float(np.sum((deficit ** 2) * (1.0 - np.cos(phi))))

    if channel_f:
        dis = disorder_cpu(phi, nb)
        E_F = 0.5 * GAMMA_PHI * float(np.sum(dis * sm * sm))
    else:
        E_F = 0.0

    H = (T_g + T_m + T_phi + E_A_g + E_A_m + E_B_g + E_B_m
         + E_phi_A + E_chi_rel + E_chi_delta + E_cpl + V_cp + E_F)

    return {
        'H': H,
        'T_g': T_g, 'T_m': T_m, 'T_phi': T_phi,
        'E_A_g': E_A_g, 'E_A_m': E_A_m,
        'E_B_g': E_B_g, 'E_B_m': E_B_m,
        'E_phi_A': E_phi_A,
        'E_chi_rel': E_chi_rel, 'E_chi_delta': E_chi_delta, 'E_cpl': E_cpl,
        'V_cp': V_cp, 'E_F': E_F,
    }


def ring_width_profile(sm, L):
    """Radial profile of sigma_m deficit around box centre (single-ring case)."""
    sm3d = sm.reshape(L, L, L)
    c = L / 2.0
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = np.where(xg - c > L/2, xg - c - L, np.where(xg - c < -L/2, xg - c + L, xg - c))
    dy = np.where(yg - c > L/2, yg - c - L, np.where(yg - c < -L/2, yg - c + L, yg - c))
    dz = np.where(zg - c > L/2, zg - c - L, np.where(zg - c < -L/2, zg - c + L, zg - c))
    # Ring axis assumed X: R = sqrt(dy^2 + dz^2), r_minor = sqrt((R-R_ring)^2 + dx^2)
    R_xy = np.sqrt(dy*dy + dz*dz)
    # Find ring radius from sigma_m deficit CoM
    dep = np.maximum(0.0, SIGMA_M_REF - sm3d)
    if dep.sum() < 1e-9:
        return {'R_ring': float('nan'), 'width_half_max': float('nan')}
    R_ring = float(np.sum(R_xy * dep) / np.sum(dep))
    r_minor = np.sqrt((R_xy - R_ring)**2 + dx*dx)

    # Bin by r_minor, radius bins 0..L/2
    bins = np.arange(0, L//2 + 1, 1.0)
    centers = 0.5 * (bins[:-1] + bins[1:])
    mean_dep = np.zeros(len(centers))
    for i in range(len(centers)):
        mask = (r_minor >= bins[i]) & (r_minor < bins[i+1])
        if mask.sum() > 0:
            mean_dep[i] = dep[mask].mean()

    # Half-max width (from max deficit to half of that)
    max_dep = mean_dep.max()
    if max_dep > 0:
        half = max_dep / 2
        # find first crossing
        for i in range(len(centers)):
            if mean_dep[i] < half:
                width = float(centers[i])
                break
        else:
            width = float('nan')
    else:
        width = float('nan')

    return {'R_ring': R_ring, 'width_half_max': width,
            'centers': centers.tolist(), 'mean_dep': mean_dep.tolist()}


def main():
    root = Path(__file__).resolve().parents[2]
    outdir = root / "07_validation" / "audits" / "qng-bi-ring-quick-analysis-v1"
    outdir.mkdir(parents=True, exist_ok=True)

    runs = {
        'single_R4_L20': {
            'path': root / "07_validation/audits/qng-v8-r1-long-time-v1/final_state.npz",
            'L': 20, 'mean_M_ref': 309.45,
        },
        'bi_d3_L24':    {
            'path': root / "07_validation/audits/qng-v8-r1-bi-ring-v3-d3/final_state.npz",
            'L': 24, 'mean_M_ref': 568.71, 'd': 3,
        },
        'bi_d4_L24':    {
            'path': root / "07_validation/audits/qng-v8-r1-bi-ring-v2-d4/final_state.npz",
            'L': 24, 'mean_M_ref': 523.62, 'd': 4,
        },
        'bi_d6_L24':    {
            'path': root / "07_validation/audits/qng-v8-r1-bi-ring-v1/final_state.npz",
            'L': 24, 'mean_M_ref': 600.63, 'd': 6,
        },
    }

    results = {}
    for name, info in runs.items():
        if not info['path'].exists():
            print(f"SKIP {name}: not found ({info['path']})")
            continue
        st = dict(np.load(info['path']))
        L = info['L']
        h = decompose_h_r1(st, L, k_gm=0.0, channel_f=True)
        # Ring width only meaningful for single-ring case
        width_info = ring_width_profile(st['sm'], L) if name == 'single_R4_L20' else None
        results[name] = {
            'L': L,
            'H_total': h['H'],
            'decomposition': h,
            'width_profile': width_info,
        }
        print(f"\n=== {name} (L={L}) ===")
        print(f"  H_total             = {h['H']:+.4f}")
        print(f"  --- Kinetic ---")
        print(f"    T_g  (chi)        = {h['T_g']:+.4f}")
        print(f"    T_m  (pi_m)       = {h['T_m']:+.4f}")
        print(f"    T_phi (pi_phi)    = {h['T_phi']:+.4f}")
        print(f"  --- Channel A (restoration) ---")
        print(f"    E_A_g             = {h['E_A_g']:+.4f}")
        print(f"    E_A_m             = {h['E_A_m']:+.4f}")
        print(f"  --- Channel B (gradient tension) ---")
        print(f"    E_B_g             = {h['E_B_g']:+.4f}")
        print(f"    E_B_m             = {h['E_B_m']:+.4f}")
        print(f"  --- Phase / couplings ---")
        print(f"    E_phi_A (XY)      = {h['E_phi_A']:+.4f}")
        print(f"    E_chi_rel         = {h['E_chi_rel']:+.4f}")
        print(f"    E_chi_delta       = {h['E_chi_delta']:+.4f}")
        print(f"    E_cpl             = {h['E_cpl']:+.4f}")
        print(f"    V_cp (V_couple)   = {h['V_cp']:+.4f}")
        print(f"    E_F (Channel F)   = {h['E_F']:+.4f}")
        if width_info:
            print(f"  --- Ring profile ---")
            print(f"    R_ring (CoM)      = {width_info['R_ring']:.3f}")
            print(f"    width_half_max    = {width_info['width_half_max']:.3f}")

    # --- Interaction-energy analysis ---
    print("\n" + "="*70)
    print("INTERACTION ENERGY vs INDEPENDENT PAIR")
    print("="*70)

    # Vacuum E_phi under R1 (pure XY, phi=0): -BETA_PHI/2 * N_nodes
    # Check: sum cos(0)=1, z=6, so E_phi_vac = -(BETA_PHI/2/z)*N*z*1 = -BETA_PHI*N/2
    def E_vac(L):
        return -BETA_PHI * (L**3) / 2.0

    if 'single_R4_L20' in results and len(results) > 1:
        H_single = results['single_R4_L20']['H_total']
        H_excess_single_L20 = H_single - E_vac(20)
        print(f"\nSingle ring R=4 L=20:")
        print(f"  H_final             = {H_single:+.4f}")
        print(f"  E_vac (L=20)        = {E_vac(20):+.4f}")
        print(f"  H_excess (single)   = {H_excess_single_L20:+.4f}  (ring 'mass' above vacuum)")
        print(f"  2 x excess (pair)   = {2*H_excess_single_L20:+.4f}")

        rows = []
        for d in [3, 4, 6]:
            key = f'bi_d{d}_L24'
            if key not in results:
                continue
            H_bi = results[key]['H_total']
            H_excess_bi = H_bi - E_vac(24)
            delta_H = H_excess_bi - 2 * H_excess_single_L20
            delta_M = results[key]['decomposition']  # placeholder
            row = (d, H_bi, H_excess_bi, delta_H, runs[key]['mean_M_ref'])
            rows.append(row)

        print(f"\n{'d':>3s}  {'H_bi':>10s}  {'H_excess':>10s}  {'dH_vs_2single':>14s}  {'<M>_t':>8s}  {'dM (%)':>8s}")
        print("-"*70)
        for (d, H_bi, H_ex, dH, M_mean) in rows:
            dM_pct = 100.0 * (M_mean - 2*runs['single_R4_L20']['mean_M_ref']) / (2*runs['single_R4_L20']['mean_M_ref'])
            print(f"{d:>3d}  {H_bi:+10.3f}  {H_ex:+10.3f}  {dH:+14.3f}  {M_mean:+8.2f}  {dM_pct:+8.2f}")

        # --- Plot LJ profile ---
        ds = [r[0] for r in rows]
        dHs = [r[3] for r in rows]
        dMs = [100.0 * (r[4] - 2*runs['single_R4_L20']['mean_M_ref']) / (2*runs['single_R4_L20']['mean_M_ref']) for r in rows]

        fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
        ax[0].plot(ds, dMs, 'o-', color='#d62728', linewidth=2, markersize=9)
        ax[0].axhline(0, color='k', linestyle='--', alpha=0.5, label='unbound')
        ax[0].set_xlabel('separation d (lu)', fontsize=11)
        ax[0].set_ylabel('Δ<M_total>_t / 2·M_single  (%)', fontsize=11)
        ax[0].set_title('Mass defect vs separation (LJ profile)', fontsize=11)
        ax[0].grid(alpha=0.3); ax[0].legend()

        ax[1].plot(ds, dHs, 's-', color='#1f77b4', linewidth=2, markersize=9)
        ax[1].axhline(0, color='k', linestyle='--', alpha=0.5, label='non-interacting')
        ax[1].set_xlabel('separation d (lu)', fontsize=11)
        ax[1].set_ylabel('ΔH_interaction  (lu)', fontsize=11)
        ax[1].set_title('Interaction energy vs separation', fontsize=11)
        ax[1].grid(alpha=0.3); ax[1].legend()

        fig.suptitle('GPU-032 bi-ring scan: Lennard-Jones potential signature (W+W-, R=4, L=24, T=5000 lu)',
                     fontsize=11, y=1.02)
        fig.tight_layout()
        plot_path = outdir / "lj_profile.png"
        fig.savefig(plot_path, dpi=130, bbox_inches='tight')
        print(f"\nPlot saved: {plot_path}")

    # --- Save JSON ---
    def _safe(v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        if isinstance(v, dict):
            return {k: _safe(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [_safe(x) for x in v]
        return v

    with open(outdir / "report.json", "w") as f:
        json.dump(_safe(results), f, indent=2)
    print(f"Report saved: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
