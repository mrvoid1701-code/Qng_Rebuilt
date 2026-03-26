# QNG-CPU-050 — GR Coupling Covariance (Multi-Seed)

**Status**: LOCKED
**Theory**: DER-BRIDGE-032
**Date**: 2026-03-26
**Depends on**: QNG-CPU-049 (6-channel GR fit), QNG-CPU-046 (multi-channel continuity)

---

## What this test does

Runs the 6-channel GR tensor fitting (E_xx, E_tt) from CPU-049 across 5 seeds
to determine whether the QM→GR coupling coefficients (e_mis, f_mem) are
Tier-1 universal or Tier-2 topology-dependent.

Seeds: [20260325, 42, 137, 1729, 2718]

For each seed, computes:
- 4-channel baseline ratio (κ, q_src, src, m_eff)
- 6-channel extended ratio (+ div_J_mis, div_J_mem)
- Coupling coefficients: e_mis, f_mem in E_tt and E_xx fits
- Dominance: |e_mis| vs |f_mem|

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | 6-channel beats 4-channel (Δratio_split < 0) on ≥ 4/5 seeds | 4/5 |
| P2 | \|e_mis_ett\| > \|f_mem_ett\| on ≥ 4/5 seeds | 4/5 |
| P3 | sign(e_mis_ett) consistent on ≥ 4/5 seeds | 4/5 |
| P4 | max(\|e_mis\|,\|f_mem\|) > 0.1·\|a_geom\| on ≥ 3/5 seeds | 3/5 |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Tier classification (post-test)

- P1 + P3 both pass → Tier-1 (coupling is universal)
- P1 pass, P3 fail → Tier-1.5 (improvement universal, sign varies)
- P1 fail → Tier-2 (topology-dependent)

---

## Expected results (theory prediction)

Since div_J_mis is a local operator (node neighborhood), the coupling should be:
- P1: PASS (6-channel always better by OLS monotonicity — each new column can only help)
- P2: PASS (mismatch dominance established in CPU-046 for most seeds)
- P3: PASS (sign determined by energy-density physical coupling, not topology)
- P4: PARTIAL (some seeds may have |e_mis| < 10% threshold depending on geometry scale)

---

## Audit output

- `07_validation/audits/qng-gr-coupling-covariance-reference-v1/report.json`
- `07_validation/audits/qng-gr-coupling-covariance-reference-v1/summary.md`
