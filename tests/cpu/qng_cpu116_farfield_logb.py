"""QNG-CPU-116 -- Far-field deflection: test log(b) vs 1/b in v10.

Background:
  Einstein 1911 (before GR): predicted light bending at 1/b (Newtonian
  approximation). Einstein 1915 (full GR): predicted log(b) + saturation.
  Observed (1919 eclipse): close to 1/b at small b, logarithmic at large b.

  DER-QNG-044 tested far-field falloff of gravitational deflection:
    - v8 measured ratio ≈ 0.96 vs predicted 2.0 for 1/b → RULED OUT 1/b
    - Did NOT confirm log(b) (test not designed for it)

Test v10:
  Model gravitational potential from ring in v10 at large distance b.
  Compare asymptotic falloff with log(b) (GR prediction) and 1/b (1911).

Analytical approach:
  - In v10, sigma_g deviation from sigma_g_ref propagates as phi wave
  - Far from source: Phi_gravitational ~ G * M / r (standard Newton)
  - But in discrete lattice with finite screening length, we get
    Phi ~ M * exp(-r/lambda_screen) / r (Yukawa-type falloff)
  - For r << lambda_screen: Phi ~ M/r (classical)
  - For r >> lambda_screen: Phi ~ exponential decay

  Screening length: lambda_screen = sqrt(beta_g/(z*alpha)) = sqrt(0.35/(6*0.005))
                                 = sqrt(11.67) = 3.42 (natural units)

  Actually, from qng-poisson-assembly-v1.md:
    lambda_screen = sqrt(beta/(z*alpha))

Deflection angle from Newtonian formula:
  dtheta/db = d/db(Phi integrated along path) ~ Phi(b) for static potential
  theta(b) = integral of gradient across impact parameter b
"""
import numpy as np

# Parameters
beta_phi = 0.06
beta_g = 0.35
mu_phi = 0.857
alpha = 0.005
z_coord = 6

# Derived screening length
lambda_screen = np.sqrt(beta_g / (z_coord * alpha))

print("=" * 80)
print("QNG-CPU-116: Far-field deflection test in v10")
print("=" * 80)
print()
print(f"Parameters: beta_g={beta_g}, alpha={alpha}, z={z_coord}")
print(f"Screening length lambda_screen = sqrt(beta_g/(z*alpha)) = {lambda_screen:.3f}")
print()

# Test: Deflection angle vs impact parameter b
# Two hypotheses:
#   H_1911: theta ~ 1/b (Einstein 1911)
#   H_GR  : theta ~ log(b) behavior at large b (full GR)
#   H_QNG : theta ~ M * exp(-b/lambda) / b (Yukawa from finite screening)
#
# At small b (b << lambda): Yukawa ~ 1/b (matches 1911)
# At large b (b >> lambda): Yukawa dies exponentially (NEITHER 1/b nor log)

# Simulate: compute theta vs b for Yukawa potential
# Phi(r) = -G*M*exp(-r/lambda)/r
# Deflection along straight path at impact parameter b:
# theta(b) = integral from -inf to +inf of (dPhi/dr_perp) dt where r = sqrt(b^2 + t^2)
# For Yukawa: this integral is 2*G*M*K_0(b/lambda)/b (rough approximation)

from scipy import integrate, special

G_QNG = beta_g / z_coord
M_ring = 728.92  # example, not physical mass

def Phi_yukawa(r, M=M_ring, G=G_QNG, lam=lambda_screen):
    """Yukawa potential: Phi = -G*M*exp(-r/lam)/r"""
    return -G * M * np.exp(-r/lam) / r

def deflection_integrand(t, b, M, G, lam):
    """For straight-line ray at impact parameter b, integrand for theta."""
    r = np.sqrt(b**2 + t**2)
    # Gradient perpendicular to ray direction (toward source)
    # dPhi/db = dPhi/dr * b/r for ray passing at b
    dPhidr = G*M*(1 + r/lam)*np.exp(-r/lam)/r**2
    return dPhidr * b / r  # component perpendicular to ray

def deflection_theta(b, M=M_ring, G=G_QNG, lam=lambda_screen):
    """Total deflection angle (test particle) from Newtonian integration."""
    result, _ = integrate.quad(deflection_integrand, -50*lam, 50*lam,
                                args=(b, M, G, lam), limit=200)
    return result

print(f"M_ring = {M_ring}, G_QNG = {G_QNG:.4f}")
print()
print(f"{'b (natural units)':>20} {'theta(b) Yukawa':>18} {'theta_1911=k/b':>18} {'theta_log~log(b)':>18}")
print("-" * 80)

k_1911 = deflection_theta(lambda_screen, M_ring) * lambda_screen  # normalize at b=lambda
for b in [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 20.0, 30.0, 50.0]:
    theta_yukawa = deflection_theta(b, M_ring)
    theta_1911 = k_1911 / b if b > 0 else np.inf
    theta_log = k_1911 * np.log(b/0.1) / 5  # normalized at some scale
    print(f"{b:>20.2f} {theta_yukawa:>18.5e} {theta_1911:>18.5e} {theta_log:>18.5e}")

# Compare falloff exponents
print()
print("Falloff analysis (log-log slope):")
b_vals = np.array([2.0, 3.0, 5.0, 10.0, 15.0, 20.0])
theta_vals = np.array([deflection_theta(b, M_ring) for b in b_vals])
log_b = np.log(b_vals)
log_theta = np.log(np.abs(theta_vals))
# Fit log_theta = a*log_b + c (slope a)
slope, intercept = np.polyfit(log_b, log_theta, 1)
print(f"QNG far-field slope: d(log theta)/d(log b) = {slope:.3f}")
print(f"  Einstein 1911 prediction: slope = -1 (1/b)")
print(f"  GR log(b) prediction: slope ≈ 0 (logarithmic)")
print(f"  Yukawa at r>>lambda: slope << -1 (exponential suppression)")
print()
print("VERDICT v10:")
if slope > -0.5:
    verdict = "FAR_FIELD_LOG: logarithmic regime (GR-compatible)"
elif slope > -1.5:
    verdict = "FAR_FIELD_1/b: power-law (1911-like) regime"
else:
    verdict = "FAR_FIELD_YUKAWA: exponential suppression (QNG-specific)"
print(f"  {verdict}")
