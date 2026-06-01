"""QNG-CPU-082-beta — action analysis on GPU-038 orbital traces.

Program β: compute the classical Hamilton action
    S = ∫(T − V) dt  (Lagrangian integral)
over the GPU-038 orbital cycle. If S is quasi-constant across cycles,
the action J is a candidate invariant suitable for Bohr-Sommerfeld
quantization J_n = 2π·ℏ·(n + ½).

Protocol:
  Load GPU-038 traces.npz (200 samples every 10 lu from T=0..2000 lu).
  Extract time series of:
    - H_v8 (total energy, conserved)
    - T_m + T_phi (kinetic)
    - V_couple (potential part)
    - M_ring (mass proxy — used to find oscillation period)
  FFT M_ring to find dominant period T_orb.
  Split trace into ~N cycles.
  For each cycle compute S_n = ∫(T − V) dt over one period.
  Report <S> ± std across cycles.

Output:
  If S_n std/mean < 5%: CLASSICAL_ACTION_INVARIANT
    → J is well-defined, Bohr-Sommerfeld quantization can proceed.
  Else: ACTION_NOT_INVARIANT
    → attractor is not a clean periodic orbit; program β weakens.

Also computes a numerical estimate of "ℏ_candidate" from S via:
    ℏ_candidate = S / (2π · (n + ½))  for n in {0, 1, 2, 3}
  and reports these values in lattice units.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TRACES_PATH = ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1" / "traces.npz"
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-gpu038-action-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def find_period_from_fft(t, signal, n_peaks=3):
    """FFT-based period detection. Returns period in same units as t."""
    signal = signal - np.mean(signal)
    dt = t[1] - t[0]
    fft = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), d=dt)
    power = np.abs(fft) ** 2

    # Exclude DC and very low freqs
    valid = freqs > 1e-6
    if not np.any(valid):
        return None, None

    peak_idx = np.argmax(power[valid]) + np.argmax(valid)
    f_peak = freqs[peak_idx]
    if f_peak < 1e-10:
        return None, None

    period = 1.0 / f_peak
    omega = 2.0 * np.pi * f_peak

    # Top-3 peaks for reporting
    peak_list = []
    for i in range(1, len(power) - 1):
        if power[i] > power[i - 1] and power[i] > power[i + 1]:
            if freqs[i] > 0:
                peak_list.append((freqs[i], power[i]))
    peak_list.sort(key=lambda x: -x[1])

    return period, omega, peak_list[:n_peaks]


def integrate_lagrangian(t, T_kin, V_pot, t_start, t_end):
    """Compute S = ∫(T-V)dt via Simpson if possible else trapezoid."""
    mask = (t >= t_start) & (t <= t_end)
    if mask.sum() < 3:
        return None
    L_vals = T_kin[mask] - V_pot[mask]
    return float(np.trapz(L_vals, t[mask]))


def main():
    print("=" * 80)
    print("QNG-CPU-082-beta: action analysis on GPU-038 orbital traces")
    print("=" * 80)

    data = np.load(TRACES_PATH)
    print(f"  Loaded {TRACES_PATH.name}")
    print(f"  Available keys: {list(data.files)}")

    t = data['times']
    H = data['H']
    M_ring = data['M_ring']
    T_m = data['T_m']
    T_phi = data['T_phi']
    T_g = data['T_g']
    V_couple = data['V_couple']

    print(f"  N samples = {len(t)},  t_range = [{t[0]:.1f}, {t[-1]:.1f}] lu")
    print(f"  H mean = {H.mean():.3f},  std = {H.std():.3f}")
    print(f"  M_ring mean = {M_ring.mean():.2f},  std = {M_ring.std():.2f}")

    # Burn-in
    t_burn = 500.0
    warm = t > t_burn
    t_w = t[warm]
    H_w = H[warm]
    M_w = M_ring[warm]
    Tm_w = T_m[warm]
    Tphi_w = T_phi[warm]
    Tg_w = T_g[warm]
    Vc_w = V_couple[warm]

    # Build kinetic and potential estimates
    T_kin = Tg_w + Tm_w + Tphi_w   # total kinetic
    # V_pot = H - T_kin (so L = T - V = 2T - H exactly)
    V_pot = H_w - T_kin
    L_vals = T_kin - V_pot  # = 2·T - H

    print(f"\n  Kinetic/Potential split (post-burn):")
    print(f"    <T_kin> = {T_kin.mean():.3f}")
    print(f"    <V_pot> = {V_pot.mean():.3f}")
    print(f"    <L=T-V> = {L_vals.mean():.3f}")

    # Find M_ring period via FFT
    result = find_period_from_fft(t_w, M_w)
    if result is None or result[0] is None:
        print("\n  FFT failed to find period — aborting")
        return
    period, omega, peaks = result
    print(f"\n  M_ring oscillation:")
    print(f"    Primary period = {period:.2f} lu  (omega = {omega:.4f})")
    for k, (f, p) in enumerate(peaks):
        print(f"    Peak {k+1}: f={f:.5f}  T={1/f:.2f} lu  power={p:.2e}")

    # Split post-burn trace into integer cycles
    n_cycles = int((t_w[-1] - t_w[0]) / period)
    print(f"\n  Cycles available (T={period:.1f} lu): {n_cycles}")

    if n_cycles < 2:
        print("  Too few cycles for action statistics; aborting")
        return

    # Compute action per cycle
    t_starts = t_w[0] + period * np.arange(n_cycles)
    actions = []
    for i in range(n_cycles):
        ts = t_starts[i]
        te = ts + period
        S = integrate_lagrangian(t_w, T_kin, V_pot, ts, te)
        if S is not None:
            actions.append(S)
            print(f"  cycle {i+1}: t in [{ts:.1f}, {te:.1f}]  S = {S:.3f}")

    if len(actions) == 0:
        print("  No valid cycles")
        return

    actions = np.array(actions)
    S_mean = float(actions.mean())
    S_std = float(actions.std())
    S_rel = abs(S_std / S_mean) if abs(S_mean) > 1e-10 else float('inf')

    print("\n" + "=" * 80)
    print("ACTION STATISTICS")
    print("=" * 80)
    print(f"  <S>    = {S_mean:.3f}  (lattice units, lu)")
    print(f"  std(S) = {S_std:.3f}")
    print(f"  |std/mean| = {S_rel:.3f}")

    # Bohr-Sommerfeld candidate quanta
    print(f"\n  Bohr-Sommerfeld candidate h-scales:")
    print(f"    n=0:  h_candidate = S/(2*pi*0.5) = {abs(S_mean)/(np.pi):.3f}")
    for n in [1, 2, 3]:
        print(f"    n={n}:  h_candidate = S/(2*pi*{n+0.5}) = "
              f"{abs(S_mean)/(2*np.pi*(n+0.5)):.3f}")

    # Verdict
    if S_rel < 0.05:
        verdict = "CLASSICAL_ACTION_INVARIANT"
        comment = ("Action invariant to <5% across cycles — Bohr-Sommerfeld"
                   " quantization viable")
    elif S_rel < 0.20:
        verdict = "ACTION_SEMI_INVARIANT"
        comment = ("Action varies 5-20% — marginal invariance, weak ℏ"
                   " candidate")
    else:
        verdict = "ACTION_NOT_INVARIANT"
        comment = (f"Action varies {S_rel*100:.0f}% — orbital is not a clean"
                   " periodic cycle; program β weakens")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {comment}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'traces_source': str(TRACES_PATH),
            'n_samples': int(len(t)),
            'n_warm':    int(warm.sum()),
            't_burn_lu': t_burn,
            'H_mean': float(H.mean()), 'H_std': float(H.std()),
            'M_ring_mean': float(M_ring.mean()),
            'M_ring_std':  float(M_ring.std()),
            'T_kin_mean':  float(T_kin.mean()),
            'V_pot_mean':  float(V_pot.mean()),
            'L_mean':      float(L_vals.mean()),
            'period_lu':   float(period),
            'omega':       float(omega),
            'top_peaks':   [{'freq': float(f), 'T_lu': float(1/f),
                             'power': float(p)} for f, p in peaks],
            'n_cycles_analyzed': len(actions),
            'actions_per_cycle': [float(a) for a in actions],
            'S_mean': S_mean, 'S_std': S_std, 'S_relative': S_rel,
            'h_candidates': {
                str(n): float(abs(S_mean)/(2*np.pi*(n+0.5)))
                for n in [0, 1, 2, 3]
            },
            'verdict': verdict,
            'comment': comment,
        }, f, indent=2)

    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
