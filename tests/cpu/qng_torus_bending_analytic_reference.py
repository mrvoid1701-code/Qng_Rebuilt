"""
QNG-CPU-078 reference: Diagnostic test of DER-QNG-045 bending formula.

Evaluates the scalar-Poisson double-integral prediction for alpha(b)
of a phi-wave pulse passing a vortex ring at impact parameter b.

    alpha_scalar(b) = (k_gm * D) / (8 pi^2 c_phi^2)
                      * integ_{u_min}^{u_max} du integ_0^{2*pi} dtheta
                        (b - R sin theta)
                        / [u^2 + R^2 + (b^2 - 2 R b sin theta)
                           - 2 R u cos theta]^{3/2}

Compares to measured alpha(b) from DER-QNG-044 Test 3f on b in {3,4,6,8},
L=28, R=4, path length 20 lu.

Purpose (diagnostic, not PASS/FAIL gate):
  D1 - does the scalar-Poisson prediction reproduce the measured alpha(b)
       in magnitude, sign, and b-dependence?
  D2 - does the far-field limit (b >> R) cleanly approach Einstein 1911
       ( b * alpha_far = const )?
  D3 - does form factor F(b/R) = alpha_full/alpha_far remain order unity
       outside the ring (b >= R)?

Physical outcome to document: if D1 fails by orders of magnitude while
the v8 bending measurement is real, the coupling mediating bending is
NOT the scalar sigma_g Poisson channel alone (consistent with 120%
anisotropy P/T=4.00 vs scalar 1.31 from Test 3e).

A companion update to DER-QNG-045 will then introduce the m^2(x) direct
coupling through V_couple = (g/2)(sigma_m,ref-sigma_m)^2 (1 - cos phi),
which sources bending quadratically in the sigma_m deficit.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------------
# Configuration - matches DER-QNG-044 Test 3f (bending probe) and CPU-074
# canonical ring at R=4, L=28.
# ---------------------------------------------------------------------------

# Substrate parameters
K_GM = 0.10               # Channel G coupling (v8 canonical)
C_PHI2 = 0.01167          # = BETA_PHI / (6 * MU_PHI) = 0.07 / (6 * 1.0) for default
RING_R = 4.0              # vortex ring radius (lattice units)
RING_M = 176.85           # M_ring from cached L=28 R=4 ring (from bending probe log)

# Pulse path: x in [4, 24], y = 14 + b, z = 14 (ring centered at (14,14,14))
X_SOURCE = 4.0
X_DETECT = 24.0
Y_C = 14.0
X_C = 14.0

# Measured alpha from DER-QNG-044 Test 3f (bending probe GPU results, 2026-04-20)
ALPHA_MEASURED = {
    3: -3.3658e-03,
    4: -1.1728e-02,
    6: -3.7010e-02,
    8: -4.2179e-02,
}

# ---------------------------------------------------------------------------
# Core integral
# ---------------------------------------------------------------------------

def integrand(u: np.ndarray, theta: np.ndarray, b: float, R: float) -> np.ndarray:
    """Kernel of the double integral: (b - R sin theta) / rho^3."""
    # rho^2 = u^2 + R^2 + (b^2 - 2 R b sin theta) - 2 R u cos theta
    # Equivalent to |r_pulse(u) - r_ring(theta)|^2 in the ring plane.
    U, T = np.meshgrid(u, theta, indexing="ij")
    rho2 = (U * U + R * R
            + (b * b - 2.0 * R * b * np.sin(T))
            - 2.0 * R * U * np.cos(T))
    rho2 = np.maximum(rho2, 1e-9)  # guard against coincident pulse/rim
    return (b - R * np.sin(T)) / rho2 ** 1.5


def alpha_full(b: float, R: float, k_gm: float, D: float, c_phi2: float,
               u_min: float = None, u_max: float = None,
               n_u: int = 2001, n_theta: int = 2001) -> float:
    """Full double-integral bending angle."""
    if u_min is None:
        u_min = X_SOURCE - X_C      # = -10
    if u_max is None:
        u_max = X_DETECT - X_C      # = +10
    u = np.linspace(u_min, u_max, n_u)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    K = integrand(u, theta, b, R)
    # Double trapezoidal integral over u, theta
    integ_theta = np.trapz(K, theta, axis=1)
    integral = np.trapz(integ_theta, u)
    prefactor = (k_gm * D) / (8.0 * np.pi * np.pi * c_phi2)
    # Sign: attractive coupling -> pulse bent toward ring
    # -> alpha negative for positive b (consistent with measured sign)
    return -prefactor * integral


def alpha_far(b: float, k_gm: float, D: float, c_phi2: float,
              u_min: float = None, u_max: float = None) -> float:
    """Far-field monopole limit: theta-integral reduces to 2*pi*b/(u^2+b^2)^{3/2}."""
    if u_min is None:
        u_min = X_SOURCE - X_C
    if u_max is None:
        u_max = X_DETECT - X_C
    # integ du * 2*pi*b / (u^2 + b^2)^{3/2}
    #  = 2*pi*b * [u/(b^2 sqrt(u^2+b^2))] from u_min to u_max
    def F(u):
        return u / (b * b * np.sqrt(u * u + b * b))
    u_integ = 2.0 * np.pi * b * (F(u_max) - F(u_min))
    prefactor = (k_gm * D) / (8.0 * np.pi * np.pi * c_phi2)
    return -prefactor * u_integ

# ---------------------------------------------------------------------------
# Driver + checks
# ---------------------------------------------------------------------------

@dataclass
class Result:
    b: float
    alpha_full: float
    alpha_far: float
    alpha_meas: float
    F: float            # form factor alpha_full / alpha_far
    ratio_meas_pred: float
    sign_match: bool

def _load_cached_ring_np(L=28, R=4):
    """Load cached L=28 R=4 ring state as numpy arrays (no cupy needed)."""
    cache_root = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-v8-stability-probe-v1", "ring_cache"
    )
    cache_root = os.path.abspath(cache_root)
    if not os.path.isdir(cache_root):
        return None
    for fn in os.listdir(cache_root):
        if fn.startswith(f"ring_L{L}_R{R}_") and fn.endswith(".npz"):
            data = np.load(os.path.join(cache_root, fn))
            return {k: np.asarray(data[k]) for k in data.files}
    return None


def alpha_from_sigma_g_grid(sg: np.ndarray, b: float, c_phi2: float,
                             L: int = 28, x_c: int = 14, y_c: int = 14,
                             z_c: int = 14, x_src: int = 4, x_det: int = 24) -> float:
    """Integrate -(1/c_phi^2) * d/dy sigma_g along pulse path at impact b."""
    # Pulse at y_c + b, z_c, x in [x_src, x_det]
    yp = y_c + int(b)
    if yp < 1 or yp >= L - 1:
        return float("nan")
    # central difference along y
    dsg_dy = 0.5 * (sg[x_src:x_det + 1, yp + 1, z_c]
                    - sg[x_src:x_det + 1, yp - 1, z_c])
    # Numerical trap-integrate along x (integer x spacing)
    integ = np.trapz(dsg_dy)
    return -(1.0 / c_phi2) * integ


def alpha_from_mass_sq_grid(sm: np.ndarray, b: float, g_couple: float,
                             sigma_m_ref: float, omega_sq: float,
                             L: int = 28, x_c: int = 14, y_c: int = 14,
                             z_c: int = 14, x_src: int = 4, x_det: int = 24) -> float:
    """Integrate -(1/2 omega^2) * d/dy m^2(x) along pulse path.

    m^2(x) = g * (sigma_m_ref - sigma_m(x))^2 (from V_couple = (g/2) deficit^2 (1-cos phi))
    Small-phi limit: V'' / phi = g * deficit^2 sets effective mass-squared.
    """
    yp = y_c + int(b)
    if yp < 1 or yp >= L - 1:
        return float("nan")
    deficit = sigma_m_ref - sm
    m2 = g_couple * deficit * deficit
    dm2_dy = 0.5 * (m2[x_src:x_det + 1, yp + 1, z_c]
                    - m2[x_src:x_det + 1, yp - 1, z_c])
    integ = np.trapz(dm2_dy)
    return -(1.0 / (2.0 * omega_sq)) * integ


def main() -> int:
    out_dir = os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-torus-bending-analytic-v1"
    )
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 78)
    print("CPU-078 - Analytic verification of DER-QNG-045 bending angle alpha(b)")
    print("=" * 78)
    print(f"  k_gm = {K_GM}")
    print(f"  c_phi^2 = {C_PHI2}")
    print(f"  R_ring = {RING_R}")
    print(f"  D (M_ring, L=28 R=4) = {RING_M}")
    print(f"  path u in [{X_SOURCE - X_C:.1f}, {X_DETECT - X_C:.1f}]")
    print()

    results: list[Result] = []
    print(f"{'b':>3} {'alpha_full':>14} {'alpha_far':>14} "
          f"{'alpha_meas':>14} {'F':>9} {'meas/pred':>12} {'sign':>5}")
    print("-" * 78)
    for b_val, a_meas in ALPHA_MEASURED.items():
        a_full = alpha_full(b_val, RING_R, K_GM, RING_M, C_PHI2)
        a_farr = alpha_far(b_val, K_GM, RING_M, C_PHI2)
        F = a_full / a_farr if abs(a_farr) > 1e-30 else float("nan")
        ratio = a_meas / a_full if abs(a_full) > 1e-30 else float("nan")
        sign_ok = (np.sign(a_full) == np.sign(a_meas))
        results.append(Result(b=b_val, alpha_full=a_full, alpha_far=a_farr,
                              alpha_meas=a_meas, F=F, ratio_meas_pred=ratio,
                              sign_match=bool(sign_ok)))
        print(f"{b_val:>3} {a_full:>+14.5e} {a_farr:>+14.5e} "
              f"{a_meas:>+14.5e} {F:>9.4f} {ratio:>+12.4f} {str(sign_ok):>5}")

    # ------------------------------------------------------------------
    # Direct test against cached ring (if present): measure sigma_g and
    # sigma_m on lattice, compute alpha from scalar Poisson and from
    # m^2(x) V_couple channel, compare to measurement.
    # ------------------------------------------------------------------
    ring = _load_cached_ring_np(L=28, R=4)
    sg_alpha = {}
    m2_alpha = {}
    if ring is not None:
        L_ring = 28
        sg = np.asarray(ring["sg"]).reshape(L_ring, L_ring, L_ring)
        sm = np.asarray(ring["sm"]).reshape(L_ring, L_ring, L_ring)
        print()
        print("Lattice-direct alpha from cached ring (L=28 R=4):")
        print(f"  <sigma_g> = {float(sg.mean()):.4f}  min = {float(sg.min()):.4f}")
        print(f"  <sigma_m> = {float(sm.mean()):.4f}  min = {float(sm.min()):.4f}")
        # Pulse dominant frequency (k_pkt=0.785): omega = k * c_phi
        k_pkt = 0.78540
        c_phi = np.sqrt(C_PHI2)
        omega_sq = (k_pkt * c_phi) ** 2
        g_couple = 0.22
        SIGMA_M_REF = 1.0
        print(f"{'b':>3} {'alpha_sg(direct)':>18} {'alpha_m2(V_couple)':>20} "
              f"{'alpha_meas':>14}")
        print("-" * 64)
        for b_val, a_meas in ALPHA_MEASURED.items():
            a_sg = alpha_from_sigma_g_grid(sg, float(b_val), C_PHI2)
            a_m2 = alpha_from_mass_sq_grid(sm, float(b_val), g_couple,
                                            SIGMA_M_REF, omega_sq)
            sg_alpha[b_val] = a_sg
            m2_alpha[b_val] = a_m2
            print(f"{b_val:>3} {a_sg:>+18.5e} {a_m2:>+20.5e} {a_meas:>+14.5e}")
    else:
        print()
        print("NOTE: cached L=28 R=4 ring not found; skipping lattice-direct check.")

    # Far-field check (C4): evaluate at b=20, 40 and confirm 1/b scaling
    print()
    print("Far-field 1/b check (C4):")
    print(f"{'b':>3} {'alpha_far':>14} {'b * alpha_far':>18}")
    print("-" * 42)
    products = []
    for b_val in [10, 20, 40, 80]:
        a_farr = alpha_far(float(b_val), K_GM, RING_M, C_PHI2)
        prod = b_val * a_farr
        products.append(prod)
        print(f"{b_val:>3} {a_farr:>+14.5e} {prod:>+18.5e}")

    # Should be approximately constant (up to finite-path correction)
    prods_arr = np.array(products)
    c4_consistent = np.std(prods_arr) / abs(np.mean(prods_arr)) < 0.20

    # Gates
    ratios = np.array([abs(r.ratio_meas_pred) for r in results])
    signs = [r.sign_match for r in results]
    F_vals = np.array([r.F for r in results])

    c1_pass = np.all((ratios > 0.33) & (ratios < 3.0))
    c2_pass = all(signs)
    c3_pass = np.all((F_vals > 0.001) & (F_vals < 0.5))
    c4_pass = bool(c4_consistent)

    print()
    print("=" * 78)
    print("GATE CHECK")
    print("=" * 78)
    print(f"  C1 (ratio in [1/3, 3] at all b): {'PASS' if c1_pass else 'FAIL'}")
    print(f"       ratios = {ratios.tolist()}")
    print(f"  C2 (sign correct at all b):      {'PASS' if c2_pass else 'FAIL'}")
    print(f"  C3 (F in [0.001, 0.5]):          {'PASS' if c3_pass else 'FAIL'}")
    print(f"       F values = {F_vals.tolist()}")
    print(f"  C4 (far-field 1/b saturation):   {'PASS' if c4_pass else 'FAIL'}")
    print(f"       b*alpha_far std/|mean| = {np.std(prods_arr)/abs(np.mean(prods_arr)):.4f}")
    print()
    all_pass = c1_pass and c2_pass and c3_pass and c4_pass
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")

    # Emit machine-readable report
    report = {
        "test_id": "QNG-CPU-078",
        "derivation": "DER-QNG-045",
        "params": {
            "k_gm": K_GM, "c_phi2": C_PHI2, "R_ring": RING_R, "D_ring": RING_M,
            "u_min": X_SOURCE - X_C, "u_max": X_DETECT - X_C,
        },
        "results": [r.__dict__ for r in results],
        "far_field_products_b_alpha": {"b": [10, 20, 40, 80],
                                       "b_times_alpha_far": prods_arr.tolist(),
                                       "std_over_mean":
                                            float(np.std(prods_arr)/abs(np.mean(prods_arr)))},
        "lattice_direct": {
            "sigma_g_bending": {str(k): float(v) for k, v in sg_alpha.items()},
            "m2_V_couple_bending": {str(k): float(v) for k, v in m2_alpha.items()},
        },
        "gates": {"C1": bool(c1_pass), "C2": bool(c2_pass),
                  "C3": bool(c3_pass), "C4": bool(c4_pass)},
        "verdict": "PASS" if all_pass else "FAIL",
    }
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {os.path.join(out_dir, 'report.json')}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
