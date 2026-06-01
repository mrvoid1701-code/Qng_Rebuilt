"""Compute E_char across R in {2, 3, 4, 5, 6} at L=28.

Confirms Gate C (R-extension) of NOTE-QNG-017: <L> R-independent at L=28,
predicted 658.56 by XY ground state.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "07_validation" / "audits"

SOURCES = {
    2: AUDIT_DIR / "qng-v8-particle-probe-R2-v1"  / "traces.npz",
    3: AUDIT_DIR / "qng-v8-particle-probe-R3-v1"  / "traces.npz",
    4: AUDIT_DIR / "qng-v8-particle-probe-v1"     / "traces.npz",  # L=28 R=4 (base)
    5: AUDIT_DIR / "qng-v8-particle-probe-R5-v1"  / "traces.npz",
    6: AUDIT_DIR / "qng-v8-particle-probe-R6-v1"  / "traces.npz",
}

BETA_PHI = 0.06
L = 28
N = L ** 3
PREDICTED = -(-BETA_PHI * N / 2.0)  # = +658.56


def e_char(path, burn_in=500.0):
    if not path.exists():
        return None
    data = np.load(path)
    t = data['times']
    warm = t > burn_in
    H = data['H'][warm]
    Tk = data['T_g'][warm] + data['T_m'][warm] + data['T_phi'][warm]
    E = 2 * Tk.mean() - H.mean()
    return {
        'H_mean': float(H.mean()), 'T_mean': float(Tk.mean()),
        'E_char': float(E), 'H_std': float(H.std()),
        'T_std': float(Tk.std()), 'n_warm': int(warm.sum()),
        'V_couple_mean': (float(data['V_couple'][warm].mean())
                          if 'V_couple' in data.files else None),
        'M_ring_mean': (float(data['M_ring'][warm].mean())
                        if 'M_ring' in data.files else None),
        'M_ring_std': (float(data['M_ring'][warm].std())
                       if 'M_ring' in data.files else None),
    }


print("=" * 78)
print("R-scan E_char at L=28 (Gate C of NOTE-QNG-017)")
print("=" * 78)
print(f"  Predicted (XY ground): {PREDICTED:.2f}  (= N*beta_phi/2 = {N}*{BETA_PHI}/2)")
print()

results = {}
for R, path in SOURCES.items():
    r = e_char(path)
    if r is None:
        print(f"  R={R}: NO DATA ({path.name})")
        continue
    results[R] = r
    dev_pct = (r['E_char'] / PREDICTED - 1) * 100
    print(f"  R={R}: E_char = {r['E_char']:8.3f}  dev {dev_pct:+.3f}%  "
          f"<T_kin>={r['T_mean']:.2f}  <V_c>={r['V_couple_mean'] or -1:.2f}  "
          f"<M>={r['M_ring_mean'] or -1:.2f} +-{r['M_ring_std'] or -1:.2f}")

# Stats
Es = np.array([r['E_char'] for r in results.values()])
print()
print(f"  Rs: {sorted(results.keys())}")
print(f"  Es: {[round(e, 2) for e in Es]}")
print(f"  Mean E_char: {Es.mean():.2f}")
print(f"  Std:         {Es.std():.2f}")
print(f"  CV:          {Es.std()/Es.mean()*100:.3f}%")
print(f"  Mean dev from XY ground: {(Es.mean()/PREDICTED - 1)*100:+.3f}%")
print(f"  Max dev from XY ground:  {max(abs(Es/PREDICTED - 1)*100):.3f}%")

# Even/odd split check
odds = [results[R]['E_char'] for R in [3, 5] if R in results]
evens = [results[R]['E_char'] for R in [2, 4, 6] if R in results]
if odds and evens:
    print()
    print(f"  Odd R mean:  {np.mean(odds):.2f}")
    print(f"  Even R mean: {np.mean(evens):.2f}")
    print(f"  Odd-even split: {(np.mean(odds)-np.mean(evens)):+.3f}")

AUDIT_R = AUDIT_DIR / "qng-R-scan-E-char-v1"
AUDIT_R.mkdir(exist_ok=True)
with open(AUDIT_R / "report.json", "w") as f:
    json.dump({
        'predicted': PREDICTED,
        'L': L, 'N': N, 'beta_phi': BETA_PHI,
        'results': {str(R): {
            'E_char': r['E_char'],
            'H_mean': r['H_mean'], 'T_mean': r['T_mean'],
            'V_couple_mean': r['V_couple_mean'],
            'M_ring_mean': r['M_ring_mean'],
            'M_ring_std': r['M_ring_std'],
            'deviation_pct': (r['E_char']/PREDICTED - 1)*100,
        } for R, r in results.items()},
        'stats': {
            'mean': float(Es.mean()),
            'std': float(Es.std()),
            'CV_pct': float(Es.std()/Es.mean()*100),
            'mean_dev_from_XY_ground_pct': float((Es.mean()/PREDICTED - 1)*100),
        },
    }, f, indent=2)
print(f"\n  Report: {AUDIT_R / 'report.json'}")
