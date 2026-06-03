"""
theory-test-1 / RUNG 6 -- head-to-head: the causal-set box vs QNG, at the level QNG reached.
The payoff of the 'is the box unique?' experiment: where the two independent QG containers
CONVERGE and where they DIVERGE, axis by axis (constraints C1-C7 + the constants + QM).

ASCII output, CPU/numpy.
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "tt1-rung6-comparison-vs-qng-v1")


def main():
    print("="*70)
    print("theory-test-1 / RUNG 6 -- causal-set box  vs  QNG  (the comparison)")
    print("="*70)

    # (axis, QNG, causal-set/tt1, verdict)
    rows = [
        ("primitive", "fields (sigma_g,sigma_m,chi,phi) on a graph", "events + causal order only", "DIVERGE"),
        ("C3 discrete/finite", "yes (graph nodes)", "yes (locally finite order)", "CONVERGE"),
        ("C6 background-indep", "NO -- fixed cubic lattice (a background)", "YES -- no grid, geometry from order", "tt1 STRONGER"),
        ("C7 Lorentz", "emergent only; lattice breaks it; LIV eta_LV signature", "EXACT in the mean (Poisson sprinkling)", "DIVERGE (both testable)"),
        ("dimension", "put in by hand (3+1 cubic)", "DERIVED from order (rung1, err<0.05)", "tt1 STRONGER"),
        ("C1 GR limit", "coarse-grained gradients; Shapiro/bending (DER-QNG-044)", "BD d'Alembertian from interval counts (rung3, R2=0.94)", "CONVERGE (both reach it)"),
        ("metric/proper time", "lattice distance (frame-dependent)", "longest chain = geodesic (rung2)", "CONVERGE (tt1 Lorentz-clean)"),
        ("Lambda (C5)", "= 0 EXACTLY (Stability) + separate holographic V_0", "~ +-1/sqrt(V) ~ 1e-122, nonzero (Sorkin, rung4)", "DIVERGE (sharp)"),
        ("c, G, hbar", "derived/identified (c_phi, G=beta/z [ID], hbar)", "scaffolding (set by l_Planck); not derived", "QNG STRONGER"),
        ("C2 QM kinematics", "Schrodinger=NR limit of KG, unitarity, [x,p]=ihbar", "sum-over-causets: superposition+interference (rung5)", "CONVERGE"),
        ("Born rule", "dynamical attractor+fixed point (P103/104)", "OPEN (quantum measure only)", "QNG STRONGER"),
        ("matter sector", "matter=|psi|^2, rings/Skyrmions, hadron spectrum", "OPEN (causal-set frontier)", "QNG STRONGER"),
        ("UV-finite (C4)", "Planck cutoff (lattice)", "Planck cutoff (discreteness)", "CONVERGE"),
        ("famous prediction", "eta_LV (CTA), no 4th gen, Koide m_tau", "Lambda scale ~1e-122 BEFORE 1998 obs.", "both have one"),
    ]

    print("\n  %-20s | %-42s | %-44s | %s" % ("AXIS", "QNG", "causal-set (theory-test-1)", "verdict"))
    print("  " + "-"*120)
    conv = div = q_str = t_str = 0
    for ax, q, t, v in rows:
        print("  %-20s | %-42s | %-44s | %s" % (ax, q[:42], t[:44], v))
        if v.startswith("CONVERGE"): conv += 1
        elif v.startswith("DIVERGE"): div += 1
        elif v.startswith("QNG"): q_str += 1
        elif v.startswith("tt1"): t_str += 1

    print("\n  tally: CONVERGE %d | DIVERGE %d | QNG-stronger %d | tt1-stronger %d" % (conv, div, q_str, t_str))

    print("\n" + "="*70)
    print("VERDICT -- is the QG box UNIQUE?")
    print("="*70)
    print("  NO -- it is a FAMILY. Two independent discrete boxes, same constraints (C1-C7):")
    print("  - CONVERGE on the broad shape: discrete/finite, Lorentzian geometry, a GR limit,")
    print("    quantum amplitudes, UV-finite. (The 'shape of the box' IS forced.)")
    print("  - DIVERGE on specifics: Lambda (=0 vs ~1e-122), Lorentz (emergent vs exact),")
    print("    background-independence (tt1 wins), and depth of QM/matter (QNG wins).")
    print("  => the CONSTRAINTS are nearly unique; the PRIMITIVE choice still decides the")
    print("     specifics. Different boxes pay off in different places.")

    verdict = (
        "IS_THE_QG_BOX_UNIQUE? -- NO, IT_IS_A_FAMILY: THE_CONSTRAINTS_ARE_NEARLY_UNIQUE_"
        "BUT_THE_PRIMITIVE_DECIDES_THE_SPECIFICS. This rung is the payoff of the whole "
        "experiment: theory-test-1 was built from the same QG constraints as QNG (C1-C7) "
        "but from a deliberately different primitive -- pure causal order rather than "
        "fields on a graph -- and climbed the SAME ladder (dimension -> metric -> GR "
        "limit -> a constant -> quantum amplitudes). Comparing the two boxes at the level "
        "QNG reached: they CONVERGE on the broad shape of quantum gravity -- both are "
        "discrete/finite (C3, C4), both reconstruct a Lorentzian geometry, both reach a "
        "GR limit (QNG via coarse-grained gradients + Shapiro/bending; the causal set via "
        "the Benincasa-Dowker d'Alembertian from interval counts, R2=0.94), and both "
        "support quantum amplitudes (C2). That convergence is itself a RESULT: the "
        "'shape of the box' (the constraints) is largely FORCED -- you cannot build a QG "
        "without discreteness/finiteness, an emergent Lorentzian geometry, a GR limit, "
        "and quantum amplitudes. But the boxes DIVERGE sharply on the specifics, and this "
        "is where the experiment is most informative: (1) the COSMOLOGICAL CONSTANT -- "
        "QNG gives Lambda = 0 exactly (Stability Principle) plus a separate holographic "
        "dark energy, whereas the causal set gives Lambda ~ +-1/sqrt(V) ~ 1e-122, "
        "nonzero and fluctuating, matching the observed scale from one counting argument "
        "(Sorkin, famously pre-1998); (2) LORENTZ INVARIANCE -- exact-in-the-mean for the "
        "causal set (Poisson sprinkling, no preferred frame) versus emergent-only for "
        "QNG (its cubic lattice breaks Lorentz, leaving the testable eta_LV signature); "
        "(3) BACKGROUND INDEPENDENCE -- the causal set is fully background-free and even "
        "DERIVES the spacetime dimension, where QNG puts 3+1 in by hand on a fixed "
        "lattice (the causal set is structurally stronger here, C6); and conversely (4) "
        "QUANTUM DYNAMICS + MATTER -- QNG is far stronger, having derived the Schrodinger "
        "equation, the Born rule as a dynamical attractor, decoherence, and matter=|psi|^2 "
        "from a concrete v8 Hamiltonian, while the causal set has only the quantum "
        "kinematics (sum-over-causets interference) with the matter sector and Born rule "
        "open; (5) the dimensionful constants c, G, hbar are derived/identified in QNG "
        "but mere scaffolding (set by the Planck length) in the bare causal set. NET "
        "ANSWER to your question 'is there another box, and can we see the difference?': "
        "YES, there is another box (we built one from pure causal order), and the "
        "difference is now explicit -- the QG CONSTRAINTS are nearly unique (every viable "
        "box converges on discreteness + Lorentzian geometry + GR limit + quantum "
        "amplitudes), but the PRIMITIVE you choose decides the rest: the causal set wins "
        "on foundations (background independence, exact Lorentz, the Lambda scale), QNG "
        "wins on dynamics (QM, matter, the particle spectrum). Quantum gravity is a "
        "FAMILY of containers sharing a forced skeleton and differing in the flesh. "
        "HONEST: theory-test-1 reached rungs 1-5 using standard causal-set results "
        "(Myrheim-Meyer dimension, longest-chain proper time, Benincasa-Dowker "
        "d'Alembertian, Sorkin's Lambda, sum-over-causets) reproduced numerically; it did "
        "NOT independently re-derive everything from zero, and its matter/dynamics sector "
        "is genuinely thin -- so the comparison is fair: QNG is the more developed box on "
        "dynamics, the causal set the cleaner box on foundations. The convergence on the "
        "skeleton and the divergence on Lambda are the two firm conclusions. No numbers "
        "forced anywhere in this track.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"rows": [{"axis": a, "qng": q, "causal_set": t, "verdict": v} for (a, q, t, v) in rows],
                   "tally": {"converge": conv, "diverge": div, "qng_stronger": q_str, "tt1_stronger": t_str},
                   "answer": "box NOT unique -- a family; constraints nearly unique, primitive decides specifics",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
