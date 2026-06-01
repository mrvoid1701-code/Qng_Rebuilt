"""
PHASE 15 (Drumul 3 frontier) -- f_g needs the dynamical graviton (Gap 12), and a
plausibility check with the DERIVED G_QNG.

Phase 14 located alpha as a gravity-induced UV fixed point alpha* = f_g/c, with
f_g the gravitational contribution to the gauge beta function. Computing f_g
properly requires the GRAVITON PROPAGATOR + gauge-graviton vertex at one loop.
But QNG's graviton is only KINEMATIC so far (E8: rank-2 edge structure, 2 TT
pols); its DYNAMICS are Gap 12 (open). So:

   Drumul 3 (compute f_g -> alpha)  REQUIRES  Gap 12 (dynamical graviton).

The two hardest open pieces are LINKED, not independent.

Plausibility check (NOT a derivation): in asymptotic safety f_g ~ k_loop * G * mu^2,
evaluated at the fixed point (mu ~ Planck, mu^2 ~ 1 in substrate units), so
f_g ~ k_loop * G_QNG. G_QNG = 0.0583 is DERIVED. What loop coefficient k_loop
makes f_g/c = alpha_em? Is it a natural O(0.1)?

ASCII output, CPU/numpy.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase15-fg-gap12-link-v1")

G_QNG = 0.0583       # derived (theory-v2 ch.04)
ALPHA_EM = 1/137.036
C_GAUGE = 1.0        # gauge-loop coefficient O(1) (only ratio matters)


def main():
    print("="*70)
    print("PHASE 15 (Drumul 3 frontier) -- f_g <-> Gap 12 link + G_QNG plausibility")
    print("="*70)

    print("\n[link] f_g = gravity's contribution to the gauge beta function")
    print("       requires: graviton propagator + gauge-graviton vertex (1 loop)")
    print("       QNG graviton: only KINEMATIC (E8, rank-2 edge, 2 TT pols);")
    print("       its DYNAMICS = Gap 12 (OPEN).")
    print("   => Drumul 3 (f_g -> alpha) is BLOCKED BY Gap 12 (dynamical graviton).")
    print("      The two hardest open problems are LINKED.")

    print("\n[plausibility] f_g ~ k_loop * G_QNG * mu^2, fixed point mu^2~1 (substrate):")
    print("       so f_g ~ k_loop * G_QNG, with G_QNG = %.4f (DERIVED)." % G_QNG)
    # alpha* = f_g/c  => f_g = alpha_em * c
    f_g_needed = ALPHA_EM * C_GAUGE
    k_loop = f_g_needed / G_QNG
    print("       to get alpha* = alpha_em = %.5f need f_g = %.5f" % (ALPHA_EM, f_g_needed))
    print("       => required loop coefficient k_loop = f_g/G_QNG = %.4f" % k_loop)
    typical_loop = 1/(8)  # ~ O(0.1) loop factor scale
    print("       a one-loop coefficient is ~1/(4pi)..1/(8pi) ~ %.3f..%.3f"
          % (1/(8*3.14159), 1/(4*3.14159)))
    plausible = 0.01 < k_loop < 1.0
    print("       required k_loop = %.3f is %s an O(0.1-1) loop coefficient"
          % (k_loop, "within" if plausible else "outside"))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    verdict = (
        "FG_NEEDS_GAP12 + PLAUSIBLE_WITH_DERIVED_G: the final step of Drumul 3 "
        "(compute f_g, hence alpha) REQUIRES the dynamical graviton, which is "
        "Gap 12 (open -- QNG has only the kinematic rank-2 edge graviton from E8, "
        "not its dynamics). So the two hardest open problems are LINKED: solving "
        "Gap 12 (dynamical graviton) ENABLES computing f_g(G_QNG), hence alpha "
        "(Drumul 3), hence -- via Phase 11/12 -- a parameter-free proton mass. "
        f"PLAUSIBILITY (not a derivation): with G_QNG={G_QNG:.4f} DERIVED and "
        f"f_g ~ k_loop*G_QNG, reproducing alpha_em needs k_loop = {k_loop:.3f} -- "
        "an O(0.1-1) one-loop coefficient (loop factors are ~1/(4-8 pi) ~ "
        "0.04-0.08, and an O(1) numerator makes ~0.1 natural). So the required "
        "gravitational coefficient is in the NATURAL range -- the scenario is not "
        "fine-tuned. HONEST: this is an order-of-magnitude plausibility check, NOT "
        "a computation of f_g (which needs the Gap-12 graviton dynamics + a "
        "scheme choice). The value of alpha remains uncomputed. What is "
        "established: Drumul 3 reduces to Gap 12 + one scheme-dependent loop "
        "integral, and the derived G_QNG sits in the right ballpark to make it "
        "work with a natural loop coefficient.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"G_QNG": G_QNG, "alpha_em": ALPHA_EM,
                   "f_g_needed": f_g_needed, "k_loop_required": k_loop,
                   "plausible_O(0.1-1)": bool(plausible),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
