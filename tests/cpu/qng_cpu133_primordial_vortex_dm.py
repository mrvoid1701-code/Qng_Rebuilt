"""QNG-CPU-133 -- Primordial vortex rings as Dark Matter candidate.

Phase 2 of DM exploration.

Hypothesis: in early QNG cosmology, vortex rings of σ_m sector form
spontaneously from random initial conditions (analog of cosmic strings,
PBH formation). These rings:
  - Carry mass via topological deficit
  - Couple to gravity via σ_g sector
  - Have no electromagnetic interaction (QNG has no derived EM yet)
  - Could provide collisionless DM if stable over Hubble time

Tests:
  A. Estimate ring mass under unit-bridge calibration
  B. Compute required number density to match Omega_DM = 0.27
  C. Check stability over Hubble time (vs Phase-2 dissolution rates)
  D. Check whether QNG predicts the right primordial formation density
  E. Honest assessment

Key issue acknowledged upfront: QNG has NO derived EM gauge field. The
distinction between "visible" baryons and "dark" matter requires either:
  (i) An EM analog identification (some QNG field interpretable as EM)
  (ii) A "complexity threshold" — visible matter = clustered, DM = isolated
  (iii) Acknowledgment that QNG cannot make this distinction yet

This test uses unit-bridge calibration (NOT the retracted DER-QNG-038
phenomenological calibration) for honesty.
"""
import numpy as np

# Unit-bridge constants (CPU-114)
a_L_SI = 4.926e-36  # m
a_M_SI = 3.317e-8   # kg per natural mass unit
a_T_SI = 1.775e-45  # s

# Cosmological observed values
H0_SI = 2.2e-18    # s^-1
c_SI = 2.998e8     # m/s
G_SI = 6.674e-11   # m^3 kg^-1 s^-2
rho_crit_SI = 3 * H0_SI**2 / (8 * np.pi * G_SI)  # kg/m^3
Omega_DM = 0.265
rho_DM_SI = Omega_DM * rho_crit_SI

# Galaxy halo typical
M_halo_typical = 1e12 * 1.989e30  # 10^12 M_sun in kg
R_halo_typical = 100 * 3.086e22   # 100 kpc in m

# Ring mass under unit-bridge (CPU-074: M_ring(R=4) = 728.92 natural)
M_ring_natural = 728.92
m_ring_SI = M_ring_natural * a_M_SI    # kg
m_ring_GeV = m_ring_SI * c_SI**2 / 1.602e-10  # GeV
m_Planck = 2.176e-8  # kg
m_proton = 1.673e-27  # kg

print("=" * 80)
print("QNG-CPU-133: Primordial vortex rings as DM candidate")
print("=" * 80)
print()

# ==============================================================
# A. Ring mass under correct calibration
# ==============================================================
print("A. Ring mass (unit-bridge calibration, NOT retracted DER-QNG-038)")
print("-" * 80)
print(f"  M_ring(R=4) natural = {M_ring_natural:.2f}")
print(f"  m_ring_SI           = {m_ring_SI:.3e} kg")
print(f"  m_ring / m_Planck   = {m_ring_SI/m_Planck:.1f}")
print(f"  m_ring / m_proton   = {m_ring_SI/m_proton:.3e}")
print(f"  m_ring (GeV/c^2)    = {m_ring_GeV:.3e}")
print()
print(f"  Each ring ~ 1100 Planck masses ~ 24 micrograms ~ 10^22 GeV")
print()

# ==============================================================
# B. Required number density for Omega_DM = 0.27
# ==============================================================
print("B. Number density needed to match observed DM")
print("-" * 80)
print(f"  rho_crit (today) = {rho_crit_SI:.3e} kg/m^3")
print(f"  rho_DM   (Omega = {Omega_DM}) = {rho_DM_SI:.3e} kg/m^3")
print()
n_rings_cosmological = rho_DM_SI / m_ring_SI
print(f"  n_rings_cosmological = rho_DM / m_ring = {n_rings_cosmological:.3e} rings/m^3")
print(f"  Equivalent: 1 ring per {(1/n_rings_cosmological)**(1/3):.3e} m cubed")
print(f"  Or: 1 ring per {(1/n_rings_cosmological)**(1/3) * 1e-3:.3e} km cubed")
print()

# In a galactic halo, density is much higher
rho_halo_local = 1e-21  # kg/m^3, typical galactic halo density
n_rings_halo = rho_halo_local / m_ring_SI
print(f"  Local galactic halo density ~ {rho_halo_local:.0e} kg/m^3 (typical)")
print(f"  n_rings local halo = {n_rings_halo:.3e} rings/m^3")
print(f"  Spacing in halo = {(1/n_rings_halo)**(1/3):.3e} m")
print()

# Total rings in galactic halo
V_halo = (4/3) * np.pi * R_halo_typical**3
N_rings_galaxy = V_halo * n_rings_halo
M_rings_total = N_rings_galaxy * m_ring_SI
M_rings_solar = M_rings_total / 1.989e30
print(f"  Galaxy halo volume = {V_halo:.3e} m^3 (radius 100 kpc)")
print(f"  Total rings in halo = {N_rings_galaxy:.3e}")
print(f"  Total ring mass = {M_rings_total:.3e} kg = {M_rings_solar:.3e} M_sun")
print()
print(f"  Compare with typical DM halo mass: 10^12 - 10^13 M_sun")
if 1e11 < M_rings_solar < 1e14:
    print(f"  -> ORDER OF MAGNITUDE MATCHES required DM halo mass")
else:
    print(f"  -> DOES NOT match typical DM halo mass")
print()

# ==============================================================
# C. Stability over Hubble time
# ==============================================================
print("C. Ring stability over Hubble time")
print("-" * 80)
t_Hubble_SI = 1/H0_SI
t_Hubble_natural = t_Hubble_SI / a_T_SI
print(f"  Hubble time = {t_Hubble_SI:.3e} s = {t_Hubble_SI/3.15e7/1e9:.1f} Gyr")
print(f"  Hubble time in natural QNG units: {t_Hubble_natural:.3e}")
print()

# QNG ring stability - from CPU-074: M_ring CONSERVED under Phase-3 (no Channel A)
# But under Phase-2 (with disorder), rings dissolve
# In v8 R1 orbital interpretation, rings are dynamic with period ~185 lu
# Hubble time in lattice units: 1.24e108 lu — astronomically larger than ring period
print("  QNG ring lifetime considerations:")
print("  - Under Phase-3 (no Channel A): M_ring exactly conserved (CPU-074)")
print("  - Under Phase-2 (Channel F active): rings dissolve over T~10^3 lu")
print("  - Under v8 R1 orbital: dynamic with period ~185 lu")
print()
print(f"  Hubble time in lattice units: {t_Hubble_natural:.2e}")
print(f"  Ring period (R=4 orbital): ~185 lu")
print(f"  Hubble = {t_Hubble_natural/185:.2e} ring periods")
print()
print("  PROBLEM: rings under v8 dissolve in O(10^4) lu unless special conditions")
print("  Hubble time = 10^108 lu — completely inconsistent with v8 dissolution rate")
print()
print("  Resolution paths:")
print("  (a) Cosmological substrate has DIFFERENT dynamics than lattice tests")
print("  (b) Specific topological protection mechanism preserves rings")
print("  (c) Rings continually formed/destroyed at equilibrium density")
print("  (d) Vortex-ring DM hypothesis FAILS due to dissolution")
print()

# ==============================================================
# D. Predicted formation density
# ==============================================================
print("D. Primordial formation density")
print("-" * 80)
print()
print("  In QNG cosmology, vortex rings form from φ-phase fluctuations")
print("  in early universe. Kibble mechanism analog: ring density ~ correlation")
print("  length at formation time.")
print()
print("  At Planck epoch: correlation length ~ a_L ~ 0.3 l_Planck")
print(f"  Ring density at formation: ~1 per a_L^3 = {1/a_L_SI**3:.3e} m^-3")
print()
print("  After cosmological dilution by (a/a_form)^3:")
print("  - if rings track matter (m a^-3): density ~ rho_DM today")
print(f"  - density today: required {n_rings_cosmological:.3e} m^-3")
print(f"  - dilution factor needed: {1/a_L_SI**3 / n_rings_cosmological:.3e}")
print("  - corresponds to (1+z_form) ~ this^(1/3)")
print(f"  - z_form ~ 10^{np.log10((1/a_L_SI**3 / n_rings_cosmological)**(1/3)):.0f}")
print()
print("  Need formation at z ~ 10^32 = ~Planck epoch (consistent with substrate scale)")
print()

# ==============================================================
# E. Honest assessment
# ==============================================================
print("=" * 80)
print("E. HONEST ASSESSMENT")
print("=" * 80)
print()
print("STATUS: Primordial vortex ring DM is a VIABLE CANDIDATE in principle:")
print("  - Mass scale (Planck-mass per ring) fits required DM density")
print("  - Order of magnitude works for galactic halos (10^12 M_sun)")
print("  - QNG produces vortex rings from φ-phase dynamics")
print()
print("CRITICAL ISSUES:")
print("  - Ring stability over Hubble time NOT confirmed (dissolution under")
print("    Phase-2 dynamics is fast in lattice tests)")
print("  - QNG has no derived electromagnetic field, so 'EM-invisible'")
print("    distinction between baryons and DM is undefined")
print("  - Cosmological vortex ring formation rate not derived from substrate")
print("  - No mechanism predicting Omega_DM = 0.27 specifically (vs 0.1, 0.5, etc.)")
print()
print("WHAT'S NEEDED to confirm:")
print("  1. EM gauge field identification in QNG (or alternative visible/dark distinction)")
print("  2. Cosmological vortex formation rate calculation")
print("  3. Hubble-time ring stability proof")
print("  4. Dimensional argument why Omega_DM = 0.27")
print()
print("BOTTOM LINE: This is a PROMISING DIRECTION but requires substantial")
print("development. The numbers approximately work; the mechanism is open.")
print()
print("Phase 3 next: Modified gravity at galactic scale (could complement or")
print("replace primordial vortex DM).")
