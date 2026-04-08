# QNG-CPU-067

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — long conservative run (1000 steps)

## Purpose

CPU-066 showed both structures stable for 150 conservative steps (total time 0.75
substrate units). The diffusion timescale for R=5 is tau_diff ~ R²/BETA ~ 71 steps
x DT=0.005 = 0.35 units — so 150 steps may be insufficient to see dissolution.

This test runs 1000 conservative steps (total time 5.0 units, ~14x diffusion timescale)
to determine whether:
1. Both structures dissolve (topological protection insufficient without Skyrme term)
2. Hopfion dissolves slower than ring (partial topological protection)
3. Neither dissolves (Hopfion AND ring are true conservative solitons in v7)

## Upstream

- DER-QNG-036: Hopfion topology in v7
- QNG-CPU-066: PASS — Hopfion 1.87x heavier, both stable at 150 steps

## Experimental design

- Start from fully formed dissipative state (Phase1=300 + Phase2=1000 dissipative)
- Switch to conservative dynamics: no Channel A, no Channel F, no CHI_DECAY
- Run 1000 conservative steps at DT=0.005
- Record M(t) every 50 steps for both structures

## Checks

**Check 1 — Hopfion half-life > ring half-life:**
Define T_half = first t where M(t) < M(0)/2.
Gate: T_half(hopfion) > T_half(ring).

**Check 2 — Hopfion retains >50% mass at T=500 conservative:**
M_hopfion(T=500) > M_hopfion(0) * 0.50.
Gate: M > 50% of initial.

**Check 3 — Any structure survives to T=1000:**
M(T=1000) > 50 for either structure.
Gate: at least one M > 50.

## Decision rule

PASS if Check 1 passes. Checks 2 and 3 informational.

## Artifact paths

- `07_validation/audits/qng-hopfion-long-v1/report.json`
- `07_validation/audits/qng-hopfion-long-v1/summary.md`
