# REPORT — demo Phase-19 (Drumul 2) lattice LIV prediction

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase19_LIV_prediction.py`
Verdict: **QNG_LIV_PREDICTION_n2**

The QNG cubic lattice phase dispersion omega^2 = c^2 * 2(3 - sum cos k_i) gives a
direction- AND energy-dependent photon speed:
   c_eff^2 = 1 - (1/12)(sum_i k_i^4 / k^2)
   anisotropy([100] vs [111]) = -k^2/18  (lattice units; [100] is SLOWER)
verified analytically vs numeric (-5.556e-4 at k=0.1, exact match).

Physical: Delta v/c ~ (1/18)(E/E_cut)^2, E_cut = hbar c/a_L = E_Planck/0.305 =
4.0e19 GeV. n=2 (quadratic) LIV with QNG-specific coefficient 1/18, and a
DISTINCTIVE cubic-lattice DIRECTION-dependence (isotropic continuum theories give
zero direction-dependence).

Honest scope: n=2 LIV is tiny at TeV (Delta v/c ~ 3e-47 at 1 TeV) -- far below
current GRB/blazar bounds; a consistency feature, not an imminent test. The
theory's headline LIV (eta_LV=0.0116/0.0347, theory-v2 ch.31/32) is a different,
more testable n=1 matter-sector mechanism. This phase adds the clean
lattice-kinematic n=2 piece; the distinctive falsifiable signature is the
DIRECTION-dependence (1/18 anisotropy), unique to the cubic-lattice substrate.
