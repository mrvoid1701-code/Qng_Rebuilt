"""QNG-CPU-085: mode decomposition of R=4 orbital attractor.

CPU-083/084 found J spread 41% across R, with R=4 a clear action minimum
(J=7460, 0.58% per-cycle stability). The 0.02% S-stability of R=4 is
exceptional.

This script asks: does R=4 have ONE clean periodic mode, or several?
If multiple modes exist, each may carry its own action quantum, giving
a discrete action SPECTRUM rather than a single h.

Analysis:
  Load R=4 trace.
  Compute FFT of every dynamical observable: M_ring, COM_x, COM_y, COM_z,
    r_eff, T_m, T_phi, T_g, V_couple, H, Lz_phi, phi_winding.
  Identify the top 3 spectral peaks per channel.
  Cross-correlate: are the peak frequencies commensurate (rational
    ratios) or incommensurate?
  Quasi-periodic motion would show a few base frequencies plus harmonics.
  If only ONE base frequency is found across all channels, the orbit is
    truly 1D-periodic and J is the unique action.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1" / "traces.npz"
AUDIT_DIR  = ROOT / "07_validation" / "audits" / "qng-R4-mode-decomp-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def find_top_peaks(t, signal, n_peaks=5, burn_in_lu=500.0):
    warm = t > burn_in_lu
    t_w = t[warm]
    s_w = signal[warm] - np.mean(signal[warm])
    if np.std(s_w) < 1e-12:
        return [], 0.0  # constant signal
    dt = t_w[1] - t_w[0]
    fft = np.fft.rfft(s_w)
    freqs = np.fft.rfftfreq(len(s_w), d=dt)
    power = np.abs(fft) ** 2
    total_power = power.sum()

    # Find local maxima (peak detection)
    peaks = []
    for i in range(1, len(power) - 1):
        if power[i] > power[i-1] and power[i] > power[i+1] and freqs[i] > 1e-6:
            peaks.append((freqs[i], power[i] / total_power))
    peaks.sort(key=lambda x: -x[1])
    return peaks[:n_peaks], float(np.std(s_w))


def main():
    print("=" * 80)
    print("QNG-CPU-085: R=4 orbital attractor mode decomposition")
    print("=" * 80)

    data = np.load(TRACE_PATH)
    t = data['times']
    print(f"  Loaded {TRACE_PATH.name}: N={len(t)}, t in [{t[0]:.0f}, {t[-1]:.0f}]")

    channels = {
        'M_ring':    data['M_ring'],
        'COM_x':     data['com_x'],
        'COM_y':     data['com_y'],
        'COM_z':     data['com_z'],
        'r_eff':     data['r_eff'],
        'T_g':       data['T_g'],
        'T_m':       data['T_m'],
        'T_phi':     data['T_phi'],
        'V_couple':  data['V_couple'],
        'H':         data['H'],
        'Lz_phi':    data['Lz_phi'],
        'phi_wind':  data['phi_winding'],
    }

    all_peaks = {}
    print("\n" + "-" * 80)
    print(f"{'channel':10s} {'std':>10s}  {'peak1_T':>10s} {'peak2_T':>10s} {'peak3_T':>10s} ")
    print("-" * 80)
    for name, sig in channels.items():
        peaks, std = find_top_peaks(t, sig, n_peaks=5)
        all_peaks[name] = {'std': float(std), 'peaks': [
            {'freq': float(f), 'period_lu': float(1/f), 'power_frac': float(p)}
            for f, p in peaks
        ]}
        if not peaks:
            print(f"  {name:10s} {std:10.3e}  (constant or empty)")
            continue
        T1 = 1/peaks[0][0] if peaks else float('nan')
        T2 = 1/peaks[1][0] if len(peaks) > 1 else float('nan')
        T3 = 1/peaks[2][0] if len(peaks) > 2 else float('nan')
        print(f"  {name:10s} {std:10.3e}  {T1:10.2f} {T2:10.2f} {T3:10.2f}")

    # Cross-channel: extract the unique fundamental periods
    fundamental_freqs = []
    for name, info in all_peaks.items():
        if not info['peaks']:
            continue
        f0 = info['peaks'][0]['freq']
        # Cluster: collapse if within 5% of any existing fundamental
        is_new = True
        for f_existing in fundamental_freqs:
            if abs(f0 - f_existing) / f_existing < 0.05:
                is_new = False
                break
        if is_new:
            fundamental_freqs.append(f0)

    fundamental_freqs.sort()
    print("\n" + "=" * 80)
    print(f"DETECTED FUNDAMENTAL FREQUENCIES: {len(fundamental_freqs)}")
    print("=" * 80)
    for i, f in enumerate(fundamental_freqs):
        print(f"  Mode {i+1}: f = {f:.5f}, T = {1/f:.2f} lu")

    # Pairwise frequency ratios — rational ratios indicate commensurate
    if len(fundamental_freqs) >= 2:
        print("\n  Pairwise ratios (look for simple rationals — commensurate):")
        for i in range(len(fundamental_freqs)):
            for j in range(i+1, len(fundamental_freqs)):
                ratio = fundamental_freqs[j] / fundamental_freqs[i]
                # Try to find nearest rational p/q with q <= 10
                best_p, best_q, best_err = 1, 1, float('inf')
                for q in range(1, 11):
                    for p in range(1, 21):
                        err = abs(ratio - p/q)
                        if err < best_err:
                            best_err = err
                            best_p, best_q = p, q
                quality = "RATIONAL" if best_err < 0.01 else "incommensurate"
                print(f"    f{j+1}/f{i+1} = {ratio:.4f}  ~ {best_p}/{best_q} = {best_p/best_q:.4f} (err {best_err:.4f})  {quality}")

    # Verdict
    if len(fundamental_freqs) == 1:
        verdict = "MONO_PERIODIC"
        msg = "single fundamental — orbit is truly 1-tori, J unique"
    elif len(fundamental_freqs) == 2:
        verdict = "QUASI_PERIODIC_2D"
        msg = "two fundamentals — motion on 2-torus; expect TWO action invariants J_1, J_2"
    else:
        verdict = f"MULTIMODAL_{len(fundamental_freqs)}"
        msg = f"{len(fundamental_freqs)} fundamentals — high-dim attractor; many action invariants"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {msg}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'trace_source': str(TRACE_PATH),
            'channels': all_peaks,
            'fundamental_freqs': [float(f) for f in fundamental_freqs],
            'fundamental_periods_lu': [float(1/f) for f in fundamental_freqs],
            'n_fundamentals': len(fundamental_freqs),
            'verdict': verdict, 'comment': msg,
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
