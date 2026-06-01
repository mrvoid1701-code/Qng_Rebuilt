"""QNG-CPU-120 -- Hawking temperature + FLRW cosmology from Stability Principle.

Phase B (quantum gravity program), task B3.

Background:
  GR Hawking (1974): at Schwarzschild horizon r_s = 2GM/c^2, vacuum
  emits thermal radiation at:
    T_H = hbar*c^3 / (8*pi*G*M*k_B)

  FLRW cosmology: universe with matter + dark energy Lambda.
    H^2 = (8*pi*G/3) rho - k*c^2/a^2 + Lambda*c^2/3
  Stability Principle (DER-QNG-066) predicts Lambda = 0 exactly.

Tests in v10:
  1. Compute Hawking temperature in natural QNG units for ring black hole.
     Compare predicted spectrum with Planck thermal radiation scaled by T_H.
  2. Given Lambda = 0, check FLRW: universe is matter-dominated,
     decelerating, with critical density rho_c = 3*H^2/(8*pi*G).
  3. Compare with observed Lambda ~ 10^-122 (Planck units) — QNG predicts
     structural Lambda = 0 -> discrepancy is MEASURED, not theoretical.
"""
import numpy as np

# Self-verified constants
beta_phi = 0.06
beta_g = 0.35
mu_phi = 0.857
z_coord = 6
alpha = 0.005

c_phi_sq = beta_phi / (z_coord * mu_phi)
c_phi = np.sqrt(c_phi_sq)
G_QNG = beta_g / z_coord
hbar_QNG = 0.2326  # CPU-108 structural
lam_screen = np.sqrt(beta_g / (z_coord * alpha))

# SI conversion constants (from CPU-114)
a_L = 4.926e-36  # m
a_M = 3.317e-8   # kg
a_T = 1.775e-45  # s

print("=" * 80)
print("QNG-CPU-120: Hawking temperature + FLRW cosmology")
print("=" * 80)
print()
print(f"Natural QNG units:")
print(f"  c_phi^2 = {c_phi_sq:.6f}")
print(f"  G_QNG   = {G_QNG:.6f}")
print(f"  hbar_QNG= {hbar_QNG}")
print()
print(f"SI conversion (CPU-114):")
print(f"  a_L = {a_L:.3e} m (= {a_L/1.616e-35:.3f} * l_Planck)")
print(f"  a_M = {a_M:.3e} kg (= {a_M/2.176e-8:.3f} * m_Planck)")
print(f"  a_T = {a_T:.3e} s (= {a_T/5.391e-44:.3f} * t_Planck)")
print()

# ==============================================================
# SUBTEST A: Hawking temperature for ring "black hole"
# ==============================================================
print("=" * 80)
print("SUBTEST A: Hawking temperature T_H = hbar*c^3 / (8*pi*G*M)")
print("=" * 80)
print()

def hawking_T_natural(M):
    """Hawking temperature in natural QNG units: hbar*c^3 / (8*pi*G*M)."""
    return hbar_QNG * c_phi**3 / (8 * np.pi * G_QNG * M)

def schwarzschild_r_natural(M):
    """Schwarzschild radius in natural units."""
    return 2 * G_QNG * M / c_phi_sq

# Scan over mass values
print(f"{'M (natural)':>15} {'r_s (natural)':>15} {'T_H (natural)':>15} {'T_H (SI K)':>15}")
print("-" * 70)

k_B = 1.381e-23  # J/K
# Energy unit = a_M * (a_L/a_T)^2
E_unit_SI = a_M * (a_L/a_T)**2  # J
# Temperature unit = E_unit / k_B
T_unit_SI = E_unit_SI / k_B

for M in [1.0, 10.0, 100.0, 728.92, 1000.0]:
    r_s = schwarzschild_r_natural(M)
    T_H = hawking_T_natural(M)
    T_H_SI = T_H * T_unit_SI
    print(f"{M:>15.2f} {r_s:>15.4f} {T_H:>15.6f} {T_H_SI:>15.3e}")

print()

# Solar mass Hawking
M_sun_kg = 1.989e30
M_sun_natural = M_sun_kg / a_M
T_H_sun_natural = hawking_T_natural(M_sun_natural)
T_H_sun_SI = T_H_sun_natural * T_unit_SI
print(f"Solar mass BH: M_sun = {M_sun_kg:.3e} kg = {M_sun_natural:.3e} (natural)")
print(f"  T_H(solar) = {T_H_sun_SI:.3e} K")
print(f"  Observed: T_H(solar BH) = 6.17e-8 K (known GR value)")
print(f"  Ratio QNG/known: {T_H_sun_SI/6.17e-8:.4f}")
print()

# ==============================================================
# SUBTEST B: FLRW cosmology — Lambda = 0 from stability
# ==============================================================
print("=" * 80)
print("SUBTEST B: FLRW cosmology with Lambda = 0")
print("=" * 80)
print()
print("Friedmann equation (vacuum):")
print("  H^2 = Lambda*c^2/3 = 0  (Stability Principle DER-QNG-066)")
print()
print("Friedmann equation (with matter density rho):")
print("  H^2 = (8*pi*G/3) * rho - k*c^2/a^2")
print()
print("For flat universe (k=0):")
print("  H^2 = (8*pi*G/3) * rho")
print("  rho_c(t) = 3*H(t)^2 / (8*pi*G)")
print()
print("Prediction: QNG universe is MATTER DOMINATED + DECELERATING")
print()

# Observed Hubble constant (SI)
H0_SI = 2.2e-18  # s^-1 (H0 approx 68 km/s/Mpc)
H0_natural = H0_SI * a_T  # natural time unit
rho_c_natural = 3 * H0_natural**2 / (8 * np.pi * G_QNG)

print(f"Observed H_0 = {H0_SI:.3e} 1/s = {H0_natural:.3e} 1/(QNG time)")
print(f"Critical density rho_c(today) = 3*H_0^2 / (8*pi*G) = {rho_c_natural:.3e}")
print()

# Now compare observed Omega_matter + Omega_Lambda vs QNG prediction
print("Observed today (Planck 2018):")
print("  Omega_matter = 0.315 (includes dark matter)")
print("  Omega_Lambda = 0.685 (dark energy)")
print("  Omega_k approx 0 (flat)")
print()
print("QNG Stability Principle prediction:")
print("  Omega_Lambda = 0 (structural)")
print("  Omega_matter = 1 - Omega_k = 1 if flat")
print()
print("Discrepancy: observed Omega_Lambda = 0.685 but QNG predicts 0")
print("Interpretation:")
print("  (1) Gap 5: alpha in QNG screened Poisson is NOT zero; alpha -> Lambda")
print("      identification makes lambda_screen = R_Hubble.")
print("      Then 'Lambda = 0 exactly' is structural requirement but")
print("      effective cosmological behavior is modified via alpha.")
print("  (2) Observed 'dark energy' might be interpretation of the Yukawa")
print("      screening: at r >> lam_screen, gravity is exponentially weaker,")
print("      mimicking anti-gravity at cosmological scales.")
print("  (3) Must check: does QNG Yukawa give rise to apparent acceleration")
print("      without true Lambda > 0?")
print()

# ==============================================================
# SUBTEST C: Yukawa screening as dark energy analog
# ==============================================================
print("=" * 80)
print("SUBTEST C: Does Yukawa screening mimic dark energy?")
print("=" * 80)
print()
print("In GR: gravitational attraction from matter at distance r is -GM/r^2.")
print("  At cosmological scales, matter doesn't cancel, gives deceleration.")
print("  Lambda > 0 (dark energy) provides repulsive force, mimicking acceleration.")
print()
print("In QNG with Yukawa: attractive force is -G*M*exp(-r/lam)/(r^2)*(1 + r/lam)")
print("  At r ~ lam: force dies exponentially.")
print("  Past r ~ lam: no effective attraction -> freely expanding universe")
print()
print("  Effective Friedmann (schematic):")
print("  H^2 = (8*pi*G/3) * rho * screen_factor(r/lam)")
print("  where screen_factor exp(-2r/lam) for Yukawa")
print()
print("  At r < lam: H^2 ~ matter (normal Friedmann)")
print("  At r > lam: H^2 -> 0 (universe 'decouples' from matter on large scales)")
print()
print("  This DOES NOT give acceleration. It gives STAGNATION.")
print()
print("  Observed: universe is ACCELERATING (z > 0.5 data from SNe Ia)")
print("  QNG Yukawa prediction: universe DECELERATES then stagnates -> WRONG?")
print()
print("Unless: alpha has time-dependence. Tests:")
print("  - alpha -> alpha(t) allows H(t) evolution matching observations")
print("  - But why would alpha depend on time? Possible if alpha traces some")
print("    substrate quantity (e.g., time-averaged sigma_g density)")
print()

# Quantitative check
lam_SI = lam_screen * a_L
R_Hubble_SI = 3e8 / H0_SI  # c/H0 ~ 1.4e26 m
print(f"QNG lam_screen in SI: {lam_SI:.3e} m")
print(f"Observable Hubble radius: c/H_0 = {R_Hubble_SI:.3e} m")
print(f"Ratio: lam / R_H = {lam_SI/R_Hubble_SI:.3e}")
print()
print(f"For lam_screen = R_Hubble (Gap 5 identification): need alpha such that")
print(f"  lam_screen_natural = R_Hubble_natural")
alpha_cosmological = beta_g / (z_coord * (R_Hubble_SI/a_L)**2)
print(f"  alpha_required = beta_g/(z*R_H^2 in natural units) = {alpha_cosmological:.3e}")
print(f"  (natural log: {np.log10(alpha_cosmological):.2f})")
print()
print(f"  Compare with observed Omega_Lambda * H_0^2:")
# Omega_Lambda * H_0^2 has units 1/s^2 in SI
# Natural:
Omega_L_H0_natural = 0.685 * H0_natural**2
print(f"  Omega_Lambda * H_0^2 (natural) = {Omega_L_H0_natural:.3e}")
print(f"  ratio alpha/(Omega_L*H^2) = {alpha_cosmological/Omega_L_H0_natural:.4f}")

print()
# ==============================================================
# VERDICT
# ==============================================================
print("=" * 80)
print("SUBTEST B3 VERDICT — QNG-CPU-120")
print("=" * 80)
print()
print("A. Hawking radiation: T_H = hbar*c^3/(8*pi*G*M) formula REPRODUCED.")
print("   For solar-mass BH, T_H predicted matches known GR value (6.17e-8 K).")
print("   This is not a NEW prediction (same as GR), but a CONSISTENCY CHECK.")
print()
print("B. Cosmology: Stability Principle predicts Lambda = 0 STRUCTURALLY.")
print("   But observed Omega_Lambda = 0.685 != 0 -> tension with observation.")
print()
print("C. Yukawa screening as dark energy analog: PARTIAL MATCH.")
print("   - Predicts decoupling at r > lam_screen (not acceleration).")
print("   - Requires alpha(t) time-dependence to match SNe Ia acceleration data.")
print("   - Alternative: Lambda = 0 exact, but effective Hubble expansion")
print("     driven by sigma_g cosmological density dynamics (not yet derived).")
print()
print("OVERALL: QNG v10 reproduces GR at solar-system + black-hole scale,")
print("  but cosmological-scale dark energy requires further work (Gap 5).")
print()
print("Phase B summary:")
print("  B1 (graviton)     : Gap 12 identified — sigma_g scalar-only")
print("  B2 (Schwarzschild): matches GR for r << lam_screen")
print("  B3 (Hawking+FLRW) : Hawking T_H formula OK; dark energy Gap 5")
