# QNG-CPU-061 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-043 (qng-gr-history-signature-preservation-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-060, QNG-CPU-059

---

## Question

How does the Lorentzian signature decay differ between history-on and history-off
rollouts across N = {8, 16, 32, 64}? What is the no-history decay power law?

---

## Setup

- N values: {8, 16, 32, 64}
- Seeds: {20260325, 42, 137, 1729, 2718}
- Steps: 24 (with and without history)
- Metric: |corr(E_tt, E_xx)| at step 1 and step 24

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | decay_nohist > decay_hist at each N | All 4 N values |
| P2 | \|corr_24_hist\| > \|corr_24_nohist\| at each N | All 4 N values |
| P3 | Δ_nohist follows power law (R² > 0.9 across N) | Single fit |
| P4 | benefit = decay_nohist − decay_hist consistent sign on ≥ 4/5 seeds at N=32 | ≥ 4/5 seeds |

---

## Expected outcomes

- P1/P2: PASS — CPU-059 showed this at N=12; expected to hold across N
- P3: UNCERTAIN — depends on no-history dynamics at large N
- P4: PASS — history benefit should be seed-consistent

---

## Audit output

- `07_validation/audits/qng-gr-history-signature-preservation-reference-v1/report.json`
- `07_validation/audits/qng-gr-history-signature-preservation-reference-v1/summary.md`
