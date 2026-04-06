# QNG-CPU-047

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Two-ring attraction/repulsion — does chi-field force move matter?

## Purpose

QNG-CPU-046 showed chi field amplifies 4x between two vortex rings.
But with epsilon=0 (Channel E disabled), chi cannot perturb phi → D_i → sigma.
The rings are coupled in the chi field but not dynamically.

This test enables Channel E (epsilon > 0): chi directly drives phi.
The coupling chain is then:
```
ring2 → chi_field → phi perturbation (Channel E) → D_i change → Channel F → sigma → ring1 position
```

Two scenarios compared:
- epsilon=0:   chi accumulates between rings, no force (baseline)
- epsilon=0.1: chi drives phi, force propagates through substrate

If ring positions differ between scenarios → chi-phi coupling mediates a force.
If identical → the chi field is dynamically inert (force requires a different mechanism).

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng_multi_ring_reference.py](../../tests/cpu/qng_multi_ring_reference.py) — QNG-CPU-046
- [qng_ring_force_reference.py](../../tests/cpu/qng_ring_force_reference.py)

## Experimental design

**Lattice:** L=24, N=13824

**Two rings:** R=4, Ring 1 at z=6, Ring 2 at z=18 (same as QNG-CPU-046)

**Two scenarios:**
1. epsilon=0.0  (Channel E off — chi cannot drive phi)
2. epsilon=0.1  (Channel E on  — chi drives phi)

All other parameters identical to QNG-CPU-046.

**Protocol:** Phase 1 (300 steps, no Channel F), Phase 2 (2000 steps, Channel F on).
Measure z_ring1 and z_ring2 every 100 Phase-2 steps using minimum-sigma plane detection.

**Reference:** single ring (ring 1 only) with epsilon=0 and epsilon=0.1,
to isolate single-ring drift from interaction-driven drift.

## Checks

**Check 1 — Both rings survive 2000 Phase-2 steps:**
```
Ring detected (sigma depletion visible) for both rings at T=2000
in both epsilon scenarios.
```

**Check 2 — Ring positions differ between epsilon=0 and epsilon=0.1:**
```
|z_ring1(epsilon=0.1, T=2000) - z_ring1(epsilon=0.0, T=2000)| > 1
OR
|z_ring2(epsilon=0.1, T=2000) - z_ring2(epsilon=0.0, T=2000)| > 1
```
If chi-phi coupling changes ring positions by more than 1 lattice unit,
the force mechanism is real and detectable.

**Check 3 — Two-ring position differs from single-ring with epsilon=0.1:**
```
|z_ring1_two(epsilon=0.1, T=2000) - z_ring1_single(epsilon=0.1, T=2000)| > 1
```
The presence of ring 2 must change ring 1's trajectory when epsilon>0.
This is the direct test of ring-ring force mediation.

**Check 4 — Direction consistent (informational):**
```
Report: do rings move TOWARD each other (attraction) or AWAY (repulsion)?
z_ring1 increases toward z=18 → attraction
z_ring1 decreases away from z=18 → repulsion
```

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass.

**Interpretation of PASS:**
The chi-phi coupling (Channel E) mediates a detectable force between vortex rings.
The ether transmits a force between particles through the chi→phi→sigma chain.
The direction (Check 4) tells us if QNG matter is attractive or repulsive
at these substrate parameters.

**Interpretation of FAIL:**
- Check 2 fails: epsilon=0.1 doesn't change ring positions — Channel E coupling
  is too weak or the chi field at ring 1 from ring 2 is too small (Yukawa-screened)
- Check 3 fails: ring 2 doesn't affect ring 1 even with epsilon>0 — the rings
  are too far apart for the chi-phi coupling to transmit a measurable force
  at separation=12 with lambda=3.41

## Artifact paths

- `07_validation/audits/qng-ring-force-reference-v1/report.json`
- `07_validation/audits/qng-ring-force-reference-v1/summary.md`
