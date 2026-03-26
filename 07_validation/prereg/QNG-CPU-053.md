# QNG-CPU-053 — QM↔GR Back-Reaction Loop Closure

**Status**: LOCKED
**Theory**: DER-BRIDGE-035
**Date**: 2026-03-26
**Depends on**: QNG-CPU-046 (QM continuity), QNG-CPU-052 (GR coupling saturates)

---

## What this test does

Tests whether the GR tensor E_tt (established as the primary QM→GR output)
feeds back into QM density evolution ∂_t(C_eff²) — closing the QM↔GR loop.

Uses the same `rollout_two_steps` structure as CPU-046:
1. Run rollout to step t (steps-1 iterations)
2. Capture state at t: c_t, phi_t, mismatch_t, mem_t
3. Run one more step → get c_{t+1}
4. Compute: drho_i = c_{t+1,i}² - c_{t,i}²
5. Compute QM channels at t: dj_phi, dj_mis, dj_mem
6. Compute GR tensor at t: E_tt, E_xx from assemble_linearized_metric(c_t, phi_t)
7. Compare: 3-channel (QM only) vs 5-channel (QM + E_tt + E_xx) fits

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | R²(3ch + E_tt) > R²(3ch) on ≥ 4/5 seeds | 4/5 |
| P2 | sign(γ_tt) consistent on ≥ 4/5 seeds | 4/5 |
| P3 | R²(3ch + E_tt) > R²(3ch + E_xx) on ≥ 3/5 seeds | 3/5 |
| P4 | mean(R²_5ch − R²_3ch) > 0.010 | — |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Tier classification

- P1 + P2 pass → Tier-1 (universal back-reaction, loop closes)
- P1 pass, P2 fail → Tier-2 (topology-dependent)
- P1 fail → no back-reaction signal detected

---

## Audit output

- `07_validation/audits/qng-gr-backreaction-loop-reference-v1/report.json`
- `07_validation/audits/qng-gr-backreaction-loop-reference-v1/summary.md`
