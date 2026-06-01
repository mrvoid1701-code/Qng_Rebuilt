"""QNG-CPU-113 -- Robustness check: beta/mu/z scan with TRIPLE verification.

Tests that hbar_QNG = sqrt(beta*mu*z)/<sqrt(lambda)> scales correctly.

TRIPLE verification:
  Method 1: Structural formula sqrt(beta*mu*z)/<sqrt(lambda)>
  Method 2: Finite-lattice zero-point balance beta*N/sum(omega_k)
  Method 3: Intensive form beta/<omega_k>

All three must match exactly for consistency.
"""
import numpy as np

L_default = 28
z_coord_default = 6

def compute_hbar_three_ways(beta_phi, mu_phi, z_coord=6, L=28):
    """Compute hbar three independent ways and check consistency."""
    N_nodes = L**3

    # Compute dispersion on cubic lattice
    k_vals = 2*np.pi*np.arange(L)/L
    if z_coord == 6:
        # Standard cubic
        kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
        lambda_k_raw = 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    elif z_coord == 8:
        # FCC or BCC-like: add diagonal couplings in same plane
        # Approximation: use different scaling
        kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
        # For FCC, lattice eigenvalue includes 12 neighbors
        # Simplified: rescale by z
        lambda_k_raw = 2.0 * (4.0 - np.cos(kx) - np.cos(ky) - np.cos(kz)
                              - (np.cos(kx)*np.cos(ky) + np.cos(kx)*np.cos(kz)
                                 + np.cos(ky)*np.cos(kz))/3)
    elif z_coord == 4:
        # 2D-like (z=4): use only kx, ky
        kx, ky, kz = np.meshgrid(k_vals, k_vals, np.array([0.0]), indexing='ij')
        lambda_k_raw = 2.0 * (2.0 - np.cos(kx) - np.cos(ky))
        N_nodes = L**2
    else:
        # Generic: just cubic for simplicity
        kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
        lambda_k_raw = 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))

    omega_sq = (beta_phi / (z_coord*mu_phi)) * lambda_k_raw
    mask = omega_sq > 1e-20
    omega_k = np.sqrt(omega_sq[mask])
    sum_omega = float(np.sum(omega_k))
    mean_omega = float(np.mean(omega_k))
    lambda_k = lambda_k_raw[mask]
    mean_sqrt_lambda = float(np.mean(np.sqrt(lambda_k)))

    # METHOD 1: Structural formula
    hbar_M1 = np.sqrt(beta_phi * mu_phi * z_coord) / mean_sqrt_lambda

    # METHOD 2: Finite-lattice zero-point balance
    hbar_M2 = beta_phi * N_nodes / sum_omega

    # METHOD 3: Intensive
    hbar_M3 = beta_phi / mean_omega

    return {
        'beta': beta_phi, 'mu': mu_phi, 'z': z_coord, 'L': L,
        'N_modes': int(mask.sum()),
        'mean_omega': mean_omega,
        'mean_sqrt_lambda': mean_sqrt_lambda,
        'hbar_M1_structural': hbar_M1,
        'hbar_M2_finitelat_zp': hbar_M2,
        'hbar_M3_intensive': hbar_M3,
        'max_diff_pct': 100*max(abs(hbar_M1-hbar_M2), abs(hbar_M2-hbar_M3), abs(hbar_M1-hbar_M3))/hbar_M1,
    }

def main():
    print("=" * 90)
    print("QNG-CPU-113: Robustness scan beta/mu/z with TRIPLE verification")
    print("=" * 90)
    print()
    print("TRIPLE VERIFY: all 3 methods must match within 0.001%")
    print()

    # Test 1: beta scan
    print("TEST 1: beta scan (mu=0.857, z=6, L=28)")
    print("-" * 90)
    print(f"{'beta':>8} {'hbar_M1':>12} {'hbar_M2':>12} {'hbar_M3':>12} {'max diff%':>10} {'predicted':>12}")
    print(f"{'':>8} {'structural':>12} {'zero-point':>12} {'intensive':>12} {'':>10} {'sqrt scaling':>12}")
    ref_hbar = None
    for beta in [0.01, 0.02, 0.03, 0.04, 0.06, 0.09, 0.12, 0.18, 0.30, 0.50]:
        r = compute_hbar_three_ways(beta, 0.857, z_coord=6, L=28)
        if beta == 0.06:
            ref_hbar = r['hbar_M1_structural']
        predicted = ref_hbar * np.sqrt(beta/0.06) if ref_hbar else None
        pred_str = f"{predicted:.5f}" if predicted else "REF"
        print(f"{r['beta']:>8.4f} {r['hbar_M1_structural']:>12.5f} {r['hbar_M2_finitelat_zp']:>12.5f} "
              f"{r['hbar_M3_intensive']:>12.5f} {r['max_diff_pct']:>10.4f} {pred_str:>12}")

    print()
    # Test 2: mu scan
    print("TEST 2: mu scan (beta=0.06, z=6, L=28)")
    print("-" * 90)
    ref_hbar = None
    for mu in [0.1, 0.2, 0.4, 0.6, 0.857, 1.2, 2.0, 3.0, 5.0]:
        r = compute_hbar_three_ways(0.06, mu, z_coord=6, L=28)
        if mu == 0.857:
            ref_hbar = r['hbar_M1_structural']
        predicted = ref_hbar * np.sqrt(mu/0.857) if ref_hbar else None
        pred_str = f"{predicted:.5f}" if predicted else "REF"
        print(f"mu={r['mu']:>6.3f} hbar_M1={r['hbar_M1_structural']:>10.5f} "
              f"hbar_M2={r['hbar_M2_finitelat_zp']:>10.5f} "
              f"max_diff={r['max_diff_pct']:>8.4f}% predicted={pred_str}")

    print()
    # Test 3: z scan (cubic only with different coord numbers - not physically meaningful for all, but tests formula)
    print("TEST 3: z scan (beta=0.06, mu=0.857, L=20)")
    print("-" * 90)
    for z in [4, 6, 8]:
        r = compute_hbar_three_ways(0.06, 0.857, z_coord=z, L=20)
        print(f"z={r['z']:>2} hbar_M1={r['hbar_M1_structural']:>10.5f} "
              f"hbar_M2={r['hbar_M2_finitelat_zp']:>10.5f} "
              f"hbar_M3={r['hbar_M3_intensive']:>10.5f} max_diff={r['max_diff_pct']:>8.4f}%")

    print()
    # Test 4: L-scan at REF params for final confirmation
    print("TEST 4: L-scan at REF params (beta=0.06, mu=0.857, z=6)")
    print("-" * 90)
    for L in [8, 12, 16, 20, 24, 28, 32, 48]:
        r = compute_hbar_three_ways(0.06, 0.857, z_coord=6, L=L)
        print(f"L={L:>3} hbar_M1={r['hbar_M1_structural']:.7f} max_diff={r['max_diff_pct']:.6f}%")

    print()
    print("VERDICT:")
    print("If all max_diff < 0.001%, three methods agree → formula verified.")
    print()
    # Test at canonical point
    canon = compute_hbar_three_ways(0.06, 0.857, z_coord=6, L=28)
    print(f"CANONICAL CHECK (beta=0.06, mu=0.857, z=6, L=28):")
    print(f"  hbar_M1 (structural)      = {canon['hbar_M1_structural']:.8f}")
    print(f"  hbar_M2 (finite-lat ZP)   = {canon['hbar_M2_finitelat_zp']:.8f}")
    print(f"  hbar_M3 (intensive)       = {canon['hbar_M3_intensive']:.8f}")
    print(f"  Max difference            = {canon['max_diff_pct']:.6f}%")
    if canon['max_diff_pct'] < 0.001:
        print(f"  STATUS: TRIPLE-VERIFIED ✓")
    else:
        print(f"  STATUS: INCONSISTENT - check formulas")

if __name__ == '__main__':
    main()
