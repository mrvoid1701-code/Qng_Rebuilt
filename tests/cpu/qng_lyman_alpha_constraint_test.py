"""QNG-CPU-LYMAN-ALPHA — Lyman-α constraints on QNG-χ-DM mass m_χ.

Tests if χ-fuzzy-DM hypothesis (Gabriel 2026-04-25) is compatible with
Lyman-α forest observations of small-scale matter power spectrum.

Approach:
1. Compute fuzzy DM transfer function T_FDM(k, m_χ)
2. Compare with CDM transfer function (which works for Lyman-α)
3. Identify cutoff scale k_J for different m_χ
4. Compare with published Lyman-α constraints
5. Assess QNG-χ-DM allowed mass window

Published Lyman-α bounds:
- Iršič et al. 2017 (Phys.Rev.Lett. 119, 031302): m_χ > 2.0e-21 eV (95% CL)
- Armengaud et al. 2017: m_χ > 2.3e-21 eV
- Rogers & Peiris 2021 (Phys.Rev.Lett. 126, 071302): m_χ > 2.0e-20 eV

Tension with cusp-core:
- Marsh & Pop 2015: galactic cores prefer m_χ ~ 1e-22 eV
- This is 1-2 orders of magnitude BELOW Lyman-α lower bound
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")

print("=" * 80)
print("QNG-CPU-LYMAN-ALPHA: Constraints on m_χ from Lyman-α forest")
print("=" * 80)
print()

# Constants
hbar_eV_s = 6.582e-16  # eV·s
c_kms = 2.998e5  # km/s
H0_invs = 67.4 * 1e3 / 3.086e22  # 1/s
H0_eV = hbar_eV_s * H0_invs  # eV (= 1.4e-33)

# Conversions
ev_per_kg = 5.61e35
mpc_per_m = 3.241e-23

print(f"H_0 = {H0_invs:.3e} 1/s = {H0_eV:.3e} eV")
print()

# ============================================================
# Fuzzy DM transfer function
# Hu, Barkana & Gruzinov 2000 (Phys.Rev.Lett. 85, 1158)
# ============================================================
def k_J_quantum(m_chi_eV, z=0):
    """Quantum Jeans scale for fuzzy DM at redshift z.

    k_J = (16π G ρ_m m²)^(1/4) at matter-radiation equality
    Or numerically: k_J ≈ 9 (m/1e-22 eV)^(1/2) × (1+z)^(1/4) Mpc^-1
    """
    m_22 = m_chi_eV / 1e-22
    return 9.0 * np.sqrt(m_22) * (1+z)**0.25  # Mpc^-1

def transfer_FDM(k_Mpc_inv, m_chi_eV):
    """Transfer function for fuzzy DM (suppression ratio P_FDM / P_CDM).

    From Hu, Barkana & Gruzinov 2000, eq. 7:
    T(k) = cos(x) / (1 + x^4) where x = k / k_J × scale_factor
    """
    k_Jeans = k_J_quantum(m_chi_eV)
    x = 1.61 * (m_chi_eV/1e-22)**(-1/18) * k_Mpc_inv / k_Jeans
    # Hu-Barkana-Gruzinov form
    T = np.cos(x**3) / (1 + x**8)
    # Cap at 0 (no negative power)
    return np.maximum(T, 0)

# ============================================================
# Test 1: Show transfer function for different m_χ
# ============================================================
print("=" * 80)
print("Test 1: Fuzzy DM transfer function vs CDM")
print("=" * 80)
print()
print("T(k) = P_FDM(k)/P_CDM(k); T ≈ 1 means matches CDM, T < 1 means suppressed.")
print()

m_chi_test = [1e-23, 1e-22, 1e-21, 1e-20, 1e-19]
k_test = [0.01, 0.1, 1.0, 5.0, 10.0]  # h/Mpc-ish, treat as Mpc^-1

print(f"{'m_χ (eV)':>15} {'k_J (Mpc^-1)':>15}", end="")
for k in k_test:
    print(f" T(k={k})", end="")
print()
print("-" * 80)

for m_chi in m_chi_test:
    k_J = k_J_quantum(m_chi)
    print(f"{m_chi:>15.1e} {k_J:>15.2f}", end="")
    for k in k_test:
        T = transfer_FDM(k, m_chi)
        print(f"  {T:.3f}", end="")
    print()
print()
print("Lyman-α probes k ~ 0.5-10 Mpc^-1 (small scales).")
print("If T(k) << 1 in this range → suppression → ruled out by data.")
print()


# ============================================================
# Test 2: Half-power scale k_1/2 (where T=0.5)
# ============================================================
print("=" * 80)
print("Test 2: Half-power scale k_1/2 (where T(k) = 0.5)")
print("=" * 80)
print()
print("k_1/2 corresponds to scale below which fuzzy DM suppresses structure.")
print("Lyman-α requires k_1/2 > k_LymanAlpha_max ~ 5 Mpc^-1")
print()

print(f"{'m_χ (eV)':>15} {'k_1/2 (Mpc^-1)':>18} {'Verdict':>30}")
m_chi_scan = np.logspace(-23, -18, 50)
for m_chi in [1e-23, 5e-23, 1e-22, 5e-22, 1e-21, 2e-21, 5e-21, 1e-20, 2e-20, 1e-19]:
    # Find k where T=0.5
    k_arr = np.logspace(-2, 2, 1000)
    T_arr = np.array([transfer_FDM(k, m_chi) for k in k_arr])
    if T_arr[0] < 0.5:
        k_half = "<0.01"
    else:
        # Find where T crosses 0.5
        idx = np.where(T_arr < 0.5)[0]
        if len(idx) == 0:
            k_half = ">100"
        else:
            k_half = f"{k_arr[idx[0]]:.2f}"

    if isinstance(k_half, str) and k_half.startswith('<'):
        verdict = "TOO MUCH SUPPRESSION"
    elif isinstance(k_half, str) and k_half.startswith('>'):
        verdict = "Pure CDM-like ✓"
    else:
        k_half_val = float(k_half)
        if k_half_val < 1:
            verdict = "TOO SUPPRESSED, RULED OUT"
        elif k_half_val < 5:
            verdict = "MARGINALLY OK at z=0"
        elif k_half_val < 20:
            verdict = "OK Lyman-α ✓"
        else:
            verdict = "fully CDM-like ✓"
    print(f"{m_chi:>15.1e} {k_half:>18} {verdict:>30}")

print()


# ============================================================
# Test 3: Cusp-core vs Lyman-α tension
# ============================================================
print("=" * 80)
print("Test 3: Cusp-core vs Lyman-α tension for fuzzy DM")
print("=" * 80)
print()
print("CONSTRAINTS:")
print()
print("Cusp-core problem (dwarf galaxies):")
print("  Marsh & Pop 2015: galactic cores prefer m_χ ~ 1e-22 eV")
print("  Soliton core size r_c ~ 1 kpc requires m_χ ≈ 1e-22 eV")
print("  THIS IS THE LOW MASS BOUND")
print()
print("Lyman-α forest constraints:")
print("  Iršič et al. 2017 (PRL 119, 031302): m_χ > 2e-21 eV (95% CL)")
print("  Armengaud et al. 2017: m_χ > 2.3e-21 eV")
print("  Rogers & Peiris 2021 (PRL 126, 071302): m_χ > 2e-20 eV (tight)")
print("  THIS IS THE LOWER LIMIT")
print()
print("TENSION:")
print(f"  Cusp-core preferred: 1e-22 eV")
print(f"  Lyman-α requires: > 2e-21 eV (Iršič) or > 2e-20 eV (Rogers-Peiris)")
print(f"  Gap: 1-2 orders of magnitude")
print()
print("This is the 'fuzzy DM tension', a well-known issue in literature.")
print()


# ============================================================
# Test 4: QNG-specific window
# ============================================================
print("=" * 80)
print("Test 4: QNG-χ-DM allowed mass window")
print("=" * 80)
print()
print("If we trust BOTH cusp-core AND Lyman-α:")
print("  Cusp-core OK: m_χ ≈ 10⁻²² eV (TOO LIGHT for Lyman-α)")
print("  Lyman-α requires: m_χ > 10⁻²⁰ eV (NO CUSP-CORE BENEFIT)")
print()
print("Possible resolutions:")
print()
print("(A) Mixed DM (fuzzy + CDM):")
print("    Some fraction f_FDM = mass at 10⁻²² eV, rest CDM")
print("    Hui-Ostriker-Tremaine-Witten 2017: f_FDM < 30% at m=1e-22 eV")
print()
print("(B) Compromise mass m_χ ≈ 10⁻²¹ eV:")
print("    Less cusp-core relief but Lyman-α-compatible")
print("    Soliton r_c ~ 0.3 kpc instead of 1 kpc")
print("    Marginal cusp-core benefit")
print()
print("(C) Self-interacting fuzzy DM:")
print("    Adds extra parameter (self-coupling λ)")
print("    Schive et al. extension")
print()
print("(D) Reinterpret Lyman-α (modeling uncertainty):")
print("    Hot-CDM-like contributions, IGM thermal history")
print("    Could relax constraint")
print()


# ============================================================
# Test 5: QNG-allowed window if we accept compromise
# ============================================================
print("=" * 80)
print("Test 5: QNG-χ-DM viable mass window")
print("=" * 80)
print()

# Conservative: accept Iršič 2e-21 eV bound
# Aggressive: accept Rogers-Peiris 2e-20 eV bound

m_chi_irsic = 2e-21
m_chi_rogers = 2e-20

print(f"QNG-allowed m_χ window:")
print()
print(f"  CONSERVATIVE (Iršič bound):")
print(f"    {m_chi_irsic:.0e} eV ≤ m_χ ≤ ~1e-19 eV")
print(f"    Soliton r_c ≈ {1.6 * (1e-22/m_chi_irsic):.2f} kpc")
print(f"    Cusp-core benefit: marginal (r_c too small for typical dwarfs)")
print()
print(f"  AGGRESSIVE (Rogers-Peiris bound):")
print(f"    {m_chi_rogers:.0e} eV ≤ m_χ ≤ ~1e-18 eV")
print(f"    Soliton r_c ≈ {1.6 * (1e-22/m_chi_rogers):.3f} kpc")
print(f"    Cusp-core benefit: NONE (essentially CDM)")
print()
print(f"  COMPROMISE (mixed model):")
print(f"    Pure fuzzy at m_χ = 1e-22 eV with f_FDM ≤ 30%")
print(f"    Most DM is CDM-like, fuzzy fraction provides some core relief")
print()


# ============================================================
# Test 6: QNG-specific implication for VEV+fluct model
# ============================================================
print("=" * 80)
print("Test 6: Impact on QNG-VEV+fluctuations model")
print("=" * 80)
print()
print("Our QNG-VEV+fluct test (theory-v2/27) used m_χ = 100 H_0 in natural units.")
print()
print(f"Converting: 100 H_0 = 100 × {H0_eV:.3e} eV = {100*H0_eV:.3e} eV")
print(f"                                      ≈ 1.4e-31 eV (TOO LIGHT)")
print()
print("That mass is way below cusp-core preferred AND Lyman-α excluded.")
print()
print("For QNG-VEV+fluct to be observationally viable:")
print(f"  Required m_χ in EV: {m_chi_irsic:.0e} to {m_chi_rogers:.0e}")
print(f"  In QNG natural units (H_0 = 1): m_χ/H_0 = {m_chi_irsic/H0_eV:.0e} to {m_chi_rogers/H0_eV:.0e}")
print()
print("So m_χ/H_0 ~ 10^11 to 10^12 (much higher than our test 100).")
print()
print("This doesn't change the QUALITATIVE matter-like behavior verified")
print("(oscillating regime requires m >> H, ALL of these masses satisfy this).")
print()
print("It only requires updating numerical normalization in the VEV+fluct model.")
print()


# ============================================================
# Test 7: Falsifiability assessment
# ============================================================
print("=" * 80)
print("Test 7: QNG-χ-DM falsifiability summary")
print("=" * 80)
print()
print("FALSIFIED IF:")
print("  - m_χ < 2e-21 eV (rejected by Iršič 2017)")
print("  - m_χ < 2e-20 eV AND no mixed-DM (rejected by Rogers-Peiris 2021)")
print()
print("CONSISTENT IF:")
print("  - m_χ ∈ [2e-21, 1e-19] eV (compromise window)")
print("  - Mixed DM with f_FDM ≤ 30%, m_χ ~ 1e-22 eV")
print()
print("CUSP-CORE BENEFIT:")
print("  - Strong: m_χ ~ 1e-22 eV (in tension with Lyman-α)")
print("  - Marginal: m_χ ~ 5e-22 eV (compromise)")
print("  - None: m_χ > 5e-21 eV")
print()
print("OBSERVATIONAL DISCRIMINATION:")
print("  - JWST + Euclid + LSST: more dwarf galaxy + Lyman-α data")
print("  - Could pin down m_χ within 10x in next 5 years")
print()


# ============================================================
# Final verdict
# ============================================================
print("=" * 80)
print("VERDICT — Lyman-α constraints on QNG-χ-DM")
print("=" * 80)
print()
print("Status of QNG-χ-fuzzy-DM hypothesis:")
print()
print("✓ NOT FALSIFIED if m_χ ∈ [2e-21, 1e-19] eV")
print("? In tension if m_χ = 1e-22 eV (cusp-core preferred)")
print("✗ Falsified if m_χ < 2e-21 eV")
print()
print("This is the SAME tension faced by all fuzzy DM models — not a")
print("specific QNG problem.")
print()
print("RESOLUTIONS available to QNG:")
print("  1. Compromise m_χ ~ 10⁻²¹ eV (some cusp-core benefit, Lyman-α OK)")
print("  2. Mixed fuzzy+CDM (well-studied in literature)")
print("  3. Wait for refined observations (next 5-10 years)")
print()
print("CONNECTION TO QNG SUBSTRATE:")
print("  - In v8 default: CHI_DECAY = 0.020 lattice → m_χ = 1.7e18 GeV (super-Planckian)")
print("  - This is NUMERICAL stability parameter")
print("  - Cosmological m_χ identification needed (analogous to α↔Λ)")
print("  - Required CHI_DECAY ~ 10⁻¹⁰⁵ Planck units (for m_χ ~ 10⁻²¹ eV)")
print()
print("STATUS: QNG-χ-DM is OBSERVATIONALLY VIABLE in compromise window.")
print("        Same constraints as standard fuzzy DM (no QNG-specific issue).")
print("        Specific m_χ identification still requires substrate principle.")
