"""
PHASE 84 (cosmology) -- the primordial spectral index n_s: an HONEST challenge for QNG.

Planck measures the primordial power spectrum to be nearly scale-invariant and
slightly RED: n_s = 0.9649 +- 0.0042 (n_s=1 is exact scale-invariance; <1 means more
power on large scales). This is the second-most-precise cosmological observable (after
the acoustic peaks) and a sharp test of any early-universe model.

Does QNG's un-packing (P48-49) reproduce it? Be honest -- this may be a TENSION.

  T1 QNG's seed is the substrate SHOT NOISE: sigma(M) ~ 1/sqrt(N) ~ (M_Pl/M)^(1/2),
     so the power P(k) ~ sigma^2 ~ M^-1 ~ k^3 -- a STEEPLY BLUE spectrum (n_s >> 1),
     the OPPOSITE of the slightly-red CMB.
  T2 matter-dominated growth (delta~a, P48) is scale-dependent via horizon entry and
     modifies the tilt, but matter domination is NOT de Sitter and does NOT
     generically produce scale-invariance.
  T3 honest verdict: turning a steeply-blue shot-noise spectrum into the observed
     slightly-red n_s=0.965 is NOT natural in the matter-dominated un-packing picture.
     Reproducing n_s most likely needs an early NEAR-DE-SITTER (inflationary) phase,
     which the matter-dominated un-packing (P48-49) does NOT provide. This is a
     GENUINE OPEN CHALLENGE / potential tension for QNG cosmology -- flagged, not hidden.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase84-spectral-index-v1")

NS_OBS = 0.9649
NS_ERR = 0.0042


def main():
    print("="*70)
    print("PHASE 84 (cosmology) -- spectral index n_s: an HONEST challenge for QNG")
    print("="*70)
    print("\n  observed: n_s = %.4f +- %.4f (slightly RED, near scale-invariant)" % (NS_OBS, NS_ERR))

    # T1: shot-noise spectral tilt
    print("\n[T1] QNG seed = substrate SHOT NOISE:")
    print("     sigma(M) ~ 1/sqrt(N) ~ (M_Pl/M)^(1/2) (P47); horizon mass M ~ k^-3.")
    print("     power P(k) ~ sigma^2 ~ M^-1 ~ k^3 -> dimensionless Delta^2 ~ k^(n_s-1)")
    print("     with n_s - 1 ~ +3..+4 -> n_s ~ 4 (STEEPLY BLUE) -- OPPOSITE to red 0.965.")
    n_s_shot = 4.0  # order: steeply blue
    print("     => raw shot-noise n_s ~ %.0f, far from observed %.3f." % (n_s_shot, NS_OBS))

    # T2: matter-domination modification
    print("\n[T2] matter-dominated growth (delta~a, P48) modifies the tilt:")
    print("     growth is scale-dependent (modes enter the horizon at different times),")
    print("     which shifts the effective n_s -- but matter domination is NOT de Sitter")
    print("     and does NOT generically give scale-invariance (that is inflation's job).")

    # T3: honest verdict
    print("\n[T3] HONEST verdict:")
    tension = abs(n_s_shot - NS_OBS) > 5*NS_ERR
    print("     turning steeply-BLUE shot noise into slightly-RED n_s=0.965 is NOT")
    print("     natural in the matter-dominated un-packing picture -> a real TENSION.")
    print("     reproducing n_s most plausibly needs an early NEAR-DE-SITTER (inflationary)")
    print("     phase, which the matter-dominated un-packing (P48-49) does NOT provide.")
    print("     => GENUINE OPEN CHALLENGE for QNG cosmology. Flagged, not hidden.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  observed n_s = %.4f (slightly red); QNG shot noise n_s ~ %.0f (steeply blue)"
          % (NS_OBS, n_s_shot))
    print("  matter-dominated un-packing does NOT naturally give scale-invariance")
    print("  => TENSION / open challenge: QNG likely needs an early de-Sitter phase")

    verdict = (
        "THE_SPECTRAL_INDEX_n_s_IS_AN_HONEST_OPEN_CHALLENGE_FOR_QNG (a tension, not a "
        "win). Planck measures the primordial spectrum to be nearly scale-invariant "
        "and slightly RED, n_s = 0.9649 +- 0.0042 -- the second-most-precise "
        "cosmological observable and a sharp test. QNG does NOT obviously pass it. "
        "(T1) QNG's primordial seed is the substrate SHOT NOISE, sigma(M) ~ 1/sqrt(N) "
        "~ (M_Pl/M)^(1/2) (P47); since the horizon mass scales as M ~ k^-3, the power "
        "spectrum is P(k) ~ sigma^2 ~ M^-1 ~ k^3 -- a STEEPLY BLUE spectrum (effective "
        "n_s ~ 4), the OPPOSITE of the observed slightly-red 0.965. (T2) The "
        "matter-dominated growth of the un-packing era (delta ~ a, P48) is "
        "scale-dependent and shifts the tilt, but matter domination is NOT a de "
        "Sitter phase and does not generically produce a scale-invariant spectrum -- "
        "scale-invariance is precisely what INFLATION (near-exponential expansion) "
        "delivers. (T3) HONEST VERDICT: turning the steeply-blue shot-noise spectrum "
        "into the observed slightly-red n_s = 0.965 is NOT natural in QNG's "
        "matter-dominated un-packing picture; reproducing n_s most plausibly requires "
        "an early NEAR-DE-SITTER (inflationary) phase, which the matter-dominated "
        "un-packing (P48-49) does not provide. So this is a GENUINE OPEN CHALLENGE -- "
        "indeed a potential TENSION -- for QNG cosmology, and it is flagged openly, "
        "not hidden among the wins. The implication: QNG's early universe likely needs "
        "a brief inflationary (de Sitter) epoch IN ADDITION to the un-packing -- "
        "perhaps a transient near-de-Sitter phase as the substrate begins to un-pack "
        "from the maximum-density state, before matter domination sets in -- to "
        "stretch fluctuations to scale-invariance. Identifying whether the QNG "
        "substrate supports such a phase (e.g. a brief chi-driven de Sitter stage) is "
        "the natural next problem. HONEST CONTEXT: this does NOT contradict P64 (QNG "
        "is LambdaCDM-like and matches the acoustic PEAKS) -- the peaks test the "
        "late-time content (CDM+baryons+DE), which QNG has; n_s tests the PRIMORDIAL "
        "spectrum, a separate and sharper requirement that QNG's structure-seeding "
        "mechanism does not yet meet. Reporting this tension is part of the no-hype "
        "discipline: QNG has real wins (P36-83) AND real open problems, and the "
        "primordial spectral index is currently one of the latter.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"n_s_obs": NS_OBS, "n_s_err": NS_ERR, "n_s_shot_noise": n_s_shot,
                   "tension": bool(tension), "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
