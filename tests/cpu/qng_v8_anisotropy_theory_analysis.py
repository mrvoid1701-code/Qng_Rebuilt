"""Rigorous theoretical analysis of the measured 120% anisotropy.

Question: can the 4x difference between transverse and parallel Shapiro
delays (26 vs 104 lu) be explained by pure scalar refraction
(integrated deficit along path), or does it require genuine
direction-dependent (tensorial) coupling?

Loads cached L=28 R=4 ring, computes TWO physical quantities along
each path:

  (i)  Integrated m^2(x) ds -- Option-E^2 scalar coupling contribution
       to Shapiro delay.
  (ii) Integrated |grad phi_bg|^2 ds -- the kinetic-term coupling
       strength between pulse-phi and background-phi gradient.
       This is the TENSORIAL channel: coupling to direction of pulse
       propagation relative to background winding.

Theory:
  KG wave equation for pulse phi_p on a background (sg0, sm0, phi0):
    mu_phi * d^2 phi_p/dt^2 = (BETA_PHI/6) grad^2 phi_p
                                - g * (SIGMA_M_REF - sm0)^2 * sin(phi0) * phi_p  [V_couple linearization]
  But there's ALSO a coupling from the kinetic term if phi0 has large
  second derivatives (mode conversion / scattering at gradients).
  Any direction-dependence of delay must come from that coupling.

If scalar-path prediction matches:  120% is 'just integrated deficit'.
If scalar-path prediction does NOT match:  the extra anisotropy
comes from the kinetic/direction coupling -> genuine tensor.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1" / "ring_cache"

SIGMA_M_REF = 1.0
BETA_PHI    = 0.06
MU_PHI      = 0.857
G_V_COUPLE  = 0.22
C_PHI_SQ    = BETA_PHI / (6.0 * MU_PHI)
C_PHI       = float(np.sqrt(C_PHI_SQ))
K_PKT       = np.pi / 4.0


def load_ring(L=28, R=4, P1=300, P2=1000):
    files = list(CACHE.glob(f"ring_L{L}_R{R}_P1_{P1}_P2_{P2}_*.npz"))
    if not files:
        return None, None
    data = np.load(files[0])
    sm = data['sm'].reshape(L, L, L)     # [z, y, x]
    phi = data['phi'].reshape(L, L, L)    # [z, y, x]
    return sm, phi


def grad_phi_sq(phi3d, axis_order='zyx'):
    """Return |grad phi|^2 using central differences (periodic)."""
    # axis 0 = z, 1 = y, 2 = x by our reshape convention
    dphi_dz = (np.roll(phi3d, -1, axis=0) - np.roll(phi3d, 1, axis=0)) / 2.0
    dphi_dy = (np.roll(phi3d, -1, axis=1) - np.roll(phi3d, 1, axis=1)) / 2.0
    dphi_dx = (np.roll(phi3d, -1, axis=2) - np.roll(phi3d, 1, axis=2)) / 2.0
    return dphi_dx ** 2 + dphi_dy ** 2 + dphi_dz ** 2, \
           dphi_dx, dphi_dy, dphi_dz


def path_integrals_T(sm3d, phi3d, L, R):
    """Transverse path: x varies in [4, L-4], y=L/2+R, z=L/2.

    sm3d and phi3d indexed as [z, y, x].
    """
    y_idx = int(L // 2 + R)         # 18
    z_idx = int(L // 2)              # 14
    deficit = SIGMA_M_REF - sm3d[z_idx, y_idx, 4:L-3]     # x in [4, L-4]
    m2 = 0.5 * G_V_COUPLE * deficit ** 2 / MU_PHI
    int_m2 = float(np.sum(m2))        # sum over nodes (dx=1)
    int_def = float(np.sum(deficit))

    _, _, _, dphi_dz_full = grad_phi_sq(phi3d)
    # pulse direction: +x.  Direction-coupling = |dphi_bg/dx| integrated
    _, dphi_dx_full, dphi_dy_full, _ = grad_phi_sq(phi3d)
    grad_par = dphi_dx_full[z_idx, y_idx, 4:L-3]    # gradient ALONG pulse
    grad_perp = np.sqrt(dphi_dy_full[z_idx, y_idx, 4:L-3] ** 2
                        + dphi_dz_full[z_idx, y_idx, 4:L-3] ** 2)
    int_grad_par2  = float(np.sum(grad_par ** 2))
    int_grad_perp2 = float(np.sum(grad_perp ** 2))
    return {
        'int_deficit': int_def, 'int_m2': int_m2,
        'int_grad_par2': int_grad_par2,
        'int_grad_perp2': int_grad_perp2,
        'dt_scalar_pred': int_m2 / (2.0 * C_PHI * K_PKT ** 2),
    }


def path_integrals_P(sm3d, phi3d, L, R):
    """Parallel path: z varies in [4, L-4], x=L/2, y=L/2 (ring axis)."""
    x_idx = int(L // 2)
    y_idx = int(L // 2)
    deficit = SIGMA_M_REF - sm3d[4:L-3, y_idx, x_idx]      # z in [4, L-4]
    m2 = 0.5 * G_V_COUPLE * deficit ** 2 / MU_PHI
    int_m2 = float(np.sum(m2))
    int_def = float(np.sum(deficit))

    _, dphi_dx_full, dphi_dy_full, dphi_dz_full = grad_phi_sq(phi3d)
    # pulse direction: +z.  Direction-coupling = |dphi_bg/dz| along path
    grad_par = dphi_dz_full[4:L-3, y_idx, x_idx]
    grad_perp = np.sqrt(dphi_dx_full[4:L-3, y_idx, x_idx] ** 2
                        + dphi_dy_full[4:L-3, y_idx, x_idx] ** 2)
    int_grad_par2  = float(np.sum(grad_par ** 2))
    int_grad_perp2 = float(np.sum(grad_perp ** 2))
    return {
        'int_deficit': int_def, 'int_m2': int_m2,
        'int_grad_par2': int_grad_par2,
        'int_grad_perp2': int_grad_perp2,
        'dt_scalar_pred': int_m2 / (2.0 * C_PHI * K_PKT ** 2),
    }


def main():
    print("=" * 78)
    print("ANISOTROPY THEORY ANALYSIS  --  why is parallel 4x transverse?")
    print("=" * 78)

    L = 28
    R = 4
    sm, phi = load_ring(L, R)
    if sm is None:
        print("  Ring cache not found.")
        return

    T = path_integrals_T(sm, phi, L, R)
    P = path_integrals_P(sm, phi, L, R)

    print(f"  c_phi = {C_PHI:.5f}")
    print(f"  k_pkt = {K_PKT:.5f}")
    print()
    print(f"{'Quantity':<35} {'T (rim, +x)':>18} {'P (axis, +z)':>18}"
          f"  {'P/T':>8}")
    print("-" * 85)
    for key, label in [
        ('int_deficit',   'integ deficit (nodes)'),
        ('int_m2',        'integ m^2(x) (lu^-2)'),
        ('dt_scalar_pred','dt_scalar_pred (lu)'),
        ('int_grad_par2', 'integ (d_par phi_bg)^2'),
        ('int_grad_perp2','integ (d_perp phi_bg)^2'),
    ]:
        t = T[key]
        p = P[key]
        ratio = p / t if abs(t) > 1e-20 else float('inf')
        print(f"  {label:<33} {t:>18.4f} {p:>18.4f}  {ratio:>+8.3f}")

    print()
    print("=" * 78)
    print("MEASURED vs PREDICTED")
    print("=" * 78)
    print(f"  dt_measured  T (transverse) = +26.00 lu")
    print(f"  dt_measured  P (parallel)   = +104.00 lu")
    print(f"  dt_measured  P/T ratio       = 4.00")
    print()
    print(f"  dt_scalar-theory P/T ratio   = {P['dt_scalar_pred']/T['dt_scalar_pred']:.3f}")
    print()

    scalar_ratio = P['dt_scalar_pred'] / T['dt_scalar_pred']
    excess_anisotropy = 4.00 / scalar_ratio
    if abs(excess_anisotropy - 1.0) < 0.3:
        print(f"  -> Scalar theory explains measured anisotropy within 30%.")
        print(f"     (measured ratio 4.0 vs scalar-theory {scalar_ratio:.2f},")
        print(f"      excess factor {excess_anisotropy:.2f}).")
        print(f"  -> 120% anisotropy is PATH-LENGTH effect, not tensorial.")
    else:
        print(f"  -> Scalar theory does NOT explain the anisotropy.")
        print(f"     (measured ratio 4.0 vs scalar-theory {scalar_ratio:.2f},")
        print(f"      excess factor {excess_anisotropy:.2f}x beyond scalar).")
        print(f"  -> The measured anisotropy requires a direction-dependent")
        print(f"     coupling -- genuine TENSORIAL (or kinetic-mode-coupling)")
        print(f"     structure in the pulse-ring interaction.")

    print()
    print("KINETIC-MODE coupling signatures:")
    par_2    = P['int_grad_par2']
    perp_2   = T['int_grad_par2']
    kinetic_ratio = par_2 / max(perp_2, 1e-20)
    print(f"  |d_along_pulse phi_bg|^2  parallel path = {par_2:.4f}")
    print(f"  |d_along_pulse phi_bg|^2  transverse    = {perp_2:.4f}")
    print(f"  ratio {kinetic_ratio:.2f}")
    print()
    print("  Pulse couples to background phi gradient ALONG its direction")
    print("  of propagation (2 nabla(phi_bg) . nabla(phi_p) term).")
    print("  Large kinetic_ratio -> mode conversion / scattering / amplification")
    print("  on axis.  This is a non-scalar, direction-dependent effect.")


if __name__ == "__main__":
    main()
