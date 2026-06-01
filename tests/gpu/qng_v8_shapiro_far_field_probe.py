"""Far-field Shapiro probe — impact-parameter scan (Einstein test #2).

Goal: distinguish GR-type Shapiro delay (logarithmic in impact parameter
b) from 1911-type (linear or 1/b falloff).

GR Shapiro (Sun-radar, Shapiro 1964):
    dt ~ (4 G M / c^3) * log(b_0 / b)
-> doubles with each halving of b.

Einstein 1911 scalar-c theory:
    dt ~ G M / (c^2 b) or linear in something else — NOT logarithmic.

Test: form R=4 ring at L=28 (cache hit after Einstein test 3b rerun).
     Launch pulse at several impact parameters b measured from ring
     center axis. Detector tracks the same b-line. Measure dt(b).

Fit form hypotheses:
  H_GR:   dt = A * log(b_ref / b) + C
  H_1911: dt = A / b + C
  H_lin:  dt = A * (b_ref - b) + C

Report: which fits with smallest residual, and extrapolated dt at b=0,
b=4R to gauge falloff character.

Protocol per impact parameter b:
  (shared) Vacuum+pulse run once (b-independent free propagation)
  (shared) Ring-only baseline run (b-dependent: detector location changes)
  (per-b ) Ring+pulse run
Each ring run uses the same cached state (from Einstein test 3b).
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
    make_state, yoshida4_step, ring_mass_deficit,
)
from qng_v8_ring_cache import form_ring_cached

DT = 0.025
C_PHI_SQ = float(BETA_PHI) / (6.0 * float(MU_PHI))
C_PHI = float(np.sqrt(C_PHI_SQ))

AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"


def make_coords(L):
    N = L * L * L
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    y = ((idx // L) % L).astype(cp.float64)
    z = (idx // (L * L)).astype(cp.float64)
    return x, y, z


def inject_pulse(state, x_coords, y_coords, z_coords, x0, y0, z0,
                 sigma, k, A):
    omega = C_PHI * k
    env = cp.exp(-(((x_coords - x0) ** 2 +
                    (y_coords - y0) ** 2 +
                    (z_coords - z0) ** 2) / (2.0 * sigma ** 2)))
    cos_part = cp.cos(k * (x_coords - x0))
    sin_part = cp.sin(k * (x_coords - x0))
    state['phi'] = state['phi'] + A * env * cos_part
    state['pi_phi'] = state['pi_phi'] - MU_PHI * omega * A * env * sin_part


def clone_state(state):
    return {k: (v.copy() if v is not None else None) for k, v in state.items()}


def evolve_record(state, nb_idx, T, detector_idx, sample_every,
                  verbose=False, label=''):
    n = int(T / DT)
    t_rec = []
    phi_rec = []
    t0 = time.time()
    for s in range(n):
        if s % sample_every == 0:
            t_rec.append(s * DT)
            phi_rec.append(float(state['phi'][detector_idx]))
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7)
    t_rec.append(n * DT)
    phi_rec.append(float(state['phi'][detector_idx]))
    wall = time.time() - t0
    if verbose:
        print(f"    evolved {label}: {n} steps done ({wall:.1f}s)")
    return state, np.array(t_rec), np.array(phi_rec)


def find_peak_arrival(t, phi_signal, window=5):
    abs_sig = np.abs(phi_signal)
    if len(abs_sig) < window:
        return float('nan'), float('nan')
    env = np.convolve(abs_sig, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(env))
    return float(t[i_peak]), float(env[i_peak])


def main():
    print("=" * 80)
    print("Einstein test #2: Far-field Shapiro (impact-parameter scan)")
    print("  Distinguishes GR log(b) from 1911 linear/1-over-b")
    print("=" * 80)
    print(f"  c_phi = {C_PHI:.5f}   c_phi^2 = {C_PHI_SQ:.5f}")
    print()

    L = 28
    R = 4
    T_track = 250.0
    DT_sample = 1.0
    sample_every = int(DT_sample / DT)
    x_coords, y_coords, z_coords = make_coords(L)

    # Geometry: ring at (L/2, L/2, L/2) in XY plane, axis along z.
    # Pulse line: y = L/2 + b (varies with b), z = L/2 (constant).
    # Source x=4, detector x=L-4=24.
    y_center  = 0.5 * L
    z_line    = 0.5 * L
    x_source  = 4.0
    x_detect  = L - 4.0
    sigma_pkt = 2.0
    k_pkt     = np.pi / 4.0
    A_pkt     = 0.05

    # Impact parameters (distance of pulse line from ring axis at z=L/2)
    # b = R  -> tangent to tube (existing 3b result = +26 lu)
    # b = 2R -> outside tube, still within ring field
    # b = 3R -> far field
    impact_params = [R, 2 * R, 3 * R]  # b = 4, 8, 12

    print(f"  L={L}, R={R}, y_center={y_center}")
    print(f"  Impact params (b from ring axis): {impact_params}")
    print(f"  Source x={x_source}, detector x={x_detect}, distance={x_detect-x_source}")
    print(f"  T_track = {T_track} lu, sample every {DT_sample} lu")
    print(f"  Vac ToF theory = d/c_phi = {(x_detect-x_source)/C_PHI:.1f} lu")
    print()

    # --- Form ring (cache hit after Test 3b rerun) ---
    print("[0] Load cached ring (L=28, R=4, P1=300, P2=1000)")
    ring_state, nb_idx = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    M_ring0 = {M_ring0:.2f}")
    print()

    # Vacuum run uses y=y_center (arbitrary — no ring, b doesn't matter)
    # But we still want a reference peak time.
    print("[1] Vacuum + pulse (b-independent reference)")
    y_vac = y_center + R   # match first b for direct reuse convenience
    det_idx_vac = int(round(x_detect)) + int(round(y_vac)) * L + int(round(z_line)) * L * L
    vac_state = make_state(L, phi_init=None)
    inject_pulse(vac_state, x_coords, y_coords, z_coords,
                 x_source, y_vac, z_line, sigma_pkt, k_pkt, A_pkt)
    _, t_vac, phi_vac = evolve_record(vac_state, nb_idx, T_track,
                                      det_idx_vac, sample_every,
                                      verbose=True, label='vacuum')
    t_peak_vac, amp_vac = find_peak_arrival(t_vac, phi_vac)
    print(f"    t_peak_vac = {t_peak_vac:.2f} lu   amp = {amp_vac:.5f}")
    print()

    # --- Per-b runs ---
    results = []
    for i_b, b in enumerate(impact_params):
        print(f"[{i_b+2}] Impact parameter b = {b} (y_line = {y_center + b})")
        y_line = y_center + b
        det_idx = int(round(x_detect)) + int(round(y_line)) * L + int(round(z_line)) * L * L

        # Ring-only baseline at this detector
        ring_copy_bg = clone_state(ring_state)
        _, t_bg, phi_bg = evolve_record(ring_copy_bg, nb_idx, T_track,
                                        det_idx, sample_every,
                                        verbose=True, label=f'ring_only b={b}')

        # Ring + pulse
        ring_copy_p = clone_state(ring_state)
        inject_pulse(ring_copy_p, x_coords, y_coords, z_coords,
                     x_source, y_line, z_line, sigma_pkt, k_pkt, A_pkt)
        _, t_rp, phi_rp = evolve_record(ring_copy_p, nb_idx, T_track,
                                        det_idx, sample_every,
                                        verbose=True, label=f'ring+pulse b={b}')

        phi_pulse_ring = phi_rp - phi_bg
        t_peak_ring, amp_ring = find_peak_arrival(t_rp, phi_pulse_ring)
        dt = t_peak_ring - t_peak_vac
        frac = dt / max(t_peak_vac, 1e-6) * 100.0
        print(f"    t_peak_ring = {t_peak_ring:.2f} lu   amp = {amp_ring:.5f}")
        print(f"    Shapiro dt = {dt:+.2f} lu   ({frac:+.1f}%)")
        print()
        results.append({
            'b': float(b),
            't_peak_vac': float(t_peak_vac),
            't_peak_ring': float(t_peak_ring),
            'dt': float(dt),
            'frac': float(frac),
            'amp_ring': float(amp_ring),
            't_arr': t_rp,
            'phi_pulse_ring': phi_pulse_ring,
            'phi_bg': phi_bg,
        })

    # --- Analysis: fit H_GR log vs H_1911 1/b vs H_lin ---
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"  {'b':>6}  {'dt [lu]':>10}  {'frac %':>8}")
    for r in results:
        print(f"  {r['b']:>6.1f}  {r['dt']:>+10.2f}  {r['frac']:>+8.1f}")
    print()

    bs  = np.array([r['b'] for r in results], dtype=float)
    dts = np.array([r['dt'] for r in results], dtype=float)

    # Fits via least squares (2 params per hypothesis)
    # H_GR:   dt = A*log(1/b) + C = -A*log(b) + C
    # H_1911: dt = A/b + C
    # H_lin:  dt = A*(b_ref - b) + C  — equivalently dt = -A*b + (A*b_ref + C)
    # Residuals compared across models.
    def fit_and_residual(xs, ys):
        A_mat = np.vstack([xs, np.ones_like(xs)]).T
        coeffs, _, _, _ = np.linalg.lstsq(A_mat, ys, rcond=None)
        pred = A_mat @ coeffs
        rss = float(np.sum((ys - pred) ** 2))
        return coeffs, pred, rss

    print("Fit comparison (lower RSS = better):")
    for name, xs in [
        ('H_GR  (dt vs -log(b))',  -np.log(bs)),
        ('H_1911 (dt vs 1/b)',      1.0 / bs),
        ('H_lin (dt vs b)',         bs),
    ]:
        coeffs, pred, rss = fit_and_residual(xs, dts)
        print(f"  {name}")
        print(f"    slope = {coeffs[0]:+.3f}   intercept = {coeffs[1]:+.3f}   RSS = {rss:.3f}")
        print(f"    predicted dt: {pred.tolist()}")
    print()

    # Save signals
    save_path = AUDIT_DIR / "shapiro_far_field_signals.npz"
    save_dict = {
        'b_values': bs,
        'dt_values': dts,
        'frac_values': np.array([r['frac'] for r in results]),
        't_peak_vac': t_peak_vac,
        'M_ring0': M_ring0,
        'L': L, 'R': R,
        'c_phi': C_PHI,
        'g': float(G_V_COUPLE),
        'mu_phi': float(MU_PHI),
    }
    for i, r in enumerate(results):
        save_dict[f'phi_pulse_ring_b{int(r["b"])}'] = r['phi_pulse_ring']
        save_dict[f'phi_bg_b{int(r["b"])}']         = r['phi_bg']
    save_dict['t_axis'] = results[0]['t_arr']
    np.savez(save_path, **save_dict)
    print(f"  Signals saved -> {save_path}")
    print()

    # Verdict
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    dt_ratio_R_to_2R = dts[0] / max(dts[1], 1e-6)
    dt_ratio_2R_to_3R = dts[1] / max(dts[2], 1e-6)
    print(f"  dt(b=R)/dt(b=2R) = {dt_ratio_R_to_2R:.2f}")
    print(f"  dt(b=2R)/dt(b=3R) = {dt_ratio_2R_to_3R:.2f}")
    print()
    print("  GR log(b) prediction: ratio ~ log(2R/b)/log(3R/b) (slow decay)")
    print("  1911 1/b prediction : ratio = 2.0 (double per halving)")
    print("  Sharp cutoff        : ratio >> 5 (no far-field effect)")
    print()
    if dts[2] > 0.5 * dts[0]:
        print("  SLOW FALLOFF: consistent with GR-type log(b) dependence.")
    elif dts[2] > 0.1 * dts[0]:
        print("  MODERATE FALLOFF: between 1/b (1911) and log (GR).")
    else:
        print("  SHARP CUTOFF: ring influence doesn't extend to b=3R.")
        print("  -> consistent with short-range interaction, NOT GR.")


if __name__ == "__main__":
    main()
