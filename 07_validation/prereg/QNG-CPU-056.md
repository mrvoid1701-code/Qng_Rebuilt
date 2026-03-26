# QNG-CPU-056 Pre-Registration

**Status**: LOCKED
**Theory doc**: DER-BRIDGE-038 (qng-gr-attractor-geometry-v1.md)
**Date locked**: 2026-03-26
**Depends on**: QNG-CPU-055 (fixed-point iteration), QNG-CPU-054 (γ_tt large-N)

---

## Question

What is the spatial structure of the QNG back-reaction attractor?

Specifically:
1. Does ρ*(QM) correlate with node degree (topological structure)?
2. Does δρ = ρ*(GR) − ρ*(QM) correlate with E_tt (gravitational imprint)?
3. Is the sign of the E_tt correlation consistent with γ_tt > 0?
4. Is the GR correction spatially structured (not a uniform shift)?

---

## Setup

- Seeds: {20260325, 42, 137, 1729, 2718}
- N = 12 (default Config)
- Steps = 24 (default Config)
- FP iteration: K=30, η=0.05 (same as CPU-055)
- All coefficients (a_mis, a_mem, g_tt) estimated per seed from two-step rollout

---

## Pass criteria

| ID | Criterion | Threshold |
|----|-----------|-----------|
| P1 | Pearson(ρ*(QM), node_degree) > 0.2 | ≥ 4/5 seeds |
| P2 | \|Pearson(δρ, E_tt)\| > 0.05 | ≥ 4/5 seeds |
| P3 | sign(Pearson(δρ, E_tt)) = sign(γ_tt) | ≥ 4/5 seeds |
| P4 | std(δρ) / mean(\|δρ\|) > 0.1 | ≥ 4/5 seeds |

---

## Expected outcomes (pre-registration)

Based on the theory (DER-BRIDGE-038):

- P1 PASS: rollout dynamics favor high-degree nodes (more current sources)
- P2 PASS: γ_tt·E_tt is the GR back-reaction driver; δρ should follow it spatially
- P3 PASS: γ_tt > 0 on all seeds (CPU-053/054); correlation sign should match
- P4 PASS: E_tt varies across nodes → δρ inherits spatial variation

Risk factors:
- P1: at N=12, degree variation is small (Erdős-Rényi with p≈0.3 gives k ≈ 3–5);
  correlation may be noisy
- P2/P3: δρ ≈ 0.001 — may be at noise floor; seeds with small γ_tt may fail
- P4: if γ_tt × E_tt is nearly uniform across nodes, ratio may be small

---

## Audit output

Test will write:
- `07_validation/audits/qng-gr-attractor-geometry-reference-v1/report.json`
- `07_validation/audits/qng-gr-attractor-geometry-reference-v1/summary.md`
