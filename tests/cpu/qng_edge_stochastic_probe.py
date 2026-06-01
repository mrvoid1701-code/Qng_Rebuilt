"""QNG-CPU-092: Edge-stochastic hbar probe (Gabriel intuition).

Promote each edge (i,j) from passive relation to stochastic channel by
adding a phase offset xi_ij(t) to the XY coupling:

    cos(phi_i - phi_j)  ->  cos(phi_i - phi_j + xi_ij)

Two modes:
  QUENCHED: xi_ij frozen at t=0, sampled once.  Preserves H structure.
  DYNAMIC:  xi_ij resampled at each noise step (tau_c = dt_noise).

Scan eps in {0, 0.01, 0.05, 0.10, 0.30, 1.00}.
Measure <L> = 2<T> - <H>, Var(phi), <cos(pair)>.

Gate X1 (quenched null): <L> shift < eps^2.
Gate X2 (dynamic response): slope d<L>/d eps; linear => no hbar.
Gate X3 (coarse-graining): compare L=8 vs L=10.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-stochastic-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

# Substrate parameters (v8 canonical pure-XY vacuum)
BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 200.0
N_STEPS = int(T_SIM / DT)

# Six cubic neighbour offsets
NBR = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
Z = len(NBR)


def build_edge_list(L):
    """Undirected edge list for z=6 cubic lattice.
    Returns array of (i_flat, j_flat) pairs with i<j to avoid duplicates."""
    edges = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                # +x neighbour
                nx = (x + 1) % L
                j = nx * L * L + y * L + z
                edges.append((min(i,j), max(i,j)))
                # +y neighbour
                ny = (y + 1) % L
                j = x * L * L + ny * L + z
                edges.append((min(i,j), max(i,j)))
                # +z neighbour
                nz = (z + 1) % L
                j = x * L * L + y * L + nz
                edges.append((min(i,j), max(i,j)))
    return np.array(edges, dtype=np.int64)


def build_edge_index(edges, N):
    """For each node i, list of (neighbour_j, edge_id, sign) where sign=+1
    if i is the smaller index of the edge (phi_i - phi_j order), -1 otherwise.
    Need for gradient: dE/dphi_i."""
    per_node = [[] for _ in range(N)]
    for e_id, (a, b) in enumerate(edges):
        per_node[a].append((b, e_id, +1))
        per_node[b].append((a, e_id, -1))
    return per_node


def energy_and_force(phi, pi_phi, edges, xi, node_edges):
    """Pure XY + kinetic, with edge phase offsets xi[e_id].
    Returns (H, force_on_phi).

    E_pair(edge) = -(beta_phi/z) * cos(phi_a - phi_b + xi_edge)
    Note: the 1/(2z) in the Hamiltonian becomes 1/z here because the edge
    list iterates each pair only ONCE (not i-j and j-i).
    """
    N = phi.shape[0]
    a = edges[:, 0]
    b = edges[:, 1]
    dphi = phi[a] - phi[b] + xi
    E_pair = -(BETA_PHI / Z) * np.cos(dphi)
    E_phi = E_pair.sum()
    T_phi = 0.5 * (pi_phi * pi_phi).sum() / MU_PHI
    H = T_phi + E_phi

    # Force: dH/dphi_i = -dV/dphi_i -> phi_dot term via Hamilton eq
    # dE_pair/dphi_a = (beta_phi/z) * sin(dphi)
    # dE_pair/dphi_b = -(beta_phi/z) * sin(dphi)
    sin_dphi = np.sin(dphi)
    coeff = (BETA_PHI / Z) * sin_dphi
    force = np.zeros(N)
    np.add.at(force, a, -coeff)  # dH/dphi_a = +coeff so -dH/dphi_a = -coeff
    np.add.at(force, b, +coeff)
    return H, T_phi, E_phi, force


def yoshida4_step(phi, pi_phi, edges, xi, node_edges, dt):
    """4th-order symplectic. Standard Yoshida coefficients."""
    w1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    w0 = 1.0 - 2.0 * w1
    coeffs = [w1, w0, w1]

    for w in coeffs:
        dt_sub = w * dt
        # Kick (half)
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi, node_edges)
        pi_phi = pi_phi + 0.5 * dt_sub * f
        # Drift (full)
        phi = phi + dt_sub * pi_phi / MU_PHI
        # Wrap
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        # Kick (half)
        _, _, _, f = energy_and_force(phi, pi_phi, edges, xi, node_edges)
        pi_phi = pi_phi + 0.5 * dt_sub * f

    return phi, pi_phi


def run_trial(L, eps, mode, seed, dt_noise_steps=None, burn_in_frac=0.25):
    """Single trial. mode in {'quenched', 'dynamic', 'zero'}.

    dt_noise_steps: resample xi every this many integrator steps (dynamic).
    """
    rng = np.random.default_rng(seed)
    N = L**3
    edges = build_edge_list(L)
    node_edges = build_edge_index(edges, N)
    n_edges = edges.shape[0]

    # Initial condition: small thermal perturbation from ferromagnetic ground
    phi = rng.normal(0, 0.1, size=N)
    pi_phi = rng.normal(0, 0.05, size=N) * np.sqrt(MU_PHI)

    # xi initialization
    if mode == 'zero' or eps == 0:
        xi = np.zeros(n_edges)
    else:
        xi = rng.normal(0, eps, size=n_edges)

    H_hist = []
    T_hist = []
    E_hist = []
    cos_hist = []
    phi_var_hist = []
    times = []

    n_burn = int(burn_in_frac * N_STEPS)

    for step in range(N_STEPS):
        # Dynamic resample
        if mode == 'dynamic' and dt_noise_steps is not None and step % dt_noise_steps == 0 and step > 0:
            xi = rng.normal(0, eps, size=n_edges)

        phi, pi_phi = yoshida4_step(phi, pi_phi, edges, xi, node_edges, DT)

        if step >= n_burn and step % 10 == 0:
            H, T, E, _ = energy_and_force(phi, pi_phi, edges, xi, node_edges)
            a = edges[:, 0]; b = edges[:, 1]
            cos_avg = float(np.cos(phi[a] - phi[b] + xi).mean())
            H_hist.append(H)
            T_hist.append(T)
            E_hist.append(E)
            cos_hist.append(cos_avg)
            phi_var_hist.append(float(phi.var()))
            times.append(step * DT)

    H_arr = np.array(H_hist)
    T_arr = np.array(T_hist)
    E_arr = np.array(E_hist)
    cos_arr = np.array(cos_hist)

    H_mean = float(H_arr.mean())
    T_mean = float(T_arr.mean())
    E_mean = float(E_arr.mean())
    L_val = 2 * T_mean - H_mean  # E_char
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0))

    return {
        'L_lattice': L,
        'N': N,
        'eps': eps,
        'mode': mode,
        'seed': seed,
        'H_mean': H_mean,
        'T_mean': T_mean,
        'E_mean': E_mean,
        'L_invariant': L_val,
        'cos_mean': float(cos_arr.mean()),
        'phi_var_mean': float(np.mean(phi_var_hist)),
        'H_drift_pct': H_drift * 100,
        'n_samples': len(H_hist),
    }


def main():
    print("=" * 70)
    print("QNG-CPU-092: Edge-stochastic hbar probe")
    print("=" * 70)
    print(f"  beta_phi = {BETA_PHI}, mu_phi = {MU_PHI}, dt = {DT}")
    print(f"  T_sim = {T_SIM} lu ({N_STEPS} steps)")
    print()

    eps_values = [0.0, 0.01, 0.05, 0.10, 0.30, 1.00]
    L_values = [8, 10]
    modes = ['quenched', 'dynamic']
    n_seeds = 2  # disorder averaging (small for CPU speed)

    all_results = []

    for L in L_values:
        N = L**3
        pred_L = N * BETA_PHI / 2.0
        print(f"\n--- L = {L} (N = {N}, XY ground = {pred_L:.2f}) ---")
        for mode in modes:
            print(f"\n  mode = {mode}")
            print(f"  {'eps':>6} {'<L>':>10} {'<L>/<L>_0':>10} {'<cos>':>8} {'H_drift%':>8} {'seed':>4}")
            base_L = None
            for eps in eps_values:
                seeds = [42] if eps == 0 else list(range(10, 10 + n_seeds))
                trial_Ls = []
                for s in seeds:
                    t0 = time.time()
                    dt_noise = 20 if mode == 'dynamic' else None
                    r = run_trial(L, eps, mode if eps > 0 else 'zero', s,
                                  dt_noise_steps=dt_noise)
                    dt_took = time.time() - t0
                    all_results.append(r)
                    trial_Ls.append(r['L_invariant'])
                    ratio = r['L_invariant'] / base_L if base_L else 1.0
                    print(f"  {eps:>6.2f} {r['L_invariant']:>10.3f} {ratio:>10.5f} "
                          f"{r['cos_mean']:>8.4f} {r['H_drift_pct']:>8.4f} {s:>4}  ({dt_took:.1f}s)")
                if eps == 0:
                    base_L = np.mean(trial_Ls)

    print("\n" + "=" * 70)
    print("GATE EVALUATION")
    print("=" * 70)

    by_key = {}
    for r in all_results:
        k = (r['L_lattice'], r['mode'], r['eps'])
        by_key.setdefault(k, []).append(r)

    # Gate X1 (quenched) and X2 (dynamic) for each L
    gates = {}
    for L in L_values:
        N = L**3
        gates[L] = {}
        for mode in modes:
            baseline = np.mean([r['L_invariant'] for r in by_key[(L, 'quenched', 0.0)]])
            slopes = []
            for eps in eps_values:
                if eps == 0:
                    continue
                Ls = [r['L_invariant'] for r in by_key[(L, mode, eps)]]
                L_mean = np.mean(Ls)
                shift = L_mean - baseline
                rel_shift = shift / baseline
                slopes.append((eps, rel_shift))
            print(f"\n  L={L}, mode={mode}:")
            for eps, rs in slopes:
                print(f"    eps={eps:.2f}: relative shift = {rs:+.6f}  ({rs*100:+.4f}%)")

            # Power-law fit shift ~ eps^p
            xs = np.array([s[0] for s in slopes if abs(s[1]) > 1e-10])
            ys = np.array([abs(s[1]) for s in slopes if abs(s[1]) > 1e-10])
            if len(xs) >= 2:
                try:
                    p, logA = np.polyfit(np.log(xs), np.log(ys), 1)
                    print(f"    shift ~ eps^{p:.3f},  prefactor A = {np.exp(logA):.4f}")
                    gates[L][mode] = {'power': float(p), 'A': float(np.exp(logA)),
                                       'slopes': slopes}
                except Exception:
                    gates[L][mode] = {'power': None, 'slopes': slopes}

    # X1: quenched power should be ~2
    print("\n" + "-" * 70)
    print("  X1 (quenched null):  shift should scale as eps^2")
    for L in L_values:
        p = gates[L].get('quenched', {}).get('power')
        if p is not None:
            verdict = 'PASS' if 1.7 < p < 2.3 else ('LINEAR' if 0.7 < p < 1.3 else 'OTHER')
            print(f"    L={L}: eps^{p:.3f}  -> {verdict}")

    print("\n  X2 (dynamic response):  slope/form classification")
    for L in L_values:
        p = gates[L].get('dynamic', {}).get('power')
        if p is not None:
            print(f"    L={L}: eps^{p:.3f}")
            if abs(p - 1.0) < 0.3:
                print(f"          -> LINEAR response (no hbar candidate)")
            elif abs(p - 2.0) < 0.3:
                print(f"          -> QUADRATIC (same as quenched; fluctuations thermal)")
            elif p < 0.3:
                print(f"          -> PLATEAU / universal scale (hbar candidate!)")
            else:
                print(f"          -> anomalous exponent")

    print("\n  X3 (coarse-graining):  L=10/L=8 intensivity")
    for mode in modes:
        if 'power' in gates[8].get(mode, {}) and 'power' in gates[10].get(mode, {}):
            A8 = gates[8][mode].get('A', 0)
            A10 = gates[10][mode].get('A', 0)
            if A8 > 0 and A10 > 0:
                ratio = A10 / A8
                expected_intensive = 1.0
                expected_extensive = (10/8)**3
                print(f"    mode={mode}: A(L=10)/A(L=8) = {ratio:.3f}  "
                      f"(intensive=1, extensive N-scaling={expected_extensive:.3f})")

    # Dump JSON
    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'inputs': {
                'beta_phi': BETA_PHI, 'mu_phi': MU_PHI, 'dt': DT,
                'T_sim': T_SIM, 'eps_values': eps_values, 'L_values': L_values,
                'modes': modes, 'n_seeds': n_seeds,
            },
            'results': all_results,
            'gates': {str(L): gates[L] for L in L_values},
        }, f, indent=2, default=float)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
