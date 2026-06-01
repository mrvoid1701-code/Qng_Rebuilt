"""QNG-GPU-044 — Vacuum-sourced FDT probe (hbar candidate via stochastic vacuum).

Extension of GPU-043 (which falsified deterministic-only two-channel FDT as
route to emergent hbar) testing Gabriel's stochastic-vacuum hypothesis:

    QNG substrate sits on a quantum vacuum providing ontological white noise
    that drives chi through Channel D. With this external stochasticity,
    Einstein-Nyquist cancellation closes:

        <chi^2> = sigma_vac^2 * dt / (2*gamma)

    so that

        hbar_cand = 2*gamma*<chi^2>/omega = sigma_vac^2*dt/omega

    is gamma-invariant by construction.

This is a CALIBRATION test, not a derivation: sigma_vac is an INPUT parameter
representing vacuum noise amplitude. If the result confirms gamma-invariance,
it shows that QNG + stochastic vacuum = emergent hbar-like behavior, which
is the SED (Stochastic Electrodynamics) conjecture applied to a discrete
substrate.

Protocol:
  gamma-scan {0.010, 0.020, 0.040} at R=4, L=20, same as GPU-043.
  sigma_vac = 0.04 fixed (~10x deterministic <chi^2>).

Expected outcomes:
  (A) hbar_cand identical across gamma (CV < 2%) -> SCENARIO (a) ON BACKDOOR:
      vacuum-layer hypothesis validated; hbar_cand derivation is now
      "sigma_vac^2*dt/omega" = configuration-dependent but gamma-invariant.
  (B) hbar_cand different across gamma -> vacuum-layer hypothesis fails,
      stochasticity alone insufficient (e.g. noise too small, or ring destroyed).

Outputs: 07_validation/audits/qng-gpu044-vacuum-fdt-v1/
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
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu044-vacuum-fdt-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Configuration (mirrors GPU-043 for direct comparison)
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

# --- NEW: vacuum-noise amplitude ---
# sigma_vac is the white-noise std added to chi after each Yoshida step,
# representing a bath-like stochastic vacuum coupled to the chi sector.
# Calibrated so that vacuum contribution dominates deterministic (~1.6e-04):
#   <chi^2>_vac = sigma_vac^2 * dt / (2*gamma)
#   at gamma=0.020, dt=0.025: sigma_vac=0.04 -> <chi^2>_vac ~1.0e-03 (6x det)
SIGMA_VAC      = 0.04

GAMMA_SCAN     = [0.010, 0.020, 0.040]


def ring_core_mask(L, R, z_ring=None):
    if z_ring is None:
        z_ring = L // 2
    zz = cp.arange(L).reshape(1, 1, L)
    zz = cp.broadcast_to(zz, (L, L, L))
    return (cp.abs(zz - z_ring) <= (R + 2)).reshape(-1)


def form_ring_r1_no_noise(L, R, T_P1, T_P2, DT, k_gm, chi_decay, verbose=True):
    """Form ring WITHOUT vacuum noise (clean orbital attractor setup)."""
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
    chi2 = float(cp.sum(state['chi'] ** 2).get()) / (L ** 3)
    sg_std = float(cp.std(state['sg']).get())
    print(f"  Ring formed ({n1+n2} steps, {wall:.1f}s) M={M:.2f} "
          f"<chi^2>={chi2:.3e} std(sg)={sg_std:.4e}", flush=True)
    return state, nb_idx


def run_with_vacuum(state, nb_idx, k_gm, chi_decay, sigma_vac, T_spinup,
                     T_meas, dt, core_mask, rng_seed=42, label=""):
    """Run with vacuum noise Xi(t) injected into chi after each step.

    Noise model: after each yoshida4 step, add sqrt(dt)*sigma_vac*N(0,1) to
    every chi site independently. This implements Stratonovich white noise
    on chi with std(Xi)=sigma_vac per unit time; the sqrt(dt) is the
    Euler-Maruyama scale so that <chi^2>_eq = sigma_vac^2 * dt / (2*gamma).
    (Actually, post-step kick: <chi^2> = sigma_vac^2 * dt / (2*gamma) after
    continuous integration; discrete step adds +sigma_vac^2*dt per step,
    accumulated to equilibrium against the -gamma*chi decay.)
    """
    cp.random.seed(rng_seed)
    n_spin = int(T_spinup / dt)
    n_meas = int(T_meas / dt)
    n_rec = n_meas // SAMPLE_STRIDE
    chi2_trace = np.zeros(n_rec, dtype=np.float64)
    sm2_trace  = np.zeros(n_rec, dtype=np.float64)
    M_trace    = np.zeros(n_rec, dtype=np.float64)
    H_trace    = np.zeros(12, dtype=np.float64)
    H_idx_step = max(1, n_meas // 10)
    N_total = float(L ** 3); N_core = float(cp.sum(core_mask).get())
    noise_scale = math.sqrt(dt) * sigma_vac
    n_chi = state['chi'].size

    t0 = time.time()
    # ---- spinup with noise ----
    for step in range(n_spin):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        # Xi(t) kick on chi
        state['chi'] = state['chi'] + noise_scale * cp.random.randn(n_chi)
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (step + 1) / elapsed
            eta = (n_spin + n_meas - step - 1) / rate
            chi2_now = float(cp.sum(state['chi'] ** 2).get()) / N_total
            M_now = float(ring_mass_deficit(state['sm']))
            print(f"    [{label}|spin] {step+1}/{n_spin}  {rate:.0f} steps/s  "
                  f"ETA {eta:.0f}s  <chi2>={chi2_now:.3e} M={M_now:.1f}",
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
        state['chi'] = state['chi'] + noise_scale * cp.random.randn(n_chi)
        if step % SAMPLE_STRIDE == 0 and rec_idx < n_rec:
            chi2_trace[rec_idx] = float(cp.sum(state['chi'] ** 2).get()) / N_total
            sm2_trace[rec_idx]  = float(cp.sum(core_mask * state['sm'] ** 2).get()) / N_core
            M_trace[rec_idx]    = float(ring_mass_deficit(state['sm']))
            rec_idx += 1
        if (step % H_idx_step) == 0 and step // H_idx_step < len(H_trace):
            H_trace[step // H_idx_step] = float(
                hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                               exact_a=EXACT_A_MODE))
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            total_step = n_spin + step + 1
            rate = total_step / elapsed
            eta = (n_spin + n_meas - total_step) / rate
            print(f"    [{label}|meas] {step+1}/{n_meas}  {rate:.0f} steps/s  "
                  f"ETA {eta:.0f}s  <chi2>={chi2_trace[max(0,rec_idx-1)]:.3e} "
                  f"M={M_trace[max(0,rec_idx-1)]:.1f}", flush=True)

    wall = time.time() - t0
    H_end = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                                 exact_a=EXACT_A_MODE))
    H_drift = abs(H_end - H0) / max(abs(H0), 1e-10)
    print(f"  [{label}] {n_spin+n_meas} steps, {wall:.1f}s  H_drift={H_drift:.2%}")
    return {
        'chi2_trace': chi2_trace[:rec_idx], 'sm2_trace': sm2_trace[:rec_idx],
        'M_trace': M_trace[:rec_idx], 'H_trace': H_trace,
        'wall_sec': wall, 'H0': H0, 'H_end': H_end, 'H_drift': H_drift,
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


def run_one(R, chi_decay, sigma_vac, rng_seed, label=""):
    print(f"\n=== {label}  R={R}  gamma={chi_decay}  sigma_vac={sigma_vac} ===")
    state, nb_idx = form_ring_r1_no_noise(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT,
                                           k_gm=K_GM, chi_decay=chi_decay,
                                           verbose=True)
    core_mask = ring_core_mask(L, R)

    res = run_with_vacuum(state, nb_idx, K_GM, chi_decay, sigma_vac,
                          T_SPINUP, T_MEASURE, DT, core_mask,
                          rng_seed=rng_seed, label=label)

    dt_sample = DT * SAMPLE_STRIDE
    T_cycle, omega = omega_orbit_from_M(res['M_trace'], dt_sample)
    half = len(res['chi2_trace']) // 2
    chi2_mean_all = float(res['chi2_trace'].mean())
    chi2_mean_h1  = float(res['chi2_trace'][:half].mean()) if half > 0 else chi2_mean_all
    chi2_mean_h2  = float(res['chi2_trace'][half:].mean()) if half > 0 else chi2_mean_all
    chi2_convergence = abs(chi2_mean_h2 - chi2_mean_h1) / max(abs(chi2_mean_all), 1e-20)
    sm2_mean = float(res['sm2_trace'].mean())
    M_mean   = float(res['M_trace'].mean())
    M_std    = float(res['M_trace'].std())

    hbar_candidate = 2.0 * chi_decay * chi2_mean_all / omega if (
        math.isfinite(omega) and omega > 0) else 0.0

    # FDT theoretical prediction: <chi^2>_vac = sigma_vac^2 * dt / (2*gamma)
    chi2_theory = sigma_vac * sigma_vac * DT / (2.0 * chi_decay)
    hbar_theory = sigma_vac * sigma_vac * DT / omega if (
        math.isfinite(omega) and omega > 0) else 0.0

    row = {
        'label': label, 'R': R, 'chi_decay': chi_decay, 'sigma_vac': sigma_vac,
        'L': L, 'k_gm': K_GM, 'exact_a': EXACT_A_MODE, 'rng_seed': rng_seed,
        'T_cycle': T_cycle, 'omega_orbit': omega,
        'mean_chi2': chi2_mean_all, 'mean_chi2_h1': chi2_mean_h1,
        'mean_chi2_h2': chi2_mean_h2, 'chi2_convergence': chi2_convergence,
        'mean_sm2_core': sm2_mean, 'M_mean': M_mean, 'M_std': M_std,
        'H0': res['H0'], 'H_end': res['H_end'], 'H_drift': res['H_drift'],
        'hbar_candidate': hbar_candidate,
        'chi2_theory_fdt': chi2_theory, 'hbar_theory_fdt': hbar_theory,
        'chi2_vs_theory_ratio': chi2_mean_all / max(chi2_theory, 1e-20),
        'wall_sec': res['wall_sec'],
    }
    np.savez(OUT_DIR / f"traces_{label}.npz",
             chi2=res['chi2_trace'], sm2=res['sm2_trace'],
             M=res['M_trace'], H=res['H_trace'])
    print(f"  -> T_cycle={T_cycle:.2f}  omega={omega:.5f}")
    print(f"     <chi2>_meas = {chi2_mean_all:.4e}")
    print(f"     <chi2>_fdt  = {chi2_theory:.4e}  ratio = {row['chi2_vs_theory_ratio']:.3f}")
    print(f"     hbar_cand  = {hbar_candidate:.4e}")
    print(f"     hbar_theory= {hbar_theory:.4e}")
    return row


def main():
    print("=" * 72)
    print(f"QNG-GPU-044: Vacuum-sourced FDT probe (SIGMA_VAC={SIGMA_VAC})")
    print("=" * 72)
    print(f"L={L}, T_P1={T_P1}, T_P2={T_P2}, T_spinup={T_SPINUP}, "
          f"T_meas={T_MEASURE}, DT={DT}")
    print(f"k_gm={K_GM}, exact_a={EXACT_A_MODE!r}, R=4 (fixed)")
    print(f"gamma_scan = {GAMMA_SCAN}")
    print(f"Theory (FDT): <chi^2> = sigma_vac^2*dt/(2*gamma)")
    print(f"              hbar = sigma_vac^2*dt/omega (gamma-invariant)")

    rows = []
    for i, gamma in enumerate(GAMMA_SCAN):
        row = run_one(R=4, chi_decay=gamma, sigma_vac=SIGMA_VAC,
                      rng_seed=42 + i,
                      label=f"vac_R4_gamma{gamma:.3f}")
        rows.append(row)

    # CSV
    keys = list(rows[0].keys())
    with open(OUT_DIR / "vacuum_gamma_scan.csv", 'w') as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(str(r[k]) for k in keys) + "\n")
    print(f"\nwrote {OUT_DIR / 'vacuum_gamma_scan.csv'}")

    hbars = [r['hbar_candidate'] for r in rows]
    mu = float(np.mean(hbars))
    cv = float(np.std(hbars, ddof=1) / mu) if mu != 0 else float('nan')

    print("\n" + "=" * 72)
    print("SUMMARY (gamma-scan with stochastic vacuum)")
    print("=" * 72)
    for r in rows:
        print(f"  gamma={r['chi_decay']:.3f}:  "
              f"<chi2>={r['mean_chi2']:.3e}  (FDT pred {r['chi2_theory_fdt']:.3e})  "
              f"hbar_cand={r['hbar_candidate']:.4e}")
    print(f"\n  mean hbar = {mu:.4e}")
    print(f"  CV        = {cv*100:.2f}%")
    print(f"  theory    = {rows[0]['hbar_theory_fdt']:.4e} "
          f"(gamma-independent by construction)")

    if math.isfinite(cv):
        if cv < 0.02:
            verdict = "VACUUM_FDT_PASS"
            diag = (f"hbar_candidate gamma-invariant at CV={cv*100:.2f}%. "
                    f"Stochastic-vacuum hypothesis validates: SED-style "
                    f"mechanism produces emergent hbar-like behavior in "
                    f"QNG substrate. NOT a derivation of hbar value "
                    f"(sigma_vac is input) but confirms STRUCTURAL path.")
        elif cv < 0.10:
            verdict = "VACUUM_FDT_MARGINAL"
            diag = (f"CV={cv*100:.2f}% in (2%,10%). Stochastic vacuum "
                    f"partially closes FDT but residual gamma-dependence "
                    f"persists — investigate correlation time, coupling "
                    f"to symplectic sector.")
        else:
            verdict = "VACUUM_FDT_FAIL"
            diag = (f"CV={cv*100:.2f}% too high. Even with added vacuum "
                    f"noise, gamma-invariance does not close — vacuum "
                    f"coupling mechanism inadequate or sigma_vac too small.")
    else:
        verdict = "VACUUM_FDT_INCONCLUSIVE"
        diag = "Measurement produced NaN CV; diagnose."

    print(f"\n  Verdict: {verdict}")
    print(f"  Diagnosis: {diag}")

    json.dump({
        'rows': rows, 'cv': cv, 'mean_hbar': mu,
        'verdict': verdict, 'diagnosis': diag,
        'config': {
            'L': L, 'T_P1': T_P1, 'T_P2': T_P2,
            'T_SPINUP': T_SPINUP, 'T_MEASURE': T_MEASURE, 'DT': DT,
            'K_GM': K_GM, 'EXACT_A_MODE': EXACT_A_MODE,
            'SIGMA_VAC': SIGMA_VAC, 'GAMMA_SCAN': GAMMA_SCAN,
        },
    }, open(OUT_DIR / "summary.json", 'w'), indent=2, default=str)
    print(f"wrote {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
