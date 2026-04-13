# QNG-CPU-076

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-13`
test_class: `mass_identification`

## Title

M_ring ratio stability under parameter variation — topological vs. kinematic origin

## Purpose

DER-QNG-038 identifies R=4 → N(938), R=5 → Δ(1232) based on the ratio
M_ring(R=4)/M_ring(R=5) = 0.7634 matching m_N/m_Δ = 0.7616 to 0.24%.

**Open question (Newton analyst review, 2026-04-13):** Is this ratio a topological
invariant of the QNG vortex ring geometry, or is it a kinematic coincidence that
depends on the specific dissipation parameters (alpha_m, beta_m, gamma_phi)?

If M_ring(R=4)/M_ring(R=5) is approximately constant (~±2%) across a wide range of
parameter values, the identification is robust — the ratio is set by ring geometry
(topology), not by the specific dissipation. If it varies by ~10%, the 0.24% match
is tuned to the default parameters and is suspect.

This test also addresses the T_P2 protocol dependence flagged in DER-QNG-038 §1:
if the ratio is T_P2-invariant, the particle mass ratios are robust regardless of
which snapshot time is chosen.

## Upstream

- DER-QNG-038: N/Δ identification, open T_P2 caveat
- QNG-CPU-074: PASS — canonical M_ring protocol
- QNG-CPU-075: PASS — R=6,7 identified
- Newton analyst review (2026-04-13): proposed this test as decisive

## Experimental design

### Part A: Parameter variation (27 configurations)

For each combination of (alpha_m, beta_m, gamma_phi) in the grid below, run the CPU-074
protocol (Phase 1=300, Phase 2=1500) for R=4 and R=5 only. Record M_ring at T_P2=1000.

Parameter grid:
```
alpha_m ∈ {0.003, 0.005, 0.008}   [default: 0.005]
beta_m  ∈ {0.25,  0.35,  0.45 }   [default: 0.35]
gamma_phi ∈ {0.07, 0.10, 0.14}    [default: 0.10]
```

27 configurations total. Measure ratio = M_ring(R=4) / M_ring(R=5) at each.

### Part B: T_P2 sensitivity (default parameters only)

At default parameters (alpha_m=0.005, beta_m=0.35, gamma_phi=0.10), measure:
M_ring(R=4) / M_ring(R=5) at T_P2 = {500, 750, 1000, 1250, 1500}.

## Checks

**Check 1 — Ratio stability across parameter grid (Part A):**
std(ratio_grid) / mean(ratio_grid) < 0.05   [relative std dev < 5%]

This tests whether the ratio is topologically stable.

**Check 2 — Ratio stability across T_P2 (Part B):**
max(ratio_T_P2) - min(ratio_T_P2) < 0.030   [absolute range < 3%]

Target ratio = 0.7634. Gate: all T_P2 values give ratio in [0.74, 0.79].

**Check 3 — N/Δ match maintained across grid:**
Fraction of 27 configurations where |ratio - 0.7616| < 0.020  ≥ 20/27  (~75%)

This tests whether the N/Δ match is broadly reproduced, not just at default parameters.

## Decision rule

PASS (topological): Check 1 AND Check 2 pass.
  Interpretation: M_ring ratio is a topological invariant. The N/Δ identification is robust.

PASS (conditional): Check 1 fails but Check 3 passes.
  Interpretation: Ratio is parameter-sensitive but N/Δ match holds broadly.
  Requires Check 2 for T_P2 stability before mass claims are hardened.

FAIL: Check 1 and Check 3 both fail.
  Interpretation: The 0.24% match is tuned to default parameters. Identification suspect.

## Artifact paths

- `07_validation/audits/qng-mring-ratio-stability-v1/report.json`
- `07_validation/audits/qng-mring-ratio-stability-v1/summary.md`
