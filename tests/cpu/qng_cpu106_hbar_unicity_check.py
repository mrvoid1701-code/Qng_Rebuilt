"""QNG-CPU-106b -- uniqueness check on hbar_QNG = 0.097 candidate.

Tests whether hbar ≈ 0.097 is uniquely picked by physics or just one
arbitrary factor choice.

Method: compute |H|·T_cycle normalized by every reasonable combinatorial
factor (N_nodes, N_edges, N_ring_circumference, various *2π / π /  2)
and see which give R-universal values across R={3,4,5}.

Uniqueness criterion: if only ONE normalization gives R-universal 0.097
at CV < 2%, that's the unique identification. If multiple normalizations
give R-universal values at different numbers, we have degenerate choices.
"""
import numpy as np
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "qng-cpu106-hbar-unicity-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data from CPU-100 REPORT
# R, T_cycle, H_mean, |H|*T
data = {
    3: (176.32, -226.07, 39858),
    4: (178.22, -225.02, 40102),
    5: (182.69, -223.78, 40886),
}

L = 28  # Lattice size from CPU-100
N_nodes = L**3  # = 21952
N_edges = N_nodes * 3  # cubic lattice z=6, N_edges = z*N/2 = 3*N = 65856

# Also consider ring-specific counts
# Ring radius R: circumference ~ 2*pi*R; thickness ~2-4 lu
# Estimate N_ring_nodes ~ 4*pi*R * 3 (rough)
def N_ring(R):
    return int(4 * np.pi * R * 3)

def try_normalization(norm_name, norm_fn_R):
    """Compute hbar candidate for each R and return mean, std, CV."""
    values = []
    for R, (T, H, HT) in data.items():
        norm = norm_fn_R(R)
        v = HT / norm
        values.append(v)
    values = np.array(values)
    mean = float(np.mean(values))
    std = float(np.std(values))
    cv = std / abs(mean) * 100 if mean != 0 else float('inf')
    return {'name': norm_name, 'values': values.tolist(),
            'mean': mean, 'std': std, 'cv_pct': cv}


# Try many normalizations
normalizations = [
    ('|H|T', lambda R: 1),
    ('|H|T / N_nodes', lambda R: N_nodes),
    ('|H|T / N_edges', lambda R: N_edges),
    ('|H|T / (2pi N_nodes)', lambda R: 2*np.pi*N_nodes),
    ('|H|T / (2pi N_edges)', lambda R: 2*np.pi*N_edges),
    ('|H|T / (pi N_nodes)', lambda R: np.pi*N_nodes),
    ('|H|T / (pi N_edges)', lambda R: np.pi*N_edges),
    ('|H|T / (N_nodes^2)', lambda R: N_nodes**2),
    ('|H|T / (N_ring(R))', lambda R: N_ring(R)),
    ('|H|T / (2pi N_ring(R))', lambda R: 2*np.pi*N_ring(R)),
    ('|H|T / (N_nodes * R)', lambda R: N_nodes * R),
    ('|H|T / (2pi * N_nodes * R)', lambda R: 2*np.pi*N_nodes*R),
    ('|H|T / (R^3)', lambda R: R**3),
    ('|H|T / (2pi R^3)', lambda R: 2*np.pi*R**3),
]

results = []
for name, fn in normalizations:
    r = try_normalization(name, fn)
    results.append(r)

# Sort by CV
results.sort(key=lambda x: x['cv_pct'])

print("=" * 80)
print("QNG-CPU-106b: Uniqueness check for hbar_QNG candidate")
print("=" * 80)
print()
print(f"{'Normalization':<40s} {'Mean':>12s} {'CV %':>8s}")
print("-" * 80)
for r in results:
    print(f"{r['name']:<40s} {r['mean']:>12.4e} {r['cv_pct']:>8.2f}")

# Identify universal candidates (CV < 2%)
print()
print("Universal candidates (CV < 2%):")
for r in results:
    if r['cv_pct'] < 2.0:
        print(f"  {r['name']}: mean = {r['mean']:.4e}, CV = {r['cv_pct']:.2f}%")

# Check if hbar = 0.097 specifically appears
print()
print("Candidates near 0.097 (likely hbar_QNG):")
for r in results:
    if 0.05 < r['mean'] < 0.15:
        print(f"  {r['name']}: mean = {r['mean']:.4e}, CV = {r['cv_pct']:.2f}%")

json.dump({'results': results, 'N_nodes': N_nodes, 'N_edges': N_edges},
          open(OUT_DIR / 'unicity_check.json', 'w'), indent=2)
print(f"\nSaved: {OUT_DIR / 'unicity_check.json'}")
