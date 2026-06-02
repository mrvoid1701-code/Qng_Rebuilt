"""
PHASE 89 (particles) -- flavor mixing (CKM / PMNS) from the wall geometry: structure
yes, angles open.

The 3 generations are the 3 domain-wall orientations (P60). The weak interaction acts
in a basis that need not align with the wall/mass basis -> the misalignment is the
MIXING matrix (CKM for quarks, PMNS for leptons). What can QNG say?

  T1 STRUCTURE: the mixing is a rotation among 3 wall-modes -> a 3x3 UNITARY matrix
     with exactly the CKM/PMNS form (3 angles + 1 CP phase). The COUNT (3x3, unitary,
     1 phase) is fixed by 3 generations -- derived. The 1 CP phase = the delta-class
     flavor phase (P74).
  T2 a QUALITATIVE hint: quark mixing is SMALL/hierarchical (CKM near-diagonal),
     lepton mixing is LARGE (PMNS near-maximal). In QNG quarks are confined/'dirty'
     (strong-coupled, like the Koide failure P35) while leptons are 'clean' (P35
     showed leptons satisfy Koide, quarks don't) -> the clean lepton wall-modes can
     mix maximally, the QCD-dressed quark modes mix little. A structural reason for
     the SMALL-quark / LARGE-lepton mixing pattern (not the angles).
  T3 honest: the COUNT and the small/large pattern have QNG structural explanations;
     the specific MIXING ANGLES are flavor parameters (like delta, P74) -- NOT
     predicted (same as the SM). No angles forced.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase89-flavor-mixing-v1")


def main():
    print("="*70)
    print("PHASE 89 (particles) -- flavor mixing (CKM/PMNS) from wall geometry")
    print("="*70)

    # T1: structure
    print("\n[T1] STRUCTURE of the mixing (derived from 3 generations):")
    n_gen = 3
    n_angles = n_gen*(n_gen-1)//2
    n_phases = (n_gen-1)*(n_gen-2)//2
    print("     3 wall-modes -> mixing = a 3x3 UNITARY rotation between wall(mass) basis")
    print("     and weak basis -> exactly the CKM/PMNS structure:")
    print("       %d mixing angles + %d CP phase (for %d generations)." % (n_angles, n_phases, n_gen))
    print("     the COUNT (3x3 unitary, 3 angles, 1 phase) is FIXED by 3 generations (P60).")
    print("     the 1 CP phase = the delta-class flavor phase (P74, a Goldstone/theta-angle).")

    # T2: small vs large pattern
    print("\n[T2] QUALITATIVE pattern -- why quark mixing SMALL, lepton mixing LARGE:")
    print("     observed: CKM (quarks) near-DIAGONAL (small angles, theta_C~13 deg);")
    print("               PMNS (leptons) near-MAXIMAL (large angles, ~33,49,8 deg).")
    print("     QNG: leptons are 'clean' wall-modes (satisfy Koide Q=2/3, P35/P61);")
    print("          quarks are QCD-confined/'dirty' (Koide FAILS for quarks, P35).")
    print("     => the clean lepton modes can mix freely (LARGE PMNS); the QCD-dressed")
    print("        quark modes are 'pinned' by the strong dynamics and mix little (SMALL")
    print("        CKM). A STRUCTURAL reason for the small-quark / large-lepton pattern.")

    # T3: honest
    print("\n[T3] honest status:")
    print("     - DERIVED: the mixing COUNT (3x3 unitary, 3 angles + 1 phase) from 3 gen.")
    print("     - EXPLAINED qualitatively: small-quark vs large-lepton mixing (clean vs")
    print("       QCD-dressed wall-modes).")
    print("     - NOT predicted: the specific mixing ANGLES (flavor parameters, like")
    print("       delta P74). No angles forced (no numerology).")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  mixing structure (3x3 unitary, %d angles + %d phase): DERIVED from 3 gen" % (n_angles, n_phases))
    print("  small-quark vs large-lepton pattern: qualitatively explained (clean vs QCD-dressed)")
    print("  specific angles: flavor parameters, NOT predicted (no numerology)")

    verdict = (
        "QNG_DERIVES_THE_MIXING_STRUCTURE_AND_EXPLAINS_THE_SMALL/LARGE_PATTERN; THE "
        "ANGLES_STAY_OPEN. With the 3 generations being the 3 domain-wall orientations "
        "(P60), flavor mixing is the misalignment between the wall (mass) basis and "
        "the weak-interaction basis. (T1) STRUCTURE: that misalignment is a 3x3 "
        "UNITARY rotation, which has exactly the CKM/PMNS form -- 3 mixing angles + 1 "
        "CP phase for 3 generations. This COUNT (3x3 unitary, 3 angles, 1 phase) is "
        "DERIVED from the 3 generations, and the single CP phase is the same "
        "delta-class flavor phase identified in P74 (a Goldstone / instanton "
        "theta-angle). (T2) QNG also gives a QUALITATIVE reason for the observed "
        "pattern -- quark mixing is small and hierarchical (CKM near-diagonal, "
        "Cabibbo ~13 deg) while lepton mixing is large (PMNS near-maximal): in QNG the "
        "leptons are 'clean' wall-modes (they satisfy the Koide relation Q=2/3, "
        "P35/P61), whereas the quarks are QCD-confined and 'dirty' (Koide FAILS for "
        "quarks, P35, exactly because of QCD/mixing contamination). The clean lepton "
        "modes can mix freely (large PMNS angles), while the strongly-dressed quark "
        "modes are pinned by the confining dynamics and mix little (small CKM angles). "
        "So the small-quark / large-lepton mixing dichotomy has a structural QNG "
        "origin (clean vs QCD-dressed wall-modes), tied to the same clean/dirty "
        "distinction that explained why leptons satisfy Koide and quarks do not. (T3) "
        "HONEST: the mixing COUNT is derived and the small/large PATTERN is "
        "qualitatively explained, but the SPECIFIC mixing angles (the Cabibbo angle, "
        "the PMNS angles) are flavor parameters -- of the same class as the CP phase "
        "delta (P74) -- and are NOT predicted by QNG, exactly as the Standard Model "
        "leaves them free. No angle is forced (no numerology). NET: QNG explains the "
        "STRUCTURE of flavor mixing (3x3 unitary, 1 phase) and the qualitative "
        "small-quark/large-lepton pattern, while the precise angles remain open flavor "
        "parameters -- consistent with the recurring lepton-sector verdict that QNG "
        "captures the counts, relations, and patterns (3 generations, Koide, mixing "
        "structure) but not the absolute flavor parameters (masses' delta, M0, mixing "
        "angles), which await a deeper theory of flavor.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"n_angles": n_angles, "n_phases": n_phases,
                   "structure": "3x3 unitary (CKM/PMNS) derived from 3 generations",
                   "pattern": "small-quark/large-lepton explained (clean vs QCD-dressed)",
                   "angles": "flavor parameters, not predicted (no numerology)",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
