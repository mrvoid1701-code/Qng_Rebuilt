"""QNG-GPU-020 Option E^2 verification probe.

Option E (linear) stabilized sigma_g (sg_min=0.5000 all configs) but introduced
tachyonic phi when sigma_m overshoots sigma_m_ref: m_phi^2 = g*(sm_ref-sm)/mu_phi
becomes negative, producing H drift 10^15-10^16.

Option E^2 (quadratic) cures this by design:

    V_couple_E2 = (g/2) * (sigma_m_ref - sigma_m)^2 * (1 - cos phi)

Properties:
    dV/dsigma_g = 0                                    (drain vanishes)
    dV/dsigma_m = -g*(sm_ref - sm)*(1-cos phi)         (linear restoring)
    dV/dphi     = (g/2)*(sm_ref - sm)^2 * sin(phi)     (mass^2 >= 0 ALWAYS)

m_phi^2(x) = g*(sm_ref - sm(x))^2 / mu_phi  >=  0    <- tachyonic mode gone
phi is MASSLESS in vacuum (sm = sm_ref -> deficit^2 = 0, Goldstone preserved)
phi is MASSIVE inside rings (sm < sm_ref) AND outside if sm overshoots
(same mass sign on both sides = oscillator not runaway).

Procedure: same as option_e_probe, but new force/potential forms.
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
    SIGMA_G_REF, SIGMA_M_REF, MU_PHI,
    ALPHA, BETA_G, BETA_M, BETA_PHI, GAMMA_PHI, K_BACK,
    build_nb, init_phi_single_ring, make_state,
    nb_mean, disorder_gpu, phi_wmean_gpu, wrap_gpu,
    yoshida4_step, SIGMA_G_MIN_ABORT,
)


# ============================================================================
# Option E^2 force overrides  (quadratic in sigma_m deficit)
# ============================================================================

def force_sm_v8_E2(sg, sm, phi, nb_idx):
    """F_sm = -dE_v7/dsm - dV_couple_E2/dsm
         = F_e_v7 + g*(sm_ref - sm)*(1 - cos phi)
    Linear restoring force (same sign as Option E, but modulated by deficit).
    """
    smb = nb_mean(sm, nb_idx)
    dis = disorder_gpu(phi, nb_idx)
    F_e_v7 = ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm) - GAMMA_PHI * dis * sm
    deficit = SIGMA_M_REF - sm
    F_couple = v8.G_V_COUPLE * deficit * (1.0 - cp.cos(phi))
    return F_e_v7 + F_couple


def force_phi_v8_E2(sg, sm, phi, nb_idx):
    """F_phi = -dE_v7/dphi - dV_couple_E2/dphi
         = BETA_PHI*(pm - phi) - (g/2)*(sm_ref - sm)^2 * sin(phi)
    Mass^2 = g*(sm_ref - sm)^2 / mu_phi >= 0 always (deficit squared).
    """
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    return BETA_PHI * wrap_gpu(pm - phi) - 0.5 * v8.G_V_COUPLE * (deficit * deficit) * cp.sin(phi)


def drive_sg_v7style_E2(sg, sm, chi, phi, nb_idx, k_gm, include_v_couple=True):
    """sigma_g drive under Option E^2: V_couple has NO sigma_g dependence.
    Same as Option E — pure v7 drive_sg, no back-reaction on sg.
    """
    sgb = nb_mean(sg, nb_idx)
    dsg = (ALPHA * (SIGMA_G_REF - sg)
           + BETA_G * (sgb - sg)
           + K_BACK * chi
           - k_gm * (SIGMA_M_REF - sm))
    return dsg


def hamiltonian_v8_E2(state, nb_idx):
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    T_g       = (K_BACK / 2.0)   * float(cp.sum(chi * chi))
    T_m       = (1.0 / (2.0 * 10.0))   * float(cp.sum(pi_m * pi_m))
    T_phi_kin = (1.0 / (2.0 * 0.857)) * float(cp.sum(pi_phi * pi_phi))
    sgb = nb_mean(sg, nb_idx); smb = nb_mean(sm, nb_idx)
    E_A_g = (ALPHA / 2.0) * float(cp.sum((sg - SIGMA_G_REF) ** 2))
    E_A_m = (ALPHA / 2.0) * float(cp.sum((sm - SIGMA_M_REF) ** 2))
    E_B_g = (BETA_G / 2.0) * float(cp.sum((sg - sgb) ** 2)) * 3.0
    E_B_m = (BETA_M / 2.0) * float(cp.sum((sm - smb) ** 2)) * 3.0
    deficit = SIGMA_M_REF - sm
    V_cp  = 0.5 * v8.G_V_COUPLE * float(cp.sum((deficit * deficit) * (1.0 - cp.cos(phi))))
    return T_g + T_m + T_phi_kin + E_A_g + E_A_m + E_B_g + E_B_m + V_cp


# Install Option E^2 overrides globally
v8.force_sm_v8       = force_sm_v8_E2
v8.force_phi_v8      = force_phi_v8_E2
v8.drive_sg_v7style  = drive_sg_v7style_E2
v8.hamiltonian_v8    = hamiltonian_v8_E2


# ============================================================================
# Probe  (same structure as option_e_probe.py)
# ============================================================================

def probe_single_ring(dt, gamma, L=16, R=4, t_max=20.0, k_gm=0.0, tag=""):
    nsteps = int(t_max / dt)
    nb = build_nb(L)
    phi0 = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi0)

    H0 = v8.hamiltonian_v8(state, nb)
    sg_min0 = float(cp.min(state['sg']))
    sm_min0 = float(cp.min(state['sm']))
    sm_max0 = float(cp.max(state['sm']))

    first_breach = None
    sample = max(1, nsteps // 50)
    t0 = time.time()
    for s in range(1, nsteps + 1):
        state = yoshida4_step(state, dt, nb, k_gm=k_gm,
                              damping_gamma=gamma, v_couple_on=True)
        if cp.any(cp.isnan(state['sg'])) or cp.any(cp.isnan(state['sm'])) \
                or cp.any(cp.isnan(state['phi'])):
            return {'tag': tag, 'dt': dt, 'gamma': gamma,
                    'nan_step': s, 'survived': False,
                    'wall': time.time() - t0}
        if s % sample == 0 or s == nsteps:
            sg_min = float(cp.min(state['sg']))
            if sg_min < SIGMA_G_MIN_ABORT and first_breach is None:
                first_breach = s

    wall = time.time() - t0
    H_final = v8.hamiltonian_v8(state, nb)
    drift = (H_final - H0) / max(abs(H0), 1e-12)
    return {
        'tag': tag, 'dt': dt, 'gamma': gamma,
        'nsteps': nsteps, 'nan_step': None, 'survived': True,
        'sg_min_initial': sg_min0,
        'sg_min_final': float(cp.min(state['sg'])),
        'sm_min_initial': sm_min0,
        'sm_min_final': float(cp.min(state['sm'])),
        'sm_max_initial': sm_max0,
        'sm_max_final': float(cp.max(state['sm'])),
        'first_breach_step': first_breach,
        'first_breach_time': first_breach * dt if first_breach else None,
        'H0': H0, 'H_final': H_final, 'drift_rel': drift,
        'wall': wall,
    }


def main():
    print("=" * 78)
    print("Option E^2 verification probe - V_couple = (g/2)*(sm_ref-sm)^2*(1-cos phi)")
    print("=" * 78)
    print(f"  g={v8.G_V_COUPLE}  SIGMA_G_MIN_ABORT={SIGMA_G_MIN_ABORT}")
    print(f"  sigma_g sector under E^2: PURE v7 (no V_couple backreaction on sg)")
    print(f"  sigma_m sector: force += g*(sm_ref-sm)*(1-cos phi) (deficit-modulated restoring)")
    print(f"  phi sector: F_phi_mass = -(g/2)*(sm_ref-sm)^2 * sin(phi) (mass^2 >= 0 ALWAYS)")
    print(f"  phi is MASSLESS in vacuum (Goldstone preserved) and massive near rings.")
    print()

    configs = [
        (0.025, 0.00, "baseline dt=0.025, no damping"),
        (0.010, 0.00, "dt=0.010, no damping"),
        (0.005, 0.00, "dt=0.005, no damping"),
        (0.025, 0.01, "dt=0.025, gamma=0.01 Langevin"),
        (0.025, 0.05, "dt=0.025, gamma=0.05 Langevin"),
        (0.010, 0.01, "dt=0.010, gamma=0.01 Langevin"),
    ]

    print("--- PART 1: Single ring L=16 R=4 t_max=20.0 ---")
    part1 = []
    for dt, gamma, tag in configs:
        print(f"  [{tag}]")
        r = probe_single_ring(dt, gamma, L=16, R=4, t_max=20.0, tag=tag)
        part1.append(r)
        if not r['survived']:
            print(f"     FAILED: NaN at step {r['nan_step']}")
        else:
            br = (f"breach @step {r['first_breach_step']} (t={r['first_breach_time']:.2f})"
                  if r['first_breach_step'] is not None else "NO breach")
            print(f"     OK ({r['wall']:.1f}s)  sg_min={r['sg_min_final']:.4f}  "
                  f"sm=[{r['sm_min_final']:.3f},{r['sm_max_final']:.3f}]  "
                  f"drift={r['drift_rel']:+.2e}  {br}")
        print()

    print("--- PART 2: Single ring L=32 R=4 t_max=20.0 (cleaner background) ---")
    part2 = []
    for dt, gamma, tag in configs[:3]:
        print(f"  [{tag}]")
        r = probe_single_ring(dt, gamma, L=32, R=4, t_max=20.0, tag=tag + " @L=32")
        part2.append(r)
        if not r['survived']:
            print(f"     FAILED: NaN at step {r['nan_step']}")
        else:
            br = (f"breach @step {r['first_breach_step']} (t={r['first_breach_time']:.2f})"
                  if r['first_breach_step'] is not None else "NO breach")
            print(f"     OK ({r['wall']:.1f}s)  sg_min={r['sg_min_final']:.4f}  "
                  f"sm=[{r['sm_min_final']:.3f},{r['sm_max_final']:.3f}]  "
                  f"drift={r['drift_rel']:+.2e}  {br}")
        print()

    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    all_L16_no_breach = all(r['survived'] and r['first_breach_step'] is None for r in part1)
    all_L32_no_breach = all(r['survived'] and r['first_breach_step'] is None for r in part2)
    all_survived_no_nan = all(r['survived'] for r in part1 + part2)

    # Check drift magnitude: with proper dynamics (bounded phi mass^2), drift
    # should be sub-percent for dt=0.005, O(1%) for dt=0.025.
    max_abs_drift = max(abs(r['drift_rel']) for r in part1 + part2 if r['survived'])

    if all_L16_no_breach and all_L32_no_breach and max_abs_drift < 0.10:
        print("OPTION E^2 CONFIRMED:")
        print("  - sigma_g stays above threshold in ALL configs.")
        print(f"  - H drift bounded: max |drift| = {max_abs_drift:.2e} (< 10%).")
        print("  - No tachyonic blowup -> phi mass^2 >= 0 enforced by construction.")
        print()
        print("  -> DER-QNG-042 amendment approved with V_couple Option E^2.")
        print("  -> Proceed: amend V_couple in qng_v8_canonical_gpu.py, VOID old GPU-020,")
        print("     restructure Stage A gate (measure omega inside ring core), re-run full.")
    elif all_L16_no_breach and all_L32_no_breach:
        print("OPTION E^2 PARTIAL: sigma_g stable but H drift large.")
        print(f"  max |drift| = {max_abs_drift:.2e}")
        print("  -> Diagnose drift source (integrator order? dt too coarse?)")
    elif all_survived_no_nan:
        print("OPTION E^2 INSUFFICIENT: some configs breached sigma_g_min.")
        for r in part1 + part2:
            if r['first_breach_step'] is not None:
                print(f"    {r['tag']}: breach at t={r['first_breach_time']:.2f}  sg_min={r['sg_min_final']:.4f}")
    else:
        print("OPTION E^2 FAILS: NaN observed in at least one config.")
        for r in part1 + part2:
            if not r['survived']:
                print(f"    {r['tag']}: NaN at step {r['nan_step']}")


if __name__ == "__main__":
    main()
