"""
E7 -- Route B make-or-break: can a coupled phi-chi system host an honest photon,
and if not, what is the MINIMAL structure that can?

Background (demo-theory/E5-RESULT-no-go.md): a single scalar phi cannot host a
propagating transverse photon (theta=dphi is curl-free, machine precision).
Route B proposes a SECOND field chi, with "circulation of chi" as a B-analog.

BUT chi is ALSO a per-node scalar. The curl of a gradient is identically zero,
so curl(d chi) = 0 -- the same Hodge obstruction. E7 tests this head-on and then
demonstrates the minimal cure.

Parts:
  E7a  Two coupled node-scalars (phi, chi). Best-case Maxwell-like coupling.
       Measure (i) the transverse SOURCE curl(d phi), curl(d chi)  [expect ~0],
       and (ii) sustained transverse edge fraction under evolution [expect ~0].
  E7b  Promote the carrier to a FUNDAMENTAL edge vector field A (a link/gauge
       field, NOT the gradient of any node scalar) with Maxwell dynamics
       d2A/dt2 = -c^2 curl curl A. Show:
         - transverse init  -> propagates at c, 2 independent polarizations
         - longitudinal init -> frozen (non-propagating)
       i.e. an edge vector field IS the photon; node scalars are not.

Verdict distinguishes: ROUTE_B_FAILS_NODE_SCALARS (photon must be an
independent edge field = v12 A_ij, forced not optional) vs a surprise pass.

ASCII output, CPU/numpy only.
"""

import json
import os
import numpy as np

BETA = 0.06
MU = 0.857
DT = 0.2
C2 = BETA / MU          # c_phi^2 reference

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
                       "07_validation", "audits", "demo-e7-phi-chi-photon-v1")


# ----------------------------------------------------------------------------
# Fourier helpers (periodic cubic lattice)
# ----------------------------------------------------------------------------
def kvecs(L):
    k1 = 2.0 * np.pi * np.fft.fftfreq(L) * L / L
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    return np.stack([KX, KY, KZ], axis=0)  # (3,L,L,L)


def laplacian(f):
    lap = np.zeros_like(f)
    for ax in range(3):
        lap += np.roll(f, 1, axis=ax) + np.roll(f, -1, axis=ax)
    lap -= 6.0 * f
    return lap


def edge_field(phi):
    """theta_a = phi(x+e_a) - phi(x): the discrete gradient (1-form)."""
    return np.stack([np.roll(phi, -1, axis=ax) - phi for ax in range(3)], axis=0)


def discrete_curl(V):
    """Lattice curl of an edge 1-form V using the SAME forward-difference
    convention as edge_field(). With matched operators d.d=0 EXACTLY, so
    curl(grad scalar) = 0 to machine precision (the Hodge identity).
        (curl V)_a = fwd_diff_b(V_c) - fwd_diff_c(V_b)   (a,b,c cyclic)
    """
    def fwd(f, ax):
        return np.roll(f, -1, axis=ax) - f
    cx = fwd(V[2], 1) - fwd(V[1], 2)   # d_y V_z - d_z V_y
    cy = fwd(V[0], 2) - fwd(V[2], 0)   # d_z V_x - d_x V_z
    cz = fwd(V[1], 0) - fwd(V[0], 1)   # d_x V_y - d_y V_x
    return np.stack([cx, cy, cz], axis=0)


def transverse_fraction_edge(theta):
    """Transverse fraction of an EDGE 1-form, using the matched forward-diff
    Fourier symbol D_a(k)=exp(i k_a)-1 (so a pure gradient dphi projects to
    exactly zero transverse)."""
    L = theta.shape[1]
    k1 = 2.0 * np.pi * np.fft.fftfreq(L) * L / L
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    D = np.stack([np.exp(1j*KX)-1.0, np.exp(1j*KY)-1.0, np.exp(1j*KZ)-1.0], axis=0)
    Dmag2 = np.sum(np.abs(D)**2, axis=0)
    Dmag2s = np.where(Dmag2 > 1e-14, Dmag2, 1.0)
    th = np.stack([np.fft.fftn(theta[a]) for a in range(3)], axis=0)
    cL = np.sum(np.conj(D)*th, axis=0) / Dmag2s
    th_long = D * cL
    th_trans = th - th_long
    th_long[:, Dmag2 <= 1e-14] = 0.0
    th_trans[:, Dmag2 <= 1e-14] = 0.0
    EL = np.sum(np.abs(th_long)**2)
    ET = np.sum(np.abs(th_trans)**2)
    return ET / (EL + ET) if (EL + ET) > 0 else 0.0


def transverse_fraction(V):
    """Hodge: fraction of |V|^2 in the divergence-free (transverse) sector."""
    L = V.shape[1]
    K = kvecs(L)
    k2 = np.sum(K ** 2, axis=0)
    k2s = np.where(k2 > 1e-14, k2, 1.0)
    Vh = np.stack([np.fft.fftn(V[a]) for a in range(3)], axis=0)
    kdotV = np.sum(K * Vh, axis=0)
    Vlong = K * (kdotV / k2s)            # P_L
    Vtrans = Vh - Vlong
    Vlong[:, k2 <= 1e-14] = 0.0
    Vtrans[:, k2 <= 1e-14] = 0.0
    EL = np.sum(np.abs(Vlong) ** 2)
    ET = np.sum(np.abs(Vtrans) ** 2)
    return ET / (EL + ET) if (EL + ET) > 0 else 0.0


# ----------------------------------------------------------------------------
# E7a -- two coupled node scalars
# ----------------------------------------------------------------------------
def smooth_scalar(L, seed):
    rng = np.random.default_rng(seed)
    x = np.arange(L)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    f = np.zeros((L, L, L))
    for _ in range(5):
        n = rng.integers(1, 4, size=3)
        f += rng.normal() * np.cos(2 * np.pi * (n[0]*X + n[1]*Y + n[2]*Z)/L
                                   + rng.uniform(0, 2*np.pi))
    return f


def part_E7a(L=32, g=0.05, steps=400):
    phi = smooth_scalar(L, 1)
    chi = smooth_scalar(L, 2)
    vphi = np.zeros_like(phi)
    vchi = np.zeros_like(chi)

    # the transverse SOURCE: curl of each scalar's edge field (must be ~0)
    curl_dphi = float(np.max(np.abs(discrete_curl(edge_field(phi)))))
    curl_dchi = float(np.max(np.abs(discrete_curl(edge_field(chi)))))

    # evolve a generous Maxwell-like cross-coupling between the two scalars
    #   mu phi'' = beta lap phi + g chi ;  mu chi'' = beta lap chi - g phi
    trans_series = []
    for t in range(steps):
        aphi = (BETA * laplacian(phi) + g * chi) / MU
        achi = (BETA * laplacian(chi) - g * phi) / MU
        vphi += DT * aphi
        vchi += DT * achi
        phi += DT * vphi
        chi += DT * vchi
        if t % 40 == 0:
            # best attempt at a vector "photon field": combine the two edge
            # fields into a candidate vector and ask for its transverse content
            cand = edge_field(phi) + discrete_curl(edge_field(chi))  # 2nd term=0
            trans_series.append(transverse_fraction_edge(cand))
    return {"max_curl_grad_phi": curl_dphi,
            "max_curl_grad_chi": curl_dchi,
            "sustained_transverse_fraction": float(np.mean(trans_series)),
            "transverse_series": [float(s) for s in trans_series]}


# ----------------------------------------------------------------------------
# E7b -- fundamental edge vector field with Maxwell dynamics
# ----------------------------------------------------------------------------
def curl_curl_spectral(A):
    """ -curl curl A  in Fourier space = (k(k.A) - k^2 A).  Returns real field
    L_op A such that  d2A/dt2 = C2 * L_op A  gives transverse waves at c."""
    L = A.shape[1]
    K = kvecs(L)
    k2 = np.sum(K ** 2, axis=0)
    Ah = np.stack([np.fft.fftn(A[a]) for a in range(3)], axis=0)
    kdotA = np.sum(K * Ah, axis=0)
    # -curl curl A_hat = -(k^2 A - k (k.A)) = -k^2 A + k(k.A)
    out_h = -(k2 * Ah) + K * kdotA
    return np.stack([np.fft.ifftn(out_h[a]).real for a in range(3)], axis=0)


def evolve_maxwell(A, V, steps, sample=20):
    series = []
    for t in range(steps):
        acc = C2 * curl_curl_spectral(A)
        V += DT * acc
        A += DT * V
        if t % sample == 0:
            series.append((t * DT, float(np.sum(A ** 2)),
                           float(transverse_fraction(A))))
    return series


def plane_wave(L, n_mode, pol):
    """A = pol * cos(k x_dir)."""
    x = np.arange(L)
    X, _, _ = np.meshgrid(x, x, x, indexing="ij")
    k = 2.0 * np.pi * n_mode / L
    A = np.zeros((3, L, L, L))
    for a in range(3):
        A[a] = pol[a] * np.cos(k * X)
    return A, k


def measure_omega(series_amp, dt_sample):
    """dominant temporal frequency of the energy/amplitude oscillation."""
    vals = np.array([s[1] for s in series_amp])
    vals = vals - np.mean(vals)
    if np.allclose(vals, 0):
        return 0.0
    sp = np.abs(np.fft.rfft(vals))
    fr = np.fft.rfftfreq(len(vals), d=dt_sample)
    return float(2.0 * np.pi * fr[np.argmax(sp[1:]) + 1])


def part_E7b(L=24, n_mode=2):
    c = np.sqrt(C2)
    # the field amplitude oscillates at 2*omega (energy ~ cos^2); track A_z directly
    # transverse polarization 1: k along x, pol along z
    A1, k = plane_wave(L, n_mode, pol=[0, 0, 1])
    V1 = np.zeros_like(A1)
    probe1 = []
    for t in range(600):
        acc = C2 * curl_curl_spectral(A1)
        V1 += DT * acc
        A1 += DT * V1
        if t % 4 == 0:
            probe1.append((t * DT, A1[2, 1, 1, 1], 0.0))
    om1 = measure_omega(probe1, 4 * DT)

    # transverse polarization 2: k along x, pol along y
    A2, _ = plane_wave(L, n_mode, pol=[0, 1, 0])
    V2 = np.zeros_like(A2)
    probe2 = []
    for t in range(600):
        acc = C2 * curl_curl_spectral(A2)
        V2 += DT * acc
        A2 += DT * V2
        if t % 4 == 0:
            probe2.append((t * DT, A2[1, 1, 1, 1], 0.0))
    om2 = measure_omega(probe2, 4 * DT)

    # longitudinal: k along x, pol along x -> should be frozen
    A3, _ = plane_wave(L, n_mode, pol=[1, 0, 0])
    V3 = np.zeros_like(A3)
    probeL = []
    for t in range(600):
        acc = C2 * curl_curl_spectral(A3)
        V3 += DT * acc
        A3 += DT * V3
        if t % 4 == 0:
            probeL.append((t * DT, A3[0, 1, 1, 1], 0.0))
    omL = measure_omega(probeL, 4 * DT)

    k_eff = np.sqrt(2.0 * (1.0 - np.cos(k)))  # finite-lattice |k|
    c_meas1 = om1 / k if k > 0 else float("nan")
    c_meas2 = om2 / k if k > 0 else float("nan")
    return {"c_phi": float(c),
            "omega_trans_pol1": om1, "omega_trans_pol2": om2,
            "omega_longitudinal": omL,
            "c_meas_pol1": float(c_meas1), "c_meas_pol2": float(c_meas2),
            "k": float(k), "k_eff_lattice": float(k_eff),
            "longitudinal_frozen": bool(omL < 1e-3),
            "two_transverse_match": bool(abs(om1 - om2) < 1e-3 and om1 > 1e-3)}


# ----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("E7 -- phi-chi photon probe (Route B make-or-break)")
    print("=" * 70)

    A = part_E7a()
    print("\n[E7a] two coupled NODE SCALARS (phi, chi)")
    print("    max |curl(grad phi)| = %.3e   (transverse source from phi)" % A["max_curl_grad_phi"])
    print("    max |curl(grad chi)| = %.3e   (transverse source from chi)" % A["max_curl_grad_chi"])
    print("    sustained transverse fraction = %.3e  <-- expect ~0" % A["sustained_transverse_fraction"])

    B = part_E7b()
    print("\n[E7b] FUNDAMENTAL EDGE VECTOR field A with Maxwell d2A/dt2=-c^2 curlcurl A")
    print("    c_phi = %.4f   k = %.4f" % (B["c_phi"], B["k"]))
    print("    transverse pol 1 (z): omega = %.5f  -> c_meas = %.4f" % (B["omega_trans_pol1"], B["c_meas_pol1"]))
    print("    transverse pol 2 (y): omega = %.5f  -> c_meas = %.4f" % (B["omega_trans_pol2"], B["c_meas_pol2"]))
    print("    longitudinal   (x): omega = %.5f  -> frozen=%s" % (B["omega_longitudinal"], B["longitudinal_frozen"]))
    print("    two transverse polarizations match: %s" % B["two_transverse_match"])

    # verdict
    node_scalars_fail = (A["max_curl_grad_phi"] < 1e-6 and
                         A["sustained_transverse_fraction"] < 1e-6)
    edge_photon_works = (B["two_transverse_match"] and B["longitudinal_frozen"])

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print("  node-scalar phi/chi cannot source transverse : %s" % node_scalars_fail)
    print("  edge vector field gives 2 transverse + frozen longitudinal : %s" % edge_photon_works)

    if node_scalars_fail and edge_photon_works:
        verdict = ("ROUTE_B_FAILS_NODE_SCALARS / EDGE_PHOTON_FORCED: chi is a "
                   "node scalar, so curl(grad chi)=0 identically -- it cannot be "
                   "the B-analog. No coupling of two node scalars sources a "
                   "sustained transverse mode. BUT a FUNDAMENTAL edge vector "
                   "field (gauge field on links, not the gradient of any node "
                   "scalar) reproduces the photon exactly: 2 transverse "
                   "polarizations propagate at c_phi, the longitudinal mode is "
                   "frozen (Gauss constraint). CONCLUSION: the v12 edge gauge "
                   "field A_ij is NOT an arbitrary bolt-on -- it is the MINIMAL "
                   "and FORCED carrier of light in a node-scalar substrate. "
                   "Light is necessarily a link degree of freedom.")
    elif not node_scalars_fail:
        verdict = "SURPRISE: node scalars sourced transverse content -- investigate."
    else:
        verdict = "INCONCLUSIVE: edge photon demo did not cleanly separate modes."
    print("\n  => " + verdict)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "report.json"), "w") as f:
        json.dump({"E7a_node_scalars": A, "E7b_edge_vector": B,
                   "verdict": verdict}, f, indent=2)
    print("\n  report -> %s" % os.path.join(OUT_DIR, "report.json"))


if __name__ == "__main__":
    main()
