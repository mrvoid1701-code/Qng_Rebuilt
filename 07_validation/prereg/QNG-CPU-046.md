# QNG-CPU-046

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Multi-ring interaction stress test — two vortex rings, chi field between them

## Purpose

QNG-CPU-043 confirmed a single vortex ring is dynamically stable. This test
places TWO rings in the same lattice and measures whether the chi field between
them shows any signature of interaction — the first test of whether the ether
mediates forces between "particles."

From DER-QNG-027: each vortex ring sources a chi field that decays as the
Yukawa kernel C_K(r) = (1+r/λ)·exp(-r/λ) with λ = 3.41 lattice units.

With rings separated by d lattice units, the Yukawa overlap is:
```
overlap ~ exp(-d/lambda)
```

For d=12, lambda=3.41: overlap ~ 3%. Small but potentially detectable in the
chi field profile along the axis between the rings.

Three measurements:
1. Chi profile along z-axis: is chi enhanced BETWEEN the rings vs outside?
2. Sigma core depth of ring 1: does ring 2 affect ring 1's depletion?
3. Ring stability: do both rings survive the mutual perturbation?

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-vortex-ring-3d-reference.py](../../tests/cpu/qng_vortex_ring_3d_reference.py) — QNG-CPU-043
- [qng_multi_ring_reference.py](../../tests/cpu/qng_multi_ring_reference.py)

## Experimental design

**Lattice:** L=24, N=13824 (same as QNG-CPU-045)

**Two rings:**
- Ring 1: center (L/2, L/2, 6),  radius R=4, chirality W=+1
- Ring 2: center (L/2, L/2, 18), radius R=4, chirality W=+1
- Separation: 12 lattice units (center to center) = 3.5 × lambda

**Same-chirality** (both W=+1): classical Biot-Savart predicts co-axial
same-chirality rings attract along z if moving in same direction.

**Parameters:** identical to QNG-CPU-043:
alpha=0.005, beta=0.35, beta_phi=0.02, delta=0.20, epsilon=0.0,
chi_decay=0.005, chi_rel=0.35, sigma_ref=0.5, gamma_phi=0.10

**Protocol:**
1. Phase 1 (300 steps): phi equilibration, Channel F off
2. Phase 2 (1000 steps): Channel F active
3. Checkpoints every 200 steps: measure ring positions, chi profile, sigma depth

**Reference run:** single ring (Ring 1 only) with identical parameters,
for direct comparison of chi profile and sigma depth.

## Checks

**Check 1 — Both rings survive Phase 2:**
```
R_t(ring1) > R/4 = 1.0  and  R_t(ring2) > R/4 = 1.0
at Phase-2 T=1000
```

**Check 2 — Chi field enhanced between rings:**
```
mean_chi_between > mean_chi_outside
```
where between = z ∈ [8, 16], outside = z ∈ [0, 4] ∪ [20, 23]
along the central z-axis (x=L/2, y=L/2).

**Check 3 — Chi profile asymmetry detectable:**
```
max(|chi_profile_two_rings - chi_profile_single_ring|) > 0.001
```
Any difference in the chi profile between two-ring and single-ring runs
indicates mutual influence through the substrate.

**Check 4 — Sigma core depths comparable:**
```
|sigma_core_ring1_tworings - sigma_core_ring1_single| < 0.05
```
Rings should not drastically perturb each other's internal structure.
A large change would indicate strong coupling.

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass (Check 4 informational).

**Interpretation of PASS:**
The chi field is enhanced between the rings — the ether builds up between
two matter sources. This is consistent with an attractive interaction mediated
by the chi field. The rings are coupled through the substrate.

**Interpretation of FAIL:**
- Check 1 fails: one ring destabilized by the other — strong repulsion
- Check 2 fails: no chi enhancement between rings — the Yukawa fields do not
  add constructively; rings are too far apart for detectable interaction
- Check 3 fails: chi profile identical to single ring — no mutual influence

## Artifact paths

- `07_validation/audits/qng-multi-ring-reference-v1/report.json`
- `07_validation/audits/qng-multi-ring-reference-v1/summary.md`
