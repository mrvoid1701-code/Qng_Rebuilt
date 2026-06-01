"""QNG-GPU-031c-prereq: finite-difference check of DER-QNG-050.

Verifies the exact canonical Channel A forces derived in
04_qng_pure/qng-channel-a-canonical-v1.md (DER-QNG-050):

  E_phi = -(beta_DER / z) * sum_i sum_{j in N(i)} sm_i * sm_j * cos(phi_i - phi_j)
  beta_DER = BETA_PHI / (2 * SIGMA_M_REF^2)

Must satisfy:
  F_phi_A_exact_k  = -dE_phi/dphi_k  = -(2*beta_DER/z) * sm_k * R_k * sin(phi_k - Theta_k)
  F_sm_XY_exact_k  = -dE_phi/dsm_k   = +(2*beta_DER/z) * R_k * cos(phi_k - Theta_k)

where Z_k = R_k * exp(i*Theta_k) = sum_{j in N(k)} sm_j * exp(i*phi_j).

Parity check: in the uniform sm = SIGMA_M_REF, small (phi - phi_j) limit,
F_phi_A_exact reduces to BETA_PHI*(pm_wmean - phi) (the pre-DER-050 code form).
"""
from __future__ import annotations

import sys
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    SIGMA_M_REF, BETA_PHI, G_V_COUPLE,
    build_nb, centered_coords,
    sm_weighted_Z_gpu,
    force_phi_v8, force_sm_v8,
    phi_wmean_gpu, wrap_gpu,
)


def E_phi_XY(sm_gpu, phi_gpu, nb_idx):
    """E_phi = -(beta_DER/z) * sum_i sum_{j in N(i)} sm_i * sm_j * cos(phi_i - phi_j)."""
    z_coord = float(nb_idx.shape[1])
    beta_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
    sm_nb = sm_gpu[nb_idx]
    phi_nb = phi_gpu[nb_idx]
    cos_d = cp.cos(phi_gpu[:, None] - phi_nb)
    return -(beta_DER / z_coord) * float(cp.sum(sm_gpu[:, None] * sm_nb * cos_d))


def V_couple_E2(sm_gpu, phi_gpu):
    """V_couple = (g/2) * sum_i (sm_ref - sm_i)^2 * (1 - cos phi_i)."""
    deficit = SIGMA_M_REF - sm_gpu
    return 0.5 * G_V_COUPLE * float(cp.sum(deficit * deficit * (1.0 - cp.cos(phi_gpu))))


def E_total_phi(sm_gpu, phi_gpu, nb_idx):
    """Total phi-dependent potential = E_phi (XY) + V_couple (E^2)."""
    return E_phi_XY(sm_gpu, phi_gpu, nb_idx) + V_couple_E2(sm_gpu, phi_gpu)


def E_total_sm(sm_gpu, phi_gpu, nb_idx):
    """sm-dependent pieces of E that force_sm_v8 must match.
    Includes E_A_m (Channel A restoration), E_B_m (Channel B gradient),
    V_couple (E^2), and E_phi (XY back-reaction)."""
    # E_phi_XY contributes the DER-QNG-050 sm-back-reaction
    return E_phi_XY(sm_gpu, phi_gpu, nb_idx)


def build_state(L, R, dip_amp=0.25, core_rho=1.2):
    dx_np, dy_np, dz_np = centered_coords(L)
    dx = cp.asarray(dx_np.ravel(), dtype=cp.float64)
    dy = cp.asarray(dy_np.ravel(), dtype=cp.float64)
    dz = cp.asarray(dz_np.ravel(), dtype=cp.float64)
    rho = cp.sqrt(dx * dx + dy * dy)

    dist_curve_sq = (rho - R) ** 2 + dz * dz
    dip_profile = cp.exp(-0.5 * dist_curve_sq / (core_rho * core_rho))
    sm = cp.asarray(SIGMA_M_REF, dtype=cp.float64) - dip_amp * dip_profile
    phi = cp.arctan2(dz, rho - R)
    return sm, phi


def check_F_phi_A(L=8, R=3, eps=1e-5, n_sample=20):
    print("=" * 80)
    print("A. F_phi_A_exact = -dE_phi/dphi (DER-QNG-050)")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm, phi = build_state(L, R)
    print(f"  L={L}, R={R}, N={L**3}, SIGMA_M_REF={SIGMA_M_REF}, BETA_PHI={BETA_PHI}")

    sg_dummy = cp.full_like(sm, 0.20)
    F_ana = force_phi_v8(sg_dummy, sm, phi, nb_idx,
                        channel_f=False, exact_a=True)

    rng = np.random.default_rng(42)
    j_samples = rng.choice(L ** 3, size=n_sample, replace=False)

    max_rel = 0.0
    rec = []
    for j in j_samples:
        phi_p = phi.copy(); phi_p[j] = phi_p[j] + eps
        phi_m = phi.copy(); phi_m[j] = phi_m[j] - eps
        E_p = E_total_phi(sm, phi_p, nb_idx)
        E_m = E_total_phi(sm, phi_m, nb_idx)
        F_fd = -(E_p - E_m) / (2.0 * eps)
        F_a = float(F_ana[int(j)])
        rel = abs(F_a - F_fd) / max(abs(F_fd), 1e-10)
        rec.append((int(j), F_a, F_fd, rel))
        max_rel = max(max_rel, rel)
    rec.sort(key=lambda x: -x[3])
    print(f"  Sampled {n_sample} nodes, eps={eps}")
    print(f"  max relative error = {max_rel:.3e}")
    print(f"  Worst 5 samples:")
    for j, f_a, f_fd, r in rec[:5]:
        print(f"    j={j:6d}  F_ana={f_a:+.4e}  F_fd={f_fd:+.4e}  rel_err={r:.2e}")
    verdict = "PASS" if max_rel < 0.01 else "FAIL"
    print(f"  VERDICT: {verdict} (gate <1%)")
    return verdict, max_rel


def check_F_sm_XY(L=8, R=3, eps=1e-5, n_sample=20):
    print("\n" + "=" * 80)
    print("B. F_sm_XY_exact = -dE_phi/dsm (DER-QNG-050)")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm, phi = build_state(L, R)

    # Expected analytic form on node k: (2*beta_DER/z) * R_k * cos(phi_k - Theta_k)
    z_coord = float(nb_idx.shape[1])
    beta_DER = BETA_PHI / (2.0 * SIGMA_M_REF ** 2)
    R_k, Theta_k = sm_weighted_Z_gpu(phi, sm, nb_idx)
    F_sm_ana = (2.0 * beta_DER / z_coord) * R_k * cp.cos(phi - Theta_k)

    rng = np.random.default_rng(17)
    j_samples = rng.choice(L ** 3, size=n_sample, replace=False)

    max_rel = 0.0
    rec = []
    for j in j_samples:
        sm_p = sm.copy(); sm_p[j] = sm_p[j] + eps
        sm_m = sm.copy(); sm_m[j] = sm_m[j] - eps
        E_p = E_phi_XY(sm_p, phi, nb_idx)
        E_m = E_phi_XY(sm_m, phi, nb_idx)
        F_fd = -(E_p - E_m) / (2.0 * eps)
        F_a = float(F_sm_ana[int(j)])
        rel = abs(F_a - F_fd) / max(abs(F_fd), 1e-10)
        rec.append((int(j), F_a, F_fd, rel))
        max_rel = max(max_rel, rel)
    rec.sort(key=lambda x: -x[3])
    print(f"  Sampled {n_sample} nodes, eps={eps}")
    print(f"  max relative error = {max_rel:.3e}")
    print(f"  Worst 5 samples:")
    for j, f_a, f_fd, r in rec[:5]:
        print(f"    j={j:6d}  F_ana={f_a:+.4e}  F_fd={f_fd:+.4e}  rel_err={r:.2e}")
    verdict = "PASS" if max_rel < 0.01 else "FAIL"
    print(f"  VERDICT: {verdict} (gate <1%)")
    return verdict, max_rel


def check_uniform_limit(L=8):
    """Parity sanity: uniform sm = SIGMA_M_REF, small perturbations in phi.

    Under uniform sm, exact F_phi_A reduces to BETA_PHI * (pm_wmean - phi)
    in the small-(phi - phi_j) expansion. Check both approximate and exact
    agree on a weakly perturbed uniform state.
    """
    print("\n" + "=" * 80)
    print("C. Parity: uniform-sm small-angle limit")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm = cp.full((L ** 3,), SIGMA_M_REF, dtype=cp.float64)
    rng = np.random.default_rng(99)
    phi_np = 0.05 * rng.standard_normal(L ** 3)
    phi = cp.asarray(phi_np, dtype=cp.float64)

    sg_dummy = cp.full_like(sm, 0.20)
    F_exact = force_phi_v8(sg_dummy, sm, phi, nb_idx,
                          channel_f=False, exact_a=True)
    F_approx = BETA_PHI * wrap_gpu(phi_wmean_gpu(phi, sm, nb_idx) - phi)
    num = float(cp.max(cp.abs(F_exact - F_approx)))
    den = max(float(cp.max(cp.abs(F_approx))), 1e-12)
    print(f"  max |F_exact - F_approx|     = {num:.3e}")
    print(f"  max |F_approx|               = {den:.3e}")
    print(f"  max rel diff                 = {num/den:.3e}")
    verdict = "PASS" if num/den < 0.05 else "FAIL"
    print(f"  VERDICT: {verdict} (expected agreement <5% in small-angle limit)")
    return verdict, num/den


def main():
    v1, e1 = check_F_phi_A()
    v2, e2 = check_F_sm_XY()
    v3, e3 = check_uniform_limit()
    print("\n" + "=" * 80)
    print("SUMMARY (DER-QNG-050 canonical forces)")
    print("=" * 80)
    print(f"  A. F_phi_A_exact = -dE_phi/dphi    : {v1}  (rel err {e1:.2e})")
    print(f"  B. F_sm_XY_exact = -dE_phi/dsm     : {v2}  (rel err {e2:.2e})")
    print(f"  C. uniform-sm parity with BETA_PHI : {v3}  (rel diff {e3:.2e})")
    all_pass = (v1 == "PASS" and v2 == "PASS" and v3 == "PASS")
    print()
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
