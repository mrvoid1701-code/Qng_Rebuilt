# QNG-CPU-061

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Two-field v7 extended run — sigma_g spatial profile and chi wave emission

## Purpose

CPU-060 showed the ring survives in sigma_m (Gap 7 resolved) and the chi field
grows slowly (0.0011 at T=1000 → 0.019 at T=1400). This test runs longer
to characterize the sigma_g spatial profile around the ring.

Key question: does sigma_g show a YUKAWA-LIKE depletion profile centered on the
ring (static gravitational halo), or does the chi field propagate as KG WAVES
(oscillating signal spreading away from ring)?

Static halo: sigma_g depletion concentrated near ring, decaying with distance.
  -> This IS the Newtonian/Yukawa gravitational field of the ring.
  -> Would confirm: matter ring sources Yukawa potential in sigma_g sector.

Wave emission: chi uniform or oscillating across lattice.
  -> Dynamic wave emission from the ring.

## Inputs

- CPU-060: ring survives, chi growing, gravity signal present
- DER-QNG-033: v7 two-field architecture
- DER-QNG-032: H = T + E

## Experimental design

Same as CPU-060 but Phase2 = 2500 steps, K_GM = 0.001.

**Extra measurement every 500 steps: radial profile**
For each distance r = 1..9 from ring axis (ring at r=5 from center):
  delta_sg(r) = mean(sigma_g_ref - sigma_g_i) over shell at distance r from ring tube

## Checks

**Check 1 — Ring still alive at T=2000:**
```
M_ring(T=2000) > 50
```

**Check 2 — sigma_g profile at T=2000 shows spatial structure:**
```
|delta_sg(r=5)| > |delta_sg(r=10)|   [signal stronger near ring than far]
```

**Check 3 — chi field active at T=2000:**
```
chi_rms(T=2000) > 0.01
```

## Decision rule

PASS if Checks 1 and 2 pass.

## Artifact paths

- `07_validation/audits/qng-two-field-extended-v1/report.json`
- `07_validation/audits/qng-two-field-extended-v1/summary.md`
