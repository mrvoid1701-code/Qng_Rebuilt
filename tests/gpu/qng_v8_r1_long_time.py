"""QNG-GPU-031f: long-time R1 probe — orbital attractor search.

Background: GPU-031e (T_P2=1000 lu) under R1 showed M_ring oscillating
chaotically in [-97, +686] with late drift 202%. Ring is not static but
may be a phase of a bounded orbit. If so, time-averaging should reveal
a convergent <M_ring>_t that can be a baryon mass candidate (DER-QNG-038
orbital reinterpretation, Scenario A).

Protocol:
  P1 (T=300 lu, v_couple=False) — phi vortex (same as GPU-031e)
  P2 (T=5000 lu, v_couple=True)  — orbital run, fine sampling

Sampling: M_ring every 1 lu (5000 samples in P2) for power spectrum
and running mean. Full hamiltonian every 100 lu (light load, drift
monitor).

Diagnostics:
  1. Running <M_ring>_t vs t — convergence?
  2. Power spectrum of M_ring(t) — orbital frequencies?
  3. Duty-cycle: fraction of time M_ring > 500 (ring phase)
  4. Minimum dwell / max dwell in ring-like vs diffuse phase

Verdicts:
  * H_ORBITAL_ATTRACTOR: <M_ring>_t converges (drift over second half
    < 5% of first half), dominant frequency detected, duty > 10%.
    => DER-QNG-038 recoverable as orbital ladder.
  * H_NO_RECURRENCE: <M_ring>_t drifts secularly, no peak in spectrum.
    => Scenario A falsified at this L, R; v9 path (R4) mandatory.
  * H_TRANSIENT_ONLY: ring hits at most once and never again
    (duty near 0, long gap stats).
    => rings are not orbits, they are one-shot transients.
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
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit, hamiltonian_v8,
    SIGMA_M_REF, CHI_DECAY_V7, MU_M, MU_PHI,
)

CPU_074_R4 = 728.92
EXACT_A_MODE = 'r1'
RING_THRESH = 500.0  # M_ring > RING_THRESH counts as "ring phase"


def run_phase_sampled(state, nb_idx, n_steps, DT, v_couple_on, exact_a,
                      m_sample_every=1, H_sample_every=100,
                      verbose=True):
    """Run n_steps, sample M_ring every m_sample_every steps, H every
    H_sample_every * m_sample_every steps."""
    t0 = time.time()
    # Pre-allocate sample arrays (lists on CPU side; arrays are scalars)
    m_times = []
    m_values = []
    H_samples = []
    n_m = n_steps // m_sample_every
    n_H = n_steps // (H_sample_every * m_sample_every)
    if verbose:
        print(f"    n_steps={n_steps}, M samples={n_m}, H samples={n_H}",
              flush=True)
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx,
                              v_couple_on=v_couple_on, chi_decay=CHI_DECAY_V7,
                              exact_a=exact_a)
        if s % m_sample_every == 0:
            t_phys = s * DT
            M = float(ring_mass_deficit(state['sm']))
            m_times.append(t_phys)
            m_values.append(M)
            if s % (H_sample_every * m_sample_every) == 0:
                H = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                                   exact_a=exact_a)
                sm_min = float(cp.min(state['sm']))
                sm_max = float(cp.max(state['sm']))
                H_samples.append({'t': t_phys, 'H': H, 'sm_min': sm_min,
                                  'sm_max': sm_max, 'M': M})
                if verbose:
                    print(f"    t={t_phys:7.1f}  M={M:+9.3f}  H={H:+10.2f}  "
                          f"sm=[{sm_min:.3f},{sm_max:.3f}]", flush=True)
    wall = time.time() - t0
    return state, np.asarray(m_times), np.asarray(m_values), H_samples, wall


def analyze_m_series(t_arr, m_arr, ring_thresh=RING_THRESH):
    """Compute orbital diagnostics on M_ring(t) samples."""
    n = len(m_arr)
    # Running <M>
    run_mean = np.cumsum(m_arr) / np.arange(1, n + 1)
    # First-half vs second-half mean (convergence test)
    half = n // 2
    mean_first_half = float(np.mean(m_arr[:half]))
    mean_second_half = float(np.mean(m_arr[half:]))
    mean_all = float(np.mean(m_arr))
    std_all = float(np.std(m_arr))
    # Convergence ratio: relative change between halves
    convergence_rel = abs(mean_second_half - mean_first_half) / max(abs(mean_all), 1e-10)
    # Duty cycle: fraction of time M > ring_thresh
    duty = float(np.mean(m_arr > ring_thresh))
    # Power spectrum (real FFT of centered series)
    m_centered = m_arr - mean_all
    # dt between samples
    dt = float(t_arr[1] - t_arr[0]) if n > 1 else 1.0
    freqs = np.fft.rfftfreq(n, d=dt)
    power = np.abs(np.fft.rfft(m_centered)) ** 2
    # Dominant frequency (excluding DC)
    if len(power) > 1:
        dom_idx = int(np.argmax(power[1:])) + 1
        dom_freq = float(freqs[dom_idx])
        dom_period = 1.0 / dom_freq if dom_freq > 0 else float('inf')
        dom_power_frac = float(power[dom_idx] / max(np.sum(power[1:]), 1e-10))
    else:
        dom_freq = 0.0
        dom_period = float('inf')
        dom_power_frac = 0.0
    return {
        'n_samples': n,
        'dt_sample': dt,
        'mean_all': mean_all,
        'std_all': std_all,
        'mean_first_half': mean_first_half,
        'mean_second_half': mean_second_half,
        'convergence_rel': convergence_rel,
        'duty_cycle_ring': duty,
        'ring_thresh': ring_thresh,
        'dominant_freq': dom_freq,
        'dominant_period_lu': dom_period,
        'dominant_power_frac': dom_power_frac,
    }


def main():
    print("=" * 80)
    print("QNG-GPU-031f: long-time R1 probe (T_P2=5000 lu)")
    print("=" * 80)

    L = 20
    R = 4
    T_P1 = 300.0
    T_P2 = 5000.0
    DT = 0.025
    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)

    # Sample M_ring every 40 steps (= every 1 lu)
    m_sample_every = int(1.0 / DT)
    # H every 100 lu
    H_sample_every = 100

    outdir = ROOT / "07_validation" / "audits" / "qng-v8-r1-long-time-v1"
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n  L={L}, R={R}, T_P1={T_P1}, T_P2={T_P2}, DT={DT}")
    print(f"  n1={n1}, n2={n2}, total {n1+n2} Yoshida4 steps")
    print(f"  exact_a={EXACT_A_MODE!r}")
    print(f"  M_ring sample every {m_sample_every} steps (= every "
          f"{m_sample_every*DT:.2f} lu)")
    print(f"  H sample every {H_sample_every} M-samples "
          f"(= every {H_sample_every*m_sample_every*DT:.0f} lu)")

    # --- Phase 1 ---
    print("\n  [Phase 1] v_couple_on=False, exact_a='r1'")
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)

    state, t_p1, m_p1, h_p1, wall_p1 = run_phase_sampled(
        state, nb_idx, n1, DT,
        v_couple_on=False, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)
    M_p1 = float(ring_mass_deficit(state['sm']))
    print(f"    end P1: M_ring={M_p1:+.3f}  wall={wall_p1:.1f}s")

    # --- Phase 2 ---
    print("\n  [Phase 2] v_couple_on=True, exact_a='r1', T=5000 lu")
    state, t_p2, m_p2, h_p2, wall_p2 = run_phase_sampled(
        state, nb_idx, n2, DT,
        v_couple_on=True, exact_a=EXACT_A_MODE,
        m_sample_every=m_sample_every,
        H_sample_every=H_sample_every, verbose=True)

    # --- Analysis ---
    print("\n" + "=" * 80)
    print("PHASE 2 M_ring ANALYSIS")
    print("=" * 80)
    stats = analyze_m_series(t_p2, m_p2, ring_thresh=RING_THRESH)
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k:28s} = {v:+.4g}")
        else:
            print(f"  {k:28s} = {v}")

    # --- Verdict ---
    final_M = float(m_p2[-1])
    print("\n  End-of-run M_ring = {:+.3f}".format(final_M))
    print("  CPU-074 baseline  = {:+.3f}".format(CPU_074_R4))
    print("  <M_ring>_t        = {:+.3f}  vs CPU-074: {:+.2f}%".format(
        stats['mean_all'], 100.0 * (stats['mean_all'] - CPU_074_R4) / CPU_074_R4))

    # Decision logic
    if stats['convergence_rel'] < 0.05 and stats['duty_cycle_ring'] > 0.10 \
            and stats['dominant_power_frac'] > 0.05:
        verdict = "H_ORBITAL_ATTRACTOR"
        diag = (f"<M_ring>_t converges (rel change {stats['convergence_rel']:.2%}), "
                f"duty={stats['duty_cycle_ring']:.1%}, dominant period "
                f"{stats['dominant_period_lu']:.1f} lu. Orbital interpretation "
                f"of DER-QNG-038 viable.")
    elif stats['duty_cycle_ring'] < 0.02 and stats['mean_all'] < 100.0:
        verdict = "H_TRANSIENT_ONLY"
        diag = (f"Rings are one-shot: duty {stats['duty_cycle_ring']:.1%}, "
                f"<M_ring>_t = {stats['mean_all']:.1f} near zero. "
                f"No recurrence.")
    elif stats['convergence_rel'] > 0.30:
        verdict = "H_NO_RECURRENCE"
        diag = (f"<M_ring>_t drifts: first-half {stats['mean_first_half']:.1f}, "
                f"second-half {stats['mean_second_half']:.1f}, rel "
                f"{stats['convergence_rel']:.2%}. Scenario A suspect.")
    else:
        verdict = "H_BOUNDED_NONPERIODIC"
        diag = (f"M_ring bounded (std {stats['std_all']:.1f}) but no clear "
                f"orbital attractor: dominant freq holds only "
                f"{stats['dominant_power_frac']:.1%} of power. Chaotic "
                f"bounded oscillation.")

    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    # --- Save artifacts ---
    np.savez(outdir / "final_state.npz",
             sm=cp.asnumpy(state['sm']), phi=cp.asnumpy(state['phi']),
             pi_m=cp.asnumpy(state['pi_m']), pi_phi=cp.asnumpy(state['pi_phi']))
    np.savez(outdir / "m_series.npz",
             t_p1=t_p1, m_p1=m_p1, t_p2=t_p2, m_p2=m_p2)

    # Convert numpy scalars to plain floats/ints for JSON
    def _json_safe(v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        return v
    stats_json = {k: _json_safe(v) for k, v in stats.items()}

    with open(outdir / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2, 'DT': DT,
            'exact_a_mode': EXACT_A_MODE,
            'm_sample_every_steps': m_sample_every,
            'm_sample_dt_lu': m_sample_every * DT,
            'H_sample_every': H_sample_every,
            'cpu_074_canonical_M_ring': CPU_074_R4,
            'final_M_ring': final_M,
            'p1_h_samples': h_p1,
            'p2_h_samples': h_p2,
            'stats': stats_json,
            'verdict': verdict,
            'diagnosis': diag,
            'wall_p1_s': wall_p1, 'wall_p2_s': wall_p2,
        }, f, indent=2)
    print(f"\n  Report:      {outdir / 'report.json'}")
    print(f"  Final state: {outdir / 'final_state.npz'}")
    print(f"  M series:    {outdir / 'm_series.npz'}")


if __name__ == "__main__":
    main()
