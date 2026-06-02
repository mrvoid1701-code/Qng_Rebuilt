"""
PHASE 87 (particles) -- the Higgs, electroweak symmetry breaking, and the hierarchy
problem in QNG.

Elementary-particle masses come from the Higgs mechanism, which QNG does not yet have
(the SM Higgs is a complex SU(2) doublet = a v13 extension; the chi-VEV is a real
singlet = dark energy, which CANNOT break SU(2)). What does QNG offer?

  T1 honest status: QNG has the gauge sector (edge SU(2)xU(1), P3), the custodial rho=1
     relation (P25), and the charges (P7) -- but NOT the Higgs field. EWSB needs a
     complex doublet (v13) or a dynamical condensate.
  T2 the HIERARCHY problem (why m_Higgs/EW scale << M_Planck, ~10^-17): a fundamental
     Higgs is quadratically unstable (needs fine-tuning to 1 part in 10^34). QNG's
     proven route -- DIMENSIONAL TRANSMUTATION (P11/12: the proton/QCD scale generated
     from M_Planck with NO fine-tuning, via a slowly-running coupling) -- suggests the
     EW scale is ALSO dynamically generated (a COMPOSITE/dynamical Higgs), naturally
     small WITHOUT fine-tuning, exactly as the hadron scale is.
  T3 so QNG plausibly SOLVES the hierarchy problem the same way it solved the hadron
     scale: the EW/Higgs scale = dimensional transmutation of a (new) confining-like
     coupling -> exponentially below M_Planck, no tuning. The Higgs is composite.
     HONEST: a DIRECTION (dynamical EWSB), not a built theory; the doublet/condensate
     and the W/Z absolute masses need construction.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase87-higgs-hierarchy-v1")

M_PLANCK_GEV = 1.22e19
V_EW_GEV = 246.0   # electroweak VEV


def main():
    print("="*70)
    print("PHASE 87 (particles) -- Higgs, EWSB, and the hierarchy problem in QNG")
    print("="*70)

    # T1: status
    print("\n[T1] honest status of the Higgs sector:")
    print("     QNG HAS: edge gauge sector SU(2)xU(1) (P3), custodial rho=1 (P25, 0.5%),")
    print("              charges Q=I3+Y (P7).")
    print("     QNG LACKS: the Higgs field -- the SM Higgs is a complex SU(2) DOUBLET (v13);")
    print("              the chi-VEV is a real SINGLET (dark energy), which CANNOT break")
    print("              SU(2) (Tr T^a = 0). So EWSB needs a doublet or a condensate.")

    # T2: hierarchy via transmutation
    print("\n[T2] the hierarchy problem and dimensional transmutation:")
    hierarchy = M_PLANCK_GEV/V_EW_GEV
    print("     EW scale / M_Planck = %.0f / %.2e = %.0e (the ~17-order hierarchy)"
          % (V_EW_GEV, M_PLANCK_GEV, 1/hierarchy))
    print("     a FUNDAMENTAL Higgs is quadratically unstable -> needs fine-tuning to")
    print("     ~1 part in (M_Pl/v)^2 ~ 1e34. QNG's PROVEN route avoids this:")
    print("     dimensional transmutation (P11/12) generated the proton/QCD scale from")
    print("     M_Planck with NO fine-tuning, via a slowly-running coupling:")
    # transmutation: scale = M_Pl * exp(-2pi/(b*alpha)); b = one-loop beta coeff (~9.6,
    # QCD-like, as in P11/12 where alpha_s(M_P)~0.015 gives the ~GeV proton scale)
    b = 9.6
    for alpha in [0.015, 0.018, 0.020]:
        scale = M_PLANCK_GEV*np.exp(-2*np.pi/(b*alpha))
        print("        alpha(M_Pl)=%.3f (b=%.1f) -> transmuted scale = %.1e GeV" % (alpha, b, scale))
    print("     => alpha~0.015 -> ~GeV (the proton/QCD scale, P12); alpha~0.018 -> ~TeV")
    print("        (the electroweak range) -- M_Planck transmuted down NATURALLY,")
    print("        NATURALLY (exponential, no tuning). The EW scale plausibly arises the")
    print("        same way -> the Higgs is COMPOSITE/dynamical, not fundamental.")

    # T3
    print("\n[T3] consequence:")
    print("     QNG plausibly SOLVES the hierarchy problem the way it solved the hadron")
    print("     scale: the EW/Higgs scale = dimensional transmutation of a confining-like")
    print("     coupling -> exponentially << M_Planck, no fine-tuning. The Higgs is a")
    print("     composite (condensate), not an unprotected fundamental scalar.")
    print("     HONEST: a DIRECTION (dynamical/composite EWSB), not a built theory --")
    print("     the doublet/condensate and the absolute W/Z/Higgs masses need construction.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Higgs field: ABSENT (needs v13 doublet or a condensate)")
    print("  gauge sector + custodial rho=1 + charges: PRESENT (P3/P7/P25)")
    print("  hierarchy problem: plausibly SOLVED by dimensional transmutation (composite Higgs)")

    verdict = (
        "QNG_LACKS_THE_HIGGS_FIELD_BUT_PLAUSIBLY_SOLVES_THE_HIERARCHY_PROBLEM_VIA_"
        "TRANSMUTATION. Honest accounting of the electroweak/Higgs sector. (T1) QNG "
        "HAS the gauge sector (edge SU(2)xU(1), P3), the custodial relation rho=1 "
        "(M_W=M_Z cos theta_W, verified to 0.5%, P25), and the electric charges "
        "(Q=I3+Y, P7) -- but it does NOT have the Higgs field: the Standard-Model "
        "Higgs is a complex SU(2) DOUBLET (a v13 extension), while QNG's chi-VEV is a "
        "real SINGLET (the dark energy, P53-66), which cannot break SU(2) (Tr T^a=0). "
        "So electroweak symmetry breaking requires either that doublet or a dynamical "
        "condensate -- a genuine gap. (T2) The deep issue is the HIERARCHY PROBLEM: "
        "the electroweak scale (v=246 GeV) is ~17 orders below the Planck scale, and a "
        "FUNDAMENTAL Higgs is quadratically unstable, needing fine-tuning to ~1 part "
        "in 1e34 to stay light. QNG has a PROVEN way to avoid exactly this kind of "
        "tuning: DIMENSIONAL TRANSMUTATION, which (P11/12) generated the proton/QCD "
        "scale from the Planck scale with NO fine-tuning, via a slowly-running "
        "coupling -- a coupling alpha(M_Pl) ~ 0.012-0.02 transmutes M_Planck down to "
        "the GeV-TeV range exponentially (scale = M_Pl exp(-2pi/b alpha)), naturally "
        "and without tuning. (T3) This strongly suggests QNG's electroweak scale is "
        "ALSO dynamically generated by dimensional transmutation of a confining-like "
        "coupling, making the Higgs a COMPOSITE (a condensate), exponentially below "
        "M_Planck WITHOUT fine-tuning -- the same mechanism that makes the proton "
        "naturally light. If so, QNG SOLVES the hierarchy problem the way it solved "
        "the hadron-scale problem: not by a protected fundamental scalar, but by a "
        "dynamically generated scale. NET: the Higgs field itself is a genuine missing "
        "piece (needs the v13 doublet or an explicit condensate), but the HARDEST part "
        "-- why the electroweak scale is so far below Planck without absurd "
        "fine-tuning -- is plausibly answered by QNG's transmutation mechanism "
        "(composite/dynamical Higgs), consistent with the theory's recurring theme "
        "that scales are generated, not put in. HONEST: this is a DIRECTION, not a "
        "built theory -- QNG does NOT yet contain a Higgs field, has not constructed "
        "the composite condensate, and does not predict the absolute W/Z/Higgs masses "
        "(which need the resulting VEV). The defensible claims: the gauge sector and "
        "rho=1 are present; the Higgs is absent; and the hierarchy problem is "
        "plausibly soluble by the SAME transmutation QNG already demonstrated for the "
        "proton, pointing to a composite rather than fundamental Higgs.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"higgs": "absent (needs v13 doublet or condensate)",
                   "gauge_sector": "present (edge SU(2)xU(1), rho=1, charges)",
                   "hierarchy_ratio": float(1/hierarchy),
                   "hierarchy_solution": "dimensional transmutation -> composite Higgs (direction)",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
