# QNG-CPU-051 — GR 6-Channel Coupling Large-N Probe

**Status**: LOCKED
**Theory**: DER-BRIDGE-033
**Date**: 2026-03-26
**Depends on**: QNG-CPU-050 (Tier-1 coupling covariance), QNG-CPU-047 (sparse-graph law)

---

## What this test does

Runs the 6-channel GR tensor fitting (E_xx, E_tt) from CPU-050 across 3 values of N
(8, 16, 32) and 5 seeds — same structure as CPU-047's large-N probe.

Goal: determine whether the sparse-graph law (R² weakens with N) that governs the
QM continuity sector also applies to the GR coupling coefficients (e_mis, f_mem).

N_VALUES: [8, 16, 32]
Seeds: [20260325, 42, 137, 1729, 2718]
Total runs: 15

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | 6-ch beats 4-ch (Δratio_split < 0) on ≥ 4/5 seeds at N=32 | 4/5 |
| P2 | \|e_mis_ett(N=32)\| < \|e_mis_ett(N=8)\| on ≥ 3/5 seeds | 3/5 |
| P3 | sign(e_mis_ett) consistent across all 3 N values on ≥ 4/5 seeds | 4/5 |
| P4 | \|mean Δratio_split(N=32)\| < \|mean Δratio_split(N=8)\| (improvement shrinks with N) | — |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Tier classification (post-test)

- P1 + P3 pass → Tier-1 large-N (coupling universal across N and topology)
- P1 pass, P3 fail → Tier-1.5 (improvement persists but sign N-dependent)
- P1 fail → Tier-2 (coupling collapses at N=32)

---

## Expected results

Based on CPU-047 sparse-graph law:
- P1: PASS (OLS monotonicity + non-zero div_J signal at all N)
- P2: PASS (sparser graphs → stronger local divergence signals → larger |e_mis|)
- P3: PASS (sign of coupling is physical, not scale-dependent)
- P4: PASS (amplitude decreases with N, consistent with sparse-graph law)

---

## Audit output

- `07_validation/audits/qng-gr-coupling-large-n-reference-v1/report.json`
- `07_validation/audits/qng-gr-coupling-large-n-reference-v1/summary.md`
