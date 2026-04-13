# QNG-CPU-073

Type: `prereg`
Status: `pass`
Author: `C.D Gabriel`
Date: `2026-04-13`
test_class: `back_reaction`

## Title

Back-reaction test — does sigma_m fall into a sigma_g gravitational well?

## Purpose

DER-QNG-036 (Section 7) shows that the coupling functional
`E_coupling = k_gm * sum_i (sigma_m_ref - sigma_m_i)(sigma_g_ref - sigma_g_i)`
implies two gradient-flow terms:

  (A) sigma_g_i -= k_gm*(sigma_m_ref - sigma_m_i)  — matter sources gravity [PRESENT in v7]
  (B) sigma_m_i += k_gm*(sigma_g_i - sigma_g_ref)  — matter falls into gravity [ABSENT in v7]

Without term (B), vortex rings create gravitational wells but do not fall into
each other's wells. Term (B) is the QNG analog of the geodesic equation.

This test directly checks whether adding term (B) — defining "v7-symmetric" —
produces measurable ring drift toward a static sigma_g depletion source.

## Upstream

- DER-QNG-036: Hamiltonian for v7 two-field substrate (back-reaction gap, Section 7)
- DER-QNG-033: v7 update law
- QNG-CPU-071: PASS — sigma_g gravitational well confirmed
- DER-QNG-034: Gap 8 stability criterion (CHI_DECAY >= 0.020 required)

## Experimental design

- L=20 lattice, two-field v7 substrate
- Vortex ring (RING_R=3) formed at center (10,10,10) in Phase 1 (no gravity, 300 steps)
- Static gravity well: sigma_g PINNED to PIN_SG=0.20 in a sphere of radius 2 around
  (GX=10, GY=10, GZ=3). Distance ring-to-pin: 7 lattice units.
- Chi at pin nodes reset to 0 each step (prevent chi buildup at pinned sites).
- K_GM=0.050, K_BACK=0.10, CHI_DECAY=0.020 (Gap 8 stable)

Two parallel Phase 2 runs (3000 steps each), branched from same Phase 1 state:

  **Case A (v7-original):** standard v7, sigma_m does NOT include term (B).
  Ring centroid should NOT drift toward pin (no force path).

  **Case B (v7-symmetric):** v7 + term (B): sigma_m_i += k_gm*(sigma_g_i - sigma_g_ref).
  Ring centroid SHOULD drift toward pin (sigma_m depleted further near pin).

Ring centroid measured as sigma_m-depletion-weighted z-coordinate:
  z_cen = sum_i [(sigma_m_ref - sigma_m_i) * z_i] / sum_i [sigma_m_ref - sigma_m_i]

Drift = z_cen_initial - z_cen_final  (positive = moved toward pin at lower z).

## Checks

**Check 1 — Symmetric case drifts toward pin:**
drift_symmetric > 0.5 lattice units.
(Ring centroid decreases from z≈10 toward pin at z=3.)

**Check 2 — Back-reaction adds drift over original:**
extra_drift = drift_symmetric - drift_original > 0.5 lattice units.
(Controls for any residual drift in the original v7.)

**Check 3 — Both rings structurally alive:**
M_final = sum_i max(0, sigma_m_ref - sigma_m_i) > 50 for both cases.

## Decision rule

PASS if Check 1 AND Check 2 AND Check 3 pass.

FAIL interpretation:
- Check 1/2 FAIL: signal too weak at these parameters OR back-reaction has no effect.
  → Increase K_GM, reduce PIN_SG, or run longer before concluding.
- Check 3 FAIL: ring dissolves; stability issue unrelated to back-reaction.

## Artifact paths

- `07_validation/audits/qng-back-reaction-v1/report.json`
- `07_validation/audits/qng-back-reaction-v1/summary.md`
