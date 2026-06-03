"""
QNG 2.0 / RUNG 9 (point 2) -- can QNG 2.0 derive the field mass m or the dimensionless
couplings (alpha_fine, mass ratios)? HONEST assessment: NO, not yet -- and here is exactly
why, and what the natural scales are.

  T1 the only scale on the causet is ell_P. A field's bare mass is m = (dimensionless)/ell_P,
     so NATURAL bare values are 0 (massless, symmetry-protected) or O(1/ell_P) (Planck).
  T2 observed particle masses are 1e-17..1e-22 of the Planck mass -> NOT natural bare values
     => they require a MECHANISM (dimensional transmutation / symmetry breaking), the same
     hierarchy problem as the Standard Model. Demonstrate the causet mode-frequency range
     (IR ~ 1/box to UV ~ 1/ell) -- a generic mode is ~Planck, light masses are exponentially special.
  T3 status: QNG 2.0 adds NO new handle on m or the dimensionless couplings beyond QNG 1.0
     (whose dimensional-transmutation route, P87, gives the hadron scale from a moderate
     coupling). So masses/couplings remain UNDERIVED -- a shared open debt, NOT a QNG-2.0
     failure and NOT claimed solved.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "qng2-rung9-mass-couplings-v1")


def main():
    print("="*70)
    print("QNG 2.0 / RUNG 9 -- can we derive the field mass m / dimensionless couplings? (honest)")
    print("="*70)

    # T1: the only scale is ell_P -> natural bare masses are 0 or Planck
    print("\n[T1] the only scale on the causet is ell_P, so a bare field mass m = c_m / ell_P")
    print("     with c_m dimensionless. NATURAL values: c_m = 0 (massless, symmetry-protected,")
    print("     e.g. the photon) or c_m = O(1) (Planck mass). Nothing in between is natural.")

    # T2: observed masses vs Planck
    print("\n[T2] observed particle masses vs the Planck mass (M_P = 1.22e19 GeV):")
    M_P = 1.22e19
    particles = [("electron", 0.000511e-3*1e3*0+0.000511e-3), ("proton", 0.938), ("Higgs", 125.0), ("top", 173.0)]
    # use GeV
    particles = [("electron", 0.000511), ("proton", 0.938), ("Higgs", 125.0), ("top", 173.0)]
    for name, mGeV in particles:
        print("     %-9s m/M_P = %.1e  (c_m = %.0e -- absurdly far from 0 or 1)" % (name, mGeV/M_P, mGeV/M_P))
    print("     => observed masses are ~1e-17..1e-23 of Planck: NOT natural bare values.")

    # mode-frequency range on a causet of N elements
    print("\n     causet mode-frequency range (a field on N elements, box L in ell units):")
    for N in [1e60, 1e120, 1e244]:
        L = N**0.25                      # 4-volume N -> linear size in ell
        f_IR = 1.0/L; f_UV = 1.0
        print("       N=%.0e: IR ~ 1/L = %.1e (1/ell), UV ~ 1 (1/ell) -> generic mode ~ Planck."
              % (N, f_IR))
    print("     light masses sit ~%g orders below UV -> need EXPONENTIAL suppression (transmutation)." % 20)

    # T3: status
    print("\n[T3] status (honest):")
    print("     QNG 2.0 adds NO new handle on m or the dimensionless couplings (alpha_fine,")
    print("     mass ratios) beyond QNG 1.0. QNG 1.0's dimensional-transmutation route (P87:")
    print("     Lambda = M_P exp(-2pi/(b0 alpha)) gives the hadron scale from a moderate")
    print("     coupling) is INHERITED, and it explains the hadron-scale hierarchy -- but the")
    print("     lepton/quark Yukawa masses and alpha_fine remain UNDERIVED, exactly as in the")
    print("     Standard Model. This is a shared open debt, not a QNG-2.0-specific failure.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  bare masses natural only at 0 or Planck; observed masses ~1e-20 M_P need transmutation")
    print("  QNG 2.0 inherits QNG 1.0's transmutation (hadron scale) but does NOT derive m, Yukawas, alpha")
    print("  => masses/dimensionless couplings: UNDERIVED (shared debt with SM); honestly NOT claimed")

    verdict = (
        "MASSES_AND_DIMENSIONLESS_COUPLINGS_ARE_NOT_DERIVED_BY_QNG_2.0 (honest -- and here "
        "is exactly why). Point 2 asked whether QNG 2.0 can derive the field mass m or the "
        "dimensionless couplings. The honest answer is no, and the reason is structural. "
        "(T1) The causet has a SINGLE scale, the discreteness length ell_P; a bare field "
        "mass is m = c_m/ell_P with c_m dimensionless, so the only NATURAL bare values are "
        "c_m = 0 (a massless, symmetry-protected field like the photon) or c_m = O(1) (the "
        "Planck mass). (T2) But the observed particle masses are 1e-17 to 1e-22 of the "
        "Planck mass -- absurdly far from either natural value -- so they cannot be bare "
        "masses; they require a MECHANISM (dimensional transmutation or symmetry "
        "breaking), which is precisely the Standard Model's hierarchy problem. On the "
        "causet this shows up as: field modes range from an IR frequency ~1/L (L the "
        "system size) up to a UV ~1/ell_P, so a generic excitation sits near the Planck "
        "scale and the light masses are exponentially special. (T3) QNG 2.0 adds NO new "
        "handle here beyond QNG 1.0: it inherits QNG 1.0's dimensional-transmutation route "
        "(P87, Lambda = M_P exp(-2pi/(b0 alpha)), which gives the HADRON scale from a "
        "moderate coupling and so explains that particular hierarchy), but the "
        "lepton/quark Yukawa masses and the fine-structure constant alpha remain "
        "UNDERIVED -- identical to the Standard Model's open status. So this is a SHARED "
        "open debt, not a QNG-2.0-specific failure, and it is explicitly NOT claimed "
        "solved. The honest scientific position: QNG 2.0 derives the GRAVITATIONAL "
        "constants economy (c, G, Lambda; rung 'constants') and inherits the hadron-scale "
        "transmutation, but the matter sector's dimensionless parameters are inputs, as "
        "they are everywhere in physics. Pretending otherwise would be numerology -- "
        "which this program rejects. No numbers forced.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"natural_bare_masses": "0 (massless) or O(1/ell_P) (Planck)",
                   "observed_over_planck": {n: m/M_P for n, m in particles},
                   "mechanism_needed": "dimensional transmutation / symmetry breaking (hierarchy problem)",
                   "qng2_status": "inherits QNG 1.0 transmutation (hadron scale); m, Yukawas, alpha UNDERIVED",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
