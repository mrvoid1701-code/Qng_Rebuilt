"""QNG-GPU-031b: phase-space orbit test at 5x finer DT.

Companion to GPU-031.  Question: is the breathing mode (T~129 lu, seen in
GPU-031 at DT=0.025) PHYSICAL or NUMERICAL?

Protocol: same cached L=28 R=4 ring, same matter-sector-only mode
(k_gm=0, chi_decay=0, damping=0, channel_f=True, v_couple=True), but
DT=0.005 and T=200 lu so we catch ~1.5 breathing periods at 5x finer
stepping (N_steps = 40_000, same as GPU-031).

Reading:
- If the breathing period at DT=0.005 still lands at ~129 +/- 20 lu AND
  the secular H drift rate drops to <2 % / 200 lu, the mode is PHYSICAL.
- If the period changes by >50 % or the mode disappears, the mode at
  DT=0.025 was INTEGRATOR ARTIFACT.

Gates:
  G1 (conservation refined): |dH/H0| < 0.03 over 200 lu
      (GPU-031 had 0.17 over first 200 lu at DT=0.025; DT=0.005 should
      drop this by >5x if integrator error dominates)
  G2 (boundedness):         max|M_ring - M0|/M0 < 2.0 over 200 lu
      (GPU-031 first 200 lu: 4.8; dropping to <2 would indicate the
      swings were DT-amplified)
  G3 (period agreement):    breathing period in [100, 160] lu
      (if present at all)

Verdicts:
  H_BREATHING_PHYSICAL  = G1 PASS + G3 PASS
  H_BREATHING_SOFTENED  = G1 PASS + G3 FAIL (period shifts but H converges)
  H_INTEGRATOR_ARTIFACT = G1 FAIL (drift persists, mode was numerical)
  H_CHAOTIC_STILL       = G2 FAIL (even at fine DT, orbit unbounded)
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

from qng_v8_canonical_gpu import (
    hamiltonian_v8, yoshida4_step,
    SIGMA_M_REF, MU_M, MU_PHI,
)
from qng_v8_ring_cache import form_ring_cached


def m_ring(sm, sm_ref=SIGMA_M_REF):
    return float(sm_ref * sm.size - cp.sum(sm))


def core_obs(sm, phi, pi_m, pi_phi):
    return {
        'sm_min': float(cp.min(sm)), 'sm_max': float(cp.max(sm)),
        'T_m':    float((1.0/(2.0*MU_M))   * cp.sum(pi_m*pi_m)),
        'T_phi':  float((1.0/(2.0*MU_PHI)) * cp.sum(pi_phi*pi_phi)),
    }


def main():
    print("=" * 80)
    print("QNG-GPU-031b: phase-space orbit at DT=0.005 (refined)")
    print("=" * 80)

    L, R = 28, 4
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0, verbose=False)
    N = L ** 3

    DT_RUN  = 0.005
    T_PHYS  = 200.0
    N_STEPS = int(round(T_PHYS / DT_RUN))
    LOG_LU  = 0.5
    STRIDE  = int(round(LOG_LU / DT_RUN))

    state = {
        'sg':     ring_state['sg'].copy(),
        'sm':     ring_state['sm'].copy(),
        'chi':    ring_state['chi'].copy(),
        'phi':    ring_state['phi'].copy(),
        'pi_m':   cp.zeros(N, dtype=cp.float64),
        'pi_phi': cp.zeros(N, dtype=cp.float64),
    }

    print(f"  L={L}, R={R}, N={N}, DT={DT_RUN}, T={T_PHYS} lu, N_steps={N_STEPS}")
    print(f"  mode: k_gm=0, chi_decay=0, damping=0, channel_f=True, v_couple=True")
    print()

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0)
    M0 = m_ring(state['sm'])
    c0 = core_obs(state['sm'], state['phi'], state['pi_m'], state['pi_phi'])
    print(f"  H_0     = {H0:+.4f}")
    print(f"  M_ring_0 = {M0:+.4f}")
    print()
    print(f"  {'t':>6s} {'H':>11s} {'dH/H0':>10s} {'M_ring':>10s} {'dM/M0':>10s}"
          f" {'sm_min':>8s} {'T_m':>8s} {'T_phi':>8s}")

    log = [{'t': 0.0, 'H': H0, 'M_ring': M0, 'dH': 0.0, 'dM': 0.0, **c0}]
    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        state = yoshida4_step(
            state, DT_RUN, nb_idx,
            k_gm=0.0, damping_gamma=0.0, chi_decay=0.0,
            v_couple_on=True, channel_f=True,
        )
        if step % STRIDE == 0:
            t_phys = step * DT_RUN
            H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0)
            M = m_ring(state['sm'])
            c = core_obs(state['sm'], state['phi'], state['pi_m'], state['pi_phi'])
            dH = (H - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
            dM = (M - M0) / abs(M0) if abs(M0) > 1e-10 else 0.0
            log.append({'t': t_phys, 'H': H, 'M_ring': M, 'dH': dH, 'dM': dM, **c})
            if step % (STRIDE * 10) == 0:
                print(f"  {t_phys:6.1f} {H:+11.3f} {dH:+10.2e} {M:+10.3f} "
                      f"{dM:+10.2e} {c['sm_min']:8.4f} "
                      f"{c['T_m']:8.4f} {c['T_phi']:8.4f}", flush=True)

    wall = time.time() - t_start
    print(f"\n  wall = {wall/60:.1f} min")

    # -- Analysis --
    ts  = np.array([e['t'] for e in log])
    Hs  = np.array([e['H'] for e in log])
    Ms  = np.array([e['M_ring'] for e in log])
    dHs = np.array([e['dH'] for e in log])
    dMs = np.array([e['dM'] for e in log])

    max_abs_dH = float(np.max(np.abs(dHs)))
    max_abs_dM = float(np.max(np.abs(dMs)))

    # Secular drift
    coef = np.polyfit(ts, Hs, 1)
    secular_rate = float(coef[0])
    secular_dH_200 = secular_rate * 200.0
    secular_frac = abs(secular_dH_200 / H0)
    H_detrended = Hs - np.polyval(coef, ts)
    osc_amp = float(H_detrended.std())
    osc_over_secular = osc_amp / max(abs(secular_dH_200), 1e-10)

    # Autocorrelation of M_ring -> breathing period if any
    Mc = Ms - Ms.mean()
    ac = np.correlate(Mc, Mc, mode='full')[len(Mc)-1:]
    ac = ac / (ac[0] + 1e-30)
    # find first zero crossing
    zero_cross_idx = int(np.argmax(ac < 0)) if np.any(ac < 0) else 0
    peak_period = None
    peak_ac = 0.0
    if zero_cross_idx > 0 and zero_cross_idx + 1 < len(ac):
        search = ac[zero_cross_idx:min(len(ac), zero_cross_idx + 400)]
        if len(search) > 0:
            peak_local = int(np.argmax(search))
            peak_period = float(ts[zero_cross_idx + peak_local])
            peak_ac = float(search[peak_local])

    # Gates
    G1_pass = max_abs_dH < 0.03
    G2_pass = max_abs_dM < 2.0
    G3_pass = (peak_period is not None) and (100.0 <= peak_period <= 160.0)

    if G2_pass and G1_pass and G3_pass:
        verdict = "H_BREATHING_PHYSICAL"
        diag = ("Breathing mode at T={:.1f} lu survives at DT=0.005 with "
                "conservative H. Mode is PHYSICAL. Scenario A has empirical "
                "content; proceed with Poincare analysis.").format(peak_period)
    elif G1_pass and not G3_pass:
        verdict = "H_BREATHING_SOFTENED"
        diag = ("H converges at fine DT but breathing period shifted "
                "(found {:.1f} lu vs GPU-031 129 lu) or absent. "
                "Mode was partly integrator-shaped.").format(peak_period or -1)
    elif not G1_pass:
        verdict = "H_INTEGRATOR_ARTIFACT"
        diag = ("Secular H drift persists at DT=0.005 ({:.2f}% over 200 lu). "
                "F_A approximation is the dominant error source. "
                "DER-QNG-050 exact canonical F_A required.").format(secular_frac*100)
    else:
        verdict = "H_CHAOTIC_STILL"
        diag = ("Even at fine DT, M_ring unbounded (>2x M0). "
                "Scenario A likely falsified.")

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  G1 (|dH/H0| < 0.03):     max={max_abs_dH:.3e}  {'PASS' if G1_pass else 'FAIL'}")
    print(f"  G2 (|dM/M0| < 2.0):      max={max_abs_dM:.3e}  {'PASS' if G2_pass else 'FAIL'}")
    print(f"  G3 (period ~ 129 lu):    T={peak_period!s:>10s}  {'PASS' if G3_pass else 'FAIL'}")
    print(f"  Secular dH/H0 over 200 lu: {secular_frac*100:+.2f}%")
    print(f"  Breathing peak ac:       {peak_ac:.3f}")
    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    # -- Compare to GPU-031 first-200-lu --
    gpu031_path = ROOT / "07_validation" / "audits" / "qng-v8-phase-space-orbit-v1" / "trajectory.npz"
    compare = {}
    if gpu031_path.exists():
        d = np.load(gpu031_path)
        t1 = d['t']; M1 = d['M_ring']; dH1 = d['dH']
        mask = t1 <= 200.0
        g031_dH_max_200 = float(np.abs(dH1[mask]).max())
        g031_dM_max_200 = float(np.max(np.abs((M1[mask] - M1[0]) / M1[0])))
        compare = {
            'gpu031_dt': 0.025,
            'gpu031_dH_max_over_first_200lu': g031_dH_max_200,
            'gpu031_dM_max_over_first_200lu': g031_dM_max_200,
            'dH_ratio_031_over_031b': g031_dH_max_200 / max_abs_dH if max_abs_dH > 1e-10 else None,
            'dM_ratio_031_over_031b': g031_dM_max_200 / max_abs_dM if max_abs_dM > 1e-10 else None,
        }
        print()
        print(f"  Compared to GPU-031 (DT=0.025) first 200 lu:")
        print(f"    |dH/H0| ratio (031/031b): {compare['dH_ratio_031_over_031b']:.2f}x")
        print(f"    |dM/M0| ratio (031/031b): {compare['dM_ratio_031_over_031b']:.2f}x")
        if compare['dH_ratio_031_over_031b'] is not None and compare['dH_ratio_031_over_031b'] > 3.0:
            print("    -> GPU-031 (coarse DT) significantly worse: INTEGRATOR-LIMITED confirmed.")

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-phase-space-orbit-v1b"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'DT': DT_RUN, 'T_phys': T_PHYS,
            'H0': H0, 'M0': M0,
            'max_abs_dH': max_abs_dH, 'max_abs_dM': max_abs_dM,
            'secular_rate_per_lu': secular_rate,
            'secular_dH_over_200lu': secular_dH_200,
            'secular_frac_200lu': secular_frac,
            'osc_amp_detrended': osc_amp,
            'osc_over_secular': osc_over_secular,
            'breathing_peak_period_lu': peak_period,
            'breathing_peak_ac': peak_ac,
            'G1_pass': bool(G1_pass),
            'G2_pass': bool(G2_pass),
            'G3_pass': bool(G3_pass),
            'verdict': verdict,
            'diagnosis': diag,
            'compare_to_gpu031': compare,
            'log_first_20': log[:20],
            'log_last_20':  log[-20:],
        }, f, indent=2)
    np.savez(outdir / "trajectory.npz",
             t=ts, H=Hs, M_ring=Ms, dH=dHs, dM=dMs,
             sm_min=np.array([e['sm_min'] for e in log]),
             sm_max=np.array([e['sm_max'] for e in log]),
             T_m=np.array([e['T_m'] for e in log]),
             T_phi=np.array([e['T_phi'] for e in log]))
    print(f"\n  Report: {outdir / 'report.json'}")


if __name__ == "__main__":
    main()
