"""QNG-CPU-108 -- Verify hbar_QNG = 0.233 is L-independent (thermodynamic limit check).

Self-verified: computes sum over lattice k-modes exactly for multiple L values.

If hbar_QNG = beta_phi / <omega_k> converges to a specific value as L increases,
then hbar is a substrate-intrinsic constant. If it diverges or depends strongly
on L, the candidate A formula is wrong.
"""
import numpy as np

beta_phi = 0.06
mu_phi = 0.857
z_coord = 6

def compute_hbar_QNG(L):
    """Compute hbar = beta_phi / <omega_k>_lattice for cubic L^3."""
    k_vals = 2 * np.pi * np.arange(L) / L
    kx, ky, kz = np.meshgrid(k_vals, k_vals, k_vals, indexing='ij')
    # omega^2 = (beta_phi/(z*mu_phi)) * 2 * [3 - sum_mu cos(k_mu)]
    omega_sq = (beta_phi / (z_coord * mu_phi)) * 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    # Exclude k=0 zero mode (ω=0)
    mask = omega_sq > 1e-20
    omega_k = np.sqrt(omega_sq[mask])
    N_modes = len(omega_k)
    N_nodes = L**3
    sum_omega = float(np.sum(omega_k))
    mean_omega = float(np.mean(omega_k))

    # Zero-point balance
    hbar_zp = beta_phi * N_nodes / sum_omega
    # Intensive formula
    hbar_intensive = beta_phi / mean_omega

    # Structural formula
    # hbar = sqrt(beta*mu*z) / <sqrt(lambda_k)>
    lambda_k_vals = 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    sqrt_lambda_mean = float(np.mean(np.sqrt(lambda_k_vals[mask])))
    hbar_structural = np.sqrt(beta_phi * mu_phi * z_coord) / sqrt_lambda_mean

    return {
        'L': L,
        'N_nodes': N_nodes,
        'N_modes': N_modes,
        'sum_omega': sum_omega,
        'mean_omega': mean_omega,
        'hbar_zp': hbar_zp,
        'hbar_intensive': hbar_intensive,
        'hbar_structural': hbar_structural,
        'sqrt_lambda_mean': sqrt_lambda_mean,
    }


def main():
    print("=" * 80)
    print("QNG-CPU-108: L-scan for hbar_QNG = beta_phi / <omega_k> thermodynamic limit")
    print("=" * 80)
    print()
    print(f"{'L':>4} {'N_modes':>10} {'<omega_k>':>10} {'hbar_zp':>10} {'hbar_intrinsic':>14} {'<sqrt(lambda)>':>15}")
    print("-" * 80)

    results = []
    for L in [4, 6, 8, 12, 16, 20, 24, 28, 32, 48, 64, 96]:
        r = compute_hbar_QNG(L)
        results.append(r)
        print(f"{r['L']:>4} {r['N_modes']:>10} {r['mean_omega']:>10.6f} "
              f"{r['hbar_zp']:>10.6f} {r['hbar_intensive']:>14.6f} {r['sqrt_lambda_mean']:>15.6f}")

    # Compare to thermodynamic limit (extrapolation)
    hbar_large_L = [r['hbar_zp'] for r in results if r['L'] >= 32]
    mean_hbar_large = np.mean(hbar_large_L)
    std_hbar_large = np.std(hbar_large_L)
    print()
    print(f"Thermodynamic limit estimate (L >= 32):")
    print(f"  mean hbar = {mean_hbar_large:.6f}")
    print(f"  std       = {std_hbar_large:.6f}")
    print(f"  CV        = {std_hbar_large/mean_hbar_large*100:.3f}%")

    # Finite-size scaling
    print()
    print("Finite-size correction (hbar_L - hbar_inf):")
    hbar_inf = results[-1]['hbar_zp']
    for r in results:
        diff_pct = (r['hbar_zp'] - hbar_inf) / hbar_inf * 100
        print(f"  L={r['L']:>3}: hbar={r['hbar_zp']:.6f}, deviation from L={results[-1]['L']}: {diff_pct:+.3f}%")

    # Check: hbar_structural should equal hbar_intensive
    print()
    print("Self-check: hbar_structural == hbar_intensive?")
    r = results[-1]
    ratio = r['hbar_structural'] / r['hbar_intensive']
    print(f"  L={r['L']}: hbar_intensive = {r['hbar_intensive']:.6f}")
    print(f"              hbar_structural = {r['hbar_structural']:.6f}")
    print(f"              ratio = {ratio:.6f}")
    print(f"              (Expected 1.0 if formulas consistent)")


if __name__ == '__main__':
    main()
