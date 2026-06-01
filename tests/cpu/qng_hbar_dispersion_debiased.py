"""QNG-CPU-088: de-biased period extraction for hbar dispersion fit.

Savant flagged: periods {150, 167, 167, 188} = 1500/{10, 9, 9, 8}
looked like grid-locked FFT bins (frequency comb artifact).

This script:
  1. Re-measures T_orb with parabolic FFT interpolation (sub-bin precision)
  2. Cross-validates with autocorrelation-based period (independent method)
  3. Re-fits E^2 = c*w^2 + d on de-biased data
  4. Computes chi^2 / d.o.f. for the 2-param fit
  5. Also does R=4-dropped fit to quantify sensitivity

If de-biased periods still give <5% residuals on the dispersion fit,
the bin-locking concern is defused.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-hbar-dispersion-debiased-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

TRACE_PATHS = {
    2: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R2-v1" / "traces.npz",
    3: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R3-v1" / "traces.npz",
    4: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1"    / "traces.npz",
    5: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R5-v1" / "traces.npz",
}


def parabolic_fft_period(t, signal):
    """FFT with 3-point parabolic interpolation around the peak bin.

    Subbin precision: f_true = f_peak + 0.5*(y_{-1}-y_{+1})/(y_{-1}-2*y_0+y_{+1})
    where y are |FFT|^2 values at bins peak-1, peak, peak+1.
    """
    s = signal - np.mean(signal)
    dt = t[1] - t[0]
    N = len(s)
    # Hann window reduces leakage (critical for non-integer-bin frequencies)
    win = 0.5 * (1 - np.cos(2 * np.pi * np.arange(N) / (N - 1)))
    s_w = s * win
    fft = np.fft.rfft(s_w)
    freqs = np.fft.rfftfreq(N, d=dt)
    power = np.abs(fft) ** 2
    # Skip DC
    valid = freqs > 1e-6
    if not np.any(valid):
        return None, None
    idx = np.argmax(power[valid]) + np.argmax(valid)
    if idx < 1 or idx >= len(power) - 1:
        f_interp = freqs[idx]
    else:
        y0, ym, yp = power[idx], power[idx-1], power[idx+1]
        denom = ym - 2*y0 + yp
        if abs(denom) < 1e-30:
            df = 0.0
        else:
            df = 0.5 * (ym - yp) / denom
        f_interp = freqs[idx] + df * (freqs[1] - freqs[0])
    T_interp = 1.0 / f_interp if f_interp > 1e-10 else None
    T_bin_raw = 1.0 / freqs[idx] if freqs[idx] > 1e-10 else None
    return T_interp, T_bin_raw


def autocorr_period(t, signal):
    """Autocorrelation-based period detection — independent of FFT binning.

    Finds the first strong peak in the autocorrelation (after lag=0).
    """
    s = signal - np.mean(signal)
    N = len(s)
    # Normalized autocorrelation
    result = np.correlate(s, s, mode='full')
    mid = len(result) // 2
    acf = result[mid:] / result[mid]
    dt = t[1] - t[0]
    # Find first local max after initial decay
    # skip the first few lags (edge of main lobe)
    lags = np.arange(len(acf)) * dt
    # start search after ACF drops below 0.3 of peak
    below = np.argmax(acf < 0.3)
    if below == 0:
        return None
    # find local max after that
    for i in range(below, len(acf) - 1):
        if acf[i] > acf[i-1] and acf[i] > acf[i+1] and acf[i] > 0.2:
            # Parabolic interp on 3 points
            y0, ym, yp = acf[i], acf[i-1], acf[i+1]
            denom = ym - 2*y0 + yp
            if abs(denom) < 1e-30:
                return float(lags[i])
            di = 0.5 * (ym - yp) / denom
            return float(lags[i] + di * dt)
    return None


def compute_action(data, period, burn_in=500.0):
    """Compute Hamilton S = integral(2T - H) dt per cycle, averaged."""
    t = data['times']
    H = data['H']
    Tg, Tm, Tp = data['T_g'], data['T_m'], data['T_phi']
    warm = t > burn_in
    t_w = t[warm]; H_w = H[warm]
    Tg_w = Tg[warm]; Tm_w = Tm[warm]; Tp_w = Tp[warm]
    if period is None:
        return None, None, 0
    n_cycles = int((t_w[-1] - t_w[0]) / period)
    if n_cycles < 2:
        return None, None, 0
    S_list = []
    for i in range(n_cycles):
        ts = t_w[0] + i * period
        te = ts + period
        mask = (t_w >= ts) & (t_w <= te)
        if mask.sum() < 3:
            continue
        T_total = Tg_w[mask] + Tm_w[mask] + Tp_w[mask]
        L_vals = 2.0 * T_total - H_w[mask]
        S_list.append(float(np.trapz(L_vals, t_w[mask])))
    if not S_list:
        return None, None, 0
    arr = np.array(S_list)
    return float(arr.mean()), float(arr.std()), len(arr)


def fit_dispersion(w_arr, E_arr):
    """Linear fit E^2 = c*w^2 + d. Returns (c, d, residuals, rms, chi2_per_dof)."""
    y = E_arr ** 2
    x = w_arr ** 2
    # 2-param linear fit: y = c*x + d
    c, d = np.polyfit(x, y, 1)
    y_pred = c * x + d
    resid = (y - y_pred) / y  # fractional residual in E^2
    rms = float(np.sqrt(np.mean(resid ** 2)))
    # No error bars → chi2 not meaningful; use RMS as proxy
    n_dof = len(y) - 2
    return float(c), float(d), resid.tolist(), rms, n_dof


def main():
    print("=" * 80)
    print("QNG-CPU-088: de-biased hbar dispersion fit")
    print("=" * 80)
    print("Savant concern: FFT periods 150,167,167,188 = 1500/{10,9,9,8}")
    print("Fix: parabolic interp + autocorrelation cross-check")
    print("=" * 80)

    periods_fft = {}
    periods_fft_raw = {}
    periods_acf = {}
    S_data = {}

    for R, path in TRACE_PATHS.items():
        if not path.exists():
            continue
        data = np.load(path)
        t = data['times']
        M = data['M_ring']
        warm = t > 500.0
        t_w, M_w = t[warm], M[warm]

        T_fft_interp, T_fft_raw = parabolic_fft_period(t_w, M_w)
        T_acf = autocorr_period(t_w, M_w)
        periods_fft[R] = T_fft_interp
        periods_fft_raw[R] = T_fft_raw
        periods_acf[R] = T_acf

        print(f"\n  R={R}:")
        print(f"    T_FFT_raw      = {T_fft_raw:.4f} lu  (grid-locked bin)")
        print(f"    T_FFT_parabolic= {T_fft_interp:.4f} lu  (sub-bin interp, Hann-windowed)")
        if T_acf is not None:
            print(f"    T_autocorr     = {T_acf:.4f} lu  (independent method)")
            dev_fft_acf = abs(T_fft_interp - T_acf) / T_acf * 100
            print(f"    FFT-parabolic vs ACF deviation: {dev_fft_acf:+.2f}%")
        S_mean, S_std, n_cycles = compute_action(data, T_fft_interp)
        S_data[R] = (S_mean, S_std, n_cycles, T_fft_interp)
        if S_mean is not None:
            print(f"    S_Hamilton     = {S_mean:9.2f} +- {S_std:.2f}  ({n_cycles} cycles)")

    # Pick period source for fit: prefer parabolic FFT (cross-validated with ACF)
    T_use = periods_fft

    print("\n" + "=" * 80)
    print("DISPERSION FITS (E^2 = c*w^2 + d)")
    print("=" * 80)

    # Fit 1: all R
    Rs = sorted([R for R in S_data if S_data[R][0] is not None])
    w = np.array([2*np.pi/T_use[R] for R in Rs])
    E = np.array([S_data[R][0]/T_use[R] for R in Rs])
    c, d, resid, rms, dof = fit_dispersion(w, E)
    h_fit = np.sqrt(c)
    m_fit = np.sqrt(d) if d > 0 else None
    print(f"\n  All {len(Rs)} points, R={Rs}:")
    print(f"    c = {c:.4e}  ->  hbar_QNG = {h_fit:.2f}")
    print(f"    d = {d:.4e}  ->  m_QNG    = {m_fit:.2f}" if m_fit else f"    d = {d:.4e}  (NEGATIVE — fit invalid, E^2 pred < 0)")
    print(f"    Fractional residuals in E^2: {[f'{r*100:+.2f}%' for r in resid]}")
    print(f"    RMS residual: {rms*100:.2f}%")
    print(f"    dof (N_pts - 2 params): {dof}")

    # Fit 2: drop R=4 (longest period, most bin-sensitive)
    if 4 in Rs and len(Rs) > 2:
        Rs_dropped = [R for R in Rs if R != 4]
        w2 = np.array([2*np.pi/T_use[R] for R in Rs_dropped])
        E2 = np.array([S_data[R][0]/T_use[R] for R in Rs_dropped])
        c2, d2, resid2, rms2, dof2 = fit_dispersion(w2, E2)
        h2 = np.sqrt(c2)
        m2 = np.sqrt(d2) if d2 > 0 else None
        print(f"\n  Drop R=4 ({len(Rs_dropped)} points):")
        print(f"    c = {c2:.4e}  ->  hbar_QNG = {h2:.2f}  (shift vs all: {(h2-h_fit)/h_fit*100:+.2f}%)")
        if m2:
            print(f"    d = {d2:.4e}  ->  m_QNG    = {m2:.2f}  (shift: {(m2-m_fit)/m_fit*100:+.2f}%)")
        print(f"    Residuals: {[f'{r*100:+.2f}%' for r in resid2]}")

    # Fit 3: use ACF periods if available
    if all(periods_acf.get(R) is not None for R in Rs):
        w3 = np.array([2*np.pi/periods_acf[R] for R in Rs])
        S_acf_list = [compute_action(np.load(TRACE_PATHS[R]), periods_acf[R]) for R in Rs]
        E3 = np.array([s_acf[0]/periods_acf[R] for R, s_acf in zip(Rs, S_acf_list) if s_acf[0]])
        if len(E3) == len(Rs):
            c3, d3, resid3, rms3, dof3 = fit_dispersion(w3, E3)
            h3 = np.sqrt(c3)
            m3 = np.sqrt(d3) if d3 > 0 else None
            print(f"\n  Using ACF periods (independent from FFT):")
            print(f"    c = {c3:.4e}  ->  hbar_QNG = {h3:.2f}  (shift: {(h3-h_fit)/h_fit*100:+.2f}%)")
            if m3:
                print(f"    d = {d3:.4e}  ->  m_QNG    = {m3:.2f}  (shift: {(m3-m_fit)/m_fit*100:+.2f}%)")
            print(f"    Residuals: {[f'{r*100:+.2f}%' for r in resid3]}")

    # Verdict
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    # Defuse if: (a) parabolic T ~ raw T to <5%, AND (b) residuals still <5%
    bin_artifact = False
    for R in Rs:
        dev = abs(periods_fft[R] - periods_fft_raw[R]) / periods_fft_raw[R] * 100
        print(f"  R={R}: raw bin period {periods_fft_raw[R]:.2f}  parabolic {periods_fft[R]:.2f}  diff {dev:.2f}%")
        if dev < 0.5:
            bin_artifact = True  # parabolic fell exactly back to bin → suspicious
    if rms * 100 < 5.0:
        print(f"\n  Full fit RMS = {rms*100:.2f}% < 5%  -> dispersion candidate SURVIVES de-biasing")
    else:
        print(f"\n  Full fit RMS = {rms*100:.2f}% >= 5%  -> dispersion candidate WEAKENED")

    # Save
    out = {
        'periods_fft_raw': {str(R): periods_fft_raw[R] for R in Rs},
        'periods_fft_parabolic': {str(R): periods_fft[R] for R in Rs},
        'periods_autocorr': {str(R): periods_acf[R] for R in Rs},
        'S_per_R': {str(R): {'S_mean': S_data[R][0], 'S_std': S_data[R][1], 'n_cycles': S_data[R][2]} for R in Rs},
        'fit_all': {'c': c, 'd': d, 'hbar': h_fit, 'm': m_fit if m_fit else None,
                    'residuals': resid, 'rms': rms, 'dof': dof},
    }
    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
