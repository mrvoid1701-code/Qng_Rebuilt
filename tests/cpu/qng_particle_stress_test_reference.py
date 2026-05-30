from __future__ import annotations

"""QNG-CPU-169: Stress test all 8 identified particles.

Test robustness of QNG-SM identifications under:
A. Longer Phase 3 (6000 lu vs original 3000) — check equilibrium
B. Compare masses at multiple checkpoints during P3 to verify convergence

If identifications are STABLE under longer evolution, they are robust.
If masses shift significantly, the original 3000-lu values may have been
non-equilibrium and the identification errors may change.

Reference: All DER-QNG-093/094 identifications.
"""

import json
import math
import time
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
import qng_v12_dynamics_reference as v12
from qng_neutron_composite_reference import init_phi_W_plus_minus, init_phi_two_W_plus
from qng_chirality_verification_reference import init_phi_anti_hopfion, init_phi_W_minus_pair
from qng_more_particles_reference import (init_phi_anti_trefoil, init_phi_3rings)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-particle-stress-test-v1"


# Extended Phase 3 for stress test
v12.PHASE3 = 6000


def init_phi_WpWmWp_layered():
    return init_phi_3rings(separation=3, charges=(+1, -1, +1))


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

    print(f"QNG-CPU-169: Stress test all identifications")
    print(f"L={v12.L} e={v12.E_CHARGE} PHASE3={v12.PHASE3} (2x longer)")
    print()

    # All 8 identifications + comparison to baseline 3000-lu values
    # Format: (label, init_fn, baseline_M_at_3000, predicted_SM, sm_mass_MeV)
    configs = [
        ("trefoil_proton",      lambda: v12.init_phi_from_knot(v12.trefoil_curve),
         1902.16, "proton", 938.27),
        ("anti_trefoil_pbar",   lambda: init_phi_anti_trefoil(),
         1902.16, "antiproton", 938.27),
        ("Hopfion_Q1_Delta+",   lambda: v12.init_phi_hopfion(1),
         2456.50, "Delta+", 1232.0),
        ("anti_Hopfion_Q1_Delta-", lambda: init_phi_anti_hopfion(1),
         2456.50, "Delta-", 1232.0),
        ("W+W+_Delta++",        lambda: init_phi_two_W_plus(6),
         2515.27, "Delta++", 1232.0),
        ("W-W-_Delta--",        lambda: init_phi_W_minus_pair(6),
         2505.33, "Delta--", 1232.0),
        ("W+W-_D10_neutron",    lambda: init_phi_W_plus_minus(10),
         1900.73, "neutron", 939.57),
        ("WpWmWp_layered_a0",   lambda: init_phi_WpWmWp_layered(),
         1991.46, "a0(980)+", 980.0),
    ]

    results = []
    t_start = time.time()
    for label, init_fn, baseline, sm_name, sm_mass in configs:
        print(f"--- {label} ---", flush=True)
        res = v12.run_v12(label, init_fn)
        m_p3_6000 = res["M_P3_end"]
        shift_pct = (m_p3_6000 - baseline) / baseline * 100 if baseline > 0 else 0

        res["baseline_3000"] = baseline
        res["M_at_6000"] = m_p3_6000
        res["shift_from_baseline_pct"] = shift_pct
        res["sm_name"] = sm_name
        res["sm_mass_MeV"] = sm_mass

        # Update QNG-SM error after stress (we need TROEFOIL stress to be the
        # proton reference, so first config establishes it)
        if label == "trefoil_proton":
            proton_baseline_stress = m_p3_6000
        # use original CPU-159 reference until trefoil stress completes
        proton_ref = proton_baseline_stress if 'proton_baseline_stress' in dir() else 1902.16
        ratio_stress = m_p3_6000 / proton_ref
        m_pred_stress = ratio_stress * 938.27
        err_stress = (m_pred_stress - sm_mass) / sm_mass * 100
        res["mass_error_stress_pct"] = err_stress

        results.append(res)
        print(f"  [{label}] M_at_6000={m_p3_6000:.2f}  baseline={baseline:.2f}  "
              f"shift={shift_pct:+.2f}%  stress_err vs SM={err_stress:+.2f}%",
              flush=True)
        print()
    dt = time.time() - t_start
    print(f"Total stress test time: {dt:.1f} s")
    print()

    # Comprehensive comparison
    print("=" * 110)
    print(f"{'QNG label':<22} {'SM':<12} {'baseline':>9} {'M(6000)':>10} "
          f"{'shift %':>8} {'err vs SM %':>11} {'verdict':>10}")
    print("-" * 110)
    for r in results:
        if abs(r["shift_from_baseline_pct"]) < 2.0:
            verdict = "STABLE"
        elif abs(r["shift_from_baseline_pct"]) < 5.0:
            verdict = "SLIGHT"
        else:
            verdict = "SHIFTED"
        print(f"{r['label']:<22} {r['sm_name']:<12} {r['baseline_3000']:>9.2f} "
              f"{r['M_at_6000']:>10.2f} {r['shift_from_baseline_pct']:>+8.2f} "
              f"{r['mass_error_stress_pct']:>+11.2f} {verdict:>10}")
    print("=" * 110)

    n_stable = sum(1 for r in results if abs(r["shift_from_baseline_pct"]) < 2.0)
    n_slight = sum(1 for r in results if 2.0 <= abs(r["shift_from_baseline_pct"]) < 5.0)
    n_shifted = sum(1 for r in results if abs(r["shift_from_baseline_pct"]) >= 5.0)

    print()
    print(f"Robustness summary:")
    print(f"  STABLE (shift < 2%): {n_stable} / {len(results)}")
    print(f"  SLIGHT (shift 2-5%): {n_slight} / {len(results)}")
    print(f"  SHIFTED (shift > 5%): {n_shifted} / {len(results)}")

    # Final identification summary
    print()
    print("=" * 80)
    print("FINAL IDENTIFICATIONS AFTER STRESS TEST")
    print("=" * 80)
    print(f"{'SM particle':<15} {'QNG structure':<25} {'Final mass err %':>18}")
    print("-" * 80)
    for r in results:
        print(f"{r['sm_name']:<15} {r['label']:<25} "
              f"{r['mass_error_stress_pct']:>+18.2f}")
    print("=" * 80)
    n_clean = sum(1 for r in results if abs(r["mass_error_stress_pct"]) < 2.0)
    print(f"\nClean identifications (error < 2%): {n_clean} of {len(results)}")

    report = {
        "test_id": "QNG-CPU-169_stress_test",
        "params": {"L": v12.L, "PHASE3": v12.PHASE3, "E_CHARGE": v12.E_CHARGE},
        "n_configs_tested": len(results),
        "n_stable_under_long_run": n_stable,
        "n_slight_shift": n_slight,
        "n_significantly_shifted": n_shifted,
        "n_clean_identifications_after_stress": n_clean,
        "results": [{k: v for k, v in r.items() if k != "history"}
                    for r in results],
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
