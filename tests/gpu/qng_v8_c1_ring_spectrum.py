"""Einstein C1: quick phi spectrum peek in cached R=4 ring.

Idea: if matter = phi bound states in sigma_m wells (Jackiw-Rebbi),
the cached ring (R=4, L=28) should host discrete phi modes whose
frequencies generate a baryon mass ladder. This probe seeds a small
noise perturbation on phi inside the cached ring, freezes sigma_m,
evolves T=1000 lu, samples phi at a handful of ring-core points,
and FFTs each time series to identify the first 3 spectral peaks.

This is NOT the full GPU-037 (which would map the entire bound-state
spectrum); it is a fast peek to see whether discrete peaks appear
or phi radiates into a continuum.

Protocol:
  Ring: load R=4 L=28 cached (form if miss) — deterministic.
  Perturb: phi += eps * randn(N), eps=0.02  (seed broad k-band).
  Freeze sm to cached profile and pi_m=0 every Yoshida4 step.
  Evolve T=1000 lu at DT=0.025.
  Sample: phi at 4 core points (on torus tube, azimuthally spaced)
          and 1 reference point at ring center (geometric center).
  FFT each trace after removing mean; find top 3 peaks per channel.

Expected m_rest at ring core: sigma_m_core ~ 0.27 (from CPU-073),
  deficit ~ 0.23, m^2 = (g/(2*mu_phi))*deficit^2 ~ 0.00679, T ~ 76 lu.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "gpu"))

from qng_v8_canonical_gpu import (
    yoshida4_step, hamiltonian_v8, DT,
    SIGMA_M_REF, CHI_DECAY_V7, G_V_COUPLE, MU_PHI, BETA_PHI,
)
from qng_v8_ring_cache import form_ring_cached

EXACT_A_MODE = 'r1'


def ring_core_points(L, R):
    """Azimuthally spaced points on the toroidal core (z=L/2, r=R from center)."""
    cx = cy = cz = (L - 1) / 2.0
    pts = []
    for phi in np.linspace(0.0, 2.0 * np.pi, 4, endpoint=False):
        x = int(round(cx + R * np.cos(phi)))
        y = int(round(cy + R * np.sin(phi)))
        z = int(round(cz))
        pts.append((x, y, z))
    pts.append((int(cx), int(cy), int(cz)))  # geometric center
    return pts


def flat_idx(pt, L):
    x, y, z = pt
    return x * L * L + y * L + z


def find_peaks(freqs, power, n_peaks=3):
    """Find up to n_peaks local maxima in power, excluding DC bin."""
    peaks = []
    for i in range(1, len(power) - 1):
        if power[i] > power[i - 1] and power[i] >= power[i + 1]:
            peaks.append((i, freqs[i], power[i]))
    peaks.sort(key=lambda p: -p[2])
    return peaks[:n_peaks]


def main():
    L = 28
    R = 4
    T_P1 = 300.0
    T_P2 = 1000.0
    T_run = 1000.0
    eps_perturb = 0.02
    sample_every_lu = 1.0

    print("=" * 80)
    print("Einstein C1: cached ring R=4 phi spectrum peek")
    print("=" * 80)
    print(f"  L={L}, R={R}, P1={T_P1}, P2={T_P2}")
    print(f"  Perturb phi += {eps_perturb}*randn(N), freeze sigma_m")
    print(f"  T_run={T_run} lu, DT={DT}, sample every {sample_every_lu} lu")

    t_load = time.time()
    state, nb_idx = form_ring_cached(L=L, R=R, T_P1=T_P1, T_P2=T_P2, DT=DT)
    print(f"  Ring loaded/formed in {time.time() - t_load:.1f}s")

    sm_frozen = state['sm'].copy()
    sm_min = float(cp.min(sm_frozen))
    sm_max = float(cp.max(sm_frozen))
    defi_max = SIGMA_M_REF - sm_min
    m2_core = (G_V_COUPLE / (2.0 * MU_PHI)) * defi_max * defi_max
    T_core = 2.0 * np.pi / np.sqrt(m2_core) if m2_core > 0 else float('inf')
    print(f"  sigma_m cached: min={sm_min:.4f} (ring core), "
          f"max={sm_max:.4f}")
    print(f"  m^2_core = {m2_core:.5f},  T_core predicted = {T_core:.2f} lu")

    # Add gaussian noise to phi
    cp.random.seed(7)
    N = L * L * L
    state['phi'] = state['phi'] + eps_perturb * cp.random.randn(N,
                                                                 dtype=cp.float64)
    state['pi_phi'].fill(0.0)
    state['pi_m'].fill(0.0)

    # Ring-core sample points
    points = ring_core_points(L, R)
    idxs = [flat_idx(p, L) for p in points]
    labels = [f"theta={i*90}deg" for i in range(4)] + ["center"]
    print(f"  Sample points: {points}")

    H0 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)

    n_steps = int(T_run / DT)
    sample_every = max(1, int(sample_every_lu / DT))
    times = [0.0]
    phi_traces = [[float(state['phi'][i].get())] for i in idxs]

    t0 = time.time()
    for s in range(1, n_steps + 1):
        state = yoshida4_step(state, DT, nb_idx, v_couple_on=True,
                              chi_decay=CHI_DECAY_V7,
                              exact_a=EXACT_A_MODE)
        # freeze sigma_m (and pi_m)
        state['sm'] = sm_frozen.copy()
        state['pi_m'].fill(0.0)
        if s % sample_every == 0:
            t_phys = s * DT
            times.append(t_phys)
            phi_vec = cp.asnumpy(state['phi'])
            for k, i in enumerate(idxs):
                phi_traces[k].append(float(phi_vec[i]))
        if s % (n_steps // 10) == 0:
            frac = s / n_steps
            elapsed = time.time() - t0
            eta = elapsed * (1 - frac) / max(frac, 1e-3)
            print(f"    {frac*100:.0f}% done  elapsed={elapsed:.0f}s  "
                  f"eta={eta:.0f}s")

    wall = time.time() - t0
    H1 = hamiltonian_v8(state, nb_idx, channel_f=True, k_gm=0.0,
                        exact_a=EXACT_A_MODE)
    H_drift = abs(H1 - H0) / abs(H0) if abs(H0) > 1e-10 else 0.0
    print(f"  Evolution: {wall:.1f}s, H drift = {H_drift:.2e}")

    # FFT each trace, find top 3 peaks
    t_arr = np.array(times)
    dt_s = t_arr[1] - t_arr[0]
    all_peaks = {}
    for k, lbl in enumerate(labels):
        vals = np.array(phi_traces[k])
        ac = vals - np.mean(vals)
        fft = np.fft.rfft(ac)
        freqs_hz = np.fft.rfftfreq(len(vals), d=dt_s)
        omega = 2.0 * np.pi * freqs_hz
        power = np.abs(fft) ** 2
        peaks = find_peaks(omega, power, n_peaks=3)
        all_peaks[lbl] = [{
            'omega': float(p[1]),
            'T_lu': float(2 * np.pi / p[1]) if p[1] > 0 else None,
            'power_norm': float(p[2] / max(power[1:].sum(), 1e-30)),
        } for p in peaks]

    print("\n" + "=" * 80)
    print("SPECTRAL PEAKS (omega, T_lu, relative power)")
    print("=" * 80)
    for lbl in labels:
        print(f"  {lbl}:")
        for p in all_peaks[lbl]:
            T = p['T_lu']
            t_str = f"{T:.2f}" if T is not None else "--"
            print(f"    omega={p['omega']:.5f}  T={t_str} lu  "
                  f"power={p['power_norm']:.3f}")

    # Cross-check: median top peak across ring points (exclude center for now)
    ring_peak_freqs = [all_peaks[lbl][0]['omega']
                       for lbl in labels[:4]
                       if all_peaks[lbl]]
    if ring_peak_freqs:
        omega_ring = float(np.median(ring_peak_freqs))
        T_ring = 2 * np.pi / omega_ring if omega_ring > 0 else None
        t_str = f"{T_ring:.2f}" if T_ring else "--"
        print(f"\n  Ring top-peak median:  omega={omega_ring:.5f}  T={t_str} lu")
        ratio_to_pred = omega_ring / np.sqrt(m2_core)
        print(f"  vs core omega_KG=sqrt(m^2_core)={np.sqrt(m2_core):.5f}"
              f"  ratio={ratio_to_pred:.3f}")

    if all_peaks[labels[0]]:
        top = all_peaks[labels[0]][0]
        if 0.80 < top['omega'] / np.sqrt(m2_core) < 1.20:
            verdict = "C1_CORE_MODE_FOUND"
        else:
            verdict = "C1_CORE_MODE_MISSED"
    else:
        verdict = "C1_NO_PEAKS"
    print(f"\n  VERDICT: {verdict}")

    # Persist
    audit = ROOT / "07_validation" / "audits" / "qng-v8-c1-ring-spectrum-v1"
    audit.mkdir(parents=True, exist_ok=True)
    with open(audit / "report.json", "w") as f:
        json.dump({
            'L': L, 'R': R, 'T_P1': T_P1, 'T_P2': T_P2,
            'T_run': T_run, 'eps_perturb': eps_perturb,
            'g': G_V_COUPLE, 'mu_phi': MU_PHI, 'beta_phi': BETA_PHI,
            'sigma_m_ref': SIGMA_M_REF,
            'sm_min': sm_min, 'sm_max': sm_max,
            'deficit_max': defi_max, 'm2_core_pred': m2_core,
            'T_core_pred_lu': T_core if not np.isinf(T_core) else None,
            'sample_points': points, 'sample_labels': labels,
            'peaks': all_peaks,
            'ring_median_top_omega': (float(np.median(ring_peak_freqs))
                                       if ring_peak_freqs else None),
            'H_drift_frac': H_drift,
            'wall_s': wall,
            'verdict': verdict,
        }, f, indent=2)

    np.savez(audit / "phi_traces.npz",
             times=np.array(times),
             **{labels[k]: np.array(phi_traces[k]) for k in range(len(labels))})

    print(f"  Report: {audit / 'report.json'}")


if __name__ == "__main__":
    main()
