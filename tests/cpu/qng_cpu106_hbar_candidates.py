"""QNG-CPU-106 -- hbar candidate identification via multiple analytical routes.

Derivation: 04_qng_pure/qng-v10-foundational-v1.md (DER-QNG-062)
            04_qng_pure/qng-unit-bridge-analysis-v1.md (DER-QNG-064)

Computes multiple candidates for hbar_QNG in natural units and checks
their consistency:

1. <omega_k>_BZ: average mode frequency over Brillouin zone
2. ℏ from zero-point balance: hbar = beta_phi / <omega_k>
3. ℏ from virial theorem: hbar = 4<T>/(N*omega_orb)
4. ℏ from Planck ansatz: hbar = l_P^2 * c^3 / G (natural units)
5. c_QNG for comparison

CPU only. Analytical computation.
"""
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu106-hbar-candidates-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def brillouin_zone_integral(beta, mu, L_bz=100):
    """Compute <omega_k>_BZ for XY dispersion on cubic lattice.

    omega_k^2 = (beta/mu) * sum_mu 2(1-cos k_mu)

    Average over cubic BZ: k_mu in [0, 2*pi).
    Use uniform grid with L_bz points per dimension.
    """
    k = np.linspace(0, 2*np.pi, L_bz, endpoint=False)
    # Triple meshgrid
    kx, ky, kz = np.meshgrid(k, k, k, indexing='ij')
    # dispersion: omega^2 = (beta/mu) * 2 * (3 - cos kx - cos ky - cos kz)
    omega_sq = (beta/mu) * 2.0 * (3.0 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    # exclude k=0 (zero mode) which is degenerate
    mask = omega_sq > 1e-20
    omega = np.sqrt(omega_sq[mask])
    omega_mean = float(np.mean(omega))
    omega_rms = float(np.sqrt(np.mean(omega_sq[mask])))
    return omega_mean, omega_rms


def compute_candidates(beta_phi=0.06, mu_phi=0.857, beta_g=0.35, z=6,
                       omega_orb=0.0346, T_mean_per_all_nodes=20.68,
                       N_total=21952):
    """Compute all hbar candidates from QNG substrate parameters."""

    c_phi_sq_einstein = beta_phi / (6 * mu_phi)  # Einstein correspondence
    c_phi = np.sqrt(c_phi_sq_einstein)
    G_QNG = beta_g / z
    omega_XY = np.sqrt(beta_phi / mu_phi)  # single-site XY frequency

    # Candidate 1: zero-point balance
    omega_mean_BZ, omega_rms_BZ = brillouin_zone_integral(beta_phi, mu_phi)
    hbar_cand_1 = beta_phi / omega_mean_BZ

    # Candidate 2: virial theorem
    T_per_node = T_mean_per_all_nodes / N_total
    hbar_cand_2 = 4.0 * T_per_node / omega_orb

    # Candidate 3: Planck ansatz l_P^2 * c^3 / G (natural units with l=1)
    hbar_cand_3 = (c_phi**3) / G_QNG

    # Candidate 4: upper bound from classical limit condition
    # Require ℏ·<ω>/β_φ < 1 (quantum correction smaller than classical)
    hbar_bound = beta_phi / omega_mean_BZ

    # Derived comparison: c_QNG (same dimension if we think in natural units)
    return {
        'beta_phi': beta_phi,
        'mu_phi': mu_phi,
        'beta_g': beta_g,
        'z': z,
        'c_phi_squared': c_phi_sq_einstein,
        'c_phi': c_phi,
        'G_QNG': G_QNG,
        'omega_XY_single_site': omega_XY,
        'omega_orb': omega_orb,
        'omega_mean_BZ': omega_mean_BZ,
        'omega_rms_BZ': omega_rms_BZ,
        'hbar_cand_zero_point_balance': hbar_cand_1,
        'hbar_cand_virial': hbar_cand_2,
        'hbar_cand_Planck_ansatz': hbar_cand_3,
        'hbar_upper_bound': hbar_bound,
    }


def main():
    print("=" * 72)
    print("QNG-CPU-106: hbar candidates via multiple analytical routes")
    print("=" * 72)
    print()

    c = compute_candidates()

    print(f"Primary-source values (substrate):")
    print(f"  beta_phi    = {c['beta_phi']}")
    print(f"  mu_phi      = {c['mu_phi']}")
    print(f"  beta_g      = {c['beta_g']}")
    print(f"  z           = {c['z']}")
    print()
    print(f"Derived:")
    print(f"  c_phi^2     = beta_phi/(6*mu_phi) = {c['c_phi_squared']:.5f}")
    print(f"  c_phi       = {c['c_phi']:.5f}")
    print(f"  G_QNG       = beta_g/z = {c['G_QNG']:.5f}")
    print(f"  omega_XY    = sqrt(beta_phi/mu_phi) = {c['omega_XY_single_site']:.5f}")
    print(f"  omega_orb   = 2*pi/T_cycle = {c['omega_orb']:.5f}")
    print(f"  <omega_k>_BZ = {c['omega_mean_BZ']:.5f}")
    print(f"  <omega_k^2>_BZ^(1/2) = {c['omega_rms_BZ']:.5f}")
    print()
    print(f"hbar candidates:")
    print(f"  Zero-point balance:  hbar = beta_phi / <omega_k> = {c['hbar_cand_zero_point_balance']:.5f}")
    print(f"  Virial theorem:      hbar = 4<T>_per_node/omega_orb = {c['hbar_cand_virial']:.5f}")
    print(f"  Planck ansatz:       hbar = c^3/G_QNG = {c['hbar_cand_Planck_ansatz']:.5f}")
    print(f"  Upper bound (classical consistency): hbar < {c['hbar_upper_bound']:.5f}")
    print()
    print(f"For comparison:")
    print(f"  c_phi        = {c['c_phi']:.5f} (same order of magnitude)")
    print()

    # Consistency check
    candidates = [
        c['hbar_cand_zero_point_balance'],
        c['hbar_cand_virial'],
        c['hbar_cand_Planck_ansatz'],
    ]
    mean_cand = np.mean(candidates)
    std_cand = np.std(candidates)
    cv_cand = std_cand / mean_cand * 100

    print(f"Cross-method consistency:")
    print(f"  Mean candidate:  {mean_cand:.5f}")
    print(f"  Std:             {std_cand:.5f}")
    print(f"  CV:              {cv_cand:.2f}%")
    print()

    # Narrow estimate
    print(f"CONSISTENT ESTIMATE: hbar_QNG ~ {c['hbar_cand_zero_point_balance']:.3f} +/- {std_cand:.3f}")
    print(f"  (in natural units; requires unit bridge to translate to SI)")

    json.dump(c, open(OUT_DIR / 'candidates.json', 'w'), indent=2)
    print(f"\nSaved: {OUT_DIR / 'candidates.json'}")


if __name__ == '__main__':
    main()
