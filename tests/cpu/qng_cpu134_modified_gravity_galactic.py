"""QNG-CPU-134 -- Modified gravity at galactic scale (Phase 3 DM exploration).

Question: does QNG predict MOND-like or other non-Newtonian gravity at
galactic scales that could explain rotation curves WITHOUT dark matter?

MOND background (Milgrom 1983):
  a >> a_0:  standard Newton, a = GM/r^2
  a << a_0:  modified, a = sqrt(a_N * a_0)
  a_0 ≈ 1.2e-10 m/s^2 (empirical fit)

  Note: a_0 ≈ c × H_0 / (2π) — coincidental order of magnitude

Tests:
  A. Does QNG have a NATURAL acceleration scale of order a_0?
  B. Does the QNG Yukawa modify gravity in MOND-like way?
  C. Does any QNG nonlinearity give MOND-like interpolation?
  D. Apply to rotation curves: comparison to OBS-001 + MOND
"""
import numpy as np

# QNG constants
beta_phi = 0.06
beta_g = 0.35
mu_phi = 0.857
z_coord = 6
alpha = 0.005

c_QNG_sq = beta_phi / (z_coord * mu_phi)
G_QNG = beta_g / z_coord
hbar_QNG = 0.2326

# Unit-bridge SI
a_L_SI = 4.926e-36
a_T_SI = 1.775e-45
a_M_SI = 3.317e-8
c_SI = 2.998e8
G_SI = 6.674e-11
H0_SI = 2.2e-18
R_Hubble_SI = c_SI / H0_SI
lam_screen_SI = R_Hubble_SI

# MOND empirical
a0_MOND = 1.2e-10  # m/s^2

print("=" * 80)
print("QNG-CPU-134: Modified gravity at galactic scale")
print("=" * 80)
print()

# ==============================================================
# A. Natural acceleration scales in QNG
# ==============================================================
print("A. Natural acceleration scales in QNG")
print("-" * 80)
print()
print("Combinations of c and Hubble-rate / screening:")
print()

a_cH = c_SI * H0_SI
print(f"  a_QNG_1 = c x H_0 = {a_cH:.3e} m/s^2")
print(f"  Compare with MOND a_0 = {a0_MOND:.3e} m/s^2")
print(f"  Ratio a_QNG/a_MOND = {a_cH/a0_MOND:.3f}")
print()

a_csqrtH = c_SI**2 / lam_screen_SI
print(f"  a_QNG_2 = c^2/lambda_screen = c x H_0 = {a_csqrtH:.3e} m/s^2")
print(f"  Same as above (as expected since lambda_screen = c/H_0)")
print()

a_Planck = c_SI / 5.391e-44   # c/t_Planck
print(f"  a_QNG_Planck = c/t_Planck = {a_Planck:.3e} m/s^2")
print(f"  Way larger than MOND scale - NOT relevant")
print()

# Verdict A
print("VERDICT A:")
print(f"  c × H_0 ≈ {a_cH:.2e} m/s^2 is approximately MOND a_0 (~5x bigger)")
print("  This is a NATURAL scale in QNG (c is substrate, H_0 from Yukawa screening)")
print("  But this is just an order-of-magnitude coincidence, NOT derived MOND")
print()

# ==============================================================
# B. Yukawa correction to acceleration
# ==============================================================
print("B. Yukawa correction to gravitational acceleration")
print("-" * 80)
print()
print("QNG Newtonian + Yukawa screening:")
print("  Phi(r) = -GM exp(-r/lambda_screen)/r")
print("  a(r) = GM exp(-r/lambda) (1/r^2 + 1/(r lambda))")
print()

print("At galactic radii (r ~ 1-100 kpc) vs lambda_screen = R_Hubble:")
KPC = 3.086e19
print(f"  lambda_screen = {lam_screen_SI:.3e} m = {lam_screen_SI/KPC:.0f} kpc")
print()
print(f"  At r = 10 kpc: r/lambda = {10*KPC/lam_screen_SI:.3e}")
print(f"  At r = 100 kpc: r/lambda = {100*KPC/lam_screen_SI:.3e}")
print()
print("  All galactic distances << lambda_screen.")
print("  Yukawa correction: exp(-r/lambda) ≈ 1 - r/lambda + ... ≈ 1.")
print("  Effective gravity at galactic scales: pure Newton (no MOND-like behavior)")
print()
print("VERDICT B: Yukawa screening DOES NOT produce MOND-like modification")
print()

# ==============================================================
# C. Compute a_QNG / a_0 ratio for galactic test
# ==============================================================
print("C. Acceleration scales in galactic rotation curves")
print("-" * 80)
print()

# Sample galactic accelerations
M_sun = 1.989e30
print(f"  At outer galaxy (r = 30 kpc, M_baryon = 10^11 M_sun):")
M_test = 1e11 * M_sun
r_test = 30 * KPC
a_N = G_SI * M_test / r_test**2
print(f"    Newtonian a = {a_N:.3e} m/s^2")
print(f"    a / a_0_MOND = {a_N/a0_MOND:.3f}")
if a_N < a0_MOND:
    print(f"    a < a_0 -> in MOND modified regime")
    a_MOND = np.sqrt(a_N * a0_MOND)
    print(f"    MOND prediction: a_eff = sqrt(a_N a_0) = {a_MOND:.3e} m/s^2")
    enhancement = a_MOND / a_N
    print(f"    MOND enhancement factor: {enhancement:.3f}x")
print()

# QNG natural enhancement?
# Let's check if QNG has any mechanism that mimics MOND enhancement
print("  Does QNG have any natural mechanism producing this enhancement?")
print()
print("  Standard QNG: a_QNG = a_Newton * (1 - r/lambda + O(r^2/lambda^2)) ≈ a_Newton")
print("  No enhancement. QNG predicts STANDARD Newton at galactic scales.")
print()

# ==============================================================
# D. Comparison with OBS-001 / MOND
# ==============================================================
print("D. Comparison with rotation-curve fits")
print("-" * 80)
print()
print("  OBS-001 (per-galaxy a_M flat): chi^2/dof improvement 2.26x [PASS Check 1,2,4]")
print("                                  a_M ~ M_baryon: FAIL Check 3")
print("  OBS-002 (global a_M from theory): NO improvement [FAIL]")
print("  OBS-003 (MOND a_0): chi^2/dof improvement 1.70x [PARTIAL]")
print()
print("  QNG with cosmological Yukawa only: chi^2 improvement ~ 1.0x [FAIL galactic]")
print("    (CPU-127 confirmed: Yukawa correction at galactic scale ~ 10^-10)")
print()
print("Where could the OBS-001 improvement come from?")
print()
print("  - Pure parameter fitting (1 free param/galaxy ALWAYS improves fits)")
print("  - Real chi field contribution (RULED OUT by CPU-132: lambda_chi ~ Planck)")
print("  - Modified Newton's law in QNG (NOT predicted by current substrate)")
print("  - DM halo (not derived from QNG, but could be primordial vortex rings)")
print()

# ==============================================================
# E. Verdict
# ==============================================================
print("=" * 80)
print("Phase 3 VERDICT")
print("=" * 80)
print()
print("Modified gravity at galactic scale FROM CURRENT QNG: NOT PREDICTED")
print()
print("Detailed:")
print("1. QNG has natural acceleration scale c × H_0 ≈ 5 × a_0_MOND")
print("   But this is order-of-magnitude coincidence, not derived MOND functional form")
print()
print("2. Yukawa screening at lambda_screen = R_Hubble gives no detectable")
print("   correction at galactic scales (r/lambda ~ 10^-5)")
print()
print("3. No QNG nonlinearity has been shown to produce MOND interpolation")
print()
print("4. OBS-001 'per-galaxy fit improvement' is parameter fitting, not")
print("   QNG-specific (CPU-132 audit)")
print()
print("CONCLUSION across DM Phase 1+2+3:")
print()
print("  Phase 1 (chi-as-DM): FALSIFIED via lambda_chi ~ Planck")
print("  Phase 2 (primordial vortex DM): VIABLE in principle, needs:")
print("    - EM identification in QNG (currently absent)")
print("    - Hubble-time stability proof")
print("    - Cosmological formation rate derivation")
print("  Phase 3 (modified gravity galactic): NOT PREDICTED by current QNG")
print()
print("OVERALL DM STATUS: QNG cannot currently solve dark matter.")
print()
print("PATH FORWARD: most promising direction is Phase 2 (primordial vortex")
print("rings) IF we can:")
print("  (a) Derive Hubble-time stability (current rings dissolve in O(10^4) lu)")
print("  (b) Identify what makes them 'invisible' (no EM in QNG yet)")
print("  (c) Get formation rate to match Omega_DM = 0.27")
print()
print("Alternative: QNG might genuinely have NO dark matter explanation, and")
print("dark matter requires extension beyond current QNG (e.g., NEW field for DM)")
print("This is honest scope: c, G, hbar, Lambda=0 from substrate, BUT DM is open.")
