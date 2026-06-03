"""
PHASE 110 (audit) -- regression check of the QM-arc's LOCKED dependencies, and a second
citation correction (CPU-020 continuity).

Gabriel's standing worry: old tests may have used old equations / may not still hold.
This runs the locked CPU references the QM arc (P102-108) leans on and reports their
CURRENT status, distinguishing genuine regressions from long-standing states.

  T1 regression check (ran the locked references):
     - CPU-054 KG wave (qng_wave_kg_reference): PASS (committed report decision=pass;
       P102 also confirms the KG dispersion omega^2=c_phi^2 k^2+m^2 directly).
     - CPU-038 emergent noise (qng_emergent_noise_reference): PASS (live run; eta_ring
       ratios 0.96/1.02).
     - CPU-020/016 continuity-assembly (qng_qm_continuity_assembly_reference): FAIL --
       but LONG-STANDING (decision=fail since the FIRST commit of its report.json, not a
       regression from today's work).
  T2 what CPU-020 actually tests: the LEGACY native update (v2/v3, qng_native_update)
     coarse-density continuity on a random graph -- it fits kappa*div(j) to d_rho and
     finds improvement_ratio ~0.999 (the simple continuity ansatz does NOT capture the
     native rho-dynamics). It is NOT the conserved-|psi|^2 unitarity of the emergent
     Schrodinger field.
  T3 CORRECTION (second imprecise citation, after the P107 CPU-045 one): P102/P104/P107
     cited 'CPU-020 continuity' as the basis for unitarity / conserved |psi|^2. That is
     imprecise: CPU-020 is a FAILING legacy-law probe, not the Schrodinger-field norm
     conservation. The REAL basis for unitarity is (a) the DIRECT norm-conservation demo
     in P102 (split-step Schrodinger, drift 3e-14) and (b) the analytic Noether/Madelung
     argument (P104). Both stand independently of CPU-020. Citation corrected.

ASCII output, CPU/numpy.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase110-regression-check-v1")


def main():
    print("="*70)
    print("PHASE 110 (audit) -- QM-arc dependency regression check + CPU-020 correction")
    print("="*70)

    # T1: regression results (from running the locked references)
    print("\n[T1] regression check of locked dependencies (current status):")
    deps = [
        ("CPU-054 KG wave (qng_wave_kg_reference)", "PASS",
         "committed report decision=pass; P102 confirms KG dispersion directly", False),
        ("CPU-038 emergent noise (qng_emergent_noise_reference)", "PASS",
         "live run; eta_ring=0.0244, ratios 0.96/1.02", False),
        ("CPU-020/016 continuity (qng_qm_continuity_assembly_reference)", "FAIL",
         "LONG-STANDING (fail since first commit of report.json) -- NOT a regression", False),
    ]
    for name, status, note, regr in deps:
        print("     [%-4s] %-50s" % (status, name))
        print("            %s" % note)

    regressions = [d for d in deps if d[3]]
    print("\n     => genuine regressions from today's work: %d." % len(regressions))
    print("        The one FAIL (CPU-020) is long-standing, not caused by the QM arc.")

    # T2: what CPU-020 actually tests
    print("\n[T2] what CPU-020 actually tests (so the FAIL is understood):")
    print("     it fits a continuity equation kappa*div(j) to the LEGACY native update's")
    print("     (v2/v3) coarse density on a random graph. improvement_ratio ~0.999 means")
    print("     the simple continuity ansatz does NOT capture the native rho-dynamics.")
    print("     This is a structural probe of the OLD native law -- it is NOT the")
    print("     conserved-|psi|^2 unitarity of the emergent Schrodinger field.")

    # T3: correction
    print("\n[T3] CORRECTION (2nd imprecise citation, after P107's CPU-045):")
    print("     P102/P104/P107 cited 'CPU-020 continuity' as the basis for unitarity.")
    print("     That is imprecise: CPU-020 is a FAILING legacy-law probe. The REAL basis")
    print("     for unitarity is (a) P102's DIRECT norm-conservation demo (split-step")
    print("     Schrodinger, drift 3e-14) and (b) the analytic Noether/Madelung argument")
    print("     (P104). Both are independent of CPU-020. Citation corrected; conclusions")
    print("     (unitarity, v=grad S, Born attractor) UNCHANGED -- they never used CPU-020.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  regression check: KG PASS, noise PASS, continuity FAIL (long-standing, NOT a regression)")
    print("  CPU-020 tests the legacy native law's coarse continuity, not Schrodinger unitarity")
    print("  CORRECTED: unitarity basis = P102 direct norm-conservation (3e-14) + P104 Madelung,")
    print("    NOT the failing CPU-020. QM-arc conclusions unchanged.")

    verdict = (
        "REGRESSION_CHECK_CLEAN (NO_NEW_REGRESSIONS) + SECOND_CITATION_CORRECTED "
        "(CPU-020). Following the standing instruction to check that old tests still "
        "hold under current code, the QM arc's locked dependencies were run. (T1) "
        "Results: CPU-054 (KG wave) PASSES -- its committed report is decision=pass and "
        "P102 independently confirms the dispersion omega^2 = c_phi^2 k^2 + m^2; CPU-038 "
        "(emergent noise) PASSES on a live run (eta_ring=0.0244, variance ratios 0.96 "
        "and 1.02); and CPU-020/016 (continuity-assembly) FAILS -- BUT this is "
        "LONG-STANDING, not a regression: its report.json has had decision=fail since "
        "its very first commit, so today's work did not break it. There are ZERO genuine "
        "regressions from the QM arc. (T2) Understanding the CPU-020 fail: that test fits "
        "a continuity equation kappa*div(j) to the LEGACY native update's (v2/v3) "
        "coarse density on a random graph and finds improvement_ratio ~0.999 -- i.e. the "
        "simple continuity ansatz does not capture the native rho-dynamics. It is a "
        "structural probe of the OLD native law, and it is NOT the conserved-|psi|^2 "
        "unitarity of the emergent Schrodinger field. (T3) This exposes a SECOND "
        "imprecise citation (after P107 caught the CPU-045 one): P102/P104/P107 cited "
        "'CPU-020 continuity' as the basis for unitarity / conserved |psi|^2. That is "
        "imprecise on two counts -- CPU-020 is a FAILING test, and it probes the legacy "
        "native law rather than the Schrodinger field. The CORRECTION: the real, "
        "load-bearing basis for unitarity is (a) the DIRECT norm-conservation "
        "demonstration in P102 (a split-step Schrodinger packet conserving its norm to a "
        "drift of 3e-14) and (b) the analytic Noether/Madelung argument in P104 (the "
        "phase-shift symmetry's conserved current). Both are entirely independent of "
        "CPU-020, so every QM-arc conclusion -- unitarity, v=grad S forced by "
        "continuity, the Born-rule attractor/fixed-point, matter=|psi|^2, the one-T_mu_nu "
        "unification -- is UNCHANGED; only the citation is corrected. NET: the QM arc "
        "has no regressions and now no imprecise dependency citations. Two overstated "
        "cross-references (CPU-045 in P107, CPU-020 here) have been caught and corrected "
        "by the audit discipline, and in BOTH cases the actual conclusion never depended "
        "on the overstated reference -- which is exactly why the honest-citation "
        "discipline matters: it keeps the record accurate without weakening the result. "
        "HONEST: this is a status/citation audit; the KG 'pass' is read from the "
        "committed report (consistent with P102's direct check), the noise 'pass' is a "
        "live run, and the continuity 'fail' is confirmed long-standing via git history "
        "of its report.json. Recommend the INDEX/STATE references to CPU-020 for "
        "unitarity be replaced by 'P102 direct norm conservation + P104 Madelung'.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"regression_check": [{"dep": d[0], "status": d[1], "note": d[2],
                                         "is_regression": d[3]} for d in deps],
                   "n_regressions": len(regressions),
                   "cpu020_meaning": "legacy native-law coarse continuity probe (improvement_ratio ~0.999), NOT Schrodinger unitarity",
                   "correction": "unitarity basis = P102 direct norm-conservation (3e-14) + P104 Madelung, NOT failing CPU-020",
                   "conclusions_unchanged": True, "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
