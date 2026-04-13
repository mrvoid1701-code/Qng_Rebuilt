# QNG-CPU-074

Type: `prereg`
Status: `pass`
Author: `C.D Gabriel`
Date: `2026-04-13`
test_class: `mass_identification`

## Title

Conservative M_ring scan — canonical mass for R=3,4,5

## Purpose

DER-QNG-036 §6 uses M_ring in the mass identification formula:
  ρ₀ = m_particle / (a_M × M_ring)

DER-QNG-036 caveat (added 2026-04-13): M_ring MUST be the conservative Phase-3
value, not any dissipative measurement. The CPU-051 value of 158.4 (dissipative,
no back-reaction) is deprecated for mass identification.

CPU-067 gave one conservative data point: R=5, M_ring=954.9 at T=1000 Phase 3.

This test extends the scan to R=3, R=4, R=5 using the same conservative protocol,
to give M_ring(R) for the three radii most used in the theory.

## Upstream

- DER-QNG-036 §6: mass formula and M_ring regime caveat
- QNG-CPU-067: PASS — conservative Phase 3 protocol confirmed; M(R=5,T=1000)=954.9
- QNG-CPU-073: PASS — back-reaction confirmed; M_ring regime dependence exposed

## Experimental design

For each R ∈ {3, 4, 5}:

  **Phase 1** (300 steps): dissipative v7, no Channel F, no Channel G.
  Purpose: let phi vortex form cleanly.

  **Phase 2** (1500 steps): dissipative v7-symmetric, Channel F active, CHI_DECAY=0.020.
  No Channel G (k_back=0 in Phase 2). No back-reaction in Phase 2.
  Purpose: form a stable sigma_m ring.

  **Phase 3** (1000 conservative steps): no Channel A, no Channel F, no chi_decay.
  Keep: Channel B (beta diffusion), Channel G (k_back=0.10), chi_rel, phi XY.
  Purpose: measure ring mass under conservative (non-dissipative) dynamics.

Record M_ring = sum_i max(0, sigma_m_ref - sigma_m_i) at:
  T_P3 = 0 (start of Phase 3), 200, 500, 750, 1000

## Checks

**Check 1 — Ring survives Phase 3 for all radii:**
M_ring(T_P3=1000) > 50 for R=3, R=4, R=5.

**Check 2 — Conservative M_ring > dissipative M_ring at T=1000:**
For each R: M_ring_conservative > M_ring_dissipative.
(Conservative dynamics should slow decay; ring lives longer without dissipative channels.)

**Check 3 — M_ring scales monotonically with R:**
M_ring(R=3) < M_ring(R=4) < M_ring(R=5) at T_P3=1000.
(Larger rings have more circumference → more matter depletion.)

## Decision rule

PASS if Check 1 and Check 3 pass.

## Artifact paths

- `07_validation/audits/qng-conservative-mring-scan-v1/report.json`
- `07_validation/audits/qng-conservative-mring-scan-v1/summary.md`
