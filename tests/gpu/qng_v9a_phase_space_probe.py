"""QNG-GPU-100: V9-A phase-space probe.

Re-runs GPU-031f (R=4, T_P2=5000 lu) across R in {3, 4, 5} with full
(sigma_m, pi_m, phi, pi_phi) checkpointing at 10-lu intervals plus
reduced observables (M_ring, P_M, COM, R_eff, H-components) at 1-lu
intervals. Output consumed by CPU-098 for V9-A Berry-integral verdict.

Protocol (per R, same as GPU-031f):
  Phase 1: T_P1=300 lu, v_couple=False
  Phase 2: T_P2=5000 lu, v_couple=True

Fixed: L=20, DT=0.025, exact_a='r1' (DER-QNG-051 pure-XY),
CHI_DECAY_V7=0.020, K_BACK=0.10. Parameters imported from
qng_v8_canonical_gpu.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (  # noqa: E402
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    SIGMA_M_REF, CHI_DECAY_V7,
)

EXACT_A_MODE = 'r1'
RING_THRESH = 500.0

# Output settings
M_SAMPLE_EVERY_LU = 1.0   # reduced observables cadence
SNAP_EVERY_LU = 10.0       # full-field snapshot cadence


def centered_coords_np(L):
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - L / 2.0
    dy = yg - L / 2.0
    dz = zg - L / 2.0
    for d in (dx, dy, dz):
        d[:] = np.where(d >  L / 2, d - L, d)
        d[:] = np.where(d < -L / 2, d + L, d)
    return dx.ravel(), dy.ravel(), dz.ravel()


def reduced_observables(state, nb_idx, dx, dy, dz, channel_f, exact_a):
    """Compute scalar reductions on current state (cheap, every 1 lu)."""
    sm = state['sm']
    pi_m = state['pi_m']
    # M_ring = N*sigma_ref - sum(sigma_m)
    M = float(SIGMA_M_REF * sm.size - cp.sum(sm))
    # P_M = -(1/N) sum pi_m — conjugate zero-mode of sum(sigma_m)
    # (since dM/dt = -sum(dsm/dt) = -sum(pi_m/mu_m), the canonical pair
    #  (Q, P) with Q = sum(sigma_m), P = (1/N)sum(pi_m) yields
    #  Q_dot = P*N/mu_m => P_M_canonical definition below)
    P_M = float(-cp.sum(pi_m) / sm.size)
    # Deficit-weighted COM of sigma_m (mass-weighted position of the deficit)
    deficit = cp.maximum(SIGMA_M_REF - sm, 0.0)
    w_tot = float(cp.sum(deficit))
    if w_tot > 1e-10:
        COM_x = float(cp.sum(cp.asarray(dx) * deficit)) / w_tot
        COM_y = float(cp.sum(cp.asarray(dy) * deficit)) / w_tot
        COM_z = float(cp.sum(cp.asarray(dz) * deficit)) / w_tot
        # Effective radius: sqrt(<r^2>_deficit)
        r2 = cp.asarray(dx) ** 2 + cp.asarray(dy) ** 2 + cp.asarray(dz) ** 2
        R_eff = float(cp.sqrt(cp.sum(r2 * deficit) / w_tot))
    else:
        COM_x = COM_y = COM_z = 0.0
        R_eff = 0.0
    # Full Hamiltonian (canonical — pass k_gm=0.0)
    H = hamiltonian_v8(state, nb_idx, channel_f=channel_f,
                       k_gm=0.0, exact_a=exact_a)
    return {'M': M, 'P_M': P_M,
            'COM_x': COM_x, 'COM_y': COM_y, 'COM_z': COM_z,
            'R_eff': R_eff, 'H': H}


def run_R(R, L, DT, n1, n2, m_sample_step, snap_step, outdir, verbose=True):
    """Run Phase 1 + Phase 2 at given R with phase-space checkpointing."""
    t0 = time.time()
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    dx, dy, dz = centered_coords_np(L)

    # --- Phase 1 (no V_couple) ---
    print(f"\n  [R={R}] Phase 1: n1={n1} steps (T_P1={n1*DT} lu)", flush=True)
    for s in range(1, n1 + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=False,
                              chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
    M_p1 = float(SIGMA_M_REF * state['sm'].size - cp.sum(state['sm']))
    print(f"  [R={R}] end P1: M_ring={M_p1:+.3f}", flush=True)

    # --- Phase 2 (V_couple on) ---
    print(f"  [R={R}] Phase 2: n2={n2} steps (T_P2={n2*DT} lu)", flush=True)
    t_red = []
    red_M = []; red_PM = []
    red_COMx = []; red_COMy = []; red_COMz = []
    red_Reff = []; red_H = []

    # Snapshot arrays — pre-allocate
    n_snap = n2 // snap_step
    N_sites = L * L * L
    sm_stack = np.empty((n_snap, N_sites), dtype=np.float32)
    pim_stack = np.empty((n_snap, N_sites), dtype=np.float32)
    phi_stack = np.empty((n_snap, N_sites), dtype=np.float32)
    piphi_stack = np.empty((n_snap, N_sites), dtype=np.float32)
    t_snap = np.empty(n_snap, dtype=np.float64)
    snap_idx = 0

    wall_last = time.time()
    for s in range(1, n2 + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=True,
                              chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        # Reduced observables
        if s % m_sample_step == 0:
            t_phys = s * DT
            obs = reduced_observables(state, nb_idx, dx, dy, dz,
                                      channel_f=True, exact_a=EXACT_A_MODE)
            t_red.append(t_phys)
            red_M.append(obs['M']); red_PM.append(obs['P_M'])
            red_COMx.append(obs['COM_x']); red_COMy.append(obs['COM_y'])
            red_COMz.append(obs['COM_z'])
            red_Reff.append(obs['R_eff']); red_H.append(obs['H'])
        # Snapshot (full fields)
        if s % snap_step == 0 and snap_idx < n_snap:
            t_snap[snap_idx] = s * DT
            sm_stack[snap_idx]    = cp.asnumpy(state['sm']).astype(np.float32)
            pim_stack[snap_idx]   = cp.asnumpy(state['pi_m']).astype(np.float32)
            phi_stack[snap_idx]   = cp.asnumpy(state['phi']).astype(np.float32)
            piphi_stack[snap_idx] = cp.asnumpy(state['pi_phi']).astype(np.float32)
            snap_idx += 1
            # Progress every 100 snapshots (=1000 lu)
            if snap_idx % 100 == 0:
                wall_now = time.time()
                dwall = wall_now - wall_last
                wall_last = wall_now
                print(f"  [R={R}] snap {snap_idx}/{n_snap}  "
                      f"t={s*DT:.1f} lu  M={red_M[-1]:+.2f}  "
                      f"H={red_H[-1]:+.2f}  dwall={dwall:.1f}s",
                      flush=True)

    t_red = np.asarray(t_red)
    red_M = np.asarray(red_M); red_PM = np.asarray(red_PM)
    red_COMx = np.asarray(red_COMx); red_COMy = np.asarray(red_COMy)
    red_COMz = np.asarray(red_COMz)
    red_Reff = np.asarray(red_Reff); red_H = np.asarray(red_H)

    # Trim stacks to actual filled length
    sm_stack = sm_stack[:snap_idx]
    pim_stack = pim_stack[:snap_idx]
    phi_stack = phi_stack[:snap_idx]
    piphi_stack = piphi_stack[:snap_idx]
    t_snap = t_snap[:snap_idx]

    # Save artifacts
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(outdir / "reduced_series.npz",
                        t=t_red, M_ring=red_M, P_M=red_PM,
                        COM_x=red_COMx, COM_y=red_COMy, COM_z=red_COMz,
                        R_eff=red_Reff, H=red_H)
    np.savez_compressed(outdir / "snapshots.npz",
                        t_snap=t_snap,
                        sm=sm_stack, pi_m=pim_stack,
                        phi=phi_stack, pi_phi=piphi_stack)
    np.savez_compressed(outdir / "final_state.npz",
                        sg=cp.asnumpy(state['sg']),
                        sm=cp.asnumpy(state['sm']),
                        chi=cp.asnumpy(state['chi']),
                        phi=cp.asnumpy(state['phi']),
                        pi_m=cp.asnumpy(state['pi_m']),
                        pi_phi=cp.asnumpy(state['pi_phi']))

    # Quick orbital stats
    half = len(red_M) // 2
    mean_1h = float(np.mean(red_M[:half])) if half > 0 else 0.0
    mean_2h = float(np.mean(red_M[half:])) if half > 0 else 0.0
    mean_all = float(np.mean(red_M))
    std_all = float(np.std(red_M))
    conv_rel = (abs(mean_2h - mean_1h) / max(abs(mean_all), 1e-10)
                if mean_all != 0 else 0.0)
    duty = float(np.mean(red_M > RING_THRESH))
    H_min = float(np.min(red_H)); H_max = float(np.max(red_H))
    H_mean = float(np.mean(red_H))
    H_drift = (H_max - H_min) / max(abs(H_mean), 1e-10)
    wall = time.time() - t0

    report = {
        'R': R, 'L': L, 'DT': DT, 'T_P1': n1 * DT, 'T_P2': n2 * DT,
        'exact_a_mode': EXACT_A_MODE,
        'n_snapshots': int(snap_idx),
        'n_reduced_samples': int(len(red_M)),
        'final_M_ring': float(red_M[-1]) if len(red_M) > 0 else 0.0,
        'mean_M_first_half': mean_1h,
        'mean_M_second_half': mean_2h,
        'mean_M_all': mean_all,
        'std_M_all': std_all,
        'convergence_rel': conv_rel,
        'duty_cycle_ring': duty,
        'H_mean': H_mean, 'H_drift_peak_to_peak': H_drift,
        'wall_s': wall,
    }
    with open(outdir / "report.json", 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  [R={R}] DONE  wall={wall/60:.1f} min  "
          f"<M>={mean_all:+.2f}  duty={duty:.1%}  "
          f"H_drift={H_drift:.2%}", flush=True)
    return report


def main():
    print("=" * 80)
    print("QNG-GPU-100: V9-A phase-space probe  (R in {3,4,5}, T_P2=5000 lu)")
    print("=" * 80)

    L = 20
    T_P1 = 300.0
    T_P2 = 5000.0
    DT = 0.025
    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    m_sample_step = int(M_SAMPLE_EVERY_LU / DT)   # every 1 lu
    snap_step = int(SNAP_EVERY_LU / DT)            # every 10 lu

    outroot = ROOT / "07_validation" / "audits" / "qng-v9a-phase-space-v1"
    outroot.mkdir(parents=True, exist_ok=True)

    print(f"\n  L={L}, DT={DT}, T_P1={T_P1}, T_P2={T_P2}")
    print(f"  reduced every {m_sample_step} steps (= {M_SAMPLE_EVERY_LU} lu)")
    print(f"  snapshot every {snap_step} steps (= {SNAP_EVERY_LU} lu)")
    print(f"  exact_a={EXACT_A_MODE!r}")

    reports = {}
    for R in (3, 4, 5):
        Rdir = outroot / f"R{R}"
        try:
            reports[R] = run_R(R, L, DT, n1, n2, m_sample_step, snap_step,
                               Rdir, verbose=True)
        except Exception as exc:
            print(f"  [R={R}] FAILED with {type(exc).__name__}: {exc}",
                  flush=True)
            reports[R] = {'R': R, 'error': str(exc)}

    # Aggregate report
    summary = {
        'test_id': 'QNG-GPU-100',
        'date': '2026-04-22',
        'prereg': '07_validation/prereg/QNG-GPU-100.md',
        'reports_per_R': reports,
    }
    # Structural gates
    def ok(k, r):
        return k in r and r[k] is not False and r.get('error') is None
    all_complete = all(ok('final_M_ring', r) for r in reports.values())
    all_H_ok = all(r.get('H_drift_peak_to_peak', 1.0) < 0.10
                   for r in reports.values() if ok('final_M_ring', r))
    all_orbital = all(r.get('duty_cycle_ring', 0.0) > 0.05 and
                       r.get('convergence_rel', 1.0) < 0.15
                       for r in reports.values() if ok('final_M_ring', r))
    summary['gates'] = {
        'G1_all_runs_complete_H_under_10pct': all_complete and all_H_ok,
        'G2_orbital_attractor_all_R': all_orbital,
        'G3_snapshots_written': all(
            (outroot / f"R{R}" / "snapshots.npz").exists() for R in (3, 4, 5)
        ),
    }
    summary['verdict'] = (
        'PASS' if all(summary['gates'].values()) else 'PARTIAL_OR_FAIL')

    with open(outroot / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    print("\n" + "=" * 80)
    print(f"  GATES: {summary['gates']}")
    print(f"  VERDICT: {summary['verdict']}")
    print(f"  Summary: {outroot / 'summary.json'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
