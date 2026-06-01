"""QNG-GPU-030c: sector-decomposed Hamiltonian diagnostic.

Given GPU-030 shows max |dH/H| = 0.94 despite
  (A) DER-QNG-049 finite-diff verified (rel err 1.67e-8)
  (B) E_B Hamiltonian fixed to match true gradient form

we localize the drift source by decomposing H into:
  - T_g  = (K_BACK/2) * sum chi^2
  - T_m  = (1/(2*MU_M)) * sum pi_m^2
  - T_phi= (1/(2*MU_PHI)) * sum pi_phi^2
  - E_A_g= (ALPHA/2) * sum (sg - SIGMA_G_REF)^2
  - E_A_m= (ALPHA/2) * sum (sm - SIGMA_M_REF)^2
  - E_B_g= (BETA_G/(4z)) * sum_edges (sg_i - sg_j)^2
  - E_B_m= (BETA_M/(4z)) * sum_edges (sm_i - sm_j)^2
  - V_cp = (g/2) * sum (SIGMA_M_REF - sm)^2 * (1 - cos phi)
  - E_F  = (GAMMA_PHI/2) * sum disorder * sm^2

At k_gm=0 and Option E^2 V_couple:
  - (sm, pi_m, phi, pi_phi) sector is decoupled from (sg, chi)
  - V_couple depends only on (sm, phi), NOT sg -> (sg, chi) truly decoupled
  - => H_matter = T_m + T_phi + E_A_m + E_B_m + V_cp + E_F should be conserved
  - => H_grav   = T_g + E_A_g + E_B_g evolves via its own v7 subsystem

Run: cached L=28 R=4 ring, v8 Yoshida4, T=20 lu, DT=0.01.
Log each sector every 1 lu.
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
    SIGMA_G_REF, SIGMA_M_REF,
    ALPHA, BETA_G, BETA_M, GAMMA_PHI, K_BACK, G_V_COUPLE,
    MU_M, MU_PHI,
    yoshida4_step,
    disorder_gpu,
)
from qng_v8_ring_cache import form_ring_cached


def h_sectors(state, nb_idx):
    sg, sm, chi, phi = state['sg'], state['sm'], state['chi'], state['phi']
    pi_m, pi_phi = state['pi_m'], state['pi_phi']
    z = float(nb_idx.shape[1])

    T_g = (K_BACK / 2.0) * float(cp.sum(chi * chi))
    T_m = (1.0 / (2.0 * MU_M)) * float(cp.sum(pi_m * pi_m))
    T_phi_kin = (1.0 / (2.0 * MU_PHI)) * float(cp.sum(pi_phi * pi_phi))

    E_A_g = (ALPHA / 2.0) * float(cp.sum((sg - SIGMA_G_REF) ** 2))
    E_A_m = (ALPHA / 2.0) * float(cp.sum((sm - SIGMA_M_REF) ** 2))

    dsg = sg[:, None] - sg[nb_idx]
    dsm = sm[:, None] - sm[nb_idx]
    E_B_g = (BETA_G / (4.0 * z)) * float(cp.sum(dsg * dsg))
    E_B_m = (BETA_M / (4.0 * z)) * float(cp.sum(dsm * dsm))

    deficit = SIGMA_M_REF - sm
    V_cp = 0.5 * G_V_COUPLE * float(cp.sum((deficit * deficit) * (1.0 - cp.cos(phi))))

    dis = disorder_gpu(phi, nb_idx)
    E_F = 0.5 * GAMMA_PHI * float(cp.sum(dis * sm * sm))

    return {
        'T_g': T_g, 'T_m': T_m, 'T_phi': T_phi_kin,
        'E_A_g': E_A_g, 'E_A_m': E_A_m,
        'E_B_g': E_B_g, 'E_B_m': E_B_m,
        'V_cp': V_cp, 'E_F': E_F,
    }


def total_H(s):
    return sum(s.values())


def H_matter(s):
    """Canonical sector at k_gm=0 & Option E^2."""
    return s['T_m'] + s['T_phi'] + s['E_A_m'] + s['E_B_m'] + s['V_cp'] + s['E_F']


def H_grav(s):
    """v7 (sigma_g, chi) sector (mixed gradient-flow + momentum in code)."""
    return s['T_g'] + s['E_A_g'] + s['E_B_g']


def main():
    print("=" * 80)
    print("QNG-GPU-030c: H sector decomposition on cached ring (v8 + canonical F)")
    print("=" * 80)

    L = 28
    R = 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=False)
    N = L ** 3
    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    ring_state['chi'].copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }

    print(f"  L={L}, R={R}, N={N}")
    print(f"  Initial state diagnostics:")
    print(f"    sg    min/max/mean = {float(cp.min(state['sg'])):.4f}/"
          f"{float(cp.max(state['sg'])):.4f}/{float(cp.mean(state['sg'])):.4f}")
    print(f"    sm    min/max/mean = {float(cp.min(state['sm'])):.4f}/"
          f"{float(cp.max(state['sm'])):.4f}/{float(cp.mean(state['sm'])):.4f}")
    print(f"    chi   min/max/mean = {float(cp.min(state['chi'])):+.4e}/"
          f"{float(cp.max(state['chi'])):+.4e}/{float(cp.mean(state['chi'])):+.4e}")
    print(f"    phi   std          = {float(cp.std(state['phi'])):.4f}")

    DT = 0.01
    T_PHYS = 20.0
    N_STEPS = int(round(T_PHYS / DT))
    LOG_LU = 2.0
    STRIDE = int(round(LOG_LU / DT))

    V_COUPLE_ON = True
    CHANNEL_F = True
    K_GM = 0.0
    CHI_DECAY = 0.0
    DAMPING = 0.0

    s0 = h_sectors(state, nb_idx)
    H0 = total_H(s0)
    Hm0 = H_matter(s0)
    Hg0 = H_grav(s0)

    print()
    print(f"  H_total_0  = {H0:.6f}")
    print(f"  H_matter_0 = {Hm0:.6f}  (T_m + T_phi + E_A_m + E_B_m + V_cp + E_F)")
    print(f"  H_grav_0   = {Hg0:.6f}  (T_g + E_A_g + E_B_g)")
    print()
    print(f"  Initial breakdown:")
    for k, v in s0.items():
        print(f"    {k:6s} = {v:+12.6f}")
    print()

    print(f"  {'t':>5s}  {'T_g':>9s} {'T_m':>9s} {'T_phi':>9s} "
          f"{'E_A_m':>9s} {'E_B_m':>9s} {'V_cp':>9s} {'E_F':>9s}  "
          f"{'H_tot':>10s}  {'H_mat':>10s}  {'H_grv':>8s}  "
          f"{'dH_m/H_m':>10s}  {'dH_g/H_g':>10s}")

    log = [{'t': 0.0, **s0, 'H_tot': H0, 'H_mat': Hm0, 'H_grv': Hg0}]
    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=K_GM, damping_gamma=DAMPING, chi_decay=CHI_DECAY,
            v_couple_on=V_COUPLE_ON, channel_f=CHANNEL_F,
        )
        if step % STRIDE == 0:
            t_phys = step * DT
            s = h_sectors(state, nb_idx)
            Ht = total_H(s)
            Hm = H_matter(s)
            Hg = H_grav(s)
            dHm = (Hm - Hm0) / abs(Hm0) if abs(Hm0) > 1e-10 else 0.0
            dHg = (Hg - Hg0) / abs(Hg0) if abs(Hg0) > 1e-10 else 0.0
            log.append({'t': t_phys, **s, 'H_tot': Ht, 'H_mat': Hm, 'H_grv': Hg})
            print(f"  {t_phys:5.1f}  {s['T_g']:+9.4f} {s['T_m']:+9.4f} {s['T_phi']:+9.4f} "
                  f"{s['E_A_m']:+9.4f} {s['E_B_m']:+9.4f} {s['V_cp']:+9.4f} {s['E_F']:+9.4f}  "
                  f"{Ht:+10.4f}  {Hm:+10.4f}  {Hg:+8.4f}  "
                  f"{dHm:+10.2e}  {dHg:+10.2e}", flush=True)

    wall = time.time() - t0
    print(f"\n  wall = {wall:.1f}s")

    # ---- Verdict ----
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    last = log[-1]
    dHm_final = (last['H_mat'] - Hm0) / abs(Hm0) if abs(Hm0) > 1e-10 else 0.0
    dHg_final = (last['H_grv'] - Hg0) / abs(Hg0) if abs(Hg0) > 1e-10 else 0.0
    dHt_final = (last['H_tot'] - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0

    print(f"  Final at t={last['t']:.1f} lu:")
    print(f"    dH_tot/H_tot    = {dHt_final:+.3e}")
    print(f"    dH_matter/H_m0  = {dHm_final:+.3e}  (canonical sector)")
    print(f"    dH_grav/H_g0    = {dHg_final:+.3e}  (v7 gradient-flow sector)")

    if abs(dHm_final) < 0.01:
        diag = ("H_matter conserved (<1%): (sm, pi_m, phi, pi_phi) canonical sector OK. "
                "Drift source is (sg, chi) sector => expected, v7 sector is not canonical "
                "in code. G1 gate on total H is mis-specified.")
    elif abs(dHm_final) < 0.1:
        diag = ("H_matter drifts 1-10%: small but non-trivial. Likely integrator dt or "
                "clipping artifact. Check sm near bounds [0,1].")
    else:
        diag = ("H_matter drifts >10%: DER-QNG-049 or E_B monitor still has a bug, OR "
                "clipping of sm in drift step is dominant dissipation, OR force form "
                "inconsistent with H form. Need finer investigation.")

    print(f"\n  Diagnosis: {diag}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-h-sector-decomp-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'DT': DT, 'T_PHYS': T_PHYS,
            'channel_f': CHANNEL_F, 'v_couple_on': V_COUPLE_ON,
            'k_gm': K_GM, 'chi_decay': CHI_DECAY, 'damping': DAMPING,
            'H_total_0': H0, 'H_matter_0': Hm0, 'H_grav_0': Hg0,
            'dH_total_final': dHt_final,
            'dH_matter_final': dHm_final,
            'dH_grav_final': dHg_final,
            'diagnosis': diag,
            'log': log,
        }, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
