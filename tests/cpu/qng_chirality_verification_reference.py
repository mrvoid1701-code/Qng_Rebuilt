from __future__ import annotations

"""QNG-CPU-165: Chirality verification — anti-Hopfion ↔ Delta-, W-W- ↔ Delta--.

DER-QNG-094 predicts that under v12 chirality symmetry:
- anti-Hopfion Q1 (phi reversed) gives same mass as Hopfion Q1
  → identifies SM Delta- (q=-1, mass 1232 MeV) at same precision as Delta+
- W-W- composite (two anti-rings) gives same mass as W+W+ composite
  → identifies SM Delta-- (q=-2, mass 1232 MeV) at same precision as Delta++

This test confirms or refutes these chirality-derived predictions.

If anti-Hopfion mass ≠ Hopfion mass, the chirality symmetry is broken
and the identification framework fails.

Reference: DER-QNG-094 §6, Paper 7 §4.2''.
"""

import json
import time
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
import qng_v12_dynamics_reference as v12


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-chirality-verification-v1"


def init_phi_anti_hopfion(q_twist: int = 1):
    """Anti-Hopfion: phi = -(poloidal + q*toroidal)."""
    return v12.wrap_pi(-v12.init_phi_hopfion(q_twist))


def init_phi_W_minus_pair(separation: int = 6, ring_R: float = 5.0):
    """W-W- composite: two opposite-chirality rings."""
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
    phi_1 = -np.arctan2(DZ1, rho1 - ring_R)  # anti-ring

    DX2 = mi(XX - XC); DY2 = mi(YY - YC2); DZ2 = mi(ZZ - ZC)
    rho2 = np.sqrt(DX2*DX2 + DY2*DY2)
    phi_2 = -np.arctan2(DZ2, rho2 - ring_R)  # anti-ring

    return v12.wrap_pi(phi_1 + phi_2)


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

    print(f"QNG-CPU-165: Chirality verification under v12 enhanced")
    print(f"L={v12.L} e={v12.E_CHARGE}")
    print(f"Tests: anti-Hopfion -> Delta-, W-W- -> Delta--")
    print()

    configs = [
        ("Hopfion_Q1_W+",     lambda: v12.init_phi_hopfion(1)),
        ("antiHopfion_Q1_W-", lambda: init_phi_anti_hopfion(1)),
        ("WpWp_Delta++",      lambda: __import__('qng_neutron_composite_reference').init_phi_two_W_plus(6)),
        ("WmWm_Delta--",      lambda: init_phi_W_minus_pair(6)),
        ("trefoil_proton",    lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
    ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"--- {label} ---", flush=True)
        res = v12.run_v12(label, init_fn)
        results.append(res)
        print(f"  [{label}] M_P3={res['M_P3_end']:.2f}  "
              f"decay_ratio={res['mean_decay_ratio']:.4f}",
              flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total time: {dt:.1f} s")
    print()

    # Chirality symmetry test
    print("=" * 90)
    print(f"{'Config':<22} {'M_P3':>10} {'ratio vs trefoil':>20} {'SM compare':>20}")
    print("-" * 90)
    proton = next(r for r in results if "trefoil" in r["label"])
    for r in results:
        ratio = r["M_P3_end"] / proton["M_P3_end"] if proton["M_P3_end"] > 0 else 0
        sm_compare = ""
        if "Hopfion" in r["label"] or "antiHopfion" in r["label"]:
            sm_compare = "Delta+/-: 1.3131 (1.65% err)"
        elif "WpWp" in r["label"] or "WmWm" in r["label"]:
            sm_compare = "Delta++/--: 1.3131 (0.68% err)"
        elif "trefoil" in r["label"]:
            sm_compare = "proton: 1.0000 (ref)"
        print(f"{r['label']:<22} {r['M_P3_end']:>10.2f} {ratio:>20.4f} {sm_compare:>20}")
    print("=" * 90)

    # Specific symmetry check
    hopfion = next(r for r in results if r["label"] == "Hopfion_Q1_W+")
    anti_hopfion = next(r for r in results if r["label"] == "antiHopfion_Q1_W-")
    wpwp = next(r for r in results if r["label"] == "WpWp_Delta++")
    wmwm = next(r for r in results if r["label"] == "WmWm_Delta--")

    print()
    print("Chirality symmetry tests:")
    h_diff = abs(hopfion["M_P3_end"] - anti_hopfion["M_P3_end"]) / hopfion["M_P3_end"] * 100
    print(f"  Hopfion ({hopfion['M_P3_end']:.2f}) vs anti-Hopfion ({anti_hopfion['M_P3_end']:.2f})")
    print(f"    Relative difference: {h_diff:.2f}%")
    print(f"    -> Delta- prediction: ratio = {anti_hopfion['M_P3_end']/proton['M_P3_end']:.4f}")
    print(f"    -> SM Delta-/proton: 1.3131")
    delta_err = abs(anti_hopfion['M_P3_end']/proton['M_P3_end'] - 1.3131) / 1.3131 * 100
    print(f"    Identification error: {delta_err:.2f}%")
    print()
    w_diff = abs(wpwp["M_P3_end"] - wmwm["M_P3_end"]) / wpwp["M_P3_end"] * 100
    print(f"  W+W+ ({wpwp['M_P3_end']:.2f}) vs W-W- ({wmwm['M_P3_end']:.2f})")
    print(f"    Relative difference: {w_diff:.2f}%")
    print(f"    -> Delta-- prediction: ratio = {wmwm['M_P3_end']/proton['M_P3_end']:.4f}")
    print(f"    -> SM Delta--/proton: 1.3131")
    delta2_err = abs(wmwm['M_P3_end']/proton['M_P3_end'] - 1.3131) / 1.3131 * 100
    print(f"    Identification error: {delta2_err:.2f}%")

    chirality_holds = h_diff < 1.0 and w_diff < 1.0

    report = {
        "test_id": "QNG-CPU-165",
        "params": {"L": v12.L, "E_CHARGE": v12.E_CHARGE},
        "results": results,
        "chirality_symmetry": {
            "hopfion_vs_anti_diff_pct": h_diff,
            "wpwp_vs_wmwm_diff_pct": w_diff,
            "symmetry_holds": bool(chirality_holds),
        },
        "delta_minus_identification": {
            "anti_hopfion_ratio_to_proton": anti_hopfion["M_P3_end"]/proton["M_P3_end"],
            "sm_delta_minus_ratio": 1.3131,
            "error_pct": delta_err,
        },
        "delta_double_minus_identification": {
            "wmwm_ratio_to_proton": wmwm["M_P3_end"]/proton["M_P3_end"],
            "sm_delta_double_minus_ratio": 1.3131,
            "error_pct": delta2_err,
        },
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
