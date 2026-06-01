"""
PHASE 50 (cosmology) -- the abundance calculation: Omega_DM from the un-packing
matter era, and the honest sensitivity / overproduction check.

Phase 49 left the abundance controlled by ONE knob: the matter-era duration N_m
(e-folds before PBHs form and reheating ends it). We now run the reduced
perturbation + Press-Schechter PBH calculation to get Omega_DM(N_m) and test
whether the observed 0.26 is predicted or tuned.

Chain:
  - seed at the relevant scale: sigma_seed ~ 5e-7 (Phase 47 shot noise).
  - matter-era growth: delta_final = sigma_seed * exp(N_m)   (delta ~ a, Phase 49).
  - PBH formation fraction: beta(delta) ~ exp(-delta_c^2 / (2 delta^2)), delta_c=0.45.
  - relic abundance scales with beta; anchor beta=5e-3 <-> Omega_DM=0.26 (Phase 47:
    that beta at M_i~1e8 g gives the relics as all of DM). So
        Omega_DM(delta) = 0.26 * beta(delta)/beta_anchor.

  T1 Omega_DM vs delta_final (the spectrum amplitude at the PBH scale).
  T2 Omega_DM vs matter-era duration N_m = ln(delta_final/sigma_seed).
  T3 sensitivity: how precisely must N_m be tuned to land on 0.26 (and how fast it
     overproduces) -- the honest verdict on predictivity.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase50-relic-omega-v1")

SIGMA_SEED = 4.66e-7      # Phase 47
DELTA_C = 0.45
BETA_ANCHOR = 5.0e-3      # Phase 47: beta(M_i~1e8g) that gives relics = all DM
OMEGA_ANCHOR = 0.26
DELTA_ANCHOR = 0.138      # the delta giving beta_anchor


def beta(delta):
    return np.exp(-DELTA_C**2/(2.0*delta**2))


def omega_dm(delta):
    return OMEGA_ANCHOR*beta(delta)/BETA_ANCHOR


def main():
    print("="*70)
    print("PHASE 50 (cosmology) -- Omega_DM from the un-packing, and its sensitivity")
    print("="*70)
    print("\n  seed sigma~%.0e (Phase 47); delta_final = seed*exp(N_m); beta=exp(-dc^2/2d^2)" % SIGMA_SEED)
    print("  anchor: beta=%.0e <-> Omega_DM=%.2f (delta=%.3f)" % (BETA_ANCHOR, OMEGA_ANCHOR, DELTA_ANCHOR))

    # T1: Omega vs delta_final
    print("\n[T1] Omega_DM vs spectrum amplitude delta_final at the PBH scale:")
    print("     delta_final   beta          Omega_DM        note")
    for d in [0.10, 0.12, 0.138, 0.15, 0.18, 0.25]:
        om = omega_dm(d)
        note = "UNDERPRODUCE" if om < 0.05 else ("~observed" if 0.1 < om < 0.6 else "OVERCLOSE")
        print("     %.3f         %.2e   %.2e     %s" % (d, beta(d), om, note))

    # T2: Omega vs matter-era duration N_m
    print("\n[T2] Omega_DM vs matter-era duration N_m = ln(delta_final/seed):")
    print("     N_m (e-folds)   delta_final   Omega_DM")
    for Nm in [12.0, 12.4, 12.59, 12.8, 13.2, 14.0]:
        d = SIGMA_SEED*np.exp(Nm)
        print("     %.2f           %.4f        %.2e" % (Nm, d, omega_dm(d)))
    Nm_target = np.log(DELTA_ANCHOR/SIGMA_SEED)
    print("     => Omega_DM=0.26 requires N_m = ln(%.3f/%.0e) = %.2f e-folds" % (DELTA_ANCHOR, SIGMA_SEED, Nm_target))

    # T3: sensitivity
    print("\n[T3] sensitivity (how tuned must N_m be?):")
    d0 = DELTA_ANCHOR
    # dOmega/Omega = (delta_c^2/delta^2) * (d delta/delta) ; and d delta/delta = dN_m
    sens = DELTA_C**2/d0**2
    print("     dln(Omega)/dN_m = delta_c^2/delta^2 = %.1f" % sens)
    print("     => a change of just dN_m = %.3f e-folds changes Omega_DM by a factor e" % (1.0/sens))
    print("        Omega is DOUBLY-exponentially sensitive to the reheating timing.")
    # overproduce check: how much extra N_m to overclose (Omega>1)?
    d_over = DELTA_ANCHOR
    Nm_over = np.log((DELTA_C/np.sqrt(2*np.log(BETA_ANCHOR/ (OMEGA_ANCHOR/1.0) ) *-1 +1e-9)) )  # rough
    print("     a mere ~%.2f e-folds MORE of matter domination -> Omega>1 (overclose)."
          % (np.log(1.0/OMEGA_ANCHOR)/sens))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Omega_DM=0.26 achievable at N_m=%.2f e-folds (delta~0.14) : yes" % Nm_target)
    print("  but dln(Omega)/dN_m = %.0f -> exponentially sensitive (standard PBH tuning)" % sens)
    print("  => Omega_DM is ACHIEVABLE but TUNED, not a parameter-free QNG prediction")

    verdict = (
        "OMEGA_DM_IS_ACHIEVABLE_BUT_FINE-TUNED (the standard PBH abundance "
        "sensitivity). Running the reduced perturbation + Press-Schechter "
        "calculation: the un-packing matter era grows the seed (sigma~5e-7) as "
        "delta~a, and the PBH/relic abundance follows beta(delta)=exp(-delta_c^2/"
        f"2delta^2). (T1) Omega_DM passes through the observed ~0.26 when the "
        f"spectrum reaches delta_final ~ {DELTA_ANCHOR:.3f} at the PBH scale; below "
        "that it underproduces, above it overcloses. (T2) That corresponds to a "
        f"matter-era duration N_m = {Nm_target:.2f} e-folds -- comfortably within "
        "the ~37 available (Phase 49), so there is NO shortage: QNG robustly makes "
        "AT LEAST enough dark matter, and generically TENDS TO OVERPRODUCE (the "
        "matter era is efficient). (T3) BUT the abundance is exponentially "
        f"sensitive: dln(Omega)/dN_m = delta_c^2/delta^2 = {sens:.0f}, so a change "
        f"of only ~{1.0/sens:.3f} e-folds in the reheating timing changes Omega by a "
        "factor e, and ~%.2f e-folds more would overclose the universe. This is the "
        "WELL-KNOWN fine-tuning of all PBH dark-matter scenarios (the abundance is "
        "doubly-exponentially sensitive to the spectrum amplitude). HONEST VERDICT: "
        "the QNG un-packing produces dark matter ABUNDANTLY and the observed Omega_DM "
        "= 0.26 is ACHIEVABLE, but it is NOT a parameter-free prediction -- it "
        "requires the reheating epoch (matter-era duration) tuned to ~0.1 e-fold, a "
        "tuning QNG does not currently fix from deeper dynamics. This is the same "
        "predictive boundary every PBH-DM model hits. NET over the whole program "
        "(Phases 38-50): QNG gives a COMPLETE, self-consistent, CMB-consistent dark-"
        "matter story -- WHAT it is (neutral cold ~3ug Planck relic / degenerate "
        "core), HOW it forms (un-packing -> matter era -> PBHs -> evaporation -> "
        "relics), and WHY it returns black-hole information -- with a single "
        "remaining un-predicted number (Omega_DM), exponentially sensitive to the "
        "reheating timing, exactly as in standard PBH cosmology. The honest claim is "
        "a fully-articulated candidate, not a derivation of the cosmic abundance."
        % (np.log(1.0/OMEGA_ANCHOR)/sens))
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"Nm_target": float(Nm_target), "delta_anchor": DELTA_ANCHOR,
                   "dlnOmega_dNm": float(sens), "dNm_for_factor_e": float(1.0/sens),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
