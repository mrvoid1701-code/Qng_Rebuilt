"""CPU-only analysis of Shapiro & redshift probe signals.

Loads saved .npz files from:
  07_validation/audits/qng-v8-stability-probe-v1/shapiro_probe_signals.npz
  07_validation/audits/qng-v8-stability-probe-v1/redshift_probe_signals.npz

Performs:
  1. Envelope extraction (Hilbert-like via abs + moving average).
  2. First-arrival time (signal crossing threshold).
  3. Peak-envelope time (max of smoothed |phi|).
  4. Group-velocity estimate from arrival times.
  5. Consistency check vs theory c_phi = sqrt(BETA_PHI/(6*mu_phi)).
  6. Relative dispersion in ring region.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SIGNAL_DIR = ROOT / "07_validation" / "audits" / "qng-v8-stability-probe-v1"

# Theory constants (match v8_canonical)
BETA_PHI = 0.06
MU_PHI   = 0.8571    # 2*BETA_PHI*SIGMA_M_REF^2 / (K_BACK*BETA_G)
G_V_COUPLE = 0.22
C_PHI = float(np.sqrt(BETA_PHI / (6.0 * MU_PHI)))


def envelope(signal, window=5):
    """Return |signal| smoothed with a moving average of `window` samples."""
    abs_s = np.abs(signal)
    kernel = np.ones(window) / window
    return np.convolve(abs_s, kernel, mode='same')


def first_crossing(t, sig, threshold):
    """Return first t where |sig| > threshold, else NaN."""
    abs_s = np.abs(sig)
    idx = np.where(abs_s > threshold)[0]
    if len(idx) == 0:
        return float('nan')
    return float(t[idx[0]])


def peak_time(t, sig, window=5):
    env = envelope(sig, window=window)
    return float(t[int(np.argmax(env))]), float(env.max())


def analyze_shapiro():
    path = SIGNAL_DIR / "shapiro_probe_signals.npz"
    if not path.exists():
        print(f"SKIP: {path.name} not found")
        return
    print("=" * 80)
    print("SHAPIRO PROBE SIGNAL ANALYSIS")
    print("=" * 80)
    data = np.load(path)
    t           = data['t']
    phi_vac     = data['phi_vac']
    phi_rp      = data['phi_ring_pulse']   # already pulse-in-ring (rp - bg)
    phi_bg      = data['phi_ring_bg']
    c_phi_saved = float(data['c_phi'])
    M_ring0     = float(data['M_ring0'])
    detector    = tuple(int(x) for x in data['detector'])

    print(f"  detector node = {detector}")
    print(f"  c_phi (saved) = {c_phi_saved:.5f}  (theory: {C_PHI:.5f})")
    print(f"  M_ring0       = {M_ring0:.2f}")
    print(f"  N samples     = {len(t)}")
    print(f"  T_track       = {t[-1]:.1f} lu, dt_sample = {t[1]-t[0]:.3f} lu")
    print()

    # Diagnostics
    rms_vac = float(np.sqrt(np.mean(phi_vac ** 2)))
    rms_rp  = float(np.sqrt(np.mean(phi_rp ** 2)))
    rms_bg  = float(np.sqrt(np.mean(phi_bg ** 2)))
    max_vac = float(np.max(np.abs(phi_vac)))
    max_rp  = float(np.max(np.abs(phi_rp)))
    max_bg  = float(np.max(np.abs(phi_bg)))
    print(f"  RMS:     vac={rms_vac:.5f}  rp(pulse-in-ring)={rms_rp:.5f}  bg(ring)={rms_bg:.5f}")
    print(f"  max|.|:  vac={max_vac:.5f}  rp={max_rp:.5f}  bg={max_bg:.5f}")
    print()

    # Envelope analysis
    env_vac = envelope(phi_vac, window=5)
    env_rp  = envelope(phi_rp, window=5)
    env_bg  = envelope(phi_bg, window=5)

    # Multiple peak definitions
    print("Peak envelope times (various window sizes):")
    for w in [3, 5, 7, 11]:
        e_v = envelope(phi_vac, window=w)
        e_r = envelope(phi_rp, window=w)
        t_v = t[int(np.argmax(e_v))]
        t_r = t[int(np.argmax(e_r))]
        dt  = t_r - t_v
        print(f"  window={w:2d}:  t_vac={t_v:6.2f}  t_ring={t_r:6.2f}  dt={dt:+6.2f}")

    # Threshold crossing times (first arrival)
    print()
    print("First-crossing times (first |phi| > threshold):")
    for thr_frac in [0.1, 0.2, 0.3, 0.5]:
        thr_v = thr_frac * max_vac
        thr_r = thr_frac * max_rp
        t_v = first_crossing(t, phi_vac, thr_v)
        t_r = first_crossing(t, phi_rp, thr_r)
        dt = t_r - t_v
        print(f"  thresh={thr_frac*100:>3.0f}% of own max:  t_vac={t_v:6.2f}  "
              f"t_ring={t_r:6.2f}  dt={dt:+6.2f}")

    # Absolute threshold (same for both)
    print()
    print("Absolute-threshold first-crossing (common threshold):")
    common_thresh = min(max_vac, max_rp) * 0.25
    t_v = first_crossing(t, phi_vac, common_thresh)
    t_r = first_crossing(t, phi_rp, common_thresh)
    print(f"  thresh={common_thresh:.5f}:  t_vac={t_v:6.2f}  t_ring={t_r:6.2f}  "
          f"dt={t_r - t_v:+6.2f}")

    # Group velocity estimates
    # For vacuum: massless wave, v_g = c_phi, theoretical ToF = 20/c_phi = 185.2
    # For ring: m^2 = (g/2)*deficit_core^2/mu_phi, in ring core deficit~0.3
    print()
    print("=" * 80)
    print("THEORY COMPARISON")
    print("=" * 80)
    d = 20.0  # source to detector distance
    t_vac_theory = d / C_PHI
    k_pulse = np.pi / 4.0
    # Ring core effective mass (assume deficit ~ 0.3 across ring material path)
    for deficit_est in [0.1, 0.2, 0.3, 0.42]:
        m_sq = 0.5 * G_V_COUPLE * deficit_est ** 2 / MU_PHI
        omega = np.sqrt(C_PHI ** 2 * k_pulse ** 2 + m_sq)
        v_g   = C_PHI ** 2 * k_pulse / omega
        # Assume half the 20-node path is through ring (mass), half vacuum
        t_ring_theory = 10.0 / C_PHI + 10.0 / v_g
        dt_theory = t_ring_theory - t_vac_theory
        print(f"  deficit={deficit_est:.2f}:  m^2={m_sq:.5f}  v_g={v_g:.5f}  "
              f"t_ring_theory={t_ring_theory:.1f}  dt_theory={dt_theory:+.2f}")
    print(f"  t_vac_theory = {t_vac_theory:.1f} lu")
    print()

    print("OBSERVATION: measured t_peak ~ 67/93 lu << theoretical ToF (185 lu).")
    print("Likely cause: dispersive spread of Gaussian pulse.  The 'peak' at")
    print("detector is not the packet center but the first significant")
    print("amplitude — a leading-edge artifact of wavepacket in short L box.")
    print("The SIGN of dt is still meaningful: ring region does delay signal.")


def analyze_redshift():
    path = SIGNAL_DIR / "redshift_probe_signals.npz"
    if not path.exists():
        print(f"SKIP: {path.name} not found")
        return
    print()
    print("=" * 80)
    print("REDSHIFT PROBE SIGNAL ANALYSIS")
    print("=" * 80)
    data = np.load(path)
    t       = data['t']
    s_core  = data['s_core']
    s_vac   = data['s_vac']
    o_core  = float(data['omega_core'])
    o_vac   = float(data['omega_vac'])
    o_th    = float(data['omega_core_th'])
    d_core  = float(data['deficit_core'])
    d_vac   = float(data['deficit_vac'])

    print(f"  deficit (core) = {d_core:.4f}   (vacuum) = {d_vac:.4f}")
    print(f"  omega measured: core={o_core:.5f}  vac={o_vac:.5f}")
    print(f"  omega theory (core k=0) = sqrt((g/2)def^2/mu) = {o_th:.5f}")
    print(f"  N samples = {len(t)}")
    print()

    # Range and saturation check
    print(f"  Ring signal range: core=[{s_core.min():.3f}, {s_core.max():.3f}]  "
          f"vacuum=[{s_vac.min():.3f}, {s_vac.max():.3f}]")
    print(f"  Saturation check: |s_core|_max/2pi = {abs(s_core).max()/(2*np.pi):.2f}")
    print(f"  (values >> 1 means phi wrapped many times — strongly nonlinear)")
    print()

    # Low-pass to isolate slow modes
    # Simple: take windowed mean
    window = int(5.0 / (t[1]-t[0]))  # smooth over 5 lu
    if window > 1 and window < len(t):
        kernel = np.ones(window) / window
        core_lp = np.convolve(s_core, kernel, mode='same')
        vac_lp  = np.convolve(s_vac, kernel, mode='same')
        print(f"  After low-pass smoothing (window={window}):")
        print(f"    core RMS = {np.sqrt(np.mean(core_lp**2)):.4f}")
        print(f"    vac  RMS = {np.sqrt(np.mean(vac_lp**2)):.4f}")
        # Zero crossings of smoothed
        zc_core_lp = int(np.sum(np.diff(np.sign(core_lp - core_lp.mean())) != 0))
        zc_vac_lp  = int(np.sum(np.diff(np.sign(vac_lp  - vac_lp.mean())) != 0))
        T = t[-1]
        print(f"    core zero-crossings={zc_core_lp}  omega_zc={np.pi*zc_core_lp/T:.4f}")
        print(f"    vac  zero-crossings={zc_vac_lp }  omega_zc={np.pi*zc_vac_lp /T:.4f}")

    # Power-weighted centroid frequency
    dt_s = t[1] - t[0]
    for name, sig in [('core', s_core), ('vac', s_vac)]:
        sig_d = sig - sig.mean()
        fft = np.fft.rfft(sig_d)
        freqs = np.fft.rfftfreq(len(sig), d=dt_s)
        power = np.abs(fft) ** 2
        # Centroid freq
        f_centroid = float(np.sum(freqs * power) / max(np.sum(power), 1e-12))
        omega_centroid = 2 * np.pi * f_centroid
        # Power in low-freq band (omega < 0.3) vs high-freq
        omegas = 2 * np.pi * freqs
        low_band  = omegas < 0.3
        high_band = omegas >= 0.3
        pow_low  = float(np.sum(power[low_band]))
        pow_high = float(np.sum(power[high_band]))
        pow_tot  = pow_low + pow_high
        print(f"  {name}: omega_centroid={omega_centroid:.4f}  "
              f"low_band_frac={pow_low/max(pow_tot,1e-12)*100:.1f}%")

    print()
    print("INTERPRETATION:")
    print("  A_kick=1.0 drove phi into strongly nonlinear regime (|phi| > 2pi).")
    print("  Both signals dominated by global collective mode at omega~1.0.")
    print("  Local mass-gap signal buried under global response.")
    print("  Need linear-regime probe: A_kick <= 0.05, or plane-wave probe.")


if __name__ == "__main__":
    analyze_shapiro()
    analyze_redshift()
