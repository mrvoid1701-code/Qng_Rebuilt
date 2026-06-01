"""QNG-CPU-T4 — Multi-sector ℏ derivation (potential factor-3 error in Paper 1).

User asked: rigorous falsification of QNG, no ad-hoc.

T4: Paper 1 (theory-v2/05) derives ℏ from Stability Principle using ONLY
the φ sector. But v8 substrate has kinetic terms for σ_g, σ_m, φ — all three
contribute zero-point energy.

If correct ℏ comes from multi-sector Stability:
  -β_φ N/2 + (ℏ/2) × Σ_sectors_with_kinetic Σ_k ω_k(sector) = 0

With c_g = c_m = c_φ (DER-QNG-042 matching), all three sectors have same ω_k.
So total zero-point = 3 × (ℏ/2) Σ_k ω_k_φ.

→ ℏ_v8 = ℏ_paper1 / 3 = 0.2326/3 = 0.0775 (predicted)

If true: Paper 1 is INCOMPLETE and η_LV prediction changes too.

This script:
1. Verifies the analysis carefully
2. Computes ℏ in both formulations
3. Identifies what observable changes (η_LV in particular)
4. Determines if Paper 1 needs revision
"""
import numpy as np

print("=" * 80)
print("T4: Multi-sector ℏ derivation — RIGOROUS check")
print("=" * 80)
print()

# ============================================================
# Step 1: Setup parameters
# ============================================================
beta_phi = 0.06
mu_phi = 0.857
beta_g = 0.35
z = 6
C_cubic = 2.388

# Match c_g = c_m = c_phi via mu_g, mu_m (DER-QNG-042)
c_phi_sq = beta_phi / (z * mu_phi)
print(f"Substrate parameters: β_φ={beta_phi}, μ_φ={mu_phi}, β_g={beta_g}, z={z}")
print(f"c_φ² = β_φ/(zμ_φ) = {c_phi_sq:.6f}")
print()

# For c_g = c_phi:
# c_g² = β_g/(zμ_g) = c_phi² → μ_g = β_g/(z × c_phi²)
mu_g = beta_g / (z * c_phi_sq)
print(f"For c_g = c_φ: μ_g = β_g/(z·c_φ²) = {mu_g:.4f}")

# For σ_m: assume similar coupling β_m
# In v8 default: μ_m = 10.0, so β_m = μ_m × c² × z = 10 × 0.01167 × 6 = 0.700
mu_m = 10.0
beta_m = mu_m * c_phi_sq * z
print(f"For c_m = c_φ with μ_m=10: β_m = {beta_m:.4f}")
print()


# ============================================================
# Step 2: Paper 1 (φ-only) Stability calculation
# ============================================================
print("=" * 80)
print("Step 2: Paper 1 (φ-only) Stability calculation")
print("=" * 80)
print()
print("E_class_φ + (ℏ/2) × Σ_k ω_k_φ = 0")
print()
print(f"E_class_φ = -β_φ × N/2 (per Paper 1 normalization)")
print(f"ω_k_φ = √(β_φ/(zμ_φ)) × √λ_k = c_φ · √λ_k")
print(f"  where λ_k = 2(3 - cos k_x - cos k_y - cos k_z)")
print()
print(f"Σ_k ω_k = c_φ · N · ⟨√λ⟩_BZ = c_φ · N · C_cubic")
print()
print(f"Stability: -β_φ N/2 + (ℏ/2) · c_φ · N · C_cubic = 0")
print(f"  → ℏ = β_φ / (c_φ · C_cubic)")
print(f"  → ℏ = β_φ × √(zμ_φ/β_φ) / C_cubic")
print(f"  → ℏ = √(β_φ × zμ_φ) / C_cubic")
print()

c_phi = np.sqrt(c_phi_sq)
hbar_paper1 = beta_phi / (c_phi * C_cubic)
print(f"ℏ_Paper1 = β_φ/(c_φ·C_cubic) = {beta_phi}/({c_phi:.4f}×{C_cubic}) = {hbar_paper1:.4f}")

# Equivalent formulation
hbar_paper1_alt = np.sqrt(beta_phi * mu_phi * z) / C_cubic
print(f"ℏ_Paper1 (alt) = √(β_φ·μ_φ·z)/C_cubic = {hbar_paper1_alt:.4f}")
print(f"Match? {abs(hbar_paper1 - hbar_paper1_alt) < 1e-4}")
print()


# ============================================================
# Step 3: Multi-sector Stability calculation
# ============================================================
print("=" * 80)
print("Step 3: Multi-sector Stability (3 fields contribute zero-point)")
print("=" * 80)
print()
print("In v8 substrate, σ_g, σ_m, φ ALL have kinetic terms with c² matched.")
print("Each contributes (ℏ/2)·Σ_k ω_k to zero-point.")
print()
print("Classical contributions:")
print("  φ: -β_φ × N/2 (from -β_φ Σ cos(φ_i-φ_j) at uniform φ)")
print("  σ_g: 0 (quadratic potential, min at σ_ref)")
print("  σ_m: 0 (quadratic potential, min at σ_ref)")
print("  Total classical = -β_φ × N/2")
print()
print("Zero-point contributions (each gives (ℏ/2)·c_field·N·C_cubic):")
print("  φ:   (ℏ/2)·c_φ·N·C_cubic  [c_φ² = β_φ/(zμ_φ)]")
print("  σ_g: (ℏ/2)·c_g·N·C_cubic  [c_g = c_φ by matching]")
print("  σ_m: (ℏ/2)·c_m·N·C_cubic  [c_m = c_φ by matching]")
print()
print("Total zero-point = 3 × (ℏ/2)·c_φ·N·C_cubic (since all c equal)")
print()
print("Stability: -β_φ N/2 + 3 × (ℏ/2)·c_φ·N·C_cubic = 0")
print(f"  → ℏ_v8_multi = β_φ / (3 c_φ C_cubic)")
print(f"  → ℏ_v8_multi = ℏ_paper1 / 3")
print()

hbar_v8_multi = hbar_paper1 / 3
print(f"ℏ_v8_multi = {hbar_v8_multi:.4f}")
print(f"ℏ_paper1 / ℏ_v8_multi = {hbar_paper1/hbar_v8_multi:.4f}")
print()


# ============================================================
# Step 4: Implications for unit-bridge to SI
# ============================================================
print("=" * 80)
print("Step 4: Implications for SI unit-bridge")
print("=" * 80)
print()

c_SI = 2.998e8
G_SI = 6.674e-11
hbar_SI = 1.055e-34
l_Planck = 1.616e-35

# Unit bridge: c_lat × (a_L/a_T) = c_SI, etc.
# For c_lat = c_phi (always Paper 1's c since it's the φ field):
# a_L/a_T = c_SI/c_phi = const

c_lat = c_phi
ratio_LT = c_SI/c_lat

# G_lat = β_g/z = const
G_lat = beta_g/z

# For ℏ matching:
# ℏ_QNG_lattice × (a_M·a_L²/a_T) = ℏ_SI
# → (a_M·a_L²/a_T) = ℏ_SI/ℏ_QNG_lattice

# Case 1: Paper 1 (ℏ = 0.2326)
factor_M_L2_T_paper1 = hbar_SI / hbar_paper1
print(f"Paper 1 ℏ_QNG = {hbar_paper1:.4f}:")
print(f"  a_M·a_L²/a_T = {factor_M_L2_T_paper1:.4e}")

# Case 2: v8 multi-sector (ℏ = 0.0775)
factor_M_L2_T_v8 = hbar_SI / hbar_v8_multi
print(f"v8 multi-sector ℏ_QNG = {hbar_v8_multi:.4f}:")
print(f"  a_M·a_L²/a_T = {factor_M_L2_T_v8:.4e}")
print(f"  Ratio v8/Paper1: {factor_M_L2_T_v8/factor_M_L2_T_paper1:.2f}")
print()

# Solve for (a_L, a_M, a_T) for each case
# 3 equations:
# c: a_L/a_T = ratio_LT
# G: a_L³/(a_M·a_T²) = G_SI/G_lat
# ℏ: a_M·a_L²/a_T = factor_M_L2_T

def solve_unit_bridge(factor_M_L2_T):
    r_LT = ratio_LT
    factor_G = G_SI/G_lat
    # a_M·a_L = factor_M_L2_T / (a_L/a_T) × a_L/a_L = factor_M_L2_T / r_LT × ... wait
    # a_M·a_L²/a_T = a_M·a_L²/(a_L/r_LT) = a_M·a_L·r_LT
    # so a_M·a_L = factor_M_L2_T/r_LT
    prod_ML = factor_M_L2_T / r_LT
    # a_L³/(a_M·a_T²) = a_L³/(a_M·(a_L/r_LT)²) = a_L·r_LT²/a_M
    # so a_L/a_M = factor_G/r_LT²
    ratio_LM = factor_G / r_LT**2
    a_L = np.sqrt(prod_ML * ratio_LM)
    a_M = prod_ML / a_L
    a_T = a_L / r_LT
    return a_L, a_M, a_T

a_L_p1, a_M_p1, a_T_p1 = solve_unit_bridge(factor_M_L2_T_paper1)
a_L_v8, a_M_v8, a_T_v8 = solve_unit_bridge(factor_M_L2_T_v8)

print(f"Unit bridge values:")
print(f"  Paper 1: a_L = {a_L_p1:.3e} m, a_L/ℓ_P = {a_L_p1/l_Planck:.4f}")
print(f"  v8 multi-sector: a_L = {a_L_v8:.3e} m, a_L/ℓ_P = {a_L_v8/l_Planck:.4f}")
print()

# η_LV prediction
eta_p1 = (a_L_p1/l_Planck)**2 / 8
eta_v8 = (a_L_v8/l_Planck)**2 / 8
print(f"η_LV prediction:")
print(f"  Paper 1: η = {eta_p1:.4f}")
print(f"  v8 multi-sector: η = {eta_v8:.4f}")
print(f"  Ratio: {eta_v8/eta_p1:.2f}")
print()


# ============================================================
# Step 5: Determine which is physically correct
# ============================================================
print("=" * 80)
print("Step 5: Which formulation is physically correct?")
print("=" * 80)
print()
print("In QFT, every kinetic field contributes zero-point energy.")
print("This is rigorous.")
print()
print("Therefore: multi-sector calculation IS more correct in principle.")
print()
print("BUT — important caveat:")
print()
print("If σ_g, σ_m, φ have CROSS-COUPLINGS (e.g., V_couple = (g/2)(σ_ref-σ_m)²(1-cos φ)),")
print("the zero-point is computed in the COUPLED system, not free fields.")
print()
print("For COUPLED system: normal modes mix the fields, eigenvalues differ from")
print("free dispersion, and the zero-point sum differs from naive 3 × free.")
print()
print("Specifically:")
print("  V_couple in v8: g/2 × (σ_ref - σ_m)² × (1 - cos φ)")
print("  At small fluctuations: V ≈ (g/2)(σ_ref-σ_m)² × (φ²/2)")
print("  This couples σ_m to φ via mixing")
print()
print("In coupled system: dispersion eigenvalues found from quadratic Hamiltonian.")
print()


# ============================================================
# Step 6: Coupled system analysis
# ============================================================
print("=" * 80)
print("Step 6: Coupled system zero-point energy")
print("=" * 80)
print()
print("For coupled scalars, zero-point = (ℏ/2) Σ_modes √eigenvalues")
print()
print("V_couple gives σ_m and φ a mass-like coupling (at minimum):")
print("  m_φ_eff² = V''(φ=0) at σ_m = 0 (ref) → 0")
print()
print("Hmm wait — V_couple = (g/2)(σ_ref-σ_m)²(1-cos φ)")
print("At σ_m = σ_ref (matter vacuum): V_couple = 0 for any φ")
print("So at TRUE vacuum (σ_m = σ_ref, φ = 0), V_couple = 0 and gives no φ mass.")
print()
print("Therefore: at vacuum, σ_m and φ are DECOUPLED at quadratic level.")
print("Their kinetic dispersions are INDEPENDENT.")
print()
print("CONCLUSION: in v8 vacuum, σ_g, σ_m, φ are 3 INDEPENDENT free fields.")
print("Each contributes (ℏ/2)·c·N·C to zero-point.")
print("Multi-sector calculation IS correct → ℏ_v8 = ℏ_paper1/3.")
print()


# ============================================================
# Step 7: Resolve the apparent contradiction with Paper 1
# ============================================================
print("=" * 80)
print("Step 7: Resolving Paper 1 vs multi-sector")
print("=" * 80)
print()
print("The Paper 1 formula gives ℏ_lattice = 0.2326. With unit-bridge, this")
print("matches ℏ_SI = 1.055e-34 to machine precision.")
print()
print("If multi-sector gives ℏ_lattice = 0.0775 (factor 3 different),")
print("the unit-bridge would give DIFFERENT (a_L, a_M, a_T) to match SI ℏ.")
print()
print("Specifically:")
print(f"  Paper 1: a_L/ℓ_P = {a_L_p1/l_Planck:.4f}")
print(f"  v8 multi: a_L/ℓ_P = {a_L_v8/l_Planck:.4f}")
print()
print("Both formulations match SI ℏ — but predict different a_L/ℓ_P!")
print()
print("a_L/ℓ_P is observable in principle (lattice cutoff scale).")
print()
print("Actually, a_L/ℓ_P CANNOT be directly measured. What's measured is η_LV at")
print("high energies (CTA). So:")
print(f"  Paper 1 predicts η_LV = {eta_p1:.4f}")
print(f"  v8 multi predicts η_LV = {eta_v8:.4f} = 3 × Paper 1")
print()
print("FUTURE LIV MEASUREMENT will discriminate.")
print()


# ============================================================
# Step 8: Other considerations
# ============================================================
print("=" * 80)
print("Step 8: Other considerations on multi-sector ℏ")
print("=" * 80)
print()
print("Possible counter-arguments to factor-3 reduction:")
print()
print("(a) Paper 1's '-β_φ N/2' is ALREADY the FULL classical ground")
print("    after integrating out σ_g, σ_m. → Paper 1 IS multi-sector")
print("    Status: not explicitly stated in Paper 1, would need check")
print()
print("(b) σ_g, σ_m are NOT dynamical in vacuum (they relax to σ_ref")
print("    deterministically). Then no zero-point.")
print("    Status: in v8 with kinetic terms, they ARE dynamical in principle")
print()
print("(c) Stability Principle is meant to apply to φ sector only,")
print("    other sectors don't need to be balanced.")
print("    Status: but then theory is incomplete (other sectors contribute non-zero E)")
print()
print("(d) Different effective C_cubic for combined system.")
print("    Status: each sector has same lattice geometry, same C_cubic")
print()


# ============================================================
# Step 9: FINAL VERDICT
# ============================================================
print("=" * 80)
print("FINAL VERDICT: T4 status")
print("=" * 80)
print()
print("RIGOROUS RESULT: Paper 1's φ-only Stability Principle is INCOMPLETE.")
print("Multi-sector application gives ℏ = ℏ_paper1 / 3.")
print()
print("HOWEVER: the unit-bridge to SI ABSORBS this via different a_L/ℓ_P.")
print(f"  Paper 1 a_L/ℓ_P = {a_L_p1/l_Planck:.4f}")
print(f"  Multi-sector a_L/ℓ_P = {a_L_v8/l_Planck:.4f}")
print()
print("BOTH match observed (c, G, ℏ) at machine precision.")
print()
print("They DIFFER on:")
print(f"  η_LV (testable by CTA): {eta_p1:.4f} vs {eta_v8:.4f}")
print()
print("=> NOT a contradiction with current observations.")
print("=> But PAPER 1 NEEDS REVISION to clarify which formulation is intended.")
print()
print("RECOMMENDED ACTION:")
print("  1. Update Paper 1 to apply Stability to MULTI-SECTOR")
print("  2. Recompute ℏ_QNG_lattice = 0.0775")
print("  3. Update unit-bridge: a_L/ℓ_P = 0.527 (not 0.305)")
print("  4. Update η_LV prediction: 0.0347 (not 0.0116)")
print()
print("OR:")
print("  Justify why σ_g, σ_m don't contribute zero-point")
print("  (e.g., gauge constraint, decoupling argument)")
print()
print("STATUS: Paper 1 has POTENTIAL FACTOR-3 ERROR.")
print("        η_LV prediction CHANGES from 0.0116 to 0.0347.")
print("        Both still testable, both still distinct from generic QG.")
print()
print("This is an HONEST FALSIFICATION of Paper 1 derivation as currently stated.")
print("Theory itself survives (predictions still falsifiable, just different values).")
