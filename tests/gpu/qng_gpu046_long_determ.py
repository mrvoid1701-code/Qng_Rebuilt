"""QNG-GPU-046-LONG — extended deterministic FDT probe to test Ruelle-Bowen hypothesis.

Context: GPU-045 measured lambda_max ~0.0015/lu for R1 attractor.
Mixing timescale 1/lambda_max ~667 lu. GPU-043/044 used T_meas=1000 lu
(~1.5 mixing times) — INSUFFICIENT for chaotic ergodic averaging.

This test: T_meas = 10000 lu (~15 mixing times) at single gamma=0.020,
R=4, L=20. Purely deterministic (no noise injection). Measures whether
<chi²> converges toward 1/gamma scaling at long times.

Success criterion:
  <chi²> at T_meas=10000 lu vs T_meas=1000 lu should INCREASE (closer
  to dissipation-limited value sigma_source²/(2*gamma) ~ several 1e-3
  instead of source-limited ~1.6e-4).

If <chi²> unchanged at long times -> Ruelle-Bowen NOT sufficient for
v8 FDT closure even with ergodic chaos present. Confirms hbar-from-v8
is structurally closed.

If <chi²> grows with T_meas -> Ruelle-Bowen mechanism operating; full
gamma-scan at long T_meas worth doing.

Runtime: L=20, T_meas=10000 lu at ~80 steps/s = 400k steps = ~85 min.
Plus formation+spinup 60k steps ~12 min. Total ~1.5h per run.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qng_v8_canonical_gpu import (
    CHI_DECAY_V7,
    build_nb, make_state, init_phi_single_ring,
    yoshida4_step, hamiltonian_v8, ring_mass_deficit,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu046-long-determ-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

L              = 20
T_P1           = 300.0
T_P2           = 1000.0
T_SPINUP       = 200.0
T_MEASURE      = 10000.0    # 10x GPU-043 = ~15 mixing times per 1/lambda_max
DT             = 0.025
SAMPLE_STRIDE  = 40         # 1 sample per lu (coarser for long run)
PROGRESS_EVERY = 4000
EXACT_A_MODE   = 'r1'
K_GM           = 0.01
CHI_DECAY      = 0.020      # single gamma — baseline


def form_ring_r1():
    print("  Phase 1+2 formation + spinup", flush=True)
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, 4)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT); n2 = int(T_P2 / DT); n_sp = int(T_SPINUP / DT)
    t0 = time.time()
    for step in range(n1):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=False,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            print(f"    [P1] {step+1}/{n1}", flush=True)
    for step in range(n2):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            print(f"    [P2] {step+1}/{n2}", flush=True)
    for step in range(n_sp):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            print(f"    [sp] {step+1}/{n_sp}", flush=True)
    wall = time.time() - t0
    print(f"  Formation+spinup ({n1+n2+n_sp} steps, {wall:.1f}s)", flush=True)
    return state, nb_idx


def run_measurement(state, nb_idx, T_meas, dt):
    n_meas = int(T_meas / dt)
    n_rec = n_meas // SAMPLE_STRIDE
    chi2_trace = np.zeros(n_rec, dtype=np.float64)
    M_trace    = np.zeros(n_rec, dtype=np.float64)
    H_samples  = np.zeros(20, dtype=np.float64)
    H_step = max(1, n_meas // 20)
    N_total = float(L ** 3)

    H0 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM,
                              exact_a=EXACT_A_MODE))
    H_samples[0] = H0

    t0 = time.time()
    rec_idx = 0
    for step in range(n_meas):
        state = yoshida4_step(state, dt, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if step % SAMPLE_STRIDE == 0 and rec_idx < n_rec:
            chi2_trace[rec_idx] = float(cp.sum(state['chi'] ** 2).get()) / N_total
            M_trace[rec_idx] = float(ring_mass_deficit(state['sm']))
            rec_idx += 1
        if (step + 1) % H_step == 0 and (step // H_step) < len(H_samples):
            H_samples[step // H_step] = float(
                hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM,
                               exact_a=EXACT_A_MODE))
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (step + 1) / elapsed
            eta = (n_meas - step - 1) / rate
            # Running averages over first half and second half so far
            half = rec_idx // 2
            if half > 0 and rec_idx > half:
                mean_h1 = float(np.mean(chi2_trace[:half]))
                mean_h2 = float(np.mean(chi2_trace[half:rec_idx]))
            else:
                mean_h1 = mean_h2 = float(chi2_trace[max(0,rec_idx-1)])
            print(f"    [meas] {step+1}/{n_meas}  {rate:.0f} steps/s  "
                  f"ETA {eta:.0f}s  "
                  f"<chi2>_1h={mean_h1:.3e} <chi2>_2h={mean_h2:.3e} "
                  f"M={M_trace[max(0,rec_idx-1)]:.1f}", flush=True)

    wall = time.time() - t0
    H_end = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=K_GM,
                                 exact_a=EXACT_A_MODE))
    H_drift = abs(H_end - H0) / max(abs(H0), 1e-10)
    print(f"  Measurement done ({wall:.1f}s) H_drift={H_drift:.2%}", flush=True)
    return {
        'chi2_trace': chi2_trace[:rec_idx],
        'M_trace':    M_trace[:rec_idx],
        'H_samples':  H_samples,
        'wall_sec':   wall,
        'H0':         H0,
        'H_end':      H_end,
        'H_drift':    H_drift,
    }


def analyze_convergence(chi2_trace, dt_sample):
    """Check if <chi²> has reached a plateau or continues changing."""
    N = len(chi2_trace)
    # Running mean over 10 equal chunks
    chunks = 10
    chunk_size = N // chunks
    chunk_means = np.array([
        float(np.mean(chi2_trace[i*chunk_size:(i+1)*chunk_size]))
        for i in range(chunks)
    ])
    # Compare last 3 chunks vs first 3 chunks
    mean_early = float(np.mean(chunk_means[:3]))
    mean_late  = float(np.mean(chunk_means[-3:]))
    rel_change = abs(mean_late - mean_early) / max(abs(mean_early), 1e-20)
    return {
        'chunks': chunks,
        'chunk_size_lu': chunk_size * dt_sample,
        'chunk_means': chunk_means.tolist(),
        'mean_early': mean_early,
        'mean_late':  mean_late,
        'relative_change': rel_change,
    }


def main():
    print("=" * 72)
    print("QNG-GPU-046-LONG: Extended deterministic FDT test")
    print(f"L={L}, R=4, gamma={CHI_DECAY}, T_meas={T_MEASURE} lu")
    print(f"Expected mixing timescale: 1/lambda_max ~ 667 lu")
    print(f"T_meas in mixing times: {T_MEASURE/667:.1f}")
    print("=" * 72)

    state, nb_idx = form_ring_r1()
    res = run_measurement(state, nb_idx, T_MEASURE, DT)

    dt_sample = DT * SAMPLE_STRIDE
    convergence = analyze_convergence(res['chi2_trace'], dt_sample)

    chi2_final = float(np.mean(res['chi2_trace'][-len(res['chi2_trace'])//4:]))
    chi2_GPU043 = 1.633e-04  # baseline from GPU-043 at T=1000

    print("\n" + "=" * 72)
    print("LONG-TIME FDT ANALYSIS")
    print("=" * 72)
    print(f"  <chi2>_final (last 25%)  = {chi2_final:.4e}")
    print(f"  <chi2>_GPU043 (T=1000)   = {chi2_GPU043:.4e}  (baseline)")
    print(f"  Ratio long/short          = {chi2_final/chi2_GPU043:.3f}")
    print(f"  Chunk-mean progression: {convergence['chunk_means']}")
    print(f"  Mean early 30%: {convergence['mean_early']:.4e}")
    print(f"  Mean late  30%: {convergence['mean_late']:.4e}")
    print(f"  Relative change: {convergence['relative_change']*100:.2f}%")

    if convergence['relative_change'] < 0.05:
        verdict = "H_CONVERGED"
        diag = (f"<chi²> reached plateau at {chi2_final:.3e}. "
                f"Ratio to GPU-043 baseline: {chi2_final/chi2_GPU043:.2f}x. "
                f"If ratio ≈ 1, FDT did NOT activate (source-limited persists "
                f"even at 15 mixing times). If ratio >> 1, dissipation-limited "
                f"regime reached — full gamma-scan worth doing.")
    elif convergence['mean_late'] > 2.0 * convergence['mean_early']:
        verdict = "H_STILL_GROWING"
        diag = (f"<chi²> still growing: early {convergence['mean_early']:.3e}, "
                f"late {convergence['mean_late']:.3e}. System has not yet "
                f"reached steady state; run even longer (T_meas=50000).")
    else:
        verdict = "H_OSCILLATING"
        diag = (f"<chi²> neither converged nor monotonically growing. "
                f"Possible slow oscillation or intermittent behavior.")

    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    np.savez(OUT_DIR / "trace.npz",
             chi2=res['chi2_trace'], M=res['M_trace'], H=res['H_samples'])
    json.dump({
        'config': {'L': L, 'R': 4, 'T_P1': T_P1, 'T_P2': T_P2,
                   'T_SPINUP': T_SPINUP, 'T_MEASURE': T_MEASURE, 'DT': DT,
                   'CHI_DECAY': CHI_DECAY, 'K_GM': K_GM,
                   'EXACT_A_MODE': EXACT_A_MODE,
                   'SAMPLE_STRIDE': SAMPLE_STRIDE},
        'chi2_final':       chi2_final,
        'chi2_GPU043_baseline': chi2_GPU043,
        'ratio_long_over_short': chi2_final / chi2_GPU043,
        'convergence_analysis': convergence,
        'H_drift':          res['H_drift'],
        'wall_sec':         res['wall_sec'],
        'verdict':          verdict,
        'diagnosis':        diag,
    }, open(OUT_DIR / "report.json", 'w'), indent=2, default=str)
    print(f"\nSaved: {OUT_DIR / 'report.json'}")
    print(f"       {OUT_DIR / 'trace.npz'}")


if __name__ == "__main__":
    main()
