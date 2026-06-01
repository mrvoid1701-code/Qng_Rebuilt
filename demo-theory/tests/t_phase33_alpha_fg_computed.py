"""
PHASE 33 (deriving alpha) -- compute f_g cleanly from the QNG lattice, and
SCRUTINIZE the alpha = beta_g/48 = 1/137 coincidence (real or numerology?).

The lattice removes the scheme ambiguity, so f_g is computable:
  g_grav* = G k^2 at the cutoff. In lattice units (a=1) the BZ cutoff is k=pi, so
  g_grav* = G_QNG * pi^2,  and  f_g = g_grav*/(16 pi^2) = G_QNG/16  (the pi^2 cancels!)
  -> f_g = G_QNG/16 = (beta_g/z)/16  -- a CLEAN QNG number, no free parameter.

Then the gravity-induced fixed point gives  alpha* = f_g/c, c = the U(1) beta
coefficient (charged-matter content).

TEMPTING COINCIDENCE: with c=1/2,  alpha* = G_QNG/8 = beta_g/(8z) = 0.35/48 =
1/137.1 -- 0.08% from observed 1/137.04. We test whether c=1/2 is JUSTIFIED or a
numerological tuning.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase33-alpha-fg-v1")

BETA_G = 0.35
Z = 6.0
G_QNG = BETA_G/Z
ALPHA_EM = 1/137.036


def main():
    print("="*70)
    print("PHASE 33 (deriving alpha) -- f_g computed; scrutinize beta_g/48 = 1/137")
    print("="*70)

    f_g = G_QNG/16.0
    print("\n  f_g = g_grav*/(16 pi^2) = (G_QNG pi^2)/(16 pi^2) = G_QNG/16 = %.5f" % f_g)
    print("       (CLEAN: pi^2 cancels; the lattice fixes the scheme, no free regulator)")

    print("\n  alpha* = f_g / c   (c = U(1) beta coefficient = charged-matter content)")
    print("    c value          alpha* = f_g/c        1/alpha*")
    for c, label in [(2/(3*np.pi), "QED 1 Dirac fermion c=2/3pi"),
                     (0.5, "c=1/2 (the tempting value)"),
                     (4/(3*np.pi), "QED 2 fermions"),
                     (41/(10*2*np.pi), "SM hypercharge b_Y=41/10")]:
        a = f_g/c
        print("    %-28s %.5f   = 1/%.1f" % (label, a, 1/a))

    # the tempting coincidence
    alpha_tempt = BETA_G/(8*Z)
    print("\n  TEMPTING: alpha = beta_g/(8z) = %.6f = 1/%.2f  vs observed 1/137.04 (%.2f%%)"
          % (alpha_tempt, 1/alpha_tempt, 100*abs(alpha_tempt-ALPHA_EM)/ALPHA_EM))

    # scrutiny: what c does the OBSERVED alpha require, vs physical QED?
    c_needed = f_g/ALPHA_EM
    c_qed = 2/(3*np.pi)
    print("\n  SCRUTINY:")
    print("    c needed for observed alpha_em = f_g/alpha = %.4f" % c_needed)
    print("    physical QED (1 Dirac fermion) c = 2/3pi    = %.4f" % c_qed)
    print("    ratio c_needed/c_QED = %.2f" % (c_needed/c_qed))
    print("    -> c=1/2 (giving 1/137) is %.1fx the single-fermion QED value;" % (0.5/c_qed))
    print("       it is NOT the physical QED coefficient. With physical c=2/3pi,")
    print("       QNG gives alpha* = %.5f = 1/%.0f (right ORDER, not 1/137)."
          % (f_g/c_qed, 1/(f_g/c_qed)))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    is_numerology = abs(0.5 - c_qed)/c_qed > 0.3   # c=1/2 differs from physical QED
    print("  beta_g/48 = 1/137 to 0.08%% : YES (striking)")
    print("  but it requires c=1/2, NOT the physical QED c=2/3pi=0.21 : %s" % is_numerology)
    print("  => so the 1/137 coincidence is c-TUNING = likely numerology")

    verdict = (
        "FG_COMPUTED_CLEAN_BUT_1/137_IS_NUMEROLOGY. Genuine progress AND discipline. "
        f"PROGRESS: f_g is now COMPUTED cleanly = G_QNG/16 = {f_g:.5f}, with NO free "
        "parameter and NO scheme ambiguity (the lattice cutoff k=pi makes the pi^2 "
        "cancel: f_g = g_grav*/(16pi^2) = G_QNG pi^2/(16 pi^2) = G_QNG/16). This is "
        "the QNG lattice advantage realized -- f_g is a definite number from the "
        "derived G. Then alpha* = f_g/c with c the U(1) charged-matter beta "
        "coefficient. WITH THE PHYSICAL QED VALUE c=2/(3pi)=0.21 (one Dirac "
        f"fermion), QNG gives alpha* = {f_g/c_qed:.4f} = 1/{1/(f_g/c_qed):.0f} -- the "
        "RIGHT ORDER, but NOT 1/137. DISCIPLINE: there IS a tempting coincidence "
        "alpha = beta_g/(8z) = 0.35/48 = 1/137.1, just 0.08% from observed -- BUT it "
        f"requires c=1/2, which is {0.5/c_qed:.1f}x the physical QED coefficient and "
        "is NOT justified. So the beta_g/48=1/137 'hit' is c-TUNING -- numerology, "
        "NOT a derivation. HONEST RESULT: QNG cleanly computes f_g=G_QNG/16 (a real "
        "advance -- no scheme ambiguity), placing alpha in the right ballpark "
        "(~1/58 with physical c); the exact 1/137 needs the charged-matter content "
        "c pinned (and the full lattice loop coefficient), and the seductive "
        "beta_g/48 coincidence is rejected as unjustified tuning. We do NOT claim "
        "alpha derived -- we claim f_g computed and the numerology caught.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"f_g": f_g, "alpha_tempting_beta_g_48": alpha_tempt,
                   "c_needed": float(c_needed), "c_qed": float(c_qed),
                   "alpha_physical_c": float(f_g/c_qed),
                   "is_numerology": bool(is_numerology), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
