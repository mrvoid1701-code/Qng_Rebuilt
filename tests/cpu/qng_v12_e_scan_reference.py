from __future__ import annotations

"""QNG-CPU-160: Parameter scan e_CHARGE — find critical coupling e* where
v7-decay transitions to v12-enhanced-stable regime.

CPU-152 found v12 canonical (e=0.3) is too weak to change v7 behavior.
CPU-159 found v12 enhanced (e=3.0) stabilizes all knots as
topology-dependent mass attractors.

CPU-160 scans e in {0.5, 1.0, 1.5, 2.0, 2.5, 3.0} on three reference
configs (ring, Hopfion Q1, trefoil) to map the transition.

Output:
- M_ring(P3 end) per (config, e)
- Decay rate vs growth rate per (config, e)
- Identify e* where M_ring stops decaying

Reference: Paper 7 §3.7, DER-QNG-092 §G.
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-v12-e-scan-v1"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--e-values", type=float, nargs='+',
                    default=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    configs = [
        ("ring_Q0",    lambda: v12.init_phi_hopfion(0)),
        ("hopfion_Q1", lambda: v12.init_phi_hopfion(1)),
        ("trefoil",    lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
    ]

    print(f"QNG-CPU-160: e_CHARGE scan")
    print(f"L={v12.L}  e values: {args.e_values}")
    print(f"Knots: {[c[0] for c in configs]}")
    print()

    all_results = []
    t_start = time.time()
    for e_val in args.e_values:
        v12.E_CHARGE = e_val
        print(f"=== e_CHARGE = {e_val} ===")
        for label, init_fn in configs:
            res = v12.run_v12(label, init_fn)
            res["e_CHARGE"] = e_val
            all_results.append(res)
            print(f"  [{label}@e={e_val}] M_P2={res['M_P2_end']:.1f} "
                  f"M_P3={res['M_P3_end']:.1f} "
                  f"ratio={res['mean_decay_ratio']:.4f}")
        print()
    dt = time.time() - t_start
    print(f"Total time: {dt:.1f} s\n")

    # Tabulate per knot, with e on rows
    print("=" * 95)
    print(f"{'e':>5} {'config':<14} {'M_P2_end':>10} {'M_P3_end':>10} "
          f"{'decay_ratio':>12} {'regime':>10}")
    print("-" * 95)
    for r in all_results:
        if r["mean_decay_ratio"] < 0.95:
            regime = "decay"
        elif r["mean_decay_ratio"] > 1.05:
            regime = "growth"
        else:
            regime = "stable"
        print(f"{r['e_CHARGE']:>5.1f} {r['label']:<14} "
              f"{r['M_P2_end']:>10.1f} {r['M_P3_end']:>10.1f} "
              f"{r['mean_decay_ratio']:>12.4f} {regime:>10}")
    print("=" * 95)

    # Find e* per knot (where decay -> stable)
    print()
    print("Critical e* per knot (where decay -> stable, ratio crosses 1.0):")
    for label in [c[0] for c in configs]:
        knot_results = [r for r in all_results if r["label"] == label]
        knot_results.sort(key=lambda r: r["e_CHARGE"])
        e_star = None
        for i in range(len(knot_results) - 1):
            if knot_results[i]["mean_decay_ratio"] < 1.0 <= knot_results[i+1]["mean_decay_ratio"]:
                # interpolate
                e_lo, r_lo = knot_results[i]["e_CHARGE"], knot_results[i]["mean_decay_ratio"]
                e_hi, r_hi = knot_results[i+1]["e_CHARGE"], knot_results[i+1]["mean_decay_ratio"]
                e_star = e_lo + (1.0 - r_lo) / (r_hi - r_lo) * (e_hi - e_lo)
                break
        print(f"  {label}: e* = {e_star:.3f}" if e_star is not None
              else f"  {label}: e* not bracketed in scan range")

    report = {
        "test_id": "QNG-CPU-160",
        "params": {"L": v12.L, "e_values": args.e_values,
                   "MU_A": v12.MU_A, "BETA_A": v12.BETA_A},
        "results": all_results,
        "interpretation": (
            "Parameter scan e_CHARGE to find critical coupling e* where "
            "v7-decay behavior transitions to v12-enhanced-stable. "
            "Higgs-like mass mechanism activated above e*."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
