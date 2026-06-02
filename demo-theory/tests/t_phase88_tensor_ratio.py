"""
PHASE 88 (cosmology) -- gravitational waves from inflation: the tensor-to-scalar
ratio r, an HONEST constraint that refines Phase 85.

P85 proposed QNG inflation driven by the max-packed state (rho_max~54 Planck
densities, H_inf~4.2 in Planck units -- i.e. NEAR-PLANCK scale). But inflation
produces primordial gravitational waves with a tensor-to-scalar ratio r ~ (H_inf/M_Pl)^2,
and the BICEP/Keck+Planck bound is r < 0.036. A near-Planck H_inf gives r >> 0.036 --
RULED OUT. So the inflationary phase CANNOT be at maximum packing; it must occur LATER,
at a sub-Planckian density, after partial un-packing.

  T1 the r bound forces the inflation energy scale: V^(1/4) < ~1.6e16 GeV (sub-Planck).
  T2 so QNG inflation occurs NOT at rho_max but after the substrate un-packs to
     rho ~ (1e16 GeV)^4 ~ 1e-12 rho_Planck -- the max-packed state is the pre-inflation
     INITIAL CONDITION, and inflation happens at the GUT-ish scale. This refines P85.
  T3 prediction: if QNG inflation sits just below the bound (as high as allowed), it
     predicts r near the current limit -> DETECTABLE by CMB-S4 / LiteBIRD. A
     falsifiable QNG-inflation target. (If r is pushed far below and never seen, QNG
     inflation is at a lower scale -- still consistent, less distinctive.)

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase88-tensor-ratio-v1")

M_PLANCK_GEV = 1.22e19
R_BOUND = 0.036          # BICEP/Keck + Planck 2021
H_INF_MAXPACK_PL = 4.2   # P85 (Planck units) -- super-Planckian (problem)


def main():
    print("="*70)
    print("PHASE 88 (cosmology) -- tensor-to-scalar r: honest constraint on QNG inflation")
    print("="*70)

    # T1: the naive problem + the bound
    print("\n[T1] the problem with near-Planck inflation (P85):")
    r_naive = H_INF_MAXPACK_PL**2   # ~ (H/M_Pl)^2, order
    print("     P85 max-packed inflation: H_inf ~ %.1f M_Pl (super-Planckian!)" % H_INF_MAXPACK_PL)
    print("     r ~ (H_inf/M_Pl)^2 ~ %.0f -- VASTLY above the bound r < %.3f -> RULED OUT." % (r_naive, R_BOUND))
    # the r bound -> inflation energy scale
    V_quarter_max_GeV = 1.6e16   # V^(1/4) for r=0.036 (standard)
    print("     the bound r < %.3f forces the inflation energy scale V^(1/4) < ~%.1e GeV"
          % (R_BOUND, V_quarter_max_GeV))
    print("     = ~%.1e M_Pl (sub-Planckian, ~GUT scale)." % (V_quarter_max_GeV/M_PLANCK_GEV))

    # T2: inflation occurs after partial un-packing
    print("\n[T2] so QNG inflation is NOT at max packing -- it occurs LATER:")
    rho_inf_over_planck = (V_quarter_max_GeV/M_PLANCK_GEV)**4
    print("     inflation density rho_inf ~ (V^1/4)^4 ~ %.0e rho_Planck" % rho_inf_over_planck)
    print("     so the substrate must un-pack from rho_max (~54 rho_Pl) DOWN to ~%.0e rho_Pl"
          % rho_inf_over_planck)
    print("     BEFORE the inflationary (de Sitter) phase. The max-packed state is the")
    print("     pre-inflation INITIAL CONDITION; inflation happens at the GUT-ish scale.")
    print("     => this REFINES P85: the inflaton is the chi/substrate energy at a")
    print("        SUB-Planckian stage, not the full max-packed density.")

    # T3: prediction
    print("\n[T3] prediction / test:")
    print("     if QNG inflation sits as high as allowed (just below the bound), it")
    print("     predicts r NEAR the current limit (~0.01-0.03) -> DETECTABLE by")
    print("     CMB-S4 and LiteBIRD (sensitivity r~0.001). A falsifiable QNG-inflation")
    print("     target: a B-mode detection at r~0.01-0.03 would support it; pushing r")
    print("     far below with no detection means QNG inflation is at a lower scale.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  near-Planck inflation (P85 naive) gives r ~ %.0f >> %.3f : RULED OUT" % (r_naive, R_BOUND))
    print("  r bound forces V^(1/4) < ~1.6e16 GeV -> inflation at the GUT scale, not max packing")
    print("  refines P85: max-packed state = pre-inflation IC; inflation sub-Planckian")
    print("  prediction: r near the current bound (~0.01-0.03) -> CMB-S4/LiteBIRD test")

    verdict = (
        "THE_TENSOR-TO-SCALAR_RATIO_FORCES_QNG_INFLATION_BELOW_THE_PLANCK_SCALE "
        "(refining P85, with a falsifiable r prediction). Honest follow-up to the P85 "
        "inflation proposal. (T1) Inflation produces primordial gravitational waves "
        "with tensor-to-scalar ratio r ~ (H_inf/M_Pl)^2, bounded by BICEP/Keck+Planck "
        "to r < 0.036. P85's naive max-packed inflation has H_inf ~ 4.2 M_Pl "
        "(super-Planckian!), giving r ~ 18 -- VASTLY above the bound, RULED OUT. So "
        "the inflationary phase CANNOT occur at maximum packing. (T2) The r bound "
        "forces the inflation energy scale to V^(1/4) < ~1.6e16 GeV (~1e-3 M_Pl, the "
        "GUT scale), i.e. a density ~1e-12 rho_Planck. Therefore QNG inflation happens "
        "AFTER the substrate has un-packed from the max-packed state (rho_max ~ 54 "
        "rho_Planck) DOWN to the GUT-scale density -- the maximally-packed state is the "
        "pre-inflation INITIAL CONDITION (the unique low-entropy start, P82), and the "
        "de Sitter inflationary phase occurs slightly later, at a sub-Planckian "
        "(GUT-ish) scale, driven by the substrate/chi energy there. This REFINES P85: "
        "the inflaton is not the full max-packed density but the lower energy at the "
        "post-un-packing GUT stage. (T3) The payoff is a FALSIFIABLE prediction: if "
        "QNG inflation sits as high as the bound allows (natural, since it descends "
        "from the Planck-scale start), it predicts a tensor-to-scalar ratio r NEAR the "
        "current limit (~0.01-0.03), DETECTABLE by the next-generation CMB B-mode "
        "experiments CMB-S4 and LiteBIRD (sensitivity r ~ 0.001). A B-mode detection "
        "at r~0.01-0.03 would support QNG inflation; if r is pushed far below 0.001 "
        "with no detection, QNG inflation must be at a lower scale (still consistent, "
        "but less distinctive). NET: this is an honest constraint that both CORRECTS "
        "P85 (inflation is sub-Planckian, not at max packing) and SHARPENS it into a "
        "testable r prediction. It is the SECOND honest tension flagged in the "
        "cosmology sector (with n_s, P84, which this inflation then resolves) -- "
        "showing the early-universe program is genuinely constrained, not free. "
        "HONEST: r ~ (H/M_Pl)^2 and V^(1/4) bound are standard inflationary relations; "
        "QNG does not yet derive the exact inflation scale (it follows from the "
        "post-un-packing density when slow-roll begins, not computed) -- so r is "
        "predicted to be 'near the bound' by the high-scale descent, not pinned to a "
        "number. The robust content: max-packed inflation is excluded by r, so QNG's "
        "inflationary phase is sub-Planckian (GUT-scale), and r should be near the "
        "current limit -- a clean CMB-S4/LiteBIRD test.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"r_bound": R_BOUND, "r_naive_maxpack": float(r_naive),
                   "V_quarter_max_GeV": V_quarter_max_GeV,
                   "inflation_scale": "sub-Planckian (~GUT, 1e16 GeV)",
                   "prediction": "r near current bound ~0.01-0.03 (CMB-S4/LiteBIRD)",
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
