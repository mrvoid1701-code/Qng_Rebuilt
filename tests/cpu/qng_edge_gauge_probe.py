"""QNG-CPU-097: Compact U(1) lattice-gauge edge probe (Program 9-gauge).

Promotes each edge from a passive geometric relation to a dynamical
U(1) gauge field. Each edge (i,j) carries:
  A_ij in [-pi, pi]    # gauge phase
  E_ij in R            # conjugate momentum ("electric field")

Hamiltonian (gauge-invariant form):

  H = T_phi + T_E
      - (beta_phi/z) * sum_edges cos(phi_i - phi_j - A_ij)   # gauge-invariant phi-hop
      + (mu_B / 2) * sum_plaq (1 - cos(W_plaq))             # magnetic plaquette

  T_phi = sum_i pi_phi_i^2 / (2 mu_phi)
  T_E   = sum_edges E_ij^2 / (2 mu_E)
  W_plaq = A_12 + A_23 + A_34 + A_41  (oriented plaquette sum)

Classical Yoshida4 evolution.

KEY AUDIT QUESTION: does the classical dynamics of this gauge-coupled
system produce a universal action scale (hbar candidate), or does it
merely give continuous classical oscillations?

Prediction (3/4 agent audit 2026-04-22): classical LGT has no
discreteness. Quantization arises from [A_ij, E_ij] = i hbar which is
IMPOSED in quantum LGT, not derived. Classical probe should confirm
this: <L> = 2<T> - <H> is a continuous function of (mu_E, mu_B, beta_phi).
No plateau, no universal scale.

Test signatures:
  1. Plaquette winding W_plaq: does it cluster near 2*pi*n (integer
     monopole sectors)? Classically: NO (continuous).
  2. <cos(W)>: Gaussian smearing, not discrete.
  3. Scan mu_E in {0.1, 1, 10}: does <L>/<H> ratio converge to
     universal constant? If yes -> hbar candidate. If it scales
     smoothly with mu_E -> classical, no hbar.
  4. Scan mu_B in {0.1, 1, 10}: same.

L=6 (216 nodes, 648 edges, 648 plaquettes), T=100 lu, Yoshida4 dt=0.05.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-edge-gauge-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

BETA_PHI = 0.06
MU_PHI = 0.857
DT = 0.05
T_SIM = 100.0
N_STEPS = int(T_SIM / DT)
L = 6
Z = 6


def build_lattice(L):
    """Build edge and plaquette index structures for 3D cubic lattice.

    Returns:
      edges: list of (i, j, mu) for i<j, mu in {0,1,2}
      edge_idx[(i,j,mu)] -> edge index  (with sign convention)
      plaquettes: list of oriented edge-index tuples (signed) (e1, s1, e2, s2, e3, s3, e4, s4)
                  where s is +1 or -1 for orientation
    """
    N = L**3
    def site(x, y, z):
        return x * L * L + y * L + z

    edges = []
    edge_map = {}  # (min(i,j), max(i,j), mu) -> idx
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = site(x, y, z)
                for mu, (dx, dy, dz) in enumerate([(1,0,0), (0,1,0), (0,0,1)]):
                    nx, ny, nz = (x+dx) % L, (y+dy) % L, (z+dz) % L
                    j = site(nx, ny, nz)
                    # Oriented edge: from (x,y,z) in direction mu
                    e_idx = len(edges)
                    edges.append((i, j, mu))
                    # The gauge link A_ij is directed from i to j
                    edge_map[(x, y, z, mu)] = e_idx
        # close scope

    # Plaquettes: pairs of directions (mu<nu) give L^3 plaquettes each
    plaquettes = []
    for x in range(L):
        for y in range(L):
            for z in range(L):
                for (mu, nu) in [(0,1), (0,2), (1,2)]:
                    # Plaquette: forward mu, forward nu (from +mu), backward mu (from +nu), backward nu
                    dx_mu, dy_mu, dz_mu = [(1,0,0),(0,1,0),(0,0,1)][mu]
                    dx_nu, dy_nu, dz_nu = [(1,0,0),(0,1,0),(0,0,1)][nu]
                    # Starting at (x,y,z)
                    # Edge 1: +mu from (x,y,z)          -> +A
                    e1 = edge_map[(x, y, z, mu)]; s1 = +1
                    # Edge 2: +nu from (x+mu_shift,y_shift,z_shift)
                    x2, y2, z2 = (x+dx_mu)%L, (y+dy_mu)%L, (z+dz_mu)%L
                    e2 = edge_map[(x2, y2, z2, nu)]; s2 = +1
                    # Edge 3: -mu from (x+mu+nu) which is +mu direction from (x+nu,...)
                    x3, y3, z3 = (x+dx_nu)%L, (y+dy_nu)%L, (z+dz_nu)%L
                    e3 = edge_map[(x3, y3, z3, mu)]; s3 = -1
                    # Edge 4: -nu from (x+nu) back to (x,y,z); i.e. +nu from (x,y,z)
                    e4 = edge_map[(x, y, z, nu)]; s4 = -1
                    plaquettes.append((e1, s1, e2, s2, e3, s3, e4, s4))

    edges_arr = np.array(edges, dtype=np.int64)  # (n_edges, 3): (i, j, mu)
    plaq_arr = np.array(plaquettes, dtype=np.int64)  # (n_plaq, 8): (e1,s1,e2,s2,e3,s3,e4,s4)
    return edges_arr, plaq_arr


def energy_and_force(phi, pi_phi, A, E, edges, plaquettes, mu_phi_, mu_E_, mu_B_, beta_phi_):
    a = edges[:, 0]; b = edges[:, 1]
    dphi_gauge = phi[a] - phi[b] - A  # gauge-invariant phase
    # XY energy
    E_phi = -(beta_phi_ / Z) * np.cos(dphi_gauge).sum()
    # Kinetic terms
    T_phi = 0.5 * (pi_phi * pi_phi).sum() / mu_phi_
    T_E = 0.5 * (E * E).sum() / mu_E_
    # Plaquette winding
    e1 = plaquettes[:, 0]; s1 = plaquettes[:, 1]
    e2 = plaquettes[:, 2]; s2 = plaquettes[:, 3]
    e3 = plaquettes[:, 4]; s3 = plaquettes[:, 5]
    e4 = plaquettes[:, 6]; s4 = plaquettes[:, 7]
    W = s1 * A[e1] + s2 * A[e2] + s3 * A[e3] + s4 * A[e4]
    E_plaq = mu_B_ * (1 - np.cos(W)).sum()
    H = T_phi + T_E + E_phi + E_plaq

    # Forces
    # phi force: d/dphi_i of XY
    sin_dphi = np.sin(dphi_gauge)
    coeff_phi = (beta_phi_ / Z) * sin_dphi
    N = phi.shape[0]
    force_phi = np.zeros(N)
    np.add.at(force_phi, a, -coeff_phi)
    np.add.at(force_phi, b, +coeff_phi)

    # A force: dH/dA_e = -(beta_phi/z) * sin(dphi_gauge) * (+1) + mu_B * sin(W) * (signs involving A_e)
    # Wait: dphi_gauge = phi_i - phi_j - A, so d/dA of cos(dphi_gauge) = +sin(dphi_gauge)
    # Thus dH_XY/dA_e = -(beta_phi/z) * (+sin(dphi_gauge)) = -(beta_phi/z) sin(dphi_gauge)
    # Force on A = -dH/dA
    force_A = -(-(beta_phi_ / Z) * sin_dphi)  # = (beta_phi/z) * sin(dphi_gauge)
    # Hmm let me redo. H contains -beta/z * cos(phi_i-phi_j-A). dH/dA = -beta/z * sin(phi_i-phi_j-A) * (-1) = +beta/z * sin(...)
    # So force_A = -dH/dA = -(beta/z) * sin(dphi_gauge)
    # That conflicts with above. Let me just carefully:
    #   E_phi_edge = -(beta/z) * cos(dphi_gauge), dphi_gauge = phi_i - phi_j - A_e
    #   d E_phi_edge / d A_e = -(beta/z) * sin(dphi_gauge) * (-1) = (beta/z) * sin(dphi_gauge)
    #   force_A_from_phi = -d E / d A_e = -(beta/z) * sin(dphi_gauge)
    force_A = -(beta_phi_ / Z) * sin_dphi

    # Plaquette contribution: E_plaq = mu_B sum (1 - cos W), dE/dA_e = mu_B sin(W) * (sign of this edge in W)
    # Each edge appears in up to 4 plaquettes with various signs
    n_edges = A.shape[0]
    force_A_plaq = np.zeros(n_edges)
    sin_W = np.sin(W)
    # For each plaquette, add -mu_B * sin(W) * s_k to edge e_k
    for k, s_col in [(0,1), (2,3), (4,5), (6,7)]:
        e_k = plaquettes[:, k]
        s_k = plaquettes[:, s_col]
        contrib = -mu_B_ * sin_W * s_k
        np.add.at(force_A_plaq, e_k, contrib)
    force_A = force_A + force_A_plaq

    # E force: dH/dE_e = E_e / mu_E, but H doesn't depend on E explicitly via potential; E is conjugate to A
    # In Hamilton's eqs: dA/dt = dH/dE = E/mu_E; dE/dt = -dH/dA = force_A
    # So "force on A" updates E, and "force on phi" updates pi_phi.
    return H, T_phi + T_E, E_phi + E_plaq, force_phi, force_A


def yoshida4_step(phi, pi_phi, A, E, edges, plaquettes, mu_phi_, mu_E_, mu_B_, beta_phi_, dt):
    w1 = 1.0 / (2.0 - 2.0**(1.0/3.0))
    w0 = 1.0 - 2.0 * w1
    for w in [w1, w0, w1]:
        dt_sub = w * dt
        _, _, _, f_phi, f_A = energy_and_force(phi, pi_phi, A, E, edges, plaquettes, mu_phi_, mu_E_, mu_B_, beta_phi_)
        pi_phi = pi_phi + 0.5 * dt_sub * f_phi
        E = E + 0.5 * dt_sub * f_A
        phi = phi + dt_sub * pi_phi / mu_phi_
        A = A + dt_sub * E / mu_E_
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        A = (A + np.pi) % (2 * np.pi) - np.pi
        _, _, _, f_phi, f_A = energy_and_force(phi, pi_phi, A, E, edges, plaquettes, mu_phi_, mu_E_, mu_B_, beta_phi_)
        pi_phi = pi_phi + 0.5 * dt_sub * f_phi
        E = E + 0.5 * dt_sub * f_A
    return phi, pi_phi, A, E


def run_trial(mu_E, mu_B, seed, init_amp=0.1):
    rng = np.random.default_rng(seed)
    N = L**3
    edges, plaquettes = build_lattice(L)
    n_edges = edges.shape[0]

    phi = rng.normal(0, init_amp, size=N)
    pi_phi = rng.normal(0, init_amp/2, size=N) * np.sqrt(MU_PHI)
    A = rng.normal(0, init_amp, size=n_edges)
    E = rng.normal(0, init_amp/2, size=n_edges) * np.sqrt(mu_E)

    H_list, L_list, T_list = [], [], []
    plaq_W_samples = []
    n_burn = int(0.3 * N_STEPS)

    for step in range(N_STEPS):
        phi, pi_phi, A, E = yoshida4_step(phi, pi_phi, A, E, edges, plaquettes, MU_PHI, mu_E, mu_B, BETA_PHI, DT)
        if step >= n_burn and step % 10 == 0:
            H, T, V, _, _ = energy_and_force(phi, pi_phi, A, E, edges, plaquettes, MU_PHI, mu_E, mu_B, BETA_PHI)
            H_list.append(H); T_list.append(T)
            if step % 50 == 0:
                # Sample plaquette W distribution
                e1 = plaquettes[:, 0]; s1 = plaquettes[:, 1]
                e2 = plaquettes[:, 2]; s2 = plaquettes[:, 3]
                e3 = plaquettes[:, 4]; s3 = plaquettes[:, 5]
                e4 = plaquettes[:, 6]; s4 = plaquettes[:, 7]
                W = s1 * A[e1] + s2 * A[e2] + s3 * A[e3] + s4 * A[e4]
                plaq_W_samples.append(W.copy())

    H_arr = np.array(H_list); T_arr = np.array(T_list)
    H_mean = float(H_arr.mean()); T_mean = float(T_arr.mean())
    L_val = 2 * T_mean - H_mean
    H_drift = float((H_arr.max() - H_arr.min()) / max(abs(H_mean), 1.0) * 100)

    # Plaquette W stats
    W_all = np.concatenate(plaq_W_samples) if plaq_W_samples else np.array([])
    W_wrapped = (W_all + np.pi) % (2*np.pi) - np.pi
    return {
        'mu_E': mu_E, 'mu_B': mu_B, 'seed': seed,
        'H_mean': H_mean, 'T_mean': T_mean, 'L_invariant': L_val,
        'H_drift_pct': H_drift,
        'W_mean': float(W_wrapped.mean()),
        'W_var': float(W_wrapped.var()),
        'cos_W_mean': float(np.cos(W_wrapped).mean()),
        'L_per_N': L_val / N,
        'H_per_N': H_mean / N,
    }


def main():
    print("=" * 78)
    print("QNG-CPU-097: Compact U(1) lattice-gauge edge probe")
    print("=" * 78)
    print(f"  L={L} (N={L**3} nodes, edges=3L^3={3*L**3}, plaquettes=3L^3={3*L**3})")
    print(f"  beta_phi={BETA_PHI}, mu_phi={MU_PHI}, T_sim={T_SIM}, dt={DT}")
    print(f"  Scan mu_E in {{0.1, 1.0, 10.0}}, mu_B in {{0.1, 1.0, 10.0}}")
    print()

    mu_E_values = [0.1, 1.0, 10.0]
    mu_B_values = [0.1, 1.0, 10.0]

    print(f"  {'mu_E':>6} {'mu_B':>6} {'<L>/N':>10} {'<H>/N':>10} {'<cos W>':>9} {'Var(W)':>8} {'H_drift%':>9}")
    results = []
    for mu_E in mu_E_values:
        for mu_B in mu_B_values:
            Ls, Hs, cosWs, varWs, hds = [], [], [], [], []
            for s in [100, 101]:
                r = run_trial(mu_E, mu_B, s)
                results.append(r)
                Ls.append(r['L_per_N']); Hs.append(r['H_per_N'])
                cosWs.append(r['cos_W_mean']); varWs.append(r['W_var']); hds.append(r['H_drift_pct'])
            print(f"  {mu_E:>6.1f} {mu_B:>6.1f} {np.mean(Ls):>10.4f} {np.mean(Hs):>+10.4f} "
                  f"{np.mean(cosWs):>9.4f} {np.mean(varWs):>8.4f} {np.mean(hds):>9.3f}")

    # Analysis: is <L>/N universal (independent of mu_E, mu_B)?
    print()
    print("=" * 78)
    print("ANALYSIS: is <L>/N universal across (mu_E, mu_B)?")
    print("=" * 78)

    L_vals = [r['L_per_N'] for r in results]
    L_mean = np.mean(L_vals)
    L_std = np.std(L_vals)
    L_cv = L_std / abs(L_mean) * 100 if L_mean != 0 else 0
    print(f"  <L>/N values: mean = {L_mean:.4f}, std = {L_std:.4f}, CV = {L_cv:.2f}%")
    print(f"  Range: [{min(L_vals):.4f}, {max(L_vals):.4f}]")
    print()

    # For reference: pure XY (no gauge) gives <L>/N = beta_phi/2 = 0.030
    print(f"  Reference: pure XY no-gauge <L>/N = beta_phi/2 = {BETA_PHI/2:.4f}")
    print(f"  Measured deviation from XY: {(L_mean - BETA_PHI/2) / (BETA_PHI/2) * 100:+.1f}%")
    print()

    print("INTERPRETATION:")
    print("  - CV << 1% across (mu_E, mu_B): UNIVERSAL -> hbar candidate!")
    print("  - CV > 10%: classical continuous dependence, no hbar")
    print("  - <cos W> near 1 + W Gaussian: weak-field regime, classical LGT")
    print("  - <cos W> structured near integer multiples: quantization hint")

    with open(AUDIT / "report.json", 'w') as f:
        json.dump({
            'L': L, 'beta_phi': BETA_PHI, 'mu_phi': MU_PHI, 'T_sim': T_SIM,
            'mu_E_values': mu_E_values, 'mu_B_values': mu_B_values,
            'L_mean': L_mean, 'L_std': L_std, 'L_cv_pct': L_cv,
            'results': results,
        }, f, indent=2, default=float)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
