"""QNG-CPU-089: L-scan analysis of ⟨L⟩ invariant.

Reads L-scan traces and fits E_char(L) to determine scaling:
  alpha = 0 (intensive)     -> intrinsic substrate rest-energy
  alpha = 1 (linear)        -> geometric (surface/edge)
  alpha = 2 (area)          -> cross-sectional
  alpha = 3 (extensive)     -> vacuum energy (volume artifact)
  other alpha               -> fractal/anomalous

E_char = 2⟨T_kin⟩ - ⟨H⟩ (period-independent virial-form).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits" / "qng-L-scan-E-char-v1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    20: ROOT / "07_validation" / "audits" / "qng-v8-L-scan-R4-L20-v1" / "traces.npz",
    24: ROOT / "07_validation" / "audits" / "qng-v8-L-scan-R4-L24-v1" / "traces.npz",
    28: ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1"    / "traces.npz",
}


def e_char(path, burn_in=500.0):
    if not path.exists():
        return None
    data = np.load(path)
    t = data['times']
    warm = t > burn_in
    if warm.sum() < 5:
        return None
    H = data['H'][warm]
    T_kin = data['T_g'][warm] + data['T_m'][warm] + data['T_phi'][warm]
    M = data['M_ring'][warm]
    H_mean = float(H.mean())
    T_mean = float(T_kin.mean())
    E = 2 * T_mean - H_mean
    return {
        'H_mean': H_mean, 'T_mean': T_mean, 'E_char': E,
        'H_std': float(H.std()), 'T_std': float(T_kin.std()),
        'M_mean': float(M.mean()),
        'M_std': float(M.std()),
        'n_samples': int(warm.sum()),
    }


def main():
    print("=" * 80)
    print("QNG-CPU-089: L-scan E_char(L) analysis")
    print("=" * 80)
    print(f"  R=4 fixed, L in {{20, 24, 28}}, burn-in 500 lu")
    print(f"  E_char = 2<T_kin> - <H> (period-independent)")
    print()

    results = {}
    for L, path in SOURCES.items():
        r = e_char(path)
        if r is None:
            print(f"  L={L}: NOT YET AVAILABLE ({path.name})")
            continue
        results[L] = r
        N = L ** 3
        print(f"  L={L} (N={N}):")
        print(f"    <H>     = {r['H_mean']:10.2f} +- {r['H_std']:.2f}")
        print(f"    <T>     = {r['T_mean']:10.2f} +- {r['T_std']:.2f}")
        print(f"    E_char  = {r['E_char']:10.2f}")
        print(f"    E/L     = {r['E_char']/L:.4f}")
        print(f"    E/L^2   = {r['E_char']/L**2:.4f}")
        print(f"    E/L^3   = {r['E_char']/L**3:.6f}")
        print(f"    <M_ring> = {r['M_mean']:8.2f} +- {r['M_std']:.2f}")

    if len(results) < 2:
        print("\n  Need >=2 L values for scaling fit.")
        return

    Ls = np.array(sorted(results.keys()))
    Es = np.array([results[L]['E_char'] for L in Ls])
    Hs = np.array([results[L]['H_mean'] for L in Ls])
    Ts = np.array([results[L]['T_mean'] for L in Ls])

    print("\n" + "=" * 80)
    print("SCALING FITS: E_char = A * L^alpha")
    print("=" * 80)

    if len(Ls) >= 2:
        log_L = np.log(Ls)
        log_E = np.log(Es)
        if len(Ls) == 2:
            # 2 points -> exact slope
            alpha = (log_E[1] - log_E[0]) / (log_L[1] - log_L[0])
            lnA = log_E[0] - alpha * log_L[0]
            A = float(np.exp(lnA))
            print(f"  N=2 exact slope: alpha = {alpha:.4f}, A = {A:.4f}")
        else:
            alpha, lnA = np.polyfit(log_L, log_E, 1)
            A = float(np.exp(lnA))
            pred = A * Ls ** alpha
            rms = np.sqrt(np.mean(((Es - pred) / Es) ** 2)) * 100
            print(f"  alpha = {alpha:.4f}, A = {A:.4f}")
            print(f"  RMS residual: {rms:.3f}%")
            for L, E, p in zip(Ls, Es, pred):
                print(f"    L={L}: measured {E:.2f}, fit {p:.2f}, dev {(E-p)/E*100:+.2f}%")

    # Verdict
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  L values:      {Ls.tolist()}")
    print(f"  E_char values: {[round(E,2) for E in Es]}")
    print(f"  ⟨H⟩ values:    {[round(h,2) for h in Hs]}")
    print()
    if len(Ls) >= 2:
        alpha_val = alpha
        if abs(alpha_val) < 0.1:
            print(f"  alpha ~= 0 -> E_char is INTENSIVE (substrate rest-energy!)")
            print(f"  This would be a FIRST emergent Lorentz-invariant scale in v8.")
        elif abs(alpha_val - 3) < 0.3:
            print(f"  alpha ~= 3 -> E_char is EXTENSIVE (vacuum energy, scales with volume)")
            print(f"  Intensive quantity: E_char / N = {Es[0]/Ls[0]**3:.6f}")
        elif 0.5 < alpha_val < 1.5:
            print(f"  alpha ~= 1 -> geometric (ring perimeter/surface)")
        elif 1.5 <= alpha_val < 2.5:
            print(f"  alpha ~= 2 -> area-law (cross-section)")
        else:
            print(f"  alpha = {alpha_val:.3f} -> anomalous scaling")

    with open(AUDIT_DIR / "report.json", "w") as f:
        json.dump({
            'L_values': Ls.tolist(),
            'E_char': Es.tolist(),
            'H_mean': Hs.tolist(),
            'T_mean': Ts.tolist(),
            'alpha_fit': float(alpha) if len(Ls) >= 2 else None,
            'A_fit': A if len(Ls) >= 2 else None,
            'details': {str(L): results[L] for L in results},
        }, f, indent=2)
    print(f"\n  Report: {AUDIT_DIR / 'report.json'}")


if __name__ == "__main__":
    main()
