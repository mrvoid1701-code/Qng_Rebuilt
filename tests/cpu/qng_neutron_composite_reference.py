from __future__ import annotations

"""QNG-CPU-164: W+W- composite — neutron candidate test.

Hypothesis: The QNG neutron is a bound state of two opposite-chirality
ring vortices (W+ and W-). v12 forbids neutral elementary particles
(DER-QNG-082 charge-topology link), but composites with q=0 are allowed.

CPU-049 showed W+W- attract; CPU-050 showed bound state at d≈3λ.
This test asks: what is the EQUILIBRIUM MASS of the composite under
v12 enhanced (e=3.0)?

If composite mass M_neutron_QNG / M_proton_QNG ≈ 1.001 (the SM ratio),
then neutron-as-composite is confirmed structurally.

If M_composite >> M_proton, the composite is too heavy and neutron-as-
elementary needs v13 extension.

Method:
- Initial phi: two opposite-chirality rings at separation D=6 lu
- W+ ring: phi = atan2(z, rho-R) around center 1
- W- ring: phi = -atan2(z, rho-R) around center 2
- Run v12 enhanced (e=3.0) for full 3-phase protocol
- Measure final M_ring of composite
- Compare with trefoil (proton candidate) mass

Reference: DER-QNG-093 §8 §A (open identifications), Paper 7 P4.
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-neutron-composite-v1"


def init_phi_W_plus_minus(separation: int = 6, ring_R: float = 5.0):
    """Two opposite-chirality ring vortices at distance `separation`."""
    L = v12.L
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    # Center the two rings along the y-axis, separated by `separation`
    YC1 = YC - separation / 2.0
    YC2 = YC + separation / 2.0

    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')

    def mi(d):
        d = d.copy()
        d[d >  L/2] -= L
        d[d < -L/2] += L
        return d

    # W+ ring centered at (XC, YC1, ZC)
    DX1 = mi(XX - XC); DY1 = mi(YY - YC1); DZ1 = mi(ZZ - ZC)
    rho1 = np.sqrt(DX1*DX1 + DY1*DY1)
    phi_plus = np.arctan2(DZ1, rho1 - ring_R)

    # W- ring centered at (XC, YC2, ZC) with OPPOSITE winding direction
    DX2 = mi(XX - XC); DY2 = mi(YY - YC2); DZ2 = mi(ZZ - ZC)
    rho2 = np.sqrt(DX2*DX2 + DY2*DY2)
    phi_minus = -np.arctan2(DZ2, rho2 - ring_R)

    # Superposition (wrapped)
    phi = phi_plus + phi_minus
    return v12.wrap_pi(phi)


def init_phi_two_W_plus(separation: int = 6, ring_R: float = 5.0):
    """Two SAME-chirality rings (W+W+) for comparison — should REPEL or stay
    separated. Mass should be ~2x single ring (no binding)."""
    L = v12.L
    XC, YC, ZC = L/2.0, L/2.0, L/2.0
    YC1 = YC - separation / 2.0
    YC2 = YC + separation / 2.0

    ax = np.arange(L, dtype=np.float64)
    XX, YY, ZZ = np.meshgrid(ax, ax, ax, indexing='ij')

    def mi(d):
        d = d.copy()
        d[d >  L/2] -= L
        d[d < -L/2] += L
        return d

    DX1 = mi(XX - XC); DY1 = mi(YY - YC1); DZ1 = mi(ZZ - ZC)
    rho1 = np.sqrt(DX1*DX1 + DY1*DY1)
    phi_1 = np.arctan2(DZ1, rho1 - ring_R)

    DX2 = mi(XX - XC); DY2 = mi(YY - YC2); DZ2 = mi(ZZ - ZC)
    rho2 = np.sqrt(DX2*DX2 + DY2*DY2)
    phi_2 = np.arctan2(DZ2, rho2 - ring_R)

    return v12.wrap_pi(phi_1 + phi_2)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--separation", type=int, default=6,
                    help="Separation between rings (lu)")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Use v12 enhanced parameters (same as CPU-159)
    v12.E_CHARGE = 3.0
    v12.MU_A = 1.0
    v12.BETA_A = 0.05

    print(f"QNG-CPU-164: W+W- composite neutron test")
    print(f"L={v12.L} separation={args.separation} v12 enhanced e={v12.E_CHARGE}")
    print()

    configs = [
        ("ring_W+_single", lambda: v12.init_phi_hopfion(0)),
        ("W+W-_composite", lambda: init_phi_W_plus_minus(args.separation)),
        ("W+W+_control",   lambda: init_phi_two_W_plus(args.separation)),
        ("trefoil_proton", lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
    ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---", flush=True)
        res = v12.run_v12(label, init_fn)
        results.append(res)
        print(f"  [{label}] DONE  M_P2={res['M_P2_end']:.2f}  "
              f"M_P3={res['M_P3_end']:.2f}  "
              f"decay_ratio={res['mean_decay_ratio']:.4f}",
              flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total time: {dt:.1f} s\n")

    print("=" * 100)
    print(f"{'Config':<20} {'M_P2_end':>10} {'M_P3_end':>10} "
          f"{'decay_ratio':>12} {'half_life':>10}")
    print("-" * 100)
    for r in results:
        print(f"{r['label']:<20} {r['M_P2_end']:>10.2f} {r['M_P3_end']:>10.2f} "
              f"{r['mean_decay_ratio']:>12.4f} {r['half_life_lu']:>10.0f}")
    print("=" * 100)

    # Identification analysis: composite mass relative to trefoil (proton)
    composite = next(r for r in results if r["label"] == "W+W-_composite")
    proton = next(r for r in results if r["label"] == "trefoil_proton")
    if proton["M_P3_end"] > 0:
        ratio = composite["M_P3_end"] / proton["M_P3_end"]
        predicted_neutron_mass = ratio * 938.27  # MeV
        actual_neutron_mass = 939.57  # MeV
        error_pct = (predicted_neutron_mass - actual_neutron_mass) / \
                    actual_neutron_mass * 100
        print()
        print(f"Neutron identification (W+W- composite -> neutron):")
        print(f"  QNG composite mass / QNG trefoil = {ratio:.4f}")
        print(f"  SM neutron mass / proton = {939.57/938.27:.4f}")
        print(f"  Predicted neutron m_QNG = {predicted_neutron_mass:.2f} MeV")
        print(f"  Actual neutron mass = {actual_neutron_mass:.2f} MeV")
        print(f"  Mass error: {error_pct:+.2f}%")

    # Bound state vs unbound comparison
    single = next(r for r in results if r["label"] == "ring_W+_single")
    same_chirality = next(r for r in results if r["label"] == "W+W+_control")
    print()
    print("Binding analysis:")
    print(f"  Single W+ ring mass: {single['M_P3_end']:.2f}")
    print(f"  W+W- composite: {composite['M_P3_end']:.2f}")
    print(f"  W+W+ control: {same_chirality['M_P3_end']:.2f}")
    print()
    print(f"  Binding energy (W+W-): "
          f"{2 * single['M_P3_end'] - composite['M_P3_end']:.2f}")
    print(f"  (2x single - composite > 0 means BOUND)")

    report = {
        "test_id": "QNG-CPU-164",
        "params": {"L": v12.L, "separation": args.separation,
                   "E_CHARGE": v12.E_CHARGE},
        "results": results,
        "composite_neutron_analysis": {
            "qng_ratio_composite_over_trefoil": composite["M_P3_end"] / proton["M_P3_end"]
                if proton["M_P3_end"] > 0 else None,
            "predicted_neutron_mass_MeV": ratio * 938.27 if proton["M_P3_end"] > 0 else None,
            "actual_neutron_mass_MeV": 939.57,
        },
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
