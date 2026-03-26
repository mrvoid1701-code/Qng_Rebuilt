# QNG-CPU-058 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-040 (qng-gr-metric-signature-correction-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-057, QNG-CPU-056, QNG-CPU-033

---

## Question

Does the GR back-reaction correction ρ*(QM) → ρ*(QM+GR) shift the assembled
metric components E_tt and E_xx in the direction of stronger Lorentzian signature
(more negative h_tt, more positive h_xx)?

Baseline (CPU-033): h_tt ≈ −0.009, h_xx ≈ +0.014, corr ≈ −0.97 at rollout state.

---

## Setup

- Seeds: {20260325, 42, 137, 1729, 2718}
- N = 12, Steps = 24 (default Config)
- K = 30, η = 0.05 (standard FP iteration)
- phi fixed at rollout final state for all metric computations
- QM attractor: K iterations without GR term
- GR attractor: K iterations with γ_tt·E_tt term (self-consistent, from CPU-057)

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | sign(ΔE_tt) consistent across seeds | ≥ 4/5 seeds have same sign |
| P2 | sign(ΔE_xx) consistent across seeds | ≥ 4/5 seeds have same sign |
| P3 | sign(ΔE_tt) ≠ sign(ΔE_xx) | ≥ 4/5 seeds (Lorentzian correction) |
| P4 | \|ΔE_tt\| > 1e-5 | ≥ 4/5 seeds (detectable shift) |

---

## Expected outcomes

- P1: UNCERTAIN — sign depends on ∂h_tt/∂c, not known analytically
- P2: UNCERTAIN — same reason
- P3: Hypothesized PASS if back-reaction is Lorentzian-enhancing
- P4: Expected PASS — CPU-057 showed E_tt_drift ≈ 13%; mean shift should be detectable

The test is designed to be genuinely unpredictable. Any of P1–P3 failing provides
equally useful information about the structure of QNG geometry.

---

## Audit output

- `07_validation/audits/qng-gr-metric-signature-correction-reference-v1/report.json`
- `07_validation/audits/qng-gr-metric-signature-correction-reference-v1/summary.md`
