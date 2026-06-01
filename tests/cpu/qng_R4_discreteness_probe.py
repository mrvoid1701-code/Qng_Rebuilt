"""QNG-CPU-086: discreteness probe of R=4 orbital attractor.

If the orbital attractor exchanges energy with the substrate in discrete
quanta, then the time series of an extensive observable (M_ring, H, COM_z)
should show a STAIRCASE structure with quantized levels rather than smooth
continuous variation.

Tests:
  (1) Histogram of M_ring(t) — look for multimodal peaks
  (2) Histogram of H(t) — look for discrete plateaus
  (3) First-difference distribution: dM_ring/dt and dH/dt should peak at
      DISCRETE values if there are quantum jumps
  (4) Wavelet-like discreteness measure: variance of M_ring conditional
      on coarse-grained time bins

If discreteness is found: the smallest level spacing in M_ring = candidate
M-quantum; in H = candidate energy quantum (ℏω).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1" / "traces.npz"
AUDIT_DIR  = ROOT / "07_validation" / "audits" / "qng-R4-discreteness-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def find_discreteness(values, n_bins=50):
    """Histogram peak detection — count distinct level peaks."""
    hist, edges = np.histogram(values, bins=n_bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    peaks = []
    for i in range(1, len(hist) - 1):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 0.05 * hist.max():
            peaks.append((centers[i], int(hist[i])))
    return peaks, hist, centers


def staircase_quality(diffs, level_threshold_frac=0.1):
    """Are the first-differences clustered in discrete levels?"""
    diffs_sorted = np.sort(diffs)
    n = len(diffs_sorted)
    if n < 10:
        return None, None
    # Histogram of diffs
    hist, edges = np.histogram(diffs, bins=30)
    centers = 0.5 * (edges[:-1] + edges[1:])
    # Peak of diff distribution
    peak_diff = centers[np.argmax(hist)]
    # Gaussianity check: kurtosis vs std
    mu = np.mean(diffs)
    std = np.std(diffs)
    kurt = np.mean((diffs - mu) ** 4) / std ** 4 if std > 0 else 0
    return float(peak_diff), float(kurt - 3)  # excess kurtosis


def main():
    print("=" * 80)
    print("QNG-CPU-086: discreteness probe of R=4 orbital")
    print("=" * 80)

    data = np.load(TRACE_PATH)
    t = data['times']
    burn_in = 500.0
    warm = t > burn_in
    t_w = t[warm]
    print(f"  Loaded {TRACE_PATH.name}: warm samples N={int(warm.sum())}, t in [{burn_in}, {t[-1]:.0f}]")

    channels_to_test = {
        'M_ring':   data['M_ring'][warm],
        'H':        data['H'][warm],
        'COM_z':    data['com_z'][warm],
        'r_eff':    data['r_eff'][warm],
        'T_m':      data['T_m'][warm],
        'T_phi':    data['T_phi'][warm],
        'V_couple': data['V_couple'][warm],
    }

    results = {}
    print("\n" + "-" * 90)
    print(f"{'channel':10s} {'mean':>12s} {'std':>12s} {'#peaks':>6s} {'level_sp':>12s} {'kurt_excess':>12s}")
    print("-" * 90)
    for name, vals in channels_to_test.items():
        peaks, hist, centers = find_discreteness(vals, n_bins=30)
        diffs = np.diff(vals)
        peak_diff, kurt_x = staircase_quality(diffs)
        n_peaks = len(peaks)
        if n_peaks >= 2:
            spacings = np.diff([p[0] for p in peaks])
            mean_sp = np.mean(spacings)
        else:
            mean_sp = 0.0
        results[name] = {
            'mean': float(vals.mean()),
            'std':  float(vals.std()),
            'n_hist_peaks': n_peaks,
            'mean_level_spacing': float(mean_sp),
            'peak_centers': [float(p[0]) for p in peaks],
            'peak_counts':  [int(p[1])    for p in peaks],
            'diff_typical': float(peak_diff) if peak_diff is not None else 0.0,
            'kurt_excess': float(kurt_x) if kurt_x is not None else 0.0,
        }
        print(f"  {name:10s} {vals.mean():12.4f} {vals.std():12.4f} "
              f"{n_peaks:6d} {mean_sp:12.4f} {kurt_x:12.4f}")

    # Search for the H-quantum: smallest detectable energy step
    print("\n" + "=" * 80)
    print("ENERGY QUANTUM SEARCH (H channel)")
    print("=" * 80)
    H = channels_to_test['H']
    H_diffs = np.diff(H)
    print(f"  H_mean = {H.mean():.4f}")
    print(f"  H_std  = {H.std():.4f}")
    print(f"  |dH| min   = {np.abs(H_diffs).min():.6e}")
    print(f"  |dH| max   = {np.abs(H_diffs).max():.6e}")
    print(f"  |dH| median = {np.median(np.abs(H_diffs)):.6e}")
    # dH levels via histogram of dH
    h_hist, h_edges = np.histogram(H_diffs, bins=50)
    h_centers = 0.5 * (h_edges[:-1] + h_edges[1:])
    # Find peaks symmetric about zero
    print(f"\n  dH distribution (top 5 bins):")
    sorted_idx = np.argsort(h_hist)[::-1][:5]
    for i in sorted_idx:
        print(f"    dH = {h_centers[i]:+.4e}  count={h_hist[i]}")

    # Verdict
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    # If any channel has >= 3 distinct hist peaks AND uniform spacing, claim discreteness
    discreet_channels = []
    for name, r in results.items():
        if r['n_hist_peaks'] >= 3:
            spacings = np.diff(r['peak_centers'])
            if len(spacings) > 0 and np.std(spacings) / max(np.mean(spacings), 1e-10) < 0.30:
                discreet_channels.append((name, np.mean(spacings)))

    if discreet_channels:
        verdict = "DISCRETENESS_FOUND"
        print(f"  Channels with discrete level structure:")
        for ch, sp in discreet_channels:
            print(f"    {ch}: level spacing = {sp:.4f}")
        if any(ch == 'H' for ch, _ in discreet_channels):
            h_quantum = next(sp for ch, sp in discreet_channels if ch == 'H')
            T_orb = 187.50
            print(f"\n  Energy quantum candidate: dH = {h_quantum:.4f} per ~{T_orb} lu period")
            print(f"  ℏω candidate = dH = {h_quantum:.4f}")
            print(f"  ℏ candidate (ω = 2pi/T) = dH * T/(2pi) = {h_quantum * T_orb / (2*np.pi):.4f} lu")
    else:
        verdict = "CONTINUOUS"
        print(f"  No channel shows discrete level structure with uniform spacing.")
        print(f"  The orbital attractor exchanges energy CONTINUOUSLY (classical regime).")
        print(f"  This is consistent with v8 being in semi-classical or fully classical regime.")

    print(f"\n  VERDICT: {verdict}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'trace_source': str(TRACE_PATH),
            'channels': results,
            'verdict': verdict,
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
