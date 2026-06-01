"""QNG-CPU-096: Edge-stochastic SPATIAL correlation probe.

CPU-092/093/094 closed the scalar i.i.d. edge noise family. CPU-095
tests TEMPORAL correlation (OU). This test tests SPATIAL correlation:
the ensemble of xi_ij is no longer independent across edges but
generated from a spatially correlated Gaussian field with correlation
length l.

Generation:
  1. Sample white Gaussian field f_mu(x) on dual lattice (one per spatial
     direction mu in {x, y, z}), size L^3.
  2. Smooth by Gaussian kernel of width l via FFT:
         F_mu(k) = f_mu(k) * exp(-l^2 * |k|^2 / 2)
     Renormalize to maintain unit per-site variance.
  3. For edge (i, j) of direction mu, set xi_ij = rms * F_mu(midpoint).

KEY QUESTION: does spatial correlation change the scaling of <L> shift
vs rms? If yes, correlated noise may carry different physics (maybe
universal scale).

Expected (hydrodynamic intuition): shift should scale with rms^2
(Debye-Waller) but the prefactor may depend on l. If prefactor saturates
to universal constant independent of l, that's a candidate.

L=8, z=6, vacuum. Scan rms in {0.05, 0.1, 0.2, 0.3}, l in {1, 2, 4}.
Compare to i.i.d. (l=0) baseline.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-stochastic-spatial-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 150.0
N_STEPS = int(T_SIM / DT)
L = 8
Z = 6


def build_edge_list_dir(L):
    """Return edges with direction labels: list of (i, j, mu) for each edge."""
    edges = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x * L * L + y * L + z
                for mu, (dx, dy, dz) in enumerate([(1,0,0), (0,1,0), (0,0,1)]):
                    nx, ny, nz = (x+dx) % L, (y+dy) % L, (z+dz) % L
                    j = nx * L * L + ny * L + nz
                    edges.append((i, j, mu))  # keep direction
    return edges


def generate_correlated_field(rng, L, l_corr):
    """Generate L^3 Gaussian field with correlation length l_corr via FFT smoothing.
    Returns array shape (L, L, L) with unit per-site variance."""
    white = rng.normal(0, 1, size=(L, L, L))
    if l_corr <= 0.0:
        return white
    # k-space smoothing kernel
    k = np.fft.fftfreq(L) * 2 * np.pi
    kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
    k2 = kx**2 + ky**2 + kz**2
    kernel = np.exp(-0.5 * l_corr**2 * k2)
    Fw = np.fft.fftn(white) * kernel
    field = np.real(np.fft.ifftn(Fw))
    # Renormalize to unit variance
    var = field.var()
    if var > 1e-12:
        field = field / np.sqrt(var)
    return field


def sample_xi_correlated(rng, L, rms, l_corr):
    """Generate spatially correlated edge noise of target per-edge rms."""
    n_edges = 3 * L**3
    if rms == 0 or l_corr < 0:
        return np.zeros(n_edges)
    # One field per direction
    xi_flat = np.zeros(n_edges)
    fields = [generate_correlated_field(rng, L, l_corr) for _ in range(3)]
    edges = build_edge_list_dir(L)
    for e_idx, (i, j, mu) in enumerate(edges):
        # Midpoint: index the field at site i (choice: start-of-edge)
        # For periodic lattice, any consistent choice is fine.
        x = i // (L * L)
        y = (i // L) % L
        z = i % L
        xi_flat[e_idx] = rms * fields[mu][x, y, z]
    return xi_flat


def energy_and_force(phi, pi_phi, edges_ij, xi):
    a = edges_ij[:, 0]; b = edges_ij[:, 1]
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


def yoshida4_step(phi, pi_phi, edges_ij, xi, dt):
    w1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    w0 = 1.0 - 2.0 * w1
    for w in [w1, w0, w1]:
        dt_sub = w * dt
        _, _, _, f = energy_and_force(phi, pi_phi, edges_ij, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
        phi = phi + dt_sub * pi_phi / MU_PHI
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        _, _, _, f = energy_and_force(phi, pi_phi, edges_ij, xi)
        pi_phi = pi_phi + 0.5 * dt_sub * f
    return phi, pi_phi


def run_trial(rms, l_corr, mode, seed, dt_noise_steps=20):
    rng = np.random.default_rng(seed)
    N = L**3
    edges = build_edge_list_dir(L)
    edges_ij = np.array([(e[0], e[1]) for e in edges], dtype=np.int64)
    phi = rng.normal(0, 0.1, size=N)
    pi_phi = rng.normal(0, 0.05, size=N) * np.sqrt(MU_PHI)

    if rms == 0:
        xi = np.zeros(3 * N)
    else:
        xi = sample_xi_correlated(rng, L, rms, l_corr)

    H_list, T_list = [], []
    xi_var_list = []
    n_burn = int(0.25 * N_STEPS)
    for step in range(N_STEPS):
        if mode == 'dynamic' and step % dt_noise_steps == 0 and step > 0 and rms > 0:
            xi = sample_xi_correlated(rng, L, rms, l_corr)
        phi, pi_phi = yoshida4_step(phi, pi_phi, edges_ij, xi, DT)
        if step >= n_burn and step % 10 == 0:
            H, T, _, _ = energy_and_force(phi, pi_phi, edges_ij, xi)
            H_list.append(H); T_list.append(T)
            if rms > 0:
                xi_var_list.append(xi.var())

    H_arr = np.array(H_list); T_arr = np.array(T_list)
    H_mean = float(H_arr.mean()); T_mean = float(T_arr.mean())
    L_val = 2 * T_mean - H_mean
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0) * 100)
    return {
        'rms': rms, 'l_corr': l_corr, 'mode': mode, 'seed': seed,
        'H_mean': H_mean, 'T_mean': T_mean, 'L_invariant': L_val,
        'H_drift_pct': H_drift,
        'xi_var_effective': float(np.mean(xi_var_list)) if xi_var_list else 0.0,
    }


def main():
    print("=" * 78)
    print("QNG-CPU-096: Edge spatial correlation probe")
    print("=" * 78)
    print(f"  L={L}, beta_phi={BETA_PHI}, T_sim={T_SIM}")
    print(f"  Scan rms in {{0.05, 0.1, 0.2, 0.3}}, l_corr in {{0, 1, 2, 4}} (0=i.i.d.)")
    print()

    r0 = run_trial(0.0, 0.0, 'quenched', 42)
    L0 = r0['L_invariant']
    print(f"  Baseline <L>_0 = {L0:.4f}")
    print()

    rms_values = [0.05, 0.10, 0.20, 0.30]
    l_values = [0.0, 1.0, 2.0, 4.0]

    results = [r0]

    for l_corr in l_values:
        for mode in ['quenched', 'dynamic']:
            tag = "i.i.d." if l_corr == 0 else f"l={l_corr:.0f}"
            print(f"  {tag:>8s} / {mode:>8s}:")
            print(f"    {'rms':>6} {'<L>':>9} {'shift':>10} {'shift/L0':>12} {'var_eff':>10} {'H_drift%':>9}")
            for rms in rms_values:
                Ls, vars_e, hd = [], [], []
                for s in [100, 101]:
                    r = run_trial(rms, l_corr, mode, s)
                    results.append(r)
                    Ls.append(r['L_invariant']); vars_e.append(r['xi_var_effective']); hd.append(r['H_drift_pct'])
                Lmean = np.mean(Ls)
                shift = Lmean - L0
                print(f"    {rms:>6.2f} {Lmean:>9.3f} {shift:>+10.4f} {shift/L0:>+12.6f} "
                      f"{np.mean(vars_e):>10.4f} {np.mean(hd):>9.3f}")
            print()

    # Power-law fits per (l_corr, mode)
    print("=" * 78)
    print("POWER-LAW FITS: |shift|/<L>_0 = A * rms^p")
    print("=" * 78)
    by_key = {}
    for r in results:
        if r['rms'] == 0: continue
        k = (r['l_corr'], r['mode'])
        by_key.setdefault(k, []).append(r)

    fits = {}
    for key, rs in sorted(by_key.items()):
        rmss = sorted(set(r['rms'] for r in rs))
        xs, ys = [], []
        for rms in rmss:
            Lvals = [r['L_invariant'] for r in rs if r['rms'] == rms]
            shift = abs(np.mean(Lvals) - L0)
            if shift > 1e-8:
                xs.append(rms); ys.append(shift / L0)
        if len(xs) < 2: continue
        xs = np.array(xs); ys = np.array(ys)
        p, lnA = np.polyfit(np.log(xs), np.log(ys), 1)
        A = float(np.exp(lnA))
        tag = "i.i.d." if key[0] == 0 else f"l={key[0]:.0f}"
        print(f"  {tag:>8s} / {key[1]:>8}: A = {A:.3f}, p = {p:.3f}")
        fits[f"l={key[0]}_{key[1]}"] = {'A': A, 'p': p}

    print()
    print("INTERPRETATION:")
    print("  - All p~2 with similar A: spatial correlation is irrelevant")
    print("  - A(l) growing with l: correlation amplifies response (no hbar, classical)")
    print("  - A(l) PLATEAU at universal value: possible hbar candidate")

    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'L': L, 'beta_phi': BETA_PHI, 'T_sim': T_SIM, 'L_0': L0,
            'rms_values': rms_values, 'l_values': l_values,
            'fits': fits,
            'results': results,
        }, f, indent=2, default=float)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
