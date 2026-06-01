"""QNG-GPU-026: 4D KG dispersion — dimension robustness of v8 substrate.

Tests whether the v8 phi wave equation
    mu_phi * d^2_t phi = BETA_PHI * (phi_mean - phi)  (on flat sm=sm_ref)
admits the expected dispersion ω² = (BETA_PHI/mu_phi)·(1-cos k)/d on a
4D cubic lattice (z=8), where d is the spatial dimension.

Prediction:
  - 3D cubic (z=6, d=3): c_phi² = BETA_PHI / (6 * mu_phi) = 0.01167
  - 4D cubic (z=8, d=4): c_phi² = BETA_PHI / (8 * mu_phi) = 0.00875
  - ratio 4D/3D = 6/8 = 0.75

Self-contained: does NOT depend on 3D make_state or ring formation.
Uses only the 4D phi+pi_phi canonical pair (V_couple = 0 on sm=sm_ref).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    BETA_PHI, MU_PHI, G_V_COUPLE, SIGMA_M_REF,
    DT, CHI_DECAY_V7,
)


# =============================================================================
# 4D lattice utilities
# =============================================================================

def build_nb_4d(L):
    """8-neighbor index table for periodic 4D cubic lattice, shape (N, 8).
    Index = x*L^3 + y*L^2 + z*L + w."""
    xs = np.arange(L, dtype=np.int64)
    xg, yg, zg, wg = np.meshgrid(xs, xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel(); wg = wg.ravel()
    L3 = L * L * L; L2 = L * L
    def idx(x, y, z, w): return x * L3 + y * L2 + z * L + w
    nb = np.stack([
        idx((xg - 1) % L, yg, zg, wg),
        idx((xg + 1) % L, yg, zg, wg),
        idx(xg, (yg - 1) % L, zg, wg),
        idx(xg, (yg + 1) % L, zg, wg),
        idx(xg, yg, (zg - 1) % L, wg),
        idx(xg, yg, (zg + 1) % L, wg),
        idx(xg, yg, zg, (wg - 1) % L),
        idx(xg, yg, zg, (wg + 1) % L),
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def nb_mean(field, nb_idx):
    return field[nb_idx].mean(axis=1)


def wrap_gpu(a):
    a = a % (2.0 * math.pi)
    return cp.where(a > math.pi, a - 2.0 * math.pi, a)


def centered_x(L):
    """Centered x coordinate flat-indexed (for x*L^3 + y*L^2 + z*L + w ordering)."""
    xs = np.arange(L, dtype=np.float64)
    xg, _, _, _ = np.meshgrid(xs, xs, xs, xs, indexing='ij')
    dx = xg - L / 2.0
    dx = np.where(dx > L / 2, dx - L, dx)
    dx = np.where(dx < -L / 2, dx + L, dx)
    return cp.asarray(dx.ravel())


# =============================================================================
# Minimal 4D phi evolution (V_couple = 0 on sm=sm_ref, so pure kinetic)
# =============================================================================

def force_phi_4d(phi, nb_idx):
    """F_phi on flat vacuum sm=sm_ref: just the kinetic coupling to phi_mean."""
    phi_mean = nb_mean(phi, nb_idx)
    return BETA_PHI * wrap_gpu(phi_mean - phi)


def kick_phi(phi, pi_phi, nb_idx, dt):
    return pi_phi + dt * force_phi_4d(phi, nb_idx)


def drift_phi(phi, pi_phi, dt):
    return wrap_gpu(phi + dt * pi_phi / MU_PHI)


def yoshida4_phi_step(phi, pi_phi, nb_idx, dt):
    """4th-order Yoshida symplectic for the minimal (phi, pi_phi) pair."""
    w0 = -math.pow(2.0, 1.0 / 3.0) / (2.0 - math.pow(2.0, 1.0 / 3.0))
    w1 = 1.0 / (2.0 - math.pow(2.0, 1.0 / 3.0))
    weights = (w1, w0, w1)
    for w in weights:
        h = w * dt
        pi_phi = kick_phi(phi, pi_phi, nb_idx, h / 2.0)
        phi = drift_phi(phi, pi_phi, h)
        pi_phi = kick_phi(phi, pi_phi, nb_idx, h / 2.0)
    return phi, pi_phi


# =============================================================================
# Dispersion probe
# =============================================================================

def run_dispersion(L, K_VALUES, T_PHYS, EPS=0.05, sample_every=4):
    """Measure omega(k) for plane-wave phi initial conditions on flat vacuum."""
    N = L ** 4
    nb_idx = build_nb_4d(L)
    x_coord = centered_x(L)
    N_STEPS = int(T_PHYS / DT)

    results = {}
    for k_mode in K_VALUES:
        if k_mode == 0:
            phi = cp.full(N, EPS, dtype=cp.float64)
        else:
            k_phys = 2.0 * math.pi * k_mode / L
            phi = EPS * cp.cos(k_phys * x_coord)
        pi_phi = cp.zeros(N, dtype=cp.float64)

        trace_t = []; trace_amp = []
        t0 = time.time()
        for istep in range(N_STEPS):
            phi, pi_phi = yoshida4_phi_step(phi, pi_phi, nb_idx, DT)
            if istep % sample_every == 0:
                if k_mode == 0:
                    amp = float(cp.mean(phi))
                else:
                    k_phys = 2.0 * math.pi * k_mode / L
                    amp = float(cp.mean(phi * cp.cos(k_phys * x_coord))) * 2.0
                trace_t.append(istep * DT)
                trace_amp.append(amp)
        wall = time.time() - t0

        t_arr = np.array(trace_t)
        amp_arr = np.array(trace_amp) - np.mean(trace_amp)
        n_fft = len(amp_arr)
        dt_sample = t_arr[1] - t_arr[0]
        freqs = np.fft.fftfreq(n_fft, d=dt_sample)[:n_fft // 2]
        spec = np.abs(np.fft.fft(amp_arr)[:n_fft // 2])
        if len(spec) > 2:
            peak_idx = int(np.argmax(spec[1:])) + 1
            f_peak = float(freqs[peak_idx])
        else:
            f_peak = 0.0
        omega_meas = 2.0 * math.pi * f_peak

        k_phys = 2.0 * math.pi * k_mode / L if k_mode > 0 else 0.0
        # Theoretical: omega^2 = (BETA_PHI/mu_phi) * (1 - cos k_phys) / d, d=4
        omega_pred = math.sqrt((BETA_PHI / MU_PHI) * (1.0 - math.cos(k_phys)) / 4.0)
        # 3D reference for comparison
        omega_pred_3d = math.sqrt((BETA_PHI / MU_PHI) * (1.0 - math.cos(k_phys)) / 3.0)

        results[k_mode] = {
            'k_mode': k_mode,
            'k_phys': k_phys,
            'omega_meas': omega_meas,
            'omega_pred_4d': omega_pred,
            'omega_pred_3d': omega_pred_3d,
            'ratio_meas_pred_4d': (omega_meas / omega_pred) if omega_pred > 0 else 0.0,
            'ratio_meas_pred_3d': (omega_meas / omega_pred_3d) if omega_pred_3d > 0 else 0.0,
            'runtime_sec': wall,
        }
        print(f"  k={k_mode}: k_phys={k_phys:.4f}  "
              f"omega_meas={omega_meas:.5f}  "
              f"pred_4d={omega_pred:.5f}  pred_3d={omega_pred_3d:.5f}  "
              f"(ratio_4d={results[k_mode]['ratio_meas_pred_4d']:.3f})  "
              f"({wall:.1f}s)",
              flush=True)

    return results


def main():
    print("=" * 80)
    print("QNG-GPU-026: 4D KG DISPERSION — dimension robustness of v8 substrate")
    print("=" * 80)

    L = 12
    K_VALUES = [1, 2, 3]
    T_PHYS = 500.0   # 20000 Yoshida substeps; enough FFT resolution

    print(f"  L = {L} (4D, N={L**4} nodes)")
    print(f"  BETA_PHI={BETA_PHI}, MU_PHI={MU_PHI:.6f}")
    c2_4d_pred = BETA_PHI / (8.0 * MU_PHI)
    c2_3d_pred = BETA_PHI / (6.0 * MU_PHI)
    print(f"  Predicted c_phi^2 (4D, z=8): {c2_4d_pred:.6f}")
    print(f"  Predicted c_phi^2 (3D, z=6): {c2_3d_pred:.6f}")
    print(f"  4D/3D ratio: {c2_4d_pred/c2_3d_pred:.4f}  (expected 6/8 = 0.75)")
    print(f"  T_PHYS={T_PHYS} lu  DT={DT}  N_STEPS={int(T_PHYS/DT)}")
    print()

    results = run_dispersion(L, K_VALUES, T_PHYS)

    # Verdict: within 10% of 4D prediction AND clearly different from 3D prediction
    passes_4d = []
    for k in K_VALUES:
        r = results[k]
        err_4d = abs(r['omega_meas'] - r['omega_pred_4d']) / max(r['omega_pred_4d'], 1e-10)
        err_3d = abs(r['omega_meas'] - r['omega_pred_3d']) / max(r['omega_pred_3d'], 1e-10)
        passes_4d.append(err_4d < 0.10 and err_3d > 0.10)
        print(f"  k={k}: err_vs_4d={err_4d*100:.1f}%  err_vs_3d={err_3d*100:.1f}%  "
              f"{'PASS' if (err_4d < 0.10 and err_3d > 0.10) else 'FAIL'}")

    all_pass = all(passes_4d)
    verdict = "H_DIM_ROBUST_4D" if all_pass else "H_DIM_ANOMALY"

    print()
    print("=" * 80)
    print(f"VERDICT: {verdict}")
    print("=" * 80)
    if all_pass:
        print("  Substrate is dimension-robust at the linear (wave) level.")
        print("  c^2 = BETA_PHI/(z*mu_phi) scales correctly 3D (z=6) -> 4D (z=8).")
        print("  Next: 4D ring stability test (pending theoretical prereq).")
    else:
        print("  Dimension anomaly detected. Unexpected — investigate.")

    outdir = ROOT / "07_validation" / "audits" / "qng-gpu026-4d-kg-dispersion-v1"
    outdir.mkdir(parents=True, exist_ok=True)
    report = {
        'L': L,
        'K_VALUES': K_VALUES,
        'T_PHYS': T_PHYS,
        'DT': DT,
        'BETA_PHI': BETA_PHI,
        'MU_PHI': MU_PHI,
        'c2_pred_4d': c2_4d_pred,
        'c2_pred_3d': c2_3d_pred,
        'ratio_expected': 0.75,
        'per_k': results,
        'verdict': verdict,
    }
    with open(outdir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report: {outdir}/report.json")


if __name__ == "__main__":
    main()
