# QNG-CPU-045

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

3D vortex ring self-velocity scaling — v_ring ∝ 1/R confirmation in v5 substrate

## Purpose

A classical vortex ring in a superfluid self-propels along its symmetry axis with
the Biot-Savart velocity:
```
v_ring = (Γ / 4πR) × [ln(8R/a) - 1/4]
```
where Γ = 2π (one quantum of circulation in QNG), R is the ring radius, and
a ≈ 1 is the core size in lattice units.

This test checks whether the QNG substrate reproduces the 1/R Biot-Savart scaling
for R = 3, 4, 5, 6, 7.

**Known issue — Phase-1 drift:**
The two-phase protocol (Phase 1: phi diffusion without Channel F) causes the ring
to drift via phi diffusion BEFORE Channel F activates. This drift is R-independent
(driven by BETA_PHI, not Biot-Savart circulation) and masks the 1/R scaling in
Phase-2 measurements. Diagnostic (QNG-CPU-045 investigation): all R give dz=11
(L=24 lattice) from Phase-1 drift, regardless of R.

A PASS requires the measured velocity ratio v(R=3)/v(R=7) > 1.3. FAIL indicates
the Biot-Savart 1/R scaling is washed out by phi diffusion — a genuine finding
about the QNG substrate dynamics at BETA_PHI=0.02.

**Interpretation of FAIL:** The ring self-velocity in the QNG substrate with
BETA_PHI=0.02 is dominated by phi diffusion (R-independent drift), not by the
Biot-Savart self-propulsion. The classical 1/R scaling requires either: (a) much
smaller BETA_PHI (nearly inviscid limit), or (b) direct measurement of the phi
winding pattern velocity (not sigma depletion position). This finding constrains
the matter-sector kinematic program: vortex ring velocity cannot be matched to
physical particle velocity using this protocol.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng_ring_self_velocity_reference.py](../../tests/cpu/qng_ring_self_velocity_reference.py)

## Experimental design

**Lattice:** L=24, N=24³=13824, periodic BC.
(Larger than QNG-CPU-043 to reduce finite-size effects for R=6 and R=7.)

**Radii tested:** R = 3, 4, 5, 6, 7 (all centered at (L/2, L/2, L/2)).

**Parameters:** Identical to QNG-CPU-043 for each radius:
alpha=0.005, beta=0.35, beta_phi=0.02, delta=0.20, epsilon=0.0,
chi_decay=0.005, chi_rel=0.35, sigma_ref=0.5, gamma_phi=0.10.

**Protocol (for each radius R):**
1. Phase 1 (300 steps): phi equilibration, GAMMA_PHI=0.
2. Phase 2 (500 steps): Channel F active.
3. Measure z_ring at Phase-2 T=0 (start of Phase 2) and T=500 (end).
4. v_ring(R) = |z_ring(500) - z_ring(0)| / 500  [lattice units per step]
5. z_ring found by searching all z-planes for minimum mean sigma in rho ∈ [R-3, R+3].

**Theoretical prediction:**
```
v_theory(R) = (1 / (2πR)) × [ln(8R/1) - 0.25]
(in QNG lattice units, Γ=2π, a=1)
```
| R | v_theory |
|---|----------|
| 3 | 0.0676   |
| 4 | 0.0516   |
| 5 | 0.0416   |
| 6 | 0.0347   |
| 7 | 0.0297   |

Expected from QNG-CPU-043: v(R=5) ≈ 0.0129 (measured 9/700).
Note: QNG substrate velocity will differ from v_theory by a substrate factor k_v:
v_QNG(R) = k_v × v_theory(R). The k_v is a substrate constant. The test checks
that the RATIO v(R=3)/v(R=7) matches theory regardless of k_v.

## Checks

**Check 1 — Ring moves for all radii (velocity detectable):**
```
z-drift |z_ring(500) - z_ring(0)| > 1 lattice unit for all R ∈ {3,4,5,6,7}
```
The ring must move at least 1 lattice unit in 500 Phase-2 steps for each radius.

**Check 2 — Scaling consistent with 1/R (large rings move slower):**
```
v_ring(R=3) > v_ring(R=7)
```
The smallest ring must be faster than the largest. This is the qualitative 1/R test.

**Check 3 — Ratio v(R=3)/v(R=7) > 1.3:**
```
v(R=3) / v(R=7) > 1.3
```
Theoretical ratio: v_theory(3)/v_theory(7) = 0.0676/0.0297 = 2.28.
Gate 1.3 is conservative (substrate corrections may reduce the ratio).

**Check 4 — R=5 velocity consistent with QNG-CPU-043:**
```
v(R=5) in [0.005, 0.030]
```
QNG-CPU-043 measured dz=9 in 700 Phase-2 steps = 0.0129 units/step.
Gate [0.005, 0.030] allows for variation with the L=24 lattice.

**Check 5 — Monotone decrease (v decreases as R increases):**
```
v(R=3) > v(R=4) > v(R=5) > v(R=6) > v(R=7)
(with tolerance: each step must decrease by at least 0.0005 units/step)
```
The 1/R law predicts a strictly decreasing sequence. The QNG substrate should
reproduce this monotonicity at least qualitatively.

## Decision rule

**Overall PASS** if Checks 1, 2, 3, 4 pass (Check 5 is informational — near-equal
adjacent velocities are acceptable given finite-size effects and phase noise).

**Interpretation of PASS:**
The vortex ring self-propels with v_ring consistent with the 1/R scaling law.
This confirms the ring behaves as a classical vortex ring in the QNG substrate.
The substrate constant k_v can be extracted from v_QNG/v_theory and feeds directly
into the a_M fixing program as the matter propagation speed.

**Interpretation of FAIL:**
- Check 1 fails: ring doesn't move — Phase 2 too short or ring already collapsed.
  Extend Phase 2 or use larger Phase 1.
- Check 2/3 fails: no 1/R scaling — the ring velocity is not set by Biot-Savart
  dynamics in the QNG substrate. The substrate's phi field dynamics differ from
  classical superfluid. Investigate phi update law.
- Check 4 fails: velocity inconsistent with QNG-CPU-043 — lattice-size effect.
  Check z_ring detection for L=24.

## Artifact paths

- `07_validation/audits/qng-ring-self-velocity-reference-v1/report.json`
- `07_validation/audits/qng-ring-self-velocity-reference-v1/summary.md`
