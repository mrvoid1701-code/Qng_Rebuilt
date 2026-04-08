# QNG-CPU-070

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `hopfion_candidate`

## Title

Hopfion Q=1 vs ring Q=0 — sigma_m radial profile shape measurement

## Purpose

CPU-069 showed near-zero total mass loss (ring 0.09%, Hopfion 0.02%) over 100k steps.
But total M is a scalar — it cannot detect shape changes. The depletion TUBE may be
broadening (sigma_m profile flattening) while total mass stays constant.

This test measures the radial sigma_m profile cross-section through the ring center
at intervals of 10,000 steps to detect shape evolution.

## Upstream

- QNG-CPU-069: PASS — ring 99.91%, Hopfion 99.98% at 100k steps

## Experimental design

- Build ring Q=0 and Hopfion Q=1 (Phase1=300 + Phase2_diss=1000)
- Run 50,000 conservative steps
- Every 10,000 steps: record radial sigma_m profile (slice through ring center)
  - Slice: y=RY plane (xz cross-section through ring equator)
  - Profile: sigma_m(r) averaged over angular bins, r = distance from ring axis
- Measure depletion depth (min sigma_m) and tube width (FWHM of depletion profile)

## Checks

**Check 1 — Tube width stable at T=50k:**
FWHM(T=50000) < 1.5 × FWHM(T=0). Gate: tube does not double in width.

**Check 2 — Depletion depth stable:**
min_sigma_m(T=50000) > 0.5 × min_sigma_m(T=0) (core not filled in by >50%).

**Check 3 — Hopfion profile wider than ring at T=0 (informational):**
Records structural difference between Q=0 and Q=1.

## Decision rule

PASS if Check 1 and Check 2 pass.

## Artifact paths

- `07_validation/audits/qng-hopfion-shape-v1/report.json`
- `07_validation/audits/qng-hopfion-shape-v1/summary.md`
