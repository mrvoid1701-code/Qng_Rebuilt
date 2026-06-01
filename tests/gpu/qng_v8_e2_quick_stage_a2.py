"""Quick Stage A2 probe under Option E^2 (DER-QNG-042-A2).

Tests the mass-generation prediction: with V_couple = (g/2)*deficit^2*(1-cos phi),
in a region with DEFICIT > 0 (sm < SIGMA_M_REF), phi should oscillate at
    omega_core = sqrt((g/2) * deficit^2 / mu_phi)
(factor 1/2 matches the 1/2 in V_couple; force = -0.5*g*deficit^2*sin(phi)).

We isolate the phi sector with sm FROZEN at a uniform chosen value:
only (phi, pi_phi) evolve under the E^2 force
    F_phi = -0.5 * g * deficit^2 * sin(phi)
    phi_dot = pi_phi / mu_phi
    pi_phi_dot = F_phi

Scan deficit in {0.10, 0.20, 0.25} and compare measured omega to theory.
Stage A1 (vacuum, deficit=0) already confirmed omega = 0.

If omega(deficit) matches sqrt(g*deficit^2/mu_phi) within 5%:
   -> E^2 mass-generation confirmed; Stage A1+A2 dichotomy closed.
If omega flat or mismatched -> amendment is wrong or not in effect.
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
from qng_v8_canonical_gpu import SIGMA_M_REF, MU_PHI, G_V_COUPLE


def evolve_phi_only(L, deficit, T, dt, eps):
    """Evolve (phi, pi_phi) under E^2 mass term with sm FROZEN at deficit."""
    N = L * L * L
    sm_val = SIGMA_M_REF - deficit
    # Uniform fields
    phi = eps * cp.ones(N, dtype=cp.float64)
    pi_phi = cp.zeros(N, dtype=cp.float64)
    deficit_arr = cp.full(N, deficit, dtype=cp.float64)
    inv_mu = 1.0 / MU_PHI
    g = float(G_V_COUPLE)

    # Symplectic leapfrog (drift-kick-drift)
    nsteps = int(T / dt)
    phi_trace = []
    t_trace = []
    sample_every = 2

    t0 = time.time()
    # Half-drift
    phi = phi + 0.5 * dt * pi_phi * inv_mu
    for s in range(nsteps):
        if s % sample_every == 0:
            phi_trace.append(float(cp.mean(phi)))
            t_trace.append(s * dt)
        # Full kick
        F_phi = -0.5 * g * (deficit_arr * deficit_arr) * cp.sin(phi)
        pi_phi = pi_phi + dt * F_phi
        # Full drift
        phi = phi + dt * pi_phi * inv_mu
    # Close: last sample
    phi_trace.append(float(cp.mean(phi)))
    t_trace.append(nsteps * dt)

    wall = time.time() - t0
    phi_arr = np.array(phi_trace)
    t_arr = np.array(t_trace)

    # FFT
    dt_sample = t_arr[1] - t_arr[0]
    phi_c = phi_arr - phi_arr.mean()
    fft = np.fft.rfft(phi_c)
    freqs = np.fft.rfftfreq(len(phi_arr), d=dt_sample)
    power = np.abs(fft) ** 2
    peak_idx = np.argmax(power[1:]) + 1
    # Parabolic interpolation around the peak for sub-bin accuracy
    if 1 < peak_idx < len(power) - 1:
        y0, y1, y2 = power[peak_idx - 1], power[peak_idx], power[peak_idx + 1]
        denom = (y0 - 2 * y1 + y2)
        offset = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
        freq_peak = freqs[peak_idx] + offset * (freqs[1] - freqs[0])
    else:
        freq_peak = freqs[peak_idx]
    omega_peak = 2 * np.pi * freq_peak

    zero_crossings = 0
    for i in range(1, len(phi_arr)):
        if (phi_arr[i - 1] - phi_arr.mean()) * (phi_arr[i] - phi_arr.mean()) < 0:
            zero_crossings += 1

    omega_theory = float(np.sqrt(0.5 * g * deficit * deficit / MU_PHI))
    return {
        'deficit': deficit,
        'sm_val': sm_val,
        'omega_theory': omega_theory,
        'omega_measured': omega_peak,
        'rel_err': (omega_peak - omega_theory) / max(omega_theory, 1e-12),
        'n_zero_crossings': zero_crossings,
        'phi_range': (phi_arr.min(), phi_arr.max()),
        'phi_initial': phi_arr[0],
        'phi_final': phi_arr[-1],
        'wall': wall,
    }


def main():
    print("=" * 76)
    print("Quick Stage A2 probe under Option E^2 (DER-QNG-042-A2)")
    print("=" * 76)
    print(f"  g={G_V_COUPLE}  mu_phi={MU_PHI:.4f}  SIGMA_M_REF={SIGMA_M_REF}")
    print(f"  Theory: omega_core(deficit) = sqrt((g/2) * deficit^2 / mu_phi)")
    print()

    L = 16
    dt = 0.025
    eps = 0.05
    # Larger T for smaller deficit (lower omega -> need more cycles for FFT)
    # deficit=0.10 -> ~4.5 cycles at T=800; scale T inversely
    deficits_T = [(0.10, 2400), (0.20, 1200), (0.25, 1200)]
    print(f"{'deficit':>8} {'sm_val':>8} {'omega_th':>10} {'omega_meas':>12} "
          f"{'rel_err':>10} {'zero_cr':>8} {'wall':>6}")
    print("-" * 76)

    results = []
    for d, T in deficits_T:
        r = evolve_phi_only(L=L, deficit=d, T=T, dt=dt, eps=eps)
        results.append(r)
        print(f"{r['deficit']:>8.3f} {r['sm_val']:>8.3f} "
              f"{r['omega_theory']:>10.4f} {r['omega_measured']:>12.4f} "
              f"{r['rel_err']*100:>9.2f}% {r['n_zero_crossings']:>8d} "
              f"{r['wall']:>5.1f}s")

    print()
    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    all_pass = all(abs(r['rel_err']) < 0.05 for r in results)
    if all_pass:
        print("STAGE A2 PASS: omega(deficit) tracks sqrt(g*deficit^2/mu_phi) within 5%.")
        print("  -> E^2 mass-generation confirmed in ring-core-like regions.")
        print("  -> Combined with A1 (vacuum massless): position-dependent mass")
        print("     m_phi^2(x) = g*deficit(x)^2/mu_phi demonstrated.")
        print("  -> Goldstone -> gapped transition realized by deficit field.")
    else:
        worst = max(results, key=lambda r: abs(r['rel_err']))
        print(f"STAGE A2 FAIL: worst case deficit={worst['deficit']}, "
              f"rel_err={worst['rel_err']*100:.2f}%.")
        print("  -> Either amendment not in effect or E^2 prediction wrong.")


if __name__ == "__main__":
    main()
