"""QNG-CPU-124 -- Audit scale tension between two a_M calibrations.

Phase C1 PREREQUISITE.

Two calibrations of "natural QNG mass unit" exist in the codebase:

  (1) DER-QNG-038 phenomenological:
      a_M_phenom = m_proton / M_ring(R=4) = 938.272 MeV / 728.92 = 1.287 MeV/unit
      Forces R=4 ring to match nucleon mass.

  (2) CPU-114 unit-bridge:
      a_M_bridge = 3.317e-8 kg = 1.524 m_Planck per unit
      Derived from solving (c_QNG, G_QNG, hbar_QNG) -> SI consistency.

These differ by ~22 orders of magnitude. They CANNOT both be correct
simultaneously. This script exposes the tension and identifies which
(if either) is structurally derived vs phenomenological fit.

Per Gabriel directive: "no tricks, all scientifically correct".
"""
import numpy as np

# Self-verified constants
beta_phi = 0.06
beta_g = 0.35
mu_phi = 0.857
z_coord = 6
hbar_QNG = 0.2326

c_phi_sq = beta_phi / (z_coord * mu_phi)
c_phi = np.sqrt(c_phi_sq)
G_QNG = beta_g / z_coord

# Unit-bridge values (CPU-114, machine-precision SI consistency)
a_L_bridge = 4.926e-36  # m
a_M_bridge = 3.317e-8   # kg
a_T_bridge = 1.775e-45  # s

# SI constants
c_SI = 2.998e8
G_SI = 6.674e-11
hbar_SI = 1.055e-34
m_proton_SI = 1.673e-27   # kg
m_proton_MeV = 938.272
m_Planck_SI = np.sqrt(hbar_SI*c_SI/G_SI)  # 2.176e-8 kg
l_Planck_SI = np.sqrt(hbar_SI*G_SI/c_SI**3)  # 1.616e-35 m
t_Planck_SI = np.sqrt(hbar_SI*G_SI/c_SI**5)  # 5.391e-44 s
E_Planck_GeV = m_Planck_SI * c_SI**2 / 1.602e-10  # 1.221e19 GeV

# CPU-074 ring data
M_ring_data = {
    3: 474.15,
    4: 728.92,
    5: 954.88,
    6: 1172.13,
    7: 1328.10,
}

print("=" * 80)
print("QNG-CPU-124: Scale tension audit between DER-QNG-038 and CPU-114")
print("=" * 80)
print()

# ============================================================
# Calibration 1: DER-QNG-038 phenomenological
# ============================================================
print("Calibration 1 (DER-QNG-038 phenomenological):")
print("  a_M_phenom = m_proton / M_ring(R=4)")
a_M_phenom_MeV = m_proton_MeV / M_ring_data[4]
a_M_phenom_kg = m_proton_SI / M_ring_data[4]
print(f"  a_M_phenom = {m_proton_MeV} MeV / {M_ring_data[4]} = {a_M_phenom_MeV:.4f} MeV/unit")
print(f"             = {a_M_phenom_kg:.4e} kg/unit")
print()

# ============================================================
# Calibration 2: CPU-114 unit-bridge
# ============================================================
print("Calibration 2 (CPU-114 unit-bridge from c, G, hbar SI):")
a_M_bridge_MeV = a_M_bridge * c_SI**2 / 1.602e-13   # J -> MeV via E=mc^2
print(f"  a_M_bridge = {a_M_bridge:.4e} kg = {a_M_bridge/m_Planck_SI:.3f} m_Planck")
print(f"             = {a_M_bridge_MeV:.4e} MeV/unit")
print(f"             = {a_M_bridge_MeV/1e22:.4f} x 10^22 MeV/unit")
print(f"             = {a_M_bridge*c_SI**2/1.602e-10/1e19:.4f} x 10^19 GeV/unit (Planck-scale)")
print()

# ============================================================
# Tension
# ============================================================
ratio = a_M_bridge_MeV / a_M_phenom_MeV
print(f"Ratio: a_M_bridge / a_M_phenom = {ratio:.4e}")
print(f"   log10(ratio) = {np.log10(ratio):.2f}")
print()
print(f"=> The two calibrations differ by ~{int(np.log10(ratio))} orders of magnitude.")
print(f"   They CANNOT both be the substrate-derived natural mass unit.")
print()

# ============================================================
# Which is substrate-derived?
# ============================================================
print("=" * 80)
print("Which calibration is substrate-derived?")
print("=" * 80)
print()
print("a_M_bridge: derived by solving 3-equation system:")
print("  c_SI = c_QNG * (a_L/a_T)")
print("  G_SI = G_QNG * (a_L^3 / (a_M * a_T^2))")
print("  hbar_SI = hbar_QNG * (a_M * a_L^2 / a_T)")
print("  Unique solution from (c, G, hbar) substrate-derived constants.")
print("  -> SUBSTRATE-DERIVED via DER-QNG-067 + CPU-114 (machine precision)")
print()
print("a_M_phenom: chosen so R=4 matches m_proton.")
print("  -> PHENOMENOLOGICAL FIT, not derived from substrate.")
print()
print("CONCLUSION: a_M_bridge is the structurally derived natural mass unit.")
print("            a_M_phenom is a phenomenological calibration that happens")
print("            to match nucleon mass for R=4 — but the absolute scale")
print("            is INCONSISTENT with the substrate-derived calibration.")
print()

# ============================================================
# Mass implications under bridge calibration
# ============================================================
print("=" * 80)
print("Ring masses under CORRECT (substrate-derived) calibration:")
print("=" * 80)
print()
print(f"{'R':>4} {'M_ring':>10} {'mass_bridge (kg)':>20} {'mass_bridge (GeV)':>20}")
print("-" * 70)
for R, M in M_ring_data.items():
    m_kg = M * a_M_bridge
    m_GeV = M * a_M_bridge * c_SI**2 / 1.602e-10
    print(f"{R:>4} {M:>10.2f} {m_kg:>20.3e} {m_GeV:>20.3e}")
print()

print(f"Compare with nucleon mass: {m_proton_SI:.3e} kg = {m_proton_MeV*1e-3:.4f} GeV")
print()
print("=> Under substrate-derived calibration, QNG rings have masses")
print(f"   ~{(M_ring_data[4]*a_M_bridge_MeV/938)/1e22:.1f} x 10^22 nucleon masses.")
print("   They are NOT hadrons. They are Planck-scale objects.")
print()

# ============================================================
# What about M_ring ratios?
# ============================================================
print("=" * 80)
print("Are M_ring RATIOS still meaningful?")
print("=" * 80)
print()
print("Under either calibration, ratios are calibration-independent:")
print()
print(f"{'R':>4} {'M_ring(R)':>12} {'M_ring(R)/M_ring(R=4)':>22} {'observed mass ratio':>22}")
print("-" * 70)
hadron_masses = {3: None, 4: 938.272, 5: 1232, 6: 1520, 7: 1700}
hadron_names  = {3: "?", 4: "N(938)", 5: "Delta(1232)", 6: "N*(1520)", 7: "Delta(1700)"}
for R, M in M_ring_data.items():
    ratio_M = M / M_ring_data[4]
    obs_mass = hadron_masses.get(R)
    if obs_mass:
        ratio_obs = obs_mass / 938.272
        agreement = abs(ratio_M - ratio_obs) / ratio_obs * 100
        print(f"{R:>4} {M:>12.2f} {ratio_M:>22.4f} {ratio_obs:>15.4f}  ({agreement:.1f}% off)  {hadron_names[R]}")
    else:
        print(f"{R:>4} {M:>12.2f} {ratio_M:>22.4f} {'?':>22}  {hadron_names[R]}")
print()
print("=> M_ring ratios match hadron mass ratios to <2% across R=4,5,6,7.")
print("   This is a REAL pattern, but the ABSOLUTE SCALE is not nucleonic")
print("   under substrate-derived calibration.")
print()

# ============================================================
# What does this mean physically?
# ============================================================
print("=" * 80)
print("PHYSICAL INTERPRETATION (honest)")
print("=" * 80)
print()
print("Possibility A (Gap 13: scale separation problem):")
print("  QNG substrate is genuinely at Planck scale (a_L ~ 0.3 l_Planck,")
print("  a_M ~ 1.5 m_Planck). Hadronic mass scale ~10^-19 m_Planck is")
print("  generated via some renormalization-group flow not yet derived.")
print("  M_ring ratios are preserved through this flow (group-theoretic).")
print()
print("Possibility B (DER-QNG-038 wrong):")
print("  The match of M_ring ratios with hadron ratios is coincidence")
print("  (4 data points, easy to fit). Real ring masses are Planck-scale,")
print("  not hadronic. R=4 is NOT a nucleon.")
print()
print("Possibility C (unit-bridge wrong):")
print("  The c, G, hbar values from QNG don't actually correspond to SI")
print("  values via simple unit conversion. Some other identification")
print("  applies. But CPU-114 verification was machine-precision...")
print()
print("Possibility D (QNG operates at multiple scales):")
print("  Substrate at Planck scale, but emergent inel-uri are dressed")
print("  composites that effectively live at hadronic scale via QNG-")
print("  specific RG flow. Like quarks (QCD) emerge at hadron scale from")
print("  Planck-level (or whatever) deeper substrate.")
print()

# ============================================================
# Verdict
# ============================================================
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("Phase C1 cannot proceed naively. Before re-deriving baryon ladder")
print("under v10, we must address scale tension:")
print()
print(f"  a_M_phenom (DER-QNG-038): {a_M_phenom_MeV:.3f} MeV/unit")
print(f"  a_M_bridge (CPU-114):     {a_M_bridge_MeV:.3e} MeV/unit")
print(f"  Discrepancy:              {ratio:.2e} = 10^{int(np.log10(ratio))}")
print()
print("This is GAP 13 (scale separation). Any baryon-ladder claim under")
print("v10 must address how Planck-scale substrate generates hadronic-scale")
print("masses. The M_ring RATIO pattern is real and worth preserving as a")
print("structural finding, but absolute mass identification needs RG-flow")
print("or scale-bridging mechanism.")
print()
print("Recommendation: declare Gap 13, document M_ring ratio pattern as")
print("structural prediction (not absolute mass identification), and proceed")
print("to Phase C with scale-aware language.")
