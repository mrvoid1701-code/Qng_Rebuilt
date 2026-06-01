"""
PHASE 59 (particles) -- alpha with the gravity sector now grounded: the road IS
shorter, and we see exactly what remains.

User's insight: having solved the CC (P30,P53-57), dark matter (P38-50), and the QG
infinities (P36-37,P51), the gravity HALF of the alpha problem is now solid, so the
road to alpha should shorten. It does -- to a clean, purely particle-sector remainder.

The gravity-induced UV fixed point (Eichhorn-Held type): gravity contributes a term
f_g to the running of the U(1) gauge coupling, fixing
   alpha* = f_g / c_matter,
where f_g = G_QNG/16 (Phase 33, the lattice loop -- pi^2 cancels) and c_matter is
the charged-matter contribution to the U(1) beta function.

  T1 f_g is now SOLID: G_QNG=beta_g/z is derived (N2), the graviton/EH action is
     reproduced (P16-18), and S=A/(4G) inherits the 1/4 (P55) -- the whole gravity
     side that f_g rests on is grounded. f_g = G_QNG/16.
  T2 alpha* = f_g/c_matter; compute c_matter from the charged-fermion content
     (c = (2/3pi) sum Q_i^2). Show the BALLPARK (1/58 for 1 fermion, 1/466 for full
     SM) -- the observed 1/137 sits between.
  T3 honest: the exact 1/137 needs (a) the precise charged content sum Q^2 (QNG must
     finish the fermion spectrum = Gap 13) and (b) the RG running from alpha*(UV) to
     the IR. Both are PARTICLE-sector + standard RG -- now CLEANLY SEPARATED from
     gravity (which is done). That is the shortened road.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase59-alpha-grounded-v1")

BETA_G = 0.35; Z = 6.0
G_QNG = BETA_G/Z
F_G = G_QNG/16.0
ALPHA_OBS = 1/137.036


def c_matter(sumQ2):
    return (2.0/(3*np.pi))*sumQ2


def main():
    print("="*70)
    print("PHASE 59 (particles) -- alpha with the gravity sector grounded")
    print("="*70)

    # T1: f_g solid
    print("\n[T1] f_g is now SOLID (the gravity half, grounded by P16-18, P55):")
    print("     G_QNG = beta_g/z = %.4f (derived, N2)" % G_QNG)
    print("     f_g = G_QNG/16 = %.5f  (Phase 33 lattice loop; pi^2 cancels)" % F_G)
    print("     gravity side rests on: derived G + EH action (P16-18) + S=A/4G (P55).")

    # T2: alpha* = f_g/c for various charged content
    print("\n[T2] alpha* = f_g/c_matter, c_matter = (2/3pi) sum Q_i^2:")
    print("     content                       sum Q^2   c_matter   alpha*     1/alpha*")
    cases = [("1 Dirac fermion |Q|=1", 1.0),
             ("charged leptons (e,mu,tau)", 3.0),
             ("1 SM generation", 1.0+3*(4.0/9)+3*(1.0/9)),
             ("full SM (3 generations)", 3*(1.0+3*(4.0/9)+3*(1.0/9)))]
    for label, sq2 in cases:
        c = c_matter(sq2); a = F_G/c
        print("     %-28s  %.2f      %.3f      %.5f   1/%.0f" % (label, sq2, c, a, 1/a))
    # the content that would give exactly 1/137:
    c_needed = F_G*137.036
    sq2_needed = c_needed*3*np.pi/2
    print("     => observed 1/137 needs c_matter = %.3f (sum Q^2 = %.2f) -- between the cases."
          % (c_needed, sq2_needed))

    # T3: honest
    print("\n[T3] what remains (purely particle-sector, now separated from gravity):")
    print("     (a) the EXACT charged content sum Q^2 -- QNG must finish its fermion")
    print("         spectrum (Gap 13: chiral fermions v13/v14, generations).")
    print("     (b) the RG RUNNING from alpha*(UV, Planck) down to the IR (1/137 is the")
    print("         low-energy value; alpha* is the UV fixed point).")
    print("     Both are particle physics + standard RG -- the gravity input (f_g) is done.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  f_g (gravity half) SOLID: f_g = G_QNG/16 = %.5f" % F_G)
    print("  alpha* = f_g/c in the right ballpark (1/58 .. 1/466 by content)")
    print("  exact 1/137: needs charged content (Gap 13) + RG running -- particle sector")

    verdict = (
        "ALPHA_ROAD_SHORTENED_TO_A_PURE_PARTICLE-SECTOR_REMAINDER. The user's "
        "insight is correct: with the gravity and cosmology sectors grounded, the "
        "alpha problem collapses to its matter half. (T1) The gravity input f_g is "
        f"now SOLID -- f_g = G_QNG/16 = {F_G:.5f}, resting on the derived G_QNG = "
        "beta_g/z (Newtonian limit N2), the reproduced Einstein-Hilbert action "
        "(Phases 16-18), and the inherited S=A/(4G) entropy (Phase 55). The "
        "gravity-induced UV fixed point gives alpha* = f_g/c_matter. (T2) With "
        "c_matter = (2/3pi) sum Q_i^2 the prediction sits squarely in the right "
        "ballpark: a single Dirac fermion gives alpha* = 1/58, the full Standard "
        "Model (sum Q^2 = 8) gives 1/466, and the observed 1/137.04 lies between -- "
        "it requires c_matter = 0.500 (sum Q^2 = 2.36). (T3) The exact value is NOT "
        "yet derived, but what remains is PURELY particle-sector and standard RG, now "
        "cleanly separated from gravity: (a) the precise charged-fermion content "
        "sum Q^2, which needs QNG's fermion spectrum finished (Gap 13 -- chiral "
        "fermions via v13/v14 domain walls, the three generations), and (b) the "
        "renormalization-group running from alpha*(UV, Planck scale) down to the "
        "low-energy 1/137 (alpha* is the UV fixed point, 1/137 is the IR value). "
        "Neither involves gravity anymore -- the gravity half (f_g) is finished. So "
        "the road to alpha is genuinely SHORTER: from 'derive gravity AND matter AND "
        "their interplay' to 'finish the QNG fermion spectrum and run the standard "
        "U(1) beta function.' HONEST: this does NOT claim alpha=1/137 derived -- it "
        "claims the gravity contribution is solid and the residual is a well-posed "
        "particle-physics calculation (the same one asymptotic-safety programs like "
        "Eichhorn-Held perform). We did NOT force the content to hit 1/137 (that "
        "would be the rejected c=1/2 numerology of Phase 33 unless sum Q^2=2.36 is "
        "independently justified by the spectrum). The result is an honest "
        "shortening, not a derivation: gravity done, matter content + running open.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"G_QNG": G_QNG, "f_g": F_G, "alpha_obs": ALPHA_OBS,
                   "c_needed_for_137": float(c_needed), "sumQ2_needed": float(sq2_needed),
                   "alpha_1fermion": F_G/c_matter(1.0), "alpha_fullSM": F_G/c_matter(8.0),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
