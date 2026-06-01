"""QNG-CPU-126 -- M_ring RATIO L-dependence test.

Critical finding from CPU-125: M_ring at L=28 differs from L=20 by ~50%.
Question: do RATIOS M(R)/M(R=4) — supposedly the "structural" prediction
of DER-QNG-038 — also depend on L?

If RATIOS are L-dependent: DER-QNG-038's <2% match with hadron ratios
at L=20 was a FINITE-SIZE COINCIDENCE.

Compute:
  - L=20: known data (CPU-074/075)
  - L=28: from CPU-125 + repeat for R=3, 5, 6, 7
  - Compare with hadron ratios

The hadron pattern is N(938), Delta(1232), N*(1520), Delta'(1700):
  m(Delta)/m(N) = 1.313
  m(N*)/m(N)   = 1.620
  m(Delta')/m(N) = 1.812
"""
import numpy as np

# Data from CPU-074/075 (L=20)
M_L20 = {
    3: 474.15,
    4: 728.92,
    5: 954.88,
    6: 1172.13,
    7: 1328.10,
}

# Data from CPU-125 (L=28, just measured)
M_L28 = {
    3: 846.39,
    4: 1136.08,
    5: 1400.39,
    6: 1678.38,
    7: 1913.23,
    8: 2133.07,
    9: 2328.69,
    10: 2479.86,
}

# Hadron mass ratios
hadron = {
    3: ('?',         None),
    4: ('N(938)',    938.272),
    5: ('Delta(1232)', 1232.0),
    6: ('N*(1520)',  1520.0),
    7: ('Delta(1700)', 1700.0),
    8: ('N(1875)',   1875.0),
    9: ('Delta(1905)', 1905.0),
    10: ('N(1990)',  1990.0),
}

print("=" * 90)
print("QNG-CPU-126: M_ring ratio L-dependence test")
print("=" * 90)
print()

print("Data summary:")
print(f"{'R':>4} {'M(L=20)':>10} {'M(L=28)':>10} {'L28/L20':>10}")
print("-" * 50)
for R in sorted(set(M_L20.keys()) | set(M_L28.keys())):
    m20 = M_L20.get(R, None)
    m28 = M_L28.get(R, None)
    if m20 and m28:
        print(f"{R:>4} {m20:>10.2f} {m28:>10.2f} {m28/m20:>10.4f}")
    elif m28:
        print(f"{R:>4} {'-':>10} {m28:>10.2f} {'-':>10}")
print()

# ============================================================
# RATIO ANALYSIS
# ============================================================
print("=" * 90)
print("Ratio M(R)/M(R=4) at each L vs observed hadron mass ratio")
print("=" * 90)
print()

print(f"{'R':>4} {'particle':>15} {'m_PDG/m_N':>12} {'L20: M(R)/M(R=4)':>18} {'(% off)':>10} {'L28: M(R)/M(R=4)':>18} {'(% off)':>10}")
print("-" * 100)

for R in sorted(set(M_L20.keys()) | set(M_L28.keys())):
    name, mass = hadron.get(R, ('?', None))
    if mass:
        obs_ratio = mass / 938.272
        m20 = M_L20.get(R)
        m28 = M_L28.get(R)
        ratio_20 = m20 / M_L20[4] if m20 else None
        ratio_28 = m28 / M_L28[4] if m28 else None
        off_20 = (ratio_20 - obs_ratio)/obs_ratio * 100 if ratio_20 else None
        off_28 = (ratio_28 - obs_ratio)/obs_ratio * 100 if ratio_28 else None
        s_20 = f"{ratio_20:.4f}" if ratio_20 else "-"
        s_28 = f"{ratio_28:.4f}" if ratio_28 else "-"
        s_off_20 = f"{off_20:+.1f}%" if off_20 is not None else "-"
        s_off_28 = f"{off_28:+.1f}%" if off_28 is not None else "-"
        print(f"{R:>4} {name:>15} {obs_ratio:>12.4f} {s_20:>18} {s_off_20:>10} {s_28:>18} {s_off_28:>10}")
    else:
        m20 = M_L20.get(R)
        m28 = M_L28.get(R)
        ratio_20 = m20 / M_L20[4] if m20 else None
        ratio_28 = m28 / M_L28[4] if m28 else None
        s_20 = f"{ratio_20:.4f}" if ratio_20 else "-"
        s_28 = f"{ratio_28:.4f}" if ratio_28 else "-"
        print(f"{R:>4} {name:>15} {'-':>12} {s_20:>18} {'-':>10} {s_28:>18} {'-':>10}")

print()

# ============================================================
# Critical comparison: L=20 vs L=28 ratios
# ============================================================
print("=" * 90)
print("CRITICAL: Compare L=20 to L=28 ratio match quality")
print("=" * 90)
print()

# Compute average % deviation for each L
devs_20 = []
devs_28 = []
for R in [5, 6, 7]:
    name, mass = hadron[R]
    obs = mass / 938.272
    if R in M_L20:
        r20 = M_L20[R] / M_L20[4]
        devs_20.append(abs(r20 - obs) / obs * 100)
    if R in M_L28:
        r28 = M_L28[R] / M_L28[4]
        devs_28.append(abs(r28 - obs) / obs * 100)

print(f"L=20 mean |deviation| (R=5,6,7): {np.mean(devs_20):.2f}% (max {max(devs_20):.2f}%)")
print(f"L=28 mean |deviation| (R=5,6,7): {np.mean(devs_28):.2f}% (max {max(devs_28):.2f}%)")
print()

if np.mean(devs_28) > 3 * np.mean(devs_20):
    verdict = "CONFIRMED: L=20 match was finite-size COINCIDENCE"
    print(f"=> {verdict}")
    print(f"   At L=28, deviations are {np.mean(devs_28)/np.mean(devs_20):.1f}x larger.")
    print(f"   DER-QNG-038 baryon ladder is L-DEPENDENT, not structural.")
elif np.mean(devs_28) < 1.5 * np.mean(devs_20):
    verdict = "Pattern PRESERVED at L=28 — could be structural"
    print(f"=> {verdict}")
else:
    verdict = "Intermediate — needs more L values"
    print(f"=> {verdict}")
print()

# ============================================================
# Per-R growth analysis at L=28
# ============================================================
print("=" * 90)
print("Per-R growth at L=28 (slope check):")
print("=" * 90)
print()

R_arr = np.array(sorted(M_L28.keys()))
M_arr = np.array([M_L28[r] for r in R_arr])
slope, intercept = np.polyfit(R_arr, M_arr, 1)
print(f"Linear fit M(R) = {slope:.2f} * R + {intercept:.2f}")

# Residuals
resids = M_arr - (slope*R_arr + intercept)
for R, M, res in zip(R_arr, M_arr, resids):
    print(f"  R={R}: M={M:.2f}, fit={slope*R+intercept:.2f}, residual={res:+.2f}")
print()

# Check if growth saturates at high R (suggesting box size limit)
diffs = np.diff(M_arr)
Rs_diff = R_arr[1:]
print("Per-step growth M(R+1) - M(R):")
for R, d in zip(Rs_diff, diffs):
    print(f"  R={R-1} -> R={R}: dM = {d:.2f}")
print()
if diffs[-1] < diffs[0] * 0.5:
    print("=> Growth is SATURATING — finite-size (box) effect kicks in at high R.")
elif abs(diffs[-1] - diffs[0]) / diffs[0] < 0.2:
    print("=> Growth is approximately CONSTANT — quasi-linear pattern.")
else:
    print("=> Growth is variable — non-trivial structure.")

print()
print("=" * 90)
print("VERDICT")
print("=" * 90)
print()
print(f"L=20 match with hadron ratios: ~{np.mean(devs_20):.1f}% (claimed <2% in DER-QNG-038)")
print(f"L=28 match with hadron ratios: ~{np.mean(devs_28):.1f}%")
print()
print(f"Verdict: {verdict}")
print()
if "COINCIDENCE" in verdict:
    print("RECOMMENDATION:")
    print("  - Retract DER-QNG-038 baryon-ladder absolute mass identification.")
    print("  - The R-progression in M_ring is a real geometric pattern (M ~ R linear).")
    print("  - But identification with specific hadron resonances was a")
    print("    LATTICE-SIZE-DEPENDENT FIT, not a substrate prediction.")
    print("  - Phase C particle identification cannot proceed via M_ring.")
    print("  - Need genuinely new approach to particle identification in QNG.")
