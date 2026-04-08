# QNG-CPU-066

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — topological stability comparison in v7

## Purpose

DER-QNG-036 shows that the (sigma_m, phi) pair in v7 already supports Hopf topology
(pi_3(S²) = Z) without new fields. The Q=1 Hopfion is initialized with an extra
toroidal twist: phi = atan2(z, rho-R) + atan2(y, x).

This test compares:
- Standard ring (Q=0): phi = atan2(z, rho-R)
- Hopfion (Q=1):      phi = atan2(z, rho-R) + atan2(y, x)

Key question: does the Hopfion survive longer in conservative dynamics (no Channel F,
no Channel G, no CHI_DECAY) where the standard ring dissolves in 50 steps (CPU-059)?

## Checks

**Check 1 — Hopfion survives Phase 2 dissipative:**
M_hopfion(T=1000) > 50 in normal v7 dynamics (Channel F + G active).
Gate: M > 50.

**Check 2 — Hopfion outlasts ring in conservative dynamics:**
Run both with NO dissipation (no Channel F, no Channel A, no CHI_DECAY).
M_hopfion(T=100) > M_ring(T=100).
Gate: M_hopfion > M_ring at T=100 conservative steps.

**Check 3 — Bipolar chi structure:**
chi_north = mean chi in z > center+3 region
chi_south = mean chi in z < center-3 region
Both should be non-zero with opposite sign or same sign but spatially separated.
Gate: |chi_north| > 2 * chi_rms_bulk  OR  |chi_south| > 2 * chi_rms_bulk.

**Check 4 — Energy higher than ring:**
E_hopfion(T=1000) > E_ring(T=1000).
Gate: E_hopfion > E_ring (Hopfion has more topological content → more energy).

## Decision rule

PASS if Checks 1 and 2 pass. Checks 3 and 4 informational.

## Artifact paths

- `07_validation/audits/qng-hopfion-v1/report.json`
- `07_validation/audits/qng-hopfion-v1/summary.md`
