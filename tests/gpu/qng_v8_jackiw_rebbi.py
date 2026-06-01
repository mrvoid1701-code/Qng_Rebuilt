"""QNG-GPU-035: Einstein Jackiw-Rebbi dispersion test.

Test the hypothesis: matter in v8 = phi quanta with position-dependent
mass m_phi^2(x) = (g/mu_phi) * (sigma_ref - sigma_m(x))^2.

Protocol (cleanest form — uniform sigma_m):
  1. Initialize sigma_m = sigma_uniform (flat), sigma_g = ref, chi = 0.
  2. Seed a tiny phi wavepacket at k=0 and k=2pi/L with amplitude A<<1.
  3. Evolve under v8 R1 with v_couple_on=True.
  4. Measure the oscillation frequency omega_meas of phi at each k.
  5. Compare to prediction omega^2 = c_phi^2 * k^2 + m_phi^2 where
     m_phi^2 = (g / mu_phi) * (sigma_ref - sigma_uniform)^2.

Prediction for canonical v8 params (g=0.22, mu_phi=0.857):
  Delta=0.1: m^2 = 0.002568,  T(k=0) = 2pi/m ≈ 123.9 lu
  Delta=0.2: m^2 = 0.01027,   T(k=0) = 2pi/m ≈  62.0 lu
  Delta=0.0: m^2 = 0,         T(k=0) = infinity (no oscillation)

Gates:
  G1: at Delta=0 (σ_m=σ_ref), k=0 phi does NOT oscillate (no mass gap).
  G2: at Delta=0.1, k=0 T_meas within 15% of 123.9 lu.
  G3: at Delta=0.2, k=0 T_meas within 15% of 62.0 lu.
  G4: Ratio test: T(Delta=0.1)/T(Delta=0.2) within 10% of theoretical 2.0.

If G1-G4 PASS:
  m_phi is position-dependent via V_couple — Jackiw-Rebbi mechanism
  confirmed. Matter = phi bound states in sigma_m wells.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    build_nb, make_state, yoshida4_step, hamiltonian_v8,
    SIGMA_G_REF, SIGMA_M_REF, CHI_DECAY_V7,
    G_V_COUPLE, MU_PHI, BETA_PHI,
)

# Canonical v8 params (from qng_v8_canonical_gpu.py)
EXACT_A_MODE = 'r1'


def make_jackiw_state(L, sigma_m_uniform, phi_amp, k_mode):
    """Uniform sigma_m, flat sigma_g, chi=0, phi = amp*cos(k*x)."""
    N = L * L * L
    state = {
        'sg':  cp.full(N, SIGMA_G_REF, dtype=cp.float64),
        'sm':  cp.full(N, sigma_m_uniform, dtype=cp.float64),
        'chi': cp.zeros(N, dtype=cp.float64),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }
    if k_mode == 0:
        phi = cp.full(N, phi_amp, dtype=cp.float64)  # global bump
    else:
        xs = np.arange(L, dtype=np.float64)
        xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
        k_vec = 2.0 * np.pi * k_mode / L
        phi_np = phi_amp * np.cos(k_vec * xg)
        phi = cp.asarray(phi_np.ravel())
    state['phi'] = phi
    return state


def measure_phi_mean(state):
    return float(cp.mean(state['phi']))


def fit_oscillation_period(times, values, max_n_periods=10):
    """Zero-crossing method + sinusoidal fit for period extraction."""
    v = np.asarray(values, dtype=np.float64)
    t = np.asarray(times, dtype=np.float64)
    v_centered = v - np.mean(v)
    # Find zero crossings (ascending)
    zc = []
    for i in range(1, len(v_centered)):
        if v_centered[i - 1] < 0 and v_centered[i] >= 0:
            # Linear interp
            t_cross = t[i - 1] + (t[i] - t[i - 1]) * (
                -v_centered[i - 1]) / (v_centered[i] - v_centered[i - 1])
            zc.append(t_cross)
    if len(zc) < 2:
        return None, 0
    # Use first few zero-crossings (lattice effects accumulate)
    n_use = min(len(zc), max_n_periods + 1)
    periods = np.diff(zc[:n_use])
    if len(periods) == 0:
        return None, 0
    return float(np.mean(periods)), len(periods)


def run_measurement(L, sigma_m_uniform, phi_amp=0.05, k_mode=0,
                    T_run=300.0, DT=0.025, freeze_sm=True):
    """Seed tiny phi amplitude, evolve, measure oscillation period.

    freeze_sm=True pins sigma_m = sigma_m_uniform and pi_m = 0 after every
    Yoshida4 step, isolating the phi dispersion from slow sigma_m drift
    (the ALPHA*(sigma_ref - sigma_m) pull + V_couple back-reaction on sigma_m
    would otherwise reduce the effective deficit over T_run).
    """
    n_steps = int(T_run / DT)
    sample_every = int(1.0 / DT)

    nb_idx = build_nb(L)
    state = make_jackiw_state(L, sigma_m_uniform, phi_amp, k_mode)

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)

    times = [0.0]
    values = [measure_phi_mean(state)]
    sm_means = [float(cp.mean(state['sm']))]

    t0 = time.time()
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=True, chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        if freeze_sm:
            state['sm'].fill(sigma_m_uniform)
            state['pi_m'].fill(0.0)
        if s % sample_every == 0:
            t_phys = s * DT
            times.append(t_phys)
            values.append(measure_phi_mean(state))
            sm_means.append(float(cp.mean(state['sm'])))
    wall = time.time() - t0
    H1 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)

    T_meas, n_per = fit_oscillation_period(times, values)
    return {
        'L': L, 'sigma_m_uniform': sigma_m_uniform,
        'deficit': SIGMA_M_REF - sigma_m_uniform,
        'phi_amp': phi_amp, 'k_mode': k_mode, 'T_run': T_run,
        'freeze_sm': freeze_sm,
        'T_measured_lu': T_meas,
        'n_periods': n_per,
        'H0': float(H0), 'H1': float(H1),
        'H_drift_frac': abs(H1 - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0,
        'sm_mean_t0': sm_means[0],
        'sm_mean_tT': sm_means[-1],
        'wall_s': wall,
        'times': times, 'values': values,
    }


def predicted_period(deficit):
    """T_pred(k=0) = 2*pi / sqrt((g/(2*mu_phi))*deficit^2) for deficit > 0.

    Derivation: V_couple = (g/2) * Delta^2 * (1 - cos phi) ~ (g/4)*Delta^2*phi^2
    for small phi. EOM: mu_phi * phi_ddot = -(g/2) * Delta^2 * phi,
    giving omega^2 = (g / (2*mu_phi)) * Delta^2.
    Script previously used omega^2 = (g/mu_phi) * Delta^2, missing a factor
    of 1/2 from the phi^2/2 expansion of (1 - cos phi).
    """
    if deficit <= 0:
        return float('inf')
    m2 = (G_V_COUPLE / (2.0 * MU_PHI)) * deficit * deficit
    return 2.0 * np.pi / np.sqrt(m2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--L", type=int, default=24)
    parser.add_argument("--phi_amp", type=float, default=0.05)
    parser.add_argument("--T_run", type=float, default=600.0)
    parser.add_argument("--freeze_sm", type=int, default=1,
                        help="1=pin sigma_m to uniform value each step; 0=let drift")
    parser.add_argument("--audit_name", type=str,
                        default="qng-v8-jackiw-rebbi-v2")
    args = parser.parse_args()

    L = args.L
    audit_name = args.audit_name
    outdir = ROOT / "07_validation" / "audits" / audit_name
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"QNG-GPU-035: Einstein Jackiw-Rebbi dispersion test")
    print("=" * 80)
    print(f"  L={L}, phi_amp={args.phi_amp}, T_run={args.T_run}")
    print(f"  g={G_V_COUPLE}, mu_phi={MU_PHI:.4f}")
    print(f"  Prediction: T(delta) = 2pi/sqrt((g/(2*mu_phi))*delta^2)")
    print(f"  freeze_sm = {bool(args.freeze_sm)}")

    deficits = [0.0, 0.1, 0.2]
    results = []
    for delta in deficits:
        sigma_u = SIGMA_M_REF - delta
        T_pred = predicted_period(delta)
        print(f"\n  --- deficit={delta:+.3f} (sigma_m={sigma_u:.3f}) ---")
        print(f"    T_pred = {T_pred:.2f} lu")
        res = run_measurement(L=L, sigma_m_uniform=sigma_u,
                              phi_amp=args.phi_amp, k_mode=0,
                              T_run=args.T_run,
                              freeze_sm=bool(args.freeze_sm))
        T_m = res['T_measured_lu']
        if T_m is None:
            T_m_str = "no osc detected"
            ratio = float('nan')
        else:
            T_m_str = f"{T_m:.2f}"
            ratio = T_m / T_pred if T_pred < float('inf') else float('inf')
        print(f"    T_meas = {T_m_str} lu  (n_periods={res['n_periods']})  "
              f"ratio={ratio:+.3f}")
        print(f"    H drift frac = {res['H_drift_frac']:.2e}  "
              f"wall = {res['wall_s']:.1f}s")
        res['T_pred_lu'] = float(T_pred) if T_pred != float('inf') else None
        res['ratio_meas_pred'] = float(ratio) if not np.isnan(ratio) else None
        results.append(res)

    # Gates
    G1 = (results[0]['T_measured_lu'] is None or
          results[0]['T_measured_lu'] > 10 * args.T_run)
    G2 = (results[1]['T_measured_lu'] is not None and
          abs(results[1]['ratio_meas_pred'] - 1.0) < 0.15)
    G3 = (results[2]['T_measured_lu'] is not None and
          abs(results[2]['ratio_meas_pred'] - 1.0) < 0.15)
    if results[1]['T_measured_lu'] and results[2]['T_measured_lu']:
        ratio_period = results[1]['T_measured_lu'] / results[2]['T_measured_lu']
        G4 = abs(ratio_period / 2.0 - 1.0) < 0.10
    else:
        ratio_period = None
        G4 = False

    all_pass = G1 and G2 and G3 and G4
    verdict = "JACKIW_REBBI_PASS" if all_pass else "JACKIW_REBBI_FAIL"

    print("\n" + "=" * 80)
    print(f"GATES")
    print("=" * 80)
    print(f"  G1 (deficit=0, no oscillation): {G1}")
    print(f"  G2 (deficit=0.1, T within 15% of {predicted_period(0.1):.1f} lu): {G2}")
    print(f"  G3 (deficit=0.2, T within 15% of {predicted_period(0.2):.1f} lu): {G3}")
    print(f"  G4 (T(0.1)/T(0.2) ~ 2): {G4}  (ratio={ratio_period})")
    print(f"\n  VERDICT: {verdict}")

    def _json_safe(v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        return v

    # Strip heavy arrays for JSON
    results_json = []
    for r in results:
        rcopy = {k: _json_safe(v) for k, v in r.items()
                 if k not in ('times', 'values')}
        results_json.append(rcopy)

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L,
            'phi_amp': args.phi_amp,
            'T_run': args.T_run,
            'g': G_V_COUPLE, 'mu_phi': MU_PHI,
            'beta_phi': BETA_PHI, 'sigma_m_ref': SIGMA_M_REF,
            'results': results_json,
            'gates': {'G1': G1, 'G2': G2, 'G3': G3, 'G4': G4},
            'ratio_period_0p1_over_0p2': ratio_period,
            'verdict': verdict,
        }, f, indent=2)

    # Save full traces
    np.savez(outdir / "phi_traces.npz",
             **{f"times_delta_{r['deficit']:.2f}": r['times'] for r in results},
             **{f"values_delta_{r['deficit']:.2f}": r['values'] for r in results})

    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
