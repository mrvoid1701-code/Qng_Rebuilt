# QNG-CPU-072

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

K_GM scan — gravitational field strength vs coupling constant

## Purpose

CPU-071 signal (min_dsg ~ 3e-4) too small for Yukawa fit at K_GM=0.001.
Scan K_GM = 0.001, 0.005, 0.010, 0.020, 0.050 to find:
- Maximum K_GM where Gap 8 stability holds
- Signal amplitude large enough for Yukawa fit (lambda extraction)

Gap 8 criterion: K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA) = 0.025.
This criterion is independent of K_GM (K_GM is a static sigma_m→sigma_g coupling,
not the oscillatory K_BACK channel). K_GM stability determined empirically.

## Upstream

- QNG-CPU-071: PASS — well exists at K_GM=0.001, signal too small for Yukawa

## Checks

**Check 1 — Signal scales with K_GM:** min_dsg(K_GM=0.020) > 10 × min_dsg(K_GM=0.001).

**Check 2 — Yukawa fit succeeds at some K_GM:** lambda in [1, L/2] for at least one value.

**Check 3 — Stability at K_GM=0.020:** M_ring > 0 at T=1500 (structure survives).

## Decision rule

PASS if Check 1 and Check 3 pass.

## Artifact paths

- `07_validation/audits/qng-hopfion-kgm-scan-v1/report.json`
- `07_validation/audits/qng-hopfion-kgm-scan-v1/summary.md`
