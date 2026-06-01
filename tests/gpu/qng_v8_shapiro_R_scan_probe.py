"""Shapiro delay R-scan probe (Einstein test #1 — mass-scaling).

Does the Shapiro delay scale with ring size (and therefore with M_ring)?

If Δt(R) tracks the integrated σ_m deficit along the pulse path, the
coupling is a real mass-like coupling (GR-compatible).  If Δt(R) is flat
the coupling is a local refractive-index artifact independent of total
mass — a red flag for a 1911-style scalar-c theory.

Protocol (same on-rim geometry as Shapiro probe #3b, looped over R):
  - L = 28, R ∈ {3, 4, 5}
  - Pulse: source=(4, L/2+R, L/2) → detector=(L-4, L/2+R, L/2)
  - For each R:
      * form_ring_cached(R)  [R=4 hits existing cache]
      * evolve ring_only 250 lu (record phi_bg at detector)
      * clone + inject pulse, evolve 250 lu (record phi_rp)
      * Δt(R) = t_peak(phi_rp - phi_bg) - t_peak_vac
  - Vacuum is R-independent; run ONCE.

Analysis:
  Report Δt(R), M_ring(R), Δt/M_ring, and the slope dΔt/dR.
  Fit Δt = a + b·M_ring.  b > 0 with low RSS ⇒ mass-like coupling.

VERDICT:
  Δt scales with M_ring (slope b positive, monotonic)  → MASS-LIKE.
  Δt flat (|Δt(5)-Δt(3)| < noise)                       → LOCAL/REFRACTIVE.
  Δt anti-correlated with M_ring                        → INVESTIGATE.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

import qng_v8_canonical_gpu as v8
from qng_v8_canonical_gpu import (
    SIGMA_M_REF, BETA_PHI, MU_PHI, G_V_COUPLE, K_BACK, CHI_DECAY_V7,
    build_nb, make_state, yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
C_PHI_SQ = float(BETA_PHI) / (6.0 * float(MU_PHI))
C_PHI = float(np.sqrt(C_PHI_SQ))


def make_coords(L):
    N = L * L * L
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def inject_pulse(state, xc, yc, zc, x0, y0, z0, sigma, k, A):
    omega = C_PHI * k
    env = cp.exp(-(((xc - x0) ** 2 + (yc - y0) ** 2 + (zc - z0) ** 2)
                   / (2.0 * sigma ** 2)))
    cos_part = cp.cos(k * (xc - x0))
    sin_part = cp.sin(k * (xc - x0))
    state['phi'] = state['phi'] + A * env * cos_part
    state['pi_phi'] = state['pi_phi'] - MU_PHI * omega * A * env * sin_part


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def evolve_record(state, nb_idx, T, det_idx, sample_every,
                  verbose=False, label=''):
    n = int(T / DT)
    t_rec, phi_rec = [], []
    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_rec.append(s * DT)
            phi_rec.append(float(state['phi'][det_idx]))
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    t_rec.append(n * DT)
    phi_rec.append(float(state['phi'][det_idx]))
    if verbose:
        print(f"    evolved {label}: {n} steps ({time.time()-t0:.1f}s)")
    return state, np.array(t_rec), np.array(phi_rec)


def find_peak_arrival(t, phi_signal):
    abs_sig = np.abs(phi_signal)
    window = 3
    if len(abs_sig) < window:
        return float('nan'), float('nan')
    env = np.convolve(abs_sig, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(env))
    return float(t[i_peak]), float(env[i_peak])


def main():
    print("=" * 80)
    print("Einstein test #1: Shapiro R-scan (does Δt scale with ring mass?)")
    print("=" * 80)
    print(f"  c_phi = {C_PHI:.5f}   c_phi^2 = {C_PHI_SQ:.5f}")

    L = 28
    R_list = [3, 4, 5]
    T_track = 250.0
    DT_sample = 1.0
    sample_every = int(DT_sample / DT)

    xc, yc, zc = make_coords(L)
    N = L * L * L

    # Geometry (common across R; y_line shifts with R)
    x_source = 4.0
    x_detect = L - 4.0
    z_line = 0.5 * L
    sigma_pkt = 2.0
    k_pkt = np.pi / 4.0
    A_pkt = 0.05
    omega_vac = C_PHI * k_pkt
    t_vac_theory = (x_detect - x_source) / C_PHI

    print(f"  L={L}, R_list={R_list}")
    print(f"  Pulse source x={x_source}, detect x={x_detect}, "
          f"sigma={sigma_pkt}, k={k_pkt:.3f}, A={A_pkt}")
    print(f"  T_track = {T_track} lu (sample {DT_sample:.1f} lu)")
    print(f"  Vac ToF theory = {t_vac_theory:.1f} lu")
    print()

    # --- Vacuum reference (R-independent, use y_line for R=4) ---
    print("[0] Vacuum pulse (R-independent reference, y_line=L/2+4)")
    nb_idx = build_nb(L)
    y_vac = 0.5 * L + 4.0
    xd_int = int(round(x_detect))
    yd_int = int(round(y_vac))
    zd_int = int(round(z_line))
    det_vac = xd_int + yd_int * L + zd_int * L * L

    vac_state = make_state(L, phi_init=None)
    inject_pulse(vac_state, xc, yc, zc, x_source, y_vac, z_line,
                 sigma_pkt, k_pkt, A_pkt)
    _, t_vac, phi_vac = evolve_record(vac_state, nb_idx, T_track,
                                      det_vac, sample_every,
                                      verbose=True, label='vacuum')
    t_peak_vac, amp_vac = find_peak_arrival(t_vac, phi_vac)
    print(f"    vacuum peak: t={t_peak_vac:.2f} lu, amp={amp_vac:.5f}")
    print()

    # --- Per-R loop ---
    results = []
    for R in R_list:
        print(f"--- R = {R} ---")
        y_line = 0.5 * L + R
        yd = int(round(y_line))
        det = xd_int + yd * L + zd_int * L * L

        # Ring formation (cached)
        ring_state, nb_idx_r = form_ring_cached(L, R, T_P1=300.0,
                                                 T_P2=1000.0, verbose=True)
        M_ring = float(ring_mass_deficit(ring_state['sm']))
        print(f"    M_ring = {M_ring:.2f}")

        # Ring-only baseline
        s_bg = clone_state(ring_state)
        _, t_bg, phi_bg = evolve_record(s_bg, nb_idx_r, T_track, det,
                                        sample_every, verbose=True,
                                        label=f'ring_only R={R}')

        # Ring + pulse
        s_rp = clone_state(ring_state)
        inject_pulse(s_rp, xc, yc, zc, x_source, y_line, z_line,
                     sigma_pkt, k_pkt, A_pkt)
        _, t_rp, phi_rp = evolve_record(s_rp, nb_idx_r, T_track, det,
                                        sample_every, verbose=True,
                                        label=f'ring+pulse R={R}')

        phi_pulse = phi_rp - phi_bg
        t_peak_ring, amp_ring = find_peak_arrival(t_rp, phi_pulse)
        dt_R = t_peak_ring - t_peak_vac
        print(f"    R={R}: t_peak_ring={t_peak_ring:.2f}  "
              f"dt={dt_R:+.3f} lu  (M_ring={M_ring:.2f})")
        print()
        results.append({'R': R, 'M_ring': M_ring, 't_peak_ring': t_peak_ring,
                        'amp_ring': amp_ring, 'dt': dt_R,
                        't_vec': t_rp, 'phi_pulse': phi_pulse, 'phi_bg': phi_bg,
                        'y_line': y_line, 'det_idx': det})

    # --- Analysis ---
    print("=" * 80)
    print("SHAPIRO R-SCAN RESULTS")
    print("=" * 80)
    print(f"  Vacuum peak: t_vac = {t_peak_vac:.3f} lu")
    print()
    print(f"{'R':>3} {'M_ring':>10} {'t_peak(R)':>12} {'dt(R)':>10} "
          f"{'dt/M_ring':>12} {'dt/R':>10}")
    print("-" * 60)
    for r in results:
        dt_over_M = r['dt'] / max(r['M_ring'], 1e-6)
        dt_over_R = r['dt'] / r['R']
        print(f"{r['R']:>3} {r['M_ring']:>10.2f} {r['t_peak_ring']:>12.3f} "
              f"{r['dt']:>+10.3f} {dt_over_M:>+12.5f} {dt_over_R:>+10.3f}")

    # Linear fit: dt = a + b * M_ring
    M = np.array([r['M_ring'] for r in results])
    dt = np.array([r['dt'] for r in results])
    A = np.vstack([np.ones_like(M), M]).T
    coef, res, _, _ = np.linalg.lstsq(A, dt, rcond=None)
    a_fit, b_fit = coef
    dt_pred = a_fit + b_fit * M
    rss_lin = float(np.sum((dt - dt_pred) ** 2))
    tss = float(np.sum((dt - dt.mean()) ** 2))
    R2_lin = 1.0 - rss_lin / max(tss, 1e-12)
    mean_dt = float(dt.mean())
    std_dt = float(dt.std())

    print()
    print(f"  Linear fit: dt = {a_fit:+.3f} + {b_fit:+.5f} * M_ring")
    print(f"    RSS = {rss_lin:.4f},  R^2 = {R2_lin:.4f}")
    print(f"  Mean dt = {mean_dt:+.3f} lu,  std(dt) = {std_dt:.3f} lu")
    print(f"  dt(R=5) - dt(R=3) = {dt[-1] - dt[0]:+.3f} lu")
    print()
    print(f"  Canonical M_ring (DER-QNG-038): R=3:474, R=4:729, R=5:955")
    print()

    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    spread = dt.max() - dt.min()
    monotone = all(dt[i] < dt[i+1] for i in range(len(dt)-1)) or \
               all(dt[i] > dt[i+1] for i in range(len(dt)-1))
    if spread < 1.0:
        print(f"FLAT: dt spread {spread:.2f} lu < 1.0 lu noise floor.")
        print("  -> Shapiro coupling appears to be LOCAL REFRACTIVE")
        print("     (independent of total ring mass).")
        print("  -> RED FLAG for 1911-style scalar-c theory.")
        print("  -> Matter coupling may be through local deficit only,")
        print("     not integrated mass. Bending test critical next.")
    elif b_fit > 0 and monotone and R2_lin > 0.9:
        print(f"MASS-LIKE: dt scales with M_ring (b={b_fit:+.5f}, R^2={R2_lin:.3f}).")
        print("  -> Shapiro coupling tracks integrated ring mass.")
        print("  -> Consistent with GR-style mass coupling.")
    elif b_fit > 0 and monotone:
        print(f"MONOTONIC but noisy (b={b_fit:+.5f}, R^2={R2_lin:.3f}).")
        print("  -> Suggests mass-like coupling; longer T_track may tighten fit.")
    else:
        print(f"UNCLEAR: spread {spread:.2f} lu, b={b_fit:+.5f}, R^2={R2_lin:.3f}.")
        print("  -> Non-monotonic or anti-correlated; investigate.")

    # --- Save raw signals ---
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / "shapiro_R_scan_signals.npz",
             R_list=np.array(R_list),
             M_ring=M,
             dt=dt,
             t_peak_vac=t_peak_vac,
             t_peak_ring=np.array([r['t_peak_ring'] for r in results]),
             amp_ring=np.array([r['amp_ring'] for r in results]),
             a_fit=a_fit, b_fit=b_fit, R2_lin=R2_lin,
             c_phi=C_PHI,
             t_vec=results[0]['t_vec'],
             phi_vac=phi_vac,
             phi_pulse_R3=results[0]['phi_pulse'],
             phi_pulse_R4=results[1]['phi_pulse'],
             phi_pulse_R5=results[2]['phi_pulse'])
    print(f"\n  Signals saved to {outdir / 'shapiro_R_scan_signals.npz'}")


if __name__ == "__main__":
    main()
