"""
PHASE 11 -- attacking Gap 13: the hadron scale from DIMENSIONAL TRANSMUTATION.

Phase 10 reframed Gap 13 (Planck->MeV, 22 orders) as an RG distance. Phase 3
showed QNG edges host SU(3) and CONFINE. Combine them: the edge-SU(3) coupling
RUNS (asymptotic freedom), and the confinement scale (where the coupling becomes
strong) is generated from the Planck scale by dimensional transmutation:
    Lambda = M_Planck * exp( -2 pi / (b0 * alpha_s(M_Planck)) )
with one-loop coefficient b0 = 11 - 2 N_f/3 for SU(3) with N_f light flavors.

This is the SAME mechanism that makes Lambda_QCD << M_Planck in the real world.
A near-marginal (logarithmically running) coupling turns an O(0.01) Planck-scale
input into an EXPONENTIAL hierarchy -- NOT fine-tuning.

Test: does an O(0.01) Planck-scale strong coupling reproduce the observed
~19-20 order M_Planck/Lambda_QCD hierarchy?

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase11-dim-transmutation-v1")

M_PLANCK = 1.22e19      # GeV
LAMBDA_QCD = 0.2        # GeV (~200 MeV)


def orders(alpha_P, b0):
    """log10(M_Planck/Lambda) from one-loop dimensional transmutation."""
    return (2*np.pi/(b0*alpha_P)) / np.log(10.0)


def main():
    print("="*70)
    print("PHASE 11 -- Gap 13 attack: hadron scale via dimensional transmutation")
    print("="*70)

    Nf = 3
    b0 = 11 - 2*Nf/3.0
    print("\n  SU(3), N_f=%d light flavors -> one-loop b0 = 11 - 2N_f/3 = %.1f" % (Nf, b0))

    obs_orders = np.log10(M_PLANCK/LAMBDA_QCD)
    print("  observed M_Planck/Lambda_QCD = %.1e -> %.1f orders of magnitude"
          % (M_PLANCK/LAMBDA_QCD, obs_orders))

    print("\n  hierarchy vs Planck-scale strong coupling alpha_s(M_P):")
    print("    alpha_s(M_P)   orders log10(M_P/Lambda)   Lambda (GeV)")
    table = {}
    for aP in (0.010, 0.0152, 0.020, 0.030, 0.050):
        n = orders(aP, b0)
        Lam = M_PLANCK * 10**(-n)
        table[aP] = {"orders": round(float(n), 1), "Lambda_GeV": float(Lam)}
        print("      %.4f         %5.1f                   %.2e"
              % (aP, n, Lam))

    # what alpha_s(M_P) reproduces the observed hierarchy?
    aP_fit = 2*np.pi/(b0*obs_orders*np.log(10.0))
    print("\n  alpha_s(M_P) that reproduces the observed %.1f orders: %.4f"
          % (obs_orders, aP_fit))
    print("  (the SM strong coupling extrapolated to M_P is ~0.02 -- same ballpark)")

    natural = 0.005 < aP_fit < 0.1   # an O(0.01) coupling, not fine-tuned
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  observed ~%.0f-order hierarchy from an O(0.01) Planck coupling : %s (a*=%.4f)"
          % (obs_orders, natural, aP_fit))

    if natural:
        verdict = ("GAP13_HADRON_SCALE_IS_DIMENSIONAL_TRANSMUTATION: the ~%.0f-order "
                   "Planck->hadron hierarchy is reproduced by the one-loop running "
                   "of QNG's edge-SU(3) coupling (Phase 3) with a Planck-scale "
                   "input alpha_s(M_P) = %.4f -- an O(0.01) number (the SM strong "
                   "coupling extrapolated to M_P is ~0.02, the same ballpark). The "
                   "22 orders are NOT fine-tuning: they are the EXPONENTIAL of a "
                   "moderate coupling, exactly the dimensional-transmutation / "
                   "asymptotic-freedom mechanism that makes Lambda_QCD << M_Planck "
                   "in the real world. Combined with Phase 10 (Gap 13 = RG distance) "
                   "and Phase 3 (edges confine), this turns the HADRON-scale part of "
                   "Gap 13 from a 10^-22 fine-tuning mystery into a natural O(0.01) "
                   "Planck-scale coupling + standard running. HONEST SCOPE: (i) this "
                   "explains the HADRON/confinement scale (Lambda_QCD ~ baryon "
                   "masses), NOT lepton/quark masses (Yukawa x Higgs-VEV, separate); "
                   "(ii) alpha_s(M_P) is an INPUT (tied to Gap 17, the gauge "
                   "coupling) -- but trading a 10^-22 hierarchy for an O(0.01) input "
                   "is a massive improvement; (iii) it assumes QNG's edge-SU(3) runs "
                   "with standard asymptotic freedom (the lattice-gauge expectation, "
                   "consistent with Phase 3 confinement)." % (obs_orders, aP_fit))
    else:
        verdict = "INCONCLUSIVE -- required alpha_s(M_P) is not a natural O(0.01)."
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"b0": b0, "observed_orders": float(obs_orders),
                   "alpha_s_MP_fit": float(aP_fit),
                   "hierarchy_table": {str(k): v for k, v in table.items()},
                   "natural": bool(natural), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
