"""
PHASE 64 (validation) -- testing QNG against real data, honestly: the Planck CMB
and the dark-energy w(z) vs DESI.

The user asks how well QNG reproduces Planck (the hardest test) and what else we can
test. HONEST framing first:

  PLANCK CMB: the legacy file qng_v3_unified_best_fit.txt is a ~25-PARAMETER
  phenomenological template (damped oscillations) fit to the peaks -- NOT a
  first-principles QNG prediction. We do NOT tout its chi2. QNG's genuine content
  (cold DM, P38-50; holographic DE ~ Lambda, P53-57; baryons; un-packing seed P48)
  is LambdaCDM-LIKE, so it inherits LambdaCDM's excellent CMB fit -- but the 6
  parameters are inputs, not unique QNG predictions. QNG passes Planck the way any
  CDM+Lambda theory does (qualitative: acoustic peaks, 3rd-peak CDM signature,
  flatness -- Phase 45). Not a unique win, not a fit to brag about.

  THE REAL FALSIFIABLE TEST: the dark-energy equation of state. QNG's holographic
  chi DE (Phase 57) predicts a SPECIFIC w(z). We compare it to (a) a cosmological
  constant (w=-1), and (b) the DESI 2024 evolving-DE hint (w0~-0.83, wa~-0.75). This
  is where QNG sticks its neck out.

  T1 fit QNG's w(z) (Phase 57 Li model) to the CPL form w(a)=w0+wa(1-a).
  T2 compare QNG (w0,wa) to CC and to DESI 2024 -> is QNG consistent or in tension?
  T3 the full list of testable QNG predictions + the data we have.

ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase64-test-data-v1")

C_HOLO = 0.80


def integrate_w(c, x_min=-2.0, dx=0.001):
    """Li holographic DE: dOmega/dx=Omega(1-Omega)(1+2sqrt(Omega)/c), Omega(0)=0.69.
    w=-1/3-(2/3c)sqrt(Omega). Return (a, w) back to x_min."""
    def f(O):
        O=min(max(O,1e-12),1-1e-12); return O*(1-O)*(1+2*np.sqrt(O)/c)
    xs=[0.0]; Os=[0.69]; O=0.69; x=0.0
    while x>x_min:
        k1=f(O);k2=f(O-dx/2*k1);k3=f(O-dx/2*k2);k4=f(O-dx*k3)
        O=O-dx/6*(k1+2*k2+2*k3+k4); x-=dx; xs.append(x); Os.append(O)
    x=np.array(xs[::-1]); O=np.array(Os[::-1])
    a=np.exp(x); w=-1.0/3-(2.0/(3*c))*np.sqrt(np.clip(O,0,1))
    return a, w


def main():
    print("="*70)
    print("PHASE 64 (validation) -- testing QNG against data (Planck honest + w(z) vs DESI)")
    print("="*70)

    # T1: fit CPL to QNG w(z)
    a, w = integrate_w(C_HOLO)
    # CPL: w(a) = w0 + wa(1-a). w0 = w at a=1; fit wa by least squares over 0.3<a<1
    i0 = np.argmin(np.abs(a-1.0)); w0 = w[i0]
    mask = (a>0.3)&(a<=1.0)
    A = np.vstack([np.ones(mask.sum()), (1-a[mask])]).T
    coef,_,_,_ = np.linalg.lstsq(A, w[mask], rcond=None)
    w0_fit, wa_fit = coef
    print("\n[T1] QNG holographic chi DE (Phase 57), fit to CPL w(a)=w0+wa(1-a):")
    print("     w0 = %.3f, wa = %.3f" % (w0_fit, wa_fit))
    print("     (QNG w runs LESS negative in the past: w(z=3)=%.2f -> w0=%.2f today)"
          % (w[np.argmin(np.abs(a-0.25))], w0))

    # T2: compare to CC and DESI
    print("\n[T2] comparison (w0, wa):")
    print("     model            w0       wa       note")
    print("     cosmological L   -1.000   0.000    Lambda (no evolution)")
    print("     QNG holographic  %+.3f   %+.3f   w MORE negative toward today (wa>0)" % (w0_fit, wa_fit))
    print("     DESI 2024 hint   -0.830   -0.750   w MORE negative in PAST (wa<0)")
    print("     observed w0 (Planck+SNe+BAO, wCDM): -1.03 +- 0.03")
    desi_wa = -0.75
    same_sign = np.sign(wa_fit) == np.sign(desi_wa)
    print("     => QNG w0 = %.2f matches the constant-w fit (-1.03); BUT QNG's wa is" % w0_fit)
    print("        POSITIVE (+%.2f) while DESI's hint is NEGATIVE (-0.75): OPPOSITE" % wa_fit)
    print("        evolution. So QNG holographic DE is in TENSION with the DESI")
    print("        evolving-DE hint -- a genuine, falsifiable test (DESI hint is ~2-3 sigma).")

    # T3: the testable-predictions list
    print("\n[T3] QNG's testable predictions and the data:")
    preds = [
        ("w(z) evolution (wa>0)", "DESI/SNe/CMB", "TENSION with DESI hint (wa<0); consistent with w=-1"),
        ("no 4th fermion generation", "LEP Z-width", "CONFIRMED (N_nu=2.984~3, Phase 60)"),
        ("Koide Q=2/3 -> m_tau", "PDG lepton masses", "CONFIRMED 0.006% (Phase 61)"),
        ("DM cold/collisionless/neutral", "Planck CMB", "CONSISTENT (3rd peak, Phase 45)"),
        ("DM = gravitational-only ug relics", "direct-detection nulls", "CONSISTENT (no signal expected)"),
        ("hadron spectrum (octet+decuplet)", "PDG masses", "0.5% mean (Phase 21-23)"),
        ("LIV n=2 directional dv/c~(E/E_cut)^2", "high-E astrophysics/GRB", "UNTESTED prediction (Phase 19)"),
        ("custodial rho=1 (M_W=M_Z cos th)", "electroweak data", "0.5% (Phase 25)"),
    ]
    for p, d, s in preds:
        print("     - %-34s [%s] %s" % (p, d, s))

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  Planck CMB: QNG is LambdaCDM-like -> inherits the fit (params are inputs);")
    print("              legacy 25-param 'best fit' is phenomenological, NOT touted.")
    print("  w(z) test: QNG w0=%.2f OK, but wa=+%.2f OPPOSITE to DESI hint -> TENSION" % (w0_fit, wa_fit))
    print("  -> QNG makes a FALSIFIABLE w(z) prediction; DESI will settle it.")

    verdict = (
        "QNG_PASSES_PLANCK_AS_A_LCDM-LIKE_THEORY_AND_MAKES_A_FALSIFIABLE_w(z)_"
        "PREDICTION_IN_MILD_TENSION_WITH_DESI. Honest test against real data. PLANCK "
        "CMB: the legacy qng_v3_unified_best_fit.txt is a ~25-parameter "
        "phenomenological template (damped oscillations) fit to the peaks -- NOT a "
        "first-principles QNG prediction, so its chi2 is not evidence for QNG and we "
        "do not tout it. QNG's genuine cosmological content -- cold dark matter "
        "(Phases 38-50), holographic dark energy that today mimics Lambda (Phases "
        "53-57), ordinary baryons, and the un-packing primordial seed (Phase 48) -- "
        "is LambdaCDM-LIKE, so it reproduces the Planck spectrum as well as LambdaCDM "
        "does (the acoustic peaks at ell=220/520/820, the CDM-driven 3rd peak, "
        "flatness -- Phase 45 verified the structure on the real TT data), but the "
        "six cosmological parameters are INPUTS, not unique QNG predictions. So QNG "
        "PASSES Planck exactly the way any cold-dark-matter + Lambda theory does -- a "
        "consistency, not a unique triumph, and honestly not a fit to brag about. "
        "THE REAL, FALSIFIABLE TEST is the dark-energy equation of state. QNG's "
        "holographic chi dark energy (Phase 57) predicts a SPECIFIC w(z): fit to the "
        f"CPL form it gives w0 = {w0_fit:.2f}, wa = {wa_fit:+.2f}. The w0 agrees with "
        "the constant-w data (-1.03 +- 0.03), but the EVOLUTION sign is the key: QNG "
        "has wa POSITIVE (w becomes MORE negative toward today, less negative in the "
        "past), whereas the DESI 2024 evolving-dark-energy hint has wa NEGATIVE "
        "(w0~-0.83, wa~-0.75: w more negative/phantom in the past). These are "
        "OPPOSITE trends, so QNG's holographic dark energy is in genuine TENSION with "
        "the DESI hint -- which is exactly what makes it a real test: if DESI's "
        "evolving-DE signal (currently ~2-3 sigma) firms up with wa<0, QNG's "
        "holographic chi DE is FALSIFIED; if dark energy is constant (w=-1) or "
        "thaws with wa>0, QNG is favored. OTHER TESTABLE PREDICTIONS: no 4th "
        "generation (CONFIRMED, LEP N_nu=3, Phase 60); Koide Q=2/3 -> m_tau to 0.006% "
        "(CONFIRMED, Phase 61); cold/collisionless/neutral DM (CONSISTENT with the "
        "Planck 3rd peak); DM as gravitational-only microgram Planck relics "
        "(CONSISTENT with all direct-detection nulls -- it predicts NO WIMP/axion "
        "signal); the light-hadron spectrum to 0.5% (Phases 21-23); custodial rho=1 "
        "(0.5%, Phase 25); and an UNTESTED falsifiable Lorentz-violation prediction "
        "(direction-dependent dv/c ~ (E/E_cut)^2, n=2, Phase 19) for high-energy "
        "astrophysics. NET: QNG is consistent with the Planck CMB as a LambdaCDM-like "
        "theory (no unique CMB triumph, no over-claimed fit), and its sharpest "
        "near-term falsifiable handle is the dark-energy w(z), where it predicts "
        "wa>0 -- testably OPPOSITE to the current DESI evolving-DE hint. The honest "
        "headline: QNG does not 'beat' Planck (nothing does better than LambdaCDM "
        "there), but it survives it and stakes a clear, falsifiable claim on the "
        "next dark-energy data.")
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"w0_fit": float(w0_fit), "wa_fit": float(wa_fit),
                   "desi_w0": -0.83, "desi_wa": -0.75, "same_sign_wa": bool(same_sign),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
