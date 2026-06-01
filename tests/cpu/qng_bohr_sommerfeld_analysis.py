"""QNG-CPU-090: Bohr-Sommerfeld naive action per attractor cycle.

For any 1D periodic orbit, the Bohr-Sommerfeld quantization rule is:
    S = oint p dq = 2pi n h   (n integer)

For a multi-dof canonical Hamiltonian with kinetic T = Σ pi_i²/(2μ_i),
per-period action is:
    S_period = ∫₀^T (Σ pi_i q̇_i - H) dt
             = ∫₀^T (2 T_kin - H) dt            # virial for kinetic
             = T * [2<T_kin> - <H>]
             = T * <L>
             = T * E_char

Where E_char is the period-independent invariant = 660 lu (R-universal).

**Test**: compute S_period for Rin{2,3,4,5,6}. If S is also R-universal
(modulo discrete multiples 2pi n), this is an emergent quantized action
scale — the first QNG candidate for h.

**Period extraction**: FFT of M_ring trace; dominant peak gives T.

If S_R values cluster at 2pi*n*h for integer n with the same h across R,
we have a new emergent scale. Otherwise FAIL.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "07_validation" / "audits" / "qng-bohr-sommerfeld-v1"
AUDIT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    2: "qng-v8-particle-probe-R2-v1",
    3: "qng-v8-particle-probe-R3-v1",
    4: "qng-v8-particle-probe-v1",
    5: "qng-v8-particle-probe-R5-v1",
    6: "qng-v8-particle-probe-R6-v1",
}

BURN_IN_LU = 500.0


def find_period(t, signal):
    """FFT-based dominant period.
    Returns (T_period, peak_power, freq_peak, all_freqs, all_powers)."""
    # Uniform sampling assumed; dt from mean
    dt = float(np.mean(np.diff(t)))
    sig = signal - signal.mean()
    n = len(sig)
    # Hann window
    win = np.hanning(n)
    F = np.fft.rfft(sig * win)
    freqs = np.fft.rfftfreq(n, dt)
    power = np.abs(F) ** 2
    # Ignore DC
    power[0] = 0.0
    idx = int(np.argmax(power))
    f_peak = freqs[idx]
    if f_peak <= 0:
        return None, 0.0, 0.0, freqs, power
    T_peak = 1.0 / f_peak
    return T_peak, float(power[idx]), float(f_peak), freqs, power


def analyze_R(R, source_dir):
    path = ROOT / "07_validation" / "audits" / source_dir / "traces.npz"
    if not path.exists():
        return None
    d = np.load(path)
    t = d["times"]
    H = d["H"]
    T_m = d["T_m"]
    T_phi = d["T_phi"]
    T_g = d["T_g"]
    M = d["M_ring"]

    warm = t > BURN_IN_LU
    t_w = t[warm]
    H_w = H[warm]
    Tkin_w = T_g[warm] + T_m[warm] + T_phi[warm]
    M_w = M[warm]

    H_mean = float(H_w.mean())
    T_mean = float(Tkin_w.mean())
    E_char = 2 * T_mean - H_mean
    H_std = float(H_w.std())
    H_drift = (H_w.max() - H_w.min()) / abs(H_mean) * 100

    # Period from M_ring FFT
    T_M, power_M, f_M, freqs, powers = find_period(t_w, M_w)
    # Also from T_phi trace (should oscillate at same or harmonic freq)
    T_Tp, power_Tp, f_Tp, _, _ = find_period(t_w, Tkin_w)

    S_M = E_char * T_M if T_M else None
    S_Tp = E_char * T_Tp if T_Tp else None

    return {
        "R": R,
        "E_char": E_char,
        "H_mean": H_mean,
        "H_std": H_std,
        "H_drift_pct": H_drift,
        "T_kin_mean": T_mean,
        "M_mean": float(M_w.mean()),
        "M_std": float(M_w.std()),
        "period_from_M_ring": T_M,
        "period_from_T_kin": T_Tp,
        "freq_peak_M": f_M,
        "freq_peak_T": f_Tp,
        "S_period_from_M": S_M,
        "S_period_from_T": S_Tp,
        "top_freqs": freqs[1:8].tolist(),
        "top_powers": (powers[1:8] / powers[1:].max()).tolist(),
    }


def main():
    print("=" * 80)
    print("QNG-CPU-090: Bohr-Sommerfeld action per attractor cycle")
    print("=" * 80)
    print("  S_period = E_char * T_period    (naive closed-orbit action)")
    print("  Test: does S_R = 2*pi*n*h with same h across R?")
    print()

    results = {}
    for R, src in SOURCES.items():
        r = analyze_R(R, src)
        if r is None:
            print(f"  R={R}: MISSING data")
            continue
        results[R] = r
        print(f"R={R}:  E_char={r['E_char']:8.2f}  T_M={r['period_from_M_ring']:7.2f}  "
              f"T_Tkin={r['period_from_T_kin']:7.2f}  S_M={r['S_period_from_M']:10.2f}  "
              f"S_Tkin={r['S_period_from_T']:10.2f}")
    print()

    # R-universality check
    Rs = sorted(results.keys())
    Es = np.array([results[R]["E_char"] for R in Rs])
    Tms = np.array([results[R]["period_from_M_ring"] for R in Rs])
    Tts = np.array([results[R]["period_from_T_kin"] for R in Rs])
    SMs = np.array([results[R]["S_period_from_M"] for R in Rs])
    STs = np.array([results[R]["S_period_from_T"] for R in Rs])

    print("=" * 80)
    print("R-UNIVERSALITY TEST")
    print("=" * 80)

    def cv(arr):
        arr = np.asarray(arr, dtype=float)
        return float(arr.std() / abs(arr.mean()) * 100)

    print(f"  CV(E_char)         : {cv(Es):.3f}%  ->  baseline (known R-universal)")
    print(f"  CV(T_M)            : {cv(Tms):.3f}%  ->  period from M_ring FFT")
    print(f"  CV(T_Tkin)         : {cv(Tts):.3f}%  ->  period from T_kin FFT")
    print(f"  CV(S_M = E*T_M)    : {cv(SMs):.3f}%  ->  Bohr-Sommerfeld M-based")
    print(f"  CV(S_T = E*T_Tkin) : {cv(STs):.3f}%  ->  Bohr-Sommerfeld T-based")
    print()

    mean_S_M = float(SMs.mean())
    mean_S_T = float(STs.mean())
    print(f"  Mean S_M = {mean_S_M:10.2f}  -> h candidate = {mean_S_M/(2*np.pi):.2f} lu")
    print(f"  Mean S_T = {mean_S_T:10.2f}  -> h candidate = {mean_S_T/(2*np.pi):.2f} lu")
    print()

    # Verdict
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    cv_SM = cv(SMs)
    cv_ST = cv(STs)
    if cv_SM < 1.0:
        print(f"  S_M R-universal (CV {cv_SM:.2f}% < 1%) -> h candidate SURVIVES naive test")
    elif cv_SM < 5.0:
        print(f"  S_M marginal (CV {cv_SM:.2f}%)  -> need integer-quantization check")
    else:
        print(f"  S_M R-DEPENDENT (CV {cv_SM:.2f}%)  -> h candidate FAIL")

    if cv_ST < 1.0:
        print(f"  S_T R-universal (CV {cv_ST:.2f}% < 1%) -> h candidate SURVIVES naive test")
    elif cv_ST < 5.0:
        print(f"  S_T marginal (CV {cv_ST:.2f}%)  -> need integer-quantization check")
    else:
        print(f"  S_T R-DEPENDENT (CV {cv_ST:.2f}%)  -> h candidate FAIL")

    # Integer-quantization check: is S_R / S_min close to integer for each R?
    if cv_SM > 1.0:
        S_min_M = float(SMs.min())
        ratios_M = SMs / S_min_M
        print(f"\n  Integer-quantization test (S_M / S_min):")
        for R, r in zip(Rs, ratios_M):
            print(f"    R={R}: ratio = {r:.4f}  (closest integer: {round(r)}, "
                  f"dev {abs(r - round(r))/round(r)*100:.2f}% from integer)")

    out = {
        "results": {str(R): results[R] for R in Rs},
        "summary": {
            "CV_E_char_pct": cv(Es),
            "CV_T_M_pct": cv(Tms),
            "CV_T_Tkin_pct": cv(Tts),
            "CV_S_M_pct": cv_SM,
            "CV_S_T_pct": cv_ST,
            "mean_S_M": mean_S_M,
            "mean_S_T": mean_S_T,
            "h_candidate_from_M": mean_S_M / (2 * np.pi),
            "h_candidate_from_T": mean_S_T / (2 * np.pi),
        },
    }
    with open(AUDIT / "report.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Report: {AUDIT / 'report.json'}")


if __name__ == "__main__":
    main()
