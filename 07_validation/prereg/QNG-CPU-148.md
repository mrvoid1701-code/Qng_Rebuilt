---
test_id: QNG-CPU-148
title: Knot universality — figure-8 and cinquefoil decay rates vs trefoil
category: structural / topological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-091 (SM ↔ QNG correspondence map)
  - DER-QNG-092 §A (CPU-146 universality conjecture)
  - CPU-145 (pure-phi knot scan baseline)
  - CPU-146 (matter-coupled knot scan, original universality observation)
---

# QNG-CPU-148 — Knot universality test

## Purpose

CPU-146 observed that ring (no winding) and trefoil knot (3 crossings)
have NEARLY IDENTICAL decay rates (~0.873 per 200 lu, half-life ~1000 lu)
under full v7 matter coupling. This raised the question:

> Is the decay rate of "local-topology" knots (those without
> toroidal cycle winding) genuinely UNIVERSAL across knot types?

CPU-148 tests this by extending to two further knot classes:
- Figure-8 knot (4 crossings, twist class 4_1)
- Cinquefoil = T(2,5) torus knot (5 crossings)

If both have decay rate ≈ 0.87 and half-life ≈ 1000 lu, the
universality conjecture is confirmed and becomes a candidate **QNG
prediction** of a topology-independent lifetime for the unstable-particle
class.

## Inputs

L=20 lattice, full v7 parameters identical to CPU-146 for direct
comparison:
- BETA_PHI=0.02, GAMMA_PHI=0.10, CHI_DECAY=0.020, K_BACK=0.10

Three knot initial configurations, all built by the same algorithm
(transverse-frame phi-winding around a closed curve):
1. **trefoil** (T(2,3) torus knot): r(t) = s·(sin t + 2 sin 2t,
   cos t − 2 cos 2t, −sin 3t), s=1.8
2. **figure_8**: r(t) = s·((2+cos 2t) cos 3t, (2+cos 2t) sin 3t,
   sin 4t), s=1.26
3. **cinquefoil** (T(2,5) torus knot): r(t) = ((R+r cos 5t) cos 2t,
   (R+r cos 5t) sin 2t, r sin 5t), R=2.7, r=1.08

Three-phase protocol: P1=300, P2=1500, P3=3000 steps.

## Outputs

Per configuration:
- M_ring(t) trace through all three phases
- Mean decay ratio per 200 lu during Phase 3
- Inferred half-life in lu

## Gates and tolerances

**G1**: All three knots form M_ring > 200 at Phase 2 end.

**G2 (universality)**: relative spread (std/mean) of decay ratio across
the three configurations < 10%.

**G3 (baseline match)**: mean half-life within 30% of CPU-146 trefoil
baseline of ~1000 lu.

## Decision criterion

PASS = G1 AND G2 AND G3. Failure of G2 means topology-dependent
lifetime (KBT spirit returns). Failure of G3 means decay rates depend
on initial knot construction scale (artifact, not physics).

## Result (2026-05-30)

| Config | M_P2_end | M_P3_end | decay ratio / 200 lu | half-life (lu) |
|---|---|---|---|---|
| trefoil | 556.18 | 70.32 | 0.8718 | 1011 |
| figure_8 | 298.23 | 40.94 | 0.8763 | 1050 |
| cinquefoil | 348.74 | 49.90 | 0.8785 | 1070 |

**Mean decay ratio**: 0.8755 ± 0.0028 (relative spread 0.32%)
**Mean half-life**: 1044 ± 25 lu (relative spread 2.4%)

**Gates evaluated**:
- G1: PASS — all M_P2_end > 200
- G2: PASS — rel spread 0.32% << 10%
- G3: PASS — 1044 lu within 5% of 1000 lu baseline

**Decision: PASS_DECISIVE**

## Interpretation

The three knot types — trefoil (3 crossings), figure-8 (4 crossings),
cinquefoil (5 crossings) — have decay rates that agree to 0.3% and
half-lives that agree to 2.4%. The differences are at the level of
finite-volume / lattice-discretization noise, not topology.

**This is a clean QNG prediction**:

> **All local-topology knots in QNG share a universal decay rate
> determined by substrate parameters β_φ and GAMMA_PHI alone, not by
> knot type.**

Combined with CPU-146 (ring also has same rate):

> The QNG "unstable particle class" — all configurations without
> toroidal cycle winding — has a SINGLE characteristic lifetime
> τ_1/2 ≈ 1044 lu under canonical v7 dynamics. Knot topology has
> NO effect on lifetime.

Stable particle class: only Hopfion family (toroidal cycle winding
protected by periodic BC) lives indefinitely.

## Comparison to SM

In SM, unstable particles have dramatically different lifetimes:
- π⁰: 8.4×10⁻¹⁷ s
- π±: 2.6×10⁻⁸ s
- μ: 2.2×10⁻⁶ s
- τ: 2.9×10⁻¹³ s
- n: 880 s
- top quark: 5×10⁻²⁵ s

Each lifetime is set by specific decay channels and couplings, NOT by
a universal substrate rate.

**QNG predicts the opposite**: in the local-knot sector, all unstable
particles share ONE lifetime, set by the topology-relaxation rate of
the phi field under matter coupling. If true experimentally, this would
falsify QNG immediately (e.g., π and μ should have same lifetime, but
they don't).

The prediction must therefore be reinterpreted in one of three ways:

1. **The unstable-knot class corresponds to ONE specific SM particle**
   (perhaps a resonance with τ ~ 1044 lu in physical units).
   Different knot complexities then correspond to different MASSES of
   the same resonance class.

2. **The universal τ holds for a specific topological subclass** —
   knot complexity matters via OTHER mechanisms (decay channels,
   couplings) not captured in pure v7 dynamics. v8 symplectic
   evolution may break universality.

3. **The universality is an L=20 artifact**. At larger L or with v13
   structure, topology might re-enter as a tiebreaker.

Testing direction (3) — larger L — is the cheapest immediate
diagnostic. CPU-149 should re-run at L=32 or L=40.

## Artifacts

- Report: `07_validation/audits/qng-knot-universality-v1/report.json`
- Summary: `07_validation/audits/qng-knot-universality-v1/summary.md`
- Test runner: `tests/cpu/qng_knot_universality_reference.py`

## Follow-up tests recommended

- CPU-149: same test at L=32, L=40 to check if universality survives
  larger lattice (rules out finite-volume artefact)
- CPU-150: same test under v8 symplectic dynamics (no dissipation)
  to check if universality is a dissipation artefact
- CPU-151: measure decay PRODUCTS — what carries off mass during knot
  decay? If all knots decay to same vacuum + same phi-wave pulse,
  topology really is invisible to decay channel.
