"""QNG-CPU-091: Hessian spectrum RMT analysis (Drumul 2).

Tests whether the phi-sector Hessian of v8 around the attractor state
exhibits Wigner-Dyson level-spacing statistics (quantum-chaos signature)
or Poisson statistics (integrable).

If Wigner-Dyson: substrate has an emergent quantum-chaos scale set by
the first spacing; this is a natural candidate for h.

If Poisson: substrate is integrable at this order, no h from this route.

Structure:
  - Use small L=10 cubic lattice (N=1000 phi variables)
  - Build phi-sector Hessian at ground state (phi=0, sigma=sigma_ref):
      H_ij = (beta_R1/z) * [z * delta_ij - (1 if j in N(i) else 0)]
           + (g/2) * deficit_i^2 * cos(phi_i=0) * delta_ij
           + Channel F disorder terms
  - Diagonalize; sort eigenvalues
  - Compute unfolded nearest-neighbor spacings
  - Fit histogram to Wigner (chaotic) vs Poisson (integrable)

Then repeat at a PERTURBED state (sigma non-uniform) to break translation
symmetry; unit cell is broken, level degeneracies lift, statistics may
shift toward Wigner.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-hessian-rmt-v1"
AUDIT.mkdir(parents=True, exist_ok=True)


# v8 parameters
BETA_PHI = 0.06
BETA_R1 = BETA_PHI / 2.0
G_V_COUPLE = 0.22
SIGMA_M_REF = 0.5
GAMMA_PHI = 0.10


def cubic_lattice_neighbors(L):
    """Return (N, z=6) array of neighbor indices for L^3 periodic cubic lattice."""
    N = L ** 3
    nb = np.zeros((N, 6), dtype=int)
    for i in range(L):
        for j in range(L):
            for k in range(L):
                idx = i * L * L + j * L + k
                nb[idx, 0] = ((i + 1) % L) * L * L + j * L + k
                nb[idx, 1] = ((i - 1) % L) * L * L + j * L + k
                nb[idx, 2] = i * L * L + ((j + 1) % L) * L + k
                nb[idx, 3] = i * L * L + ((j - 1) % L) * L + k
                nb[idx, 4] = i * L * L + j * L + ((k + 1) % L)
                nb[idx, 5] = i * L * L + j * L + ((k - 1) % L)
    return nb


def phi_sector_hessian(sm, phi, nb_idx):
    """Analytic phi-sector Hessian at state (sm, phi).

    H_ij = d2 E / d phi_i d phi_j

    E_phi_A = -(beta_R1/z) * sum_{i, j in N(i)} cos(phi_i - phi_j)
    V_cp    = (g/2) * sum_i (sigma_ref - sm_i)^2 * (1 - cos phi_i)

    So:
      d2/d phi_i d phi_j (E_phi_A) = +(beta_R1/z) * 2 * cos(phi_i - phi_j)  [i != j, j in N(i)]
                                    = -(beta_R1/z) * 2 * cos(0)            [diagonal, sum over j]
        (Actually: d/dphi_i sum over j{i}..cos = sum_j sin(phi_i-phi_j); then d/dphi_j gives cos factor).

    More carefully:
      f(phi) = cos(phi_i - phi_j)
      d2 f / dphi_i dphi_j = +cos(phi_i - phi_j)
      d2 f / dphi_i^2      = -cos(phi_i - phi_j)
      d2 f / dphi_j^2      = -cos(phi_i - phi_j)

    For the sum E_phi_A = -(beta/z) * sum_i sum_{j in N(i)} cos(phi_i - phi_j), each pair (i,j)
    appears twice (once from i's perspective, once from j's). So:

    H_ij (off-diagonal, j in N(i)):
      = -2 * (beta/z) * cos(phi_i - phi_j)   [factor 2 from pair-double-counting]

    Wait — actually each ordered pair (i,j) with j in N(i) appears once in the sum. If graph is
    symmetric (j in N(i) iff i in N(j)), each unordered pair appears twice. So the sum has
    z*N/2 unique terms times 2 = z*N terms total (which matches sum_i sum_{j in N(i)} 1 = z*N).

    For the Hessian, only terms containing phi_i or phi_j contribute. Each pair contributes
    once (via (i,j)) and once again (via (j,i)), so the off-diagonal Hessian is:

      H_ij = -(beta/z) * [cos(phi_i - phi_j) from (i,j) term  +  cos(phi_j - phi_i) from (j,i) term]
           = -(beta/z) * 2 * cos(phi_i - phi_j)              [off-diagonal, j in N(i)]

    Wait, the SIGN: d2/d phi_i d phi_j [cos(phi_i - phi_j)] = +cos(...), so
      H_ij = -(beta/z) * 2 * (+cos) = -2(beta/z)cos  (off-diag)
    No, we have E_phi_A = -(beta/z) * sum_{(i,j)} cos(phi_i - phi_j), so
      d2 E / d phi_i d phi_j = -(beta/z) * [+cos + +cos] = -2(beta/z) cos

    And the diagonal:
      d2 E / d phi_i^2 = -(beta/z) * sum_{j in N(i)} [(-cos) * 2]
                       = +(beta/z) * 2 * sum_{j in N(i)} cos(phi_i - phi_j)
    (the "2" comes from pair (i,j) and (j,i) both containing phi_i^2).

    At phi = 0: cos = 1, so
      H_ij (off-diag, j in N(i)) = -2 * beta/z
      H_ii (diagonal)            = +2 * z * beta/z = +2 * beta      [sum of z cosines each =1]

    So Hessian is just -2beta/z times graph Laplacian with standard sign convention:
      H = 2 * beta/z * (z*I - A)   where A is adjacency matrix
        = 2 * beta * L_normalized   (graph Laplacian)

    Add V_couple diagonal: (g/2)*(sigma_ref - sm_i)^2 * sin(phi_i) ... at phi=0, sin=0,
    so d2/dphi_i^2 V_cp = (g/2)*(sigma_ref - sm_i)^2 * cos(phi_i) = (g/2)*deficit^2 at phi=0.

    Return: scipy-compatible dense Hessian.
    """
    N = len(phi)
    z = nb_idx.shape[1]

    H = np.zeros((N, N))

    # E_phi_A contribution
    for i in range(N):
        sum_cos_i = 0.0
        for j in nb_idx[i]:
            c = np.cos(phi[i] - phi[j])
            # Off-diagonal: -2*(beta/z)*cos (noting pair appears twice in sum)
            # But if we iterate i over all nodes and j over N(i), we ALREADY count each
            # unordered pair twice in the sum. So per-iteration off-diagonal contribution is:
            H[i, j] -= (BETA_R1 / z) * c  # this will accumulate 2x since (j,i) iter exists
            sum_cos_i += c
        # Diagonal: +2*(beta/z)*sum_cos  (since pair (i,j) gives 2 copies of phi_i^2 term)
        H[i, i] += (BETA_R1 / z) * sum_cos_i * 2

    # Actually the above has double-counted off-diagonal. Reset + clean build:
    H = np.zeros((N, N))
    for i in range(N):
        for j in nb_idx[i]:
            c = np.cos(phi[i] - phi[j])
            # Off-diagonal: each pair (i,j) contributes -2(beta/z)cos to H_ij (and H_ji)
            # But since i runs over all, the contribution from iter i adds -(beta/z)cos to H[i,j]
            # and when iter reaches j, it adds -(beta/z)cos to H[j,i]. Total H[i,j] = -2(beta/z)cos.
            # But H[i,j] and H[j,i] are SEPARATE matrix entries — so each iter accumulates once.
            H[i, j] += -(BETA_R1 / z) * 2 * c  # this is set, assuming we want full Hessian
            # Wait, we should add once per iter to avoid doubling:
        # Clean approach: iterate each pair once.
        pass

    # Clean re-implementation: iterate each unordered pair once, then
    # contribute its full pair-Hessian (both H[i,j] and H[i,i], H[j,j]).
    H = np.zeros((N, N))
    for i in range(N):
        for j in nb_idx[i]:
            if j <= i:
                continue  # process each unordered pair once
            c = np.cos(phi[i] - phi[j])
            # E_phi_A = -(beta/z) * sum_{(i,j)} cos(phi_i - phi_j)
            # pair contribution ( i < j ): -(beta/z)*cos, counted ONCE.
            # But sum_{i} sum_{j in N(i)} counts each unordered pair TWICE.
            # So E_pair = -2*(beta/z)*cos, treating pair as an oriented-neighbor sum.
            E_pair_factor = -2.0 * BETA_R1 / z
            # d2 E_pair / dphi_i dphi_j = +E_pair_factor * cos
            # d2 E_pair / dphi_i^2      = -E_pair_factor * cos
            # d2 E_pair / dphi_j^2      = -E_pair_factor * cos
            H[i, j] += E_pair_factor * c
            H[j, i] += E_pair_factor * c
            H[i, i] -= E_pair_factor * c
            H[j, j] -= E_pair_factor * c

    # V_couple contribution: V_cp = (g/2) * deficit^2 * (1 - cos phi)
    # d2/dphi_i^2 = (g/2) * deficit_i^2 * cos(phi_i)
    for i in range(N):
        deficit_i = SIGMA_M_REF - sm[i]
        H[i, i] += 0.5 * G_V_COUPLE * deficit_i * deficit_i * np.cos(phi[i])

    return H


def unfolded_spacings(eigvals):
    """Unfold eigenvalues to unit mean spacing, return nearest-neighbor spacings."""
    eigvals = np.sort(eigvals)
    # Remove rigid translation (subtract smallest)
    eigvals = eigvals - eigvals.min()
    spacings = np.diff(eigvals)
    # Local unfolding: divide each spacing by local mean (rolling window)
    window = max(10, len(spacings) // 20)
    unfolded = np.zeros_like(spacings)
    for i in range(len(spacings)):
        lo = max(0, i - window // 2)
        hi = min(len(spacings), i + window // 2 + 1)
        unfolded[i] = spacings[i] / spacings[lo:hi].mean()
    return unfolded


def wigner_surmise(s):
    """Wigner-Dyson GOE surmise."""
    return (np.pi * s / 2) * np.exp(-np.pi * s * s / 4)


def poisson_density(s):
    return np.exp(-s)


def fit_brody(spacings):
    """Fit Brody distribution: P(s) = (1+q)*beta*s^q * exp(-beta*s^(q+1))
    where beta = Gamma((q+2)/(q+1))^(q+1). q=0 Poisson, q=1 Wigner."""
    from scipy.optimize import minimize_scalar
    from scipy.special import gamma as G

    def neg_log_like(q):
        if q < -0.999 or q > 2:
            return 1e10
        b = G((q + 2) / (q + 1)) ** (q + 1)
        logp = np.log((1 + q) * b) + q * np.log(spacings + 1e-12) - b * spacings ** (q + 1)
        return -np.sum(logp)

    r = minimize_scalar(neg_log_like, bounds=(-0.5, 1.5), method="bounded")
    return float(r.x), float(-r.fun)


def chi2_compare(unfolded, bins=30):
    """Compute chi^2 vs Wigner and Poisson."""
    hist, edges = np.histogram(unfolded, bins=bins, range=(0, 4), density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    bin_w = edges[1] - edges[0]

    pred_w = wigner_surmise(centers) * bin_w
    pred_p = poisson_density(centers) * bin_w
    obs = hist * bin_w

    nonzero = (pred_w > 1e-6) & (pred_p > 1e-6)
    chi2_w = float(np.sum((obs[nonzero] - pred_w[nonzero]) ** 2 / pred_w[nonzero]))
    chi2_p = float(np.sum((obs[nonzero] - pred_p[nonzero]) ** 2 / pred_p[nonzero]))
    return chi2_w, chi2_p, centers, hist


def test_state(label, L, sm_field, phi_field, nb_idx, results):
    print(f"\n--- {label} ---")
    H = phi_sector_hessian(sm_field, phi_field, nb_idx)
    eigvals = eigh(H, eigvals_only=True)

    # Drop near-zero modes (Goldstone of phi symmetry)
    mask = eigvals > 1e-8 * eigvals.max()
    eigvals_pos = eigvals[mask]

    print(f"  N = {L**3}, eigenvalue range = [{eigvals.min():.4g}, {eigvals.max():.4g}]")
    print(f"  Positive eigenvalues: {mask.sum()} / {len(eigvals)}")
    print(f"  Goldstone (near-zero) modes: {(~mask).sum()}")

    if mask.sum() < 100:
        print("  Not enough eigenvalues for RMT test (need >=100)")
        return

    unfolded = unfolded_spacings(eigvals_pos)
    # Drop extremes (unfolding artefacts)
    unfolded = unfolded[(unfolded > 1e-3) & (unfolded < 5)]

    chi2_w, chi2_p, centers, hist = chi2_compare(unfolded)
    q, logL = fit_brody(unfolded)

    print(f"  chi^2 vs Wigner: {chi2_w:.4f}")
    print(f"  chi^2 vs Poisson: {chi2_p:.4f}")
    print(f"  Brody fit q = {q:.3f}  (0=Poisson, 1=Wigner)")
    print(f"  Verdict: {'WIGNER (chaos)' if q > 0.7 else 'POISSON (integrable)' if q < 0.3 else 'INTERMEDIATE'}")
    print(f"  Mean spacing s = {unfolded.mean():.4f} (should be ~1 after unfolding)")

    results[label] = {
        "N": int(L ** 3),
        "n_positive": int(mask.sum()),
        "n_goldstone": int((~mask).sum()),
        "eig_min": float(eigvals.min()),
        "eig_max": float(eigvals.max()),
        "chi2_wigner": chi2_w,
        "chi2_poisson": chi2_p,
        "brody_q": q,
        "mean_unfolded_s": float(unfolded.mean()),
        "hist_centers": centers.tolist(),
        "hist": hist.tolist(),
    }


def main():
    L = 10
    N = L ** 3
    nb_idx = cubic_lattice_neighbors(L)
    print(f"QNG-CPU-091: Hessian spectrum RMT analysis, L={L} N={N}")
    print("=" * 70)

    results = {}

    # Test 1: exact ground state (uniform field)
    phi_0 = np.zeros(N)
    sm_0 = np.full(N, SIGMA_M_REF)
    test_state("Ground state (phi=0, sigma=ref)", L, sm_0, phi_0, nb_idx, results)

    # Test 2: ring-like state — plug in a Gaussian sigma_m deficit at center
    cx = cy = cz = L // 2
    R = 4
    sm_ring = np.full(N, SIGMA_M_REF)
    for i in range(L):
        for j in range(L):
            for k in range(L):
                idx = i * L * L + j * L + k
                r = np.sqrt((i - cx) ** 2 + (j - cy) ** 2)
                z_dist = k - cz
                # Ring deficit: peak at torus (r=R, z=0)
                s = np.exp(-((r - R) ** 2 + z_dist ** 2) / 2.0)
                sm_ring[idx] = SIGMA_M_REF - 0.3 * s
    phi_ring = np.random.default_rng(42).uniform(-0.05, 0.05, N)
    test_state("Ring-perturbed state", L, sm_ring, phi_ring, nb_idx, results)

    # Test 3: random phi (hot state, max symmetry breaking)
    phi_rand = np.random.default_rng(123).uniform(-np.pi, np.pi, N)
    sm_rand = SIGMA_M_REF + 0.1 * np.random.default_rng(456).normal(size=N)
    test_state("Random hot state", L, sm_rand, phi_rand, nb_idx, results)

    with open(AUDIT / "report.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nReport: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
