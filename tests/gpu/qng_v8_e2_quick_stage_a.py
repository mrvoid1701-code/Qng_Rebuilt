"""Quick Stage A probe under Option E^2 (DER-QNG-042-A1).

Tests the core E^2 prediction: in FLAT VACUUM (sm = sm_ref everywhere),
phi should be massless. Excite uniform phi = eps cos(k=0), evolve, measure
oscillation frequency.

Original V_couple prediction: omega(k=0) ~= 0.359 (m_phi massive)
Option E^2 prediction:        omega(k=0) ~= 0    (massless Goldstone in vacuum)

If omega ~ 0 -> E^2 confirmed, Goldstone theorem restored in vacuum.
If omega ~ 0.359 -> module amend didn't take effect or E^2 wrong.
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
    SIGMA_G_REF, SIGMA_M_REF, MU_PHI, G_V_COUPLE,
    build_nb, make_state, yoshida4_step,
)


def quick_stage_a(L=20, T=400, dt=0.025, eps=0.05, k=0):
    """Measure omega(k) for uniform phi excitation in vacuum."""
    nb = build_nb(L)

    # Init flat vacuum state (all arrays are flat (N,) in canonical_gpu)
    state = make_state(L, phi_init=None)
    N = L * L * L
    # Excite uniform phi (k=0 is just phi = eps everywhere)
    if k == 0:
        phi0 = eps * cp.ones(N, dtype=cp.float64)
    else:
        x = cp.arange(L).reshape(L, 1, 1)
        phi3 = eps * cp.cos(2 * cp.pi * k * x / L)
        phi3 = cp.broadcast_to(phi3, (L, L, L)).copy()
        phi0 = phi3.reshape(-1).astype(cp.float64)
    state['phi'] = phi0

    nsteps = int(T / dt)
    phi_mean_trace = []
    t_trace = []
    sample_every = 2  # every 0.05 lu

    t0 = time.time()
    for s in range(nsteps + 1):
        if s % sample_every == 0:
            phi_mean_trace.append(float(cp.mean(state['phi'])))
            t_trace.append(s * dt)
        if s < nsteps:
            state = yoshida4_step(state, dt, nb, v_couple_on=True, damping_gamma=0.0)

    wall = time.time() - t0
    phi_arr = np.array(phi_mean_trace)
    t_arr = np.array(t_trace)

    # Detect oscillation: FFT of mean phi
    dt_sample = t_arr[1] - t_arr[0]
    phi_centered = phi_arr - phi_arr.mean()
    fft = np.fft.rfft(phi_centered)
    freqs = np.fft.rfftfreq(len(phi_arr), d=dt_sample)
    power = np.abs(fft) ** 2
    peak_idx = np.argmax(power[1:]) + 1   # skip DC
    omega_peak = 2 * np.pi * freqs[peak_idx]
    amp_peak = np.sqrt(power[peak_idx]) / len(phi_arr)
    amp_dc = abs(fft[0]) / len(phi_arr)

    # Also measure first zero crossing or envelope decay
    zero_crossings = 0
    for i in range(1, len(phi_arr)):
        if (phi_arr[i - 1] - phi_arr.mean()) * (phi_arr[i] - phi_arr.mean()) < 0:
            zero_crossings += 1

    return {
        'L': L, 'T': T, 'dt': dt, 'eps': eps, 'k': k,
        'wall': wall,
        'omega_fft_peak': omega_peak,
        'amp_peak': amp_peak,
        'amp_dc': amp_dc,
        'n_zero_crossings': zero_crossings,
        'phi_initial': phi_arr[0],
        'phi_final': phi_arr[-1],
        'phi_range': (phi_arr.min(), phi_arr.max()),
    }


def main():
    print("=" * 76)
    print("Quick Stage A probe under Option E^2 (DER-QNG-042-A1)")
    print("=" * 76)
    print(f"  g={G_V_COUPLE}  mu_phi={MU_PHI}")
    print(f"  Original V_couple prediction: omega(k=0) = sqrt(g*sg_ref/mu_phi) = {np.sqrt(G_V_COUPLE * SIGMA_G_REF / MU_PHI):.4f}")
    print(f"  E^2 prediction:               omega(k=0) = 0 (vacuum deficit = 0)")
    print(f"  Gate (old, pre-amend):        omega(k=0) in [0.323, 0.395]")
    print()

    print("--- Test 1: flat vacuum (sm = sm_ref), uniform phi = 0.05 ---")
    r = quick_stage_a(L=20, T=400, dt=0.025, eps=0.05, k=0)
    print(f"  wall={r['wall']:.1f}s  n_zero_crossings={r['n_zero_crossings']}")
    print(f"  phi range: [{r['phi_range'][0]:.4f}, {r['phi_range'][1]:.4f}]")
    print(f"  phi initial -> final: {r['phi_initial']:.4f} -> {r['phi_final']:.4f}")
    print(f"  omega_fft_peak = {r['omega_fft_peak']:.4f}")
    print(f"  amp_peak/amp_dc ratio = {r['amp_peak'] / max(r['amp_dc'], 1e-12):.4e}")
    print()

    # Verdict
    omega = r['omega_fft_peak']
    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    if omega < 0.02 and r['n_zero_crossings'] <= 2:
        print("E^2 CONFIRMED: omega(k=0) ~= 0 in vacuum (massless as predicted).")
        print("  -> Goldstone theorem restored in vacuum under Option E^2.")
        print("  -> Original Stage A gate [0.323, 0.395] is INAPPROPRIATE for E^2")
        print("     (it was designed for the obsolete V_couple = g*sg*(1-cos phi)).")
        print("  -> Stage A must be restructured to A1 (vacuum massless) + A2 (ring-core mass).")
    elif 0.32 < omega < 0.40:
        print(f"UNEXPECTED: omega = {omega:.4f} matches OLD V_couple prediction.")
        print("  -> E^2 amendment may NOT be active in canonical_gpu.py.")
        print("  -> Verify that module reload worked.")
    else:
        print(f"UNEXPECTED: omega = {omega:.4f}, neither 0 nor 0.359.")
        print("  -> Investigate: possibly residual from BETA_PHI diffusion or numerical jitter.")


if __name__ == "__main__":
    main()
