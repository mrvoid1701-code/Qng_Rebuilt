"""
PHASE 61 (particles / Gap 13) -- the lepton masses: what QNG's 3-phase structure
ACTUALLY predicts (tau from e, mu) vs the delta=2/9 temptation (refused).

Phase 60: QNG's 3 domain-wall orientations -> 3 generations -> the Koide 3-phase
structure (3 phases 2pi/3 apart, amplitude sqrt2 on the phi-circle) -> Q=2/3.

The Koide form sqrt(m_n) = M0[1 + sqrt2 cos(2pi n/3 + delta)] has TWO free
parameters (M0 = scale, delta = offset) for THREE masses, so it predicts exactly
ONE relation: the Koide value Q = (Sum m)/(Sum sqrt m)^2 = 2/3, holding for ANY
M0, delta. QNG supplies that relation (the structure). Therefore QNG predicts ONE
lepton mass from the other two.

  T1 the real, parameter-free test: given m_e and m_mu, the Q=2/3 relation predicts
     m_tau. Compute and compare to the measured tau mass.
  T2 the delta=2/9 question: fit delta from the masses; it lands near 2/9 -- but is
     that a QNG geometric prediction or a numerical coincidence? We REFUSE to claim
     a derivation we do not have (same discipline that rejected beta_g/48=1/137).
  T3 honest accounting: QNG predicts 1 of 3 lepton masses (the Koide relation, from
     the 3-phase structure); the remaining 2 (the scale M0 ~ electron mass, and the
     offset delta) are NOT derived -> absolute lepton masses still open.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase61-koide-tau-v1")

M_E = 0.5109989   # MeV
M_MU = 105.6584
M_TAU_OBS = 1776.86


def predict_tau(m_e, m_mu):
    """Koide Q=2/3 -> solve for sqrt(m_tau). c = 2(a+b) +- sqrt(3(a^2+4ab+b^2))."""
    a = np.sqrt(m_e); b = np.sqrt(m_mu)
    disc = 3*(a*a + 4*a*b + b*b)
    c_plus = 2*(a+b) + np.sqrt(disc)
    c_minus = 2*(a+b) - np.sqrt(disc)
    return c_plus**2, c_minus**2


def main():
    print("="*70)
    print("PHASE 61 (Gap 13) -- lepton masses: the real Koide prediction vs delta=2/9")
    print("="*70)

    # T1: predict tau from e, mu
    tau_plus, tau_minus = predict_tau(M_E, M_MU)
    err = abs(tau_plus - M_TAU_OBS)/M_TAU_OBS
    print("\n[T1] PARAMETER-FREE test: Q=2/3 predicts m_tau from m_e, m_mu:")
    print("     inputs: m_e = %.4f MeV, m_mu = %.4f MeV" % (M_E, M_MU))
    print("     predicted m_tau = %.2f MeV  (other root %.2f MeV, unphysical)" % (tau_plus, tau_minus))
    print("     observed  m_tau = %.2f MeV" % M_TAU_OBS)
    print("     agreement: %.4f%%  -- a genuine QNG prediction (the 3-phase structure)" % (100*err))
    predicts = err < 0.001

    # T2: the delta question
    print("\n[T2] the delta = 2/9 temptation (scrutinized):")
    # fit delta: sqrt(m_n)/M0 - 1 = sqrt2 cos(2pi n/3 + delta), M0 = mean(sqrt m)
    sm = np.array([np.sqrt(M_E), np.sqrt(M_MU), np.sqrt(M_TAU_OBS)])
    M0 = sm.mean()
    cosvals = (sm/M0 - 1)/np.sqrt(2)
    # the largest (tau) angle is closest to 0; delta = that angle
    delta_fit = np.arccos(np.clip(cosvals[2], -1, 1))
    print("     fitted delta = %.4f rad ;  2/9 = %.4f rad  (diff %.1f%%)"
          % (delta_fit, 2.0/9.0, 100*abs(delta_fit-2.0/9)/(2.0/9)))
    print("     => delta is VERY close to 2/9 -- BUT this is NOT a QNG derivation:")
    print("        delta is one of the 2 free Koide params (with M0); the form predicts")
    print("        only Q=2/3, not delta. We have NO geometric derivation of delta=2/9")
    print("        from the wall orientations, so we REFUSE to claim one (same")
    print("        discipline that rejected beta_g/48=1/137 in Phase 33). delta=2/9 is")
    print("        a striking coincidence, flagged, NOT explained.")

    # T3: honest accounting
    print("\n[T3] honest accounting of the lepton spectrum:")
    print("     PREDICTED by QNG (3-phase structure -> Q=2/3): 1 mass (tau from e,mu, 0.01%%).")
    print("     NOT derived: M0 (the scale ~ electron mass) and delta (the offset) = 2 inputs.")
    print("     => the Koide RELATION is a QNG prediction; the ABSOLUTE masses are not")
    print("        (2 of 3 remain inputs). delta=2/9 unexplained; M0 needs the Yukawa scale.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Q=2/3 predicts m_tau from e,mu: %.2f vs %.2f MeV (%.3f%%) : %s"
          % (tau_plus, M_TAU_OBS, 100*err, predicts))
    print("  delta=2/9: striking coincidence, REFUSED as a derivation (no geometric proof)")
    print("  absolute masses: M0 + delta (2 of 3) still inputs -> NOT derived")

    verdict = (
        "QNG_PREDICTS_ONE_LEPTON_MASS_FROM_THE_OTHER_TWO; DELTA=2/9_REFUSED_AS_"
        "NUMEROLOGY. The honest content of the lepton sector. The Koide form "
        "sqrt(m_n) = M0[1 + sqrt2 cos(2pi n/3 + delta)] has TWO free parameters (M0, "
        "delta) for three masses, so it predicts exactly ONE relation -- the Koide "
        "value Q = 2/3 -- which QNG's three-domain-wall / three-phase structure "
        "(Phase 60) supplies. (T1) The real, parameter-free consequence: given m_e "
        "and m_mu, Q=2/3 PREDICTS m_tau = %.2f MeV, versus the measured 1776.86 MeV "
        "-- agreement to %.3f%%. This is a genuine QNG prediction (one lepton mass "
        "from the other two, via the 3-phase structure), at the 0.01%% level. (T2) "
        "The fitted Koide offset delta = %.4f rad lands strikingly close to 2/9 = "
        "0.2222 rad -- a famous near-coincidence -- BUT delta is merely one of the "
        "two free parameters (it is whatever the masses make it once Q=2/3 holds), "
        "and we have NO geometric derivation of delta = 2/9 from the wall "
        "orientations. So we REFUSE to claim a derivation we do not possess, exactly "
        "as we rejected the seductive beta_g/48 = 1/137 in Phase 33. delta = 2/9 is "
        "flagged as a striking, UNEXPLAINED coincidence -- not a QNG result. (T3) "
        "HONEST ACCOUNTING: QNG predicts 1 of the 3 charged-lepton masses (the Koide "
        "relation, from the 3-phase structure of Phase 60); the remaining 2 -- the "
        "overall scale M0 (set by the electron-mass / Yukawa scale) and the offset "
        "delta -- are NOT derived. So the Koide RELATION is a QNG prediction, but the "
        "ABSOLUTE lepton masses are still open (two inputs remain). NET for Gap 13: "
        "the generation COUNT is given a falsifiable QNG origin (3 = 3D, Phase 60), "
        "and the mass RELATION among the three is predicted (Q=2/3 -> tau to 0.01%%, "
        "this phase); what stays open is the absolute scale M0 and the offset delta "
        "(the Yukawa hierarchy) -- and the tantalizing delta=2/9 is honestly left as "
        "an unexplained coincidence rather than dressed up as a derivation. The "
        "no-numerology discipline holds: we claim the real prediction (tau) and "
        "refuse the tempting one (2/9)." % (tau_plus, 100*err, delta_fit))
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"m_e": M_E, "m_mu": M_MU, "m_tau_predicted": float(tau_plus),
                   "m_tau_observed": M_TAU_OBS, "tau_error_pct": float(100*err),
                   "delta_fit": float(delta_fit), "two_ninths": 2.0/9.0,
                   "predicts_tau": bool(predicts), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
