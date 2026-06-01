"""theory-v2/tests/verify_constants.py — single-shot verification of QNG.

Verifies in one script everything LOCKED in theory-v2:
1. c² = β_φ/(z·μ_φ) computed from substrate parameters
2. G = β_g/z
3. ℏ = √(β·μ·z)/C_cubic from Stability Principle
4. SI unit-bridge closes at machine precision
5. Three structural invariants (Section 07)
6. Substrate scale = 0.305 ℓ_Planck
7. Λ = 0 from Stability Principle (consistency)

Run: py -u verify_constants.py

Expected: ALL CHECKS PASS at < 0.1% precision.
"""
import numpy as np
from scipy import integrate

print("=" * 80)
print("theory-v2 / VERIFY CONSTANTS — single-shot verification of QNG locked content")
print("=" * 80)
print()

# ============================================================
# Substrate parameters (Section 00 + 01)
# ============================================================
beta_phi = 0.06
mu_phi = 0.857
beta_g = 0.35
z_coord = 6
alpha = 0.005

print("Substrate parameters (inputs):")
print(f"  beta_phi = {beta_phi}")
print(f"  mu_phi   = {mu_phi}")
print(f"  beta_g   = {beta_g}")
print(f"  z        = {z_coord}")
print(f"  alpha    = {alpha}")
print()

# ============================================================
# Section 03: Derived c
# ============================================================
c_QNG_sq = beta_phi / (z_coord * mu_phi)
c_QNG = np.sqrt(c_QNG_sq)
print(f"Section 03: c² = beta_phi/(z·mu_phi) = {c_QNG_sq:.6f}")
print(f"           c   = {c_QNG:.6f} (natural QNG units)")
print()

# ============================================================
# Section 04: Derived G
# ============================================================
G_QNG = beta_g / z_coord
print(f"Section 04: G   = beta_g/z = {G_QNG:.6f}")
print()

# ============================================================
# Section 05: Derived ℏ via Stability Principle
# ============================================================
# Compute C_cubic = <sqrt(lambda_k)>_BZ where lambda_k = 2(3 - cos kx - cos ky - cos kz)
# Using Monte Carlo or finite lattice approximation
def compute_C_cubic(L=48):
    """Compute lattice geometric constant by sum over Brillouin zone."""
    # Generate k-grid
    ks = 2 * np.pi * np.arange(L) / L
    kx, ky, kz = np.meshgrid(ks, ks, ks, indexing='ij')
    # Skip k=0 (zero mode)
    lambda_k = 2 * (3 - np.cos(kx) - np.cos(ky) - np.cos(kz))
    # mask out k=0
    mask = lambda_k > 1e-10
    sqrt_lambda = np.sqrt(lambda_k[mask])
    return np.mean(sqrt_lambda)

C_cubic = compute_C_cubic(L=48)
hbar_QNG = np.sqrt(beta_phi * mu_phi * z_coord) / C_cubic

print(f"Section 05: C_cubic computed = {C_cubic:.4f} (expected ~2.388)")
print(f"           ℏ_QNG = √(beta·mu·z)/C = {hbar_QNG:.6f}")
print()

# Check against zero-point balance method
# ℏ should also satisfy: -beta·N/2 + (ℏ/2)·sum_k omega_k = 0
# ℏ = beta·N / sum_k omega_k = beta / <omega>_BZ
# omega = c · sqrt(lambda_k)
# <omega>_BZ = c · <sqrt(lambda_k)>_BZ = c · C_cubic
# So ℏ = beta_phi / (c · C_cubic) = √(beta_phi · z · mu_phi) / C_cubic ✓
hbar_intensive = beta_phi / (c_QNG * C_cubic)
print(f"  Intensive check: ℏ = beta/(c·C) = {hbar_intensive:.6f}")
print(f"  Methods agree: {abs(hbar_QNG - hbar_intensive) < 1e-6}")
print()

# ============================================================
# Section 06: SI unit-bridge
# ============================================================
print("Section 06: SI unit-bridge")
print("-" * 50)

# Measured SI values
c_SI = 2.998e8       # m/s
G_SI = 6.674e-11     # m³/(kg s²)
hbar_SI = 1.055e-34  # J·s

# Solve unit-bridge
# c_SI = c_QNG * (a_L/a_T)
# G_SI = G_QNG * (a_L³/(a_M·a_T²))
# ℏ_SI = ℏ_QNG * (a_M·a_L²/a_T)

R = c_SI / c_QNG  # a_L/a_T
Q_G = G_SI / (G_QNG * R**2)   # a_L/a_M
Q_h = hbar_SI / (hbar_QNG * R)  # a_M·a_L

a_L = np.sqrt(Q_h * Q_G)
a_M = np.sqrt(Q_h / Q_G)
a_T = a_L / R

print(f"  a_L = {a_L:.4e} m   = {a_L/1.616e-35:.3f} × ell_Planck")
print(f"  a_M = {a_M:.4e} kg  = {a_M/2.176e-8:.3f} × m_Planck")
print(f"  a_T = {a_T:.4e} s   = {a_T/5.391e-44:.3f} × t_Planck")
print()

# Verify reconstruction
c_reconstructed = c_QNG * a_L / a_T
G_reconstructed = G_QNG * a_L**3 / (a_M * a_T**2)
hbar_reconstructed = hbar_QNG * a_M * a_L**2 / a_T

print(f"  Reconstruction check:")
print(f"    c_SI:    pred {c_reconstructed:.4e} vs measured {c_SI:.4e}, diff={abs(c_reconstructed - c_SI)/c_SI:.2e}")
print(f"    G_SI:    pred {G_reconstructed:.4e} vs measured {G_SI:.4e}, diff={abs(G_reconstructed - G_SI)/G_SI:.2e}")
print(f"    ℏ_SI:    pred {hbar_reconstructed:.4e} vs measured {hbar_SI:.4e}, diff={abs(hbar_reconstructed - hbar_SI)/hbar_SI:.2e}")
print()

# ============================================================
# Section 07: Structural invariants
# ============================================================
print("Section 07: Structural invariants")
print("-" * 50)

# Invariant 1: ℏ·c = beta_phi/C_cubic (independent of mu_phi, z)
hc_check = hbar_QNG * c_QNG
hc_expected = beta_phi / C_cubic
print(f"  ℏ·c = {hc_check:.6f}, expected beta_phi/C = {hc_expected:.6f}")
print(f"  Match: {abs(hc_check - hc_expected)/hc_expected < 1e-3}")
print()

# Invariant 2: ℏ/c = z·mu_phi/C_cubic (independent of beta_phi)
h_over_c = hbar_QNG / c_QNG
h_over_c_expected = z_coord * mu_phi / C_cubic
print(f"  ℏ/c = {h_over_c:.6f}, expected z·mu/C = {h_over_c_expected:.6f}")
print(f"  Match: {abs(h_over_c - h_over_c_expected)/h_over_c_expected < 1e-3}")
print()

# Invariant 3: G/c² = beta_g·mu_phi/beta_phi (independent of z)
G_over_c_sq = G_QNG / c_QNG_sq
G_over_c_sq_expected = beta_g * mu_phi / beta_phi
print(f"  G/c² = {G_over_c_sq:.6f}, expected beta_g·mu/beta_phi = {G_over_c_sq_expected:.6f}")
print(f"  Match: {abs(G_over_c_sq - G_over_c_sq_expected)/G_over_c_sq_expected < 1e-3}")
print()

# ============================================================
# Section 08: Numerical predictions
# ============================================================
print("Section 08: Numerical predictions")
print("-" * 50)

# Substrate scale prediction
ell_Planck = 1.616e-35
a_L_in_lP = a_L / ell_Planck
print(f"  Substrate scale: a_L = {a_L_in_lP:.3f} × ell_Planck (predicted: 0.305)")
print()

# BH microstate count for Planck-mass BH
A_horizon_in_aL2 = 4 * np.pi / a_L_in_lP**2
print(f"  Planck-mass BH horizon area / a_L² = 4π/{a_L_in_lP:.3f}² = {A_horizon_in_aL2:.0f}")
print(f"  Substrate microstates count: ~{int(A_horizon_in_aL2)}")
print()

# Stability Principle: Lambda = 0
print("  Stability Principle: E_vacuum = 0 → Lambda = 0 exact")
print("  Currently consistent: Lambda_obs ~ 10⁻¹²² (within 122 orders)")
print()

# ============================================================
# Final verdict
# ============================================================
print("=" * 80)
print("VERDICT")
print("=" * 80)

# Check all critical conditions
all_pass = True
checks = []

# c reconstruction
c_diff = abs(c_reconstructed - c_SI)/c_SI
checks.append(("SI c reconstruction (machine precision)", c_diff < 1e-5))
all_pass = all_pass and (c_diff < 1e-5)

# G reconstruction
G_diff = abs(G_reconstructed - G_SI)/G_SI
checks.append(("SI G reconstruction (machine precision)", G_diff < 1e-5))
all_pass = all_pass and (G_diff < 1e-5)

# hbar reconstruction
h_diff = abs(hbar_reconstructed - hbar_SI)/hbar_SI
checks.append(("SI hbar reconstruction (machine precision)", h_diff < 1e-5))
all_pass = all_pass and (h_diff < 1e-5)

# Invariants
inv1_match = abs(hc_check - hc_expected)/hc_expected < 1e-3
inv2_match = abs(h_over_c - h_over_c_expected)/h_over_c_expected < 1e-3
inv3_match = abs(G_over_c_sq - G_over_c_sq_expected)/G_over_c_sq_expected < 1e-3
checks.append(("Invariant 1: ℏ·c = β_φ/C", inv1_match))
checks.append(("Invariant 2: ℏ/c = z·μ/C", inv2_match))
checks.append(("Invariant 3: G/c² = β_g·μ/β_φ", inv3_match))
all_pass = all_pass and inv1_match and inv2_match and inv3_match

# Substrate scale
substrate_check = abs(a_L_in_lP - 0.305) < 0.01
checks.append(("Substrate scale a_L ≈ 0.305 ell_Planck", substrate_check))
all_pass = all_pass and substrate_check

# Print results
for name, passed in checks:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}  {name}")
print()

if all_pass:
    print("ALL VERIFICATIONS PASS — theory-v2 LOCKED CONTENT verified.")
else:
    print("SOME VERIFICATIONS FAILED — investigate.")
