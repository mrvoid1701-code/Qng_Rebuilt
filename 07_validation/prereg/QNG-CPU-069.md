# QNG-CPU-069

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — 100,000 step conservative run (GPU)

## Purpose

CPU-068 ran 15,000 steps = 17.5% of corrected diffusion timescale
(tau_ring = R² × 6 / (BETA × DT) ≈ 86,000 steps). Both structures showed
near-zero mass loss (ring 99.98%, Hopfion 100.00%).

This test runs 100,000 conservative steps (≈ 1.16× corrected tau_ring) to
determine whether dissolution eventually occurs at the true diffusion timescale.

## Upstream

- QNG-CPU-068: PASS — both stable at 15k steps; corrected tau_ring ≈ 86,000 steps

## Checks

**Check 1 — Any dissolution at T=100,000 (informational):**
M(T=100000) < 0.99 × M0.

**Check 2 — Half-life comparison:**
T_half(hopfion) >= T_half(ring) (50% threshold). If neither dissolves: tie → PASS.

## Decision rule

PASS if Check 2 passes.

## Artifact paths

- `07_validation/audits/qng-hopfion-100k-v1/report.json`
- `07_validation/audits/qng-hopfion-100k-v1/summary.md`
