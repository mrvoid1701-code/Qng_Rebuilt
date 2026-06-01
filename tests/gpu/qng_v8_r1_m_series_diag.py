"""Post-hoc diagnostic on GPU-031f m_series.npz.

Extracts additional orbital structure that the main script's summary
does not capture:
  - Autocorrelation function (identifies all orbital timescales)
  - Amplitude modulation envelope (breather structure check)
  - Phase-space density (<M> vs |d<M>/dt|)
  - Distribution of M_ring values (unimodal vs bimodal)
  - Peak/trough statistics vs uniform distribution
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

NPZ = ROOT / "07_validation" / "audits" / "qng-v8-r1-long-time-v1" / "m_series.npz"
OUT_JSON = ROOT / "07_validation" / "audits" / "qng-v8-r1-long-time-v1" / "m_series_diag.json"


def find_peaks_troughs(x, min_separation=50):
    """Simple peak/trough finder: local extrema separated by min_separation."""
    peaks = []
    troughs = []
    n = len(x)
    for i in range(1, n - 1):
        if x[i] > x[i-1] and x[i] > x[i+1]:
            if not peaks or i - peaks[-1] >= min_separation:
                peaks.append(i)
            elif x[i] > x[peaks[-1]]:
                peaks[-1] = i
        elif x[i] < x[i-1] and x[i] < x[i+1]:
            if not troughs or i - troughs[-1] >= min_separation:
                troughs.append(i)
            elif x[i] < x[troughs[-1]]:
                troughs[-1] = i
    return np.array(peaks), np.array(troughs)


def main():
    data = np.load(NPZ)
    t = data['t_p2']
    m = data['m_p2']
    print(f"Loaded {len(m)} samples from {NPZ}")
    print(f"  t range: [{t[0]:.1f}, {t[-1]:.1f}]")
    print(f"  M range: [{m.min():.1f}, {m.max():.1f}]")
    print(f"  <M>_t  : {m.mean():.1f}")

    # --- 1. Autocorrelation ---
    m_centered = m - m.mean()
    n = len(m_centered)
    # Use FFT for efficiency
    f = np.fft.rfft(m_centered, n=2*n)
    acf_full = np.fft.irfft(f * np.conj(f))[:n].real
    acf = acf_full / acf_full[0]

    # Find first 3 positive peaks in ACF (orbital resonances)
    acf_peaks = []
    for i in range(10, min(1000, n)):
        if acf[i] > 0.1 and acf[i] > acf[i-1] and acf[i] > acf[i+1]:
            if not acf_peaks or i - acf_peaks[-1][0] >= 50:
                acf_peaks.append((i, acf[i]))
            if len(acf_peaks) >= 5:
                break

    print(f"\nACF peaks (lag_lu, acf):")
    for lag, a in acf_peaks:
        print(f"  lag={lag} lu, acf={a:.3f}")

    # --- 2. Histogram / distribution ---
    hist, edges = np.histogram(m, bins=40)
    centers = 0.5 * (edges[:-1] + edges[1:])
    # Check bimodality: compare hist[argmax] with a "valley"
    peak_idx = int(np.argmax(hist))
    # Largest-valley check
    left_valley = int(np.argmin(hist[:peak_idx])) if peak_idx > 0 else 0
    right_valley_rel = int(np.argmin(hist[peak_idx:]))
    right_valley = peak_idx + right_valley_rel
    bimodal_score = 0.0
    if right_valley < len(hist) - 1 and np.max(hist[right_valley:]) > hist[right_valley]:
        # There IS a second lobe
        second_peak_rel = int(np.argmax(hist[right_valley:]))
        second_peak = right_valley + second_peak_rel
        bimodal_score = float(hist[second_peak] / max(hist[peak_idx], 1))
        print(f"\nBimodality: primary peak at M={centers[peak_idx]:.0f} (n={hist[peak_idx]})")
        print(f"  valley at M={centers[right_valley]:.0f} (n={hist[right_valley]})")
        print(f"  secondary peak at M={centers[second_peak]:.0f} (n={hist[second_peak]})")
        print(f"  bimodal score = {bimodal_score:.3f}")

    # --- 3. Peak/trough statistics ---
    peaks_idx, troughs_idx = find_peaks_troughs(m, min_separation=80)
    print(f"\nPeaks: {len(peaks_idx)} found")
    print(f"Troughs: {len(troughs_idx)} found")
    if len(peaks_idx) >= 2:
        peak_periods = np.diff(t[peaks_idx])
        print(f"  Peak-to-peak periods: mean={peak_periods.mean():.1f}, "
              f"std={peak_periods.std():.1f}, "
              f"range=[{peak_periods.min():.1f}, {peak_periods.max():.1f}]")
        peak_heights = m[peaks_idx]
        print(f"  Peak heights: mean={peak_heights.mean():.1f}, "
              f"std={peak_heights.std():.1f}")

    if len(troughs_idx) >= 2:
        trough_periods = np.diff(t[troughs_idx])
        trough_depths = m[troughs_idx]
        print(f"  Trough-to-trough periods: mean={trough_periods.mean():.1f}")
        print(f"  Trough depths: mean={trough_depths.mean():.1f}, "
              f"std={trough_depths.std():.1f}")

    # --- 4. Amplitude envelope (Hilbert-transform-like) ---
    # Use rolling std as proxy
    window = 200
    if n > window:
        env = np.array([m[max(0, i-window//2):min(n, i+window//2)].std()
                        for i in range(n)])
        env_first = env[:n//2].mean()
        env_second = env[n//2:].mean()
        print(f"\nEnvelope (rolling std window {window}):")
        print(f"  first half mean std  = {env_first:.1f}")
        print(f"  second half mean std = {env_second:.1f}")
        print(f"  drift                = {(env_second-env_first)/env_first:.2%}")

    # --- 5. Scan of frequency spectrum beyond dominant ---
    freqs = np.fft.rfftfreq(n, d=float(t[1]-t[0]))
    power = np.abs(np.fft.rfft(m_centered))**2
    # Top 5 peaks
    top_indices = np.argsort(power[1:])[::-1][:5] + 1
    print("\nTop 5 spectral peaks:")
    tot_power = power[1:].sum()
    for idx in top_indices:
        period_lu = 1.0 / freqs[idx] if freqs[idx] > 0 else 0
        power_frac = power[idx] / tot_power
        print(f"  period={period_lu:.1f} lu, freq={freqs[idx]:.5f}, "
              f"power_frac={power_frac:.1%}")

    # --- Save summary ---
    summary = {
        'n_samples': int(n),
        'dt_lu': float(t[1] - t[0]),
        'mean_M': float(m.mean()),
        'std_M': float(m.std()),
        'M_min': float(m.min()),
        'M_max': float(m.max()),
        'acf_peaks_lag_lu': [int(p[0]) for p in acf_peaks],
        'acf_peaks_value': [float(p[1]) for p in acf_peaks],
        'bimodal_score': float(bimodal_score),
        'n_peaks': len(peaks_idx),
        'n_troughs': len(troughs_idx),
        'peak_period_mean_lu': (
            float(np.diff(t[peaks_idx]).mean()) if len(peaks_idx) >= 2 else None),
        'peak_period_std_lu': (
            float(np.diff(t[peaks_idx]).std()) if len(peaks_idx) >= 2 else None),
        'peak_height_mean': (
            float(m[peaks_idx].mean()) if len(peaks_idx) >= 1 else None),
        'trough_depth_mean': (
            float(m[troughs_idx].mean()) if len(troughs_idx) >= 1 else None),
        'envelope_drift': float((env_second-env_first)/env_first) if n > window else None,
        'top5_periods_lu': [
            float(1.0 / freqs[idx]) if freqs[idx] > 0 else 0
            for idx in top_indices],
        'top5_power_frac': [
            float(power[idx] / tot_power) for idx in top_indices],
    }
    with open(OUT_JSON, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary: {OUT_JSON}")


if __name__ == '__main__':
    main()
