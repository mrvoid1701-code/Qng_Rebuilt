"""Finite-diff sanity check for DER-QNG-051 Option R1 force derivation.

Checks:
  A) F_A_R1 = -dE_phi_R1/dphi at a random non-uniform (sm, phi) state,
     with V_couple SET TO ZERO (g=0) so we isolate the XY force.
     E_phi_R1 = -(beta_R1/z) * sum_{i, j in N(i)} cos(phi_i - phi_j)
     with beta_R1 = BETA_PHI/2.
  B) dE_phi_R1/dsm = 0 everywhere (checked by verifying force_sm_v8
     with exact_a='r1' and g=0 matches force_sm_v8 with exact_a=False
     and g=0 to machine precision — no F_XY_sm term).

A and B together verify that Option R1 is a consistent canonical
Hamiltonian variant with sigma_m decoupled from E_phi.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

import qng_v8_canonical_gpu as qng
from qng_v8_canonical_gpu import (
    build_nb, make_state, BETA_PHI,
    force_phi_v8, force_sm_v8,
)


def E_phi_R1(phi, nb_idx):
    """E_phi_R1 = -(beta_R1/z) sum_{i, j~i} cos(phi_i - phi_j)."""
    z_coord = float(nb_idx.shape[1])
    beta_R1 = BETA_PHI / 2.0
    phi_nb = phi[nb_idx]
    cos_dphi = cp.cos(phi[:, None] - phi_nb)
    return -(beta_R1 / z_coord) * float(cp.sum(cos_dphi))


def finite_diff_dE_dphi(phi0, nb_idx, idx, eps=1e-4):
    phi_p = phi0.copy(); phi_p[idx] += eps
    phi_m = phi0.copy(); phi_m[idx] -= eps
    return (E_phi_R1(phi_p, nb_idx) - E_phi_R1(phi_m, nb_idx)) / (2.0 * eps)


def main():
    print("=" * 72)
    print("DER-QNG-051 Option R1 finite-diff verification")
    print("=" * 72)

    # Disable V_couple so we isolate F_A
    g_save = qng.G_V_COUPLE
    qng.G_V_COUPLE = 0.0
    try:
        L = 12
        nb_idx = build_nb(L)
        np.random.seed(7)
        phi0 = cp.asarray(np.random.uniform(-np.pi, np.pi, size=L**3).astype(np.float64))
        sm0 = cp.asarray(np.random.uniform(0.2, 0.8, size=L**3).astype(np.float64))
        sg0 = cp.full(L**3, 0.20, dtype=cp.float64)

        # ---- Check A: F_A_R1 == -dE_phi_R1/dphi ----
        print("\n[A] F_phi_R1 vs -dE_phi_R1/dphi (channel_f=False, g=0)")
        F_phi_code = force_phi_v8(sg0, sm0, phi0, nb_idx,
                                  channel_f=False, exact_a='r1')
        rng = np.random.default_rng(7)
        test_indices = rng.choice(L**3, size=25, replace=False)
        max_err = 0.0
        worst_at = -1
        for idx in test_indices:
            dE_num = finite_diff_dE_dphi(phi0, nb_idx, int(idx))
            F_num  = -dE_num
            F_code = float(F_phi_code[int(idx)])
            err = abs(F_code - F_num)
            rel = err / max(abs(F_num), 1e-8)
            if err > max_err:
                max_err = err; worst_at = int(idx)
        # Final relative
        if abs(F_num) > 0:
            rel_max = max_err / max(abs(F_num), 1e-8)
        else:
            rel_max = max_err
        print(f"  max abs error across 25 nodes: {max_err:.3e}")
        verdictA = "PASS" if max_err < 1e-5 else "FAIL"
        print(f"  Verdict A: {verdictA}")

        # ---- Check B: F_sm_R1 has no F_XY_sm contribution ----
        print("\n[B] force_sm_v8(exact_a='r1') == force_sm_v8(exact_a=False) "
              "(g=0, channel_f=False)")
        F_sm_r1   = force_sm_v8(sg0, sm0, phi0, nb_idx,
                                channel_f=False, exact_a='r1')
        F_sm_none = force_sm_v8(sg0, sm0, phi0, nb_idx,
                                channel_f=False, exact_a=False)
        diff = float(cp.max(cp.abs(F_sm_r1 - F_sm_none)))
        print(f"  max |F_sm_r1 - F_sm_none| = {diff:.3e}")
        verdictB = "PASS" if diff < 1e-12 else "FAIL"
        print(f"  Verdict B: {verdictB}")

        overall = "PASS" if (verdictA == "PASS" and verdictB == "PASS") else "FAIL"
        print("\n" + "=" * 72)
        print(f"OVERALL: {overall}")
        print("=" * 72)
    finally:
        qng.G_V_COUPLE = g_save


if __name__ == "__main__":
    main()
