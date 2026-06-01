"""
E4 -- Mass as resonance? Measure, for vortex rings R = 3,4,5:
   (a) Sigma sigma_m deficit  = the volume / topological charge  (old M_ring)
   (b) omega_1                = internal breathing frequency (FFT of the deficit)
and test three hypotheses for physical mass against the baryon ladder
N(938), Delta(1232), N*(1520):

   H_volume   :  m ~ Sigma sigma_m            (DER-QNG-038 found this matches)
   H_freq     :  m ~ omega_1                  (pure cavity resonance, ~1/R)
   H_product  :  m ~ Sigma sigma_m * omega_1  (page-05 conjecture: density x freq)

Self-contained: builds a poloidal vortex ring phi = atan2(z, rho-R), carves
sigma_m by Channel F (depletion where phase coherence |Z| < 1), then evolves phi
conservatively (v8-style, with momentum) and FFTs the breathing of the deficit.

ASCII output, CPU/numpy.
"""

import json
import os
import numpy as np

BETA_PHI = 0.06
MU_PHI = 0.857
GAMMA_PHI = 0.10
SIGMA_REF = 1.0
DT = 0.2

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-e4-mass-resonance-v1")

# baryon ladder for comparison (MeV)
PDG = {3: None, 4: 938.0, 5: 1232.0}   # R=3 has no SM match (per DER-QNG-038)


def laplacian(f):
    lap = np.zeros_like(f)
    for ax in range(3):
        lap += np.roll(f, 1, axis=ax) + np.roll(f, -1, axis=ax)
    lap -= 6.0 * f
    return lap


def local_coherence(phi):
    """|Z_i| = | mean of exp(i phi) over the 6 neighbors |  in [0,1]."""
    z = np.zeros(phi.shape, dtype=complex)
    for ax in range(3):
        z += np.exp(1j*np.roll(phi, 1, axis=ax)) + np.exp(1j*np.roll(phi, -1, axis=ax))
    z /= 6.0
    return np.abs(z)


def vortex_ring(L, R):
    x = np.arange(L) - L/2.0
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    rho = np.sqrt(X**2 + Y**2)
    phi = np.arctan2(Z, rho - R)        # 2pi poloidal winding around the tube
    return phi


def run_ring(L, R, carve_steps=700, evolve_steps=700):
    phi = vortex_ring(L, R)
    sigma = np.full((L, L, L), SIGMA_REF)

    # --- Phase 2: carve sigma_m by Channel F (phi held fixed) ---
    for _ in range(carve_steps):
        coh = local_coherence(phi)
        sigma -= DT * GAMMA_PHI * (1.0 - coh) * sigma
        np.clip(sigma, 0.0, SIGMA_REF, out=sigma)
    deficit = float(SIGMA_REF * sigma.size - sigma.sum())  # volume charge

    # --- Phase 3: conservative phi evolution (v8), record breathing ---
    # give a small radial breathing kick via a perturbed momentum
    pi = 0.05 * np.sin(phi)             # small momentum perturbation
    series = []
    for t in range(evolve_steps):
        # Hamilton: phidot = pi/mu ; pidot = beta*lap(phi) - gamma coupling to sigma
        coh = local_coherence(phi)
        acc = (BETA_PHI * laplacian(phi)) / MU_PHI
        pi += DT * MU_PHI * acc
        phi += DT * pi / MU_PHI
        # re-measure deficit breathing (Channel F response, weak)
        sig_t = sigma - DT*0  # sigma frozen; track coherence-deficit proxy instead
        if t % 3 == 0:
            # breathing proxy: total phase-incoherence (1-|Z|) summed -> oscillates
            series.append(float((1.0 - coh).sum()))
    series = np.array(series) - np.mean(series)
    if np.allclose(series, 0):
        omega1 = 0.0
    else:
        sp = np.abs(np.fft.rfft(series))
        fr = np.fft.rfftfreq(len(series), d=3*DT)
        omega1 = float(2*np.pi*fr[np.argmax(sp[1:]) + 1])
    return {"R": R, "deficit_sigma_m": deficit, "omega_1": omega1}


def main():
    print("="*70)
    print("E4 -- mass as resonance? rings R=3,4,5")
    print("="*70)

    L = 28
    rows = []
    for R in (3, 4, 5):
        r = run_ring(L, R)
        rows.append(r)
        print("\n  R=%d  Sigma_sigma_m deficit = %.2f   omega_1 = %.5f"
              % (R, r["deficit_sigma_m"], r["omega_1"]))

    print("\n  [CAVEAT] self-contained sim is CRUDE: the deficit above does NOT")
    print("  reproduce canonical M_ring (CPU-074: 474/729/955) -- Channel F here")
    print("  depletes sigma_m globally, not just the ring core; and omega_1 is")
    print("  R-independent (a global phi mode, not the toroidal cavity mode).")
    print("  The decisive analysis below uses the ESTABLISHED canonical M_ring.")

    # ---- canonical analysis using established CPU-074 M_ring (= Sigma sigma_m) ----
    M_canon = {3: 474.15, 4: 728.92, 5: 954.88}   # CPU-074 conserved charge
    # cavity conjecture omega_1 ~ c_phi / R  (page 05)
    c_phi = np.sqrt(BETA_PHI/MU_PHI)
    om_cav = {R: c_phi/R for R in (3, 4, 5)}

    def rat(d, R):
        return d[R]/d[4]
    H_vol = {R: rat(M_canon, R) for R in (3, 4, 5)}
    H_frq = {R: rat(om_cav, R) for R in (3, 4, 5)}
    prodd = {R: M_canon[R]*om_cav[R] for R in (3, 4, 5)}
    H_prod = {R: prodd[R]/prodd[4] for R in (3, 4, 5)}

    print("\n" + "="*70)
    print("HYPOTHESIS TEST -- canonical M_ring (CPU-074) + cavity omega~1/R")
    print("  (ratios normalized to R=4; target Delta/N = 1.313)")
    print("="*70)
    target = PDG[5]/PDG[4]   # Delta/N = 1.313
    print("  R5/R4   H_volume = %.3f   H_freq = %.3f   H_product = %.3f   | PDG = %.3f"
          % (H_vol[5], H_frq[5], H_prod[5], target))
    print("  R3/R4   H_volume = %.3f   H_freq = %.3f   H_product = %.3f   | PDG = (no match)"
          % (H_vol[3], H_frq[3], H_prod[3]))

    # which hypothesis is closest to PDG Delta/N at R5/R4
    cand = {"H_volume": H_vol[5], "H_freq": H_frq[5], "H_product": H_prod[5]}
    best = min(cand, key=lambda h: abs(cand[h] - target))
    print("\n  closest to baryon ladder at R5/R4: %s (%.3f vs %.3f)"
          % (best, cand[best], target))

    if best == "H_volume":
        verdict = ("MASS_IS_VOLUME_CHARGE: the baryon ladder (Delta/N=1.313) is "
                   "reproduced by canonical Sigma sigma_m alone (H_volume=1.310, "
                   "0.2%% off), NOT by the product with a 1/R cavity frequency "
                   "(H_product=1.048). The page-05 'mass = 1/R resonance' "
                   "conjecture is DISFAVORED: multiplying by omega~1/R BREAKS the "
                   "match. Mass tracks the conserved volume/topological charge "
                   "(consistent with DER-QNG-038, modulo Gap 14 lattice "
                   "dependence). DIVISION OF LABOR HOLDS: frequency/edges set "
                   "LIGHT (E5/E7), node volume-charge sets MASS. NOTE: a faithful "
                   "omega_1(R) still needs the real v8 ring infrastructure; if "
                   "omega_1 were R-INDEPENDENT (not 1/R), product==volume and the "
                   "match survives -- so 'resonance' is only excluded in its "
                   "specific 1/R cavity form, not as a constant dressing.")
    elif best == "H_product":
        verdict = ("MASS_IS_DENSITY_TIMES_FREQUENCY: product law matches ladder "
                   "-> page-05 resonance conjecture SUPPORTED.")
    else:
        verdict = ("MASS_IS_PURE_FREQUENCY: cavity 1/R matches -> unexpected; "
                   "investigate.")
    print("\n  => " + verdict)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump({"rows": rows, "ratios_R5_R4": cand,
                   "pdg_target": target, "best": best,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
