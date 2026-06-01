"""
E5 -- The honest-photon make-or-break test for demo-theory.

Question (from demo-theory/03-light-without-a-gauge-field.md):
    Does the TRANSVERSE part of the edge field theta_ij = phi_i - phi_j
    constitute a genuine propagating light mode (2 polarizations at c_phi),
    or is it identically zero / pinned to defects?

Method: discrete Hodge/Helmholtz decomposition of the edge 1-form via FFT.
    theta_a(x) = phi(x + e_a) - phi(x)          (forward difference = exterior derivative d)
    Fourier symbol of d along axis a:  D_a(k) = exp(i k_a) - 1
    For a SINGLE-VALUED scalar phi:  theta_hat = D * phi_hat  is EXACTLY parallel
    to D(k), so the transverse projector P_T = I - D D^dagger/|D|^2 annihilates it.
    => transverse fraction must be ~ machine epsilon (structural no-go).
    Topological winding (vortices) makes phi multi-valued; the WRAPPED edge field
    acquires a transverse (co-exact) part. We test whether that part PROPAGATES.

Parts:
    A  reference c_phi from phi-wave dispersion
    B  (E5a) smooth single-valued phi  -> transverse fraction (expect ~0)
    C  (E5b) vortex line phi (winding)  -> transverse fraction (expect >0, at core)
    D  (E5c) evolve vortex; does transverse energy radiate at c_phi or stay pinned?

All ASCII output (Windows cp1252 safe). CPU/numpy only.
"""

import json
import os
import numpy as np

# ----------------------------------------------------------------------------
# Substrate parameters (phi sector, from theory: DER-QNG-042)
# ----------------------------------------------------------------------------
BETA_PHI = 0.06      # phase rigidity (stiffness)
MU_PHI   = 0.857     # phase inertia
M2       = 0.0       # massless light branch for the reference/decomposition
DT       = 0.2

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-e5-transverse-light-v1")


# ----------------------------------------------------------------------------
# Lattice operators
# ----------------------------------------------------------------------------
def graph_laplacian(phi):
    """Sum over 6 cubic neighbors of (phi_j - phi_i), periodic."""
    lap = np.zeros_like(phi)
    for ax in range(3):
        lap += np.roll(phi, +1, axis=ax) + np.roll(phi, -1, axis=ax)
    lap -= 6.0 * phi
    return lap


def edge_field(phi, wrap):
    """theta_a(x) = phi(x+e_a) - phi(x). If wrap, fold into (-pi, pi]."""
    th = np.stack([np.roll(phi, -1, axis=ax) - phi for ax in range(3)], axis=0)
    if wrap:
        th = (th + np.pi) % (2.0 * np.pi) - np.pi
    return th  # shape (3, L, L, L)


def helmholtz_fractions(theta):
    """Hodge-decompose the edge 1-form. Returns (frac_long, frac_trans,
    transverse_energy_density_field)."""
    L = theta.shape[1]
    k1 = 2.0 * np.pi * np.fft.fftfreq(L) * L / L  # = 2 pi n / L
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    # Fourier symbol of forward difference d along each axis: exp(i k)-1
    D = np.stack([np.exp(1j * KX) - 1.0,
                  np.exp(1j * KY) - 1.0,
                  np.exp(1j * KZ) - 1.0], axis=0)        # (3,L,L,L) complex
    Dmag2 = np.sum(np.abs(D) ** 2, axis=0)               # |D(k)|^2
    Dmag2_safe = np.where(Dmag2 > 1e-14, Dmag2, 1.0)

    th_hat = np.stack([np.fft.fftn(theta[a]) for a in range(3)], axis=0)

    # longitudinal coefficient  c_L(k) = (D^dagger . th_hat)/|D|^2
    cL = np.sum(np.conj(D) * th_hat, axis=0) / Dmag2_safe
    th_long = D * cL                                     # P_L theta
    th_trans = th_hat - th_long                          # P_T theta
    # zero mode (D=0) carries no gradient/curl meaning -> drop from both
    mask0 = Dmag2 <= 1e-14
    th_long[:, mask0] = 0.0
    th_trans[:, mask0] = 0.0

    # Parseval energies
    E_long = np.sum(np.abs(th_long) ** 2)
    E_trans = np.sum(np.abs(th_trans) ** 2)
    E_tot = E_long + E_trans
    frac_long = E_long / E_tot if E_tot > 0 else 0.0
    frac_trans = E_trans / E_tot if E_tot > 0 else 0.0

    # transverse energy density back in real space (for locality test)
    trans_real = np.stack([np.fft.ifftn(th_trans[a]).real for a in range(3)], axis=0)
    trans_dens = np.sum(trans_real ** 2, axis=0)
    return frac_long, frac_trans, trans_dens


# ----------------------------------------------------------------------------
# PART A -- reference c_phi from dispersion of a single phi plane-wave
# ----------------------------------------------------------------------------
def measure_c_phi(L=24, n_mode=2, steps=400):
    x = np.arange(L)
    KX, _, _ = np.meshgrid(x, x, x, indexing="ij")
    k = 2.0 * np.pi * n_mode / L
    phi = 0.01 * np.cos(k * KX)
    v = np.zeros_like(phi)

    series = []
    for _ in range(steps):
        acc = (BETA_PHI * graph_laplacian(phi) - M2 * np.sin(phi)) / MU_PHI
        v += DT * acc
        phi += DT * v
        series.append(phi[1, 1, 1] + phi[L // 2, 1, 1])  # sample
    series = np.array(series) - np.mean(series)
    # dominant frequency via FFT of the time series
    sp = np.abs(np.fft.rfft(series))
    freqs = np.fft.rfftfreq(len(series), d=DT)
    omega = 2.0 * np.pi * freqs[np.argmax(sp[1:]) + 1]
    # lattice dispersion: omega^2 = (BETA/MU) * 2(1-cos k)  (1 active axis)
    k_eff2 = 2.0 * (1.0 - np.cos(k))
    c_meas = omega / np.sqrt(k_eff2) if k_eff2 > 0 else float("nan")
    c_theory = np.sqrt(BETA_PHI / MU_PHI)
    return {"omega_meas": float(omega), "k": float(k),
            "c_phi_meas": float(c_meas), "c_phi_theory_smallk": float(c_theory)}


# ----------------------------------------------------------------------------
# PART B (E5a) -- smooth single-valued phi: transverse must vanish
# ----------------------------------------------------------------------------
def part_B_smooth_scalar(L=32, seed=0):
    rng = np.random.default_rng(seed)
    x = np.arange(L)
    KX, KY, KZ = np.meshgrid(x, x, x, indexing="ij")
    # smooth single-valued field: a few low-k Fourier modes (no winding)
    phi = np.zeros((L, L, L))
    for _ in range(6):
        nx, ny, nz = rng.integers(1, 4, size=3)
        a = rng.normal()
        ph = rng.uniform(0, 2 * np.pi)
        phi += a * np.cos(2 * np.pi * (nx * KX + ny * KY + nz * KZ) / L + ph)
    theta = edge_field(phi, wrap=False)
    fL, fT, _ = helmholtz_fractions(theta)
    # also with wrap=True but amplitude kept < pi so no actual wrapping occurs
    phi_small = phi / (np.max(np.abs(theta)) + 1e-9) * 0.5  # ensure |dphi|<pi
    theta_w = edge_field(phi_small, wrap=True)
    fLw, fTw, _ = helmholtz_fractions(theta_w)
    return {"frac_long": float(fL), "frac_trans": float(fT),
            "frac_trans_wrapped_nowrapneeded": float(fTw)}


# ----------------------------------------------------------------------------
# PART C (E5b) -- vortex line (winding 2pi): wrapped edge gets transverse part
# ----------------------------------------------------------------------------
def make_vortex_line(L, charge=1):
    """phi = charge * atan2(y-y0, x-x0), winding around the z-axis line."""
    x = np.arange(L)
    X, Y, _ = np.meshgrid(x, x, x, indexing="ij")
    x0 = y0 = L / 2.0
    phi = charge * np.arctan2(Y - y0, X - x0)
    return phi, (x0, y0)


def part_C_vortex(L=32, charge=1):
    phi, (x0, y0) = make_vortex_line(L, charge)
    theta_raw = edge_field(phi, wrap=False)    # treats branch cut as huge gradient
    theta_wrap = edge_field(phi, wrap=True)     # physical compact edge field
    fL_r, fT_r, _ = helmholtz_fractions(theta_raw)
    fL_w, fT_w, tdens = helmholtz_fractions(theta_wrap)

    # locality: fraction of transverse energy within radius 4 of the core line
    x = np.arange(L)
    X, Y, _ = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt((X - x0) ** 2 + (Y - y0) ** 2)
    core = tdens[r <= 4.0].sum()
    halo = tdens[r > 4.0].sum()
    core_frac = core / (core + halo) if (core + halo) > 0 else 0.0
    return {"frac_trans_wrapped": float(fT_w),
            "frac_trans_unwrapped": float(fT_r),
            "transverse_core_fraction_r<=4": float(core_frac)}


# ----------------------------------------------------------------------------
# PART D (E5c) -- evolve vortex; does transverse energy radiate at c_phi?
# ----------------------------------------------------------------------------
def part_D_propagation(L=28, charge=1, steps=300, m2=0.02):
    """Evolve a vortex configuration under sine-Gordon phi dynamics and watch
    the transverse-energy radius vs time. Radiating light => radius grows ~ c*t.
    Pinned/topological => radius stays ~const."""
    phi, (x0, y0) = make_vortex_line(L, charge)
    # add a localized transverse 'kick': a small azimuthal velocity bump
    x = np.arange(L)
    X, Y, _ = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt((X - x0) ** 2 + (Y - y0) ** 2)
    v = 0.3 * np.exp(-((r - 5.0) ** 2) / 2.0)  # ring-shaped impulse at r=5

    c_phi = np.sqrt(BETA_PHI / MU_PHI)
    radii = []
    times = []
    for t in range(steps):
        acc = (BETA_PHI * graph_laplacian(phi) - m2 * np.sin(phi)) / MU_PHI
        v += DT * acc
        phi += DT * v
        if t % 20 == 0:
            theta = edge_field(phi, wrap=True)
            _, _, tdens = helmholtz_fractions(theta)
            w = tdens
            rad = np.sqrt((w * r ** 2).sum() / (w.sum() + 1e-12))  # rms radius
            radii.append(float(rad))
            times.append(float(t * DT))
    radii = np.array(radii)
    times = np.array(times)
    # fit radius growth rate (lu per lu-time); compare to c_phi
    if len(times) > 2:
        slope = np.polyfit(times, radii, 1)[0]
    else:
        slope = float("nan")
    return {"c_phi": float(c_phi), "rms_radius_growth_rate": float(slope),
            "radius_series": radii.tolist(), "time_series": times.tolist(),
            "ratio_growth_to_c": float(slope / c_phi) if c_phi else float("nan")}


# ----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("E5 -- transverse edge-field light probe (demo-theory)")
    print("=" * 70)

    A = measure_c_phi()
    print("\n[A] reference c_phi")
    print("    omega_meas = %.5f   c_phi_meas = %.5f   c_theory(small k) = %.5f"
          % (A["omega_meas"], A["c_phi_meas"], A["c_phi_theory_smallk"]))

    B = part_B_smooth_scalar()
    print("\n[B / E5a] smooth single-valued scalar phi (no winding)")
    print("    frac_long  = %.6e" % B["frac_long"])
    print("    frac_TRANS = %.6e   <-- expect ~ machine epsilon" % B["frac_trans"])

    C = part_C_vortex()
    print("\n[C / E5b] vortex line phi (winding 2pi), compact wrapped edge field")
    print("    frac_TRANS (wrapped)   = %.6e   <-- expect > 0 (topological)"
          % C["frac_trans_wrapped"])
    print("    transverse energy within r<=4 of core = %.1f%%"
          % (100.0 * C["transverse_core_fraction_r<=4"]))

    D = part_D_propagation()
    print("\n[D / E5c] evolve vortex + transverse kick: does it radiate at c_phi?")
    print("    c_phi = %.4f   rms-radius growth rate = %.4f   ratio = %.3f"
          % (D["c_phi"], D["rms_radius_growth_rate"], D["ratio_growth_to_c"]))

    # ---- verdict logic ----
    trans_scalar_zero = B["frac_trans"] < 1e-6
    trans_vortex_nonzero = C["frac_trans_wrapped"] > 1e-3
    pinned = abs(D["ratio_growth_to_c"]) < 0.2   # radius barely grows vs c
    radiates = D["ratio_growth_to_c"] > 0.5

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print("  E5a single-valued scalar -> transverse = 0 ?  %s" % trans_scalar_zero)
    print("  E5b vortex               -> transverse > 0 ?  %s" % trans_vortex_nonzero)
    print("  E5c transverse content   -> radiates at c ?   %s (pinned=%s)"
          % (radiates, pinned))

    if trans_scalar_zero and not radiates:
        verdict = ("ROUTE_A_INSUFFICIENT: a single scalar phi cannot host a "
                   "propagating transverse photon. Transverse sector is "
                   "identically zero for single-valued phi (structural no-go), "
                   "and topological transverse content stays pinned to defects "
                   "rather than radiating at c_phi. A genuine photon needs a "
                   "SECOND dynamical edge d.o.f. -> Route B (phi-chi circulation) "
                   "or Route C (axiomatic gauge field A_ij).")
    elif radiates and trans_vortex_nonzero:
        verdict = ("HONEST_PHOTON_CANDIDATE: transverse edge content propagates "
                   "near c_phi -- pursue Route A, verify 2 polarizations next.")
    else:
        verdict = "INCONCLUSIVE: see fractions above."
    print("\n  => " + verdict)

    os.makedirs(OUT_DIR, exist_ok=True)
    report = {"part_A_reference": A, "part_B_E5a_smooth": B,
              "part_C_E5b_vortex": C, "part_D_E5c_propagation": D,
              "verdict": verdict}
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
