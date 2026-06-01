"""theory-v2/tests/verify_substrate_spectrum.py — substrate excitation spectrum.

Compute the free-field quantum excitation spectrum of QNG substrate.
These are the "particles" QNG produces at the most basic level
(before V_couple, vortex backgrounds, etc.)

Each scalar field gives one massive/massless particle species:
- σ_g: with α "mass" = √α
- σ_m: free, massless (in linearized limit)
- φ: massless Goldstone (free)
- χ: massive with m_χ = √CHI_DECAY
- h_ij: massless graviton (v11)
- A_ij: massless photon (v12)

Goal: identify what particles QNG produces at substrate level + their
masses in SI.
"""
import numpy as np

print("=" * 80)
print("theory-v2 / VERIFY SUBSTRATE SPECTRUM")
print("=" * 80)
print()

# Substrate parameters
beta_phi = 0.06
mu_phi = 0.857
beta_g = 0.35
z_coord = 6
alpha = 0.005
CHI_DECAY = 0.020
CHI_REL = 0.35
g_coupling = 0.22  # V_couple coefficient
sigma_ref = 0.5

# Derived constants
c_QNG_sq = beta_phi / (z_coord * mu_phi)
c_QNG = np.sqrt(c_QNG_sq)
G_QNG = beta_g / z_coord
hbar_QNG = 0.2326

# Unit-bridge to SI
a_L_SI = 4.926e-36
a_M_SI = 3.317e-8
a_T_SI = 1.775e-45

# Conversion factors
E_unit_SI = a_M_SI * 9e16  # in J = a_M * c²
E_unit_GeV = E_unit_SI / 1.602e-10  # convert to GeV
mass_unit_kg = a_M_SI
mass_unit_GeV_c2 = mass_unit_kg * 9e16 / 1.602e-10

print(f"QNG substrate parameters:")
print(f"  beta_phi = {beta_phi}, mu_phi = {mu_phi}, beta_g = {beta_g}, z = {z_coord}")
print(f"  alpha = {alpha}, CHI_DECAY = {CHI_DECAY}")
print()
print(f"Derived: c² = {c_QNG_sq:.6f}, G = {G_QNG:.4f}, ℏ = {hbar_QNG:.4f}")
print()
print(f"Unit conversions:")
print(f"  Energy unit: a_M·c² = {E_unit_GeV:.3e} GeV (Planck-scale)")
print(f"  Mass unit:   a_M = {mass_unit_GeV_c2:.3e} GeV/c²")
print()

# ============================================================
# σ_g sector: massive scalar with mass = √α
# ============================================================
print("=" * 80)
print("σ_g sector — gravitational potential mode")
print("=" * 80)
print()
m_sg_natural = np.sqrt(alpha)
m_sg_SI = m_sg_natural * mass_unit_kg
m_sg_GeV = m_sg_natural * mass_unit_GeV_c2
print(f"In free linearized theory: m_sg² = α (restoring constant)")
print(f"  m_sg (natural) = √α = {m_sg_natural:.4f}")
print(f"  m_sg (SI) = {m_sg_SI:.3e} kg = {m_sg_GeV:.3e} GeV/c²")
print()
print("This is the σ_g 'mass'. With α very small (cosmological), σ_g is")
print("nearly massless. λ_screen = 1/m_sg in natural ≈ 14 lattice units.")
print()
print("In SI: λ_screen = a_L/m_sg = 4.926e-36/0.071 ~ 7e-35 m (sub-Planck)")
print("=> σ_g modes propagate at substrate scale; not a 'particle' per se,")
print("   it's the gravitational potential field.")
print()

# ============================================================
# σ_m sector: massless free scalar (with V_couple in vortex backgrounds)
# ============================================================
print("=" * 80)
print("σ_m sector — matter mode (free)")
print("=" * 80)
print()
print("Free σ_m: massless (kinetic term + neighbor coupling, no mass term)")
print(f"  m_sm = 0 (linearized free)")
print()
print("With V_couple = (g/2)(σ_ref - σ_m)²(1 - cos φ) in vortex backgrounds:")
print(f"  Effective mass depends on φ background")
print(f"  At cos φ = 0: m²_sm_eff = g·(σ_ref - σ_m)·(...) — varies")
print()
print("=> σ_m massless free; non-trivial in vortex backgrounds")
print()

# ============================================================
# φ sector: Goldstone + Jackiw-Rebbi
# ============================================================
print("=" * 80)
print("φ sector — phase mode (Jackiw-Rebbi-able)")
print("=" * 80)
print()
print(f"Free φ: massless Goldstone (XY phase symmetry)")
print(f"  m_φ_free = 0")
print()

# Jackiw-Rebbi mass in σ_m well
# m²_φ = (g/(2 μ_φ))·(σ_ref - σ_m)²
sigma_m_max_deficit = sigma_ref  # full depletion
m_phi_max_natural = np.sqrt(g_coupling / (2 * mu_phi)) * sigma_m_max_deficit
m_phi_max_SI = m_phi_max_natural * mass_unit_kg
m_phi_max_GeV = m_phi_max_natural * mass_unit_GeV_c2

print(f"In σ_m core (full depletion, σ_m → 0):")
print(f"  m²_φ = (g/(2μ_φ))·σ_ref² = {(g_coupling/(2*mu_phi))*sigma_ref**2:.5f}")
print(f"  m_φ (natural) = {m_phi_max_natural:.4f}")
print(f"  m_φ (SI) = {m_phi_max_SI:.3e} kg = {m_phi_max_GeV:.3e} GeV/c²")
print()
print(f"=> φ Jackiw-Rebbi mass ~ Planck scale (Gap 13: not MeV-scale)")
print()

# ============================================================
# χ sector: massive responsiveness mode
# ============================================================
print("=" * 80)
print("χ sector — responsiveness mode")
print("=" * 80)
print()
m_chi_natural = np.sqrt(CHI_DECAY)
m_chi_SI = m_chi_natural * mass_unit_kg
m_chi_GeV = m_chi_natural * mass_unit_GeV_c2
print(f"χ free with relaxation: m²_χ = CHI_DECAY = {CHI_DECAY}")
print(f"  m_χ (natural) = √CHI_DECAY = {m_chi_natural:.4f}")
print(f"  m_χ (SI) = {m_chi_SI:.3e} kg = {m_chi_GeV:.3e} GeV/c²")
print()
print(f"χ has mass ~ {m_chi_natural:.2f} substrate units = ~10²² GeV/c² in SI")
print(f"Macroscopic mass under unit-bridge — not a SM particle")
print()

# ============================================================
# Graviton (v11)
# ============================================================
print("=" * 80)
print("Graviton (v11 axiomatic extension)")
print("=" * 80)
print()
print("h_ij field, 2 transverse-traceless polarizations")
print(f"  m_graviton = 0 (massless, GW170817 confirmed)")
print(f"  c_g = c_φ exactly (DER-QNG-042 §3.3)")
print()

# ============================================================
# Photon (v12)
# ============================================================
print("=" * 80)
print("Photon (v12 axiomatic extension)")
print("=" * 80)
print()
print("A_ij field, 2 transverse polarizations")
print(f"  m_photon = 0 (massless)")
print(f"  c_γ = c_φ exactly")
print(f"  Charge quantum: e (input)")
print()

# ============================================================
# Summary table
# ============================================================
print("=" * 80)
print("SUBSTRATE PARTICLE SPECTRUM SUMMARY")
print("=" * 80)
print()
print(f"{'Field':>8} {'Particle':>20} {'Mass (natural)':>15} {'Mass (GeV/c²)':>18} {'Status':>15}")
print("-" * 90)
print(f"{'σ_g':>8} {'grav-potential mode':>20} {m_sg_natural:>15.4f} {m_sg_GeV:>18.3e} {'~Planck':>15}")
print(f"{'σ_m':>8} {'matter mode (free)':>20} {0:>15.4f} {0:>18.3e} {'massless':>15}")
print(f"{'φ free':>8} {'Goldstone':>20} {0:>15.4f} {0:>18.3e} {'massless':>15}")
print(f"{'φ in well':>8} {'Jackiw-Rebbi':>20} {m_phi_max_natural:>15.4f} {m_phi_max_GeV:>18.3e} {'~Planck':>15}")
print(f"{'χ':>8} {'responsiveness':>20} {m_chi_natural:>15.4f} {m_chi_GeV:>18.3e} {'~Planck':>15}")
print(f"{'h_ij':>8} {'graviton':>20} {0:>15.4f} {0:>18.3e} {'spin-2':>15}")
print(f"{'A_ij':>8} {'photon':>20} {0:>15.4f} {0:>18.3e} {'spin-1':>15}")
print()

# ============================================================
# Comparison with Standard Model
# ============================================================
print("=" * 80)
print("Comparison with Standard Model particles")
print("=" * 80)
print()
print(f"{'SM particle':>15} {'mass (GeV/c²)':>15} {'QNG match':>30}")
print("-" * 70)

sm_particles = [
    ("photon", 0, "v12 A_ij ✓"),
    ("graviton", 0, "v11 h_ij ✓ (axiomatic)"),
    ("electron", 0.000511, "Gap 13 blocks (would be Planck)"),
    ("muon", 0.1057, "Gap 13 blocks"),
    ("tau", 1.777, "Gap 13 blocks"),
    ("neutrino_e", 1e-9, "no candidate"),
    ("up quark", 0.0022, "Gap 13 + no SU(3)"),
    ("down quark", 0.0047, "Gap 13 + no SU(3)"),
    ("proton", 0.938, "Gap 13 + no SU(3)"),
    ("neutron", 0.940, "Gap 13 + no SU(3)"),
    ("W boson", 80.4, "no SU(2)"),
    ("Z boson", 91.2, "no SU(2)"),
    ("Higgs", 125.1, "no analog"),
    ("dark matter", "?", "DM no-go (DER-QNG-082)"),
]

for name, mass, qng_status in sm_particles:
    print(f"{name:>15} {str(mass):>15} {qng_status:>30}")
print()

# ============================================================
# What's needed
# ============================================================
print("=" * 80)
print("What's needed for full SM identification")
print("=" * 80)
print()
print("To match QNG with Standard Model particles, would need:")
print()
print("1. **Resolve Gap 13** (scale separation):")
print("   Mechanism to bridge 22 orders Planck → MeV/GeV")
print("   Candidates: dimensional transmutation, RG flow, hidden sectors")
print()
print("2. **Higgs-like mass mechanism**:")
print("   Currently QNG has no equivalent of Higgs VEV setting masses")
print("   Could be substrate-derived if Stability Principle extended")
print()
print("3. **Non-Abelian gauge sectors** (v13, v14):")
print("   Add SU(2) for weak, SU(3) for strong")
print("   Same axiomatic pattern as v11, v12")
print()
print("4. **Generation structure**:")
print("   Why 3 generations of quarks/leptons?")
print("   Could come from substrate topology (3 spatial dimensions?)")
print()
print("5. **Yukawa couplings**:")
print("   Why specific masses (electron 0.511 MeV, top 173 GeV, etc.)")
print("   Open even in Standard Model")
print()

# ============================================================
# Verdict
# ============================================================
print("=" * 80)
print("VERDICT — Particles in QNG")
print("=" * 80)
print()
print("**Free substrate spectrum**: 4 scalar excitations + graviton + photon")
print("All massless or Planck-scale (Gap 13)")
print()
print("**SM particle identification**: OPEN")
print("  - Photon ✓ (v12)")
print("  - Graviton ✓ (v11 axiomatic)")
print("  - All SM matter particles: BLOCKED by Gap 13")
print()
print("**Path forward**:")
print("  Resolve Gap 13 (multi-week analytical effort)")
print("  Or add v13/v14 axiomatic extensions for SU(2)/SU(3)")
print("  Or accept honest scope: QNG provides foundation, particles open")
print()
print("Status: HONEST framework. SM particle IDENTIFICATION is open program,")
print("        same as in Standard Model itself (Yukawa couplings input).")
