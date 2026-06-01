"""QNG-GPU-030d: extended H decomposition including E_phi (DER-QNG-036 §2.4).

Hypothesis (post GPU-030c): the +75% H drift is caused by a MISSING E_phi term
in hamiltonian_v8.  The force F_A = BETA_PHI * wrap(pm_wmean - phi) in
force_phi_v8 derives (in the uniform-sm small-angle limit) from

    E_phi = -(β_DER/z) * Σ_{i,j~i} sm_i sm_j cos(phi_i - phi_j)

with β_DER = BETA_PHI / (2 * SIGMA_M_REF²) = 0.06 / (2·0.25) = 0.12.

If E_phi accounts for the drift, |dH/H| (including E_phi) should drop from
+0.75 toward zero.  Residual drift remains because F_A in the code is an
APPROXIMATION to -dE_phi/dphi valid only for uniform sm — in the ring core
sm is non-uniform, so the code force differs from the exact canonical force.

This is a diagnostic, not a physics change.  If it confirms the hypothesis,
next step is:
  (a) add E_phi to hamiltonian_v8, AND
  (b) derive DER-QNG-050 that either (i) corrects F_A to the exact canonical
      form F_A_canonical = -(2β_DER/z) * sm_k * |Z_sm_k| * sin(arg(Z_sm_k) - phi_k)
      or (ii) reformulates E_phi to match the simplified force (no known form).
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
    SIGMA_G_REF, SIGMA_M_REF,
    ALPHA, BETA_G, BETA_M, BETA_PHI, GAMMA_PHI, K_BACK, G_V_COUPLE,
    MU_M, MU_PHI,
    yoshida4_step,
    disorder_gpu,
)
from qng_v8_ring_cache import form_ring_cached


BETA_PHI_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)  # 0.12


def E_phi_DER036(sm, phi, nb_idx):
    """E_phi = -(β_DER/z) * Σ_{i,j∈N(i)} sm_i sm_j cos(phi_i - phi_j)."""
    z = float(nb_idx.shape[1])
    sm_nb  = sm[nb_idx]
    phi_nb = phi[nb_idx]
    # Σ over all (i, j∈N(i)) pairs; each edge counted twice
    cos_dphi = cp.cos(phi[:, None] - phi_nb)
    return -(BETA_PHI_DER / z) * float(cp.sum(sm[:, None] * sm_nb * cos_dphi))


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

    E_phi = E_phi_DER036(sm, phi, nb_idx)

    return {
        'T_g': T_g, 'T_m': T_m, 'T_phi': T_phi_kin,
        'E_A_g': E_A_g, 'E_A_m': E_A_m,
        'E_B_g': E_B_g, 'E_B_m': E_B_m,
        'V_cp': V_cp, 'E_F': E_F, 'E_phi': E_phi,
    }


def total_H_with_phi(s):
    return sum(s.values())


def H_old(s):
    """What the current hamiltonian_v8 computes (missing E_phi)."""
    return (s['T_g'] + s['T_m'] + s['T_phi']
            + s['E_A_g'] + s['E_A_m']
            + s['E_B_g'] + s['E_B_m']
            + s['V_cp'] + s['E_F'])


def main():
    print("=" * 80)
    print("QNG-GPU-030d: H decomposition WITH E_phi (DER-QNG-036 §2.4)")
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

    print(f"  L={L}, R={R}, BETA_PHI_code={BETA_PHI}  BETA_PHI_DER={BETA_PHI_DER}")

    DT = 0.01
    T_PHYS = 20.0
    N_STEPS = int(round(T_PHYS / DT))
    LOG_LU = 2.0
    STRIDE = int(round(LOG_LU / DT))

    s0 = h_sectors(state, nb_idx)
    H_old_0 = H_old(s0)
    H_new_0 = total_H_with_phi(s0)

    print()
    print(f"  H_old_0 (no E_phi) = {H_old_0:.4f}")
    print(f"  E_phi_0            = {s0['E_phi']:.4f}")
    print(f"  H_new_0 (w/ E_phi) = {H_new_0:.4f}")
    print()
    print(f"  {'t':>5s}  {'T_m':>7s} {'T_phi':>7s} {'E_B_m':>7s} {'V_cp':>7s} "
          f"{'E_F':>7s} {'E_phi':>9s}   {'H_old':>9s}  {'H_new':>9s}   "
          f"{'dH_old/H0':>10s}  {'dH_new/H0':>10s}")

    log = [{'t': 0.0, **s0, 'H_old': H_old_0, 'H_new': H_new_0}]
    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT, nb_idx,
            k_gm=0.0, damping_gamma=0.0, chi_decay=0.0,
            v_couple_on=True, channel_f=True,
        )
        if step % STRIDE == 0:
            t_phys = step * DT
            s = h_sectors(state, nb_idx)
            Ho = H_old(s)
            Hn = total_H_with_phi(s)
            dHo = (Ho - H_old_0) / abs(H_old_0) if abs(H_old_0) > 1e-10 else 0.0
            dHn = (Hn - H_new_0) / abs(H_new_0) if abs(H_new_0) > 1e-10 else 0.0
            log.append({'t': t_phys, **s, 'H_old': Ho, 'H_new': Hn})
            print(f"  {t_phys:5.1f}  {s['T_m']:+7.3f} {s['T_phi']:+7.3f} "
                  f"{s['E_B_m']:+7.3f} {s['V_cp']:+7.3f} {s['E_F']:+7.3f} "
                  f"{s['E_phi']:+9.3f}   {Ho:+9.3f}  {Hn:+9.3f}   "
                  f"{dHo:+10.2e}  {dHn:+10.2e}", flush=True)

    wall = time.time() - t0
    print(f"\n  wall = {wall:.1f}s")

    # ---- Verdict ----
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    last = log[-1]
    dHo_final = (last['H_old'] - H_old_0) / abs(H_old_0)
    dHn_final = (last['H_new'] - H_new_0) / abs(H_new_0)
    print(f"  final t={last['t']:.1f}:")
    print(f"    dH_old/H_0  = {dHo_final:+.3e}  (monitor missing E_phi)")
    print(f"    dH_new/H_0  = {dHn_final:+.3e}  (monitor WITH E_phi)")

    absorption = (abs(dHo_final) - abs(dHn_final)) / max(abs(dHo_final), 1e-12)
    print(f"    drift absorbed by E_phi: {absorption*100:.1f}%")

    if abs(dHn_final) < 0.01:
        diag = ("E_phi is the ENTIRE missing term. GPU-030 G1 FAIL was a monitor bug. "
                "hamiltonian_v8 must be patched to include E_phi.")
    elif absorption > 0.5:
        diag = ("E_phi absorbs most of the drift (>50%). Adding it to hamiltonian_v8 "
                "will greatly improve G1, but a residual remains from F_A being an "
                "APPROXIMATION to -dE_phi/dphi in non-uniform sm. Requires DER-QNG-050 "
                "(exact canonical F_A).")
    elif absorption > 0:
        diag = ("E_phi absorbs some drift. More sectors are non-canonical. Inspect each.")
    else:
        diag = ("E_phi does NOT absorb the drift — hypothesis falsified; look elsewhere.")
    print(f"\n  Diagnosis: {diag}")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-h-sector-decomp-v2"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'DT': DT, 'T_PHYS': T_PHYS,
            'BETA_PHI_code': BETA_PHI, 'BETA_PHI_DER': BETA_PHI_DER,
            'H_old_0': H_old_0, 'H_new_0': H_new_0,
            'dH_old_final': dHo_final, 'dH_new_final': dHn_final,
            'absorption_fraction': absorption,
            'diagnosis': diag,
            'log': log,
        }, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
