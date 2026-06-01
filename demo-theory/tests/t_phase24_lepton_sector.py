"""
PHASE 24 (particle masses) -- the lepton sector: honest assessment + the Koide
target.

Leptons (e, mu, tau, neutrinos) are NOT solitons -- they are elementary chiral
fermions = the v13 (complex doublet) + v14 (chirality) sector, with masses set by
Yukawa couplings x the Higgs VEV (inputs, as in the SM). The May-2026 attempt to
get lepton mass ratios from a Hopfion ladder FAILED (m_mu/m_e=207, m_tau/m_e=3477
not reproduced) -- correctly, since leptons are not topological solitons. So QNG
does NOT predict lepton masses, same status as the SM.

What QNG CAN say:
  - leptons are charged chiral fermions (v12 charge from winding + v14 chirality);
  - the v12 charge-topology link forbids a neutral ELEMENTARY stable particle ->
    neutrinos (neutral) need a distinct mechanism (Majorana / different sector).
  - the one empirical lepton-mass STRUCTURE is the KOIDE relation
       Q = (m_e+m_mu+m_tau)/(sqrt m_e + sqrt m_mu + sqrt m_tau)^2 = 2/3
    (holds to ~5 digits) -- the target any lepton-mass theory (QNG included)
    would need to explain. QNG does NOT derive it (no accepted derivation exists).

Test: confirm Koide = 2/3; state QNG's honest lepton-sector position.
ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase24-lepton-sector-v1")

# PDG charged-lepton masses (MeV)
m_e, m_mu, m_tau = 0.51099895, 105.6583755, 1776.86


def main():
    print("="*70)
    print("PHASE 24 (particle masses) -- lepton sector + the Koide target")
    print("="*70)

    Q = (m_e+m_mu+m_tau)/(np.sqrt(m_e)+np.sqrt(m_mu)+np.sqrt(m_tau))**2
    print("\n[Koide] Q = (sum m)/(sum sqrt m)^2 = %.6f   vs 2/3 = %.6f  (%.3f%% off)"
          % (Q, 2/3, 100*abs(Q-2/3)/(2/3)))
    koide_holds = abs(Q-2/3) < 1e-3

    print("\n  mass ratios: m_mu/m_e = %.1f, m_tau/m_mu = %.2f, m_tau/m_e = %.0f"
          % (m_mu/m_e, m_tau/m_mu, m_tau/m_e))
    print("  (May-2026 Hopfion-ladder attempt to get these FAILED -- correctly,")
    print("   leptons are NOT topological solitons.)")

    print("\n[QNG lepton-sector position -- honest]")
    print("  - leptons = elementary chiral fermions: v13 (complex doublet) + v14")
    print("    (chirality, domain-wall surmountable, Phase 9). NOT solitons.")
    print("  - masses = Yukawa x Higgs VEV -> INPUTS, same status as the SM.")
    print("    QNG does NOT predict lepton masses (no Yukawa structure derived).")
    print("  - v12 charge-topology forbids a neutral ELEMENTARY stable particle")
    print("    -> neutrinos (neutral) need a distinct mechanism (open).")
    print("  - KOIDE Q=2/3 is the empirical lepton-mass STRUCTURE any theory must")
    print("    explain; QNG does not derive it (no accepted derivation exists).")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Koide relation Q = 2/3 holds (target structure) : %s (%.5f)" % (koide_holds, Q))

    verdict = (
        "LEPTON_SECTOR_OPEN_KOIDE_TARGET: honest status of the lepton sector. "
        f"The Koide relation Q=(sum m)/(sum sqrt m)^2 = {Q:.5f} holds (vs 2/3, "
        f"{100*abs(Q-2/3)/(2/3):.2f}%) -- the one empirical lepton-mass structure. "
        "QNG does NOT predict lepton masses: leptons are elementary chiral fermions "
        "(v13 complex doublet + v14 chirality, NOT solitons), with masses = "
        "Yukawa x Higgs VEV (inputs, same status as the SM). The May-2026 "
        "Hopfion-ladder attempt to reproduce m_mu/m_e=207, m_tau/m_e=3477 FAILED -- "
        "correctly, since leptons are not topological solitons (the demo edge/node "
        "ontology confirms: leptons are elementary v13/v14 matter, not phi-solitons "
        "like baryons). What QNG CAN say: (1) leptons are charged chiral fermions "
        "(v12 charge from winding + v14 chirality); (2) the v12 charge-topology link "
        "forbids a neutral ELEMENTARY stable particle, so neutrinos need a distinct "
        "mechanism (Majorana/seesaw, open); (3) Koide Q=2/3 is the target structure "
        "any lepton-mass theory must explain, QNG included -- and QNG does not "
        "derive it (no accepted derivation exists anywhere). So the lepton sector "
        "is GENUINELY OPEN: masses are Yukawa inputs (Drumul-3-like, but flavor), "
        "Koide is the target, and neutrinos need new structure. This COMPLETES the "
        "honest particle survey: HADRONS predicted (~14 states, ~1%, Phase 23); "
        "LEPTONS open (Yukawa + Koide + neutrino mechanism); gauge bosons "
        "structural (photon derived, W/Z/gluons edges-host).")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"koide_Q": float(Q), "koide_2_3": 2/3,
                   "koide_holds": bool(koide_holds),
                   "ratios": {"mu_e": m_mu/m_e, "tau_mu": m_tau/m_mu, "tau_e": m_tau/m_e},
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
