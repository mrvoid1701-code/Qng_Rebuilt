"""QNG-GPU-048 — v9-E edge-noise intermediate test.

Pre-registration: 07_validation/prereg/QNG-GPU-048.md

Tests whether injecting noise into the discrete Laplacian operator
(equivalent to random edge weight fluctuations) closes Einstein-Nyquist
FDT where direct noise on χ (GPU-044) and state-dependent noise on χ
(GPU-046 v9-P) failed.

Implementation approximation: after each Yoshida4 step, apply a small
RANDOM diffusion kernel to σ_g, σ_m, χ simultaneously. Random direction
differs at each node each step. This is the simplest implementation of
"fluctuating Laplacian operator" without rewriting v8 core module.

    field_new = field + sigma_edge * sqrt(dt) * random_laplacian(field)

where random_laplacian applies noise-weighted neighbor differences.

Protocol:
  sigma_edge ∈ {0.05, 0.10} × γ ∈ {0.010, 0.020, 0.040} = 6 runs
  Plus control: sigma_edge=0 at γ=0.020 (replicates GPU-043 baseline).

Outputs: 07_validation/audits/qng-gpu048-edge-noise-v1/
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
    yoshida4_step, hamiltonian_v8, ring_mass_deficit, nb_mean,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu048-edge-noise-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

L              = 20
T_P1           = 300.0
T_P2           = 1000.0
T_SPINUP       = 200.0
T_MEASURE      = 1000.0
DT             = 0.025
SAMPLE_STRIDE  = 4
PROGRESS_EVERY = 2000
EXACT_A_MODE   = 'r1'
K_GM           = 0.01

SIGMA_EDGE_SCAN = [0.05, 0.10]
GAMMA_SCAN      = [0.010, 0.020, 0.040]


def apply_edge_noise(state, nb_idx, sigma_edge, dt, rng_state):
    """Apply random-diffusion-kernel noise to fields after a Yoshida step.

    For each of (sg, sm, chi):
      field_noisy[i] = field[i] + sigma_edge * sqrt(dt) * xi[i] * (field_bar[i] - field[i])

    where xi[i] is i.i.d. N(0,1) per site per step, and field_bar[i] is
    the neighbor mean.

    This is equivalent to a fluctuating diffusion coefficient: each site
    has a random "effective kappa" multiplying the Laplacian.
    """
    scale = sigma_edge * math.sqrt(dt)
    for key in ('sg', 'sm', 'chi'):
        field = state[key]
        field_bar = nb_mean(field, nb_idx)
        xi = cp.random.randn(field.size)
        state[key] = field + scale * xi * (field_bar - field)
        if key in ('sg', 'sm'):
            state[key] = cp.clip(state[key], 0.0, 1.0)
    return state


def form_ring(L, R, k_gm, chi_decay, verbose=True):
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT); n2 = int(T_P2 / DT)
    t0 = time.time()
    for step in range(n1):
        state = yoshida4_step(state, DT, nb_idx, k_gm=k_gm,
                              chi_decay=chi_decay, v_couple_on=False,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if verbose and (step + 1) % PROGRESS_EVERY == 0:
            print(f"    [P1] {step+1}/{n1}", flush=True)
    for step in range(n2):
        state = yoshida4_step(state, DT, nb_idx, k_gm=k_gm,
                              chi_decay=chi_decay, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if verbose and (step + 1) % PROGRESS_EVERY == 0:
            rate = (n1+step+1)/(time.time()-t0)
            print(f"    [P2] {step+1}/{n2}  {rate:.0f} steps/s  ETA "
                  f"{(n2-step-1)/rate:.0f}s", flush=True)
    M = float(ring_mass_deficit(state['sm']))
    print(f"  Ring formed ({n1+n2} steps, {time.time()-t0:.1f}s) M={M:.2f}",
          flush=True)
    return state, nb_idx


def run_with_edge_noise(state, nb_idx, k_gm, chi_decay, sigma_edge,
                         T_spin, T_meas, dt, rng_seed=42, label=""):
    cp.random.seed(rng_seed)
    n_spin = int(T_spin / dt); n_meas = int(T_meas / dt)
    n_rec = n_meas // SAMPLE_STRIDE
    chi2_trace = np.zeros(n_rec, dtype=np.float64)
    M_trace    = np.zeros(n_rec, dtype=np.float64)
    N_total = float(L ** 3)

    t0 = time.time()
    for step in range(n_spin):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if sigma_edge > 0:
            state = apply_edge_noise(state, nb_idx, sigma_edge, dt, None)
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (step + 1) / elapsed
            eta = (n_spin + n_meas - step - 1) / rate
            chi2_now = float(cp.sum(state['chi'] ** 2).get()) / N_total
            M_now = float(ring_mass_deficit(state['sm']))
            print(f"    [{label}|spin] {step+1}/{n_spin}  {rate:.0f} steps/s "
                  f"ETA {eta:.0f}s  <chi2>={chi2_now:.3e} M={M_now:.1f}",
                  flush=True)

    H0 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                              exact_a=EXACT_A_MODE))
    rec_idx = 0
    for step in range(n_meas):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if sigma_edge > 0:
            state = apply_edge_noise(state, nb_idx, sigma_edge, dt, None)
        if step % SAMPLE_STRIDE == 0 and rec_idx < n_rec:
            chi2_trace[rec_idx] = float(cp.sum(state['chi'] ** 2).get()) / N_total
            M_trace[rec_idx] = float(ring_mass_deficit(state['sm']))
            rec_idx += 1
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (n_spin + step + 1) / elapsed
            eta = (n_spin + n_meas - n_spin - step - 1) / rate
            print(f"    [{label}|meas] {step+1}/{n_meas}  {rate:.0f} steps/s "
                  f"ETA {eta:.0f}s  <chi2>={chi2_trace[max(0,rec_idx-1)]:.3e} "
                  f"M={M_trace[max(0,rec_idx-1)]:.1f}", flush=True)

    wall = time.time() - t0
    H_end = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                                 exact_a=EXACT_A_MODE))
    H_drift = abs(H_end - H0) / max(abs(H0), 1e-10)
    print(f"  [{label}] {wall:.1f}s  H_drift={H_drift:.2%}", flush=True)
    return {
        'chi2_trace': chi2_trace[:rec_idx], 'M_trace': M_trace[:rec_idx],
        'H0': H0, 'H_end': H_end, 'H_drift': H_drift, 'wall_sec': wall,
    }


def omega_from_M(M_trace, dt_sample):
    x = M_trace - M_trace.mean(); N = len(x)
    if N < 100 or np.std(x) < 1e-8:
        return float('nan'), float('nan')
    ac = np.correlate(x, x, mode='full')[N-1:]; ac /= ac[0]
    zc = None
    for i in range(1, N-1):
        if ac[i-1] > 0 >= ac[i]:
            zc = i; break
    if zc is None: zc = 1
    peak_idx = None; peak_val = -np.inf
    for i in range(zc+1, min(N-1, zc+N//2)):
        if ac[i-1] < ac[i] > ac[i+1] and ac[i] > 0.05:
            if ac[i] > peak_val: peak_val = ac[i]; peak_idx = i; break
    if peak_idx is None:
        freqs = np.fft.rfftfreq(N, d=dt_sample); fft_mag = np.abs(np.fft.rfft(x))
        if len(freqs) > 3:
            lo = 3; peak_bin = lo + int(np.argmax(fft_mag[lo:]))
            f_peak = freqs[peak_bin]
            if f_peak > 0: return 1.0/f_peak, 2.0*math.pi*f_peak
        return float('nan'), float('nan')
    T = peak_idx * dt_sample
    return T, 2.0*math.pi/T


def run_one(R, chi_decay, sigma_edge, rng_seed, label=""):
    print(f"\n=== {label}  R={R}  gamma={chi_decay}  sigma_edge={sigma_edge} ===")
    state, nb_idx = form_ring(L, R, K_GM, chi_decay)
    res = run_with_edge_noise(state, nb_idx, K_GM, chi_decay, sigma_edge,
                               T_SPINUP, T_MEASURE, DT,
                               rng_seed=rng_seed, label=label)
    dt_sample = DT * SAMPLE_STRIDE
    T_cycle, omega = omega_from_M(res['M_trace'], dt_sample)
    chi2_mean = float(res['chi2_trace'].mean())
    M_mean = float(res['M_trace'].mean()); M_std = float(res['M_trace'].std())
    hbar = 2.0 * chi_decay * chi2_mean / omega if (omega > 0 and math.isfinite(omega)) else 0.0
    row = {
        'label': label, 'R': R, 'chi_decay': chi_decay,
        'sigma_edge': sigma_edge, 'L': L, 'rng_seed': rng_seed,
        'T_cycle': T_cycle, 'omega_orbit': omega,
        'mean_chi2': chi2_mean, 'M_mean': M_mean, 'M_std': M_std,
        'H_drift': res['H_drift'], 'hbar_candidate': hbar,
        'wall_sec': res['wall_sec'],
    }
    np.savez(OUT_DIR / f"traces_{label}.npz",
             chi2=res['chi2_trace'], M=res['M_trace'])
    print(f"  -> T={T_cycle:.2f} omega={omega:.5f} <chi2>={chi2_mean:.3e} "
          f"M={M_mean:.1f}±{M_std:.1f} hbar={hbar:.4e}")
    return row


def main():
    print("=" * 72)
    print("QNG-GPU-048: v9-E edge-noise FDT test")
    print(f"sigma_edge_scan={SIGMA_EDGE_SCAN}, gamma_scan={GAMMA_SCAN}")
    print("=" * 72)

    rows = []
    # Control: sigma_edge=0 at baseline gamma=0.020 (replicates GPU-043)
    rows.append(run_one(R=4, chi_decay=0.020, sigma_edge=0.0,
                         rng_seed=1, label="ctrl_R4_sigma0_gamma0.020"))
    # Main scan
    for si, sigma_edge in enumerate(SIGMA_EDGE_SCAN):
        for gi, gamma in enumerate(GAMMA_SCAN):
            rows.append(run_one(R=4, chi_decay=gamma, sigma_edge=sigma_edge,
                                 rng_seed=10+si*10+gi,
                                 label=f"R4_sigma{sigma_edge}_gamma{gamma}"))

    # CSV
    keys = list(rows[0].keys())
    with open(OUT_DIR / "edge_noise_scan.csv", 'w') as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(str(r[k]) for k in keys) + "\n")
    print(f"\nwrote {OUT_DIR / 'edge_noise_scan.csv'}")

    # Analysis per sigma_edge: CV across gamma
    def cv(xs):
        xs = [x for x in xs if math.isfinite(x) and x > 0]
        if len(xs) < 2: return float('nan')
        mu = np.mean(xs)
        return float(np.std(xs, ddof=1) / mu) if mu != 0 else float('nan')

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for sigma_edge in [0.0] + SIGMA_EDGE_SCAN:
        hbars = [r['hbar_candidate'] for r in rows
                 if abs(r['sigma_edge'] - sigma_edge) < 1e-9
                 and r['chi_decay'] != 0.020 or sigma_edge > 0]
        # For sigma=0 we only have one gamma, skip CV
        if sigma_edge == 0.0:
            print(f"  sigma_edge=0.0 (control): hbar={rows[0]['hbar_candidate']:.4e}")
            continue
        gamma_hbars = sorted([(r['chi_decay'], r['hbar_candidate']) for r in rows
                              if abs(r['sigma_edge'] - sigma_edge) < 1e-9])
        print(f"  sigma_edge={sigma_edge}: {gamma_hbars}")
        cv_val = cv([h for _, h in gamma_hbars])
        print(f"    CV = {cv_val*100:.2f}%" if math.isfinite(cv_val) else "    CV = NaN")

    json.dump({
        'rows': rows,
        'config': {'L': L, 'K_GM': K_GM, 'EXACT_A_MODE': EXACT_A_MODE,
                   'SIGMA_EDGE_SCAN': SIGMA_EDGE_SCAN, 'GAMMA_SCAN': GAMMA_SCAN},
    }, open(OUT_DIR / "summary.json", 'w'), indent=2, default=str)


if __name__ == "__main__":
    main()
