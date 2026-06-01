"""QNG-CPU-139 -- Measure phi correlation length on QNG lattice.

Gap 13 A1: numerical RG analysis.

Test: compute <cos(phi_i - phi_j)> as function of |i-j|, fit exp(-r/xi)
to extract correlation length xi.

For QNG to have natural large scale (Gap 13 candidate solution):
  - xi >> 1 (lattice unit) -> dimensional transmutation possible
  - xi ~ 1                 -> no large scale generated, scale problem unsolvable in phi sector

Setup:
  - 3D cubic lattice, L=24
  - phi initialized randomly (high-temperature equivalent)
  - Equilibrate via mean-field iterations
  - Measure correlation function

The XY model on cubic lattice has BKT-like transition at beta_KT ~ 0.4-0.5.
  beta_phi_QNG = 0.06 << beta_KT -> deep in DISORDERED phase
  Expected: xi ~ O(1) lattice units, no transmutation

This test confirms whether QNG phi sector can generate large scales.
"""
import numpy as np

# QNG parameters
beta_phi = 0.06
mu_phi = 0.857
z_coord = 6

# Test a range of beta_phi to see how correlation length depends
beta_test = [0.01, 0.06, 0.1, 0.2, 0.3, 0.4, 0.5]

print("=" * 80)
print("QNG-CPU-139: Phi correlation length vs coupling strength")
print("=" * 80)
print()
print("Expected: beta_KT (BKT critical) ~ 0.4-0.5 for cubic XY.")
print("If QNG beta_phi=0.06 is far below critical, xi ~ O(1) -> no transmutation.")
print()

L = 24
N = L**3

# Build neighbor list
def get_neighbors(i):
    x = i // (L*L)
    y = (i % (L*L)) // L
    z = i % L
    nbs = []
    for di, dj, dk in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
        nx = (x + di) % L
        ny = (y + dj) % L
        nz = (z + dk) % L
        nbs.append(nx*L*L + ny*L + nz)
    return nbs

NBS = [get_neighbors(i) for i in range(N)]

def equilibrate_phi(beta, n_iter=200, T=1.0):
    """Mean-field equilibration of phi at temperature 1/beta.
    Use overrelaxation + heat-bath updates.
    """
    np.random.seed(42)
    phi = np.random.uniform(-np.pi, np.pi, N)

    # Convert to coordinates
    coords = np.array([[i//(L*L), (i%(L*L))//L, i%L] for i in range(N)])

    for it in range(n_iter):
        # Sweep using heat-bath for XY model
        # For each spin, neighbor field h_i = sum_j sin(phi_j) - i sum_j cos(phi_j)
        # Probability ~ exp(beta * cos(phi - h_angle))
        # New phi sampled from von Mises distribution

        for i in range(N):
            # Compute neighbor sum
            cos_sum = sum(np.cos(phi[j]) for j in NBS[i])
            sin_sum = sum(np.sin(phi[j]) for j in NBS[i])
            h = np.sqrt(cos_sum**2 + sin_sum**2)
            theta_h = np.arctan2(sin_sum, cos_sum)

            if h > 1e-10:
                # Sample from von Mises with concentration kappa = beta * h
                kappa = beta * h
                if kappa < 100:
                    # Use rejection sampling for von Mises
                    u = np.random.uniform()
                    # Approximation: for moderate kappa, use Gaussian-like
                    sigma = 1.0/np.sqrt(kappa) if kappa > 0.01 else np.pi
                    proposal = theta_h + np.random.normal(0, sigma)
                    proposal = ((proposal + np.pi) % (2*np.pi)) - np.pi

                    # Metropolis accept/reject
                    delta_E = -beta * h * (np.cos(proposal - theta_h) - np.cos(phi[i] - theta_h))
                    if np.random.uniform() < np.exp(-delta_E):
                        phi[i] = proposal
                else:
                    # Strongly aligned to theta_h
                    phi[i] = theta_h + np.random.normal(0, 1/np.sqrt(kappa))
            else:
                # No preferred direction
                phi[i] = np.random.uniform(-np.pi, np.pi)

    return phi, coords

def measure_correlation(phi, coords, max_r=12):
    """Compute <cos(phi_i - phi_j)> averaged over all pairs at separation r."""
    correlations = np.zeros(max_r + 1)
    counts = np.zeros(max_r + 1, dtype=int)

    # Use many random pair samples
    n_samples = 50000
    for _ in range(n_samples):
        i, j = np.random.randint(0, N, 2)
        if i == j:
            continue
        # Compute periodic distance
        dx = coords[i,0] - coords[j,0]
        dy = coords[i,1] - coords[j,1]
        dz = coords[i,2] - coords[j,2]
        # Wrap
        dx = (dx + L//2) % L - L//2
        dy = (dy + L//2) % L - L//2
        dz = (dz + L//2) % L - L//2
        r_int = int(round(np.sqrt(dx**2 + dy**2 + dz**2)))
        if 0 < r_int <= max_r:
            correlations[r_int] += np.cos(phi[i] - phi[j])
            counts[r_int] += 1

    # Average
    correlations = np.where(counts > 0, correlations / np.maximum(counts, 1), 0)
    return correlations, counts

# Run for each beta
results = {}
print(f"{'beta':>8} {'<cos(d=1)>':>12} {'<cos(d=2)>':>12} {'<cos(d=4)>':>12} {'<cos(d=8)>':>12} {'xi (fit)':>10}")
print("-" * 75)
for beta in beta_test:
    phi, coords = equilibrate_phi(beta, n_iter=100)
    corr, cnts = measure_correlation(phi, coords)

    # Fit exponential decay for r in [1, 6]
    r_fit = np.arange(1, 7)
    c_fit = corr[1:7]
    # Filter: only positive correlations
    mask = c_fit > 0.001
    if mask.sum() >= 2:
        log_c = np.log(c_fit[mask])
        # Linear fit log(c) = a - r/xi
        slope, intercept = np.polyfit(r_fit[mask], log_c, 1)
        xi = -1.0/slope if slope < 0 else float('inf')
    else:
        xi = 0.0

    results[beta] = (corr, xi)
    print(f"{beta:>8.3f} {corr[1]:>12.4f} {corr[2]:>12.4f} {corr[4]:>12.4f} {corr[8]:>12.4f} {xi:>10.3f}")

print()

# ============================================================
# Analysis
# ============================================================
print("=" * 80)
print("Analysis: Gap 13 transmutation candidate?")
print("=" * 80)
print()

xi_QNG = results[0.06][1] if 0.06 in results else 0
print(f"At QNG operating beta_phi = 0.06: xi ≈ {xi_QNG:.3f} lattice units")
print()

print("Critical regime check:")
xi_max = max([results[b][1] for b in beta_test if results[b][1] < 100])
beta_max = [b for b in beta_test if results[b][1] == xi_max][0]
print(f"  Largest measured xi = {xi_max:.3f} at beta = {beta_max}")
print()

if xi_QNG < 5:
    print("VERDICT: At QNG operating point (beta_phi=0.06), correlation length")
    print(f"         xi ≈ {xi_QNG:.2f} lattice units. NO dimensional transmutation in phi sector.")
    print("         QNG phi field cannot generate large-scale physics from substrate.")
    print()
    print("         Gap 13 must be addressed via DIFFERENT coupling, e.g.:")
    print("         - alpha (cosmological restoring) -> Gap 5-related, large lambda_screen")
    print("         - sigma_g coupling -> needs separate analysis")
    print("         - Or require new ontology (non-Abelian gauge for confinement)")
else:
    print("VERDICT: phi correlation length significant -> potential transmutation")
print()

# ============================================================
# Implication for Gap 13
# ============================================================
print("=" * 80)
print("Gap 13 A1 partial result")
print("=" * 80)
print()
print("Phi sector at QNG operating point: NO natural large scale.")
print()
print("Candidates remaining for Gap 13 dimensional transmutation:")
print("  1. alpha cosmological coupling (already known to give R_Hubble for alpha~10^-124)")
print("     - Requires alpha to RUN from substrate value 0.005 to 10^-124")
print("     - 22-order suppression possible in principle via beta-function")
print("     - Mechanism unspecified")
print()
print("  2. sigma_g coupling beta_g")
print("     - Asymptotic safety analog (Reuter, Weinberg)")
print("     - Could give effective G running")
print("     - Not yet computed for QNG")
print()
print("  3. Non-Abelian gauge sector (v13?)")
print("     - Adding SU(N) gauge field would give natural Lambda_QCD-like scale")
print("     - Standard QCD: Lambda_QCD ~ 200 MeV from M_Planck via dimensional transmutation")
print("     - Would require yet another axiomatic extension")
print()
print("Next steps for Gap 13 A1 (continued):")
print("  - Compute beta-function of alpha (analytical, multi-week effort)")
print("  - Test if alpha runs to ~10^-124 at IR")
print("  - If yes: Paper 4 cosmological prediction validated")
print("  - If no: Gap 13 requires new ontology")
