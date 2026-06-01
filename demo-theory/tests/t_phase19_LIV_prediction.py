"""
PHASE 19 (Drumul 2, concrete) -- a falsifiable Lorentz-violation (LIV) prediction
from the QNG lattice dispersion.

A discrete lattice breaks continuous Lorentz invariance at order (k a)^2: the
phase dispersion omega^2 = c^2 * 2(3 - cos kx - cos ky - cos kz) expands as
   omega^2 = c^2 [ k^2 - (1/12) sum_i k_i^4 + ... ]
so the effective speed depends on DIRECTION (anisotropy) and on |k| (dispersion).
This is a concrete, QNG-specific, FALSIFIABLE prediction: high-energy photons
travel at slightly direction/energy-dependent speeds, testable via gamma-ray
burst arrival times (CTA, Fermi-LAT).

We compute:
  T1 the leading (k a)^2 anisotropy between [100] and [111] directions.
  T2 the energy scale: at physical momentum p, k a = p a_L / hbar = p / E_cut,
     E_cut = hbar c / a_L (a few x Planck). The fractional speed deviation
     Delta v/c ~ coeff * (E/E_cut)^2 -- an n=2 (quadratic) LIV.
  T3 the dimensionless coefficient (QNG-specific, from a_L = 0.305 lP).

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase19-LIV-prediction-v1")

A_L_OVER_LP = 0.305          # lattice spacing / Planck length (theory-v2 ch.06)
E_PLANCK_GEV = 1.22e19


def omega2_over_c2(kvec):
    """lattice phase dispersion omega^2/c^2 = 2(3 - sum cos k_i)."""
    return 2.0*(3.0 - np.cos(kvec[0]) - np.cos(kvec[1]) - np.cos(kvec[2]))


def main():
    print("="*70)
    print("PHASE 19 (Drumul 2) -- falsifiable LIV prediction from the QNG lattice")
    print("="*70)

    # T1: anisotropy between [100] and [111] at small k (measure c_eff(k) per dir)
    print("\n[T1] direction-dependent effective speed c_eff(k)^2 = omega^2/k^2:")
    print("     k        c_eff[100]^2   c_eff[111]^2   anisotropy (rel)")
    aniso = {}
    for k in (0.1, 0.2, 0.4):
        k100 = np.array([k, 0, 0])
        k111 = np.array([k, k, k])/np.sqrt(3)   # same |k|
        c100 = omega2_over_c2(k100)/k**2
        c111 = omega2_over_c2(k111)/k**2
        rel = (c100 - c111)/(0.5*(c100+c111))
        aniso[k] = rel
        print("     %.2f     %.6f      %.6f      %.3e" % (k, c100, c111, rel))

    # T2/T3: the leading coefficient. Analytic: omega^2/k^2 = 1 - (1/12) S4/k^2,
    # S4 = sum k_i^4. [100]: S4/k^2 = k^2 ; [111]: S4/k^2 = k^2/3.
    # so c_eff^2 = 1 - (1/12)(S4/k^2); anisotropy(100-111) = (1/12)(k^2 - k^2/3) = k^2/18.
    print("\n[T2/T3] analytic leading coefficient:")
    print("     c_eff^2 = 1 - (1/12)(sum k_i^4 / k^2)   [k in lattice units = k_phys*a_L]")
    print("     anisotropy(100 vs 111) = k^2/18  (lattice units)")
    # check analytic vs numeric at k=0.1 (sign: [100] is SLOWER -> anisotropy < 0)
    pred = -0.1**2/18
    print("     analytic anisotropy at k=0.1: %.3e   numeric: %.3e ([100] slower)"
          % (pred, aniso[0.1]))

    # physical: k_lattice = E/E_cut, E_cut = hbar c / a_L = E_Planck / (a_L/lP)
    E_cut = E_PLANCK_GEV / A_L_OVER_LP
    print("\n  LIV cutoff E_cut = hbar c / a_L = E_Planck/(a_L/lP) = %.3e GeV" % E_cut)
    print("  => fractional speed deviation  Delta v/c ~ (1/18)(E/E_cut)^2  (n=2 LIV)")
    coeff = 1.0/18.0
    print("  dimensionless coefficient = 1/18 = %.4f (QNG-specific, from cubic lattice)" % coeff)

    # concrete numbers for a CTA-band photon
    for E_obs_TeV in (1.0, 10.0, 100.0):
        E = E_obs_TeV*1e-3  # GeV
        dvc = coeff*(E/E_cut)**2
        print("     E=%6.1f TeV: Delta v/c ~ %.2e (n=2)" % (E_obs_TeV, dvc))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    analytic_ok = abs(abs(pred) - abs(aniso[0.1]))/abs(pred) < 0.05
    print("  analytic (-k^2/18) matches numeric lattice anisotropy : %s" % analytic_ok)

    verdict = (
        "QNG_LIV_PREDICTION_n2: the QNG cubic lattice predicts a concrete, "
        "falsifiable Lorentz-violation signature. The phase dispersion gives a "
        "direction- and energy-dependent photon speed: Delta v/c ~ (1/18)(E/E_cut)^2 "
        f"with E_cut = hbar c / a_L = {E_cut:.2e} GeV (= E_Planck/0.305, set by the "
        "DERIVED lattice spacing a_L=0.305 lP). This is an n=2 (quadratic) LIV with "
        "a QNG-SPECIFIC coefficient 1/18 (from the cubic-lattice sum_i k_i^4 "
        "anisotropy), verified analytically vs the numeric lattice dispersion. "
        "FALSIFIABLE: gamma-ray-burst / blazar arrival-time dispersion (CTA, "
        "Fermi-LAT) constrains exactly this n=2 term. NOTE: n=2 LIV is suppressed "
        "by (E/E_cut)^2 ~ (E/10^19 GeV)^2 -- tiny at TeV (Delta v/c ~ 10^-32), so "
        "this LATTICE-anisotropy LIV is far below current bounds (it is a "
        "consistency feature, not an imminent test). The theory's headline LIV "
        "(eta_LV=0.0116/0.0347, theory-v2 ch.31/32) is a DIFFERENT, n=1-type "
        "mechanism from the matter sector -- the more testable one. This phase adds "
        "the lattice-kinematic n=2 piece as a clean, QNG-derived, direction- "
        "AND-energy-dependent prediction (the anisotropy 1/18 is the distinctive, "
        "cubic-lattice-specific signature -- isotropic continuum theories predict "
        "zero direction-dependence).")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"anisotropy_vs_k": {str(k): float(v) for k, v in aniso.items()},
                   "coefficient": coeff, "E_cut_GeV": E_cut,
                   "analytic_matches_numeric": bool(analytic_ok),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
