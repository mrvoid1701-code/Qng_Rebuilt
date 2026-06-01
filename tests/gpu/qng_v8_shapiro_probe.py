"""Shapiro delay probe for v8 rings (Einstein test #3b, 1919 analog).

Einstein 1919: light bends near the Sun; equivalently, a photon passing
close to a mass takes longer than the straight-line vacuum transit time
(Shapiro delay).

v8 analog:
  - Light = KG phi wave (c_phi = sqrt(BETA_PHI/(6*mu_phi)) ≈ 0.108 in QNG units).
  - Mass source = v8 vortex ring at R=4 (confirmed stable, CPU-074).
  - "Refractive index" arises because in a region with deficit d(x),
    the phi dispersion is omega^2 = c_phi^2 * k^2 + (g/2)*d^2/mu_phi.
    Near the ring core, d > 0 so group velocity v_g = c_phi^2 k / omega
    is REDUCED below c_phi — waves slow down near mass.

Protocol:
  1. Vacuum-with-pulse run:
       Start from vacuum, inject a rightward Gaussian pulse at
       (x0=4, L/2+R, L/2). Evolve, record phi(x_detect, L/2+R, L/2) vs t.
  2. Ring-only run:
       Form R=4 ring (P1=300, P2=1000). Evolve extra 200 lu, record
       phi_bg(x_detect, L/2+R, L/2) vs t.
  3. Ring-plus-pulse run:
       Clone ring state, add same pulse, evolve, record phi_rp.
  4. Extract pulse-in-ring signal: phi_pulse_in_ring = phi_rp - phi_bg.
  5. Find peak arrival time at detector for vacuum vs ring cases.
  6. Shapiro delay Δt = t_ring - t_vac.

VERDICT:
  Δt > 0 (consistent with theory)  -> ring gravitates; Einstein 1919 PASS.
  Δt ≈ 0                           -> ring does NOT act as GR source.
  Δt < 0                           -> anti-gravity (unphysical).
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
    build_nb, make_state, init_phi_single_ring, yoshida4_step,
    ring_mass_deficit,
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


def inject_pulse(state, x_coords, y_coords, z_coords, x0, y0, z0,
                 sigma, k, A):
    """Add rightward-traveling Gaussian wave packet to phi, pi_phi.

    phi      -> phi + A * env(x,y,z) * cos(k*(x-x0))
    pi_phi   -> pi_phi - mu_phi * omega * A * env(x,y,z) * sin(k*(x-x0))

    Sign chosen so packet moves in +x direction:
      phi_pulse(x,t) = A env(x - c_g*t) * cos(k(x-x0) - omega*t)
      d/dt phi = -A env * omega * sin(k(x-x0) - omega*t)  (at t=0)
      pi_phi = mu_phi * d/dt phi = -mu_phi * A env * omega * sin(k*(x-x0))
    """
    omega = C_PHI * k   # massless in vacuum
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
    """Evolve under full v8 dynamics and record phi at detector index vs time."""
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


def find_peak_arrival(t, phi_signal, phi_threshold=None):
    """Find first envelope peak. Returns (t_peak, amp_peak)."""
    abs_sig = np.abs(phi_signal)
    # Smooth with a short moving average to get envelope
    window = 3
    if len(abs_sig) < window:
        return float('nan'), float('nan')
    env = np.convolve(abs_sig, np.ones(window) / window, mode='same')
    i_peak = int(np.argmax(env))
    return float(t[i_peak]), float(env[i_peak])


def main():
    print("=" * 80)
    print("Einstein test #3b: Shapiro delay (1919 light-bending analog)")
    print("=" * 80)
    print(f"  c_phi   = {C_PHI:.5f}   (phi wave speed in vacuum)")
    print(f"  c_phi^2 = {C_PHI_SQ:.5f}  = BETA_PHI/(6 mu_phi)")
    print()

    L = 28
    R = 4
    T_track = 250.0
    DT_sample = 1.0         # sample every 1 lu
    sample_every = int(DT_sample / DT)

    x_coords, y_coords, z_coords = make_coords(L)
    N = L * L * L

    # Geometry
    x_source  = 4.0
    x_detect  = L - 4.0             # = 24
    y_line    = 0.5 * L + R         # passes through ring core at x=L/2
    z_line    = 0.5 * L
    sigma_pkt = 2.0
    k_pkt     = np.pi / 4.0          # wavelength = 8
    A_pkt     = 0.05

    # Detector node index
    xd_int = int(round(x_detect))
    yd_int = int(round(y_line))
    zd_int = int(round(z_line))
    detector_idx = xd_int + yd_int * L + zd_int * L * L

    omega_vac = C_PHI * k_pkt
    t_vac_theory = (x_detect - x_source) / C_PHI

    print(f"  L={L}, R={R}")
    print(f"  Pulse: source=({x_source:.1f}, {y_line:.1f}, {z_line:.1f})")
    print(f"         sigma={sigma_pkt}, k={k_pkt:.3f}, A={A_pkt}")
    print(f"  Detect: ({x_detect:.1f}, {y_line:.1f}, {z_line:.1f})  "
          f"[idx={detector_idx}]")
    print(f"  Distance = {x_detect - x_source:.1f} nodes")
    print(f"  Vac ToF theory = d/c_phi = {t_vac_theory:.1f} lu")
    print(f"  T_track = {T_track} lu  (sample every {DT_sample:.1f} lu)")
    print()

    # --- 1. Vacuum pulse run ---
    print("[1] Vacuum + pulse")
    nb_idx = build_nb(L)
    vac_state = make_state(L, phi_init=None)
    inject_pulse(vac_state, x_coords, y_coords, z_coords,
                 x_source, y_line, z_line, sigma_pkt, k_pkt, A_pkt)
    print(f"    injected pulse (phi max={float(cp.max(cp.abs(vac_state['phi']))):.4f})")
    _, t_vac, phi_vac = evolve_record(vac_state, nb_idx, T_track,
                                      detector_idx, sample_every,
                                      verbose=True, label='vacuum')

    # --- 2. Form ring (cache-backed) ---
    print()
    print("[2] Ring formation (P1=300, P2=1000 lu) [cache-backed]")
    ring_state, nb_idx_r = form_ring_cached(L, R, T_P1=300.0, T_P2=1000.0)
    M_ring0 = float(ring_mass_deficit(ring_state['sm']))
    print(f"    ring ready, M_ring={M_ring0:.2f}")

    # --- 3. Ring-only baseline (no pulse) ---
    print()
    print("[3] Ring-only baseline evolution (no pulse)")
    ring_copy_bg = clone_state(ring_state)
    _, t_bg, phi_bg = evolve_record(ring_copy_bg, nb_idx_r, T_track,
                                    detector_idx, sample_every,
                                    verbose=True, label='ring_only')

    # --- 4. Ring + pulse run ---
    print()
    print("[4] Ring + pulse evolution")
    ring_copy_p = clone_state(ring_state)
    inject_pulse(ring_copy_p, x_coords, y_coords, z_coords,
                 x_source, y_line, z_line, sigma_pkt, k_pkt, A_pkt)
    _, t_rp, phi_rp = evolve_record(ring_copy_p, nb_idx_r, T_track,
                                    detector_idx, sample_every,
                                    verbose=True, label='ring+pulse')

    # --- 5. Extract pulse-in-ring signal ---
    # Ensure same time grid (they should match)
    assert np.allclose(t_vac, t_rp), "time grids differ"
    phi_pulse_ring = phi_rp - phi_bg    # pulse contribution only

    # --- 6. Peak arrival detection ---
    t_peak_vac, amp_vac = find_peak_arrival(t_vac, phi_vac)
    t_peak_ring, amp_ring = find_peak_arrival(t_rp, phi_pulse_ring)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"  Vacuum pulse:  t_peak = {t_peak_vac:.2f} lu   amp = {amp_vac:.5f}")
    print(f"  Ring  pulse:   t_peak = {t_peak_ring:.2f} lu   amp = {amp_ring:.5f}")
    print(f"  Theory ToF:    t_vac_theory = {t_vac_theory:.2f} lu (massless)")
    print()
    delta_t = t_peak_ring - t_peak_vac
    print(f"  Shapiro delay:  dt = t_ring - t_vac = {delta_t:+.3f} lu")
    frac = delta_t / max(t_peak_vac, 1e-6)
    print(f"                    ratio = {frac*100:+.2f}%")
    print()

    # Print sampled signal snapshots
    print("  Signal samples (t, phi_vac, phi_pulse_in_ring):")
    n_samp = min(30, len(t_vac))
    step = max(1, len(t_vac) // n_samp)
    for i in range(0, len(t_vac), step):
        print(f"    t={t_vac[i]:6.1f}   phi_vac={phi_vac[i]:+.5f}   "
              f"phi_ring={phi_pulse_ring[i]:+.5f}   phi_bg={phi_bg[i]:+.5f}")

    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    if np.isnan(delta_t):
        print("INCONCLUSIVE: could not extract peaks cleanly. Inspect signals.")
    elif delta_t > 0.5:
        print(f"SHAPIRO POSITIVE: ring delays phi wave by {delta_t:.2f} lu.")
        print("  -> v8 ring acts as GR mass source for phi (light) propagation.")
        print("  -> Einstein 1919 light-bending analog PASS.")
    elif delta_t > -0.5:
        print(f"NULL RESULT: |Δt| = {abs(delta_t):.2f} lu (< 0.5 lu noise floor).")
        print("  -> Ring does NOT measurably slow phi waves at this amplitude.")
        print("  -> Could be: effect too small, noise dominated, or no coupling.")
    else:
        print(f"SHAPIRO NEGATIVE: Δt = {delta_t:.2f} lu (wave SPED UP near ring).")
        print("  -> Unphysical sign — anti-gravity? Investigate.")

    # Save raw trajectories for inspection
    outdir = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    np.savez(outdir / "shapiro_probe_signals.npz",
             t=t_vac, phi_vac=phi_vac, phi_ring_pulse=phi_pulse_ring,
             phi_ring_bg=phi_bg,
             detector=(xd_int, yd_int, zd_int),
             c_phi=C_PHI, M_ring0=M_ring0)
    print(f"\n  Signals saved to {outdir / 'shapiro_probe_signals.npz'}")


if __name__ == "__main__":
    main()
