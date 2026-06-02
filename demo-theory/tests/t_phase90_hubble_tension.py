"""
PHASE 90 (cosmology) -- the Hubble tension and QNG's holographic dark energy.

The H0 tension: early-universe (Planck CMB) H0 = 67.4 +- 0.5 vs late-universe (SH0ES)
H0 = 73.0 +- 1.0 -- a ~5-sigma discrepancy. Does QNG's evolving holographic dark
energy (P57: w0=-1.06, wa=+0.62) ease it, worsen it, or neither? Be honest.

  T1 the mechanism: for a fixed CMB calibration, dark energy that is PHANTOM (w<-1) at
     late times RAISES the inferred local H0 (less deceleration recently -> faster
     recent expansion). QNG's w0 = -1.06 < -1 is (slightly) phantom TODAY -> pushes
     H0 UP -> in the HELPFUL direction for the tension.
  T2 BUT QNG's wa = +0.62 > 0 means w was LESS phantom (toward quintessence) in the
     past -> the early-time effect partly offsets. The NET shift needs a full fit;
     a slightly-phantom-today, quintessence-past history gives a modest H0 increase.
  T3 honest: QNG's holographic DE points in the RIGHT direction (phantom-today raises
     H0) but a w0~-1.06 alone gives only a partial (~1-2 km/s/Mpc) shift -- not the
     full ~5 km/s/Mpc needed. So QNG EASES but does not obviously RESOLVE the H0
     tension; a quantitative MCMC fit (not done here) is needed. Same status as most
     evolving-DE models.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase90-hubble-v1")

H0_PLANCK = 67.4; H0_SH0ES = 73.0
W0_QNG = -1.06; WA_QNG = 0.62


def main():
    print("="*70)
    print("PHASE 90 (cosmology) -- the Hubble tension vs QNG holographic dark energy")
    print("="*70)
    print("\n  H0 (Planck, early) = %.1f ; H0 (SH0ES, late) = %.1f -> ~5 sigma tension"
          % (H0_PLANCK, H0_SH0ES))
    print("  needed shift: ~%.1f km/s/Mpc" % (H0_SH0ES - H0_PLANCK))

    # T1: direction
    print("\n[T1] mechanism: phantom (w<-1) dark energy raises the inferred local H0.")
    print("     QNG today: w0 = %.2f < -1 -> (slightly) PHANTOM -> pushes H0 UP." % W0_QNG)
    print("     => QNG's DE points in the HELPFUL direction for the tension.")
    helpful = W0_QNG < -1.0

    # T2: the wa offset
    print("\n[T2] but wa = +%.2f > 0 -> w was LESS phantom (quintessence-like) in the past:" % WA_QNG)
    # crude estimate: H0 shift ~ - (w0+1) * scale; phantom w0=-1.06 -> small positive shift
    # illustrative magnitude only
    dH0_est = -(W0_QNG + 1.0) * 30.0   # ~30 km/s/Mpc per unit (w0+1), rough/illustrative
    print("     a slightly-phantom-today / quintessence-past history gives a MODEST H0")
    print("     increase; rough estimate dH0 ~ %.1f km/s/Mpc (illustrative)." % dH0_est)

    # T3: honest
    print("\n[T3] honest verdict:")
    closes = dH0_est >= (H0_SH0ES - H0_PLANCK)
    print("     QNG EASES the tension (right direction, dH0 ~ +%.1f) but w0~-1.06 alone" % dH0_est)
    print("     gives only a PARTIAL shift, not the full ~%.1f needed -> does NOT clearly"
          % (H0_SH0ES - H0_PLANCK))
    print("     RESOLVE it. A quantitative MCMC fit (not done here) would settle the size.")
    print("     Same status as most evolving-DE models: helpful, not a clean cure.")
    print("     NOTE: this is the SAME w0,wa whose wa>0 is in TENSION with the DESI hint")
    print("     (P64) -- so the H0-easing and the DESI-tension are linked; the data will")
    print("     decide whether QNG's specific (w0=-1.06, wa=+0.62) is favored.")

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  QNG w0=%.2f phantom-today -> raises H0 (helpful direction): %s" % (W0_QNG, helpful))
    print("  but only a partial shift (~%.1f of the needed ~%.1f); not a clean resolution"
          % (dH0_est, H0_SH0ES - H0_PLANCK))
    print("  needs a full MCMC fit; linked to the DESI w(z) tension (P64)")

    verdict = (
        "QNG_HOLOGRAPHIC_DARK_ENERGY_EASES_BUT_DOES_NOT_CLEANLY_RESOLVE_THE_HUBBLE_"
        "TENSION. The H0 tension (Planck 67.4 vs SH0ES 73.0, ~5 sigma) is one of "
        "cosmology's sharpest current discrepancies, and evolving dark energy is a "
        "leading proposed resolution. (T1) The mechanism: for a fixed early-universe "
        "(CMB) calibration, dark energy that is PHANTOM (w < -1) at late times raises "
        "the inferred local H0. QNG's holographic dark energy has w0 = -1.06 < -1 -- "
        "slightly phantom TODAY -- so it pushes H0 UP, in the HELPFUL direction for "
        "the tension. (T2) However, QNG's wa = +0.62 > 0 means w was LESS phantom "
        "(quintessence-like) in the past, which partly offsets the late-time effect; "
        "the net H0 shift from a slightly-phantom-today / quintessence-past history is "
        "MODEST. (T3) HONEST verdict: QNG EASES the tension (it pushes H0 in the right "
        "direction) but a w0 ~ -1.06 alone yields only a partial shift (order ~1-2 "
        "km/s/Mpc), not the full ~5.6 km/s/Mpc needed -- so QNG does NOT clearly "
        "RESOLVE the H0 tension, and a quantitative MCMC fit (not done here) is "
        "required to determine the actual size. This is the same status as most "
        "evolving-dark-energy models: helpful but not a clean cure. CRUCIALLY, this is "
        "the SAME (w0=-1.06, wa=+0.62) whose wa>0 is in TENSION with the DESI "
        "evolving-DE hint (P64): the H0-easing (which wants phantom-today) and the "
        "DESI tension (which prefers wa<0) are LINKED through QNG's single holographic "
        "prediction, so the upcoming dark-energy data (DESI, Euclid) will jointly "
        "decide whether QNG's specific w(z) is favored or falsified. NET: QNG's dark "
        "energy is in the helpful direction for H0 but does not by itself resolve the "
        "tension; its honest, falsifiable signature is the specific w0=-1.06, wa=+0.62 "
        "that the next-generation surveys are now testing. HONEST: the dH0 estimate "
        "here is illustrative (a rough w0-to-H0 slope), not an MCMC; the real "
        "assessment needs a full fit to CMB+BAO+SNe with the holographic w(z). We "
        "claim only the DIRECTION (helpful) and the LINKAGE to the DESI test, not a "
        "resolution.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"H0_planck": H0_PLANCK, "H0_sh0es": H0_SH0ES, "w0": W0_QNG, "wa": WA_QNG,
                   "direction": "helpful (phantom-today raises H0)",
                   "resolves": False, "dH0_estimate_illustrative": float(dH0_est),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
