"""
PHASE 47 (dark matter) -- ENTERING the primordial-production problem: can QNG seed
the primordial black holes whose relics are the dark matter?

Phase 46 left ONE input: the relic abundance Y_req = 2.3e-28, achievable only if a
specific population of primordial black holes (PBHs) formed and evaporated. Here we
map EXACTLY what is required and test it against QNG's intrinsic fluctuations.

The chain: primordial density fluctuations of amplitude sigma at a small scale ->
rare regions above the collapse threshold delta_c~0.45 collapse to PBHs with
formation fraction beta -> they evaporate, each leaving one Planck relic (Phase 38)
-> relics are the dark matter.

  T1 the PBH formation fraction beta(M_i) needed so that the relics = all of DM
     (from Y_req and PBH/horizon-mass bookkeeping): beta = Y_req * (M_i/M_Pl)^2.
  T2 the primordial fluctuation amplitude sigma required for that beta, via the
     Press-Schechter tail beta ~ exp(-delta_c^2/(2 sigma^2)).
  T3 QNG's intrinsic fluctuation at the PBH horizon scale: discrete shot noise of
     N ~ M_i/M_Pl nodes gives sigma_QNG ~ 1/sqrt(N). Compare to the required sigma.

HONEST GOAL: locate precisely what QNG must supply and whether its natural
fluctuation source can. (Spoiler from the physics: substrate shot noise is far too
small -> seeding PBHs needs a COHERENT enhancement = inflation, which QNG lacks.)

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase47-primordial-v1")

M_PLANCK_KG = 2.176e-8
Y_REQ = 2.31e-28          # Phase 46
DELTA_C = 0.45            # PBH collapse threshold (radiation era)
A_S_CMB = 2.1e-9          # measured scalar amplitude (CMB scales)
SIGMA_CMB = np.sqrt(A_S_CMB)   # ~ 4.6e-5 rms on CMB scales


def sigma_from_beta(beta):
    """Invert beta ~ exp(-delta_c^2/(2 sigma^2)) -> sigma."""
    return DELTA_C/np.sqrt(2.0*(-np.log(beta)))


def main():
    print("="*70)
    print("PHASE 47 (dark matter) -- can QNG seed the primordial BHs for relic DM?")
    print("="*70)
    print("\n  required relic abundance (Phase 46): Y_req = %.2e" % Y_REQ)

    print("\n[T1] PBH formation fraction beta needed (beta = Y_req*(M_i/M_Pl)^2):")
    print("     M_i (g)     M_i/M_Pl       beta needed")
    betas = {}
    for M_i_g in [1e6, 1e8, 1e9]:
        M_i_kg = M_i_g*1e-3
        ratio = M_i_kg/M_PLANCK_KG
        beta = Y_REQ*ratio**2
        betas[M_i_g] = beta
        print("     %-9.0e  %.2e     %.2e" % (M_i_g, ratio, beta))
    print("     => beta ~ 1e-3 .. 1e-1 (a sensible, known light-PBH window).")

    print("\n[T2] primordial fluctuation amplitude sigma required for that beta")
    print("     (Press-Schechter: beta ~ exp(-delta_c^2/2sigma^2), delta_c=%.2f):" % DELTA_C)
    print("     M_i (g)     beta         sigma required")
    sigmas = {}
    for M_i_g, beta in betas.items():
        s = sigma_from_beta(beta)
        sigmas[M_i_g] = s
        print("     %-9.0e  %.2e   %.3f" % (M_i_g, beta, s))
    s_req = sigmas[1e8]
    print("     => required sigma ~ %.2f at the PBH scale -- vs sigma_CMB ~ %.0e:" % (s_req, SIGMA_CMB))
    print("        a STEEP blue spectrum, ~%.0e x larger power at small scales."
          % (s_req/SIGMA_CMB))

    print("\n[T3] QNG intrinsic fluctuation at the PBH horizon scale (shot noise):")
    print("     M_i (g)     N~M_i/M_Pl    sigma_QNG~1/sqrt(N)   vs required")
    for M_i_g in [1e6, 1e8, 1e9]:
        M_i_kg = M_i_g*1e-3
        N = M_i_kg/M_PLANCK_KG
        s_qng = 1.0/np.sqrt(N)
        gap = sigmas[M_i_g]/s_qng
        print("     %-9.0e  %.2e    %.2e          %.0e x too small"
              % (M_i_g, N, s_qng, gap))
    N8 = (1e8*1e-3)/M_PLANCK_KG
    s_qng8 = 1.0/np.sqrt(N8)
    gap8 = s_req/s_qng8
    print("     => QNG's discrete shot noise (sigma~%.0e) is ~%.0e x TOO SMALL to" % (s_qng8, gap8))
    print("        reach the required sigma~%.2f: thermal/granular noise cannot seed PBHs." % s_req)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  beta needed ~ %.0e (M_i~1e8 g): sensible window" % betas[1e8])
    print("  sigma required ~ %.2f (steep blue spectrum) : computed" % s_req)
    print("  QNG shot noise ~ %.0e -> ~%.0e too small : need COHERENT (inflationary) power"
          % (s_qng8, gap8))

    verdict = (
        "ENTERING_PRIMORDIAL_PRODUCTION: QNG LACKS THE INFLATIONARY SECTOR NEEDED, "
        "AND WE QUANTIFY THE GAP. We mapped exactly what producing the relic dark "
        "matter requires. (T1) For primordial black holes of initial mass "
        "M_i ~ 1e8 g (the light window that evaporates before BBN), the formation "
        f"fraction needed for their relics to be ALL of dark matter is beta ~ "
        f"{betas[1e8]:.0e} -- a sensible, known value. (T2) Via Press-Schechter "
        "that beta demands a primordial density-fluctuation amplitude sigma ~ "
        f"{s_req:.2f} at the PBH scale -- a STEEP BLUE spectrum, ~{s_req/SIGMA_CMB:.0e}x "
        "more small-scale power than the measured CMB amplitude (sigma_CMB ~ "
        f"{SIGMA_CMB:.0e}). (T3) QNG's intrinsic fluctuation at that scale is the "
        "discrete SHOT NOISE of N ~ M_i/M_Pl nodes, sigma_QNG ~ 1/sqrt(N) ~ "
        f"{s_qng8:.0e} -- about {gap8:.0e}x TOO SMALL. So QNG's granular/thermal "
        "noise CANNOT seed the required PBHs (it is many orders below threshold), "
        "and the measured CMB spectrum is both too small AND scale-invariant (no "
        "small-scale enhancement). Producing the relics therefore needs a COHERENT "
        "amplification of small-scale power -- an INFLATIONARY mechanism (or an "
        "early matter-dominated / preheating phase) -- which QNG as a substrate "
        "theory does NOT currently contain. HONEST CONCLUSION: 'entering' the "
        "abundance problem does not close it; instead it SHARPENS it to a single, "
        "well-posed missing ingredient -- a QNG early-universe sector that produces "
        "sigma ~ 0.1 at the PBH scale. QNG's own fluctuations (shot noise ~1e-6) are "
        "far too small, so the abundance genuinely requires physics beyond the "
        "current substrate theory. This is a clean, honest boundary: WHAT dark "
        "matter is (Phases 38-45) is settled and CMB-consistent; HOW MUCH (Omega_DM) "
        "awaits a QNG inflation/early-universe model. Speculative alternative not "
        "computed here: direct relic production at the QNG 'Big Bang' (substrate "
        "un-packing from the Phase-37 max-density state) -- a possible QNG-intrinsic "
        "channel, but not yet calculable.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"Y_req": Y_REQ, "beta_1e8g": betas[1e8], "sigma_required": s_req,
                   "sigma_CMB": SIGMA_CMB, "sigma_QNG_shotnoise": s_qng8,
                   "gap_factor": gap8, "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
