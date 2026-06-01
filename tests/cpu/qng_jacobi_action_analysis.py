"""QNG-CPU-084: Jacobi action J = integral(p dq) universality across R.

CPU-083 computed S_Hamilton = integral(L dt) = integral(T - V) dt and found
16.5% R-spread. But the ADIABATIC INVARIANT and Bohr-Sommerfeld quantum is
the Jacobi action (abbreviated action):

    J = cycle_integral(p · dq) = 2 * integral(T_kin) dt over one period

For v8 canonical pairs (sigma_m, pi_m) and (phi, pi_phi):
  J_m   = integral(pi_m   * d_sigma_m/dt) dt = integral(pi_m^2 / mu_m) dt
        = 2 * integral(T_m) dt
  J_phi = 2 * integral(T_phi) dt

Note: sigma_g is NOT canonical in v8 (gradient-flow evolution, no conjugate
momentum). T_g = (K_BACK/2) chi^2 is a potential-like term for chi. We
exclude J_g.

Proper Bohr-Sommerfeld candidate:
    J_canonical = 2 * integral(T_m + T_phi) dt

If J_canonical is universal across R in {3,4,5}, it is the Planck-constant-
candidate in QNG. Unlike S, it is gauge-invariant under H -> H + const.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-jacobi-action-v1"
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


def compute_jacobi(trace_path, burn_in_lu=500.0):
    data = np.load(trace_path)
    t = data['times']; H = data['H']; M_ring = data['M_ring']
    T_g = data['T_g']; T_m = data['T_m']; T_phi = data['T_phi']

    warm = t > burn_in_lu
    t_w = t[warm]
    T_m_w = T_m[warm]; T_phi_w = T_phi[warm]; T_g_w = T_g[warm]
    H_w = H[warm]; M_w = M_ring[warm]

    period = find_period_from_fft(t_w, M_w)
    if period is None:
        return None

    n_cycles = int((t_w[-1] - t_w[0]) / period)
    if n_cycles < 2:
        return None

    t_starts = t_w[0] + period * np.arange(n_cycles)
    J_can = []  # 2 * integral(T_m + T_phi) dt
    J_full = []  # 2 * integral(T_m + T_phi + T_g) dt   (includes chi)
    S_ham = []  # integral(L) dt = integral(2T - H) dt
    E_cycle = []  # mean H in cycle
    for i in range(n_cycles):
        ts, te = t_starts[i], t_starts[i] + period
        mask = (t_w >= ts) & (t_w <= te)
        if mask.sum() < 3:
            continue
        tt = t_w[mask]
        # Canonical only
        T_can = T_m_w[mask] + T_phi_w[mask]
        J_can.append(2.0 * float(np.trapz(T_can, tt)))
        # Full (include T_g = K_BACK/2 chi^2)
        T_all = T_can + T_g_w[mask]
        J_full.append(2.0 * float(np.trapz(T_all, tt)))
        # Hamilton action
        L_vals = 2.0 * T_all - H_w[mask]
        S_ham.append(float(np.trapz(L_vals, tt)))
        E_cycle.append(float(np.mean(H_w[mask])))

    if len(J_can) == 0:
        return None

    J_can = np.array(J_can)
    J_full = np.array(J_full)
    S_ham = np.array(S_ham)
    E_cycle = np.array(E_cycle)

    return {
        'period_lu': float(period),
        'n_cycles': int(len(J_can)),
        'J_canonical_mean': float(J_can.mean()),
        'J_canonical_std':  float(J_can.std()),
        'J_canonical_rel':  float(abs(J_can.std() / J_can.mean())) if abs(J_can.mean()) > 1e-10 else float('inf'),
        'J_full_mean':      float(J_full.mean()),
        'J_full_std':       float(J_full.std()),
        'S_ham_mean':       float(S_ham.mean()),
        'E_cycle_mean':     float(E_cycle.mean()),
        'T_kin_can_mean':   float((T_m_w + T_phi_w).mean()),
        'T_g_mean':         float(T_g_w.mean()),
        'E_over_omega':     float(E_cycle.mean() * period / (2 * np.pi)),  # classical adiabatic invariant for SHO
    }


def main():
    print("=" * 80)
    print("QNG-CPU-084: Jacobi action (Bohr-Sommerfeld) across R")
    print("=" * 80)

    results = {}
    for R in [3, 4, 5]:
        path = TRACE_PATHS[R]
        if not path.exists():
            print(f"\n  R={R}: traces NOT FOUND")
            continue
        print(f"\n  R={R}: loading {path.name}")
        r = compute_jacobi(path)
        if r is None:
            print(f"  R={R}: analysis failed")
            continue
        results[R] = r
        print(f"    period       = {r['period_lu']:.2f} lu  (cycles={r['n_cycles']})")
        print(f"    J_canonical  = {r['J_canonical_mean']:12.2f} +- {r['J_canonical_std']:.2f}  ({r['J_canonical_rel']*100:.3f}%)")
        print(f"    J_full (+Tg) = {r['J_full_mean']:12.2f} +- {r['J_full_std']:.2f}")
        print(f"    S_Hamilton   = {r['S_ham_mean']:12.2f}")
        print(f"    E_cycle      = {r['E_cycle_mean']:12.2f}")
        print(f"    E/omega      = {r['E_over_omega']:12.2f}  (classical SHO adiabatic inv)")
        print(f"    <T_kin_can>  = {r['T_kin_can_mean']:.3f}")
        print(f"    <T_g>        = {r['T_g_mean']:.3f}")

    if set(results.keys()) < {3, 4, 5}:
        print("\n  Missing radii — aborting")
        return

    print("\n" + "=" * 80)
    print("R-UNIVERSALITY OF JACOBI ACTION")
    print("=" * 80)

    for key in ['J_canonical_mean', 'J_full_mean', 'S_ham_mean', 'E_over_omega']:
        v3 = results[3][key]; v4 = results[4][key]; v5 = results[5][key]
        r34 = v3 / v4 if abs(v4) > 1e-10 else float('inf')
        r54 = v5 / v4 if abs(v4) > 1e-10 else float('inf')
        max_dev = max(abs(r34 - 1), abs(r54 - 1))
        print(f"  {key:22s}  R=3={v3:11.2f}  R=4={v4:11.2f}  R=5={v5:11.2f}  max_dev={max_dev*100:.2f}%")

    J_vals = [results[R]['J_canonical_mean'] for R in [3, 4, 5]]
    J_mean = np.mean(J_vals)
    J_std = np.std(J_vals)
    rel = J_std / J_mean if abs(J_mean) > 1e-10 else float('inf')

    print(f"\n  J_canonical statistics across R in {{3,4,5}}:")
    print(f"    mean = {J_mean:.2f}")
    print(f"    std  = {J_std:.2f}")
    print(f"    rel  = {rel*100:.2f}%")

    # Verdict
    if rel < 0.02:
        verdict = "UNIVERSAL"
        msg = ("J_canonical universal to <2% across R -> "
               "genuine Bohr-Sommerfeld action invariant -> "
               "h_QNG candidate confirmed.")
    elif rel < 0.10:
        verdict = "WEAKLY_UNIVERSAL"
        msg = ("J_canonical agrees within 10% -> "
               "common attractor basin with mild R-modulation.")
    else:
        verdict = "R_DEPENDENT"
        msg = ("J_canonical varies >10% with R -> "
               "not universal even in canonical form.")

    print(f"\n  VERDICT: {verdict}")
    print(f"  {msg}")

    # Bohr-Sommerfeld candidate quanta for the universal value (if any)
    if rel < 0.10:
        print(f"\n  Bohr-Sommerfeld: J = 2*pi*(n+1/2)*h_QNG")
        for n in [0, 1, 2, 3]:
            h_cand = J_mean / (2 * np.pi * (n + 0.5))
            print(f"    n={n}: h_QNG_candidate = {h_cand:.3f}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'results_per_R': {str(k): v for k, v in results.items()},
            'J_canonical_mean_across_R': float(J_mean),
            'J_canonical_std_across_R': float(J_std),
            'J_canonical_rel_spread': float(rel),
            'verdict': verdict, 'comment': msg,
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
