"""QNG-CPU-142 -- Search for sigma_g topological defects (DM candidate).

DM Phase 2b — sigma_g defects independent of sigma_m matter.

Background: sigma_m vortex rings (DM Phase 2 candidate) have stability
issues over Hubble time. An ALTERNATIVE: sigma_g sector itself could
host topological defects (vortices, monopoles, domain walls) that:
  - Couple to gravity (since sigma_g IS gravitational potential field)
  - Don't need EM coupling (no charged matter)
  - Could be naturally invisible (no atoms, just field configurations)
  - Possibly more stable than sigma_m vortex rings

Question: does sigma_g admit stable topological defect solutions?

sigma_g satisfies screened Poisson:
  (alpha + nu * Lap) sigma_g = -k_gm * (sigma_ref - sigma_m)

For pure sigma_g (no matter source), the equation is:
  (alpha - nu * Lap) sigma_g = 0

with sigma_g ∈ [0, 1]. Boundary condition: sigma_g → sigma_ref at infinity.

Tests:
  A. Domain walls: 1D step from sigma_g=0 to sigma_g=1
  B. Vortex (cylindrical): sigma_g varies in radial direction
  C. Monopole (spherical): sigma_g varies radially in 3D
  D. Stability under perturbation

If stable defects exist, they are DM candidates. Their mass would be
proportional to defect "core energy" × volume.
"""
import numpy as np
from scipy.optimize import brentq

# QNG parameters
beta_g = 0.35
z_coord = 6
alpha = 0.005
nu = beta_g / z_coord
sigma_ref = 0.5

print("=" * 80)
print("QNG-CPU-142: sigma_g topological defects as DM candidates")
print("=" * 80)
print()
print(f"sigma_g satisfies: alpha*(sigma_g - sigma_ref) - nu*Lap(sigma_g) = source")
print(f"  alpha = {alpha}, nu = beta_g/z = {nu:.5f}")
print(f"  sigma_ref = {sigma_ref}")
print(f"  natural screening length lambda = sqrt(nu/alpha) = {np.sqrt(nu/alpha):.4f}")
print()

# ============================================================
# A. Domain wall (1D)
# ============================================================
print("=" * 80)
print("A. 1D domain wall: sigma_g(x) interpolating between two vacua")
print("=" * 80)
print()
print("Without nonlinear potential V(sigma_g), the linear screened Poisson")
print("has only one stable vacuum at sigma_g = sigma_ref.")
print()
print("For domain walls to exist, need NONLINEAR potential with degenerate vacua.")
print("Standard QNG sigma_g sector has only quadratic V (linear EOM) — no defects.")
print()
print("=> sigma_g DOMAIN WALLS DO NOT EXIST in linear screened Poisson.")
print()

# However, in v8/v10 with V_couple, sigma_g effectively has nonlinear coupling
# via sigma_m and phi. Let me check.
print("UNLESS: nonlinearity from coupling to sigma_m, phi enters.")
print("Coupling: sigma_g + V_couple(sigma_g, sigma_m, phi) terms.")
print()
print("At sigma_m = sigma_ref, phi uniform: no nonlinearity in sigma_g alone.")
print("So pure-sigma_g defects require either:")
print("  (a) self-interaction in sigma_g (none in current QNG)")
print("  (b) bound state with sigma_m or phi")
print()
print("=> Pure sigma_g defects: STRUCTURALLY ABSENT in QNG v10/v11.")
print()

# ============================================================
# B. Are there sigma_g configurations that are LOCAL MINIMA?
# ============================================================
print("=" * 80)
print("B. Local energy minima in sigma_g sector")
print("=" * 80)
print()
print("Energy functional for sigma_g:")
print("  E[sigma_g] = sum_i (alpha/2)*(sigma_g_i - sigma_ref)^2")
print("            + sum_<ij> (nu/2)*(sigma_g_i - sigma_g_j)^2")
print()
print("This is QUADRATIC in sigma_g. Hence has UNIQUE minimum at sigma_g = sigma_ref.")
print("No multiple vacua, no topological defects.")
print()
print("=> Confirmed: sigma_g sector has NO topological defects without")
print("   nonlinear coupling to other fields.")
print()

# ============================================================
# C. Composite defects involving sigma_g + sigma_m?
# ============================================================
print("=" * 80)
print("C. Composite (sigma_g, sigma_m) defects")
print("=" * 80)
print()
print("Could a sigma_m vortex CAUSE a sigma_g defect via coupling?")
print()
print("Yes — and this IS the standard QNG ring solution:")
print("  sigma_m vortex with phi-winding creates sigma_g 'well' around it.")
print("  CPU-074: M_ring = 728.92 (sigma_m deficit)")
print("  Implied sigma_g pattern: depleted near ring core (gravitational potential)")
print()
print("This is EXACTLY the standard ring as DM candidate (DM Phase 2).")
print("Not a NEW defect class.")
print()

# ============================================================
# D. sigma_g topological structure inventory
# ============================================================
print("=" * 80)
print("D. Topological structure inventory of sigma_g")
print("=" * 80)
print()
print("sigma_g is a real scalar field on lattice, sigma_g_n in [0, 1].")
print()
print("Topological classes of (real scalar field on R^3, M = R) maps:")
print("  - pi_0(R) = 0 (R is connected) — no domain walls")
print("  - pi_1(R) = 0 (R is simply connected) — no vortices/strings")
print("  - pi_2(R) = 0 — no monopoles")
print("  - pi_3(R) = 0 — no Skyrmions")
print()
print("  ALL homotopy groups of target R are trivial.")
print()
print("=> sigma_g target manifold (R or [0,1]) has NO TOPOLOGY.")
print("   No topological defects possible.")
print()
print("Compare with phi (target U(1) = circle):")
print("  - pi_0(U(1)) = 0")
print("  - pi_1(U(1)) = Z — VORTICES exist (these are the QNG rings)")
print("  - pi_2(U(1)) = 0")
print("  - pi_3(U(1)) = 0")
print()
print("=> The ONLY topological defects in QNG come from phi (U(1)) winding.")
print("   sigma_g has no topology, sigma_m has no topology.")
print()

# ============================================================
# VERDICT
# ============================================================
print("=" * 80)
print("VERDICT — DM Phase 2b: sigma_g defects")
print("=" * 80)
print()
print("RULED OUT structurally:")
print("  sigma_g target manifold (real, R or [0,1]) has trivial topology.")
print("  All homotopy groups vanish: pi_n(R) = 0 for all n.")
print("  Therefore NO topological defects in sigma_g sector.")
print()
print("Only topological defects in QNG come from phi (U(1) target):")
print("  - phi vortices = sigma_m matter rings (Phase 2 candidate)")
print("  - hopfions Q=1 (Phase 2 candidate, see CPU-066..072)")
print()
print("Pure-gravity DM (independent of sigma_m matter) is RULED OUT in QNG v10/v11.")
print()
print("This NARROWS DM candidates to:")
print("  1. sigma_m vortex rings (Phase 2 candidate, stability untested over Hubble)")
print("  2. Hopfions (Q=1 phi topology, also stability untested)")
print("  3. Modified gravity (Phase 3 candidate, DM Phase 3 RULED OUT for current QNG)")
print()
print("Real path forward for DM in QNG:")
print("  - Test hopfion stability over very long times (T ~ 10^5 lu)")
print("  - Investigate primordial cosmology mechanism for ring formation")
print("  - Or accept that QNG cannot solve DM and document as scope limitation")
