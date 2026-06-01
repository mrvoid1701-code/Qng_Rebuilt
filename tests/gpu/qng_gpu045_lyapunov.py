"""QNG-GPU-045 — Lyapunov exponent on R1 orbital attractor.

Decisive diagnostic per Einstein-mind analysis (2026-04-24):

    lambda_max > 0 with fast mixing  ->  intrinsic stochasticity possible
                                         (Ruelle-Bowen path, hbar-emergent viable)
    lambda_max ~ 0 (quasi-periodic)  ->  KAM torus, no hbar at any parameter
                                         (confirms hbar is axiomatic at substrate)

Method: Benettin's algorithm with periodic renormalization.

  1. Reference trajectory x(t) from cached ring state
  2. Perturbed trajectory x(t) + delta_x(0), |delta_x(0)| = eps = 1e-8
  3. Every T_renorm = 10 lu:
       d_k = log(|delta_x(t_k)| / eps)
       delta_x(t_k) rescaled back to eps in direction of deviation
  4. lambda_max ~ sum(d_k) / t_total

Verdict:
  lambda_max > 1e-3 (per lu) -> H_CHAOTIC -> path forward for intrinsic ℏ
  lambda_max < 1e-4           -> H_QUASIPERIODIC -> ℏ axiomatic, no FDT closure possible
  1e-4 < lambda_max < 1e-3    -> H_MARGINAL -> needs larger L or longer run

Outputs: 07_validation/audits/qng-gpu045-lyapunov-v1/
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
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu045-lyapunov-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
L              = 20
R              = 4
T_P1           = 300.0
T_P2           = 1000.0
T_SPINUP       = 200.0   # let attractor settle before Lyapunov measurement
T_LYAPUNOV     = 2000.0  # 11 orbital periods of 185 lu
DT             = 0.025
T_RENORM_LU    = 10.0    # renormalize every 10 lu
EPS            = 1e-8    # perturbation magnitude
EXACT_A_MODE   = 'r1'
K_GM           = 0.01
CHI_DECAY      = 0.020
PROGRESS_EVERY = 2000


def state_to_vec(state):
    """Flatten state dict into a single vector for perturbation math."""
    return cp.concatenate([state['sg'], state['sm'], state['chi'], state['phi'],
                           state['pi_m'], state['pi_phi']])


def vec_to_state(v, L):
    N = L * L * L
    return {
        'sg':      v[0*N:1*N],
        'sm':      v[1*N:2*N],
        'chi':     v[2*N:3*N],
        'phi':     v[3*N:4*N],
        'pi_m':    v[4*N:5*N],
        'pi_phi':  v[5*N:6*N],
    }


def form_ring_and_spinup():
    print("  Phase 1+2 formation + spin-up", flush=True)
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT); n2 = int(T_P2 / DT); n_sp = int(T_SPINUP / DT)
    t0 = time.time()
    for step in range(n1):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=False,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            print(f"    [P1] {step+1}/{n1}  {(step+1)/(time.time()-t0):.0f} steps/s",
                  flush=True)
    for step in range(n2):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            rate = (n1+step+1)/(time.time()-t0)
            print(f"    [P2] {step+1}/{n2}  {rate:.0f} steps/s  ETA "
                  f"{(n2+n_sp-step-1)/rate:.0f}s", flush=True)
    for step in range(n_sp):
        state = yoshida4_step(state, DT, nb_idx, k_gm=K_GM,
                              chi_decay=CHI_DECAY, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if (step + 1) % PROGRESS_EVERY == 0:
            rate = (n1+n2+step+1)/(time.time()-t0)
            print(f"    [sp] {step+1}/{n_sp}  {rate:.0f} steps/s", flush=True)
    wall = time.time() - t0
    M = float(ring_mass_deficit(state['sm']))
    print(f"  Formation+spinup done ({n1+n2+n_sp} steps, {wall:.1f}s) M={M:.2f}",
          flush=True)
    return state, nb_idx


def run_lyapunov(state_ref, nb_idx):
    """Benettin's algorithm: parallel trajectories + periodic renormalization."""
    # Build perturbed state: add random direction * EPS
    cp.random.seed(137)
    v_ref = state_to_vec(state_ref)
    dim = v_ref.size
    # Perturbation direction: uniform in all sectors
    delta = cp.random.randn(dim)
    delta = EPS * delta / cp.linalg.norm(delta)
    v_pert = v_ref + delta
    state_pert = vec_to_state(v_pert.copy(), L)
    # Need to enforce clipping on sg, sm (bounded to [0,1] per v8 convention)
    state_pert['sg'] = cp.clip(state_pert['sg'], 0.0, 1.0)
    state_pert['sm'] = cp.clip(state_pert['sm'], 0.0, 1.0)

    steps_per_renorm = int(T_RENORM_LU / DT)
    n_renorms = int(T_LYAPUNOV / T_RENORM_LU)
    n_total = n_renorms * steps_per_renorm

    print(f"\n  Lyapunov run: T={T_LYAPUNOV} lu, {n_total} steps")
    print(f"    Renormalize every {T_RENORM_LU} lu = {steps_per_renorm} steps")
    print(f"    Number of renormalizations: {n_renorms}")
    print(f"    Initial perturbation: EPS={EPS}", flush=True)

    log_ratios = np.zeros(n_renorms, dtype=np.float64)
    M_ref_trace = np.zeros(n_renorms, dtype=np.float64)
    M_pert_trace = np.zeros(n_renorms, dtype=np.float64)

    t0 = time.time()
    for r_idx in range(n_renorms):
        # Evolve both for T_RENORM_LU
        for step in range(steps_per_renorm):
            state_ref = yoshida4_step(state_ref, DT, nb_idx, k_gm=K_GM,
                                       chi_decay=CHI_DECAY, v_couple_on=True,
                                       channel_f=True, exact_a=EXACT_A_MODE)
            state_pert = yoshida4_step(state_pert, DT, nb_idx, k_gm=K_GM,
                                        chi_decay=CHI_DECAY, v_couple_on=True,
                                        channel_f=True, exact_a=EXACT_A_MODE)
        # Measure separation
        v_r = state_to_vec(state_ref)
        v_p = state_to_vec(state_pert)
        delta_v = v_p - v_r
        delta_norm = float(cp.linalg.norm(delta_v).get())
        log_ratios[r_idx] = math.log(delta_norm / EPS) if delta_norm > 0 else 0.0
        # Renormalize: rescale perturbation back to EPS
        delta_v = EPS * delta_v / (delta_norm + 1e-30)
        v_p_new = v_r + delta_v
        state_pert = vec_to_state(v_p_new, L)
        state_pert['sg'] = cp.clip(state_pert['sg'], 0.0, 1.0)
        state_pert['sm'] = cp.clip(state_pert['sm'], 0.0, 1.0)

        M_ref_trace[r_idx] = float(ring_mass_deficit(state_ref['sm']))
        M_pert_trace[r_idx] = float(ring_mass_deficit(state_pert['sm']))

        if (r_idx + 1) % 20 == 0:
            elapsed = time.time() - t0
            rate = (r_idx + 1) / elapsed
            eta = (n_renorms - r_idx - 1) / rate
            cumulative_lambda = np.sum(log_ratios[:r_idx+1]) / ((r_idx + 1) * T_RENORM_LU)
            print(f"    [r={r_idx+1}/{n_renorms}]  t={((r_idx+1)*T_RENORM_LU):.0f} lu  "
                  f"log_ratio={log_ratios[r_idx]:+.4f}  "
                  f"lambda_cum={cumulative_lambda:+.5f}/lu  ETA {eta:.0f}s",
                  flush=True)

    wall = time.time() - t0
    # Final Lyapunov exponent
    lambda_max = np.sum(log_ratios) / T_LYAPUNOV
    # Also compute late-time average (discard first 20% transient)
    n_transient = n_renorms // 5
    lambda_late = np.sum(log_ratios[n_transient:]) / ((n_renorms - n_transient) * T_RENORM_LU)

    print(f"\n  Run done ({wall:.1f}s)", flush=True)
    return {
        'lambda_max':       lambda_max,
        'lambda_late':      lambda_late,
        'log_ratios':       log_ratios,
        'M_ref_trace':      M_ref_trace,
        'M_pert_trace':     M_pert_trace,
        'n_renorms':        n_renorms,
        'T_renorm_lu':      T_RENORM_LU,
        'eps':              EPS,
        'wall_sec':         wall,
    }


def main():
    print("=" * 72)
    print("QNG-GPU-045: Lyapunov exponent on R1 orbital attractor (R=4)")
    print("=" * 72)
    print(f"L={L}, R={R}, T_P1={T_P1}, T_P2={T_P2}, T_spinup={T_SPINUP}")
    print(f"T_Lyapunov={T_LYAPUNOV} lu (~{T_LYAPUNOV/185:.1f} orbital periods)")
    print(f"k_gm={K_GM}, chi_decay={CHI_DECAY}, exact_a={EXACT_A_MODE!r}")

    state, nb_idx = form_ring_and_spinup()
    result = run_lyapunov(state, nb_idx)

    print("\n" + "=" * 72)
    print("LYAPUNOV RESULTS")
    print("=" * 72)
    print(f"  lambda_max (all)   = {result['lambda_max']:+.5f} per lu")
    print(f"  lambda_late (last 80%) = {result['lambda_late']:+.5f} per lu")

    lm = result['lambda_late']
    if lm > 1e-3:
        verdict = "H_CHAOTIC"
        diag = (f"lambda_max = {lm:+.5f} > 1e-3 -> R1 attractor is CHAOTIC. "
                f"Intrinsic stochasticity via Ruelle-Bowen is possible. "
                f"Path forward for hbar-emergent exists: pursue ergodic "
                f"diffusion + FDT closure at higher L.")
    elif lm < 1e-4:
        verdict = "H_QUASIPERIODIC"
        diag = (f"lambda_max = {lm:+.5f} < 1e-4 -> R1 attractor is "
                f"QUASI-PERIODIC (KAM torus). No intrinsic chaos; no "
                f"effective stochasticity without external noise. Combined "
                f"with GPU-043 (deterministic FDT fail) and GPU-044 (vacuum "
                f"FDT fail), this confirms hbar is AXIOMATIC at the v8 "
                f"substrate boundary. V9-C (external hbar via path integral) "
                f"is the obligatory path. Alternative: v9-graphity (ontology "
                f"change to probabilistic graphs).")
    else:
        verdict = "H_MARGINAL"
        diag = (f"lambda_max = {lm:+.5f} in transitional regime (1e-4, 1e-3). "
                f"Needs larger L or longer T_Lyapunov to disambiguate.")
    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    # Save
    np.savez(OUT_DIR / "lyapunov_trace.npz",
             log_ratios=result['log_ratios'],
             M_ref=result['M_ref_trace'],
             M_pert=result['M_pert_trace'])
    json.dump({
        'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2,
        'T_SPINUP': T_SPINUP, 'T_LYAPUNOV': T_LYAPUNOV,
        'DT': DT, 'T_RENORM_LU': T_RENORM_LU, 'EPS': EPS,
        'K_GM': K_GM, 'CHI_DECAY': CHI_DECAY,
        'EXACT_A_MODE': EXACT_A_MODE,
        'lambda_max_all': float(result['lambda_max']),
        'lambda_late':    float(result['lambda_late']),
        'n_renorms':      int(result['n_renorms']),
        'wall_sec':       float(result['wall_sec']),
        'verdict':        verdict,
        'diagnosis':      diag,
    }, open(OUT_DIR / "report.json", 'w'), indent=2, default=str)
    print(f"\n  Saved: {OUT_DIR / 'report.json'}")
    print(f"         {OUT_DIR / 'lyapunov_trace.npz'}")


if __name__ == "__main__":
    main()
