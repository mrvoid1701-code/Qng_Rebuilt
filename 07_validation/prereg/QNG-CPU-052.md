# QNG-CPU-052 — GR Coupling Continuum Limit Probe (N=64)

**Status**: LOCKED
**Theory**: DER-BRIDGE-034
**Date**: 2026-03-26
**Depends on**: QNG-CPU-051 (large-N sparse-graph law)

---

## What this test does

Extends the N-scaling probe to N=64, adding a fourth data point to the scaling
curve established by CPU-051. Full run: N ∈ {8, 16, 32, 64} × 5 seeds = 20 runs.

Goal: distinguish between power-law vanishing vs saturation of the QM→GR coupling
constant e_mis as N → ∞ (continuum limit).

Reference from CPU-051:
- N=8:  mean|e_mis|=1.037  mean Δratio=−0.147
- N=16: mean|e_mis|=0.259  mean Δratio=−0.043
- N=32: mean|e_mis|=0.159  mean Δratio=−0.018

Decay rate N=8→16: ×0.25 (steep). Decay rate N=16→32: ×0.61 (slowing).

---

## Pre-registered predictions

| ID | Prediction | Threshold |
|----|-----------|-----------|
| P1 | Δratio_split(N=64) < 0 on ≥ 4/5 seeds | 4/5 |
| P2 | mean\|e_mis(N=64)\| < mean\|e_mis(N=32)\| = 0.159 | — |
| P3 | mean\|e_mis(N=64)\| > 0.050 (non-vanishing) | — |
| P4 | sign(e_mis_ett) consistent across all 4 N values on ≥ 4/5 seeds | 4/5 |

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Saturation classification (post-test)

| |e_mis(N=64)| | Interpretation |
|---|---|
| > 0.120 | Saturation regime — coupling stabilizing |
| 0.050–0.120 | Slow decay — finite continuum limit plausible |
| < 0.050 | Vanishing — UV law only, lattice artifact |

---

## Audit output

- `07_validation/audits/qng-gr-coupling-continuum-limit-reference-v1/report.json`
- `07_validation/audits/qng-gr-coupling-continuum-limit-reference-v1/summary.md`
