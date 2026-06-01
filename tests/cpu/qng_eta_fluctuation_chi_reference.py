"""QNG-CPU-082-v2 — eta fluctuation test with chi channel active.

Program α refined: CPU-082 v1 showed pure symplectic σ_m+π_m sector has
no substrate-intrinsic scale (P ~ ε^4 exactly). v2 adds the chi channel
with CHI_DECAY dissipation, which is the ONLY non-conservative term in
v8. Hypothesis: FDT holds on chi, giving an η that is ε-independent.

Protocol:
  Lattice: 1D L=100 periodic
  Fields: sigma_m, pi_m, chi
  EOM:
    dot(sigma_m) = pi_m / mu_m
    dot(pi_m)    = beta_m · Δsigma_m − k_eff · (sigma_m − sigma_ref)
                   + K_BACK · chi  (chi back-reaction on sigma_m)
    dot(chi)     = alpha · <sigma_m field gradient>  − CHI_DECAY · chi
                   + eps_xi · kick_noise  (NONE for deterministic test)

For deterministic test:
  Perturb: sigma_m, pi_m, chi all += eps · randn(L)
  Evolve T=200 lu, sample every 5 lu
  Measure: <Var(chi)>·<Var(pi_m)>  — cross product (canonical conjugate pair)
  Also: <Var(sigma_m)>·<Var(pi_m)>  (original CPU-082 reference)

Key test: does <Var(chi)> saturate at ε-independent level due to
CHI_DECAY thermalization? If yes → universal substrate scale found.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-eta-fluctuation-chi-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# v8 parameters
SIGMA_M_REF = 0.5
BETA_M = 0.40
MU_M = 10.0
K_EFF = 0.04
K_BACK = 0.10
ALPHA_BACK = 0.005       # chi response to sigma_m gradient (small)
CHI_DECAY = 0.020        # v8 canonical dissipation rate

L = 100
DT = 0.025
T_RUN = 400.0            # longer run: need to reach chi-thermalization
T_BURN = 100.0
SAMPLE_EVERY_LU = 5.0


def laplacian_1d(f):
    return np.roll(f, 1) + np.roll(f, -1) - 2.0 * f


def gradient_1d(f):
    return 0.5 * (np.roll(f, -1) - np.roll(f, 1))


def step_rk2(sm, pi_m, chi, dt):
    """2nd-order RK integrator (simple; not symplectic because of chi_decay)."""
    # Step 1
    grad_sm = gradient_1d(sm)
    lap_sm = laplacian_1d(sm)

    dsm1 = pi_m / MU_M
    dpi1 = BETA_M * lap_sm - K_EFF * (sm - SIGMA_M_REF) + K_BACK * chi
    dchi1 = ALPHA_BACK * grad_sm - CHI_DECAY * chi

    sm_h = sm + 0.5 * dt * dsm1
    pi_h = pi_m + 0.5 * dt * dpi1
    chi_h = chi + 0.5 * dt * dchi1

    # Step 2
    grad_sm_h = gradient_1d(sm_h)
    lap_sm_h = laplacian_1d(sm_h)

    dsm2 = pi_h / MU_M
    dpi2 = BETA_M * lap_sm_h - K_EFF * (sm_h - SIGMA_M_REF) + K_BACK * chi_h
    dchi2 = ALPHA_BACK * grad_sm_h - CHI_DECAY * chi_h

    sm_new = sm + dt * dsm2
    pi_new = pi_m + dt * dpi2
    chi_new = chi + dt * dchi2

    return sm_new, pi_new, chi_new


def hamiltonian(sm, pi_m, chi):
    """Pseudo-Hamiltonian (no chi kinetic term since chi is overdamped)."""
    kin = 0.5 * np.sum(pi_m * pi_m) / MU_M
    grad = np.roll(sm, -1) - sm
    pot_grad = 0.5 * BETA_M * np.sum(grad * grad)
    pot_res = 0.5 * K_EFF * np.sum((sm - SIGMA_M_REF) ** 2)
    pot_chi = 0.5 * K_BACK * np.sum(chi * chi)  # chi "tension"
    return kin + pot_grad + pot_res + pot_chi


def run_one(eps, seed):
    rng = np.random.default_rng(seed)
    sm = SIGMA_M_REF + eps * rng.standard_normal(L)
    pi_m = eps * rng.standard_normal(L)
    chi = eps * rng.standard_normal(L)

    H0 = hamiltonian(sm, pi_m, chi)

    n_steps = int(T_RUN / DT)
    sample_every = max(1, int(SAMPLE_EVERY_LU / DT))

    times = []
    var_sm = []
    var_pi = []
    var_chi = []
    H_arr = []

    for s in range(n_steps):
        sm, pi_m, chi = step_rk2(sm, pi_m, chi, DT)
        if s % sample_every == 0:
            t = s * DT
            times.append(t)
            var_sm.append(float(np.var(sm - np.mean(sm))))
            var_pi.append(float(np.var(pi_m - np.mean(pi_m))))
            var_chi.append(float(np.var(chi - np.mean(chi))))
            H_arr.append(hamiltonian(sm, pi_m, chi))

    t_arr = np.array(times)
    warm = t_arr > T_BURN
    var_sm = np.array(var_sm)
    var_pi = np.array(var_pi)
    var_chi = np.array(var_chi)
    H_arr = np.array(H_arr)

    H_drift = abs(H_arr[-1] - H0) / max(abs(H0), 1e-10)

    return {
        'eps': eps, 'seed': seed,
        'var_sm_mean': float(var_sm[warm].mean()),
        'var_pi_mean': float(var_pi[warm].mean()),
        'var_chi_mean': float(var_chi[warm].mean()),
        'var_chi_final': float(var_chi[warm][-10:].mean()),
        'product_sm_pi':  float(var_sm[warm].mean() * var_pi[warm].mean()),
        'product_chi_pi': float(var_chi[warm].mean() * var_pi[warm].mean()),
        'product_chi_sm': float(var_chi[warm].mean() * var_sm[warm].mean()),
        'H0': float(H0), 'H_final': float(H_arr[-1]),
        'H_drift_frac': float(H_drift),
    }


def scaling_exponent(products, eps_values):
    """Fit log(P) = zeta * log(eps) + const."""
    logp = np.log(products)
    loge = np.log(eps_values)
    slope, intercept = np.polyfit(loge, logp, 1)
    return float(slope), float(np.exp(intercept))


def main():
    print("=" * 80)
    print("QNG-CPU-082-v2: eta fluctuation with chi channel (program alpha refined)")
    print("=" * 80)
    print(f"  L={L}, DT={DT}, T_RUN={T_RUN} lu")
    print(f"  mu_m={MU_M}, beta_m={BETA_M}, k_eff={K_EFF}")
    print(f"  K_BACK={K_BACK}, ALPHA_BACK={ALPHA_BACK}, CHI_DECAY={CHI_DECAY}")

    eps_values = [0.005, 0.010, 0.020]
    seeds = [7, 13, 31]
    results = []

    t_start = time.time()
    for eps in eps_values:
        for seed in seeds:
            r = run_one(eps, seed)
            results.append(r)
            print(f"  eps={eps:.3f} seed={seed}  "
                  f"<Var(chi)>={r['var_chi_mean']:.3e}  "
                  f"<Var(sm)>={r['var_sm_mean']:.3e}  "
                  f"<Var(pi)>={r['var_pi_mean']:.3e}  "
                  f"Q_chi_pi={r['product_chi_pi']:.3e}  "
                  f"H_drift={r['H_drift_frac']:.2e}")

    wall = time.time() - t_start
    print(f"\n  Total wall: {wall:.1f}s")

    # Aggregate per eps
    by_eps = {}
    for eps in eps_values:
        rs = [r for r in results if r['eps'] == eps]
        by_eps[eps] = {
            'var_chi_mean': float(np.mean([r['var_chi_mean'] for r in rs])),
            'var_sm_mean':  float(np.mean([r['var_sm_mean'] for r in rs])),
            'var_pi_mean':  float(np.mean([r['var_pi_mean'] for r in rs])),
            'product_chi_pi': float(np.mean([r['product_chi_pi'] for r in rs])),
            'product_sm_pi':  float(np.mean([r['product_sm_pi']  for r in rs])),
            'product_chi_sm': float(np.mean([r['product_chi_sm'] for r in rs])),
        }

    eps_arr = np.array(eps_values)

    print("\n" + "=" * 80)
    print("SCALING ANALYSIS (3-seed means)")
    print("=" * 80)

    # Each variance individually
    for channel in ['var_sm_mean', 'var_pi_mean', 'var_chi_mean']:
        vals = np.array([by_eps[e][channel] for e in eps_values])
        zeta, amp = scaling_exponent(vals, eps_arr)
        print(f"  {channel:15s}  ~ eps^{zeta:.3f}")

    print()

    # Cross products
    for prod in ['product_sm_pi', 'product_chi_pi', 'product_chi_sm']:
        vals = np.array([by_eps[e][prod] for e in eps_values])
        zeta, amp = scaling_exponent(vals, eps_arr)
        print(f"  {prod:18s} ~ eps^{zeta:.3f}  "
              f"(eps=0.005: {vals[0]:.3e},  eps=0.020: {vals[2]:.3e})")

    # Verdict: look at var_chi_mean scaling specifically
    var_chi_vals = np.array([by_eps[e]['var_chi_mean'] for e in eps_values])
    zeta_chi, _ = scaling_exponent(var_chi_vals, eps_arr)

    if abs(zeta_chi) < 0.3:
        verdict_chi = "CHI_SATURATES_UNIVERSAL"
        chi_comment = "chi variance eps-independent -> CHI_DECAY thermalization gives universal scale"
    elif 1.7 <= zeta_chi <= 2.3:
        verdict_chi = "CHI_LINEAR"
        chi_comment = "chi variance scales as eps^2 -> pure linear response, no substrate scale in chi"
    else:
        verdict_chi = "CHI_AMBIGUOUS"
        chi_comment = f"chi scaling exponent {zeta_chi:.2f} intermediate"

    print(f"\n  VERDICT for chi: {verdict_chi}")
    print(f"  {chi_comment}")

    # Dedicated test: measure chi saturation ratio (if CHI_DECAY thermalizes)
    # chi should evolve: dchi/dt = ALPHA·grad_sm - CHI_DECAY·chi
    # In equilibrium: <chi²> ~ (ALPHA/CHI_DECAY)² · <grad_sm²>
    # This scales as <grad_sm²> ~ eps², so chi would also ~ eps² at equilibrium
    # UNLESS there's a noise floor (e.g., from integration error)

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'L': L, 'DT': DT, 'T_RUN': T_RUN, 'T_BURN': T_BURN,
            'MU_M': MU_M, 'BETA_M': BETA_M, 'K_EFF': K_EFF,
            'K_BACK': K_BACK, 'ALPHA_BACK': ALPHA_BACK, 'CHI_DECAY': CHI_DECAY,
            'eps_values': eps_values, 'seeds': seeds,
            'runs': results,
            'by_eps': {str(k): v for k, v in by_eps.items()},
            'zeta_chi': float(zeta_chi),
            'verdict_chi': verdict_chi,
            'comment': chi_comment,
            'wall_s': wall,
        }, f, indent=2)

    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
