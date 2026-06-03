"""
QNG 2.0 / RUNG 7 -- PREDICTIONS: where QNG 2.0 differs TESTABLY from its parents
(QNG 1.0, bare causal sets, string theory) and from LambdaCDM. The point: QNG 2.0 is
falsifiable AND distinct, not a relabelling.

ASCII output, CPU/numpy.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "qng2-rung7-predictions-v1")


def main():
    print("="*70)
    print("QNG 2.0 / RUNG 7 -- distinctive, testable predictions")
    print("="*70)

    # (observable, QNG 2.0 prediction, differs from, test)
    preds = [
        ("Lorentz violation (directional)",
         "NONE of QNG 1.0's kind -- Lorentz is EXACT (Poisson order, no preferred frame)",
         "QNG 1.0 (predicts eta_LV=0.0347 directional LIV)",
         "CTA / Fermi-LAT -- a NULL for directional LIV falsifies QNG 1.0, supports 2.0"),
        ("particle momentum diffusion (swerves)",
         "tiny ISOTROPIC (Lorentz-invariant) momentum diffusion from discreteness",
         "QNG 1.0 (directional) & smooth-spacetime theories (none)",
         "ultra-high-energy cosmic rays / pulsar timing (tightly bounded)"),
        ("dark energy w(z)",
         "FLUCTUATING around w=-1 (everpresent Lambda ~ +-1/sqrt(V))",
         "QNG 1.0 (Lambda=0 + static holographic V_0) & LambdaCDM (constant w=-1)",
         "DESI / Euclid -- a fluctuating/evolving w(z) supports 2.0 (cf. DESI hints)"),
        ("Lambda magnitude",
         "~1/sqrt(V) ~ 1e-122 (predicted, not tuned)",
         "QFT vacuum energy (off by ~120 orders); QNG 1.0 (Lambda=0)",
         "already matches observed Lambda (Sorkin, pre-1998)"),
        ("superpartners / extra dimensions",
         "NONE (no SUSY, no compactified dimensions)",
         "string theory (predicts both)",
         "LHC / colliders -- continued non-observation supports 2.0 over strings"),
        ("Planck-scale discreteness",
         "yes -- minimum length, finite d.o.f. (holographic)",
         "shared with QNG 1.0, causal sets, strings(via holography)",
         "GRB time-of-flight (shared discreteness signature)"),
        ("quantum + matter dynamics",
         "full QM (Schrodinger/Born) + matter spectrum (conditional on manifold-like)",
         "BARE causal sets (which lack a developed matter sector)",
         "any particle-physics test the spectrum makes (inherited from QNG 1.0)"),
    ]

    print("\n  observable                      QNG 2.0 says            differs from / test")
    print("  " + "-"*100)
    for o, p, d, t in preds:
        print("  %-30s | %s" % (o, p))
        print("  %-30s |   vs %s" % ("", d))
        print("  %-30s |   test: %s" % ("", t))
        print()

    print("="*70)
    print("VERDICT")
    print("="*70)
    print("  QNG 2.0's sharpest distinctive predictions:")
    print("  1. NO directional LIV (Lorentz EXACT) -> splits cleanly from QNG 1.0 (eta_LV).")
    print("  2. FLUCTUATING dark energy w(z) (everpresent Lambda) -> vs QNG 1.0 (Lambda=0) & LambdaCDM.")
    print("  3. Lambda ~ 1/sqrt(V) predicted (matches obs) + isotropic swerves + no SUSY.")
    print("  => falsifiable AND distinct from all parents.")

    verdict = (
        "QNG_2.0_IS_FALSIFIABLE_AND_DISTINCT_FROM_ALL_ITS_PARENTS. The synthesis is not a "
        "relabelling -- it makes sharp, testable predictions that separate it from QNG "
        "1.0, bare causal sets, string theory, and LambdaCDM. The two headline "
        "discriminators: (1) LORENTZ INVARIANCE -- because QNG 2.0's substrate is a "
        "Poisson causal order with no preferred frame, it predicts NO directional "
        "Lorentz violation of the kind QNG 1.0's cubic lattice produces (eta_LV=0.0347); "
        "so a CTA/Fermi-LAT NULL for directional LIV would FALSIFY QNG 1.0 while "
        "SUPPORTING QNG 2.0 -- a clean experimental split between the two versions. (2) "
        "DARK ENERGY -- QNG 2.0 inherits the causal-set everpresent-Lambda, Lambda ~ "
        "+-1/sqrt(V), which both PREDICTS the observed magnitude (~1e-122, where QFT is "
        "off by 120 orders and QNG 1.0 forced Lambda=0) AND predicts a FLUCTUATING "
        "w(z) around -1, distinct from LambdaCDM's constant w=-1 and testable by "
        "DESI/Euclid (intriguingly close to current evolving-dark-energy hints). Further "
        "distinctive predictions: tiny ISOTROPIC (Lorentz-invariant) momentum diffusion "
        "of particles -- 'swerves', a causal-set signature, unlike any directional "
        "effect, tightly bounded by UHECR/pulsar data; NO supersymmetric partners and NO "
        "extra dimensions, separating it from string theory; and a full quantum + matter "
        "dynamics (Schrodinger/Born + the inherited particle spectrum) that BARE causal "
        "sets lack. Shared with the parents: Planck-scale discreteness and the "
        "holographic finite-d.o.f. bound. NET: QNG 2.0 occupies a real, distinct, "
        "falsifiable position -- it keeps QNG 1.0's dynamical/matter physics while "
        "REPLACING its lattice (and hence its directional-LIV prediction and its Lambda=0) "
        "with causal-set foundations (exact Lorentz, predicted fluctuating Lambda). The "
        "single experiment that most cleanly distinguishes QNG 2.0 from QNG 1.0 is the "
        "directional-LIV search; the one that most distinguishes it from LambdaCDM is "
        "w(z). HONEST: these predictions are inherited/assembled from the parent theories' "
        "established phenomenology (causal-set everpresent Lambda and swerves; QNG 1.0's "
        "spectrum; the LIV contrast) rather than newly derived numbers; the matter-sector "
        "predictions remain conditional on manifold-selection (rung 6, partially "
        "resolved). No numbers forced -- the only numeric, Lambda~1e-122, is the "
        "pre-1998 Sorkin prediction matching observation.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"predictions": [{"observable": o, "qng2": p, "differs_from": d, "test": t}
                                   for (o, p, d, t) in preds],
                   "headline_discriminators": ["no directional LIV (vs QNG 1.0 eta_LV)",
                                               "fluctuating w(z) (vs LambdaCDM & QNG 1.0 Lambda=0)"],
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
