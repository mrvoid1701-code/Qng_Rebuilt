from __future__ import annotations

"""QNG-CPU-168: Discover more particles via additional composites + knot types.

Test:
A. W+W+W- composite (q=+1): could be excited proton state (N*, Roper, etc.)
B. W+W+W+ composite (q=+3): no SM analog, structural prediction
C. W+W-W+ stacked (q=+1, different layout): alternative excited state
D. 5_2 twist knot (4 crossings, distinct from trefoil and figure-8)
E. Hopfion Q1 + ring (q=+2): alternative to W+W+ for Delta++
F. Anti-trefoil (chirality reverse): should match proton mass (= anti-proton)

Reference: DER-QNG-094 §10 follow-ups; Paper 7 §4 expansion.
"""

import json
import math
import time
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
import qng_v12_dynamics_reference as v12


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-more-particles-v1"


def init_phi_3rings(separation: int = 4, charges: tuple = (+1, +1, -1),
                     ring_R: float = 5.0):
    """Three rings along y-axis with given charges (sign of poloidal winding)."""
    L = v12.L
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    n = len(charges)
    offsets = [(i - (n-1)/2.0) * separation for i in range(n)]

    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')

    def mi(d):
        d = d.copy()
        d[d >  L/2] -= L
        d[d < -L/2] += L
        return d

    phi_total = np.zeros_like(XX)
    for off, chg in zip(offsets, charges):
        DXi = mi(XX - XC); DYi = mi(YY - (YC + off)); DZi = mi(ZZ - ZC)
        rho_i = np.sqrt(DXi*DXi + DYi*DYi)
        phi_i = chg * np.arctan2(DZi, rho_i - ring_R)
        phi_total = phi_total + phi_i

    return v12.wrap_pi(phi_total)


def init_phi_5_2_knot(scale_factor: float = 0.4):
    """5_2 twist knot parametrization.

    Standard form: x(t) = (R + r cos t) cos 2t with twist...
    Use Lissajous-like: r(t) = (3cos t + cos 5t, 2sin t + sin 5t, 2 sin 3t)
    """
    n_curve = 360
    ts = np.linspace(0.0, 2*math.pi, n_curve, endpoint=False)
    s = scale_factor * v12.L / 8.0
    x = s * (3 * np.cos(ts) + np.cos(5*ts))
    y = s * (2 * np.sin(ts) + np.sin(5*ts))
    z = s * (2 * np.sin(3*ts))
    curve = np.stack([x, y, z], axis=-1)

    return v12.init_phi_from_knot(lambda t: np.stack([
        s * (3 * np.cos(t) + np.cos(5*t)),
        s * (2 * np.sin(t) + np.sin(5*t)),
        s * (2 * np.sin(3*t)),
    ], axis=-1))


def init_phi_anti_trefoil():
    """Anti-trefoil: phi = -trefoil_phi (chirality reverse)."""
    return v12.wrap_pi(-v12.init_phi_from_knot(v12.trefoil_curve))


def init_phi_hopfion_plus_ring(distance: int = 6):
    """Hopfion Q1 + ring (q=+1 + q=+1 = q=+2) at separation."""
    L = v12.L
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    YC1 = YC - distance / 2.0
    YC2 = YC + distance / 2.0

    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')

    def mi(d):
        d = d.copy()
        d[d >  L/2] -= L
        d[d < -L/2] += L
        return d

    # Hopfion at center 1
    DX1 = mi(XX - XC); DY1 = mi(YY - YC1); DZ1 = mi(ZZ - ZC)
    rho1 = np.sqrt(DX1*DX1 + DY1*DY1)
    phi_hopfion = np.arctan2(DZ1, rho1 - 5.0) + np.arctan2(DY1, DX1)

    # Ring at center 2
    DX2 = mi(XX - XC); DY2 = mi(YY - YC2); DZ2 = mi(ZZ - ZC)
    rho2 = np.sqrt(DX2*DX2 + DY2*DY2)
    phi_ring = np.arctan2(DZ2, rho2 - 5.0)

    return v12.wrap_pi(phi_hopfion + phi_ring)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    v12.E_CHARGE = 3.0
    v12.MU_A = 1.0
    v12.BETA_A = 0.05

    print(f"QNG-CPU-168: Discover more particles")
    print(f"L={v12.L} e={v12.E_CHARGE}")
    print()

    configs = [
        ("anti_trefoil",       lambda: init_phi_anti_trefoil()),
        ("WpWpWm_q+1",         lambda: init_phi_3rings(separation=4, charges=(+1,+1,-1))),
        ("WpWpWp_q+3",         lambda: init_phi_3rings(separation=4, charges=(+1,+1,+1))),
        ("WpWmWp_layered_q+1", lambda: init_phi_3rings(separation=3, charges=(+1,-1,+1))),
        ("knot_5_2",           lambda: init_phi_5_2_knot()),
        ("Hopfion_plus_ring_q+2", lambda: init_phi_hopfion_plus_ring(distance=6)),
    ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---")
        try:
            res = v12.run_v12(label, init_fn)
            results.append(res)
            print(f"  [{label}] M_P3={res['M_P3_end']:.2f}  "
                  f"decay_ratio={res['mean_decay_ratio']:.4f}")
        except Exception as e:
            print(f"  [{label}] ERROR: {e}")
        print()
    dt = time.time() - t_start
    print(f"Total: {dt:.1f}s")
    print()

    print("=" * 100)
    print(f"{'Config':<25} {'M_P3':>10} {'ratio vs proton':>16} "
          f"{'pred MeV':>10} {'best SM match':>25}")
    print("-" * 100)
    proton_M = 1902.16
    proton_m_MeV = 938.27
    sm_baryons = [
        ("proton", 938.27, +1),
        ("neutron", 939.57, 0),
        ("N(1440)", 1440, +1),
        ("N(1520)", 1520, +1),
        ("N(1535)", 1535, +1),
        ("N(1650)", 1650, +1),
        ("Sigma+", 1189.37, +1),
        ("Sigma-", 1197.45, -1),
        ("Delta+", 1232, +1),
        ("Delta++", 1232, +2),
        ("Delta--", 1232, -2),
        ("Lambda", 1115.68, 0),
        ("eta'", 957.78, 0),
        ("a0(980)+", 980, +1),
        ("rho+", 775, +1),
    ]
    for r in results:
        ratio = r["M_P3_end"] / proton_M
        m_pred = ratio * proton_m_MeV
        # Find best match across all SM particles
        best = min(sm_baryons, key=lambda b: abs(m_pred - b[1]) / b[1])
        err = (m_pred - best[1]) / best[1] * 100
        print(f"{r['label']:<25} {r['M_P3_end']:>10.2f} {ratio:>16.4f} "
              f"{m_pred:>10.1f} {best[0] + f' ({err:+.2f}%)':>25}")
    print("=" * 100)

    report = {
        "test_id": "QNG-CPU-168_more_particles",
        "params": {"L": v12.L, "E_CHARGE": v12.E_CHARGE},
        "results": results,
        "proton_reference_QNG": proton_M,
        "proton_reference_MeV": proton_m_MeV,
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
