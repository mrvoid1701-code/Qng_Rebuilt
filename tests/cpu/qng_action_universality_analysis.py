"""QNG-CPU-083: action universality analysis across ring radii.

Reads traces from GPU-038 (R=4) and GPU-039 (R=3, R=5) probes and computes
the Hamilton action S_cycle = integral(T_kin - V_pot) dt per period for
each. Tests the R-universality hypothesis: if S(R=3) = S(R=4) = S(R=5)
within a few percent, then the orbital attractor produces a UNIVERSAL
action invariant -> genuine h_QNG candidate.

If S varies with R systematically, the "attractor" is an R-labeled tower
and h is not uniquely defined.

Protocol:
  For each R in {3, 4, 5}:
    Load traces.npz from its probe audit dir
    Find dominant M_ring oscillation period via FFT
    Split into integer cycles, compute S per cycle
    Report <S> +- std

  Compare R=3/R=4/R=5:
    ratio(3/4), ratio(5/4)
    Universality verdict
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-action-universality-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

TRACE_PATHS = {
    3: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R3-v1" / "traces.npz",
    4: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1"    / "traces.npz",
    5: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R5-v1" / "traces.npz",
}


def find_period_from_fft(t, signal):
    signal = signal - np.mean(signal)
    dt = t[1] - t[0]
    fft = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), d=dt)
    power = np.abs(fft) ** 2
    valid = freqs > 1e-6
    if not np.any(valid):
        return None
    peak_idx = np.argmax(power[valid]) + np.argmax(valid)
    f_peak = freqs[peak_idx]
    if f_peak < 1e-10:
        return None
    return 1.0 / f_peak


def compute_action_stats(trace_path, burn_in_lu=500.0):
    data = np.load(trace_path)
    t = data['times']
    H = data['H']
    M_ring = data['M_ring']
    T_m = data['T_m']; T_phi = data['T_phi']; T_g = data['T_g']

    warm = t > burn_in_lu
    t_w = t[warm]; H_w = H[warm]
    Tm_w = T_m[warm]; Tphi_w = T_phi[warm]; Tg_w = T_g[warm]
    M_w = M_ring[warm]

    T_kin = Tg_w + Tm_w + Tphi_w
    V_pot = H_w - T_kin

    period = find_period_from_fft(t_w, M_w)
    if period is None:
        return None

    n_cycles = int((t_w[-1] - t_w[0]) / period)
    if n_cycles < 2:
        return None

    t_starts = t_w[0] + period * np.arange(n_cycles)
    actions = []
    for i in range(n_cycles):
        ts, te = t_starts[i], t_starts[i] + period
        mask = (t_w >= ts) & (t_w <= te)
        if mask.sum() < 3:
            continue
        L_vals = T_kin[mask] - V_pot[mask]
        actions.append(float(np.trapz(L_vals, t_w[mask])))
    actions = np.array(actions)
    if len(actions) == 0:
        return None

    return {
        'period_lu': float(period),
        'n_cycles': int(len(actions)),
        'actions_per_cycle': [float(a) for a in actions],
        'S_mean': float(actions.mean()),
        'S_std': float(actions.std()),
        'S_relative': float(abs(actions.std() / actions.mean()))
                       if abs(actions.mean()) > 1e-10 else float('inf'),
        'H_mean': float(H_w.mean()),
        'H_std': float(H_w.std()),
        'H_drift_frac': float(abs(H_w[-1] - H_w[0]) / max(abs(H_w[0]), 1e-10)),
        'M_ring_mean': float(M_w.mean()),
        'T_kin_mean': float(T_kin.mean()),
        'V_pot_mean': float(V_pot.mean()),
    }


def main():
    print("=" * 80)
    print("QNG-CPU-083: action universality across ring radii")
    print("=" * 80)

    results = {}
    for R in [3, 4, 5]:
        path = TRACE_PATHS[R]
        if not path.exists():
            print(f"\n  R={R}: traces NOT FOUND at {path}")
            continue
        print(f"\n  R={R}: loading {path.name}")
        r = compute_action_stats(path)
        if r is None:
            print(f"  R={R}: analysis failed")
            continue
        results[R] = r
        print(f"    period  = {r['period_lu']:.2f} lu")
        print(f"    cycles  = {r['n_cycles']}")
        print(f"    <S>     = {r['S_mean']:.3f}")
        print(f"    std(S)  = {r['S_std']:.3f}")
        print(f"    |std/mean| = {r['S_relative']:.4f} ({r['S_relative']*100:.2f}%)")
        print(f"    H_mean  = {r['H_mean']:.3f}")
        print(f"    H_drift = {r['H_drift_frac']:.2e}")
        print(f"    M_ring  = {r['M_ring_mean']:.2f}")

    if set(results.keys()) < {3, 4, 5}:
        print("\n  Missing radii - run GPU-039 probes first")
        return

    S3 = results[3]['S_mean']; S4 = results[4]['S_mean']; S5 = results[5]['S_mean']
    r34 = S3 / S4; r54 = S5 / S4

    print("\n" + "=" * 80)
    print("R-UNIVERSALITY")
    print("=" * 80)
    print(f"  S(R=3) = {S3:.3f}")
    print(f"  S(R=4) = {S4:.3f}")
    print(f"  S(R=5) = {S5:.3f}")
    print(f"  ratio S(3)/S(4) = {r34:.4f}")
    print(f"  ratio S(5)/S(4) = {r54:.4f}")

    max_dev = max(abs(r34 - 1), abs(r54 - 1))
    print(f"  max deviation from universality = {max_dev*100:.2f}%")

    if max_dev < 0.02:
        verdict = "UNIVERSAL"
        comment = ("S_cycle universal to <2% across R in {3,4,5} -> "
                   "orbital-attractor action is an R-independent substrate "
                   "invariant. h_QNG candidate strengthens.")
    elif max_dev < 0.10:
        verdict = "WEAKLY_UNIVERSAL"
        comment = (f"S_cycle within {max_dev*100:.1f}% across R - "
                   "consistent with common attractor basin with mild R-memory.")
    else:
        verdict = "R_DEPENDENT"
        comment = (f"S_cycle varies {max_dev*100:.1f}% across R -> "
                   "not a universal invariant; possibly a tower indexed by R. "
                   "Program beta (single h_QNG) WEAKENS.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {comment}")

    # L/c_phi Tesla prediction - cavity fundamental
    # c_phi**2 = beta_phi / (3 mu_phi) = 0.06 / (3*0.857) = 0.02334
    c_phi = np.sqrt(0.06 / (3.0 * 0.857))
    T_bare = 28 / c_phi
    print(f"\n  Tesla-mind cavity prediction: T_bare = L/c_phi = {T_bare:.2f} lu")
    for R in [3, 4, 5]:
        if R in results:
            T_meas = results[R]['period_lu']
            dev = (T_meas - T_bare) / T_bare
            print(f"    R={R}: T_meas={T_meas:.2f}  deviation={dev*100:+.1f}%")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'results_per_R': {str(k): v for k, v in results.items()},
            'S3_over_S4': float(r34),
            'S5_over_S4': float(r54),
            'max_deviation': float(max_dev),
            'verdict': verdict, 'comment': comment,
            'c_phi_predicted': float(c_phi),
            'T_bare_L_over_c_phi': float(T_bare),
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
