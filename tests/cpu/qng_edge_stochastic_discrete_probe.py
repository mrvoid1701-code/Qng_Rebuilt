"""QNG-CPU-094: Edge-stochastic DISCRETE probe (Poisson + Z_N).

CPU-092+093 showed that ALL continuous scalar noise on edges gives
ε^2 Debye-Waller response — smooth renormalization of cos coupling,
no quantization.

This test probes DISCRETE stochastic structures which violate the
Taylor-expansion / characteristic-function argument:

1. **Sparse Bernoulli-Gaussian** (rare events): each edge at each step
   has probability p of receiving a kick ξ ~ N(0, A/√p); else ξ=0.
   Mean 0, variance A². At p→0, limit = compound Poisson.
   TEST: at small p, does the response deviate from A^2 scaling?

2. **Z_6 discrete** (Professor Z_N recommendation): each edge at each
   step samples ξ from {0, π/3, 2π/3, π, 4π/3, 5π/3} uniformly.
   Mean ≈ 0 (up to lattice offset), variance = finite.
   TEST: is the response DIFFERENT from Gaussian at matched variance?
   Especially: does <L> show any DISCRETE signature at ε = π/3
   (one step)?

3. **Uniform bounded** (xi ~ U[-a, a]): maximally flat, no heavy tails,
   no discreteness. Pure distributional-shape control.

L=8, T=150 lu. Comparison of |Δ⟨L⟩| scaling vs equivalent rms.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-stochastic-discrete-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 150.0
N_STEPS = int(T_SIM / DT)
L = 8
Z = 6


def build_edge_list(L):
    edges = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                for dx, dy, dz in [(1,0,0), (0,1,0), (0,0,1)]:
                    nx, ny, nz = (x+dx) % L, (y+dy) % L, (z+dz) % L
                    j = nx * L * L + ny * L + nz
                    edges.append((min(i,j), max(i,j)))
    return np.array(edges, dtype=np.int64)


def sample_xi(rng, n, rms, family, params=None):
    """Draw xi with target rms (or characteristic scale).

    family:
      'gaussian': N(0, rms)
      'bernoulli_gauss': each site prob p of N(0, rms/sqrt(p)), else 0
      'z6': uniform on {0, pi/3, 2pi/3, pi, 4pi/3, 5pi/3}  (scale is fixed)
      'z6_centered': z6 shifted so mean=0 exactly per sample
      'uniform': U[-a,a] with a=rms*sqrt(3)
    """
    if family == 'gaussian':
        return rng.normal(0, rms, size=n)
    elif family == 'bernoulli_gauss':
        p = params.get('p', 0.1)
        mask = rng.random(n) < p
        amp = rms / np.sqrt(p) if p > 0 else 0.0
        kicks = rng.normal(0, amp, size=n)
        return mask * kicks
    elif family == 'z6':
        # 6 discrete values in Z_6
        k = rng.integers(0, 6, size=n)
        values = (2 * np.pi / 6) * k  # {0, pi/3, ..., 5pi/3}
        # center to mean 0 by subtracting sample mean
        values = values - values.mean()
        # scale: original rms is ~pi*sqrt((6^2-1)/12)/3 ~ 1.71; we ignore rms match here
        # instead 'rms' is multiplicative scale factor
        return rms * values / (np.sqrt(np.mean(values**2)) + 1e-12)
    elif family == 'uniform':
        a = rms * np.sqrt(3.0)
        return rng.uniform(-a, a, size=n)
    else:
        raise ValueError(family)


def energy_and_force(phi, pi_phi, edges, xi):
    a = edges[:, 0]
    b = edges[:, 1]
    dphi = phi[a] - phi[b] + xi
    E_phi = -(BETA_PHI / Z) * np.cos(dphi).sum()
    T_phi = 0.5 * (pi_phi * pi_phi).sum() / MU_PHI
    H = T_phi + E_phi
    sin_dphi = np.sin(dphi)
    coeff = (BETA_PHI / Z) * sin_dphi
    N = phi.shape[0]
    force = np.zeros(N)
    np.add.at(force, a, -coeff)
    np.add.at(force, b, +coeff)
    return H, T_phi, E_phi, force


def yoshida4_step(phi, pi_phi, edges, xi, dt):
    w1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    w0 = 1.0 - 2.0 * w1
    coeffs = [w1, w0, w1]
    for w in coeffs:
        dt_sub = w * dt
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
        phi = phi + dt_sub * pi_phi / MU_PHI
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
    return phi, pi_phi


def run_trial(rms, family, params, mode, seed, dt_noise_steps=None):
    rng = np.random.default_rng(seed)
    N = L**3
    edges = build_edge_list(L)
    n_edges = edges.shape[0]
    phi = rng.normal(0, 0.1, size=N)
    pi_phi = rng.normal(0, 0.05, size=N) * np.sqrt(MU_PHI)

    if rms == 0:
        xi = np.zeros(n_edges)
    else:
        xi = sample_xi(rng, n_edges, rms, family, params)

    H_list, T_list = [], []
    xi_var_list = []
    n_burn = int(0.25 * N_STEPS)
    for step in range(N_STEPS):
        if mode == 'dynamic' and dt_noise_steps and step % dt_noise_steps == 0 and step > 0 and rms > 0:
            xi = sample_xi(rng, n_edges, rms, family, params)
        phi, pi_phi = yoshida4_step(phi, pi_phi, edges, xi, DT)
        if step >= n_burn and step % 10 == 0:
            H, T, _, _ = energy_and_force(phi, pi_phi, edges, xi)
            H_list.append(H)
            T_list.append(T)
            if rms > 0:
                xi_var_list.append(xi.var())

    H_arr = np.array(H_list)
    T_arr = np.array(T_list)
    H_mean = float(H_arr.mean())
    T_mean = float(T_arr.mean())
    L_val = 2 * T_mean - H_mean
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0) * 100)
    return {
        'rms': rms, 'family': family, 'mode': mode, 'seed': seed, 'params': params or {},
        'H_mean': H_mean, 'T_mean': T_mean, 'L_invariant': L_val,
        'H_drift_pct': H_drift,
        'xi_var_effective': float(np.mean(xi_var_list)) if xi_var_list else 0.0,
    }


def main():
    print("=" * 78)
    print("QNG-CPU-094: Discrete / Poisson edge-stochastic probe")
    print("=" * 78)
    print(f"  L={L}, beta_phi={BETA_PHI}, T_sim={T_SIM}")
    print(f"  All distributions compared at matched RMS (except z6)")
    print()

    rms_values = [0.0, 0.05, 0.10, 0.20, 0.30]

    tests = [
        ('gaussian', 'gaussian', None),
        ('bernoulli01', 'bernoulli_gauss', {'p': 0.1}),
        ('bernoulli001', 'bernoulli_gauss', {'p': 0.01}),
        ('uniform', 'uniform', None),
        ('z6', 'z6', None),
    ]

    r0 = run_trial(0.0, 'gaussian', None, 'quenched', 42)
    L0 = r0['L_invariant']
    print(f"  Baseline <L>_0 = {L0:.4f} (XY ground prediction = {L**3 * BETA_PHI / 2:.2f})")
    print()

    all_results = [r0]

    for label, family, params in tests:
        for mode in ['quenched', 'dynamic']:
            print(f"  {label:>12} / {mode:>8}:")
            print(f"    {'rms':>6} {'<L>':>9} {'shift':>10} {'shift/<L>_0':>13} {'xi_var_eff':>12} {'H_drift%':>9}")
            for rms in rms_values:
                if rms == 0:
                    continue
                Ls = []
                vars_eff = []
                h_drifts = []
                for s in [100, 101]:
                    r = run_trial(rms, family, params, mode, s, dt_noise_steps=20 if mode == 'dynamic' else None)
                    all_results.append(r)
                    Ls.append(r['L_invariant'])
                    vars_eff.append(r['xi_var_effective'])
                    h_drifts.append(r['H_drift_pct'])
                Lmean = np.mean(Ls)
                shift = Lmean - L0
                print(f"    {rms:>6.2f} {Lmean:>9.3f} {shift:>+10.4f} {shift/L0:>+13.6f} "
                      f"{np.mean(vars_eff):>12.4f} {np.mean(h_drifts):>9.3f}")
            print()

    # Fits
    print("=" * 78)
    print("POWER-LAW FITS: |shift|/<L>_0 = A * rms^p (match to effective xi variance)")
    print("=" * 78)
    by_key = {}
    for r in all_results:
        if r['rms'] == 0:
            continue
        k = (r['family'], str(r.get('params') or ''), r['mode'])
        by_key.setdefault(k, []).append(r)

    for key, rs in sorted(by_key.items()):
        family, params, mode = key
        rmss = sorted(set(r['rms'] for r in rs))
        xs, ys, vars_eff = [], [], []
        for rms in rmss:
            Lvals = [r['L_invariant'] for r in rs if r['rms'] == rms]
            var_effs = [r['xi_var_effective'] for r in rs if r['rms'] == rms]
            shift = abs(np.mean(Lvals) - L0)
            if shift > 1e-8:
                xs.append(rms); ys.append(shift / L0)
                vars_eff.append(np.mean(var_effs))
        if len(xs) < 2:
            continue
        xs = np.array(xs); ys = np.array(ys); vars_eff = np.array(vars_eff)
        # fit vs rms
        p_rms, lnA_rms = np.polyfit(np.log(xs), np.log(ys), 1)
        # fit vs actual xi variance (more meaningful for bernoulli)
        if np.all(vars_eff > 0):
            p_var, lnA_var = np.polyfit(np.log(np.sqrt(vars_eff)), np.log(ys), 1)
            print(f"  {family:>16s} {params:>15s} / {mode:>8}: "
                  f"shift = {np.exp(lnA_rms):.3f}*rms^{p_rms:.3f}  "
                  f"| shift = {np.exp(lnA_var):.3f}*sqrt(var)^{p_var:.3f}")
        else:
            print(f"  {family:>16s} {params:>15s} / {mode:>8}: shift = {np.exp(lnA_rms):.3f}*rms^{p_rms:.3f}")

    print()
    print("INTERPRETATION:")
    print("  - All families with p~2 (vs effective xi rms) => Debye-Waller universality")
    print("  - bernoulli p<<1 with p<2 => rare-event signature (Poisson limit)")
    print("  - z6 with distinct signature => discrete-spectrum candidate")

    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'L': L, 'beta_phi': BETA_PHI, 'T_sim': T_SIM, 'L_0': L0,
            'rms_values': rms_values,
            'tests': [t[0] for t in tests],
            'results': all_results,
        }, f, indent=2, default=float)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
