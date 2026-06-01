"""QNG-CPU-132 -- Chi-field as Dark Matter candidate AUDIT.

Background:
  OBS-001 (legacy 2026-04 prereg) tested V^2_QNG = V^2_baryon + a_M_galaxy
  with a_M_galaxy fitted PER galaxy. Result:
    - Check 1 (chi^2 improvement): PASS 2.26x
    - Check 2 (frac improved): PASS 100%
    - Check 3 (a_M ~ M_baryon Tully-Fisher): FAIL r=-0.03
    - Check 4 (frac a_M > 0): PASS 72.5%
  Verdict: FAIL overall, but with ambiguous "partial confirmation".

  The 2.26x improvement comes from adding ONE FREE PARAMETER per galaxy.
  ANY function with 1 parameter/galaxy would improve fits. The only
  QNG-specific test (Check 3) FAILED.

  This audit asks: can the chi field actually be Dark Matter in v10/v11?

Tests:
  A. Compute lambda_chi from substrate parameters.
  B. Check if chi profile around point mass produces galactic-scale signature.
  C. If lambda_chi << galactic scale, chi is local — cannot be DM via Yukawa.
  D. Identify alternative mechanisms.

Substrate parameters:
  CHI_REL = 0.35    (chi-sigma_g coupling, also chi diffusion)
  CHI_DECAY = 0.020 (chi relaxation rate)
  DELTA = 0.20     (sigma_ref-sigma_g coupling)
  z = 6            (cubic coordination)
"""
import numpy as np

# Chi sector parameters
CHI_REL = 0.35
CHI_DECAY = 0.020
DELTA = 0.20
z_coord = 6

# Unit-bridge (CPU-114)
a_L_SI = 4.926e-36   # m
a_M_SI = 3.317e-8    # kg
a_T_SI = 1.775e-45   # s
KPC = 3.086e19       # m

print("=" * 80)
print("QNG-CPU-132: Chi-field as Dark Matter — AUDIT")
print("=" * 80)
print()
print("Substrate chi parameters:")
print(f"  CHI_REL   = {CHI_REL}  (diffusion + sigma_g coupling)")
print(f"  CHI_DECAY = {CHI_DECAY} (relaxation rate)")
print(f"  DELTA     = {DELTA}  (sigma_ref-sigma_g coupling)")
print(f"  z         = {z_coord}")
print()

# ==============================================================
# A. Derive lambda_chi
# ==============================================================
print("=" * 80)
print("A. Chi screening length lambda_chi")
print("=" * 80)
print()
print("Chi dynamics in v10:")
print("  d chi/dt = CHI_REL/z * Lap(chi) + DELTA*(sigma_ref-sigma_g) - CHI_DECAY*chi")
print()
print("Steady-state with source S(x) = DELTA*(sigma_ref-sigma_g(x)):")
print("  (CHI_DECAY - CHI_REL/z * Lap) chi = S")
print("  => Yukawa kernel with screening length:")
print("     lambda_chi^2 = (CHI_REL/z) / CHI_DECAY")
print()
nu_chi = CHI_REL / z_coord
lam_chi_sq = nu_chi / CHI_DECAY
lam_chi = np.sqrt(lam_chi_sq)
lam_chi_SI = lam_chi * a_L_SI
print(f"  nu_chi = CHI_REL/z = {nu_chi:.5f}")
print(f"  lambda_chi (natural) = sqrt({lam_chi_sq:.4f}) = {lam_chi:.4f} lattice units")
print(f"  lambda_chi (SI)      = {lam_chi:.4f} * a_L = {lam_chi_SI:.3e} m")
print(f"  lambda_chi / l_Planck = {lam_chi_SI/1.616e-35:.3f}")
print(f"  lambda_chi / 1 kpc    = {lam_chi_SI/KPC:.3e}")
print()

# Verdict
if lam_chi_SI < 1e-30:
    verdict_A = "lambda_chi is SUB-PLANCK — chi field is LOCAL only"
elif lam_chi_SI < 1e-20:
    verdict_A = "lambda_chi is sub-atomic — chi cannot propagate at macro scales"
elif lam_chi_SI < KPC:
    verdict_A = f"lambda_chi < 1 kpc — chi cannot create galactic-scale halos"
else:
    verdict_A = f"lambda_chi >= 1 kpc — chi could form galactic halos"
print(f"VERDICT A: {verdict_A}")
print()

# ==============================================================
# B. Chi profile around point mass
# ==============================================================
print("=" * 80)
print("B. Chi field around a point matter source")
print("=" * 80)
print()
print("If chi were sourced by point mass M with strength k_chi:")
print("  chi(r) = -(k_chi * M) * exp(-r/lambda_chi) / (4 pi r)")
print()
print("Gravitational contribution to V^2 at r:")
print("  V_chi^2(r) = G_eff * Q(r)")
print()
print("With lambda_chi << r_galactic, chi(r) ~ exp(-r/lambda_chi) -> 0 for r >> lambda_chi")
print()
print(f"At r = 1 kpc = {KPC:.2e} m:")
ratio = KPC / lam_chi_SI
print(f"  r / lambda_chi = {ratio:.3e}")
print(f"  exp(-r/lambda_chi) = exp(-{ratio:.3e}) = {np.exp(-min(ratio, 700)):.3e}")
print()
print("=> chi field is essentially ZERO at galactic scales.")
print("=> Chi-Yukawa profile CANNOT produce DM-like rotation curve excess.")
print()

# ==============================================================
# C. Was OBS-001 success real?
# ==============================================================
print("=" * 80)
print("C. Re-interpretation of OBS-001 result")
print("=" * 80)
print()
print("OBS-001 found:")
print("  V^2_QNG = V^2_baryon + a_M_galaxy fits 2.26x better than baryon-only")
print("  WITH a_M_galaxy fitted PER GALAXY (one free parameter each)")
print()
print("CRITICAL: this is just adding ONE FREE PARAMETER per galaxy.")
print("Any function with 1 free parameter per galaxy would give similar improvement.")
print()
print("Compare with:")
print("  - MOND (zero free parameters): 1.70x improvement [OBS-003]")
print("  - QNG global a_M (zero free parameters): 1.00x [OBS-002 FAIL]")
print("  - QNG per-galaxy a_M: 2.26x [OBS-001 partial PASS]")
print("  - 'Galaxy-specific dark matter halo' (1+ free params): always ~2-3x")
print()
print("=> OBS-001 'success' is TRIVIAL parameter fitting, NOT QNG-specific evidence.")
print()
print("The QNG-specific prediction was Tully-Fisher scaling (Check 3): FAILED at r=-0.03.")
print()
print("HONEST CONCLUSION: chi-field-as-DM via Yukawa profile is FALSIFIED.")
print(f"  - lambda_chi too small ({lam_chi_SI:.2e} m << 1 kpc)")
print("  - OBS-001 'partial pass' was free-parameter artifact")
print("  - Tully-Fisher prediction FAILED")
print()

# ==============================================================
# D. Alternative DM mechanisms in QNG
# ==============================================================
print("=" * 80)
print("D. Surviving DM candidate mechanisms")
print("=" * 80)
print()
print("1. PRIMORDIAL VORTEX RINGS (Phase 2 candidate)")
print("   - Stable σ_m vortex rings formed in early universe")
print("   - EM-invisible (no charge in QNG ontology yet)")
print("   - Gravitationally active via σ_g coupling")
print("   - Could form distributed DM halo")
print("   - TESTABLE: count predicted primordial ring density vs Omega_DM")
print()
print("2. SIGMA_G TOPOLOGICAL DEFECTS")
print("   - Vortices/monopoles in σ_g sector itself")
print("   - Independent of σ_m matter")
print("   - Would be 'pure gravity' DM")
print("   - TESTABLE: do σ_g admit stable defect solutions?")
print()
print("3. MODIFIED GRAVITY AT GALACTIC SCALE")
print("   - NOT cosmological Yukawa (CPU-127 ruled out)")
print("   - NOT chi-field Yukawa (this audit ruled out)")
print("   - But could be: kinetic-mixing effect, sub-Planck QNG corrections")
print("     accumulated over galactic distances")
print("   - TESTABLE: sum corrections from N~10^60 lattice sites in galaxy")
print()
print("4. DARK MATTER FROM HIDDEN SECTOR")
print("   - QNG could have additional fields not yet identified")
print("   - Like 'chi prime' or 'sigma_g excitations' at sub-substrate level")
print("   - Speculative, no current substrate basis")
print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("Chi-field-as-DM hypothesis (the OBS-001 path): EFFECTIVELY FALSIFIED")
print(f"  Reason: lambda_chi = {lam_chi_SI:.2e} m << 1 kpc by 50+ orders of magnitude")
print()
print("Surviving DM candidates in QNG:")
print("  - Primordial vortex rings (Phase 2 next)")
print("  - sigma_g topological defects (Phase 2 alt)")
print("  - Modified gravity at galactic scale (Phase 3)")
print()
print("Phase 2 next: investigate primordial vortex ring DM candidate.")
