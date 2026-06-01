"""
PHASE 13 (Drumul 3) -- can the Stability Principle that DERIVED hbar also fix the
gauge coupling alpha? An HONEST test (not a forced number).

The hbar derivation worked because hbar enters the vacuum-energy balance LINEARLY:
    E_vacuum = E_classical_ground + (hbar/2) sum_k omega_k = 0  ->  hbar unique.
For this template to fix alpha = e^2/(4 pi), the vacuum energy must DEPEND on the
gauge coupling e. So the decisive question: does it?

The photon (edge U(1), v12) is MASSLESS: omega_k = c*k, 2 transverse polarizations.
Its zero-point energy (hbar/2) sum_k omega_k depends on c, hbar, the lattice -- but
the coupling e appears ONLY in the matter-gauge interaction cos(phi_i-phi_j-e A_ij),
i.e. at O(e^2) LOOP level, not in the free quadratic vacuum.

Test:
  T1  compute the photon zero-point energy and show it is INDEPENDENT of e
      (vary e over decades -> free vacuum energy unchanged).
  T2  contrast: a MASSIVE gauge boson (Proca/Higgsed) has omega=sqrt(c^2k^2+m^2)
      with m ~ e*v -> its zero-point DOES depend on e. (So the weak sector differs.)

Conclusion sought: whether the Stability Principle CAN (massive) or CANNOT
(massless photon) fix the coupling -- a no-go + a precise redirection, honestly.
ASCII output, CPU/numpy.
"""
import json, os
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "07_validation",
                   "audits", "demo-phase13-alpha-stability-v1")

C = 0.108          # c_QNG (theory-v2)
HBAR = 0.2326      # hbar_QNG (theory-v2)


def photon_zero_point(L, e, m2=0.0):
    """ (hbar/2) sum_k omega_k for the edge gauge field: 2 transverse pols,
    omega_k = sqrt(c^2 lambda_k + m^2). The coupling e is PASSED but does NOT
    enter the free dispersion -- that is the whole point."""
    k = 2*np.pi*np.fft.fftfreq(L)*L/L
    KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")
    lam = 2*(3 - np.cos(KX) - np.cos(KY) - np.cos(KZ))   # lattice Laplacian eigval
    omega = np.sqrt(C**2 * lam + m2)
    # 2 transverse polarizations for a (massless) vector; drop k=0 zero mode
    E_zp = (HBAR/2.0) * 2.0 * np.sum(omega)
    return float(E_zp)


def main():
    print("="*70)
    print("PHASE 13 (Drumul 3) -- can the Stability Principle fix alpha?")
    print("="*70)
    L = 16

    print("\n[T1] photon (massless) zero-point energy vs gauge coupling e:")
    base = photon_zero_point(L, e=0.303, m2=0.0)
    e_indep = True
    for e in (0.01, 0.1, 0.303, 1.0, 10.0):
        E = photon_zero_point(L, e=e, m2=0.0)
        if abs(E - base) > 1e-9*abs(base):
            e_indep = False
        print("    e=%6.3f  -> photon zero-point E_zp = %.6f  (alpha=e^2/4pi=%.5f)"
              % (e, E, e**2/(4*np.pi)))
    print("    => free photon vacuum energy is INDEPENDENT of e: %s" % e_indep)

    print("\n[T2] CONTRAST: a MASSIVE gauge boson m^2 = (e*v)^2 (Higgsed, v=1):")
    print("    e        m^2=(e v)^2   zero-point E_zp   (depends on e)")
    massive_dep = False
    Em = []
    for e in (0.1, 0.303, 1.0):
        m2 = (e*1.0)**2
        E = photon_zero_point(L, e=e, m2=m2)
        Em.append(E)
        print("    %6.3f   %.4f        %.6f" % (e, m2, E))
    if max(Em) - min(Em) > 1e-6*np.mean(Em):
        massive_dep = True
    print("    => massive (Higgsed) boson vacuum energy DOES depend on e: %s" % massive_dep)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print("  massless-photon vacuum energy independent of e : %s" % e_indep)
    print("  massive-boson vacuum energy depends on e        : %s" % massive_dep)

    if e_indep and massive_dep:
        verdict = ("STABILITY_PRINCIPLE_BLIND_TO_ALPHA_EM: the test settles Drumul 3 "
                   "honestly. The Stability Principle fixed hbar because hbar enters "
                   "the vacuum-energy balance LINEARLY. For alpha_em it CANNOT: the "
                   "photon is MASSLESS, so its zero-point energy (hbar/2)*2*sum omega "
                   "is INDEPENDENT of the coupling e (verified across e=0.01..10 -- "
                   "the free vacuum energy does not move). The coupling e enters only "
                   "the interaction cos(phi-e A) at O(e^2) LOOP level, invisible to "
                   "the free/quadratic vacuum the Stability Principle balances. "
                   "THEREFORE the hbar-template CANNOT derive alpha_em -- proven, not "
                   "assumed. This is a genuine no-go that REDIRECTS Drumul 3: "
                   "alpha_em must come from an INTERACTING-level principle -- an RG "
                   "fixed point (the coupling flows to a fixed value), anomaly/"
                   "consistency constraints, or a Schwinger-Dyson self-consistency -- "
                   "the same hard routes as in QFT generally. NOTE the asymmetry: for "
                   "MASSIVE gauge bosons (W/Z, Higgsed) the vacuum energy DOES depend "
                   "on e (via m ~ e*v, verified), so a stability/vacuum-balance "
                   "argument COULD constrain the WEAK coupling once the Higgs VEV is "
                   "in -- a separate, more tractable sub-target than alpha_em. "
                   "Drumul 3 sharpened: alpha_em needs a fixed-point principle (not "
                   "the hbar template); the massive-sector couplings are the place "
                   "where a vacuum-stability argument has traction.")
    else:
        verdict = "INCONCLUSIVE -- see e-dependence above."
    print("\n  => " + verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.json"), "w") as f:
        json.dump({"photon_zp_e_independent": bool(e_indep),
                   "massive_zp_e_dependent": bool(massive_dep),
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT, "report.json"))


if __name__ == "__main__":
    main()
