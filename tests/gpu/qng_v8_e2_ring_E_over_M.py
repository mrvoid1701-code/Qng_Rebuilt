"""Einstein test #2: E_ring / M_ring on a real ring (DER-QNG-042 E^2).

Forms a canonical R=4 vortex ring via Phase1+Phase2 (CPU-074/075 protocol,
reduced to L=24 for speed), then measures:

    M_ring = sum(SIGMA_M_REF - sigma_m)            [CPU-074 canonical mass]
    E_ring = H_v8(ring_state) - H_v8(vacuum)      [above-vacuum energy]

and reports the ratio c_eff^2 := E_ring / M_ring.

Expected from phi dispersion (DER-QNG-043):
    c_phi^2 = BETA_PHI / (6 * mu_phi) = 0.01167

If the ring's above-vacuum energy is dominated by rest-mass-like content
(phi mass term + deficit energy), the ratio should come out close to c_phi^2
or some universal combination. If it deviates, the difference tells us how
much of the ring's energy is gradient/string-tension vs rest-mass — which
informs the "E=mc^2 for an extended object" interpretation.
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
    SIGMA_G_REF, SIGMA_M_REF, MU_PHI, MU_M, G_V_COUPLE,
    BETA_PHI, BETA_G, BETA_M, ALPHA, K_BACK, CHI_DECAY_V7,
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    hamiltonian_v8, ring_mass_deficit, ring_radius,
)

DT = 0.025


def run_ring_formation(L, R, T_P1=300.0, T_P2=500.0, T_P3=300.0, gamma=0.05,
                       verbose=True):
    """Form a canonical ring, damp to rest frame, return (state, nb_idx)."""
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)

    t0 = time.time()
    # Phase 1: ring formation, V_couple OFF
    n1 = int(T_P1 / DT)
    for _ in range(n1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=False,
                              chi_decay=CHI_DECAY_V7)
    t_p1 = time.time() - t0
    if verbose:
        print(f"  Phase 1 done ({n1} steps, {t_p1:.1f}s)")

    # Phase 2: V_couple ON
    n2 = int(T_P2 / DT)
    for s in range(n2):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
        if verbose and (s + 1) % max(1, n2 // 5) == 0:
            M = ring_mass_deficit(state['sm'])
            R_meas = ring_radius(state['sm'], L)
            print(f"    P2 {(s+1)*DT:.0f}/{T_P2:.0f}  M={M:.2f}  R={R_meas:.2f}")
    t_p2 = time.time() - t0 - t_p1
    if verbose:
        print(f"  Phase 2 done ({n2} steps, {t_p2:.1f}s)")

    # Phase 3: damp kinetic DOFs to approach rest frame
    n3 = int(T_P3 / DT)
    for s in range(n3):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7,
                              damping_gamma=gamma)
        if verbose and (s + 1) % max(1, n3 // 3) == 0:
            M = ring_mass_deficit(state['sm'])
            R_meas = ring_radius(state['sm'], L)
            Tphi_now = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(state['pi_phi'] ** 2))
            print(f"    P3 {(s+1)*DT:.0f}/{T_P3:.0f}  gamma={gamma}  "
                  f"M={M:.2f}  R={R_meas:.2f}  T_phi={Tphi_now:.3f}")
    t_p3 = time.time() - t0 - t_p1 - t_p2
    if verbose:
        print(f"  Phase 3 done ({n3} steps, {t_p3:.1f}s)  [rest-frame approach]")

    return state, nb_idx


def hamiltonian_components(state, nb_idx):
    """Return full breakdown of H_v8 contributions."""
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']

    T_g = (K_BACK / 2.0) * float(cp.sum(chi * chi))
    T_m = (1.0 / (2.0 * MU_M)) * float(cp.sum(pi_m * pi_m))
    T_phi = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))

    from qng_v8_canonical_gpu import nb_mean
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    E_A_g = (ALPHA / 2.0) * float(cp.sum((sg - SIGMA_G_REF) ** 2))
    E_A_m = (ALPHA / 2.0) * float(cp.sum((sm - SIGMA_M_REF) ** 2))
    E_B_g = (BETA_G / 2.0) * float(cp.sum((sg - sgb) ** 2)) * 3.0
    E_B_m = (BETA_M / 2.0) * float(cp.sum((sm - smb) ** 2)) * 3.0

    deficit = SIGMA_M_REF - sm
    V_cp = 0.5 * float(G_V_COUPLE) * float(cp.sum((deficit * deficit) * (1.0 - cp.cos(phi))))

    total = T_g + T_m + T_phi + E_A_g + E_A_m + E_B_g + E_B_m + V_cp
    return {
        'T_g': T_g, 'T_m': T_m, 'T_phi': T_phi,
        'E_A_g': E_A_g, 'E_A_m': E_A_m,
        'E_B_g': E_B_g, 'E_B_m': E_B_m,
        'V_cp': V_cp,
        'total': total,
    }


def main():
    print("=" * 80)
    print("Einstein test #2: E_ring / M_ring (DER-QNG-042 E^2)")
    print("=" * 80)
    print(f"  g={G_V_COUPLE}  mu_phi={MU_PHI:.4f}  BETA_PHI={BETA_PHI}")

    L = 24
    R = 4

    # --- Vacuum reference ---
    print()
    print(f"[Vacuum reference] L={L}")
    nb_idx = build_nb(L)
    vac_state = make_state(L, phi_init=None)
    vac = hamiltonian_components(vac_state, nb_idx)
    print(f"  H_vacuum = {vac['total']:.6e}  (T_g={vac['T_g']:.3e}  "
          f"V_cp={vac['V_cp']:.3e})")

    # --- Ring formation ---
    print()
    print(f"[Ring formation] L={L}, R={R}, P1=300lu, P2=1000lu, P3=300lu(damp)")
    state, nb_idx = run_ring_formation(L, R, T_P1=300.0, T_P2=1000.0,
                                       T_P3=300.0, gamma=0.1, verbose=True)

    ring = hamiltonian_components(state, nb_idx)
    M_ring = ring_mass_deficit(state['sm'])
    R_meas = ring_radius(state['sm'], L)

    print()
    print("[Ring Hamiltonian breakdown]")
    print(f"  T_g        = {ring['T_g']:>12.4f}   (chi kinetic)")
    print(f"  T_m        = {ring['T_m']:>12.4f}   (pi_m kinetic)")
    print(f"  T_phi      = {ring['T_phi']:>12.4f}   (pi_phi kinetic)")
    print(f"  E_A_g      = {ring['E_A_g']:>12.4f}   (sigma_g -> ref)")
    print(f"  E_A_m      = {ring['E_A_m']:>12.4f}   (sigma_m -> ref)")
    print(f"  E_B_g      = {ring['E_B_g']:>12.4f}   (sigma_g smoothness)")
    print(f"  E_B_m      = {ring['E_B_m']:>12.4f}   (sigma_m smoothness)")
    print(f"  V_cp       = {ring['V_cp']:>12.4f}   (E^2 mass term)")
    print(f"  H_total    = {ring['total']:>12.4f}")
    print()
    print(f"  M_ring (CPU-074) = {M_ring:.4f}")
    print(f"  R_measured       = {R_meas:.4f}")

    # --- Einstein ratio ---
    E_above_vacuum = ring['total'] - vac['total']
    ratio = E_above_vacuum / max(M_ring, 1e-12)

    # Theoretical c^2 candidates
    c_phi_sq = float(BETA_PHI) / (6.0 * float(MU_PHI))
    c_g_sq_est = float(K_BACK) * float(BETA_G) / 6.0    # v6 wave-speed form
    c_m_sq_est = float(BETA_M) / (6.0 * float(MU_M))    # analogous to phi

    print()
    print("=" * 80)
    print("EINSTEIN E=mc^2 CHECK")
    print("=" * 80)
    print(f"  E_ring (above vacuum) = {E_above_vacuum:.4f}")
    print(f"  M_ring                = {M_ring:.4f}")
    print(f"  ratio E/M := c_eff^2  = {ratio:.5f}")
    print()
    print("Reference 'speed-of-light squared' candidates in QNG units:")
    print(f"  c_phi^2  = BETA_PHI / (6 mu_phi)   = {c_phi_sq:.5f}")
    print(f"  c_m^2    = BETA_M / (6 mu_m)       = {c_m_sq_est:.5f}")
    print(f"  c_g^2    = K_BACK * BETA_G / 6     = {c_g_sq_est:.5f}")
    print()
    print("Component shares (fraction of H above vacuum):")
    for key in ['T_g', 'T_m', 'T_phi', 'E_A_g', 'E_A_m', 'E_B_g', 'E_B_m', 'V_cp']:
        delta = ring[key] - vac[key]
        frac = delta / max(E_above_vacuum, 1e-12)
        print(f"  {key:>6}: {delta:>12.4f}   ({frac*100:>6.2f}%)")


if __name__ == "__main__":
    main()
