# QNG-GPU-011

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-15`
test_class: `mass_identification`
hardware: `GPU`

## Title

M_ring ratio L-convergence under v8 Channel H (IR-safety test)

## Purpose

GPU-009 and GPU-010 confirmed that in v7, M_ring = N*sigma_ref - sum(sigma_m) is
IR-divergent: grows as L^1.6, ratio M(R=5)/M(R=4) drifts from 1.310 (L=20) to ~1.8
(L=80). The 0.24% N/Delta agreement at L=20 is a finite-size coincidence (phi halo
crossing SM ratio during halo growth).

Einstein-mind diagnosis: phi is a massless Goldstone field in QNG. A vortex in a
gapless field has divergent halo energy. M_ring = core (finite) + halo (divergent).

Fix: Channel H (v8, DER-QNG-039). With bp_eff = bp_min + bp_ring * depletion:
  - In ring core (depletion > 0): phi diffuses fast -> winding stays localized
  - In bulk (depletion ~ 0): phi frozen (bp_min ~ 0) -> no bulk disorder -> Channel F inactive

Decisive test: run v8 with Channel H in BOTH Phase 1 and Phase 2, k_gm=0
(no gravitational compression). Check if M(R=5)/M(R=4) converges with L.

## Upstream

- DER-QNG-038: N/Delta identification, IR-safety caveat added 2026-04-15
- DER-QNG-039: Channel H definition
- GPU-009: v7 L-scan, NOT_CONVERGED
- GPU-010: v8 windowed L-scan, NOT_CONVERGED (Phase 1 still used constant BETA_PHI)
- Einstein-mind: phi-halo diagnosis
- Newton analyst: required remediation — CPU-076 reframed as GPU-011

## Key protocol change vs GPU-010

GPU-010 used constant BETA_PHI=0.02 in Phase 1, then Channel H in Phase 2.
This caused phi to spread into bulk during Phase 1 before Channel H could act.

GPU-011 uses Channel H from Phase 1 also:
  bp_eff_i = BETA_PHI_MIN + BETA_PHI_RING * depletion(i)
In Phase 1, sigma_m ~ SIGMA_REF everywhere -> depletion ~ 0 -> bp_eff ~ bp_min ~ 0.
Phi stays at its initial configuration (ring topology preserved, no bulk spreading).

## Parameters

Channel H: BETA_PHI_MIN=0.0005, BETA_PHI_RING=0.06
k_gm = 0 (pure phi confinement test, no gravitational coupling)
GAMMA_PHI = 0.10, ALPHA=0.005, BETA=0.35, CHI_DECAY=0.020
Phase 1: 300 steps (Channel H active, no Channel F)
Phase 2: 1500 steps (Channel H + Channel F)

L values: [20, 30, 40, 60, 80]
Radii: [4, 5]

## Checks

Check 1 — L-convergence of global M_ring ratio:
  last-3-L spread of M(R=5)/M(R=4) < 0.02   [vs 0.0832 in v7, 0.0204 in GPU-010]

Check 2 — Ratio approaches SM:
  |ratio_L80 - 1.3130| / 1.3130 < 0.05   [within 5% of SM]

Check 3 — dis_bulk converges to near 0:
  dis_bulk(L=80) < 0.002   [phi confined to ring core]

## Decision rule

PASS: Check 1 AND Check 2 AND Check 3.
  Interpretation: phi confined, mass IR-safe, 0.24% match is a genuine prediction.

PASS_WEAK: Check 1 AND Check 3 but NOT Check 2.
  Interpretation: phi confined, mass converges, but to a value != SM. Need deeper analysis.

FAIL: Check 1 fails.
  Interpretation: Channel H insufficient for IR safety. Need stronger confinement or
  different mass definition. Baryon mass identification remains candidate only.

## Artifact paths

- `07_validation/audits/qng-v8-l-convergence-v1/report.json`
- `07_validation/audits/qng-v8-l-convergence-v1/summary.md`
