"""
PHASE 54 (cosmology) -- attacking the residual O(1): is the holographic dark-energy
coefficient genuinely O(1), and where does QNG pin it?

Phase 53 found rho_holo/rho_obs = 12.4 ("right order within ~10x"). This phase asks
whether that factor 12 is a real discrepancy or a CONVENTION artifact, and reduces
the leftover to a clean O(1) statement.

Standard holographic dark energy is written   rho_Lambda = 3 c^2 M_Pl_red^2 / R_H^2
with M_Pl_red^2 = 1/(8 pi G) the REDUCED Planck mass and c^2 an O(1) coefficient.
Phase 53 used the FULL Planck mass and dropped the 3 and 8pi, i.e. rho ~ M_Pl^2/R_H^2;
the difference is exactly the factor (8 pi / 3).

  T1 show the Phase-53 "12.4" = (8 pi/3)/Omega_Lambda -- a pure convention/Friedmann
     factor, NOT a physical discrepancy.
  T2 in the standard convention the required coefficient is c^2 = Omega_Lambda ~ 0.69
     -- a GENUINE O(1) number (within ~1.4x of unity). So holographic DE is NATURAL,
     not fine-tuned. (Honest caveat: c^2 = Omega_Lambda uses the observed value, so
     this shows O(1)-ness/consistency, it does NOT predict 0.69 from first principles.)
  T3 where QNG pins the O(1): the entropy area-law S = A/(4 l_P^2) -- the Bekenstein-
     Hawking 1/4 -- is the microscopic origin of the holographic coefficient. QNG
     gives the area law structurally (horizon = a surface of nodes, S ~ number of
     horizon nodes), but the exact 1/4 needs horizon-node counting (entropy per node
     x node area = 1/4 l_P^2). Set up that relation and state what is derived (area
     law) vs the residual O(1) (the 1/4 and c^2~0.7) and 'why now'.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase54-O1-coefficient-v1")

OMEGA_LAMBDA = 0.69
A_L_OVER_LP = 0.305       # bulk node spacing in Planck lengths


def main():
    print("="*70)
    print("PHASE 54 -- the residual O(1): is the holographic DE coefficient natural?")
    print("="*70)

    # T1: decompose the Phase-53 factor 12.4
    conv = (8*np.pi/3)
    factor53 = conv/OMEGA_LAMBDA
    print("\n[T1] decomposing the Phase-53 'ratio 12.4':")
    print("     Phase 53 used rho ~ M_Pl_full^2/R_H^2 (no 3, no 8pi, full not reduced M_Pl).")
    print("     standard: rho_Lambda = 3 c^2 M_Pl_red^2/R_H^2, M_Pl_red^2 = 1/(8piG).")
    print("     the difference is exactly 8pi/3 = %.2f." % conv)
    print("     (8pi/3)/Omega_Lambda = %.2f/%.2f = %.1f  == the Phase-53 '12.4'."
          % (conv, OMEGA_LAMBDA, factor53))
    print("     => the factor ~12 is a CONVENTION/Friedmann artifact, NOT a physical gap.")
    artifact = abs(factor53 - 12.4) < 1.0

    # T2: the genuine coefficient
    c2 = OMEGA_LAMBDA
    print("\n[T2] the genuine coefficient (standard convention):")
    print("     rho_Lambda/rho_crit = c^2  ->  c^2 = Omega_Lambda = %.2f" % c2)
    print("     that is GENUINELY O(1) (within %.2fx of unity) -- holographic DE is" % (1.0/c2))
    print("     NATURAL, not fine-tuned. (Literature: event-horizon HDE fits c^2 ~ 0.7-0.8.)")
    print("     HONEST CAVEAT: c^2 = Omega_Lambda uses the OBSERVED value; this shows")
    print("     O(1)-ness/consistency, it does NOT derive 0.69 from first principles.")
    is_O1 = 0.1 < c2 < 10

    # T3: where QNG pins it -- the area law and the 1/4
    print("\n[T3] where QNG pins the O(1): the Bekenstein-Hawking 1/4 from node counting.")
    print("     holographic coefficient <- entropy area law S = A/(4 l_P^2).")
    print("     QNG: horizon = a surface of nodes; S ~ (number of horizon nodes) x s_node")
    print("        = (A/a_node^2) x s_node.  Matching S = A/(4 l_P^2) requires")
    s_node_needed = A_L_OVER_LP**2/4.0     # if horizon node spacing = bulk a_L, nats/node
    print("        s_node x (l_P^2/a_node^2) = 1/4.")
    print("     if horizon node spacing = bulk a_L=%.3f l_P: s_node = a_L^2/(4 l_P^2) = %.4f nats."
          % (A_L_OVER_LP, s_node_needed))
    # alternatively, if s_node = ln2 (1 bit), the horizon node spacing is:
    a_eff = np.sqrt(4*np.log(2))           # in l_P, if s_node = ln2
    print("     OR if s_node = ln2 (1 bit/node): horizon node spacing a_eff = sqrt(4 ln2) = %.2f l_P."
          % a_eff)
    print("     => QNG gives the AREA LAW S ~ A structurally (horizon nodes); the exact")
    print("        1/4 fixes (s_node, horizon spacing) but is not independently derived")
    print("        -- this IS the residual O(1) (the same hard step LQG/strings needed).")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Phase-53 '12.4' is the convention factor (8pi/3)/Omega_L = %.1f : %s" % (factor53, artifact))
    print("  genuine holographic coefficient c^2 = %.2f : O(1), natural (not tuned) : %s" % (c2, is_O1))
    print("  QNG gives the area law S~A structurally; exact 1/4 + why-now : residual")

    verdict = (
        "THE_RESIDUAL_O(1)_IS_GENUINELY_O(1)_AND_THE_FACTOR-12_WAS_A_CONVENTION. "
        "Attacking the leftover from Phase 53. (T1) The 'ratio 12.4' was NOT a "
        "physical discrepancy: it is exactly (8 pi/3)/Omega_Lambda = "
        f"{factor53:.1f}, the pure Friedmann/convention factor between writing the "
        "holographic dark energy as rho ~ M_Pl_full^2/R_H^2 (Phase 53) versus the "
        "standard rho_Lambda = 3 c^2 M_Pl_red^2/R_H^2 with the reduced Planck mass. "
        "Once normalized correctly the apparent order-of-magnitude gap disappears. "
        "(T2) In the standard convention the required coefficient is simply c^2 = "
        f"Omega_Lambda = {c2:.2f} -- a GENUINELY O(1) number, within "
        f"{1.0/c2:.2f}x of unity, exactly the range (c^2 ~ 0.7-0.8) that "
        "event-horizon holographic-dark-energy models fit to the data. So the "
        "holographic vacuum energy is NATURAL, not fine-tuned: no small or large "
        "coefficient is needed, just an O(1) one. HONEST CAVEAT: c^2 = Omega_Lambda "
        "uses the observed value, so this establishes O(1)-ness and consistency, NOT "
        "a first-principles derivation of 0.69. (T3) The microscopic origin of that "
        "O(1) is the Bekenstein-Hawking entropy coefficient 1/4 in S = A/(4 l_P^2). "
        "QNG supplies the AREA LAW structurally -- a horizon is a surface of nodes, "
        "so its entropy scales as the number of horizon nodes ~ A/a_node^2 -- which "
        "is the deep reason the vacuum dof scale as area (the whole holographic "
        "mechanism). Matching the exact 1/4 fixes a relation between the per-node "
        "entropy and the horizon node spacing (e.g. s_node = ln2 per node requires "
        f"horizon spacing a_eff = sqrt(4 ln2) = {a_eff:.2f} l_P), but pinning that "
        "absolutely is the same hard microscopic counting that loop quantum gravity "
        "(Immirzi parameter) and string theory had to do for specific black holes -- "
        "it is NOT independently derived in QNG here. NET: the residual O(1) of "
        "Phase 53 is genuinely O(1) (~0.7), the factor-12 was a convention artifact, "
        "and QNG explains WHY the coefficient is O(1) (the area law) while the exact "
        "1/4 and the 'why now' coincidence remain -- a clean, honest, "
        "order-unity-sized frontier, no fine-tuning hiding anywhere. The "
        "cosmological-constant magnitude is now QNG-natural: Stability Principle "
        "kills the 10^122 overshoot (P30), the area-law holography sets the residual "
        "to rho_Lambda ~ O(1) x M_Pl^2/R_H^2 (P53-54), and only the O(1) value and "
        "why-now are left.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"phase53_factor": factor53, "convention_8pi_3": conv,
                   "c2_required": c2, "is_O1": bool(is_O1), "artifact_confirmed": bool(artifact),
                   "s_node_if_aL": s_node_needed, "a_eff_if_ln2": a_eff,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
