"""
PHASE 73 (particles / Gap 13) -- the symmetry-breaking mechanism for delta: which
QNG term (if any) can fix the Koide-offset Goldstone mode?

Phase 72: delta is a GOLDSTONE zero mode of the 3-generation phase system; fixing it
needs EXPLICIT breaking of the global U(1). This phase asks WHICH breaking term can
do it, and whether QNG supplies it.

Sharp constraint: a potential term cos(m*phi) added to the 3 splay phases
theta_n = delta + 2pi n/3 contributes S(m,delta) = sum_n cos(m(delta+2pi n/3)).
   sum_n exp(i*m*2pi n/3) = 0  UNLESS m = 0 mod 3 (then = 3).
So S(m,delta) is INDEPENDENT of delta (=0) for m not divisible by 3, and
= 3 cos(m*delta) (delta-DEPENDENT) only for m = 3, 6, ... Hence ONLY a THREE-FOLD
(m=3) term can lift the delta degeneracy and fix it.

  T1 verify numerically: S(m,delta) is delta-independent for m=1,2,4,5 and
     delta-dependent only for m=3,6.
  T2 test the QNG candidate breaking terms: V_couple ~ (1-cos phi) is m=1; cubic
     lattice anisotropy ~ cos(4 phi) is m=4 -> NEITHER couples to delta.
  T3 the ONLY thing that fixes delta is an m=3 term -- naturally an instanton /
     't Hooft 3-generation vertex cos(3 phi + theta). Its phase theta is a
     theta-angle-like parameter, NOT predicted by QNG (strong-CP-class problem). So
     delta is undetermined for the SAME fundamental reason theta_QCD is.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase73-delta-breaking-v1")


def splay_sum(m, delta):
    n = np.arange(3)
    return np.sum(np.cos(m*(delta + 2*np.pi*n/3)))


def main():
    print("="*70)
    print("PHASE 73 (Gap 13) -- the symmetry-breaking mechanism for delta")
    print("="*70)

    # T1: which harmonics couple to delta?
    print("\n[T1] which breaking harmonic cos(m phi) can fix delta?")
    print("     (S(m,delta) = sum over the 3 splay phases; delta-DEPENDENT => can fix delta)")
    print("     m    S(m, delta=0.0)  S(m, delta=0.5)  depends on delta?")
    couples = {}
    for m in range(1, 7):
        s0 = splay_sum(m, 0.0); s1 = splay_sum(m, 0.5)
        dep = abs(s0 - s1) > 1e-6
        couples[m] = dep
        print("     %d    %+.4f          %+.4f          %s" % (m, s0, s1, "YES (m=0 mod 3)" if dep else "no (=0)"))
    print("     => ONLY m = 3, 6, ... (multiples of 3) couple to delta. A breaking term")
    print("        must be THREE-FOLD (cos 3phi) to lift the delta Goldstone degeneracy.")

    # T2: QNG candidate terms
    print("\n[T2] do QNG's existing breaking terms fix delta?")
    print("     V_couple ~ (1 - cos phi)            -> m=1 : couples to delta? %s" % couples[1])
    print("     cubic lattice anisotropy ~ cos(4 phi) -> m=4 : couples to delta? %s" % couples[4])
    print("     => NEITHER is three-fold, so NEITHER fixes delta. (The m=1 sine-Gordon")
    print("        and the m=4 cubic anisotropy both average to zero over the 3 phases.)")

    # T3: the m=3 source
    print("\n[T3] the only mechanism that CAN fix delta: a three-fold (m=3) term.")
    print("     natural source: an INSTANTON / 't Hooft 3-generation vertex cos(3 phi + theta)")
    print("     -- exactly the kind of term that breaks U(1) -> Z3 (like U(1)_A breaking in")
    print("     QCD). It fixes delta = -theta/3 (the splay aligns to the vertex phase).")
    print("     BUT theta is a THETA-ANGLE-like parameter -- NOT predicted from first")
    print("     principles (this is the strong-CP-class problem). So delta is")
    print("     undetermined for the SAME reason theta_QCD is undetermined.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  only m=3 (three-fold) terms can fix delta : confirmed (m=1,2,4,5 decouple)")
    print("  QNG's V_couple (m=1) and cubic anisotropy (m=4) do NOT fix delta")
    print("  the m=3 source = instanton/'t Hooft vertex -> delta tied to a theta-angle (unpredicted)")
    print("  => delta open, traced to the strong-CP-class problem. 2/9 still refused.")

    verdict = (
        "DELTA_REQUIRES_A_THREE-FOLD_BREAKING_TERM_AND_REDUCES_TO_AN_UNPREDICTED_"
        "THETA-ANGLE. Following the Phase-72 result (delta is a Goldstone zero mode), "
        "this phase pins down EXACTLY what could fix it. A breaking potential cos(m*phi) "
        "added to the three splay phases theta_n = delta + 2pi n/3 contributes a "
        "delta-dependent term ONLY if m is a multiple of 3 -- because sum_n "
        "exp(i*m*2pi n/3) vanishes unless m=0 mod 3. (T1) Verified numerically: the "
        "splay-sum S(m,delta) is delta-INDEPENDENT for m=1,2,4,5 and delta-DEPENDENT "
        "only for m=3,6. So lifting the delta Goldstone degeneracy REQUIRES a "
        "three-fold (cos 3phi) term. (T2) QNG's existing breaking terms FAIL this: the "
        "V_couple sine-Gordon potential ~ (1-cos phi) is m=1, and the cubic-lattice "
        "anisotropy ~ cos(4 phi) is m=4 -- BOTH average to zero over the three phases "
        "and leave delta free. (T3) The ONLY thing that can fix delta is a genuinely "
        "three-fold term, whose natural origin is an INSTANTON / 't Hooft "
        "3-generation vertex cos(3 phi + theta) -- precisely the structure that breaks "
        "U(1) down to Z3 (the analogue of U(1)_A breaking in QCD). Such a vertex would "
        "lock delta = -theta/3 to the vertex phase theta -- but theta is a "
        "THETA-ANGLE-like parameter, which is NOT predicted from first principles "
        "(this is the strong-CP-class problem, where theta_QCD is mysteriously ~0 with "
        "no accepted derivation). CONCLUSION: delta is undetermined for the SAME "
        "fundamental reason the QCD theta-angle is -- it is the phase of a "
        "three-fold (instanton-like) vertex, a quantity no current theory predicts. "
        "This is a genuine, sharp structural result: it shows delta is NOT a missing "
        "geometric number but the value of a topological vacuum angle, tying the "
        "lepton-mass offset to one of physics' deepest open parameters. So delta "
        "remains OPEN, now precisely located (a theta-angle of a 3-generation "
        "instanton vertex), and the seductive 2/9 is again REFUSED -- a vacuum angle "
        "has no reason to equal a rational radian. HONEST: this identifies the FORM "
        "of the breaking (m=3, instanton-induced) and WHY QNG's existing terms can't "
        "do it (wrong harmonic); it does NOT construct the QNG instanton vertex "
        "explicitly nor compute its theta (which would be the strong-CP problem in "
        "QNG). The lepton-sector status: 3 generations = 3D (P60), Q=2/3 -> m_tau "
        "0.006% (P61), M0 ~ transmutation scale (P62), delta = a Goldstone fixed only "
        "by an instanton theta-angle (P72/73) -- absolute lepton masses await that "
        "theta, a strong-CP-class problem, NOT a guessable number.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"couples_by_m": {str(m): bool(couples[m]) for m in couples},
                   "V_couple_m": 1, "cubic_anisotropy_m": 4,
                   "fixing_term": "m=3 instanton/'t Hooft vertex cos(3phi+theta)",
                   "delta_reduces_to": "theta-angle (strong-CP-class, unpredicted)",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
