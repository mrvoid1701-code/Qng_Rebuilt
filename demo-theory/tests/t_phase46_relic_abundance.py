"""
PHASE 46 (dark matter) -- the relic ABUNDANCE: can QNG predict Omega_DM, or is it
an input? Honest top-down calculation.

QNG dark matter is a cold gas of ~3.3 ug Planck-mass relics (Phase 44), the
endpoints of evaporated primordial black holes (Phase 38). Whether they are ALL of
the dark matter depends on HOW MANY were produced -- the abundance.

We compute, honestly:
  T1 the REQUIRED relic abundance Y_req = n_relic/s (comoving number-to-entropy
     ratio) to give the observed Omega_DM h^2 = 0.120. This is a definite number.
  T2 the THERMAL-PRODUCTION check: if relics were produced thermally (Y ~ O(0.1-1),
     like any relativistic species), their ~3 ug mass would OVERCLOSE the universe
     by ~27 orders. So relics CANNOT be thermal relics -- production must be hugely
     suppressed. (This is the generic Planck-relic overclosure problem.)
  T3 the PBH-REMNANT scenario: each primordial black hole leaves ONE relic, so
     Y_relic = Y_PBH = n_PBH/s. Producing Y_req needs a SPECIFIC primordial-BH
     number density (a known window: PBHs light enough to evaporate before BBN).
     This is ACHIEVABLE but requires an inflationary/initial-condition input that
     QNG does NOT derive.

CONCLUSION: the abundance is COMPUTABLE AS A REQUIREMENT (Y_req ~ 2e-28) and
ACHIEVABLE in a known PBH-remnant window, but NOT predicted by QNG -- it needs the
primordial-BH spectrum (inflation), which a substrate theory does not fix.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase46-relic-abundance-v1")

# constants (SI / cosmology)
M_PLANCK_KG = 2.176e-8
RELIC_KG = 0.152*M_PLANCK_KG          # Phase 44: 3.32e-9 kg
S0 = 2.891e9                          # entropy density today, /m^3 (2891/cm^3)
RHO_CRIT = 8.5e-27                    # kg/m^3
OMEGA_DM = 0.26
T_BBN_S = 1.0                         # BBN ~ 1 s; PBHs must evaporate before this
G = 6.674e-11; C = 2.998e8; HBAR = 1.055e-34


def main():
    print("="*70)
    print("PHASE 46 (dark matter) -- the relic abundance: prediction or input?")
    print("="*70)
    print("\n  relic mass = %.2e kg (3.3 ug, Phase 44); entropy density s0 = %.2e /m^3" % (RELIC_KG, S0))

    # T1: required Y = n/s
    rho_dm = OMEGA_DM*RHO_CRIT
    n_relic = rho_dm/RELIC_KG
    Y_req = n_relic/S0
    print("\n[T1] required relic abundance to BE the dark matter:")
    print("     rho_DM = %.2e kg/m^3 -> n_relic = %.2e /m^3" % (rho_dm, n_relic))
    print("     Y_req = n_relic/s0 = %.2e   (comoving number-to-entropy ratio)" % Y_req)

    # T2: thermal overclosure check
    Y_thermal = 0.1                   # typical relativistic freeze-out Y ~ O(0.1)
    rho_if_thermal = RELIC_KG*Y_thermal*S0
    overclose = rho_if_thermal/rho_dm
    print("\n[T2] thermal-production check (if relics froze out like a normal species):")
    print("     Y_thermal ~ %.1f -> rho_relic = %.2e kg/m^3" % (Y_thermal, rho_if_thermal))
    print("     that OVERCLOSES the observed dark matter by a factor %.1e (~%.0f orders)"
          % (overclose, np.log10(overclose)))
    print("     => 3 ug relics CANNOT be thermal relics; production must be suppressed")
    print("        by ~%.0f orders -- the generic Planck-relic overclosure problem." % np.log10(overclose))

    # T3: PBH-remnant scenario -- one relic per PBH; required PBH abundance
    print("\n[T3] PBH-remnant scenario (each primordial BH -> 1 relic, Phase 38):")
    Y_pbh_req = Y_req                 # one relic per PBH
    print("     need Y_PBH = n_PBH/s = Y_req = %.2e (one relic per evaporated PBH)." % Y_pbh_req)
    # PBHs must evaporate before BBN: lifetime tau ~ G^2 M^3/(hbar c^4) < 1 s
    # solve for max initial mass M_i (in kg) with tau = T_BBN
    # tau ~ 5120 pi G^2 M^3 /(hbar c^4)
    M_i_max = (T_BBN_S*HBAR*C**4/(5120*np.pi*G**2))**(1.0/3.0)
    print("     PBHs must evaporate before BBN (tau<1 s) -> initial mass M_i < %.2e kg" % M_i_max)
    print("       (~%.1e g; the known light-PBH window that leaves relics by today)." % (M_i_max*1e3))
    # required formation fraction beta ~ (relic mass / PBH mass) bookkeeping is model-
    # dependent; the point: a SPECIFIC primordial-BH number density is required.
    print("     => achievable in a KNOWN window, but requires a SPECIFIC primordial-BH")
    print("        abundance (Y_PBH=%.0e) fixed by INFLATION / initial conditions --" % Y_pbh_req)
    print("        which QNG (a substrate theory) does NOT derive.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  required abundance Y_req = %.2e (a definite number) : computed" % Y_req)
    print("  thermal production : EXCLUDED (overcloses %.0e)" % overclose)
    print("  PBH-remnant production : achievable in a known window, but an INPUT")
    print("  => Omega_DM is QUANTIFIED-as-requirement + achievable, NOT predicted by QNG")

    verdict = (
        "RELIC_ABUNDANCE_IS_COMPUTABLE_AS_A_REQUIREMENT_BUT_NOT_PREDICTED_BY_QNG. "
        "Honest endpoint of the dark-matter program. (T1) To be the observed dark "
        f"matter (Omega_DM h^2=0.120), the ~3.3 ug Planck relics need a comoving "
        f"abundance Y_req = n/s = {Y_req:.2e} -- a definite, computed number. (T2) "
        "They CANNOT be thermal relics: a normal relativistic freeze-out (Y~0.1) of "
        f"3 ug objects would overclose the universe by ~{np.log10(overclose):.0f} "
        "orders of magnitude (the generic Planck-relic overclosure problem), so "
        "their production must be suppressed by ~27 orders. (T3) The viable channel "
        "is the PBH-remnant scenario of this program: each primordial black hole "
        "leaves exactly one relic (Phase 38), so Y_relic = Y_PBH; supplying Y_req "
        "needs a specific primordial-BH number density in a KNOWN window (PBHs light "
        f"enough to evaporate before BBN, M_i < {M_i_max*1e3:.0e} g). This is "
        "ACHIEVABLE -- Planck-relic dark matter from light PBHs is an established "
        "scenario -- but the required primordial-BH abundance is fixed by INFLATION "
        "/ initial conditions, which QNG as a substrate theory does NOT derive. "
        "CONCLUSION: QNG fixes WHAT dark matter is (a neutral, cold, "
        "information-bearing ~3 ug Planck relic / degenerate dark core, Phases "
        "38-45) and its per-particle scale, and the abundance is now QUANTIFIED as a "
        "precise requirement (Y=2e-28) that is achievable in a known production "
        "window -- but Omega_DM itself is NOT predicted, because it depends on the "
        "primordial-BH spectrum (inflationary physics) outside QNG's current scope. "
        "This is the same predictive boundary every leading DM candidate hits; the "
        "honest claim is a complete, CMB-consistent dark-matter CANDIDATE with a "
        "derived particle nature and a single remaining input (the production "
        "efficiency), not a parameter-free prediction of the cosmic abundance.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"Y_req": Y_req, "n_relic_per_m3": n_relic,
                   "thermal_overclosure_factor": overclose,
                   "M_i_max_kg": M_i_max, "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
