---
test_id: QNG-CPU-149
title: Finite-volume test of knot universality — L scan at L=32, 40
category: structural / topological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-091 (SM ↔ QNG correspondence map)
  - DER-QNG-092 §D and §E (CPU-148 + refinement)
  - CPU-148 (L=20 universality observation)
---

# QNG-CPU-149 — Finite-volume test of knot universality

## Purpose

CPU-148 reported a "universal" half-life ~1044 lu at L=20 for trefoil,
figure-8, and cinquefoil knots under v7 matter coupling. CPU-149 tests
whether this universality is L-independent (genuine QNG prediction) or
a finite-volume artefact.

## Inputs

Same knot constructions, scale, parameters as CPU-148, varied only L:
- L=32 (4.1× nodes vs L=20)
- L=40 (8× nodes vs L=20)

Three knots tested at each L:
- trefoil (T(2,3), KNOT_SCALE=1.8)
- figure_8 (KNOT_SCALE=1.8 × 0.7)
- cinquefoil (T(2,5), KNOT_SCALE=1.8 × 0.6)

Phase 1=300, Phase 2=1500, Phase 3=3000 steps. Same matter coupling
parameters as CPU-148.

## Gates

**G1**: At each L, the within-L spread of half-life across knot types
remains <10% (knot-type universality preserved at each L).

**G2**: Mean half-life at L=32 and L=40 is within 30% of the L=20
baseline of 1044 lu (lifetime L-independence holds).

## Decision

PASS = G1 AND G2.

## Result (2026-05-30)

| L | τ_trefoil | τ_figure_8 | τ_cinquefoil | Mean | Spread within L |
|---|---|---|---|---|---|
| 20 (CPU-148) | 1011 | 1050 | 1070 | 1044 lu | 2.4% |
| 32 | 2105 | 2257 | 2342 | 2235 lu | 4.4% |
| 40 | 2714 | 2925 | 3010 | 2883 lu | 4.3% |

**Gates evaluated**:
- G1: PASS at all L (knot-type universality holds within each L: spread
  4.4% at L=32, 4.3% at L=40)
- G2: **FAIL** — L=32 mean (2235) is 113% above baseline; L=40 mean
  (2883) is 176% above. Significant L-dependence.

**Decision: PARTIAL_FAIL** — G1 holds (knot-type independence
universal), G2 fails (lifetime is L-dependent, not a constant).

## Power-law fit

τ ~ L^p with:
- (L=20, τ=1044), (L=32, τ=2235): p = 1.62
- (L=20, τ=1044), (L=40, τ=2883): p = 1.48
- (L=32, τ=2235), (L=40, τ=2883): p = 1.18

Mean: p ≈ 1.4 ± 0.2

This is sub-quadratic (p < 2) and super-linear (p > 1), consistent with
a diffusive timescale modulated by finite-volume corrections.

## Refined interpretation

The CPU-148 "universal lifetime" claim is FALSIFIED in its strong form.
The original 1044 lu was specific to L=20 finite volume.

REFINED prediction: at each L, the within-L universality across knot
topologies holds (decay rate is topology-independent). But the
ABSOLUTE LIFETIME scales as τ ~ L^1.4 — consistent with diffusive
smearing of phi-disorder into the surrounding lattice volume.

**Crucial implication**: in the L → ∞ continuum limit, τ → ∞. Local
knots are STABLE in continuous QNG, not decaying. The apparent decay
at finite L is a smearing artefact, not a fundamental decay channel.

This is, paradoxically, MORE consistent with SM physics:
- In QNG v7 (no gauge bosons), no particle has a decay channel → all
  stable in continuum, as one would expect for a theory with no W/Z/γ
  to emit
- Real SM lifetimes for unstable particles come from access to
  lighter final states via gauge bosons (weak/EM/strong interactions)
- v12 EM coupling and a future v13 weak interaction should restore
  particle-specific decay channels and spread of lifetimes

## Status update for DER-QNG-092

§D (universal lifetime law) is SUPERSEDED by §E (finite-volume scan +
refined interpretation). The refined claim:

> All local-topology knots are STABLE in the continuum limit of QNG
> v7. Apparent finite-volume lifetime scales as τ ~ L^1.4 and is
> topology-independent within ~5% spread at each fixed L. Real
> SM-like decay channels require v12 EM or higher gauge structure.

## Artifacts

- Report: `07_validation/audits/qng-knot-finite-volume-v1/report.json`
- Test runner: `tests/cpu/qng_knot_finite_volume_reference.py`

## Follow-up tests recommended

- CPU-150: extend L scan to L=48, 56, 64 to confirm power-law
  exponent p≈1.4 and refine the extrapolation
- CPU-151: same test under v12 EM coupling — does adding the gauge
  channel produce topology-dependent decay rates?
- CPU-152: same test under v8 symplectic (no dissipation) — does
  universal smearing disappear without v7 friction?
