"""Theoretical Shapiro delay + bending predictions from cached ring (CPU-only).

Runs WITHOUT the GPU -- uses the cached L=28, R=4 ring state in .npz form.

Predictions computed:
  (A) Shapiro delay dtt(b) for pulse at impact parameter b from ring axis,
      pulse direction +x.  Compared to:
        - measured far-field b=4: dtt=+26 lu
        - measured far-field b=8: dtt=+27 lu
  (B) Expected asymptotic behavior: constant (saturated), log(b),
      or 1/b -- fits the 1911 vs GR discriminator.
  (C) Bending angle alpha(b): predicted transverse deflection of a +x
      pulse at impact parameter b.  Two hypotheses:
        - H_1911  (scalar-c): alpha = (1/c_phi^2) integ d__y [m^2(x)/k^2] dx
        - H_GR    (metric):  alpha = 2 x H_1911 (factor 2 from spatial curvature)

Theory:
  KG wave dispersion in Option-E^2 coupling:
      omega^2(x) = c_phi^2 k^2 + m^2(x),    m^2(x) = (g/2) · deficit(x)^2 / mu_phi
  Group velocity: v_g = c_phi^2 k / omega
  Refractive index: n(x) = c_phi / v_g = omega / (c_phi k)
  Shapiro delay along path P:
      dtt = integ_P (1/v_g - 1/c_phi) ds
         ~ (1/(2 c_phi k^2)) integ_P m^2(x) ds   [to leading order]

Bending by transverse gradient (eikonal):
      dk_perp/ds = -d__⊥ omega = -d__⊥ m^2(x) / (2 omega)
  Integrated:
      dtk_y ~ -(1/(2 omega)) integ d__y m^2(x,y=b) dx
      alpha ~ dtk_y / k    (small angle)
  In the k -> inf eikonal limit omega -> c_phi k, so:
      alpha_1911 = -(1/(2 c_phi^2 k^2)) integ d__y m^2(x,y=b) dx

Expected sign: deficit concentrated near y=L/2, so d__y m^2 < 0 for y > L/2.
Pulse at y=L/2+b is attracted toward the deficit (−y direction) -- bent
toward the ring.  alpha > 0 means deflection toward ring (attractive).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1" / "ring_cache"

# v8 parameters (must match qng_v8_canonical_gpu.py)
SIGMA_M_REF = 1.0
BETA_PHI    = 0.06
MU_PHI      = 0.857
G_V_COUPLE  = 0.22
C_PHI_SQ    = BETA_PHI / (6.0 * MU_PHI)     # 0.01167
C_PHI       = float(np.sqrt(C_PHI_SQ))      # 0.10801
K_PKT       = np.pi / 4.0                    # same pulse wavenumber as probe


def load_ring(L=28, R=4, P1=300, P2=1000):
    files = list(CACHE.glob(f"ring_L{L}_R{R}_P1_{P1}_P2_{P2}_*.npz"))
    if not files:
        print(f"  No cache for L={L} R={R}; skip.")
        return None
    data = np.load(files[0])
    sm = data['sm']
    deficit = SIGMA_M_REF - sm
    d3 = deficit.reshape(L, L, L)   # NOTE: check axis order below
    return d3


def path_integral_deficit2(deficit3d, x_path, y_b, z_b, L):
    """Integrate m^2(x)=g/2 * deficit^2 along x-axis line at (x, y_b, z_b).

    Returns array m2(x) along path + its x-integral and y-derivative at b.
    """
    # Fractional y,z: linear interpolation along those axes
    yi0 = int(np.floor(y_b)) % L
    yi1 = (yi0 + 1) % L
    wy  = y_b - np.floor(y_b)
    zi0 = int(np.floor(z_b)) % L
    zi1 = (zi0 + 1) % L
    wz  = z_b - np.floor(z_b)

    # deficit3d indexed as [z, y, x]? need to verify -- QNG ravels as
    # idx = x + y*L + z*L*L, so deficit3d = deficit.reshape(L, L, L) gives
    # axis 0 = z (outer), axis 1 = y, axis 2 = x.
    def _at(z_i, y_i):
        return deficit3d[z_i, y_i, :]

    d_line = ((1 - wy) * (1 - wz) * _at(zi0, yi0)
              + wy * (1 - wz) * _at(zi0, yi1)
              + (1 - wy) * wz * _at(zi1, yi0)
              + wy * wz * _at(zi1, yi1))

    m2_x = 0.5 * G_V_COUPLE * d_line ** 2 / MU_PHI
    return m2_x, d_line


def shapiro_delay_prediction(deficit3d, L, y_b, z_b, x_range=None):
    """Predict dtt for pulse at (y_b, z_b) along x in x_range."""
    m2_x, d_line = path_integral_deficit2(deficit3d, None, y_b, z_b, L)
    if x_range is None:
        x_range = (4.0, L - 4.0)
    # Integrate along x in [x_source, x_detect]
    xi0 = int(np.ceil(x_range[0]))
    xi1 = int(np.floor(x_range[1]))
    m2_path = m2_x[xi0:xi1 + 1]
    # dtt ~ (1 / (2 c_phi k^2)) integ m^2(x) dx     (dx = 1 node spacing)
    dt_pred = float(np.sum(m2_path)) / (2.0 * C_PHI * K_PKT ** 2)
    # Also report path-integrated deficit (first moment)
    deficit_int = float(np.sum(d_line[xi0:xi1 + 1]))
    return dt_pred, deficit_int, m2_path


def bending_prediction(deficit3d, L, b_list, y_center, z_b, x_range=None):
    """Predict alpha(b) for pulse at impact parameter b from ring axis.

    alpha = -(1/(2 c_phi^2 k^2)) integ d__y m^2(x,y=y_c+b) dx
    """
    if x_range is None:
        x_range = (4.0, L - 4.0)
    xi0 = int(np.ceil(x_range[0]))
    xi1 = int(np.floor(x_range[1]))

    alphas = []
    for b in b_list:
        y_b = y_center + b
        # central difference: d__y m^2 at y=y_b
        m2_plus, _  = path_integral_deficit2(deficit3d, None, y_b + 0.5, z_b, L)
        m2_minus, _ = path_integral_deficit2(deficit3d, None, y_b - 0.5, z_b, L)
        dm2_dy = (m2_plus - m2_minus) / 1.0
        alpha_1911 = -float(np.sum(dm2_dy[xi0:xi1 + 1])) \
                     / (2.0 * C_PHI ** 2 * K_PKT ** 2)
        alphas.append(alpha_1911)
    return alphas


def describe_asymptote(b_list, dt_list):
    """Fit dt vs {const, log(b), 1/b} and report best via RSS."""
    b = np.array(b_list, dtype=float)
    dt = np.array(dt_list, dtype=float)
    # Const
    dt_const = np.full_like(dt, dt.mean())
    rss_c = float(np.sum((dt - dt_const) ** 2))
    # log(b): dt = a + c*log(b)
    A = np.vstack([np.ones_like(b), np.log(b)]).T
    (coef_log, _, _, _) = np.linalg.lstsq(A, dt, rcond=None)
    dt_log = A @ coef_log
    rss_l = float(np.sum((dt - dt_log) ** 2))
    # 1/b: dt = a + c/b
    A = np.vstack([np.ones_like(b), 1.0 / b]).T
    (coef_inv, _, _, _) = np.linalg.lstsq(A, dt, rcond=None)
    dt_inv = A @ coef_inv
    rss_i = float(np.sum((dt - dt_inv) ** 2))
    # linear b: dt = a + c*b
    A = np.vstack([np.ones_like(b), b]).T
    (coef_lin, _, _, _) = np.linalg.lstsq(A, dt, rcond=None)
    rss_lin = float(np.sum((dt - A @ coef_lin) ** 2))
    return {
        'const': rss_c,
        'log(b)': (rss_l, coef_log),
        '1/b':   (rss_i, coef_inv),
        'lin(b)': (rss_lin, coef_lin),
    }


def main():
    print("=" * 78)
    print("QNG v8 CPU prediction -- Shapiro dtt(b) and bending alpha(b)")
    print("  (uses cached L=28 R=4 ring; no GPU needed)")
    print("=" * 78)
    print(f"  c_phi  = {C_PHI:.5f}")
    print(f"  k_pkt  = {K_PKT:.5f}")
    print(f"  g/2/mu_phi = {0.5 * G_V_COUPLE / MU_PHI:.5f}")
    print()

    L = 28
    R = 4
    deficit3d = load_ring(L, R)
    if deficit3d is None:
        print("No ring cache; abort.")
        return
    y_c = L / 2.0
    z_c = L / 2.0

    # --- (A) On-rim Shapiro: y_line = y_c + R (original probe geometry) ---
    print("=" * 78)
    print("[A] On-rim Shapiro prediction (y = L/2 + R)")
    print("=" * 78)
    dt_on_rim, def_int_on, m2_path_on = shapiro_delay_prediction(
        deficit3d, L, y_b=y_c + R, z_b=z_c)
    print(f"  pulse at y={y_c + R:.1f}, z={z_c:.1f}, x in [4,{L-4}]")
    print(f"  integdeficit ds  = {def_int_on:.3f}")
    print(f"  dtt_pred      = {dt_on_rim:.3f} lu")
    print(f"  Measured (Test 3b GPU): +26.00 lu")
    print(f"  Ratio (measured/predicted): {26.0 / dt_on_rim:.2f}")
    print(f"  Peak m^2(x):  {float(m2_path_on.max()):.5f}")
    print()

    # --- (B) Far-field Shapiro: b in {4, 8, 12} at y = y_c + b ---
    print("=" * 78)
    print("[B] Far-field Shapiro prediction (impact parameter scan)")
    print("=" * 78)
    b_list = [4, 8, 12]
    print(f"  b        dtt_pred      integdeficit      max m^2(x)")
    dt_list = []
    for b in b_list:
        dt_b, def_int_b, m2_b = shapiro_delay_prediction(
            deficit3d, L, y_b=y_c + b, z_b=z_c)
        dt_list.append(dt_b)
        print(f"  b={b:>2} :  {dt_b:>10.3f}    {def_int_b:>8.3f}    "
              f"{float(m2_b.max()):.5e}")

    # Compare to measured (from tail of GPU log): b=4 -> 26, b=8 -> 27
    print()
    print(f"  Measured so far: b=4 -> +26.00 lu, b=8 -> +27.00 lu")
    print(f"  (b=12 still running on GPU)")

    print()
    fits = describe_asymptote(b_list, dt_list)
    print(f"  Falloff fits (RSS, lower = better):")
    print(f"    const    RSS = {fits['const']:.4f}")
    print(f"    log(b)   RSS = {fits['log(b)'][0]:.4f}  "
          f"coef = {fits['log(b)'][1]}")
    print(f"    1/b      RSS = {fits['1/b'][0]:.4f}  "
          f"coef = {fits['1/b'][1]}")
    print(f"    lin(b)   RSS = {fits['lin(b)'][0]:.4f}  "
          f"coef = {fits['lin(b)'][1]}")
    best = min(fits.keys(),
               key=lambda k: fits[k] if isinstance(fits[k], float)
               else fits[k][0])
    print(f"  Best: {best}")
    print()
    print(f"  Einstein 1911 prediction: 1/b falloff (sharp cutoff)")
    print(f"  GR 1915 prediction:       log(b) falloff (slow)")
    print(f"  If our theory says CONST -> coupling is saturated inside grid")
    print()

    # --- (C) On-axis Shapiro: path through ring center y=L/2, z=L/2 ---
    print("=" * 78)
    print("[C] On-axis (through ring center) -- pulse crosses full ring diameter")
    print("=" * 78)
    dt_on_axis, def_int_ax, m2_ax = shapiro_delay_prediction(
        deficit3d, L, y_b=y_c, z_b=z_c)
    print(f"  pulse at y={y_c:.1f}, z={z_c:.1f}, x in [4,{L-4}]")
    print(f"  integdeficit ds  = {def_int_ax:.3f}")
    print(f"  dtt_pred      = {dt_on_axis:.3f} lu")
    print(f"  Peak m^2(x):  {float(m2_ax.max()):.5f}")
    print()

    # --- (D) BENDING PREDICTION -- THE critical test ---
    print("=" * 78)
    print("[D] Einstein bending prediction alpha(b)")
    print("=" * 78)
    print("  H_1911:   alpha  (scalar-c theory)")
    print("  H_GR:     alpha x 2  (metric, Eddington 1919)")
    print()
    b_bend = [3, 4, 5, 6, 8, 10]
    alphas_1911 = bending_prediction(deficit3d, L, b_bend, y_c, z_c)
    print(f"  {'b':>4} {'alpha_1911 (rad)':>16} {'alpha_GR (rad)':>16} "
          f"{'dty at x=20 (nodes)':>22}")
    print("  " + "-" * 70)
    path_len = L - 8   # x from 4 to L-4
    for b, a in zip(b_bend, alphas_1911):
        a_gr = 2.0 * a
        dy_1911 = a * path_len
        print(f"  {b:>4} {a:>+16.5e} {a_gr:>+16.5e}  {dy_1911:>+22.5e}")

    print()
    max_alpha = max(abs(a) for a in alphas_1911)
    max_dy = max_alpha * path_len
    print(f"  Max predicted |dty| (1911) over 20 nodes: {max_dy:.3e} nodes")
    if max_dy < 0.01:
        print("  -> TOO SMALL for 20-node path. Need L>=40 or longer integration.")
        print(f"  -> For detectable dty~0.1: path length >= {0.1/max_alpha:.0f} nodes.")
    elif max_dy < 0.1:
        print("  -> Marginal. Feasible with Gaussian centroid fit at L=32.")
    else:
        print(f"  -> Detectable. L=28 probe should resolve dty ~ {max_dy:.2f} nodes.")

    print()
    print("=" * 78)
    print("SUMMARY -- what these predictions tell us")
    print("=" * 78)
    print(f"  1. Shapiro on-rim prediction vs measurement:")
    print(f"     pred {dt_on_rim:.1f} lu  vs  measured 26.0 lu  -> ratio "
          f"{26.0 / max(dt_on_rim, 1e-6):.2f}")
    print()
    print(f"  2. Far-field asymptotic:")
    print(f"     theory predicts '{best}' as best falloff law")
    print()
    print(f"  3. Bending feasibility:")
    print(f"     need path >= {max(10, int(0.1/max_alpha)+1)} nodes to get dty > 0.1")


if __name__ == "__main__":
    main()
