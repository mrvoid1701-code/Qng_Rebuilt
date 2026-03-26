# QNG-CPU-060 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-042 (qng-gr-initial-signature-scaling-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-059 (signature buildup/decay), QNG-CPU-052 (continuum N=64)

---

## Question

Is |corr(E_tt,E_xx)| ≈ 1.000 at step 1 a universal property independent of N?
Does the signature decay (Δ = |corr_1| − |corr_24|) decrease with N?

---

## Setup

- N values: {8, 16, 32, 64}
- Seeds: {20260325, 42, 137, 1729, 2718}
- Steps tracked: 1 and 24 (with history)
- Metric: assemble_linearized_metric + tensorial_proxy

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | mean\|corr_1\| > 0.95 at each N | All 4 N values |
| P2 | mean\|corr_1\| > mean\|corr_24\| at each N | All 4 N values |
| P3 | mean Δ decreases N=8→64 | Δ(N=64) < Δ(N=8) |
| P4 | \|corr_1\| > 0.90 on ≥ 4/5 seeds at N=64 | ≥ 4/5 seeds |

---

## Expected outcomes

- P1: likely PASS — CPU-059 showed 0.999 at N=12; structural property expected
- P2: likely PASS — CPU-059 confirmed this at N=12
- P3: UNCERTAIN — depends on rollout dynamics at large N
- P4: likely PASS if P1 holds

---

## Audit output

- `07_validation/audits/qng-gr-initial-signature-scaling-reference-v1/report.json`
- `07_validation/audits/qng-gr-initial-signature-scaling-reference-v1/summary.md`
