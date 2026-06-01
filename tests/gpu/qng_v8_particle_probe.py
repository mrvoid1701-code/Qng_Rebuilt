"""Einstein GPU-038: quantize the orbital attractor as a particle.

After GPU-037 B1+C1 established that phi is NOT bound inside sigma_m
deficits, the only remaining localized structure in v8 is the orbital
attractor from GPU-031f (R=4 ring, <M>_t ~ 310, universal basin).

This probe measures the attractor's PARTICLE-LIKE properties without
assuming anything about its internal constituents:

  1. Rest energy:        time-averaged H_v8
  2. Mass (topological): <M_ring>_t = sum(sigma_m_ref - sigma_m)
  3. Angular momentum:   L_z of sigma_m field
  4. Spatial extent:     R_eff from 2nd moment of sigma_m deficit
  5. Topological charge: phi winding number around ring axis
  6. Component budget:   <T_g>, <T_m>, <T_phi>, <E_v7>, <V_couple>

Protocol:
  Cached R=4 ring (v8 R1, L=28, T_P1=300, T_P2=1000).
  Full v8 symplectic evolution (no freeze): T=2000 lu, DT=0.025.
  Record observables every 10 lu (200 samples).

NOT expected to vary significantly — GPU-031f already showed the
attractor is robust. Point here is to EXTRACT particle-level observables
(spin, mass, size) so we have a clean identity card.
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
    """Center of mass of sigma_m deficit: COM = sum((σref-σm) r) / sum(σref-σm)."""
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
    """RMS radius of deficit distribution about com."""
    cx, cy, cz = com_xyz
    sm = cp.asnumpy(state['sm']).reshape(L, L, L)
    def_field = np.maximum(SIGMA_M_REF - sm, 0.0)
    W = def_field.sum()
    if W < 1e-10:
        return 0.0
    r2 = (xg - cx) ** 2 + (yg - cy) ** 2 + (zg - cz) ** 2
    return float(np.sqrt((def_field * r2).sum() / W))


def ang_mom_z(state, L, xg, yg, zg, com_xyz):
    """L_z of sigma_m field = sum((x-cx)*pi_m_y - (y-cy)*pi_m_x).

    Since pi_m is scalar (not vector), we use pi_m as the conjugate
    of sigma_m; the closest scalar-field analog of angular momentum is
        L_z = sum((y-cy)*d(sm)/dx - (x-cx)*d(sm)/dy) * pi_m
    but for a rotating ring without angular velocity this is 0.
    Instead we define a phi-based angular momentum:
        L_z_phi = sum((x-cx)*d(phi)/dy - (y-cy)*d(phi)/dx) * pi_phi
    which measures rotation of phi about the z-axis.
    """
    cx, cy, cz = com_xyz
    phi = cp.asnumpy(state['phi']).reshape(L, L, L)
    pi_phi = cp.asnumpy(state['pi_phi']).reshape(L, L, L)

    # Gradient of phi with periodic BC (wrap-aware via np.gradient won't wrap,
    # but for L=28 and localized structure this is acceptable)
    dphi_dx, dphi_dy, dphi_dz = np.gradient(phi)
    # Unwrap gradient jumps at +/- pi branch
    dphi_dx = np.mod(dphi_dx + np.pi, 2 * np.pi) - np.pi
    dphi_dy = np.mod(dphi_dy + np.pi, 2 * np.pi) - np.pi

    Lz_phi = float(np.sum(((xg - cx) * dphi_dy - (yg - cy) * dphi_dx)
                           * pi_phi))
    return Lz_phi


def phi_winding_z(state, L, R_ring, com_xyz):
    """Compute phi winding number around a circle of radius R_ring
    in the z=cz plane centered at (cx, cy).
    """
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
    """Return (T_g, T_m, T_phi, V_couple_placeholder, H_total)."""
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    T_g   = (K_BACK / 2.0)   * float(cp.sum(chi * chi))
    T_m   = (1.0 / (2.0 * MU_M))   * float(cp.sum(pi_m * pi_m))
    T_phi = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))
    # V_couple = (g/2)*(σref-σm)^2*(1-cos phi)
    V_c = (G_V_COUPLE / 2.0) * float(
        cp.sum((SIGMA_M_REF - sm) ** 2 * (1.0 - cp.cos(phi))))
    H_total = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                                     exact_a=EXACT_A_MODE))
    return T_g, T_m, T_phi, V_c, H_total


def main():
    L = 28
    R = 4
    T_P1 = 300.0
    T_P2 = 1000.0
    T_run = 2000.0
    sample_every_lu = 10.0

    print("=" * 80)
    print("GPU-038: Particle-properties probe (orbital attractor)")
    print("=" * 80)
    print(f"  L={L}, R={R}, P1={T_P1}, P2={T_P2}")
    print(f"  T_run={T_run} lu, DT={DT}, sample every {sample_every_lu} lu")

    state, nb_idx = form_ring_cached(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT)
    print(f"  Initial M_ring = {float(ring_mass_deficit(state['sm'])):.2f}")

    xg, yg, zg, cx_geom, cy_geom, cz_geom = lattice_coords(L)

    # Initial snapshot
    t0 = 0.0
    com0 = com(state, L, xg, yg, zg)
    print(f"  Initial COM = ({com0[0]:.2f}, {com0[1]:.2f}, {com0[2]:.2f}), "
          f"W_def_initial = {com0[3]:.2f}")

    n_steps = int(T_run / DT)
    sample_every = max(1, int(sample_every_lu / DT))

    times = []
    M_ring_arr = []
    H_arr = []
    T_g_arr, T_m_arr, T_phi_arr, V_c_arr = [], [], [], []
    com_x_arr, com_y_arr, com_z_arr = [], [], []
    r_eff_arr = []
    Lz_phi_arr = []
    winding_arr = []

    def record(t):
        c = com(state, L, xg, yg, zg)
        if c is None:
            return
        cx, cy, cz, W = c
        times.append(t)
        M_ring_arr.append(float(ring_mass_deficit(state['sm'])))
        Tg, Tm, Tp, Vc, H = hamiltonian_components(state, nb_idx)
        H_arr.append(H)
        T_g_arr.append(Tg)
        T_m_arr.append(Tm)
        T_phi_arr.append(Tp)
        V_c_arr.append(Vc)
        com_x_arr.append(cx)
        com_y_arr.append(cy)
        com_z_arr.append(cz)
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
                  f"H={H_arr[-1]:.3f}  Lz_phi={Lz_phi_arr[-1]:.2e}")

    wall = time.time() - t_start

    # Skip first 500 lu (transient burn-in before orbital attractor is set)
    t_arr = np.array(times)
    warm = t_arr > 500.0
    if warm.sum() < 10:
        warm = np.ones(len(t_arr), dtype=bool)

    def stats(arr, mask):
        a = np.asarray(arr)[mask]
        return {
            'mean': float(a.mean()), 'std': float(a.std()),
            'min': float(a.min()), 'max': float(a.max()),
        }

    summary = {
        'M_ring':     stats(M_ring_arr, warm),
        'H':          stats(H_arr, warm),
        'T_g':        stats(T_g_arr, warm),
        'T_m':        stats(T_m_arr, warm),
        'T_phi':      stats(T_phi_arr, warm),
        'V_couple':   stats(V_c_arr, warm),
        'r_eff':      stats(r_eff_arr, warm),
        'Lz_phi':     stats(Lz_phi_arr, warm),
        'phi_winding': stats(winding_arr, warm),
        'com_x':      stats(com_x_arr, warm),
        'com_y':      stats(com_y_arr, warm),
        'com_z':      stats(com_z_arr, warm),
    }

    print("\n" + "=" * 80)
    print(f"PARTICLE PROPERTIES (time-averaged over t > 500 lu, wall={wall:.0f}s)")
    print("=" * 80)
    for k, s in summary.items():
        print(f"  {k:12s}  mean={s['mean']:+.4e}  std={s['std']:.3e}  "
              f"range=[{s['min']:.4e},{s['max']:.4e}]")

    print("\n  Rest-frame interpretation:")
    print(f"    M_ring (topological) = {summary['M_ring']['mean']:.2f}  "
          f"+/- {summary['M_ring']['std']:.2f}")
    print(f"    Rest energy H_v8    = {summary['H']['mean']:.3f}  "
          f"+/- {summary['H']['std']:.3f}")
    H_split = summary['T_g']['mean'] + summary['T_m']['mean'] + summary['T_phi']['mean']
    H_pot   = summary['H']['mean'] - H_split
    print(f"    Kinetic split  T_g+T_m+T_phi = {H_split:.3f}  "
          f"(T_g={summary['T_g']['mean']:.3f}, "
          f"T_m={summary['T_m']['mean']:.3f}, T_phi={summary['T_phi']['mean']:.3f})")
    print(f"    Potential remainder          = {H_pot:.3f}")
    print(f"    V_couple                     = {summary['V_couple']['mean']:.3f}")
    print(f"    R_eff (rms size)             = {summary['r_eff']['mean']:.2f} lu")
    print(f"    L_z (phi rotation)           = {summary['Lz_phi']['mean']:.2e} "
          f"(std {summary['Lz_phi']['std']:.2e})")
    print(f"    phi winding around z-axis    = {summary['phi_winding']['mean']:.3f}")

    # Minimal particle identity verdict
    verdict_lines = []
    if abs(summary['Lz_phi']['mean']) > 3 * summary['Lz_phi']['std']:
        verdict_lines.append(
            f"SPIN_DETECTED: L_z mean {summary['Lz_phi']['mean']:.2e} exceeds 3 sigma")
    else:
        verdict_lines.append("SPIN_NULL: L_z consistent with zero (scalar particle)")
    if abs(summary['phi_winding']['mean']) > 0.5:
        verdict_lines.append(
            f"TOPOLOGICAL_CHARGE: winding = {summary['phi_winding']['mean']:.2f}")
    else:
        verdict_lines.append(
            f"NO_WINDING: Q ~ {summary['phi_winding']['mean']:.3f}")
    print(f"\n  VERDICT: {' | '.join(verdict_lines)}")

    audit = ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1"
    audit.mkdir(parents=True, exist_ok=True)
    with open(audit / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'T_run': T_run,
            'sample_every_lu': sample_every_lu,
            'n_samples_total': len(times),
            'n_samples_warm': int(warm.sum()),
            'g': G_V_COUPLE, 'mu_phi': MU_PHI, 'mu_m': MU_M,
            'beta_phi': BETA_PHI, 'beta_g': BETA_G, 'beta_m': BETA_M,
            'sigma_m_ref': SIGMA_M_REF, 'sigma_g_ref': SIGMA_G_REF,
            'summary': summary,
            'verdict_lines': verdict_lines,
            'wall_s': wall,
        }, f, indent=2)
    np.savez(audit / "traces.npz",
             times=t_arr,
             M_ring=np.array(M_ring_arr),
             H=np.array(H_arr),
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
