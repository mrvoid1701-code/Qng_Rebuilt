"""QNG-CPU-093: Edge-stochastic non-Gaussian probe (Savant follow-up).

CPU-092 showed Gaussian xi_ij -> |Delta<L>| ~ 0.5 * eps^2 exactly
(Debye-Waller: <exp(i xi)> = exp(-eps^2/2)).

Prediction for Cauchy xi ~ Cauchy(0, gamma):
  <exp(i xi)> = exp(-|gamma|)       (characteristic function of Cauchy)
  => |Delta<L>|/<L>_0 ~ gamma^1    (LINEAR, not quadratic)

If we find Cauchy ALSO gives linear or anything smooth, then:
  "<cos(dphi + xi)> = <cos(dphi)> * phi_xi(1)" for ANY zero-mean
  distribution, where phi_xi is the characteristic function. Always
  smooth in scale parameter, never quantized.  => NO hbar from any
  scalar edge noise.

If Cauchy gives non-smooth or unexpected response (steps, plateau,
non-monotonic), interesting.

L=8 only, quenched + dynamic, gamma scan. ~5 min runtime.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-stochastic-nongauss-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 150.0
N_STEPS = int(T_SIM / DT)
L = 8
NBR = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
Z = len(NBR)


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


def sample_xi(rng, n, gamma, dist):
    """Sample xi with scale gamma.

    dist in {'gaussian', 'cauchy', 'laplace'}.
    Cauchy is clipped at +-10*gamma to avoid extreme outliers breaking
    the integrator; clipping removes the pure heavy-tail limit but keeps
    the non-Gaussian shape.
    """
    if dist == 'gaussian':
        return rng.normal(0, gamma, size=n)
    elif dist == 'cauchy':
        x = rng.standard_cauchy(size=n) * gamma
        # Clip to +-10*gamma (preserves ~99% of the bulk)
        return np.clip(x, -10*gamma, 10*gamma)
    elif dist == 'laplace':
        # Laplace(0, b) has variance 2*b^2; set b = gamma/sqrt(2)
        return rng.laplace(0, gamma / np.sqrt(2), size=n)
    else:
        raise ValueError(dist)


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


def run_trial(gamma, dist, mode, seed, dt_noise_steps=None):
    rng = np.random.default_rng(seed)
    N = L**3
    edges = build_edge_list(L)
    n_edges = edges.shape[0]
    phi = rng.normal(0, 0.1, size=N)
    pi_phi = rng.normal(0, 0.05, size=N) * np.sqrt(MU_PHI)

    if gamma == 0:
        xi = np.zeros(n_edges)
    else:
        xi = sample_xi(rng, n_edges, gamma, dist)

    H_list, T_list = [], []
    n_burn = int(0.25 * N_STEPS)
    for step in range(N_STEPS):
        if mode == 'dynamic' and dt_noise_steps and step % dt_noise_steps == 0 and step > 0 and gamma > 0:
            xi = sample_xi(rng, n_edges, gamma, dist)
        phi, pi_phi = yoshida4_step(phi, pi_phi, edges, xi, DT)
        if step >= n_burn and step % 10 == 0:
            H, T, _, _ = energy_and_force(phi, pi_phi, edges, xi)
            H_list.append(H)
            T_list.append(T)

    H_arr = np.array(H_list)
    T_arr = np.array(T_list)
    H_mean = float(H_arr.mean())
    T_mean = float(T_arr.mean())
    L_val = 2 * T_mean - H_mean
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0) * 100)
    return {
        'gamma': gamma, 'dist': dist, 'mode': mode, 'seed': seed,
        'H_mean': H_mean, 'T_mean': T_mean, 'L_invariant': L_val,
        'H_drift_pct': H_drift,
    }


def main():
    print("=" * 75)
    print("QNG-CPU-093: Non-Gaussian edge-stochastic probe (Savant follow-up)")
    print("=" * 75)
    print(f"  L=8 (N=512), beta_phi={BETA_PHI}, T_sim={T_SIM}")
    print(f"  Distributions: gaussian (control), cauchy, laplace")
    print(f"  Theory: <cos(dphi + xi)> / <cos(dphi)> = characteristic function")
    print(f"    Gaussian(eps):   exp(-eps^2/2)    -> shift ~ eps^2")
    print(f"    Cauchy(gamma):   exp(-|gamma|)    -> shift ~ gamma^1  (LINEAR)")
    print(f"    Laplace(eps):    1/(1+eps^2/2)    -> shift ~ eps^2 (different prefactor)")
    print()

    eps_values = [0.0, 0.05, 0.10, 0.20, 0.30]
    dists = ['gaussian', 'cauchy', 'laplace']
    all_results = []

    # Get baseline once (any dist at eps=0 is the same)
    r0 = run_trial(0.0, 'gaussian', 'quenched', 42)
    L0 = r0['L_invariant']
    print(f"  Baseline <L>_0 = {L0:.4f} (XY ground = {L**3 * BETA_PHI / 2:.2f})\n")
    all_results.append(r0)

    for dist in dists:
        for mode in ['quenched', 'dynamic']:
            print(f"  {dist} / {mode}:")
            print(f"    {'gamma':>6} {'<L>':>10} {'shift':>10} {'shift/<L>_0':>14}  {'H_drift%':>9}")
            for gamma in eps_values:
                if gamma == 0:
                    continue
                seeds = [100, 101]
                trial_Ls = []
                for s in seeds:
                    r = run_trial(gamma, dist, mode, s, dt_noise_steps=20 if mode=='dynamic' else None)
                    all_results.append(r)
                    trial_Ls.append(r['L_invariant'])
                Lmean = np.mean(trial_Ls)
                shift = Lmean - L0
                print(f"    {gamma:>6.2f} {Lmean:>10.3f} {shift:>+10.4f} {shift/L0:>+14.6f}  {r['H_drift_pct']:>9.3f}")
            print()

    # Power-law fits
    print("=" * 75)
    print("POWER-LAW FITS: |shift|/<L>_0 = A * gamma^p")
    print("=" * 75)
    by_key = {}
    for r in all_results:
        if r['gamma'] == 0:
            continue
        k = (r['dist'], r['mode'])
        by_key.setdefault(k, []).append(r)

    for (dist, mode), rs in sorted(by_key.items()):
        gammas = sorted(set(r['gamma'] for r in rs))
        gammas_used = []
        shifts_used = []
        for g in gammas:
            Lvals = [r['L_invariant'] for r in rs if r['gamma'] == g]
            shift = abs(np.mean(Lvals) - L0)
            if shift > 1e-8:
                gammas_used.append(g)
                shifts_used.append(shift / L0)
        if len(gammas_used) < 2:
            continue
        xs = np.array(gammas_used)
        ys = np.array(shifts_used)
        p, lnA = np.polyfit(np.log(xs), np.log(ys), 1)
        A = np.exp(lnA)
        print(f"  {dist:>9} / {mode:>9}: shift/<L>_0 = {A:.4f} * gamma^{p:.3f}")

    print()
    print("INTERPRETATION:")
    print("  If Cauchy gives p ~ 1 -> linear response -> 'any scalar noise is smooth'")
    print("  If Cauchy gives p ~ 2 -> Gaussian-like (bounded by clip) -> CLT kicks in")
    print("  If Cauchy gives unusual p or plateau -> interesting, worth deeper probe")
    print()

    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'L': L, 'beta_phi': BETA_PHI, 'T_sim': T_SIM, 'L_0': L0,
            'eps_values': eps_values, 'dists': dists,
            'results': all_results,
        }, f, indent=2, default=float)
    print(f"  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
