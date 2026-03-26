# QNG-CPU-054 — GR→QM Back-Reaction Coupling Large-N Probe

**Status**: LOCKED
**Theory**: DER-BRIDGE-036
**Date**: 2026-03-26
**Depends on**: QNG-CPU-053 (back-reaction loop), QNG-CPU-052 (e_mis saturation)

---

## What this test does

Tests whether the GR→QM coupling γ_tt (from CPU-053) follows the sparse-graph
N-attenuation law established for e_mis (CPU-051/052).

N_VALUES: [8, 16, 32] × 5 seeds = 15 runs.

For each (N, seed): 3-channel QM baseline vs 4-channel (+E_tt) fit.
Measures: R² improvement, γ_tt value and sign.

Also computes loop_strength(N) = mean|γ_tt| × mean|e_mis| at each N
to assess whether the back-reaction loop survives in the continuum.

Reference (CPU-053, N=16): mean γ_tt ≈ +0.005, 5/5 signs positive.

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | R²(3ch+E_tt) > R²(3ch) at N=32 on ≥ 4/5 seeds | 4/5 |
| P2 | mean γ_tt(N=32) < mean γ_tt(N=8) on ≥ 3/5 seeds | 3/5 |
| P3 | sign(γ_tt) consistent across all 3 N values on ≥ 4/5 seeds | 4/5 |
| P4 | mean γ_tt(N=32) > 0.001 (non-vanishing) | — |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Audit output

- `07_validation/audits/qng-gr-backreaction-large-n-reference-v1/report.json`
- `07_validation/audits/qng-gr-backreaction-large-n-reference-v1/summary.md`
