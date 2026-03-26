# QNG-CPU-057 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-039 (qng-gr-selfconsistent-backreaction-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-056 (attractor geometry), QNG-CPU-055 (fixed-point)

---

## Question

CPU-056 found δρ ∝ E_tt with |Pearson| > 0.99. But E_tt was held fixed during
the FP iteration (linear approximation). What happens when E_tt is re-evaluated
at every step (self-consistent nonlinear iteration)?

---

## Setup

- Seeds: {20260325, 42, 137, 1729, 2718}
- N = 12, Steps = 24 (default Config)
- K = 30, η = 0.05 (same as CPU-055/056)
- Coefficients (a_mis, a_mem, g_tt) estimated per seed from two-step rollout
- QM-only FP run once → ρ*_QM (reference, same as CPU-056)
- Linear GR run: E_tt computed once → ρ*_lin
- Self-consistent GR run: E_tt re-evaluated each step → ρ*_sc

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | δ_norms decreasing in self-consistent run | ≥ 4/5 seeds |
| P2 | \|\|ρ*_sc − ρ*_lin\|\|₂ < 0.005 | ≥ 4/5 seeds |
| P3 | \|Pearson(δρ_sc, E_tt_final)\| > 0.5 | ≥ 4/5 seeds |
| P4 | E_tt_drift > 0.001 (relative change in E_tt_0→E_tt_final) | ≥ 3/5 seeds |

---

## Expected outcomes

- P1 PASS: small γ_tt perturbation unlikely to destabilize QM attractor
- P2 PASS: fp_shift ≈ 0.001 implies E_tt changes by < 1% → linear ≈ nonlinear
- P3 PASS: E_tt direction dominates even in nonlinear regime
- P4 UNCERTAIN: E_tt drift may be negligibly small (< 0.001) if fp_shift tiny;
  or measurably above 0.001 for seeds with larger γ_tt (1729, 2718)

---

## Audit output

- `07_validation/audits/qng-gr-selfconsistent-backreaction-reference-v1/report.json`
- `07_validation/audits/qng-gr-selfconsistent-backreaction-reference-v1/summary.md`
