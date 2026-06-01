"""QNG-GPU-046 — v9-P multiplicative-noise Langevin probe.

Pre-registration: 07_validation/prereg/QNG-GPU-046.md
Derivation:       04_qng_pure/qng-probabilistic-graph-v1.md (DER-QNG-056 draft)

Tests whether STATE-DEPENDENT noise (sigma depends on local sigma_m) closes
Einstein-Nyquist FDT where constant-amplitude noise (GPU-044) failed.

Langevin equation:
    dchi_i = [Channel D deterministic] - gamma*chi_i*dt + sigma(sigma_m_i)*sqrt(dt)*randn

with sigma²(sigma_m) = SIGMA_0² * (sigma_m / SIGMA_M_REF)^N_EXPONENT

Prediction (DER-QNG-056 §Analytical):
    <chi²>_local = sigma²(sigma_m)/(2*gamma)           (1/gamma scaling)
    hbar_local = 2*gamma*<chi²>_local / omega_orbit    (gamma-INVARIANT!)

If BOTH hold → v9-P mechanism validated.

Protocol:
  Part A: gamma in {0.010, 0.020, 0.040} at SIGMA_0=0.04, N=1 (linear)
  Part B: N in {0.5, 1.0, 2.0} at gamma=0.020 (functional form test)
  Part C: N=0 (constant sigma) — should replicate GPU-044 failure

Outputs: 07_validation/audits/qng-gpu046-v9p-langevin-v1/
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
    SIGMA_M_REF, CHI_DECAY_V7,
    build_nb, make_state, init_phi_single_ring,
    yoshida4_step, hamiltonian_v8, ring_mass_deficit,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu046-v9p-langevin-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
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

SIGMA_0        = 0.04
GAMMA_SCAN     = [0.010, 0.020, 0.040]
N_EXPONENT_SCAN = [0.5, 1.0, 2.0]


def ring_core_mask(L, R, z_ring=None, r_inner=None):
    """Return flat (L³,) boolean mask selecting ring-core region."""
    if z_ring is None:
        z_ring = L // 2
    if r_inner is None:
        r_inner = R + 2
    zz = cp.arange(L).reshape(1, 1, L)
    zz = cp.broadcast_to(zz, (L, L, L))
    return (cp.abs(zz - z_ring) <= r_inner).reshape(-1)


def vacuum_mask(L, R, z_ring=None):
    """Complement of ring-core region."""
    if z_ring is None:
        z_ring = L // 2
    zz = cp.arange(L).reshape(1, 1, L)
    zz = cp.broadcast_to(zz, (L, L, L))
    return (cp.abs(zz - z_ring) > (R + 4)).reshape(-1)


def form_ring_r1(L, R, T_P1, T_P2, DT, k_gm, chi_decay, verbose=True):
    """Fresh ring formation using DER-QNG-051 R1 protocol. No noise."""
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
            print(f"    [P1] {step+1}/{n1}  {(step+1)/(time.time()-t0):.0f} steps/s",
                  flush=True)
    for step in range(n2):
        state = yoshida4_step(state, DT, nb_idx, k_gm=k_gm,
                              chi_decay=chi_decay, v_couple_on=True,
                              channel_f=True, exact_a=EXACT_A_MODE)
        if verbose and (step + 1) % PROGRESS_EVERY == 0:
            rate = (n1+step+1)/(time.time()-t0)
            print(f"    [P2] {step+1}/{n2}  {rate:.0f} steps/s  ETA "
                  f"{(n2-step-1)/rate:.0f}s", flush=True)
    wall = time.time() - t0
    M = float(ring_mass_deficit(state['sm']))
    print(f"  Ring formed ({n1+n2} steps, {wall:.1f}s) M={M:.2f}", flush=True)
    return state, nb_idx


def run_langevin_v9p(state, nb_idx, k_gm, chi_decay, sigma_0, n_exp,
                      T_spinup, T_meas, dt, core_mask, vac_mask,
                      rng_seed=42, label=""):
    """Run v8 dynamics + multiplicative-noise kick on chi after each step.

    sigma_local[i] = sigma_0 * (sigma_m_i / SIGMA_M_REF)^(n_exp/2)

    Records:
      chi2_core[t]   = <chi²> averaged over ring-core region
      chi2_vacuum[t] = <chi²> averaged over vacuum region
      M_ring[t]      = ring mass deficit
    """
    cp.random.seed(rng_seed)
    n_spin = int(T_spinup / dt)
    n_meas = int(T_meas / dt)
    n_rec = n_meas // SAMPLE_STRIDE
    chi2_core  = np.zeros(n_rec, dtype=np.float64)
    chi2_vac   = np.zeros(n_rec, dtype=np.float64)
    M_trace    = np.zeros(n_rec, dtype=np.float64)
    H_trace    = np.zeros(12, dtype=np.float64)
    H_idx_step = max(1, n_meas // 10)
    N_total = float(L ** 3)
    N_core = float(cp.sum(core_mask).get())
    N_vac  = float(cp.sum(vac_mask).get())
    n_chi = state['chi'].size

    t0 = time.time()
    # ---- spinup with noise ----
    for step in range(n_spin):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        # State-dependent multiplicative noise
        sigma_local = sigma_0 * cp.power(cp.maximum(state['sm'] / SIGMA_M_REF, 1e-10),
                                          n_exp / 2.0)
        state['chi'] = state['chi'] + sigma_local * math.sqrt(dt) * cp.random.randn(n_chi)
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (step + 1) / elapsed
            eta = (n_spin + n_meas - step - 1) / rate
            chi2_core_now = float(cp.sum(core_mask * state['chi']**2).get()) / N_core
            chi2_vac_now  = float(cp.sum(vac_mask * state['chi']**2).get()) / N_vac
            M_now = float(ring_mass_deficit(state['sm']))
            print(f"    [{label}|spin] {step+1}/{n_spin}  {rate:.0f} steps/s "
                  f"ETA {eta:.0f}s  <chi2>_c={chi2_core_now:.3e} "
                  f"<chi2>_v={chi2_vac_now:.3e} M={M_now:.1f}",
                  flush=True)

    H0 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                              exact_a=EXACT_A_MODE))
    H_trace[0] = H0

    # ---- measurement ----
    rec_idx = 0
    for step in range(n_meas):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        sigma_local = sigma_0 * cp.power(cp.maximum(state['sm'] / SIGMA_M_REF, 1e-10),
                                          n_exp / 2.0)
        state['chi'] = state['chi'] + sigma_local * math.sqrt(dt) * cp.random.randn(n_chi)
        if step % SAMPLE_STRIDE == 0 and rec_idx < n_rec:
            chi2_core[rec_idx] = float(cp.sum(core_mask * state['chi']**2).get()) / N_core
            chi2_vac[rec_idx]  = float(cp.sum(vac_mask * state['chi']**2).get()) / N_vac
            M_trace[rec_idx]   = float(ring_mass_deficit(state['sm']))
            rec_idx += 1
        if (step % H_idx_step) == 0 and step // H_idx_step < len(H_trace):
            H_trace[step // H_idx_step] = float(
                hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                               exact_a=EXACT_A_MODE))
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (n_spin + step + 1) / elapsed
            eta = (n_spin + n_meas - n_spin - step - 1) / rate
            print(f"    [{label}|meas] {step+1}/{n_meas}  {rate:.0f} steps/s "
                  f"ETA {eta:.0f}s  <chi2>_c={chi2_core[max(0,rec_idx-1)]:.3e} "
                  f"<chi2>_v={chi2_vac[max(0,rec_idx-1)]:.3e} "
                  f"M={M_trace[max(0,rec_idx-1)]:.1f}", flush=True)

    wall = time.time() - t0
    H_end = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                                 exact_a=EXACT_A_MODE))
    H_drift = abs(H_end - H0) / max(abs(H0), 1e-10)
    print(f"  [{label}] {n_spin+n_meas} steps, {wall:.1f}s  H_drift={H_drift:.2%}")
    return {
        'chi2_core_trace': chi2_core[:rec_idx],
        'chi2_vac_trace':  chi2_vac[:rec_idx],
        'M_trace':         M_trace[:rec_idx],
        'H_trace':         H_trace,
        'wall_sec':        wall, 'H0': H0, 'H_end': H_end, 'H_drift': H_drift,
    }


def omega_orbit_from_M(M_trace, dt_sample):
    x = M_trace - M_trace.mean(); N = len(x)
    if N < 100 or np.std(x) < 1e-8:
        return float('nan'), float('nan')
    ac = np.correlate(x, x, mode='full')[N - 1:]
    ac /= ac[0]
    zc = None
    for i in range(1, N - 1):
        if ac[i - 1] > 0 >= ac[i]:
            zc = i; break
    if zc is None: zc = 1
    peak_idx = None; peak_val = -np.inf
    for i in range(zc + 1, min(N - 1, zc + N // 2)):
        if ac[i - 1] < ac[i] > ac[i + 1] and ac[i] > 0.05:
            if ac[i] > peak_val:
                peak_val = ac[i]; peak_idx = i; break
    if peak_idx is None:
        freqs = np.fft.rfftfreq(N, d=dt_sample)
        fft_mag = np.abs(np.fft.rfft(x))
        if len(freqs) > 3:
            lo = 3
            peak_bin = lo + int(np.argmax(fft_mag[lo:]))
            f_peak = freqs[peak_bin]
            if f_peak > 0:
                T_cycle = 1.0 / f_peak
                return T_cycle, 2.0 * math.pi / T_cycle
        return float('nan'), float('nan')
    T_cycle = peak_idx * dt_sample
    return T_cycle, 2.0 * math.pi / T_cycle


def run_one(R, chi_decay, sigma_0, n_exp, rng_seed, label=""):
    print(f"\n=== {label}  R={R}  gamma={chi_decay}  sigma_0={sigma_0}  n={n_exp} ===")
    state, nb_idx = form_ring_r1(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT,
                                  k_gm=K_GM, chi_decay=chi_decay, verbose=True)
    core_mask = ring_core_mask(L, R)
    vac_mask  = vacuum_mask(L, R)

    res = run_langevin_v9p(state, nb_idx, K_GM, chi_decay, sigma_0, n_exp,
                            T_SPINUP, T_MEASURE, DT, core_mask, vac_mask,
                            rng_seed=rng_seed, label=label)

    dt_sample = DT * SAMPLE_STRIDE
    T_cycle, omega = omega_orbit_from_M(res['M_trace'], dt_sample)
    chi2_core = float(res['chi2_core_trace'].mean())
    chi2_vac  = float(res['chi2_vac_trace'].mean())
    M_mean    = float(res['M_trace'].mean())
    M_std     = float(res['M_trace'].std())

    hbar_core = 2.0 * chi_decay * chi2_core / omega if (omega > 0 and math.isfinite(omega)) else 0.0
    hbar_vac  = 2.0 * chi_decay * chi2_vac  / omega if (omega > 0 and math.isfinite(omega)) else 0.0

    row = {
        'label': label, 'R': R, 'chi_decay': chi_decay,
        'sigma_0': sigma_0, 'n_exp': n_exp, 'L': L, 'k_gm': K_GM,
        'exact_a': EXACT_A_MODE, 'rng_seed': rng_seed,
        'T_cycle': T_cycle, 'omega_orbit': omega,
        'mean_chi2_core': chi2_core, 'mean_chi2_vac': chi2_vac,
        'M_mean': M_mean, 'M_std': M_std,
        'H_drift': res['H_drift'],
        'hbar_cand_core': hbar_core, 'hbar_cand_vac': hbar_vac,
        'wall_sec': res['wall_sec'],
    }
    np.savez(OUT_DIR / f"traces_{label}.npz",
             chi2_core=res['chi2_core_trace'], chi2_vac=res['chi2_vac_trace'],
             M=res['M_trace'], H=res['H_trace'])
    print(f"  -> T_cycle={T_cycle:.2f}  omega={omega:.5f}")
    print(f"     <chi2>_core = {chi2_core:.4e}   hbar_core = {hbar_core:.4e}")
    print(f"     <chi2>_vac  = {chi2_vac:.4e}    hbar_vac  = {hbar_vac:.4e}")
    return row


def main():
    print("=" * 72)
    print(f"QNG-GPU-046: v9-P multiplicative-noise Langevin")
    print("=" * 72)
    print(f"L={L}, SIGMA_0={SIGMA_0}, gamma_scan={GAMMA_SCAN}")
    print(f"n_exponent_scan={N_EXPONENT_SCAN}")

    rows_gamma = []
    rows_n = []
    rows_ctrl = []

    # Part A: gamma-scan at N=1 (linear)
    print("\n\n### PART A: gamma-scan at N=1 (linear state-dependence) ###")
    for i, gamma in enumerate(GAMMA_SCAN):
        row = run_one(R=4, chi_decay=gamma, sigma_0=SIGMA_0, n_exp=1.0,
                      rng_seed=42 + i,
                      label=f"A_R4_gamma{gamma:.3f}_n1.0")
        rows_gamma.append(row)

    # Part B: n-scan at gamma=0.020
    print("\n\n### PART B: n-scan at gamma=0.020 ###")
    for i, n_exp in enumerate(N_EXPONENT_SCAN):
        if abs(n_exp - 1.0) < 1e-9:
            # already have this one from Part A
            r = next((r for r in rows_gamma if abs(r['chi_decay']-0.020)<1e-9), None)
            if r is not None:
                copy = dict(r); copy['label'] = f"B_R4_gamma0.020_n{n_exp}"
                rows_n.append(copy); continue
        row = run_one(R=4, chi_decay=0.020, sigma_0=SIGMA_0, n_exp=n_exp,
                      rng_seed=52 + i,
                      label=f"B_R4_gamma0.020_n{n_exp}")
        rows_n.append(row)

    # Part C: control N=0 (constant sigma — should fail like GPU-044)
    print("\n\n### PART C: control N=0 (constant sigma) ###")
    row = run_one(R=4, chi_decay=0.020, sigma_0=SIGMA_0, n_exp=0.0,
                  rng_seed=99, label=f"C_R4_gamma0.020_n0")
    rows_ctrl.append(row)

    # ----- write CSVs -----
    def write_csv(path, rows):
        if not rows: return
        keys = list(rows[0].keys())
        with open(path, 'w') as f:
            f.write(",".join(keys) + "\n")
            for r in rows:
                f.write(",".join(str(r[k]) for k in keys) + "\n")
        print(f"wrote {path}")

    write_csv(OUT_DIR / "gamma_scan.csv", rows_gamma)
    write_csv(OUT_DIR / "n_scan.csv", rows_n)
    write_csv(OUT_DIR / "control.csv", rows_ctrl)

    # Analysis: γ-invariance of hbar_cand
    def cv(xs):
        xs = [x for x in xs if math.isfinite(x) and x > 0]
        if len(xs) < 2: return float('nan')
        mu = np.mean(xs)
        return float(np.std(xs, ddof=1) / mu) if mu != 0 else float('nan')

    hbars_core_gamma = [r['hbar_cand_core'] for r in rows_gamma]
    hbars_vac_gamma  = [r['hbar_cand_vac']  for r in rows_gamma]
    cv_core = cv(hbars_core_gamma)
    cv_vac  = cv(hbars_vac_gamma)
    mean_core = np.mean(hbars_core_gamma)
    mean_vac  = np.mean(hbars_vac_gamma)

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"gamma-scan (core):   {hbars_core_gamma}")
    print(f"gamma-scan (vacuum): {hbars_vac_gamma}")
    print(f"CV(core)   = {cv_core*100:.2f}%")
    print(f"CV(vacuum) = {cv_vac*100:.2f}%")
    print(f"mean hbar_cand_core   = {mean_core:.4e}")
    print(f"mean hbar_cand_vac    = {mean_vac:.4e}")
    print(f"ratio core/vac        = {mean_core/mean_vac if mean_vac!=0 else 'nan':.3f}")

    # Verdict
    if math.isfinite(cv_core) and math.isfinite(cv_vac):
        if cv_core < 0.02 and cv_vac < 0.02:
            if abs(mean_core - mean_vac) / max(mean_core, mean_vac) < 0.05:
                verdict = "V9P_PASS"
                diag = (f"hbar_cand gamma-invariant in both core and vacuum "
                        f"(CV core {cv_core*100:.2f}%, vac {cv_vac*100:.2f}%) "
                        f"AND core ≈ vacuum -> universal hbar. "
                        f"DER-QNG-056 upgraded from draft to confirmed.")
            else:
                verdict = "V9P_LOCAL_OK"
                diag = (f"hbar_cand gamma-invariant locally (CV core "
                        f"{cv_core*100:.2f}%, vac {cv_vac*100:.2f}%) but "
                        f"core ({mean_core:.4e}) != vacuum ({mean_vac:.4e}). "
                        f"Local hbar prediction confirmed.")
        elif cv_core < 0.10 and cv_vac < 0.10:
            verdict = "V9P_MARGINAL"
            diag = (f"CV in (2%, 10%) range. Partial closure — may need "
                    f"longer T_meas or different sigma_0.")
        else:
            verdict = "V9P_FAIL"
            diag = (f"CV too high (core {cv_core*100:.2f}%, vac {cv_vac*100:.2f}%). "
                    f"State-dependent noise does not close FDT.")
    else:
        verdict = "V9P_INCONCLUSIVE"
        diag = "Measurement invalid"

    print(f"\nVerdict: {verdict}")
    print(f"Diagnosis: {diag}")

    json.dump({
        'rows_gamma': rows_gamma, 'rows_n': rows_n, 'rows_ctrl': rows_ctrl,
        'cv_core': cv_core, 'cv_vac': cv_vac,
        'mean_hbar_core': float(mean_core), 'mean_hbar_vac': float(mean_vac),
        'verdict': verdict, 'diagnosis': diag,
        'config': {
            'L': L, 'T_P1': T_P1, 'T_P2': T_P2,
            'T_SPINUP': T_SPINUP, 'T_MEASURE': T_MEASURE, 'DT': DT,
            'K_GM': K_GM, 'EXACT_A_MODE': EXACT_A_MODE,
            'SIGMA_0': SIGMA_0, 'GAMMA_SCAN': GAMMA_SCAN,
            'N_EXPONENT_SCAN': N_EXPONENT_SCAN,
        },
    }, open(OUT_DIR / "summary.json", 'w'), indent=2, default=str)
    print(f"wrote {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
