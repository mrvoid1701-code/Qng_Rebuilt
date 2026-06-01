"""QNG-CPU-087: full R-scan action analysis (R={2,3,4,5,6}).

Extends CPU-083 (S Hamilton) and CPU-084 (J Jacobi) to R={2,3,4,5,6}
to map the full action landscape. Tests:
  1. Is R=4 the true minimum, or a local one?
  2. Does T_orb(R) match Tesla's cavity prediction T=L/(n*c_phi)?
  3. Is J(R) parabolic (single well) or multi-well?
  4. Compare Hamilton S and Jacobi J spreads.

Outputs comprehensive J(R), S(R), T_orb(R) tables and verdicts on:
  - Cavity hypothesis (Tesla)
  - Action minimum (β strong form)
  - Effective ℏ candidates
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-action-full-scan-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

TRACE_PATHS = {
    2: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R2-v1" / "traces.npz",
    3: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R3-v1" / "traces.npz",
    4: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1"    / "traces.npz",
    5: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R5-v1" / "traces.npz",
    6: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-R6-v1" / "traces.npz",
}

L = 28
BETA_PHI = 0.06
MU_PHI = 0.857
C_PHI = float(np.sqrt(BETA_PHI / (3.0 * MU_PHI)))
T_CAVITY = L / C_PHI


def find_period(t, signal):
    s = signal - np.mean(signal)
    dt = t[1] - t[0]
    fft = np.fft.rfft(s)
    freqs = np.fft.rfftfreq(len(s), d=dt)
    power = np.abs(fft) ** 2
    valid = freqs > 1e-6
    if not np.any(valid):
        return None
    idx = np.argmax(power[valid]) + np.argmax(valid)
    f = freqs[idx]
    return 1.0 / f if f > 1e-10 else None


def analyze_R(trace_path, burn_in=500.0):
    if not trace_path.exists():
        return None
    data = np.load(trace_path)
    t = data['times']; H = data['H']; M = data['M_ring']
    Tg, Tm, Tp = data['T_g'], data['T_m'], data['T_phi']
    com_z, r_eff = data['com_z'], data['r_eff']
    Lz, wind = data['Lz_phi'], data['phi_winding']

    warm = t > burn_in
    t_w = t[warm]; H_w = H[warm]; M_w = M[warm]
    Tg_w = Tg[warm]; Tm_w = Tm[warm]; Tp_w = Tp[warm]
    com_z_w = com_z[warm]; r_eff_w = r_eff[warm]
    Lz_w = Lz[warm]; wind_w = wind[warm]

    period = find_period(t_w, M_w)
    if period is None or period < 5:
        return {
            'period_lu': None,
            'M_ring_mean': float(M_w.mean()),
            'M_ring_std':  float(M_w.std()),
            'M_ring_min':  float(M_w.min()),
            'M_ring_max':  float(M_w.max()),
            'H_mean':      float(H_w.mean()),
            'H_std':       float(H_w.std()),
            'r_eff_mean':  float(r_eff_w.mean()),
            'L_z_mean':    float(Lz_w.mean()),
            'phi_winding_final': float(wind_w[-1]),
            'COM_z_range': [float(com_z_w.min()), float(com_z_w.max())],
            'verdict': 'NO_PERIOD',
            'note': 'period detection failed - chaotic or non-oscillating'
        }

    n_cycles = int((t_w[-1] - t_w[0]) / period)
    if n_cycles < 2:
        return {'period_lu': float(period), 'verdict': 'TOO_FEW_CYCLES'}

    starts = t_w[0] + period * np.arange(n_cycles)
    S_list = []; J_list = []
    for i in range(n_cycles):
        ts, te = starts[i], starts[i] + period
        mask = (t_w >= ts) & (t_w <= te)
        if mask.sum() < 3:
            continue
        T_total = Tg_w[mask] + Tm_w[mask] + Tp_w[mask]
        L_vals = 2.0 * T_total - H_w[mask]  # L = 2T - H = T - V
        # Canonical kinetic only (excludes T_g)
        T_can = Tm_w[mask] + Tp_w[mask]
        S_list.append(float(np.trapz(L_vals, t_w[mask])))
        J_list.append(2.0 * float(np.trapz(T_can, t_w[mask])))

    S_arr = np.array(S_list); J_arr = np.array(J_list)

    return {
        'period_lu':     float(period),
        'n_cycles':      int(len(S_arr)),
        'S_mean':        float(S_arr.mean()),
        'S_std':         float(S_arr.std()),
        'S_relative':    float(abs(S_arr.std()/S_arr.mean())) if abs(S_arr.mean()) > 1e-10 else float('inf'),
        'J_mean':        float(J_arr.mean()),
        'J_std':         float(J_arr.std()),
        'J_relative':    float(abs(J_arr.std()/J_arr.mean())) if abs(J_arr.mean()) > 1e-10 else float('inf'),
        'M_ring_mean':   float(M_w.mean()),
        'M_ring_std':    float(M_w.std()),
        'M_ring_range':  [float(M_w.min()), float(M_w.max())],
        'H_mean':        float(H_w.mean()),
        'H_std':         float(H_w.std()),
        'r_eff_mean':    float(r_eff_w.mean()),
        'L_z_mean':      float(Lz_w.mean()),
        'phi_winding_final': float(wind_w[-1]),
        'COM_z_range':   [float(com_z_w.min()), float(com_z_w.max())],
        'T_cavity_dev':  float((period - T_CAVITY)/T_CAVITY),
    }


def main():
    print("=" * 80)
    print(f"QNG-CPU-087: full action scan R in {{2,3,4,5,6}} on L={L}")
    print(f"  c_phi = sqrt(beta_phi/(3*mu_phi)) = {C_PHI:.5f}")
    print(f"  T_cavity_fundamental = L/c_phi    = {T_CAVITY:.2f} lu")
    print(f"  T_cavity_2nd_harmonic = L/(2*c_phi) = {T_CAVITY/2:.2f} lu")
    print(f"  T_cavity_3rd_harmonic = L/(3*c_phi) = {T_CAVITY/3:.2f} lu")
    print("=" * 80)

    results = {}
    for R in [2, 3, 4, 5, 6]:
        path = TRACE_PATHS[R]
        if not path.exists():
            print(f"\n  R={R}: NOT YET RUN")
            continue
        print(f"\n  R={R}: loading {path.name}")
        r = analyze_R(path)
        if r is None:
            print(f"  R={R}: failed")
            continue
        results[R] = r
        if r.get('verdict') == 'NO_PERIOD':
            print(f"    NO PERIOD detected; M_ring range [{r['M_ring_min']:+.1f}, {r['M_ring_max']:+.1f}]")
            print(f"    M mean {r['M_ring_mean']:+.2f} std {r['M_ring_std']:.2f} (huge std -> chaotic/unstable)")
            print(f"    H_mean={r['H_mean']:.3f}  r_eff={r['r_eff_mean']:.2f}  L_z={r['L_z_mean']:.2e}")
            print(f"    phi_winding final = {r['phi_winding_final']:.4f}")
            continue
        print(f"    period       = {r['period_lu']:.2f} lu  (cycles={r['n_cycles']})  "
              f"vs cavity dev {r['T_cavity_dev']*100:+.1f}%")
        print(f"    J_canonical  = {r['J_mean']:11.2f} +- {r['J_std']:.2f}  ({r['J_relative']*100:.3f}%)")
        print(f"    S_Hamilton   = {r['S_mean']:11.2f} +- {r['S_std']:.2f}  ({r['S_relative']*100:.3f}%)")
        print(f"    M_ring       = {r['M_ring_mean']:8.2f} +- {r['M_ring_std']:.2f}  range {r['M_ring_range']}")
        print(f"    H_mean       = {r['H_mean']:8.3f}  r_eff={r['r_eff_mean']:.2f}  L_z={r['L_z_mean']:+.2e}")

    # Summary table & cavity test
    valid = {R: r for R, r in results.items() if r.get('period_lu') is not None}
    if not valid:
        print("\n  No valid traces for analysis")
        return

    print("\n" + "=" * 80)
    print("J(R) ACTION LANDSCAPE")
    print("=" * 80)
    print(f"{'R':>3s} {'T_orb (lu)':>12s} {'T_pred(L/(nc))':>14s} {'n_cavity':>8s} "
          f"{'J':>10s} {'S':>10s} {'M_ring':>10s}")
    for R in sorted(valid.keys()):
        r = valid[R]
        # Find best cavity n
        n_best, dev_best = 0, 1.0
        for n in [1, 2, 3, 4]:
            T_pred = T_CAVITY / n
            dev = abs(r['period_lu'] - T_pred) / T_pred
            if dev < dev_best:
                dev_best = dev; n_best = n
        T_pred = T_CAVITY / n_best if n_best > 0 else 0
        cavity_match = "OK" if dev_best < 0.05 else "x"
        print(f"  R={R} {r['period_lu']:12.2f} {T_pred:14.2f} {n_best:8d}{cavity_match:>2s}  "
              f"{r['J_mean']:10.2f} {r['S_mean']:10.2f} {r['M_ring_mean']:10.2f}")

    # Find J minimum
    J_vals = {R: r['J_mean'] for R, r in valid.items()}
    R_min = min(J_vals.keys(), key=lambda R: J_vals[R])
    print(f"\n  J minimum at R={R_min}: J_min = {J_vals[R_min]:.2f}")

    # ℏ candidates
    h_can_jmin = J_vals[R_min] / (2 * np.pi)
    print(f"\n  Candidate h_QNG = J_min / (2*pi) = {h_can_jmin:.4f} (Bohr-Sommerfeld n=0)")
    h_can_jmin1 = J_vals[R_min] / (2 * np.pi * 1.5)
    print(f"  Candidate h_QNG = J_min / (2*pi * 1.5) = {h_can_jmin1:.4f} (Bohr-Sommerfeld n=1)")

    # Cavity universality
    cavity_scores = []
    for R, r in valid.items():
        for n in [1, 2, 3, 4]:
            T_pred = T_CAVITY / n
            dev = abs(r['period_lu'] - T_pred) / T_pred
            if dev < 0.05:
                cavity_scores.append((R, n, dev))
                break

    print("\n" + "=" * 80)
    print("CAVITY HYPOTHESIS VERDICT (Tesla)")
    print("=" * 80)
    if len(cavity_scores) >= 3:
        verdict_cavity = "CAVITY_LADDER_CONFIRMED"
        print(f"  >=3 R values match cavity modes T=L/(n*c_phi) within 5%")
        for R, n, dev in cavity_scores:
            print(f"    R={R}: n={n}, deviation {dev*100:.2f}%")
    elif len(cavity_scores) == 0:
        verdict_cavity = "CAVITY_DEAD"
        print(f"  NO R value matches any cavity mode within 5% — Tesla cavity hypothesis FALSIFIED")
    else:
        verdict_cavity = "CAVITY_PARTIAL"
        print(f"  Only {len(cavity_scores)} R-values cavity-locked: {[r for r,_,_ in cavity_scores]}")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'L': L, 'c_phi': C_PHI, 'T_cavity_fundamental': T_CAVITY,
            'results_per_R': {str(k): v for k, v in results.items()},
            'J_minimum_R': int(R_min),
            'J_min_value': float(J_vals[R_min]),
            'h_candidate_n0': float(h_can_jmin),
            'h_candidate_n1': float(h_can_jmin1),
            'cavity_verdict': verdict_cavity,
            'cavity_matches': [{'R': r, 'n': n, 'dev': d} for r, n, d in cavity_scores],
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
