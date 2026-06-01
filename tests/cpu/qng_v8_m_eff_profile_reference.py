"""Numerical m_eff^2(x) profile analysis on cached v8 ring.

Pre-registration: QNG-CPU-081 (DER-QNG-046 promotion item 3).

Purpose
-------
Test candidate #2 (evanescent tunneling) for the high-s saturation
discovered by QNG-GPU-022:

  m_eff^2(x, y, z) = (g / (2 mu_phi)) * Delta(x)^2 * cos(phi_bg(x))
  Delta = SIGMA_M_REF - sigma_m_scaled

Pulse dispersion: omega^2 = c_phi^2 * k^2 + m_eff^2
                  evanescent when m_eff^2 > omega^2

Configuration identical to QNG-GPU-022 post-cache scaling.

This is a CPU post-processing analysis - no new simulation run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

# v8 constants (MUST match qng_v8_canonical_gpu.py)
# NOTE: SIGMA_M_REF = 0.5 (NOT 1.0); verified via inspect.getsource on GPU module.
SIGMA_M_REF = 0.5
BETA_PHI    = 0.06
MU_PHI      = 0.857
G_V_COUPLE  = 0.22

C_PHI_SQ = BETA_PHI / (6.0 * MU_PHI)         # 0.011669...
C_PHI    = np.sqrt(C_PHI_SQ)

K_PKT    = 3.0 * np.pi / 4.0
OMEGA    = C_PHI * K_PKT
OMEGA_SQ = OMEGA * OMEGA                      # 0.06480 for k=3pi/4

CACHE_PATH = (ROOT / "07_validation" / "audits"
              / "qng-v8-stability-probe-v1" / "ring_cache"
              / "ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz")

L = 28
R = 4


def load_cached_ring():
    data = np.load(CACHE_PATH)
    sm   = data['sm' ].astype(np.float64).reshape(L, L, L)
    phi  = data['phi'].astype(np.float64).reshape(L, L, L)
    return sm, phi


def scale_deficit(sm, s):
    """sigma_m -> SIGMA_M_REF - s*(SIGMA_M_REF - sigma_m)."""
    return SIGMA_M_REF - s * (SIGMA_M_REF - sm)


def m_eff_sq_field(sm_scaled, phi_bg):
    """m_eff^2(x,y,z) = (g/(2 mu_phi)) * Delta^2 * cos(phi_bg)."""
    Delta = SIGMA_M_REF - sm_scaled
    coef  = G_V_COUPLE / (2.0 * MU_PHI)
    return coef * (Delta ** 2) * np.cos(phi_bg)


def extract_path_profile(field_3d, x_src, x_det, y_path, z_path):
    """Extract field along (x, y_path, z_path) for integer x in
    [x_src, x_det]."""
    xs = np.arange(int(x_src), int(x_det) + 1)
    return xs, field_3d[xs, int(y_path) % L, int(z_path) % L]


def wkb_reflection(m_eff_sq_path, xs, omega_sq):
    """Approximate WKB reflection through a barrier where
    m_eff^2(x) > omega^2.

    T ~ exp(-2 * integral sqrt(m_eff^2 - omega^2) dx) over evanescent region.
    R = 1 - T for a single barrier (rough 1D estimate).
    """
    kappa_sq = m_eff_sq_path - omega_sq
    evanescent = kappa_sq > 0
    if not evanescent.any():
        return 0.0, 0.0  # (transmission integral, R)
    kappa = np.sqrt(np.maximum(kappa_sq, 0.0))
    # integrate kappa over the path (unit spacing in lattice units)
    S = np.trapz(kappa, xs.astype(float))
    T = np.exp(-2.0 * S)
    R = 1.0 - T
    return float(S), float(R)


def analyze_one(sm, phi, s, b, x_src=4.0, x_det=24.0, z_line=L/2):
    """Compute m_eff^2 profile along path y = L/2 + b, z = L/2 for
    scaling factor s."""
    sm_s = scale_deficit(sm, s)
    field = m_eff_sq_field(sm_s, phi)
    y_path = 0.5 * L + b
    xs, m_eff_sq_path = extract_path_profile(field, x_src, x_det,
                                              y_path, z_line)
    Delta_path = SIGMA_M_REF - sm_s[xs, int(y_path) % L, int(z_line) % L]
    phi_path = phi[xs, int(y_path) % L, int(z_line) % L]

    max_m2 = float(m_eff_sq_path.max())
    min_m2 = float(m_eff_sq_path.min())
    mean_abs_m2 = float(np.mean(np.abs(m_eff_sq_path)))
    ix_max_abs = int(np.argmax(np.abs(m_eff_sq_path)))

    # Evanescent assessment (uses m_eff_sq > omega_sq; sign of m_eff_sq matters)
    frac_evan = float(np.mean(m_eff_sq_path > OMEGA_SQ))
    S, R_coef = wkb_reflection(m_eff_sq_path, xs, OMEGA_SQ)

    # Sign structure of cos(phi_bg) along path
    cos_phi = np.cos(phi_path)
    frac_pos = float(np.mean(cos_phi > 0))
    frac_neg = float(np.mean(cos_phi < 0))
    sign_flips = int(np.sum(np.diff(np.sign(cos_phi)) != 0))

    return {
        's': s,
        'b': b,
        'xs': xs.tolist(),
        'Delta_path': Delta_path.tolist(),
        'cos_phi_path': cos_phi.tolist(),
        'm_eff_sq_path': m_eff_sq_path.tolist(),
        'max_m_eff_sq': max_m2,
        'min_m_eff_sq': min_m2,
        'mean_abs_m_eff_sq': mean_abs_m2,
        'ix_max_abs': ix_max_abs,
        'x_max_abs': int(xs[ix_max_abs]),
        'ratio_max_to_omega_sq': max_m2 / OMEGA_SQ,
        'frac_evanescent': frac_evan,
        'wkb_action_S': S,
        'wkb_reflection_R': R_coef,
        'cos_phi_frac_pos': frac_pos,
        'cos_phi_frac_neg': frac_neg,
        'cos_phi_sign_flips': sign_flips,
    }


def verdict_label(max_m2, omega_sq):
    ratio = max_m2 / omega_sq
    if ratio >= 1.0:
        return 'H_evanescent_strong', ratio
    elif ratio >= 0.5:
        return 'H_evanescent_onset', ratio
    elif ratio >= 0.1:
        return 'H_intermediate', ratio
    else:
        return 'H_transparent', ratio


def main():
    print("=" * 80)
    print("QNG-CPU-081: m_eff^2(x) PROFILE ANALYSIS")
    print("  Test evanescent tunneling candidate for GPU-022 high-s saturation")
    print("=" * 80)
    print(f"  g = {G_V_COUPLE}, mu_phi = {MU_PHI}")
    print(f"  c_phi^2 = {C_PHI_SQ:.5f}, k = 3pi/4 = {K_PKT:.4f}")
    print(f"  omega^2 = {OMEGA_SQ:.4e}  (evanescent threshold)")
    print(f"  Cached ring: {CACHE_PATH.name}")
    print()

    sm, phi = load_cached_ring()
    print(f"  ring loaded, L={L}, sm shape={sm.shape}")
    print(f"  sm range: [{sm.min():.4f}, {sm.max():.4f}]")
    print(f"  phi range: [{phi.min():.4f}, {phi.max():.4f}]")

    # Sanity: M_ring at s=1 should match GPU cache (~176.85)
    M_ring = float(np.sum(SIGMA_M_REF - sm))
    print(f"  M_ring(s=1) = {M_ring:.2f}  (expected ~176.85)")
    print()

    s_list = [0.7, 1.0, 1.4]
    b_list = [4, 6]

    results = []
    for b in b_list:
        for s in s_list:
            r = analyze_one(sm, phi, s, b)
            results.append(r)

    # Verdicts
    print("=" * 80)
    print("m_eff^2 PROFILE RESULTS")
    print("=" * 80)
    header = f"{'b':>3} {'s':>5} {'max m_eff^2':>14} {'min m_eff^2':>14} {'ratio/omega^2':>14} {'frac_evan':>10} {'WKB R':>8} {'x_max':>6} {'sign_flips':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['b']:>3d} {r['s']:>5.2f} "
              f"{r['max_m_eff_sq']:>+14.4e} "
              f"{r['min_m_eff_sq']:>+14.4e} "
              f"{r['ratio_max_to_omega_sq']:>14.4f} "
              f"{r['frac_evanescent']:>10.3f} "
              f"{r['wkb_reflection_R']:>8.4f} "
              f"{r['x_max_abs']:>6d} "
              f"{r['cos_phi_sign_flips']:>10d}")
    print()

    # Primary verdict on b=6, s=1.4 (the saturation case)
    r_primary = next(r for r in results if r['b'] == 6 and r['s'] == 1.4)
    verdict, ratio = verdict_label(r_primary['max_m_eff_sq'], OMEGA_SQ)
    print("=" * 80)
    print(f"PRIMARY VERDICT (b=6, s=1.4):")
    print(f"  max m_eff^2 = {r_primary['max_m_eff_sq']:+.4e}")
    print(f"  omega^2     = {OMEGA_SQ:+.4e}")
    print(f"  ratio       = {ratio:.4f}")
    print(f"  {verdict}")
    print("=" * 80)
    print()

    # Scaling sanity: max m_eff^2 should scale as s^2 (at fixed b)
    print("S^2 SCALING CHECK (max m_eff^2 vs s):")
    for b in b_list:
        r1 = next(r for r in results if r['b'] == b and r['s'] == 1.0)
        for s_test in [0.7, 1.4]:
            r_s = next(r for r in results if r['b'] == b and r['s'] == s_test)
            ratio_obs = r_s['max_m_eff_sq'] / r1['max_m_eff_sq']
            ratio_exp = s_test ** 2
            dev = abs(ratio_obs - ratio_exp) / ratio_exp
            print(f"  b={b}, s={s_test}: observed ratio {ratio_obs:.4f}, "
                  f"expected {ratio_exp:.4f}, dev {dev*100:.2f}%")
    print()

    # cos(phi) sign structure
    print("cos(phi_bg) SIGN STRUCTURE ALONG PATH:")
    for r in results:
        if r['s'] == 1.0:  # only s=1, others identical except scaling
            print(f"  b={r['b']}: cos_phi_frac_pos={r['cos_phi_frac_pos']:.3f}, "
                  f"frac_neg={r['cos_phi_frac_neg']:.3f}, "
                  f"sign_flips={r['cos_phi_sign_flips']}")

    # Save
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-m-eff-profile-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L, 'R': R,
        'g': G_V_COUPLE, 'mu_phi': MU_PHI,
        'c_phi_sq': C_PHI_SQ,
        'k_pkt': K_PKT, 'omega_sq': OMEGA_SQ,
        'M_ring_base': M_ring,
        'cache_file': CACHE_PATH.name,
        'results': results,
        'primary_verdict': verdict,
        'primary_ratio': ratio,
        'verdict_thresholds': {
            'H_evanescent_strong': '>= 1.0',
            'H_evanescent_onset': '>= 0.5',
            'H_intermediate': '>= 0.1',
            'H_transparent': '< 0.1',
        },
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
