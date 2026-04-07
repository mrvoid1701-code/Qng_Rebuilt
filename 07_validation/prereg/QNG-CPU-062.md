# QNG-CPU-062

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Two-field v7 k_gm scan — gravity signal strength vs coupling

## Purpose

CPU-060/061 use k_gm=0.001 (weak coupling). This test scans k_gm to:
1. Find the range where sigma_m ring remains stable (large k_gm might destabilize)
2. Measure gravity signal (delta_sg_core) vs k_gm
3. Check if signal scales linearly with k_gm (expected: linear)

## Experimental design

k_gm scan: [0.0, 0.001, 0.005, 0.01, 0.05, 0.10]
Phase2 = 1500 steps. Snapshot at T=1000.

## Checks

**Check 1 — Ring survives for k_gm <= 0.01:**
M_ring(T=1000) > 50 for all k_gm in [0.0, 0.001, 0.005, 0.01]

**Check 2 — Signal scales with k_gm (informational):**
Report delta_sg_core(T=1500) vs k_gm.

**Check 3 — Ring stability limit:**
Report k_gm_max where ring first drops below M=50.

## Decision rule

PASS if Check 1 passes.

## Artifact paths

- `07_validation/audits/qng-two-field-kgm-scan-v1/report.json`
- `07_validation/audits/qng-two-field-kgm-scan-v1/summary.md`
