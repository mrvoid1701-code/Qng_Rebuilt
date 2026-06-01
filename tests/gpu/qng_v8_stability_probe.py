"""QNG-GPU-020 stability probe (NOT a prereg test).

Diagnoses v8 Yoshida 4 numerical instability observed in Stage B
(d=6/8/10 all produced F_v8=NaN while v7 gave finite, monotone F).

Runs a short single-ring simulation under several (dt, gamma) settings
and reports when NaN first appears and the Hamiltonian drift trace.
Purpose: pick dt and damping that make v8 stable before re-pre-registering
GPU-020 Stage B.

Usage:  py -u tests/gpu/qng_v8_stability_probe.py
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (  # noqa: E402
    SIGMA_G_REF, SIGMA_M_REF,
    MU_M, MU_PHI, M_PHI_DEPRECATED, G_V_COUPLE,
    build_nb, init_phi_single_ring, make_state,
    yoshida4_step, hamiltonian_v8,
    SIGMA_G_MIN_ABORT,
)


def probe_single_ring(dt, gamma, L=16, R=4, nsteps=2000, k_gm=0.0, tag=""):
    """Run single-ring v8 evolution and report first instability step.

    Records NaN onset, H drift, sigma_g min. Returns dict with diagnostics.
    """
    cp.random.seed(0)
    nb = build_nb(L)
    phi0 = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi0)

    H0 = hamiltonian_v8(state, nb)
    sg_min0 = float(cp.min(state['sg']))

    nan_step = None
    sg_abort_step = None
    H_hist = [H0]
    sg_min_hist = [sg_min0]
    sample_every = max(1, nsteps // 40)

    t0 = time.time()
    for s in range(1, nsteps + 1):
        state = yoshida4_step(state, dt, nb, k_gm=k_gm,
                              damping_gamma=gamma, v_couple_on=True)
        if s % sample_every == 0 or s == nsteps:
            sg_nan = bool(cp.any(cp.isnan(state['sg'])))
            sm_nan = bool(cp.any(cp.isnan(state['sm'])))
            phi_nan = bool(cp.any(cp.isnan(state['phi'])))
            pim_nan = bool(cp.any(cp.isnan(state['pi_m'])))
            piphi_nan = bool(cp.any(cp.isnan(state['pi_phi'])))
            if sg_nan or sm_nan or phi_nan or pim_nan or piphi_nan:
                if nan_step is None:
                    nan_step = s
                break
            sg_min = float(cp.min(state['sg']))
            sg_min_hist.append(sg_min)
            H_hist.append(hamiltonian_v8(state, nb))
            if sg_min < SIGMA_G_MIN_ABORT and sg_abort_step is None:
                sg_abort_step = s
    wall = time.time() - t0

    H_final = H_hist[-1] if H_hist else float('nan')
    drift = (H_final - H0) / max(abs(H0), 1e-12)
    return {
        'tag': tag,
        'dt': dt,
        'gamma': gamma,
        'nsteps_requested': nsteps,
        'nan_step': nan_step,
        'sg_abort_step': sg_abort_step,
        'H0': H0,
        'H_final': H_final,
        'drift_rel': drift,
        'sg_min_initial': sg_min0,
        'sg_min_final': sg_min_hist[-1] if sg_min_hist else float('nan'),
        'wall_sec': wall,
        'survived': nan_step is None,
    }


def main():
    print("=" * 74)
    print("QNG-GPU-020 v8 stability probe (single ring, L=16, R=4)")
    print("=" * 74)
    print(f"  MU_M={MU_M:.4f}  MU_PHI={MU_PHI:.4f}  M_PHI_DEPRECATED={M_PHI_DEPRECATED:.4f}  g={G_V_COUPLE}")
    print(f"  SIGMA_G_MIN_ABORT={SIGMA_G_MIN_ABORT}")
    print()

    configs = [
        # (dt,     gamma, nsteps, tag)
        (0.025,   0.00,   800,  "baseline: prereg dt, no damping"),
        (0.010,   0.00,  2000,  "dt/2.5 (0.010), no damping"),
        (0.005,   0.00,  4000,  "dt/5   (0.005), no damping"),
        (0.025,   0.01,   800,  "prereg dt + gamma=0.01 light Langevin"),
        (0.025,   0.05,   800,  "prereg dt + gamma=0.05 mod Langevin"),
        (0.010,   0.01,  2000,  "dt=0.010 + gamma=0.01"),
    ]

    results = []
    for dt, gamma, nsteps, tag in configs:
        print(f"--- {tag} ---")
        print(f"  dt={dt}  gamma={gamma}  nsteps={nsteps}")
        r = probe_single_ring(dt, gamma, nsteps=nsteps, tag=tag)
        results.append(r)
        if r['survived']:
            print(f"  SURVIVED all {nsteps} steps")
            print(f"  H0={r['H0']:.3e}  H_final={r['H_final']:.3e}  drift={r['drift_rel']:+.3e}")
            print(f"  sg_min initial={r['sg_min_initial']:.4f}  final={r['sg_min_final']:.4f}")
        else:
            print(f"  FAILED at step {r['nan_step']}  (NaN observed)")
        if r['sg_abort_step'] is not None:
            print(f"  sigma_g positivity breach at step {r['sg_abort_step']}")
        print(f"  wall: {r['wall_sec']:.1f}s")
        print()

    print("=" * 74)
    print("SUMMARY")
    print("=" * 74)
    print(f"{'tag':<50s} {'dt':<6s} {'gamma':<6s} {'NaN@':<10s} {'drift':<12s}")
    for r in results:
        nan_s = str(r['nan_step']) if r['nan_step'] is not None else "OK"
        drift_s = f"{r['drift_rel']:+.2e}" if r['survived'] else "n/a"
        print(f"{r['tag']:<50s} {r['dt']:<6g} {r['gamma']:<6g} {nan_s:<10s} {drift_s}")

    survivors = [r for r in results if r['survived']]
    if survivors:
        best = min(survivors, key=lambda r: abs(r['drift_rel']))
        print()
        print(f"Best stable config: {best['tag']}")
        print(f"  dt={best['dt']} gamma={best['gamma']}  |drift|={abs(best['drift_rel']):.2e}")
    else:
        print()
        print("NO stable config found — v8 has deeper instability.")
        print("Next step: investigate force magnitude / initialization, not just dt.")


if __name__ == "__main__":
    main()
