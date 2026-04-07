# QNG-CPU-058

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Vortex ring mass spectrum — H_ring(R) for R=2,3,4,5 vs hadron mass ratios

## Purpose

CPU-057 established the snapshot H measurement protocol and found that the
absolute mass scale requires m_u ~ 7.7e-34 kg (not Planck mass). However,
the RATIOS m_ring(R1)/m_ring(R2) are independent of m_u — they depend only
on the substrate dynamics.

If H_ring(R) ratios match known hadron mass ratios, this provides empirical
evidence that vortex rings ARE the matter sector, even before the absolute
scale is fixed.

Key question: does m_ring scale as R, R^2, R^3, or something non-trivial?

Reference hadron mass ratios (PDG):
  pi(140) / proton(938) = 0.149
  rho(770) / proton(938) = 0.821
  Delta(1232) / proton(938) = 1.313
  K(494) / proton(938) = 0.527

## Inputs

- QNG-CPU-057: snapshot H protocol (PASS), k_min=0.0044 at R=5
- QNG-CPU-043/044: R=4 ring stable (confirmed baseline)
- DER-QNG-032: H = T + E formula

## Experimental design

**Ring radii:** R = 2, 3, 4, 5  (all on L=20 lattice)

**Parameters (identical to CPU-057 for R=5):**
- ALPHA=0.005, BETA=0.35, DELTA=0.20, CHI_DECAY=0.005, CHI_REL=0.35
- GAMMA_PHI=0.10, BETA_PHI=0.02, EPSILON=0.0
- Phase 1: 300 steps (no Channel F), Phase 2: 1500 steps (Channel F active)

**Snapshot k_back:** [0.005, 0.01, 0.02, 0.05, 0.10, 1.00]

**Measurements at Phase-2 T=1000:**
```
For each R:
  H_ring(R)    = snapshot H(k_back=0.10) at T=1000
  k_min(R)     = 2*|E_ring(R)| / sum_chi2(R)
  M_ring(R)    = sigma depletion integral
  ratio(R/R5)  = H_ring(R) / H_ring(R=5)
```

## Checks

**Check 1 — All rings survive Phase 2:**
```
M_ring(R, T=1000) > 10   for R in [2,3,4,5]
```
Note: smaller rings may have smaller M; threshold is lower than CPU-057.

**Check 2 — H scales non-trivially with R:**
```
H_ring(R=2) / H_ring(R=5) != (2/5)^n for n=1,2,3 within 10%
```
If H ~ R^n for integer n, the scaling is trivial (geometric).
Non-trivial scaling suggests dynamical mass generation.

**Check 3 — Mass ratios informational (no PASS/FAIL gate):**
Report H_ring(R) / H_ring(R=5) for R=2,3,4 and compare to:
  pi/p=0.149,  rho/p=0.821,  Delta/p=1.313

Any ratio within 10% of a known hadron ratio is flagged as a candidate match.

## Decision rule

**Overall PASS** if Check 1 passes (all rings survive).
Checks 2 and 3 are findings regardless of value.

## Artifact paths

- `07_validation/audits/qng-ring-mass-spectrum-v1/report.json`
- `07_validation/audits/qng-ring-mass-spectrum-v1/summary.md`
