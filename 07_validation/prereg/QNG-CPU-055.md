# QNG-CPU-055 — Back-Reaction Fixed-Point Iteration

**Status**: LOCKED
**Theory**: DER-BRIDGE-037
**Date**: 2026-03-26
**Depends on**: QNG-CPU-053, QNG-CPU-054

---

## What this test does

Iterates the back-reaction equation from the final rollout state, testing
whether the QM↔GR system converges to a non-trivial fixed point ρ*.

Two iterations compared per seed:
- QM-only: ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis + α_mem·dJ_mem))
- QM+GR:   ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis + α_mem·dJ_mem) + γ_tt·E_tt)

Coefficients (α_mis, α_mem, γ_tt) estimated from the same seed's rollout data.
Step size η = 0.05, K = 30 iterations, phi held fixed.

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | QM-only ||Δρ|| decreases k=0→29 on ≥ 4/5 seeds | 4/5 |
| P2 | QM+GR ||Δρ|| decreases on ≥ 4/5 seeds | 4/5 |
| P3 | ||ρ*_QM+GR − ρ*_QM|| > 0.001 on ≥ 3/5 seeds | 3/5 |
| P4 | ||Δρ_29||_QM+GR < ||Δρ_29||_QM on ≥ 3/5 seeds | 3/5 |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Audit output

- `07_validation/audits/qng-gr-backreaction-fixedpoint-reference-v1/report.json`
- `07_validation/audits/qng-gr-backreaction-fixedpoint-reference-v1/summary.md`
