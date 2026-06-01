"""QNG-CPU-082 — eta fluctuation invariant (program alpha probe).

After GPU-038 showed the orbital attractor is a GLOBAL MODE (R_eff = L/2)
rather than a localized particle, the quantization question shifts from
"particle has ℏ-spin" to "do the field modes admit an emergent Planck
constant?"

This CPU-only test implements program alpha from
`04_qng_pure/qng-quantization-program-v1.md` (NOTE-QNG-016):

    If the classical v8 substrate has a universal fluctuation product
      Q = <(Δπ_m)²><(Δσ_m)²>
    that is independent of initial perturbation amplitude and ring
    configuration, then Q is a candidate for η² — the substrate action
    quantum that plays the role of ℏ.

Protocol (minimal 1D reduction of v8 sigma_m + pi_m sector):
  Lattice: L=100 nodes (1D chain, periodic).
  Background: uniform sigma_m = SIGMA_M_REF = 0.5 (no ring).
  Perturb: sigma_m += eps · randn(L), pi_m += eps · randn(L).
  Evolve: Yoshida4 on (sigma_m, pi_m) with KG-like dynamics:
      dot(sigma_m) = pi_m / mu_m
      dot(pi_m)    = beta_m · Laplacian(sigma_m)  - k_eff · (sigma_m - SIGMA_M_REF)
  Sample every 5 lu, compute spatial var(sigma_m) and var(pi_m).
  Report time-averaged product <Var(sigma_m)>_t · <Var(pi_m)>_t.

Test three amplitudes eps ∈ {0.005, 0.010, 0.020}:
  - If Q scales as eps^0 (constant)  → substrate has zero-point fluctuations
                                         → program alpha is VIABLE
  - If Q scales as eps^4             → trivial classical linearity
                                         → program alpha is DEAD (no universal scale)
  - If Q scales as eps^2             → linear response floor → intermediate

Success criterion:
  - For eps^0 scaling: ratio Q(eps=0.020)/Q(eps=0.005) ∈ [0.3, 3.0]
  - For eps^2 scaling: ratio ~ 16
  - For eps^4 scaling: ratio ~ 256
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-eta-fluctuation-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# v8 parameters (matched to tests/gpu/qng_v8_canonical_gpu.py)
SIGMA_M_REF = 0.5
BETA_M = 0.40
MU_M = 10.0
K_EFF = 0.04  # soft restoring term; emergent from V_couple at small deficit

L = 100        # 1D lattice size
DT = 0.025
T_RUN = 200.0  # lu (fast CPU run)
T_BURN = 50.0  # burn-in
SAMPLE_EVERY_LU = 5.0


def laplacian_1d(f):
    """Periodic 1D Laplacian (5-point stencil would be overkill; 3-point)."""
    return np.roll(f, 1) + np.roll(f, -1) - 2.0 * f


def acceleration(sm, pi_m):
    """Return d(pi_m)/dt given current (sm, pi_m).

    EOM mimics the sigma_m sector of v8 in 1D:
      H = pi_m²/(2μ) + (β/2)·(∇σ)² + (k/2)·(σ-σ_ref)²
    """
    lap = laplacian_1d(sm)
    return BETA_M * lap - K_EFF * (sm - SIGMA_M_REF)


def yoshida4_step(sm, pi_m, dt):
    """4th-order symplectic step on (sigma_m, pi_m)."""
    w1 = 1.0 / (2.0 - 2.0 ** (1.0 / 3.0))
    w0 = 1.0 - 2.0 * w1
    weights = [w1, w0, w1]

    for w in weights:
        # kick half
        pi_m = pi_m + 0.5 * w * dt * acceleration(sm, pi_m)
        # drift full
        sm = sm + w * dt * pi_m / MU_M
        # kick half
        pi_m = pi_m + 0.5 * w * dt * acceleration(sm, pi_m)

    return sm, pi_m


def hamiltonian(sm, pi_m):
    kin = 0.5 * np.sum(pi_m * pi_m) / MU_M
    grad = np.roll(sm, -1) - sm
    pot_grad = 0.5 * BETA_M * np.sum(grad * grad)
    pot_res = 0.5 * K_EFF * np.sum((sm - SIGMA_M_REF) ** 2)
    return kin + pot_grad + pot_res


def run_one(eps, seed):
    """Run one configuration, return stats."""
    rng = np.random.default_rng(seed)
    sm = SIGMA_M_REF + eps * rng.standard_normal(L)
    pi_m = eps * rng.standard_normal(L)

    H0 = hamiltonian(sm, pi_m)

    n_steps = int(T_RUN / DT)
    sample_every = max(1, int(SAMPLE_EVERY_LU / DT))

    times = []
    var_sm = []
    var_pi = []
    H_arr = []

    for s in range(n_steps):
        sm, pi_m = yoshida4_step(sm, pi_m, DT)
        if s % sample_every == 0:
            t = s * DT
            times.append(t)
            # spatial variance about current mean (captures perturbation only)
            sm_dev = sm - np.mean(sm)
            pi_dev = pi_m - np.mean(pi_m)
            var_sm.append(float(np.var(sm_dev)))
            var_pi.append(float(np.var(pi_dev)))
            H_arr.append(hamiltonian(sm, pi_m))

    t_arr = np.array(times)
    warm = t_arr > T_BURN
    var_sm = np.array(var_sm)
    var_pi = np.array(var_pi)
    H_arr = np.array(H_arr)

    H_drift = abs(H_arr[-1] - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0

    return {
        'eps': eps,
        'seed': seed,
        'var_sm_mean': float(var_sm[warm].mean()),
        'var_sm_std':  float(var_sm[warm].std()),
        'var_pi_mean': float(var_pi[warm].mean()),
        'var_pi_std':  float(var_pi[warm].std()),
        'product':     float(var_sm[warm].mean() * var_pi[warm].mean()),
        'H0': float(H0),
        'H_final': float(H_arr[-1]),
        'H_drift_frac': float(H_drift),
    }


def main():
    print("=" * 80)
    print("QNG-CPU-082: eta fluctuation invariant (program alpha probe)")
    print("=" * 80)
    print(f"  L={L} (1D periodic), DT={DT}, T_RUN={T_RUN} lu")
    print(f"  mu_m={MU_M}, beta_m={BETA_M}, k_eff={K_EFF}, sigma_ref={SIGMA_M_REF}")

    eps_values = [0.005, 0.010, 0.020]
    seeds = [7, 13, 31]
    results = []

    t_start = time.time()
    for eps in eps_values:
        for seed in seeds:
            r = run_one(eps, seed)
            results.append(r)
            print(f"  eps={eps:.3f} seed={seed}  "
                  f"<Var(sm)>={r['var_sm_mean']:.4e}  "
                  f"<Var(pi)>={r['var_pi_mean']:.4e}  "
                  f"product={r['product']:.4e}  "
                  f"H_drift={r['H_drift_frac']:.2e}")

    wall = time.time() - t_start
    print(f"\n  Total wall: {wall:.1f}s")

    # Aggregate per eps
    by_eps = {}
    for eps in eps_values:
        rs = [r for r in results if r['eps'] == eps]
        prods = np.array([r['product'] for r in rs])
        by_eps[eps] = {
            'mean_product':  float(prods.mean()),
            'std_product':   float(prods.std()),
            'n_runs':        len(rs),
        }

    print("\n" + "=" * 80)
    print("SUMMARY per eps (average over 3 seeds)")
    print("=" * 80)
    for eps, s in by_eps.items():
        print(f"  eps={eps:.3f}:  <product>={s['mean_product']:.4e}  "
              f"(std={s['std_product']:.4e})")

    # Scaling analysis
    p_low = by_eps[eps_values[0]]['mean_product']
    p_mid = by_eps[eps_values[1]]['mean_product']
    p_high = by_eps[eps_values[2]]['mean_product']

    ratio_mid_low = p_mid / max(p_low, 1e-30)
    ratio_high_low = p_high / max(p_low, 1e-30)

    # Predicted ratios for each scaling hypothesis
    eps_ratio_mid_low  = eps_values[1] / eps_values[0]   # 2.0
    eps_ratio_high_low = eps_values[2] / eps_values[0]   # 4.0

    scaling_exponent = np.log(ratio_high_low) / np.log(eps_ratio_high_low)

    print("\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)
    print(f"  P(eps=0.010) / P(eps=0.005) = {ratio_mid_low:.3f} "
          f"(eps^2 predicts 4.0, eps^4 predicts 16.0, eps^0 predicts ~1)")
    print(f"  P(eps=0.020) / P(eps=0.005) = {ratio_high_low:.3f} "
          f"(eps^2 predicts 16.0, eps^4 predicts 256.0, eps^0 predicts ~1)")
    print(f"  Empirical scaling exponent: P ~ eps^{scaling_exponent:.3f}")

    # Verdict
    if abs(scaling_exponent) < 0.3:
        verdict = "ETA_UNIVERSAL_CANDIDATE"
        comment = ("Product is ~eps-independent: substrate has a zero-point "
                   "fluctuation scale. Program alpha VIABLE.")
    elif 1.7 <= scaling_exponent <= 2.3:
        verdict = "ETA_LINEAR_RESPONSE"
        comment = ("Product scales as eps^2 — expected for linear response. "
                   "No universal substrate scale distinct from perturbation.")
    elif 3.7 <= scaling_exponent <= 4.3:
        verdict = "ETA_TRIVIAL"
        comment = ("Product scales as eps^4 — trivial product of two linear "
                   "responses. Program alpha DEAD in this reduction.")
    else:
        verdict = "ETA_AMBIGUOUS"
        comment = (f"Scaling exponent {scaling_exponent:.2f} — intermediate. "
                   "Requires wider amplitude range or 3D substrate test.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {comment}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'L': L, 'DT': DT, 'T_RUN': T_RUN, 'T_BURN': T_BURN,
            'sample_every_lu': SAMPLE_EVERY_LU,
            'sigma_m_ref': SIGMA_M_REF, 'beta_m': BETA_M,
            'mu_m': MU_M, 'k_eff': K_EFF,
            'eps_values': eps_values, 'seeds': seeds,
            'runs': results,
            'by_eps': {str(k): v for k, v in by_eps.items()},
            'scaling_exponent': float(scaling_exponent),
            'verdict': verdict,
            'comment': comment,
            'wall_s': wall,
        }, f, indent=2)

    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
