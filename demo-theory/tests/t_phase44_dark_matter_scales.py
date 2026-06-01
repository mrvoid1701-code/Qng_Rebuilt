"""
PHASE 44 (dark matter) -- QUANTITATIVE scales of QNG dark matter from the
substrate constants. Turns Phase-43's existence result into numbers.

The neutral stable object QNG actually provides is the Planck-mass REMNANT
(Phase 38: M_rem ~ a_L/2 ~ 0.15 m_Planck), the black-hole evaporation endpoint.
Dark matter is then a population of these neutral, gravitating, information-bearing
relics; the degenerate "dark star" (Phase 43) is their self-gravitating bound form.

We compute, from constants only (a_L, a_M, hbar/c/G, M_rem):
  T1 the relic mass in physical units (kg, micrograms, GeV).
  T2 the degenerate dark-star scales: Fermi EOS P=K rho^5/3, and the Chandrasekhar-
     like maximum mass M_ch ~ M_Planck^3/m^2. With a Planck-heavy constituent this
     is ~mg -> the degenerate clusters are MICRO; so DM is effectively a COLD GAS
     of Planck-mass relics (a clean CDM candidate), not macroscopic dark stars.
  T3 the cosmological number density to be Omega_DM, the relic spacing, and the
     coldness check (velocity dispersion utterly negligible -> perfect CDM).

HONEST: the relic ABUNDANCE (how many formed) is set by primordial production and
is an INPUT here, not derived. The masses/scales ARE derived from the constants.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase44-dm-scales-v1")

# physical constants (SI)
M_PLANCK_KG = 2.176e-8            # Planck mass
L_PLANCK_M = 1.616e-35           # Planck length
C = 2.998e8                      # m/s
G = 6.674e-11
HBAR = 1.055e-34
GEV_KG = 1.783e-27               # 1 GeV/c^2 in kg
RHO_CRIT = 8.5e-27               # kg/m^3 (critical density, h~0.67)
OMEGA_DM = 0.26
OMEGA_B = 0.049

# QNG
A_L_OVER_LP = 0.305
M_REM_MPL = A_L_OVER_LP/2.0      # Phase 38 remnant ~ 0.152 m_Planck


def main():
    print("="*70)
    print("PHASE 44 (dark matter) -- quantitative scales from QNG constants")
    print("="*70)

    # T1: relic mass
    m_rem_kg = M_REM_MPL*M_PLANCK_KG
    m_rem_ug = m_rem_kg*1e9          # micrograms (1 kg = 1e9 ug)
    m_rem_gev = m_rem_kg/GEV_KG
    print("\n[T1] relic mass (the neutral stable object = Planck remnant, Phase 38):")
    print("     M_rem = %.3f m_Planck = %.3e kg = %.2f micrograms = %.2e GeV"
          % (M_REM_MPL, m_rem_kg, m_rem_ug, m_rem_gev))

    # T2: degenerate dark-star scales
    M_ch_kg = M_PLANCK_KG**3/m_rem_kg**2     # ~ M_Planck^3/m^2
    M_ch_mp = M_ch_kg/M_PLANCK_KG
    print("\n[T2] degenerate dark-star scales (Fermi EOS P=K rho^5/3):")
    print("     Chandrasekhar-like max mass M_ch ~ M_Planck^3/m^2 = %.2e kg (%.1f m_Planck)"
          % (M_ch_kg, M_ch_mp))
    print("     => with a Planck-heavy constituent the bound clusters are ~mg (MICRO);")
    print("        so QNG dark matter is effectively a COLD GAS of Planck-mass relics")
    print("        (a clean CDM candidate), the dark-star (Phase 43) being its bound form.")

    # T3: cosmological number density + coldness
    rho_dm = OMEGA_DM*RHO_CRIT
    n_rem = rho_dm/m_rem_kg                  # relics per m^3
    spacing = n_rem**(-1.0/3.0)              # mean spacing (m)
    print("\n[T3] cosmological abundance (INPUT) + coldness:")
    print("     rho_DM = Omega_DM rho_crit = %.2e kg/m^3" % rho_dm)
    print("     n_rem = rho_DM/M_rem = %.2e relics/m^3  -> mean spacing %.2e m (~%.0f km)"
          % (n_rem, spacing, spacing/1e3))
    # coldness: a relic in thermal equilibrium at T_eq ~ 1 eV would have v ~ sqrt(kT/m)
    kT_eV = 1.0
    kT_J = kT_eV*1.602e-19
    v_therm = np.sqrt(kT_J/m_rem_kg)         # m/s (utterly tiny)
    print("     thermal velocity at kT~1 eV: v ~ sqrt(kT/m) = %.2e m/s = %.2e c"
          % (v_therm, v_therm/C))
    cold = v_therm/C < 1e-10
    print("     => v/c = %.1e << 1: the relics are PERFECTLY COLD (CDM). Neutral +" % (v_therm/C))
    print("        gravitating-only + cold + collisionless = textbook cold dark matter.")
    print("     DM/baryon ratio Omega_DM/Omega_b = %.1f (NOT predicted: two separate"
          % (OMEGA_DM/OMEGA_B))
    print("        production mechanisms -- abundance is an INPUT here).")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  relic mass derived: %.2f ug (%.3f m_Planck)" % (m_rem_ug, M_REM_MPL))
    print("  perfectly cold (v/c=%.0e): %s" % (v_therm/C, cold))
    print("  abundance Omega_DM: INPUT (primordial production, not derived)")

    verdict = (
        "QNG_DARK_MATTER_IS_A_COLD_GAS_OF_PLANCK_MASS_RELICS. Quantitative scales "
        "from the constants: the neutral stable object QNG provides is the "
        f"Planck-mass remnant (Phase 38), M_rem = {M_REM_MPL:.3f} m_Planck = "
        f"{m_rem_kg:.2e} kg = {m_rem_ug:.2f} micrograms = {m_rem_gev:.1e} GeV. (T2) "
        "Its degenerate self-gravitating clusters (Phase 43) have a Chandrasekhar-"
        f"like maximum mass M_ch ~ M_Planck^3/m^2 = {M_ch_kg:.1e} kg (~mg) -- MICRO, "
        "because the constituent is Planck-heavy. So QNG dark matter is effectively "
        "a COLD GAS of ~microgram Planck-mass relics (the dark star being their "
        "bound form), a clean cold-dark-matter candidate. (T3) To be Omega_DM the "
        f"number density is n_rem = {n_rem:.1e}/m^3 (mean spacing ~{spacing/1e3:.0f} "
        "km); their thermal velocity is utterly negligible (v/c ~ "
        f"{v_therm/C:.0e}), so they are PERFECTLY COLD and collisionless -- textbook "
        "CDM. HONEST: the masses and scales ARE derived from the substrate constants "
        "(a_L, M_rem, hbar/c/G), but the relic ABUNDANCE (how many formed) is set by "
        "primordial production and is an INPUT, not derived; the DM/baryon ratio 5.4 "
        "is likewise not predicted (two separate mechanisms). NET: QNG fixes WHAT "
        "dark matter is and its per-particle scale (a ~3 ug neutral cold relic), and "
        "leaves the total abundance to a production mechanism -- the same predictive "
        "status as every leading DM candidate (WIMP, axion, primordial BH). Next "
        "(Phase 45): test the COLD/collisionless/neutral profile against the real "
        "Planck CMB data.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"M_rem_mPl": M_REM_MPL, "m_rem_kg": m_rem_kg, "m_rem_ug": m_rem_ug,
                   "m_rem_GeV": m_rem_gev, "M_chandra_kg": M_ch_kg, "n_rem_per_m3": n_rem,
                   "spacing_m": spacing, "v_over_c": v_therm/C, "cold": bool(cold),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
