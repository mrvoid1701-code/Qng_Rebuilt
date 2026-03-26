# QNG-CPU-062 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-044 (qng-gr-n32-transition-mechanism-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-061, QNG-CPU-051, QNG-CPU-052

---

## Question

What is the mechanism behind the N=32 cross-sector transition? Specifically, does
phi synchronization velocity (early Kuramoto slope, no-history) peak at N=32,
thereby explaining the signature collapse anomaly seen in CPU-061?

---

## Setup

- N values: {8, 16, 32, 64}
- Seeds: {20260325, 42, 137, 1729, 2718}
- Steps for phi trajectory: 24 (without history only)
- Sync velocity: linear slope of kuramoto order r(t) over steps 1..12
- Graph metrics: mean_degree k̄, degree_cv, clustering C, mean_path_length L

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | v_sync (no-history) peaks at N=32 on ≥ 4/5 seeds | ≥ 4/5 seeds |
| P2 | mean_degree k̄ increases monotonically with N | All 4 N values |
| P3 | clustering C is non-monotone with N (changes character) | Non-monotone |
| P4 | Pearson(mean v_sync(N), Δ_nohist(N)) > 0.5 across N values | r > 0.5 |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Expected outcomes

- P1: UNCERTAIN — non-monotone sync speed is the central prediction; must be verified
- P2: PASS — ER graph with fixed p gives k̄ = (N−1)·p; should increase with N
- P3: UNCERTAIN — clustering in ER graphs typically decreases with N (C ~ p/N), but finite-N effects may produce non-monotone behavior
- P4: UNCERTAIN — if v_sync explains Δ_nohist, correlation should be strong

---

## Δ_nohist reference values (from CPU-061)

These are the per-N no-history decay values that P4 will correlate against:

| N  | Δ_nohist (mean across seeds) |
|----|------------------------------|
| 8  | ~0.225                       |
| 16 | ~0.232                       |
| 32 | ~0.371 (peak)                |
| 64 | ~0.280                       |

---

## Audit output

- `07_validation/audits/qng-gr-n32-transition-mechanism-reference-v1/report.json`
- `07_validation/audits/qng-gr-n32-transition-mechanism-reference-v1/summary.md`
