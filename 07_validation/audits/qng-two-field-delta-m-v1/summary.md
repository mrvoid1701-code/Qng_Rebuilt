# QNG-CPU-065 Audit Summary

**Result: FAIL (Check 2 — T_kin ratio=85.6 < gate 100)**
Date: 2026-04-08
Script: `tests/cpu/qng_two_field_delta_m_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - All rings M>10 | M>10 | PASS |
| 2 - T_kin grows ×100 (DELTA_m 0→0.20) | ratio > 100 | FAIL (ratio=85.6) |
| 3 - chi_rms < 1.0 | chi_rms < 1.0 | PASS (max=0.012) |
| 4 - Spectrum scaling n (informational) | — | n=1.05→1.17 |

## Full spectrum table

| DELTA_m | H(R=2) | H(R=3) | H(R=4) | H(R=5) | n | R=2/R=5 |
|---------|--------|--------|--------|--------|---|---------|
| 0.00 | 7.088 | 9.621 | 14.446 | 18.498 | 1.05 | 0.383 |
| 0.02 | 7.095 | 9.634 | 14.482 | 18.558 | 1.05 | 0.382 |
| 0.05 | 7.114 | 9.672 | 14.594 | 18.748 | 1.06 | 0.379 |
| 0.10 | 7.171 | 9.785 | 14.941 | 19.332 | 1.08 | 0.371 |
| 0.20 | 7.380 | 10.198 | 16.226 | 21.500 | 1.17 | 0.343 |

## Key finding: DELTA_m does not recover kinetic mass at CHI_DECAY=0.020

Expected (from v5 analogy): chi_rms ~ DELTA_m * m_dep / CHI_DECAY = 0.20*0.3/0.020 = 3.0
Measured at DELTA_m=0.20, R=5: chi_rms = 0.012

Discrepancy factor: 3.0/0.012 = 250×. The chi buildup is negligible.

**Root cause: CHI_DECAY=0.020 damps chi 4× faster than v5 (CHI_DECAY=0.005).**
In v5, chi_rms ~ 5 at ring (large kinetic energy). In v7 with Fix B, chi_rms ~ 0.01.
The ratio T_kin(DELTA_m=0.20)/T_kin(DELTA_m=0) = 85.6 (vs gate 100) confirms chi
is growing but very slowly. Gate missed by only 15% — borderline FAIL.

## Structural tension confirmed (DER-QNG-034)

This test confirms the fundamental tension identified analytically:

  Gap 8 fix (CHI_DECAY=0.020) suppresses exactly the kinetic mass mechanism.

  - CHI_DECAY small (0.005): chi builds up large at ring → kinetic mass H~R² → pion spectrum
    BUT Gap 8 Jeans instability → sigma_g collapses globally by T=2000
  - CHI_DECAY large (0.020): Gap 8 stable → chi stays small → E~R^1 only → string tension spectrum
    DELTA_m=0.20 only shifts n from 1.05 to 1.17 (not 2.0)

These two requirements cannot both be satisfied by tuning CHI_DECAY alone.

## Spectrum shift direction

DELTA_m increases n from 1.05 to 1.17 — correct direction (toward n=2) but insufficient.
To reach n=2 (full kinetic dominance) with stable chi, would need DELTA_m >> 0.20 while
keeping chi_rms < 1.0. Extrapolating: need n increase of ~0.95 more, at rate ~0.06/per 0.1
DELTA_m → would need DELTA_m ~ 1.8. But chi_rms would then be ~0.22, possibly unstable.

Alternatively: a separate stabilization mechanism for chi at the ring is needed —
not global CHI_DECAY but a LOCAL chi saturation (nonlinear term, Einstein's chi³ suggestion).

## What changes with DELTA_m (physically real)

Even though kinetic mass is small, DELTA_m does something physically correct:
- H(R=5) increases from 18.498 to 21.500 (+16%) at DELTA_m=0.20
- E_ring grows more than string tension alone: E(R=5) goes 18.497 → 21.440 (+16%)
- The ring's potential energy increases because chi(from DELTA_m) feeds back into sigma_g
  via Channel G, deepening the sigma_g depletion → more gravitational binding energy

This means: DELTA_m couples the matter sector to the gravitational sector in a physically
meaningful way even without kinetic mass dominance.

## Next architectural step

The DELTA_m test reveals that the kinetic mass recovery requires either:

1. **Local chi saturation** (nonlinear): chi_i += -lambda_chi * chi_i^3
   Allows large chi at ring (local) without global runaway.
   This is Einstein's suggested fix for Gap 8 — not yet implemented.

2. **Separate pi_m field** (structural): give sigma_m its own conjugate momentum pi_m.
   H = K_BACK/2*sum_chi² + K_M/2*sum_pi_m² + E[sg,sm,chi,pi_m,phi]
   This is the full conservative Hamiltonian for v7 (DER-QNG-034 open program).

3. **Accept string tension spectrum** (reframe): E~R^1 is physically correct for a
   topological line defect (vortex string). The K meson match at R=3 (1.4%) may not be
   coincidental if the string tension scale is correctly normalized. Hopfion extension
   (3D topological soliton) could provide the stable conservative structure.

## Connection to Hopfion program

The user identified (2026-04-08) that a rotating quantum structure with bipolar jets
(north/south) may hold the key. This describes a **Hopfion** — a 3D topological soliton
in the Skyrme-Faddeev model. Hopfions:
- Are stable under conservative Hamiltonian dynamics (no dissipation needed)
- Have bipolar field structure (field lines through north/south poles of torus)
- Have energy E ~ L^(3/4) where L is the Hopf charge (different from both R^1 and R^2)
- Could replace the current ring as the fundamental particle candidate in QNG

This is the suggested next theoretical program after CPU-065.
