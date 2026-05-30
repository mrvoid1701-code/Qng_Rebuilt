from __future__ import annotations

"""QNG-CPU-170: Ultra-long Phase 3 to find true equilibrium masses.

CPU-169 stress test showed M_ring at Phase 3 = 6000 lu is significantly
LOWER than at 3000 lu. The masses are still relaxing/oscillating at 6000 lu.

CPU-170 runs Phase 3 = 30000 lu (10x original) with checkpoints every
1000 lu to characterize the full decay trajectory and identify the
asymptotic equilibrium value.

Configurations tested:
- trefoil (proton reference)
- Hopfion Q1 (Delta+ candidate)
- W+W+ composite (Delta++ candidate)
- W-W- composite (Delta-- candidate, best at 3000 lu)

Output: M_ring(t) trajectory for each config, asymptote extraction.
"""

import json
import math
import time
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
import qng_v12_dynamics_reference as v12
from qng_neutron_composite_reference import init_phi_two_W_plus
from qng_chirality_verification_reference import init_phi_W_minus_pair


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equilibrium-hunt-v1"


def run_with_long_tracking(label, init_fn, total_p3=30000, log_every=1000):
    """Run v12 dynamics with PHASE 3 extended to total_p3 lu.
    Track M_ring at every log_every steps for full trajectory.
    """
    L = v12.L
    sg  = np.full((L, L, L), v12.SIGMA_REF)
    sm  = np.full((L, L, L), v12.SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_fn()
    A_x = np.zeros((L, L, L))
    A_y = np.zeros((L, L, L))
    A_z = np.zeros((L, L, L))

    history = []

    def snap(t, phase):
        return {
            "t": t, "phase": phase,
            "M_ring": v12.ring_mass(sm),
            "E_gauge": v12.E_gauge_total(A_x, A_y, A_z),
        }

    print(f"  [{label}] Phase 1 (300 lu)...", flush=True)
    history.append(snap(0, "init"))
    for t in range(1, v12.PHASE1 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=False)
    history.append(snap(v12.PHASE1, "P1_end"))

    print(f"  [{label}] Phase 2 (1500 lu)...", flush=True)
    for t in range(1, v12.PHASE2 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True)
        if t % log_every == 0 or t == v12.PHASE2:
            history.append(snap(v12.PHASE1 + t, "P2"))

    print(f"  [{label}] Phase 3 extended ({total_p3} lu)...", flush=True)
    last_print = time.time()
    for t in range(1, total_p3 + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True)
        if t % log_every == 0:
            snap_data = snap(v12.PHASE1 + v12.PHASE2 + t, "P3")
            history.append(snap_data)
            # Throttle prints
            if time.time() - last_print > 3.0:
                print(f"    [{label}] t={t} M={snap_data['M_ring']:.2f}",
                      flush=True)
                last_print = time.time()

    return history


def analyze_trajectory(history, label):
    """Extract asymptotic mass from trajectory."""
    p3_records = [h for h in history if h["phase"] == "P3"]
    if len(p3_records) < 5:
        return {"label": label, "asymptote": None, "data_points": len(p3_records)}

    masses = [h["M_ring"] for h in p3_records]
    times = [h["t"] for h in p3_records]

    # Take the last 25% of data for asymptote estimate
    n_last = max(5, len(masses) // 4)
    asymptote = float(np.mean(masses[-n_last:]))
    asymptote_std = float(np.std(masses[-n_last:]))

    # Convergence check: relative change in last quarter vs middle quarter
    n_mid = len(masses) // 4
    mid_mean = float(np.mean(masses[n_mid:2*n_mid]))
    rel_change = abs(asymptote - mid_mean) / max(1.0, mid_mean) * 100

    return {
        "label": label,
        "asymptote": asymptote,
        "asymptote_std": asymptote_std,
        "n_p3_points": len(masses),
        "first_M": masses[0],
        "peak_M": max(masses),
        "min_M": min(masses),
        "rel_change_mid_to_end_pct": rel_change,
        "trajectory": [(h["t"], h["M_ring"]) for h in p3_records],
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--total-p3", type=int, default=30000,
                    help="Phase 3 total duration in lu")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    v12.E_CHARGE = 3.0
    v12.MU_A = 1.0
    v12.BETA_A = 0.05

    print(f"QNG-CPU-170: Ultra-long Phase 3 equilibrium hunt")
    print(f"L={v12.L} e={v12.E_CHARGE} PHASE3={args.total_p3} lu")
    print()

    configs = [
        ("trefoil_proton", lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
        ("Hopfion_Q1",     lambda: v12.init_phi_hopfion(1)),
        ("WpWp",           lambda: init_phi_two_W_plus(6)),
        ("WmWm",           lambda: init_phi_W_minus_pair(6)),
    ]

    analyses = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"=== {label} ===")
        history = run_with_long_tracking(label, init_fn, total_p3=args.total_p3)
        analysis = analyze_trajectory(history, label)
        analyses.append(analysis)
        print(f"  [{label}] peak={analysis['peak_M']:.0f}  "
              f"min={analysis['min_M']:.0f}  "
              f"asymptote={analysis['asymptote']:.0f} +/- {analysis['asymptote_std']:.0f}  "
              f"rel_change(mid->end)={analysis['rel_change_mid_to_end_pct']:.2f}%")
        print()
    dt = time.time() - t_start
    print(f"Total time: {dt:.1f}s")
    print()

    # Trajectory analysis
    print("=" * 90)
    print(f"{'Config':<20} {'Peak M':>10} {'Min M':>10} "
          f"{'Asymp.':>10} {'std':>8} {'Conv?':>8}")
    print("-" * 90)
    for a in analyses:
        conv = "YES" if a['rel_change_mid_to_end_pct'] < 5 else "NO"
        print(f"{a['label']:<20} {a['peak_M']:>10.0f} {a['min_M']:>10.0f} "
              f"{a['asymptote']:>10.0f} {a['asymptote_std']:>8.0f} {conv:>8}")
    print("=" * 90)

    # SM identification with TRUE equilibrium
    trefoil_asymp = next(a["asymptote"] for a in analyses if "trefoil" in a["label"])
    print()
    print(f"SM identifications using asymptotic (PHASE3={args.total_p3}) mass ratios:")
    print(f"  trefoil asymptote = {trefoil_asymp:.0f} (proton ref, 938.27 MeV)")
    print()
    sm_targets = [
        ("Hopfion_Q1", "Delta+", 1232.0),
        ("WpWp", "Delta++", 1232.0),
        ("WmWm", "Delta--", 1232.0),
    ]
    for q_label, sm_name, sm_mass in sm_targets:
        a = next(x for x in analyses if x["label"] == q_label)
        ratio = a["asymptote"] / trefoil_asymp
        m_pred = ratio * 938.27
        err = (m_pred - sm_mass) / sm_mass * 100
        print(f"  {q_label} -> {sm_name}: ratio={ratio:.4f}, "
              f"pred={m_pred:.1f} MeV, target={sm_mass:.1f}, err={err:+.2f}%")

    report = {
        "test_id": "QNG-CPU-170_equilibrium_hunt",
        "params": {"L": v12.L, "TOTAL_P3": args.total_p3, "E_CHARGE": v12.E_CHARGE},
        "analyses": analyses,
        "trefoil_asymptote_substrate_units": trefoil_asymp,
        "proton_reference_MeV": 938.27,
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
