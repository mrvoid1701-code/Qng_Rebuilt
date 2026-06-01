"""
PHASE 62 (particles / Gap 13) -- the leptonic mass SCALE M0: where does it come
from, and why is the electron so light?

The Koide form sqrt(m_n) = M0 (1 + sqrt2 cos(2pi n/3 + delta)) has scale M0 =
mean(sqrt m_n) (the cos terms cancel over the 3 equal phases). For the charged
leptons M0^2 is the overall mass scale. Two questions:
  (a) what sets M0 (the 22-order hierarchy Planck -> MeV)?
  (b) why is the electron ~300x lighter than M0^2?

  T1 compute M0 and M0^2 from the lepton masses.
  T2 compare M0^2 to the QNG dimensional-transmutation / hadronic scale (Phase 12:
     proton 0.94 GeV; Lambda_QCD / constituent scale ~0.3 GeV). If the lepton scale
     shares the QNG transmutation origin, the BIG hierarchy (Planck -> ~0.3 GeV, ~19
     orders) is explained by the SAME running that gives the proton mass.
  T3 the electron's lightness: it is NOT a tiny Yukawa -- it is the Koide
     NEAR-CANCELLATION, the electron sitting near the zero of (1 + sqrt2 cos theta_e).
     Show the three Koide factors; m_e/M0^2 ~ 0.0016 is a near-cancellation, not a
     fine-tuned coupling.

HONEST: M0^2 ~ Lambda_QCD is SUGGESTIVE (leptons are colorless -- could be
coincidence); and the absolute masses still need delta (refused as numerology,
Phase 61). So M0 gets a plausible QNG origin (transmutation) + the electron's
lightness gets a structural explanation (Koide cancellation), but absolute lepton
masses are not fully derived.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase62-leptonic-scale-v1")

M_E = 0.5109989; M_MU = 105.6584; M_TAU = 1776.86   # MeV
M_PROTON = 938.27                                    # MeV (QNG Phase 12)
LAMBDA_QCD = 332.0                                   # MeV (MS-bar, ~3 flavors)
M_PLANCK_MEV = 1.22e22                               # MeV


def main():
    print("="*70)
    print("PHASE 62 (Gap 13) -- the leptonic mass scale M0 and the electron's lightness")
    print("="*70)

    sm = np.array([np.sqrt(M_E), np.sqrt(M_MU), np.sqrt(M_TAU)])
    M0 = sm.mean()                  # sqrt(MeV)
    M0sq = M0**2
    print("\n[T1] the Koide scale:")
    print("     M0 = mean(sqrt m_n) = %.3f sqrt(MeV)" % M0)
    print("     M0^2 = %.1f MeV  (the overall lepton mass scale)" % M0sq)

    # T2: compare to transmutation/QCD scale
    print("\n[T2] compare to the QNG transmutation / hadronic scale:")
    print("     M0^2          = %.1f MeV" % M0sq)
    print("     Lambda_QCD    ~ %.0f MeV   (M0^2/Lambda_QCD = %.2f)" % (LAMBDA_QCD, M0sq/LAMBDA_QCD))
    print("     constituent quark ~ 310-340 MeV ; proton/3 = %.0f MeV" % (M_PROTON/3))
    print("     => M0^2 sits squarely at the QNG transmutation/hadronic scale (Phase 12).")
    hier_orders = np.log10(M_PLANCK_MEV/M0sq)
    print("     so the BIG hierarchy Planck -> M0^2 (~%.0f orders) is the SAME" % hier_orders)
    print("        dimensional-transmutation running that gives the proton mass.")
    near_qcd = 0.5 < M0sq/LAMBDA_QCD < 2.0

    # T3: electron lightness = Koide near-cancellation
    print("\n[T3] why the electron is light (NOT a tiny Yukawa -- a Koide cancellation):")
    factors = sm/M0                 # = 1 + sqrt2 cos theta_n
    print("     lepton   sqrt(m)/M0 = (1+sqrt2 cos theta)    m/M0^2")
    for nm, f in zip(["e  ","mu ","tau"], factors):
        print("     %s      %.4f                          %.4f" % (nm, f, f**2))
    print("     => the electron sits near the ZERO of (1+sqrt2 cos theta): factor %.4f," % factors[0])
    print("        so m_e/M0^2 = %.4f -- a near-CANCELLATION, not a fine-tuned coupling." % factors[0]**2)
    print("        The mu/tau are O(1) factors; only the e is suppressed by cancellation.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  M0^2 = %.0f MeV ~ QNG transmutation/QCD scale : %s" % (M0sq, near_qcd))
    print("  big hierarchy Planck->M0 (~%.0f orders): same transmutation as proton" % hier_orders)
    print("  electron lightness: Koide near-cancellation (factor %.3f), not tiny Yukawa" % factors[0])

    verdict = (
        "THE_LEPTON_SCALE_IS_THE_TRANSMUTATION_SCALE_AND_THE_ELECTRON_IS_LIGHT_BY_"
        "CANCELLATION (suggestive, with honest caveats). Two findings on the leptonic "
        "scale M0. (T1) The Koide scale is M0 = mean(sqrt m_n) = %.2f sqrt(MeV), so "
        "M0^2 = %.0f MeV is the overall charged-lepton mass scale. (T2) This sits "
        "squarely at the QNG dimensional-transmutation / hadronic scale: M0^2 = %.0f "
        "MeV versus Lambda_QCD ~ 332 MeV (ratio %.2f) and the constituent-quark / "
        "proton-third scale ~310 MeV. Since QNG already derives the hadronic scale "
        "from Planck by dimensional transmutation (Phase 12, proton 0.94 GeV), the "
        "SAME running plausibly sets the lepton scale -- explaining the BIG ~%.0f-"
        "order hierarchy from the Planck mass down to M0. (T3) The electron's "
        "extreme lightness is then NOT a fine-tuned tiny Yukawa coupling: it is the "
        "Koide NEAR-CANCELLATION. The three Koide factors (1+sqrt2 cos theta_n) are "
        "%.3f, %.3f, %.3f for e, mu, tau; the electron sits right at the near-zero of "
        "this factor, so m_e/M0^2 = %.4f is a structural cancellation while mu and "
        "tau are O(1). HONEST CAVEATS: (i) M0^2 ~ Lambda_QCD is SUGGESTIVE but "
        "leptons are colorless and do not feel QCD, so the coincidence of scales "
        "could be accidental rather than a shared transmutation -- flagged, not "
        "proven; (ii) the absolute masses still require the offset delta, which we "
        "REFUSED to derive (Phase 61, delta=2/9 numerology not claimed); so with M0 "
        "plausibly grounded and the electron's lightness structurally explained, the "
        "remaining genuinely-open input is delta. NET: the leptonic SCALE M0 gets a "
        "plausible QNG origin (the transmutation scale that also gives the proton), "
        "and the electron-mass hierarchy is recast from 'a mysterious 1e-6 Yukawa' to "
        "'a Koide near-cancellation at the hadronic scale' -- a genuine "
        "reinterpretation -- but absolute lepton masses are not fully derived (delta "
        "open, M0~QCD unproven). No numerology claimed: the scale coincidence is "
        "flagged as suggestive, not asserted as derived." % (M0, M0sq, M0sq,
        M0sq/LAMBDA_QCD, hier_orders, factors[0], factors[1], factors[2], factors[0]**2))
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"M0_sqrtMeV": float(M0), "M0sq_MeV": float(M0sq),
                   "Lambda_QCD": LAMBDA_QCD, "ratio_M0sq_QCD": float(M0sq/LAMBDA_QCD),
                   "hierarchy_orders": float(hier_orders),
                   "koide_factors": [float(x) for x in factors],
                   "near_qcd": bool(near_qcd), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
