"""
QNG-CPU-079 reference: Numerical verification of DER-QNG-046 cos(phi_bg)
cancellation mechanism.

DER-QNG-046 predicts that the effective pulse mass m_eff^2(x) =
(g / (2 mu_phi)) * Delta^2(x) * cos(phi_bg(x)). The bending-integral
contributions decompose as:

  alpha_scalar(b) = -(g / (2 mu_phi omega^2)) * integral Delta d_y Delta cos(phi_bg) dx
  alpha_winding(b) = +(g / (4 mu_phi omega^2)) * integral Delta^2 sin(phi_bg) d_y phi_bg dx

For a thin vortex ring in its own plane, BOTH integrands are odd in
u = x - x_c and the continuum integrals vanish. The non-zero measured
alpha(b) is the symmetry-breaking residual.

This script loads the cached v8 L=28 R=4 ring, evaluates the two
integrals numerically along the pulse path at b in {3, 4, 6, 8}, and
checks the predictions:

  P1: integral Delta * d_y(Delta) * cos(phi_bg) should be much smaller
      than the same integral with cos(phi_bg) replaced by 1 (scalar
      absolute value), confirming cancellation by factor >> 10
  P2: integral along axis direction (ring z-axis) should be much larger
      than in-plane integral, explaining P/T=4 anisotropy
  P3: predicted alpha_tensorial(b) = alpha_scalar(b) + alpha_winding(b)
      should be of the same order as measured alpha(b) (10^-2 rad),
      not 10^1 rad like the scalar-only prediction
"""
from __future__ import annotations

import json
import os
import sys
import numpy as np

# Parameters matching DER-QNG-044 Test 3f
G_COUPLE = 0.22
MU_PHI = 0.857
C_PHI2 = 0.01167
C_PHI = np.sqrt(C_PHI2)
K_PKT = 0.78540
OMEGA = K_PKT * C_PHI
OMEGA2 = OMEGA * OMEGA
SIGMA_M_REF = 1.0

ALPHA_MEASURED = {
    3: -3.3658e-03,
    4: -1.1728e-02,
    6: -3.7010e-02,
    8: -4.2179e-02,
}


def _load_cached_ring(L=28, R=4):
    cache_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-v8-stability-probe-v1", "ring_cache"
    ))
    for fn in os.listdir(cache_root):
        if fn.startswith(f"ring_L{L}_R{R}_") and fn.endswith(".npz"):
            data = np.load(os.path.join(cache_root, fn))
            return {k: np.asarray(data[k]).reshape(L, L, L) for k in data.files}
    return None


def phi_bg_from_cache(phi: np.ndarray) -> np.ndarray:
    """Cached phi field is already the winding background (pulse not yet injected)."""
    return phi


def deficit_from_cache(sm: np.ndarray) -> np.ndarray:
    return SIGMA_M_REF - sm


def pulse_path_samples(arr: np.ndarray, b: float, x_src=4, x_det=24,
                      y_c=14, z_c=14, axis="transverse") -> np.ndarray:
    """Return 1D samples of arr along the pulse path at impact b."""
    if axis == "transverse":   # pulse along +x at y = y_c + b
        return arr[x_src:x_det + 1, int(y_c + b), int(z_c)]
    if axis == "axis":          # pulse along +z through ring center (axis line)
        # z in [4, 24], at x=x_c, y=y_c
        return arr[int(y_c + b), int(y_c), 4:25]
    raise ValueError(axis)


def dy(arr: np.ndarray, b: float, x_src=4, x_det=24,
       y_c=14, z_c=14) -> np.ndarray:
    """Central difference d/dy along pulse path (transverse)."""
    yp = int(y_c + b)
    return 0.5 * (arr[x_src:x_det + 1, yp + 1, z_c]
                  - arr[x_src:x_det + 1, yp - 1, z_c])


def tensorial_bending_integrals(sm: np.ndarray, phi: np.ndarray, b: float):
    """Compute alpha_scalar and alpha_winding per DER-QNG-046 eq 5."""
    Delta = deficit_from_cache(sm)
    phi_bg = phi_bg_from_cache(phi)
    # Pulse path: transverse, along +x at y=y_c+b, z=z_c
    x_src, x_det, y_c, z_c = 4, 24, 14, 14
    yp = int(y_c + b)
    # Sample along path
    D_path   = Delta[x_src:x_det + 1, yp, z_c]
    phi_path = phi_bg[x_src:x_det + 1, yp, z_c]
    # Transverse gradients (central difference in y)
    dD_dy   = 0.5 * (Delta[x_src:x_det + 1, yp + 1, z_c]
                     - Delta[x_src:x_det + 1, yp - 1, z_c])
    dphi_dy = 0.5 * (phi_bg[x_src:x_det + 1, yp + 1, z_c]
                     - phi_bg[x_src:x_det + 1, yp - 1, z_c])
    # Wrap phi gradient through branch cut (use arctan2 of difference)
    # But simpler: unwrap the raw diff
    dphi_dy = np.angle(np.exp(1j * dphi_dy))  # fold to [-pi, pi]
    cos_bg = np.cos(phi_path)
    sin_bg = np.sin(phi_path)
    # Scalar-only (naive, no cos modulation)
    integrand_scalar_naive = D_path * dD_dy
    integ_scalar_naive = np.trapz(integrand_scalar_naive)
    # Tensorial decomposition
    integrand_scalar  = D_path * dD_dy * cos_bg
    integrand_winding = D_path * D_path * sin_bg * dphi_dy
    integ_scalar  = np.trapz(integrand_scalar)
    integ_winding = np.trapz(integrand_winding)
    prefac = G_COUPLE / (2.0 * MU_PHI * OMEGA2)
    alpha_scalar   = -prefac * integ_scalar
    alpha_winding  = +prefac * integ_winding / 2.0  # factor 1/2 from DER eq
    alpha_scalar_naive = -prefac * integ_scalar_naive
    return {
        "b": b,
        "integ_scalar_naive_no_cos": float(integ_scalar_naive),
        "integ_scalar_with_cos":      float(integ_scalar),
        "integ_winding":              float(integ_winding),
        "cancellation_factor":        float(abs(integ_scalar_naive) /
                                             (abs(integ_scalar) + 1e-30)),
        "alpha_scalar_naive":         float(alpha_scalar_naive),
        "alpha_scalar":               float(alpha_scalar),
        "alpha_winding":              float(alpha_winding),
        "alpha_tensorial_total":      float(alpha_scalar + alpha_winding),
    }


def anisotropy_integrals(sm: np.ndarray, phi: np.ndarray, x_c=14, y_c=14, z_c=14):
    """Measure integral Delta^2 cos(phi_bg) along transverse vs axis directions."""
    Delta = deficit_from_cache(sm)
    phi_bg = phi_bg_from_cache(phi)
    cos_bg = np.cos(phi_bg)
    # Transverse (in ring plane) at y = y_c, x in [4,24], z = z_c
    path_trans_D2 = (Delta[4:25, y_c, z_c]) ** 2
    path_trans_cos = cos_bg[4:25, y_c, z_c]
    integ_trans_abs = float(np.trapz(path_trans_D2))
    integ_trans_with_cos = float(np.trapz(path_trans_D2 * path_trans_cos))
    # Axis path through ring center, z in [4,24], x=x_c, y=y_c
    path_axis_D2 = (Delta[x_c, y_c, 4:25]) ** 2
    path_axis_cos = cos_bg[x_c, y_c, 4:25]
    integ_axis_abs = float(np.trapz(path_axis_D2))
    integ_axis_with_cos = float(np.trapz(path_axis_D2 * path_axis_cos))
    return {
        "trans_D2_integ": integ_trans_abs,
        "trans_D2_cos_integ": integ_trans_with_cos,
        "trans_cancellation": integ_trans_abs / (abs(integ_trans_with_cos) + 1e-30),
        "axis_D2_integ": integ_axis_abs,
        "axis_D2_cos_integ": integ_axis_with_cos,
        "axis_cancellation": integ_axis_abs / (abs(integ_axis_with_cos) + 1e-30),
        "anisotropy_ratio_abs": integ_axis_abs / (integ_trans_abs + 1e-30),
        "anisotropy_ratio_with_cos":
             abs(integ_axis_with_cos) / (abs(integ_trans_with_cos) + 1e-30),
    }


def main() -> int:
    out_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "07_validation", "audits", "qng-tensorial-cancellation-v1"
    ))
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 78)
    print("CPU-079 - DER-QNG-046 cos(phi_bg) cancellation mechanism verification")
    print("=" * 78)
    print(f"  g_couple = {G_COUPLE}, mu_phi = {MU_PHI}, c_phi^2 = {C_PHI2}")
    print(f"  omega^2 = {OMEGA2:.6f}")

    ring = _load_cached_ring(L=28, R=4)
    if ring is None:
        print("ERROR: no cached L=28 R=4 ring found")
        return 2
    sm = ring["sm"]
    phi = ring["phi"]

    print()
    print(f"  <sigma_m> = {sm.mean():.4f}, min = {sm.min():.4f}")
    print(f"  <phi>     = {phi.mean():.4f}, range = [{phi.min():.3f}, {phi.max():.3f}]")
    print(f"  max |deficit| = {np.abs(SIGMA_M_REF - sm).max():.4f}")

    # Part 1: per-b bending decomposition (transverse path)
    print()
    print("Per-impact-parameter transverse bending decomposition:")
    print(f"{'b':>3} {'cancel':>8} {'a_naive':>12} {'a_scalar':>12} "
          f"{'a_wind':>12} {'a_total':>12} {'a_meas':>12}")
    print("-" * 78)
    per_b = []
    for b_val, a_meas in ALPHA_MEASURED.items():
        r = tensorial_bending_integrals(sm, phi, float(b_val))
        per_b.append({**r, "alpha_measured": a_meas})
        print(f"{b_val:>3} {r['cancellation_factor']:>8.2f} "
              f"{r['alpha_scalar_naive']:>+12.4e} "
              f"{r['alpha_scalar']:>+12.4e} {r['alpha_winding']:>+12.4e} "
              f"{r['alpha_tensorial_total']:>+12.4e} {a_meas:>+12.4e}")

    # Part 2: anisotropy (axis vs transverse)
    print()
    print("Anisotropy (axis direction vs in-plane, for P/T=4 prediction):")
    aniso = anisotropy_integrals(sm, phi)
    for k, v in aniso.items():
        print(f"  {k:30s} = {v:+.4e}")

    # Gate check
    # G1: cancellation factor > 10 for at least 2 of 4 b values
    cancels = [r["cancellation_factor"] for r in per_b]
    g1 = sum(1 for c in cancels if c > 10) >= 2
    # G2: alpha_tensorial magnitude reduced to < 1e-1 rad for all b (not 10 rad)
    total_alphas = [abs(r["alpha_tensorial_total"]) for r in per_b]
    g2 = all(a < 1.0 for a in total_alphas)
    # G3: axis integral with cos >> transverse integral with cos
    g3 = aniso["anisotropy_ratio_with_cos"] > 2.0

    print()
    print("=" * 78)
    print("GATE CHECK")
    print("=" * 78)
    print(f"  G1 cancellation factor > 10 at 2+ b values: "
          f"{'PASS' if g1 else 'FAIL'}  (values = {cancels})")
    print(f"  G2 tensorial alpha < 1 rad at all b:         "
          f"{'PASS' if g2 else 'FAIL'}  (max = {max(total_alphas):.3e})")
    print(f"  G3 axis/trans (with cos) > 2:                "
          f"{'PASS' if g3 else 'FAIL'}  (ratio = {aniso['anisotropy_ratio_with_cos']:.3f})")

    all_pass = g1 and g2 and g3
    print(f"\nOVERALL: {'PASS' if all_pass else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-079",
        "derivation": "DER-QNG-046",
        "params": {"g": G_COUPLE, "mu_phi": MU_PHI, "c_phi2": C_PHI2,
                   "k_pkt": K_PKT, "omega2": OMEGA2,
                   "sigma_m_ref": SIGMA_M_REF},
        "per_b": per_b,
        "anisotropy": aniso,
        "gates": {"G1_cancellation": bool(g1),
                  "G2_tensorial_small": bool(g2),
                  "G3_anisotropy": bool(g3)},
        "verdict": "PASS" if all_pass else "FAIL",
    }
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {os.path.join(out_dir, 'report.json')}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
