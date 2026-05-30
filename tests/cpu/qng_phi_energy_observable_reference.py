from __future__ import annotations

"""QNG-CPU-172: Use phi-XY energy as identification observable.

DER-QNG-096 identified that M_ring (matter depletion) is not a
well-defined equilibrium observable under v12 enhanced dynamics.

This test introduces an ALTERNATIVE observable: the phi-XY coupling
energy E_phi = -(beta_phi/(2z)) sum cos(phi_i - phi_j - e*A_ij).

Hypothesis: E_phi is closer to a Hamiltonian-like quantity and may
be more stable across protocols than M_ring.

We compute E_phi at multiple time checkpoints (1500, 3000, 5000, 7500
lu after Phase 2 end) for the 4 key configs and report:
- E_phi at each checkpoint
- E_phi - E_vacuum (= topological energy = mass candidate)
- Stability of ratios across checkpoints

If ratios stabilize, this is the right observable.

Reference: DER-QNG-096, Paper 7 §4 revision.
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-phi-energy-observable-v1"


def phi_xy_energy_gauge_invariant(phi, A_x, A_y, A_z):
    """E_phi_v12 = -(beta_phi/(2z)) * sum_<ij> cos(phi_i - phi_j - e*A_ij).

    Sum over edges (each counted once: +x, +y, +z direction per node).
    """
    e = v12.E_CHARGE
    cos_x = np.cos(np.roll(phi, -1, axis=0) - phi - e * A_x)
    cos_y = np.cos(np.roll(phi, -1, axis=1) - phi - e * A_y)
    cos_z = np.cos(np.roll(phi, -1, axis=2) - phi - e * A_z)
    total = float(cos_x.sum() + cos_y.sum() + cos_z.sum())
    return -(v12.BETA_PHI / 6.0) * total  # 6 = 2*z, but we sum 3 edges/node


def E_phi_vacuum():
    """Vacuum: phi = constant, A = 0. E = -(BETA_PHI/6) * 3N (since 3 edges/node)."""
    L = v12.L
    N = L * L * L
    return -(v12.BETA_PHI / 6.0) * 3 * N * 1.0  # cos(0)=1


def run_with_phi_energy_tracking(label, init_fn,
                                  checkpoints_lu=(1500, 3000, 5000, 7500)):
    L = v12.L
    sg  = np.full((L, L, L), v12.SIGMA_REF)
    sm  = np.full((L, L, L), v12.SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_fn()
    A_x = np.zeros((L, L, L))
    A_y = np.zeros((L, L, L))
    A_z = np.zeros((L, L, L))

    snapshots = []

    # Phase 1
    for t in range(v12.PHASE1):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=False)
    snapshots.append({
        "t": v12.PHASE1, "phase": "P1_end",
        "M_ring": v12.ring_mass(sm),
        "E_phi": phi_xy_energy_gauge_invariant(phi, A_x, A_y, A_z),
    })

    # Phase 2
    for t in range(v12.PHASE2):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True)
    snapshots.append({
        "t": v12.PHASE1 + v12.PHASE2, "phase": "P2_end",
        "M_ring": v12.ring_mass(sm),
        "E_phi": phi_xy_energy_gauge_invariant(phi, A_x, A_y, A_z),
    })

    # Phase 3: track at multiple checkpoints
    t_current = 0
    for target_t in checkpoints_lu:
        while t_current < target_t:
            sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
                sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True)
            t_current += 1
        snapshots.append({
            "t": v12.PHASE1 + v12.PHASE2 + t_current,
            "phase": f"P3_t{target_t}",
            "M_ring": v12.ring_mass(sm),
            "E_phi": phi_xy_energy_gauge_invariant(phi, A_x, A_y, A_z),
        })

    return snapshots


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

    E_vac = E_phi_vacuum()
    print(f"QNG-CPU-172: E_phi observable for identification")
    print(f"L={v12.L} e={v12.E_CHARGE}")
    print(f"Vacuum E_phi = {E_vac:.4f}")
    print()

    configs = [
        ("trefoil_proton", lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
        ("Hopfion_Q1",     lambda: v12.init_phi_hopfion(1)),
        ("WpWp",           lambda: init_phi_two_W_plus(6)),
        ("WmWm",           lambda: init_phi_W_minus_pair(6)),
    ]

    all_snapshots = {}
    t_start = time.time()
    for label, init_fn in configs:
        print(f"=== {label} ===", flush=True)
        snapshots = run_with_phi_energy_tracking(label, init_fn)
        all_snapshots[label] = snapshots
        print(f"  Checkpoints (E_phi, dE = E - E_vac, M_ring):")
        for s in snapshots:
            dE = s["E_phi"] - E_vac
            print(f"    {s['phase']:<10} t={s['t']:>5}  "
                  f"E_phi={s['E_phi']:.4f}  dE={dE:.4f}  "
                  f"M_ring={s['M_ring']:.2f}")
        print()
    dt = time.time() - t_start
    print(f"Total: {dt:.1f}s")
    print()

    # Analysis: compute dE at each checkpoint and see if ratios are stable
    print("=" * 100)
    print("dE = E_phi - E_vacuum (mass candidate) per config across time")
    print("=" * 100)
    phases = ["P1_end", "P2_end", "P3_t1500", "P3_t3000", "P3_t5000", "P3_t7500"]
    print(f"{'Phase':<12} " + " ".join(f"{l:>14}" for l in [c[0] for c in configs]))
    print("-" * 100)
    for ph in phases:
        row = [ph]
        for c_label, _ in configs:
            snapshots = all_snapshots[c_label]
            s = next((x for x in snapshots if x["phase"] == ph), None)
            if s:
                row.append(f"{s['E_phi'] - E_vac:>14.3f}")
            else:
                row.append(f"{'-':>14}")
        print(f"{row[0]:<12} " + " ".join(row[1:]))
    print("=" * 100)

    # Ratios at each checkpoint
    print()
    print("Ratios vs trefoil (= proton candidate):")
    print(f"{'Phase':<12} " + " ".join(f"{l:>14}" for l in [c[0] for c in configs]))
    print("-" * 100)
    for ph in phases:
        row = [ph]
        trefoil_dE = None
        for c_label, _ in configs:
            snapshots = all_snapshots[c_label]
            s = next((x for x in snapshots if x["phase"] == ph), None)
            if s:
                dE = s["E_phi"] - E_vac
                if c_label == "trefoil_proton":
                    trefoil_dE = dE
                    row.append(f"{1.0000:>14.4f}")
                elif trefoil_dE and trefoil_dE > 0:
                    row.append(f"{dE / trefoil_dE:>14.4f}")
                else:
                    row.append(f"{'-':>14}")
            else:
                row.append(f"{'-':>14}")
        print(f"{row[0]:<12} " + " ".join(row[1:]))
    print()

    # SM identification using P3_t7500 ratios
    print("SM identification using E_phi ratios at P3 t=7500:")
    trefoil_dE_final = next(s["E_phi"] - E_vac for s in all_snapshots["trefoil_proton"]
                            if s["phase"] == "P3_t7500")
    sm_targets = {
        "Hopfion_Q1": ("Delta+", 1232.0),
        "WpWp": ("Delta++", 1232.0),
        "WmWm": ("Delta--", 1232.0),
    }
    for c_label, _ in configs:
        if c_label not in sm_targets:
            continue
        sm_name, sm_mass = sm_targets[c_label]
        s = next(x for x in all_snapshots[c_label] if x["phase"] == "P3_t7500")
        dE = s["E_phi"] - E_vac
        ratio = dE / trefoil_dE_final if trefoil_dE_final > 0 else 0
        m_pred = ratio * 938.27
        err = (m_pred - sm_mass) / sm_mass * 100
        print(f"  {c_label}: dE_ratio={ratio:.4f}  pred={m_pred:.1f} MeV  "
              f"vs {sm_name} ({sm_mass}): err={err:+.2f}%")

    report = {
        "test_id": "QNG-CPU-172_phi_energy_observable",
        "params": {"L": v12.L, "E_CHARGE": v12.E_CHARGE,
                   "BETA_PHI": v12.BETA_PHI},
        "E_phi_vacuum": E_vac,
        "all_snapshots": {k: v for k, v in all_snapshots.items()},
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
