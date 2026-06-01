"""QNG-GPU-043 — Two-channel FDT probe for emergent hbar candidate.

Pre-registration: 07_validation/prereg/QNG-GPU-043.md
Derivation:       04_qng_pure/qng-two-channel-structure-v1.md (DER-QNG-054)

Tests whether v8's intrinsic two-channel structure (symplectic sector S =
(sigma_m, pi_m, phi, pi_phi) coupled to dissipative OU sector D = chi via
Channels G and D) produces an Einstein-Nyquist FDT relation with a
CHI_DECAY-independent and R-universal hbar candidate:

    hbar_candidate = 2 * CHI_DECAY * <chi^2> / omega_orbit

Protocol v2 (post-debug 2026-04-24):
  - Must use exact_a='r1' (DER-QNG-051 R1 pure-XY) to avoid vacuum
    instability that dissolves the ring.
  - Must pass k_gm > 0 to yoshida4_step so Channel A (sm -> sg) activates
    and sources chi via sg-deviation terms in drive_chi_v7style.
  - Cached rings under default exact_a=False have sg=uniform and chi=0
    exactly; their chi drive has zero source. We do NOT reuse those
    caches here -- ring is formed fresh using the R1 protocol from
    GPU-031f/qng_v8_r1_long_time.

Parts:
  A: R-scan {3, 4, 5, 6} at CHI_DECAY=0.020, k_gm=0.01
  B: gamma-scan {0.010, 0.020, 0.040} at R=4
  C: Channel-D-off control at R=4

Outputs: 07_validation/audits/qng-gpu043-two-channel-fdt-v1/
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
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu043-two-channel-fdt-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Run configuration
# ---------------------------------------------------------------------------
L              = 20
T_P1           = 300.0   # Phase 1 (phi vortex formation)
T_P2           = 1000.0  # Phase 2 (sigma_m ring formation)
T_SPINUP       = 200.0   # let attractor settle + let chi charge up
T_MEASURE      = 1000.0  # long enough for several orbital periods (T~185 lu)
DT             = 0.025
SAMPLE_STRIDE  = 4       # record every 4 steps = 0.1 lu
PROGRESS_EVERY = 2000
EXACT_A_MODE   = 'r1'    # DER-QNG-051 Option R1 (pure-XY E_phi)
K_GM           = 0.01    # v7 default; small so orbital attractor survives

R_SCAN     = [3, 4, 5, 6]
GAMMA_SCAN = [0.010, 0.020, 0.040]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ring_core_mask(L, R, z_ring=None):
    """Boolean mask (flat shape (L**3,)) selecting ring core region."""
    if z_ring is None:
        z_ring = L // 2
    zz = cp.arange(L).reshape(1, 1, L)
    zz = cp.broadcast_to(zz, (L, L, L))
    return (cp.abs(zz - z_ring) <= (R + 2)).reshape(-1)


def form_ring_r1(L, R, T_P1, T_P2, DT, k_gm, chi_decay, verbose=True):
    """Fresh ring formation using DER-QNG-051 R1 protocol (pure-XY E_phi).

    Phase 1: v_couple_on=False  (phi vortex alone)
    Phase 2: v_couple_on=True   (sigma_m ring develops)
    k_gm passed through both phases so sg tracks sm deficit from start.
    """
    nb_idx = build_nb(L)
    phi_ic = init_phi_single_ring(L, R)
    state = make_state(L, phi_init=phi_ic)
    n1 = int(T_P1 / DT)
    n2 = int(T_P2 / DT)
    t0 = time.time()
    for step in range(n1):
        state = yoshida4_step(state, DT, nb_idx, k_gm=k_gm,
                              chi_decay=chi_decay,
                              v_couple_on=False, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if verbose and (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            print(f"    [P1] {step+1}/{n1}  {(step+1)/elapsed:.0f} steps/s",
                  flush=True)
    for step in range(n2):
        state = yoshida4_step(state, DT, nb_idx, k_gm=k_gm,
                              chi_decay=chi_decay,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if verbose and (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (n1 + step + 1) / elapsed
            eta = (n2 - step - 1) / rate
            print(f"    [P2] {step+1}/{n2}  {rate:.0f} steps/s  ETA {eta:.0f}s",
                  flush=True)
    wall = time.time() - t0
    M = float(ring_mass_deficit(state['sm']))
    chi2 = float(cp.sum(state['chi'] ** 2).get()) / (L ** 3)
    sg_std = float(cp.std(state['sg']).get())
    if verbose:
        print(f"  Ring formed ({n1+n2} steps, {wall:.1f}s) "
              f"M_ring={M:.2f} <chi^2>={chi2:.3e} std(sg)={sg_std:.4e}",
              flush=True)
    return state, nb_idx


def run_spinup_and_measure(state, nb_idx, k_gm, chi_decay, T_spinup, T_meas,
                            dt, core_mask, with_channel_d=True, label=""):
    """Spin-up then measure chi^2, sigma_m^2, M_ring traces."""
    n_spin = int(T_spinup / dt)
    n_meas = int(T_meas / dt)
    n_rec = n_meas // SAMPLE_STRIDE
    chi2_trace = np.zeros(n_rec, dtype=np.float64)
    sm2_trace  = np.zeros(n_rec, dtype=np.float64)
    M_trace    = np.zeros(n_rec, dtype=np.float64)
    H_trace    = np.zeros(12, dtype=np.float64)
    H_idx_step = max(1, n_meas // 10)

    N_total = float(L ** 3)
    N_core  = float(cp.sum(core_mask).get())
    cd = chi_decay if with_channel_d else 0.0

    t0 = time.time()
    # ---- spinup ----
    for step in range(n_spin):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=cd,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if not with_channel_d:
            state['chi'].fill(0.0)
        if (step + 1) % PROGRESS_EVERY == 0:
            elapsed = time.time() - t0
            rate = (step + 1) / elapsed
            eta = (n_spin + n_meas - step - 1) / rate
            chi2_now = float(cp.sum(state['chi'] ** 2).get()) / N_total
            M_now = float(ring_mass_deficit(state['sm']))
            print(f"    [{label}|spin] {step+1}/{n_spin}  {rate:.0f} steps/s  "
                  f"ETA {eta:.0f}s  <chi2>={chi2_now:.3e} M={M_now:.1f}",
                  flush=True)

    # ---- H0 monitor start ----
    H0 = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                              exact_a=EXACT_A_MODE))
    H_trace[0] = H0

    # ---- measurement ----
    rec_idx = 0
    for step in range(n_meas):
        state = yoshida4_step(state, dt, nb_idx, k_gm=k_gm, chi_decay=cd,
                              v_couple_on=True, channel_f=True,
                              exact_a=EXACT_A_MODE)
        if not with_channel_d:
            state['chi'].fill(0.0)
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
                  f"M={M_trace[max(0,rec_idx-1)]:.1f}",
                  flush=True)

    wall = time.time() - t0
    H_end = float(hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=k_gm,
                                 exact_a=EXACT_A_MODE))
    H_drift = abs(H_end - H0) / max(abs(H0), 1e-10)
    print(f"  [{label}] {n_spin+n_meas} steps, {wall:.1f}s  H_drift={H_drift:.2%}")
    return {
        'chi2_trace': chi2_trace[:rec_idx],
        'sm2_trace':  sm2_trace[:rec_idx],
        'M_trace':    M_trace[:rec_idx],
        'H_trace':    H_trace,
        'wall_sec':   wall,
        'H0':         H0,
        'H_end':      H_end,
        'H_drift':    H_drift,
    }


def omega_orbit_from_M(M_trace, dt_sample):
    """Estimate dominant orbital omega from M_ring autocorrelation peak.

    Fallback to FFT peak if autocorrelation peak ambiguous.
    """
    x = M_trace - M_trace.mean()
    N = len(x)
    if N < 100 or np.std(x) < 1e-8:
        return float('nan'), float('nan')
    ac = np.correlate(x, x, mode='full')[N - 1:]
    ac /= ac[0]
    # first zero crossing
    zc = None
    for i in range(1, N - 1):
        if ac[i - 1] > 0 >= ac[i]:
            zc = i
            break
    if zc is None:
        zc = 1
    peak_idx = None
    peak_val = -np.inf
    for i in range(zc + 1, min(N - 1, zc + N // 2)):
        if ac[i - 1] < ac[i] > ac[i + 1] and ac[i] > 0.05:
            if ac[i] > peak_val:
                peak_val = ac[i]
                peak_idx = i
                break
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


# ---------------------------------------------------------------------------
# One full run (fresh formation + spinup + measurement)
# ---------------------------------------------------------------------------
def run_one(R, chi_decay, with_channel_d=True, label=""):
    print(f"\n=== {label}  R={R}  gamma={chi_decay}  "
          f"channel_D={'ON' if with_channel_d else 'OFF'} ===")
    state, nb_idx = form_ring_r1(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT,
                                   k_gm=K_GM, chi_decay=chi_decay, verbose=True)
    core_mask = ring_core_mask(L, R)

    res = run_spinup_and_measure(state, nb_idx, K_GM, chi_decay,
                                  T_SPINUP, T_MEASURE, DT, core_mask,
                                  with_channel_d=with_channel_d,
                                  label=label)

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

    if with_channel_d and math.isfinite(omega) and omega > 0:
        hbar_candidate = 2.0 * chi_decay * chi2_mean_all / omega
    else:
        hbar_candidate = 0.0

    row = {
        'label':          label,
        'R':              R,
        'chi_decay':      chi_decay,
        'with_channel_d': with_channel_d,
        'L':              L,
        'k_gm':           K_GM,
        'exact_a':        EXACT_A_MODE,
        'T_cycle':        T_cycle,
        'omega_orbit':    omega,
        'mean_chi2':      chi2_mean_all,
        'mean_chi2_h1':   chi2_mean_h1,
        'mean_chi2_h2':   chi2_mean_h2,
        'chi2_convergence': chi2_convergence,
        'mean_sm2_core':  sm2_mean,
        'M_mean':         M_mean,
        'M_std':          M_std,
        'H0':             res['H0'],
        'H_end':          res['H_end'],
        'H_drift':        res['H_drift'],
        'hbar_candidate': hbar_candidate,
        'wall_sec':       res['wall_sec'],
    }

    np.savez(OUT_DIR / f"traces_{label}.npz",
             chi2=res['chi2_trace'], sm2=res['sm2_trace'],
             M=res['M_trace'], H=res['H_trace'])
    print(f"  -> T_cycle={T_cycle:.2f}  omega={omega:.5f}  "
          f"<chi2>={chi2_mean_all:.4e}  M_mean={M_mean:+.1f}  "
          f"hbar_cand={hbar_candidate:.4e}")
    return row


# ---------------------------------------------------------------------------
# Minimal proof-of-concept: single run (called first to validate protocol)
# ---------------------------------------------------------------------------
def poc_single_run():
    print("=" * 72)
    print("GPU-043 proof-of-concept: single R=4 gamma=0.020 run")
    print("Verifies: chi^2 > 0, M_ring ~300, orbital period ~185 lu")
    print("=" * 72)
    print(f"L={L}, T_P1={T_P1}, T_P2={T_P2}, T_spinup={T_SPINUP}, "
          f"T_meas={T_MEASURE}, DT={DT}")
    print(f"k_gm={K_GM}, chi_decay={CHI_DECAY_V7}, exact_a={EXACT_A_MODE!r}")
    row = run_one(R=4, chi_decay=CHI_DECAY_V7, with_channel_d=True,
                  label="POC_R4_gamma0.020")
    with open(OUT_DIR / "poc_result.json", "w") as f:
        json.dump(row, f, indent=2, default=str)

    # Verdict summary
    print("\n" + "=" * 72)
    print("POC VERDICT")
    print("=" * 72)
    ok_chi = row['mean_chi2'] > 1e-10
    ok_M   = 100.0 < row['M_mean'] < 1000.0 and row['M_std'] / max(abs(row['M_mean']),1) < 1.0
    ok_T   = math.isfinite(row['T_cycle']) and 50.0 < row['T_cycle'] < 500.0
    print(f"  chi^2 > 1e-10:          {ok_chi}  (<chi2>={row['mean_chi2']:.3e})")
    print(f"  M_mean in (100, 1000):  {ok_M}   (M={row['M_mean']:.1f} std={row['M_std']:.1f})")
    print(f"  T_cycle in (50, 500):   {ok_T}   (T={row['T_cycle']:.2f} lu)")
    if ok_chi and ok_M and ok_T:
        print("  >>> POC PASS: two-channel FDT coupling confirmed active <<<")
        print(f"      hbar_candidate = {row['hbar_candidate']:.4e}")
    else:
        print("  >>> POC FAIL: diagnose before R-scan <<<")
    return row


# ---------------------------------------------------------------------------
# Full scan driver (only runs if POC passes)
# ---------------------------------------------------------------------------
def main_full_scan():
    print("\n" + "=" * 72)
    print("QNG-GPU-043: FULL SCAN (DER-QNG-054)")
    print("=" * 72)

    rows_rscan = []
    rows_gscan = []
    rows_ctrl  = []

    # Part A: R-scan at CHI_DECAY=0.020
    for R in R_SCAN:
        row = run_one(R=R, chi_decay=CHI_DECAY_V7, with_channel_d=True,
                      label=f"A_R{R}_gamma{CHI_DECAY_V7:.3f}")
        rows_rscan.append(row)

    # Part B: gamma-scan at R=4
    for gamma in GAMMA_SCAN:
        if abs(gamma - CHI_DECAY_V7) < 1e-9:
            r4 = next((r for r in rows_rscan if r['R'] == 4), None)
            if r4 is not None:
                copy = dict(r4); copy['label'] = f"B_R4_gamma{gamma:.3f}"
                rows_gscan.append(copy)
                continue
        row = run_one(R=4, chi_decay=gamma, with_channel_d=True,
                      label=f"B_R4_gamma{gamma:.3f}")
        rows_gscan.append(row)

    # Part C: control (Channel D off)
    row = run_one(R=4, chi_decay=CHI_DECAY_V7, with_channel_d=False,
                  label=f"C_R4_gamma{CHI_DECAY_V7:.3f}_Doff")
    rows_ctrl.append(row)

    def write_csv(path, rows):
        if not rows: return
        keys = list(rows[0].keys())
        with open(path, 'w') as f:
            f.write(",".join(keys) + "\n")
            for r in rows:
                f.write(",".join(str(r[k]) for k in keys) + "\n")
        print(f"wrote {path}")

    write_csv(OUT_DIR / "hbar_candidate_R_scan.csv", rows_rscan)
    write_csv(OUT_DIR / "hbar_candidate_gamma_scan.csv", rows_gscan)
    write_csv(OUT_DIR / "hbar_candidate_control.csv", rows_ctrl)

    def cv(xs):
        if len(xs) < 2: return float('nan')
        mu = np.mean(xs)
        return float(np.std(xs, ddof=1) / mu) if mu != 0 else float('nan')

    hbars_R = [r['hbar_candidate'] for r in rows_rscan
               if math.isfinite(r['hbar_candidate']) and r['hbar_candidate'] > 0]
    hbars_g = [r['hbar_candidate'] for r in rows_gscan
               if math.isfinite(r['hbar_candidate']) and r['hbar_candidate'] > 0]
    cv_R = cv(hbars_R); cv_g = cv(hbars_g)

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"R-scan hbar_candidate: {hbars_R}")
    print(f"R-scan CV: {cv_R*100:.2f}%" if math.isfinite(cv_R) else "R-scan CV: NaN")
    print(f"gamma-scan hbar_candidate: {hbars_g}")
    print(f"gamma-scan CV: {cv_g*100:.2f}%" if math.isfinite(cv_g) else "gamma-scan CV: NaN")
    if rows_ctrl:
        print(f"Control (D off) hbar_candidate: {rows_ctrl[0]['hbar_candidate']}")

    def gate_verdict(cv_R, cv_g):
        if not math.isfinite(cv_R) or not math.isfinite(cv_g):
            return "ATTRACTOR_INCONCLUSIVE"
        if cv_R < 0.02 and cv_g < 0.02:
            return "TWO_CHANNEL_PASS"
        if cv_R < 0.10 and cv_g < 0.05:
            return "TWO_CHANNEL_R_DEPENDENT"
        return "TWO_CHANNEL_FAIL"

    verdict = gate_verdict(cv_R, cv_g)
    print(f"\nPreliminary verdict: {verdict}")

    json.dump({
        'rows_rscan': rows_rscan,
        'rows_gscan': rows_gscan,
        'rows_ctrl':  rows_ctrl,
        'cv_R': cv_R, 'cv_gamma': cv_g,
        'verdict': verdict,
        'config': {
            'L': L, 'T_P1': T_P1, 'T_P2': T_P2,
            'T_SPINUP': T_SPINUP, 'T_MEASURE': T_MEASURE, 'DT': DT,
            'K_GM': K_GM, 'EXACT_A_MODE': EXACT_A_MODE,
            'R_SCAN': R_SCAN, 'GAMMA_SCAN': GAMMA_SCAN,
        },
    }, open(OUT_DIR / "summary.json", 'w'), indent=2, default=str)
    print(f"wrote {OUT_DIR / 'summary.json'}")


def gamma_scan_only():
    """Run gamma={0.010, 0.040} at R=4 (POC already covered 0.020)."""
    print("=" * 72)
    print("GPU-043 Step 1: gamma-scan at R=4 (gamma in {0.010, 0.040})")
    print("POC already gave gamma=0.020 -> hbar_cand=1.8889e-04")
    print("=" * 72)
    rows = []
    for gamma in [0.010, 0.040]:
        row = run_one(R=4, chi_decay=gamma, with_channel_d=True,
                      label=f"B_R4_gamma{gamma:.3f}")
        rows.append(row)
    with open(OUT_DIR / "gamma_scan_rows.json", "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print("\n" + "=" * 72)
    print("gamma-scan results (including POC):")
    print("=" * 72)
    print(f"  gamma=0.010:  hbar_cand={rows[0]['hbar_candidate']:.4e}  "
          f"<chi2>={rows[0]['mean_chi2']:.3e}  T_cycle={rows[0]['T_cycle']:.1f}")
    print(f"  gamma=0.020:  hbar_cand=1.8889e-04               "
          f"<chi2>=1.633e-04  T_cycle=181.7    (POC)")
    print(f"  gamma=0.040:  hbar_cand={rows[1]['hbar_candidate']:.4e}  "
          f"<chi2>={rows[1]['mean_chi2']:.3e}  T_cycle={rows[1]['T_cycle']:.1f}")
    hbars = [rows[0]['hbar_candidate'], 1.8889e-04, rows[1]['hbar_candidate']]
    if all(math.isfinite(h) and h > 0 for h in hbars):
        mu = float(np.mean(hbars))
        cv = float(np.std(hbars, ddof=1) / mu)
        print(f"\n  mean   = {mu:.4e}")
        print(f"  CV     = {cv*100:.2f}%")
        if cv < 0.02:
            print("  >>> GAMMA-INVARIANCE PASS (<2%) -> proceed to R-scan <<<")
        elif cv < 0.05:
            print("  >>> GAMMA-INVARIANCE MARGINAL (2-5%) -> R-scan still worth it <<<")
        else:
            print("  >>> GAMMA-INVARIANCE FAIL (>5%) -> 17th failed hbar program <<<")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--poc', action='store_true',
                   help='Run only proof-of-concept single run (~15 min)')
    p.add_argument('--gamma', action='store_true',
                   help='Run gamma-scan at R=4 (gamma in {0.010, 0.040})')
    p.add_argument('--full', action='store_true',
                   help='Run full R-scan + gamma-scan + control')
    args = p.parse_args()
    if not (args.poc or args.gamma or args.full):
        args.poc = True  # default = POC
    if args.poc:
        row = poc_single_run()
    if args.gamma:
        gamma_scan_only()
    if args.full:
        main_full_scan()
