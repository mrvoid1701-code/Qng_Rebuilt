from __future__ import annotations

"""QNG-CPU-171: Conservative Phase 3 — find equilibrium without dissipation.

CPU-170 found that dissipative Phase 3 doesn't converge even at 30000 lu.
The issue may be that dissipation (Channel A relaxation, CHI_DECAY) drives
the system AWAY from the topological soliton equilibrium toward vacuum.

CPU-171 implements CONSERVATIVE Phase 3:
- Channel A (alpha) turned off
- Channel F (gamma_phi) turned off
- CHI_DECAY turned off
- Only Channel B (neighbor diffusion), Channel G (chi back-reaction),
  and gauge dynamics remain

This should preserve the topological soliton structure formed in
Phase 2 and let us measure the true post-formation mass.

Reference: CPU-066/074 used conservative Phase 3 (no A/F/chi_decay)
for canonical M_ring measurement. Apply same to v12 enhanced.
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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-conservative-equilibrium-v1"


def step_v12_conservative(sg, sm, chi, phi, A_x, A_y, A_z):
    """Conservative v12 step:
    - sigma_g: only Channel B + Channel G (no A, no K_GM)
    - sigma_m: only Channel B (no A, no F)
    - chi: only CHI_REL (no decay, no DELTA)
    - phi: same XY alignment
    - A: same gauge dynamics
    """
    sgb = v12.neighbor_mean(sg)
    smb = v12.neighbor_mean(sm)

    # sigma_g: Channel B + Channel G (NO alpha, no K_GM)
    dsg = v12.BETA * (sgb - sg) + v12.K_BACK * chi
    sg_new = np.clip(sg + dsg, 0.0, 1.0)

    # sigma_m: pure diffusion (NO alpha, NO Channel F)
    dsm = v12.BETA * (smb - sm)
    sm_new = np.clip(sm + dsm, 0.0, 1.0)

    # chi: NO decay, NO DELTA
    chi_new = chi + v12.CHI_REL * (sgb - sg)

    # phi: gauge-invariant XY alignment (same as full step)
    pm = v12.phi_neighbor_xy_weighted_gauge(phi, sm, A_x, A_y, A_z)
    dphi = v12.BETA_PHI * v12.wrap_pi(pm - phi)
    phi_new = v12.wrap_pi(phi + dphi)

    # A: same gauge dynamics as full step
    phi_grad_x = v12.wrap_pi(np.roll(phi, -1, axis=0) - phi - v12.E_CHARGE * A_x)
    phi_grad_y = v12.wrap_pi(np.roll(phi, -1, axis=1) - phi - v12.E_CHARGE * A_y)
    phi_grad_z = v12.wrap_pi(np.roll(phi, -1, axis=2) - phi - v12.E_CHARGE * A_z)

    F_xy = A_x + np.roll(A_y, -1, axis=0) - np.roll(A_x, -1, axis=1) - A_y
    F_yz = A_y + np.roll(A_z, -1, axis=1) - np.roll(A_y, -1, axis=2) - A_z
    F_xz = A_x + np.roll(A_z, -1, axis=0) - np.roll(A_x, -1, axis=2) - A_z

    div_F_at_Ax = (1.0/(2.0*v12.MU_A)) * (
        F_xy - np.roll(F_xy, +1, axis=1)
      + F_xz - np.roll(F_xz, +1, axis=2)
    )
    div_F_at_Ay = (1.0/(2.0*v12.MU_A)) * (
      - F_xy + np.roll(F_xy, +1, axis=0)
      + F_yz - np.roll(F_yz, +1, axis=2)
    )
    div_F_at_Az = (1.0/(2.0*v12.MU_A)) * (
      - F_yz + np.roll(F_yz, +1, axis=1)
      - F_xz + np.roll(F_xz, +1, axis=0)
    )

    phi_coupling_x = (v12.E_CHARGE * v12.BETA_PHI / (2.0 * 6)) * np.sin(phi_grad_x)
    phi_coupling_y = (v12.E_CHARGE * v12.BETA_PHI / (2.0 * 6)) * np.sin(phi_grad_y)
    phi_coupling_z = (v12.E_CHARGE * v12.BETA_PHI / (2.0 * 6)) * np.sin(phi_grad_z)

    A_x_new = A_x - v12.BETA_A * (phi_coupling_x + div_F_at_Ax)
    A_y_new = A_y - v12.BETA_A * (phi_coupling_y + div_F_at_Ay)
    A_z_new = A_z - v12.BETA_A * (phi_coupling_z + div_F_at_Az)

    return sg_new, sm_new, chi_new, phi_new, A_x_new, A_y_new, A_z_new


def run_with_conservative_p3(label, init_fn, p3_steps=5000, log_every=500):
    L = v12.L
    sg  = np.full((L, L, L), v12.SIGMA_REF)
    sm  = np.full((L, L, L), v12.SIGMA_REF)
    chi = np.zeros((L, L, L))
    phi = init_fn()
    A_x = np.zeros((L, L, L))
    A_y = np.zeros((L, L, L))
    A_z = np.zeros((L, L, L))

    # Phase 1 (full v12 dissipative, no F)
    print(f"  [{label}] Phase 1 (300 lu, dissipative, no F)...", flush=True)
    for t in range(v12.PHASE1):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=False)

    # Phase 2 (full v12 dissipative WITH F to form structure)
    print(f"  [{label}] Phase 2 (1500 lu, dissipative + F)...", flush=True)
    for t in range(v12.PHASE2):
        sg, sm, chi, phi, A_x, A_y, A_z = v12.step_v12(
            sg, sm, chi, phi, A_x, A_y, A_z, channel_f_active=True)

    M_P2_end = v12.ring_mass(sm)
    print(f"  [{label}] P2 end: M={M_P2_end:.2f}", flush=True)

    # Phase 3 CONSERVATIVE (no A, no F, no chi_decay)
    print(f"  [{label}] Phase 3 conservative ({p3_steps} lu)...", flush=True)
    trajectory = [(0, M_P2_end)]
    last_print = time.time()
    for t in range(1, p3_steps + 1):
        sg, sm, chi, phi, A_x, A_y, A_z = step_v12_conservative(
            sg, sm, chi, phi, A_x, A_y, A_z)
        if t % log_every == 0:
            M = v12.ring_mass(sm)
            trajectory.append((t, M))
            if time.time() - last_print > 3.0:
                print(f"    [{label}] t={t} M={M:.2f}", flush=True)
                last_print = time.time()

    return {
        "label": label,
        "M_P2_end": M_P2_end,
        "trajectory": trajectory,
        "M_final": trajectory[-1][1],
        "M_min": min(m for _, m in trajectory),
        "M_max": max(m for _, m in trajectory),
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--p3-steps", type=int, default=5000)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    v12.E_CHARGE = 3.0
    v12.MU_A = 1.0
    v12.BETA_A = 0.05

    print(f"QNG-CPU-171: Conservative Phase 3 — find true equilibrium")
    print(f"L={v12.L} e={v12.E_CHARGE}  conservative P3={args.p3_steps} lu")
    print()

    configs = [
        ("trefoil_proton", lambda: v12.init_phi_from_knot(v12.trefoil_curve)),
        ("Hopfion_Q1",     lambda: v12.init_phi_hopfion(1)),
        ("WpWp",           lambda: init_phi_two_W_plus(6)),
        ("WmWm",           lambda: init_phi_W_minus_pair(6)),
    ]

    results = []
    t_start = time.time()
    for label, init_fn in configs:
        print(f"=== {label} ===")
        res = run_with_conservative_p3(label, init_fn, args.p3_steps)
        results.append(res)
        print(f"  [{label}] P2_end={res['M_P2_end']:.0f}  "
              f"P3_min={res['M_min']:.0f}  P3_max={res['M_max']:.0f}  "
              f"P3_final={res['M_final']:.0f}")
        # Check stability
        traj = res["trajectory"]
        last_5 = traj[-5:]
        last_vals = [m for _, m in last_5]
        rel_var = (max(last_vals) - min(last_vals)) / max(1.0, np.mean(last_vals)) * 100
        res["last_5_rel_variation_pct"] = rel_var
        print(f"  [{label}] last 5 checkpoints relative variation: {rel_var:.2f}%")
        print()
    dt = time.time() - t_start
    print(f"Total: {dt:.1f}s")
    print()

    # SM ID using conservative-equilibrium masses
    trefoil = next(r for r in results if "trefoil" in r["label"])
    print()
    print("=" * 80)
    print(f"{'Config':<20} {'M_final':>10} {'ratio':>10} {'pred MeV':>10} {'vs SM':>15}")
    print("-" * 80)
    sm_targets = {
        "Hopfion_Q1": ("Delta+", 1232.0),
        "WpWp": ("Delta++", 1232.0),
        "WmWm": ("Delta--", 1232.0),
    }
    for r in results:
        ratio = r["M_final"] / trefoil["M_final"]
        m_pred = ratio * 938.27
        if r["label"] in sm_targets:
            sm_name, sm_mass = sm_targets[r["label"]]
            err = (m_pred - sm_mass) / sm_mass * 100
            sm_str = f"{sm_name} ({err:+.2f}%)"
        else:
            sm_str = "(ref)" if "trefoil" in r["label"] else "?"
        print(f"{r['label']:<20} {r['M_final']:>10.0f} {ratio:>10.4f} "
              f"{m_pred:>10.1f} {sm_str:>15}")
    print("=" * 80)

    report = {
        "test_id": "QNG-CPU-171_conservative_equilibrium",
        "params": {"L": v12.L, "p3_conservative_steps": args.p3_steps,
                   "E_CHARGE": v12.E_CHARGE},
        "results": results,
        "trefoil_conservative_M": trefoil["M_final"],
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
