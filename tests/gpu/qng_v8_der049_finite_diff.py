"""QNG-GPU-030b: finite-difference check of DER-QNG-049 and E_B proxy.

Purpose: before interpreting GPU-030's FAIL, verify the two candidate sources:
  (A) DER-QNG-049 F_phi_F derivation bug.
  (B) E_B Hamiltonian-proxy mismatch (using (sigma - sigma_bar)^2 instead of
      (sigma_i - sigma_j)^2 edge sum).

Tests run on a small lattice (L=8) with the cached-ring-style state:
  sigma_m dip in ring curve + phi 2pi winding.

A. F_phi_F analytic gradient vs central finite differences of E_F.
B. E_B_proxy value  vs  true edge-sum value on the same state.
C. E_B force   -dE_B_proxy/dsigma  vs  -dE_B_true/dsigma finite diff.

All checks should agree to <0.1% if analytics are right.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    SIGMA_G_REF, SIGMA_M_REF,
    GAMMA_PHI, BETA_M,
    build_nb, centered_coords,
    disorder_gpu, nb_mean,
)


def E_F_scalar(sm_gpu, phi_gpu, nb_idx):
    """E_F = (GAMMA_PHI/2) * sum_i disorder_i * sigma_m_i^2  (no clipping)."""
    dis = disorder_gpu(phi_gpu, nb_idx)
    return 0.5 * GAMMA_PHI * float(cp.sum(dis * sm_gpu * sm_gpu))


def F_phi_F_analytic(sm_gpu, phi_gpu, nb_idx):
    """F_F_j = +(GAMMA_PHI/(2z)) * sum_{i in N(j)} sin(theta_i - phi_j) * sm_i^2.

    theta_i = arg(Z_i) with unweighted mean.
    """
    pnb = phi_gpu[nb_idx]
    cos_mean = cp.cos(pnb).mean(axis=1)
    sin_mean = cp.sin(pnb).mean(axis=1)
    theta_i = cp.arctan2(sin_mean, cos_mean)
    z_coord = float(nb_idx.shape[1])
    theta_nb = theta_i[nb_idx]
    sm_nb_sq = sm_gpu[nb_idx] ** 2
    return (GAMMA_PHI / (2.0 * z_coord)) * (
        cp.sin(theta_nb - phi_gpu[:, None]) * sm_nb_sq
    ).sum(axis=1)


def E_B_proxy(sigma_gpu, nb_idx, beta):
    """Current code form: (beta/2)*3*sum (sigma - sigma_bar)^2."""
    sbar = nb_mean(sigma_gpu, nb_idx)
    return (beta / 2.0) * 3.0 * float(cp.sum((sigma_gpu - sbar) ** 2))


def E_B_true(sigma_gpu, nb_idx, beta):
    """Correct form: (beta/(4z)) * sum_i sum_{j in N(i)} (sigma_i - sigma_j)^2.

    Standard discrete gradient energy. Gives exact gradient:
      -dE_B/dsigma_i = beta * (sigma_bar_i - sigma_i).
    """
    z_coord = float(nb_idx.shape[1])
    snb = sigma_gpu[nb_idx]
    diff = sigma_gpu[:, None] - snb
    return (beta / (4.0 * z_coord)) * float(cp.sum(diff * diff))


def build_state(L, R, dip_amp=0.25, core_rho=1.2):
    N = L ** 3
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


def check_F_phi_F(L=8, R=3, eps=1e-5, n_sample=20):
    print("=" * 80)
    print("A. Finite-diff check of F_phi_F (DER-QNG-049)")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm, phi = build_state(L, R)
    print(f"  L={L}, R={R}, N={L**3}")

    F_ana = F_phi_F_analytic(sm, phi, nb_idx)
    E0 = E_F_scalar(sm, phi, nb_idx)
    print(f"  E_F baseline = {E0:.6f}")

    rng = np.random.default_rng(42)
    j_samples = rng.choice(L ** 3, size=n_sample, replace=False)

    max_abs_err = 0.0
    max_rel_err = 0.0
    err_records = []
    for j in j_samples:
        phi_p = phi.copy(); phi_p[j] += eps
        phi_m = phi.copy(); phi_m[j] -= eps
        E_plus  = E_F_scalar(sm, phi_p, nb_idx)
        E_minus = E_F_scalar(sm, phi_m, nb_idx)
        dEdphi_fd = (E_plus - E_minus) / (2.0 * eps)
        F_fd = -dEdphi_fd  # F_phi_F_j = -dE/dphi_j

        F_ana_j = float(F_ana[int(j)])
        abs_err = abs(F_ana_j - F_fd)
        rel_err = abs_err / max(abs(F_fd), 1e-10)
        err_records.append((int(j), F_ana_j, F_fd, abs_err, rel_err))
        max_abs_err = max(max_abs_err, abs_err)
        max_rel_err = max(max_rel_err, rel_err)

    err_records.sort(key=lambda x: -x[4])  # worst first
    print(f"  Sampled {n_sample} nodes, eps={eps}")
    print(f"  max |F_ana - F_fd|          = {max_abs_err:.3e}")
    print(f"  max relative error          = {max_rel_err:.3e}")
    print(f"  Worst 5 samples:")
    for j, f_a, f_fd, a, r in err_records[:5]:
        print(f"    j={j:6d}  F_ana={f_a:+.4e}  F_fd={f_fd:+.4e}  rel_err={r:.2e}")

    verdict = "PASS" if max_rel_err < 0.01 else "FAIL"
    print(f"  VERDICT: {verdict} (gate <1% relative error)")
    return verdict, max_rel_err


def check_E_B(L=8, R=3, beta=BETA_M):
    print("\n" + "=" * 80)
    print("B. E_B proxy vs true gradient energy")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm, phi = build_state(L, R)

    E_proxy = E_B_proxy(sm, nb_idx, beta)
    E_true = E_B_true(sm, nb_idx, beta)
    print(f"  E_B_proxy (code)             = {E_proxy:.6f}")
    print(f"  E_B_true  (edge-sum form)    = {E_true:.6f}")
    print(f"  ratio proxy/true             = {E_proxy/max(E_true, 1e-12):.4f}")
    print(f"  absolute diff                = {E_proxy - E_true:+.6f}")


def check_E_B_gradient(L=8, R=3, beta=BETA_M, eps=1e-5, n_sample=20):
    """Finite-diff check of force against TRUE E_B. Force is beta*(sbar-sigma).

    If -dE_B_true/dsigma = beta*(sbar - sigma) exactly, code force is canonical
    w.r.t. E_B_true. The E_B_proxy is NOT the true Hamiltonian.
    """
    print("\n" + "=" * 80)
    print("C. Code force vs -dE_B_true/dsigma (finite difference)")
    print("=" * 80)
    nb_idx = build_nb(L)
    sm, phi = build_state(L, R)

    sbar = nb_mean(sm, nb_idx)
    F_code = beta * (sbar - sm)

    rng = np.random.default_rng(17)
    idxs = rng.choice(L ** 3, size=n_sample, replace=False)

    max_rel_true = 0.0
    max_rel_proxy = 0.0
    for j in idxs:
        sm_p = sm.copy(); sm_p[j] += eps
        sm_m = sm.copy(); sm_m[j] -= eps

        E_tp = E_B_true(sm_p, nb_idx, beta)
        E_tm = E_B_true(sm_m, nb_idx, beta)
        F_true_j = -(E_tp - E_tm) / (2.0 * eps)

        E_pp = E_B_proxy(sm_p, nb_idx, beta)
        E_pm = E_B_proxy(sm_m, nb_idx, beta)
        F_proxy_j = -(E_pp - E_pm) / (2.0 * eps)

        F_code_j = float(F_code[int(j)])

        rel_true = abs(F_code_j - F_true_j) / max(abs(F_true_j), 1e-10)
        rel_proxy = abs(F_code_j - F_proxy_j) / max(abs(F_proxy_j), 1e-10)
        max_rel_true = max(max_rel_true, rel_true)
        max_rel_proxy = max(max_rel_proxy, rel_proxy)

    print(f"  max rel err  F_code vs -dE_true/dsigma   = {max_rel_true:.3e}")
    print(f"  max rel err  F_code vs -dE_proxy/dsigma  = {max_rel_proxy:.3e}")
    if max_rel_true < 0.01 and max_rel_proxy > 0.1:
        verdict = "CONFIRMED: code force matches E_B_true, NOT E_B_proxy"
    elif max_rel_true < 0.01 and max_rel_proxy < 0.01:
        verdict = "BOTH match — E_B_proxy happens to agree on this state"
    else:
        verdict = f"UNEXPECTED — investigate further (true_err={max_rel_true:.2e}, proxy_err={max_rel_proxy:.2e})"
    print(f"  VERDICT: {verdict}")


def main():
    v1, err1 = check_F_phi_F()
    check_E_B()
    check_E_B_gradient()
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  A. F_phi_F derivation {v1} (max rel err = {err1:.2e})")
    print(f"  B. E_B proxy: shown above")
    print(f"  C. Force vs true E_B gradient: shown above")


if __name__ == "__main__":
    main()
