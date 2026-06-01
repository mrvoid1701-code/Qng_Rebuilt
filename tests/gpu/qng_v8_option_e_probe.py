"""QNG-GPU-020 Option E verification probe.

After qng_v8_stability_probe + g_scan showed V_couple = g*sigma_g*(1-cos phi)
produces monotonic sigma_g drain with sg_min=0 at t_phys~=1.5 across the
entire Stage-A-allowed g window, two independent reviews (einstein-mind,
savant-physics-reviewer) converged on Option E:

    V_couple_E = g * (sigma_m_ref - sigma_m) * (1 - cos phi)

Properties:
    dV/dsigma_g = 0      (drain term VANISHES by construction)
    dV/dsigma_m = -g*(1-cos phi)  -> force on sm is +g*(1-cos phi) (restoring)
    dV/dphi     = g*(sigma_m_ref - sm) * sin(phi)

Physics: phi acquires mass INSIDE rings (where sm < sm_ref) and remains
MASSLESS in vacuum. m_phi^2(x) = g * (sigma_m_ref - sm(x)) / mu_phi.
This is the superconducting-condensate analogue — photon gapped inside
material, massless outside. Goldstone theorem satisfied globally.

Procedure:
    Monkey-patch qng_v8_canonical_gpu force functions to Option E form,
    re-run the same 6 configs as qng_v8_stability_probe on single ring L=16 R=4,
    then g-scan at L=32 for good measure. If sigma_g stays above SIGMA_G_MIN_ABORT
    in all configs -> Option E confirmed. Stage A gate needs restructuring
    separately (measure omega inside ring core, not in vacuum).
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
# Option E force overrides
# ============================================================================

def force_sm_v8_E(sg, sm, phi, nb_idx):
    """F_sm = -dE_v7/dsm - dV_couple_E/dsm
         = [ALPHA(ref-sm) + BETA_M(<sm>-sm) - GAMMA_PHI*dis*sm] + g*(1-cos phi)
    V_couple_E = g*(sm_ref - sm)*(1-cos phi) contributes restoring +g*(1-cos phi) on sm.
    """
    smb = nb_mean(sm, nb_idx)
    dis = disorder_gpu(phi, nb_idx)
    F_e_v7 = ALPHA * (SIGMA_M_REF - sm) + BETA_M * (smb - sm) - GAMMA_PHI * dis * sm
    F_couple = v8.G_V_COUPLE * (1.0 - cp.cos(phi))
    return F_e_v7 + F_couple


def force_phi_v8_E(sg, sm, phi, nb_idx):
    """F_phi = -dE_v7/dphi - dV_couple_E/dphi
         = BETA_PHI*(pm - phi) - g*(sm_ref - sm)*sin(phi)
    """
    pm = phi_wmean_gpu(phi, sm, nb_idx)
    deficit = SIGMA_M_REF - sm
    return BETA_PHI * wrap_gpu(pm - phi) - v8.G_V_COUPLE * deficit * cp.sin(phi)


def drive_sg_v7style_E(sg, sm, chi, phi, nb_idx, k_gm, include_v_couple=True):
    """sigma_g drive under Option E:  V_couple has NO sigma_g dependence.
    Drops the -G_V_COUPLE*(1-cos phi) term entirely. Pure v7 drive_sg remains.
    """
    sgb = nb_mean(sg, nb_idx)
    dsg = (ALPHA * (SIGMA_G_REF - sg)
           + BETA_G * (sgb - sg)
           + K_BACK * chi
           - k_gm * (SIGMA_M_REF - sm))
    # NO V_couple backreaction on sigma_g (this is the essence of Option E).
    return dsg


def hamiltonian_v8_E(state, nb_idx):
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
    V_cp  = v8.G_V_COUPLE * float(cp.sum((SIGMA_M_REF - sm) * (1.0 - cp.cos(phi))))
    return T_g + T_m + T_phi_kin + E_A_g + E_A_m + E_B_g + E_B_m + V_cp


# Install Option E overrides globally
v8.force_sm_v8       = force_sm_v8_E
v8.force_phi_v8      = force_phi_v8_E
v8.drive_sg_v7style  = drive_sg_v7style_E
v8.hamiltonian_v8    = hamiltonian_v8_E


# ============================================================================
# Probe
# ============================================================================

def probe_single_ring(dt, gamma, L=16, R=4, t_max=20.0, k_gm=0.0, tag=""):
    nsteps = int(t_max / dt)
    nb = build_nb(L)
    phi0 = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi0)

    H0 = v8.hamiltonian_v8(state, nb)
    sg_min0 = float(cp.min(state['sg']))
    sm_min0 = float(cp.min(state['sm']))

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
        'first_breach_step': first_breach,
        'first_breach_time': first_breach * dt if first_breach else None,
        'H0': H0, 'H_final': H_final, 'drift_rel': drift,
        'wall': wall,
    }


def main():
    print("=" * 78)
    print("Option E verification probe — V_couple = g*(sm_ref - sm)*(1 - cos phi)")
    print("=" * 78)
    print(f"  g={v8.G_V_COUPLE}  SIGMA_G_MIN_ABORT={SIGMA_G_MIN_ABORT}")
    print(f"  sigma_g sector under E: PURE v7 (no V_couple backreaction on sg)")
    print(f"  sigma_m sector: force += g*(1-cos phi) = restoring against Channel F")
    print(f"  phi sector: F_phi_mass = -g*(sm_ref - sm)*sin(phi)  [gapped inside ring only]")
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
            print(f"     OK ({r['wall']:.1f}s)  sg_min final={r['sg_min_final']:.4f}  "
                  f"sm_min final={r['sm_min_final']:.4f}  drift={r['drift_rel']:+.2e}  {br}")
        print()

    any_stable_L16 = any(r['survived'] and r['first_breach_step'] is None for r in part1)
    print("--- PART 2: Single ring L=32 R=4 t_max=20.0 (cleaner background) ---")
    part2 = []
    for dt, gamma, tag in configs[:3]:  # only no-damping runs, faster
        print(f"  [{tag}]")
        r = probe_single_ring(dt, gamma, L=32, R=4, t_max=20.0, tag=tag + " @L=32")
        part2.append(r)
        if not r['survived']:
            print(f"     FAILED: NaN at step {r['nan_step']}")
        else:
            br = (f"breach @step {r['first_breach_step']} (t={r['first_breach_time']:.2f})"
                  if r['first_breach_step'] is not None else "NO breach")
            print(f"     OK ({r['wall']:.1f}s)  sg_min final={r['sg_min_final']:.4f}  "
                  f"sm_min final={r['sm_min_final']:.4f}  drift={r['drift_rel']:+.2e}  {br}")
        print()

    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    all_L16_no_breach = all(r['survived'] and r['first_breach_step'] is None for r in part1)
    all_L32_no_breach = all(r['survived'] and r['first_breach_step'] is None for r in part2)
    all_survived_no_nan = all(r['survived'] for r in part1 + part2)

    if all_L16_no_breach and all_L32_no_breach:
        print("OPTION E CONFIRMED: sigma_g stays above threshold in ALL configs.")
        print("  -> DER-QNG-042 amendment approved.")
        print("  -> Proceed: amend V_couple in qng_v8_canonical_gpu.py, VOID old GPU-020,")
        print("     restructure Stage A gate (measure omega inside ring core), re-run full.")
    elif all_survived_no_nan:
        print("OPTION E PARTIAL: no NaN but some configs breached sigma_g_min.")
        print("  Breach configs:")
        for r in part1 + part2:
            if r['first_breach_step'] is not None:
                print(f"    {r['tag']}: breach at t={r['first_breach_time']:.2f}  sg_min={r['sg_min_final']:.4f}")
        print("  -> Option E improves over original but requires additional stabilization.")
    else:
        print("OPTION E FAILS: NaN observed in at least one config.")
        for r in part1 + part2:
            if not r['survived']:
                print(f"    {r['tag']}: NaN at step {r['nan_step']}")
        print("  -> Theory requires deeper rethink. Option E alone insufficient.")


if __name__ == "__main__":
    main()
