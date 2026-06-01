"""Klein-Gordon dispersion probe under Option E^2 (DER-QNG-042 / Einstein test #1).

Tests the full relativistic E^2 = (pc)^2 + (mc^2)^2 in the phi sector:
in a uniform-deficit region, a plane-wave phi excitation at wavenumber k
must satisfy

    omega^2(k) = c_phi^2 * k^2 + m_rest^2      (small-k KG form)

or the exact lattice dispersion

    omega^2(k) = (BETA_PHI/(3*mu_phi)) * (1 - cos k) + (g/2)*deficit^2/mu_phi

If slope(omega^2 vs k^2) = c_phi^2 = BETA_PHI/(6*mu_phi) = 0.01167
and intercept = m_rest^2 = (g/2)*deficit^2/mu_phi, then Einstein's E^2
relation is numerically realized in the QNG substrate.

This is the direct numerical test of E = mc^2 at p=0 (the intercept) AND
the full E^2 = p^2 c^2 + m^2 c^4 relation (the slope).
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
    SIGMA_M_REF, MU_PHI, G_V_COUPLE, BETA_PHI, build_nb,
)


def wrap(x):
    return cp.remainder(x + cp.pi, 2 * cp.pi) - cp.pi


def evolve_phi_wave(L, deficit, k_lattice, T, dt, eps, nb_idx):
    """Evolve (phi, pi_phi) on a plane-wave excitation with frozen sm.

    phi(r, 0) = eps * cos(k_x * x)  (along x-axis only)
    sm        = SIGMA_M_REF - deficit  (uniform, frozen)
    EOM: mu_phi * phi_ddot = BETA_PHI*(phi_mean - phi) - 0.5*g*deficit^2*sin(phi)
    """
    N = L * L * L
    # Cubic lattice coordinates
    idx = cp.arange(N, dtype=cp.int64)
    x = (idx % L).astype(cp.float64)
    # Plane wave along x
    phi = eps * cp.cos(k_lattice * x)
    pi_phi = cp.zeros(N, dtype=cp.float64)
    inv_mu = 1.0 / MU_PHI
    g = float(G_V_COUPLE)
    deficit2 = float(deficit) ** 2

    nsteps = int(T / dt)
    sample_every = 2

    # Projector: integrate phi * cos(k*x) / N_positions, recovers amplitude of
    # k-mode. For amplitude-only trace we use spatial projection.
    proj_weight = cp.cos(k_lattice * x) / N

    amp_trace = []
    t_trace = []

    t0 = time.time()
    # Half-drift
    phi = phi + 0.5 * dt * pi_phi * inv_mu
    for s in range(nsteps):
        if s % sample_every == 0:
            amp_trace.append(float(2.0 * cp.sum(phi * proj_weight * N) / N))
            t_trace.append(s * dt)
        # Phi mean over neighbors (uniform sm -> unweighted mean)
        # nb_idx has shape (N, 6): indices of 6 neighbors
        phi_nb = phi[nb_idx]                       # (N, 6)
        phi_mean = cp.mean(phi_nb, axis=1)         # (N,)
        # Wrap (phi_mean - phi) into (-pi, pi]
        dphi = wrap(phi_mean - phi)
        F_diff = BETA_PHI * dphi
        F_mass = -0.5 * g * deficit2 * cp.sin(phi)
        F_phi = F_diff + F_mass
        # Kick
        pi_phi = pi_phi + dt * F_phi
        # Drift
        phi = phi + dt * pi_phi * inv_mu
    amp_trace.append(float(2.0 * cp.sum(phi * proj_weight * N) / N))
    t_trace.append(nsteps * dt)

    wall = time.time() - t0
    amp = np.array(amp_trace)
    t = np.array(t_trace)

    # FFT for omega with parabolic interpolation
    dt_s = t[1] - t[0]
    ac = amp - amp.mean()
    fft = np.fft.rfft(ac)
    freqs = np.fft.rfftfreq(len(amp), d=dt_s)
    power = np.abs(fft) ** 2
    if len(power) <= 3:
        omega = 0.0
    else:
        pk = np.argmax(power[1:]) + 1
        if 1 < pk < len(power) - 1:
            y0, y1, y2 = power[pk - 1], power[pk], power[pk + 1]
            denom = (y0 - 2 * y1 + y2)
            offset = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
            fp = freqs[pk] + offset * (freqs[1] - freqs[0])
        else:
            fp = freqs[pk]
        omega = 2 * np.pi * fp

    zc = 0
    for i in range(1, len(amp)):
        if (amp[i - 1] - amp.mean()) * (amp[i] - amp.mean()) < 0:
            zc += 1

    return {
        'k': float(k_lattice),
        'omega': float(omega),
        'amp_range': (float(amp.min()), float(amp.max())),
        'n_zero_crossings': zc,
        'wall': wall,
    }


def main():
    print("=" * 80)
    print("Klein-Gordon dispersion probe — Einstein test #1 (DER-QNG-042 E^2)")
    print("=" * 80)
    print(f"  g={G_V_COUPLE}  mu_phi={MU_PHI:.4f}  BETA_PHI={BETA_PHI}")

    L = 16
    dt = 0.025
    eps = 0.05
    deficit = 0.20
    deficit2 = deficit * deficit

    # Theory
    m_rest_sq = 0.5 * float(G_V_COUPLE) * deficit2 / float(MU_PHI)
    c_phi_sq_small = float(BETA_PHI) / (6.0 * float(MU_PHI))
    slope_exact = float(BETA_PHI) / (3.0 * float(MU_PHI))
    print(f"  deficit={deficit}  m_rest^2 = (g/2)*deficit^2/mu_phi = {m_rest_sq:.5f}")
    print(f"  c_phi^2 (small-k)      = BETA_PHI/(6*mu_phi)       = {c_phi_sq_small:.5f}")
    print(f"  lattice slope exact    = BETA_PHI/(3*mu_phi)       = {slope_exact:.5f}")
    print()

    # Lattice k values: 2*pi*n/L for n=0..4
    nb_idx = build_nb(L)
    ks = [2.0 * np.pi * n / L for n in range(5)]

    print(f"{'n':>2} {'k':>7} {'T':>6} {'omega_meas':>12} {'omega_th':>10} "
          f"{'rel_err':>10} {'zero_cr':>8}")
    print("-" * 80)

    rows = []
    for n, k in enumerate(ks):
        # Scale T inversely to omega so we get >=5 cycles even for small k
        omega_pred = float(np.sqrt(slope_exact * (1 - np.cos(k)) + m_rest_sq))
        period = 2 * np.pi / max(omega_pred, 0.01)
        T = max(1200, 8 * period)   # at least 8 cycles
        r = evolve_phi_wave(L=L, deficit=deficit, k_lattice=float(k),
                            T=T, dt=dt, eps=eps, nb_idx=nb_idx)
        rel = (r['omega'] - omega_pred) / max(omega_pred, 1e-12)
        rows.append((n, k, omega_pred, r['omega'], rel, r['n_zero_crossings']))
        print(f"{n:>2} {k:>7.4f} {T:>6.0f} {r['omega']:>12.5f} "
              f"{omega_pred:>10.5f} {rel*100:>9.2f}% {r['n_zero_crossings']:>8d}")

    print()
    # Fit ω^2 vs k^2 for small-k linear check
    k_arr = np.array([row[1] for row in rows])
    w_arr = np.array([row[3] for row in rows])
    w2 = w_arr ** 2
    k2 = k_arr ** 2
    small_k = k_arr < 1.0  # n=0,1,2
    if small_k.sum() >= 2:
        slope, intercept = np.polyfit(k2[small_k], w2[small_k], 1)
        print(f"[Small-k linear fit over n in {{0,1,2}}]")
        print(f"  slope (c_phi^2)     = {slope:.5f}   (theory: {c_phi_sq_small:.5f}, "
              f"err {(slope-c_phi_sq_small)/c_phi_sq_small*100:+.2f}%)")
        print(f"  intercept (m_rest^2)= {intercept:.5f}   (theory: {m_rest_sq:.5f}, "
              f"err {(intercept-m_rest_sq)/m_rest_sq*100:+.2f}%)")

    # Fit ω^2 vs (1-cos k) for lattice-exact check
    lcos = 1 - np.cos(k_arr)
    slope_l, inter_l = np.polyfit(lcos, w2, 1)
    print(f"[Lattice-exact linear fit over all k]")
    print(f"  slope              = {slope_l:.5f}   (theory: {slope_exact:.5f}, "
          f"err {(slope_l-slope_exact)/slope_exact*100:+.2f}%)")
    print(f"  intercept          = {inter_l:.5f}   (theory: {m_rest_sq:.5f}, "
          f"err {(inter_l-m_rest_sq)/m_rest_sq*100:+.2f}%)")

    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    all_rel = [abs(row[4]) for row in rows]
    if max(all_rel) < 0.05:
        print("E^2 DISPERSION CONFIRMED: omega(k) tracks Klein-Gordon lattice form")
        print("  within 5% across k=0..pi/2. Einstein relation E^2 = p^2 c^2 + m^2 c^4")
        print("  is numerically realized in the QNG phi sector.")
        print(f"  -> Rest mass:  m_rest^2 = (g/2)*deficit^2/mu_phi = {m_rest_sq:.5f}")
        print(f"  -> Wave speed: c_phi^2  = BETA_PHI/(6*mu_phi)    = {c_phi_sq_small:.5f}")
        print("  -> E = mc^2 at p=0 verified (A1+A2 covered the p=0 limit).")
        print("  -> Finite-k term kicks in exactly as Klein-Gordon predicts.")
    else:
        worst = max(rows, key=lambda r: abs(r[4]))
        print(f"DISPERSION FAIL: worst n={worst[0]}, k={worst[1]:.4f}, "
              f"omega_meas={worst[3]:.5f} vs theory={worst[2]:.5f} "
              f"(err {worst[4]*100:.2f}%).")
        print("  -> Either kinetic term coefficient wrong or lattice formula off.")


if __name__ == "__main__":
    main()
