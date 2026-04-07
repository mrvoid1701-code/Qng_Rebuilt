# QNG-CPU-063

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Two-field v7 mass spectrum — H_ring(R) for R=2,3,4,5 in v7 substrate

## Purpose

CPU-058 measured the mass spectrum in v5 (single sigma). The pion/proton ratio
at R=2/R=5 was 1% match (suspicious coincidence or genuine prediction?).

This test repeats the measurement in the two-field v7 substrate. Since sigma_m
evolves identically to v5 (fully decoupled from sigma_g/chi), the mass ratios
should be identical to CPU-058. This is a CONSISTENCY CHECK.

If ratios differ: the k_gm coupling or phi weighting by sigma_m changes the
ring structure in a non-trivial way.
If ratios same: the two-field architecture preserves all matter-sector results.

## Experimental design

Same as CPU-058 (R=2,3,4,5, L=20, snapshot at T=1000, k_back=0.10)
but using v7 two-field update. k_gm=0.001.

Snapshot H: same formula, but now includes sigma_g energy too.

## Checks

**Check 1 — All rings survive (M>10 at T=1000):** same as CPU-058.

**Check 2 — v7 ratios match v5 ratios within 5%:**
|H_v7(R)/H_v7(R=5) - H_v5(R)/H_v5(R=5)| < 0.05 for all R

**Check 3 — Pion/proton ratio preserved (informational):**
H_v7(R=2)/H_v7(R=5) vs 0.1492 (PDG pion/proton).

## Decision rule

PASS if Checks 1 and 2 pass.

## Artifact paths

- `07_validation/audits/qng-two-field-spectrum-v1/report.json`
- `07_validation/audits/qng-two-field-spectrum-v1/summary.md`
