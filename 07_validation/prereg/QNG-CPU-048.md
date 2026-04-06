# QNG-CPU-048

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Two-ring force direction — epsilon scan in linear regime with separation tracking

## Purpose

QNG-CPU-047 showed epsilon=0.1 destabilizes rings (chi~13 produces too strong
a phi perturbation per step: 0.1*13=1.3 rad >> linear regime). The rings were
scrambled, not cleanly displaced.

This test uses epsilon=0.005 (phi perturbation per step: 0.005*13=0.065 rad,
small relative to pi — linear regime). The key measurement is SEPARATION
between the two rings over time, not absolute position. Attraction = separation
decreases. Repulsion = separation increases.

Two improvements over CPU-047:
1. Ring-specific detection zones prevent algorithm confusion between the two rings
2. Separation tracking (|z2 - z1|) is the direct force observable

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng_ring_force_linear_reference.py](../../tests/cpu/qng_ring_force_linear_reference.py)

## Experimental design

**Lattice:** L=24, N=13824

**Two rings:** R=4, Ring 1 at z=6, Ring 2 at z=18, separation=12

**Epsilon values tested:**
- epsilon=0.000 (baseline — chi inert)
- epsilon=0.005 (linear regime — chi weakly drives phi)

**Ring-specific detection:**
- Ring 1 searched in z ∈ [0, 11]   (lower half)
- Ring 2 searched in z ∈ [12, 23]  (upper half)

**Separation:** S(t) = min(|z2-z1|, L-|z2-z1|) [periodic distance]

**Protocol:** Phase 1 (300 steps), Phase 2 (3000 steps, check every 100).

## Checks

**Check 1 — Both rings detectable throughout Phase 2:**
```
Both ring positions detectable (sigma depletion visible) at all checkpoints
from T=100 to T=3000.
```

**Check 2 — epsilon=0.005 changes separation vs baseline:**
```
|S_final(eps=0.005) - S_final(eps=0.000)| > 1
```
The chi-phi coupling must produce a measurable change in ring separation.

**Check 3 — Separation trend is monotonic (informational):**
```
Report whether S(t) is increasing (repulsion), decreasing (attraction),
or oscillating over T=1000 to T=3000.
```

**Check 4 — epsilon=0.005 separation different from single-ring drift:**
```
S_final(eps=0.005, two rings) differs from 2*|z_single(eps=0.005) - z_single(eps=0)|
```
The separation change must be due to ring-ring interaction, not just
epsilon-induced single-ring drift.

## Decision rule

**Overall PASS** if Checks 1, 2 pass.

**Interpretation:**
- S decreasing with eps=0.005 → ATTRACTION through chi-phi-sigma chain
- S increasing with eps=0.005 → REPULSION
- No change → chi field too screened at this separation to produce measurable force

## Artifact paths

- `07_validation/audits/qng-ring-force-linear-reference-v1/report.json`
- `07_validation/audits/qng-ring-force-linear-reference-v1/summary.md`
