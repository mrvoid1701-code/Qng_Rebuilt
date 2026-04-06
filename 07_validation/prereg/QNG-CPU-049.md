# QNG-CPU-049

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Ring force chirality comparison — same-winding vs opposite-winding at epsilon=0.005

## Purpose

QNG-CPU-048 showed that epsilon=0.005 produces a measurable separation change
(sep_diff=5, REPULSION trend) between two W=+1 rings. But the chi->phi channel
(Channel E) adds epsilon*chi_i uniformly to phi — it does not explicitly carry
winding information.

**Key question:** Does the winding number of ring 2 affect the force on ring 1?

- Same chirality (W=+1, W=+1): both rings source chi fields with same phi topology
- Opposite chirality (W=+1, W=-1): ring 2 has flipped phi winding

If QNG is chirality-sensitive: the two scenarios produce different separation trends
If QNG is chirality-blind: both scenarios produce identical separation trajectories

This is a binary structural prediction that does not require rho_0 or physical units.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng_ring_force_linear_reference.py](../../tests/cpu/qng_ring_force_linear_reference.py) — QNG-CPU-048
- [qng_ring_chirality_reference.py](../../tests/cpu/qng_ring_chirality_reference.py)

## Experimental design

**Lattice:** L=24, N=13824

**Rings:** R=4, Ring 1 at z=6 (W=+1 always), Ring 2 at z=18
**Separation:** 12 lattice units

**Three scenarios, all epsilon=0.005:**
1. `same`     — W=+1, W=+1 (both same chirality)
2. `opposite` — W=+1, W=-1 (ring 2 flipped)
3. `single`   — W=+1 only (drift reference, same as CPU-048)

**One baseline (epsilon=0.000):**
4. `same_eps0` — W=+1, W=+1, no Channel E (structural baseline)

**Winding initialization:**
- W=+1: phi = atan2(dz, rho - R)
- W=-1: phi = atan2(-dz, rho - R)  [z-component flipped]

**Protocol:** Phase 1 (300 steps, Channel F off), Phase 2 (3000 steps, Channel F on).
Zone-restricted detection: Ring 1 in z∈[0,11], Ring 2 in z∈[12,23].
Separation S(t) = min(|z2-z1|, L-|z2-z1|) recorded every 100 steps.

## Checks

**Check 1 — Both rings detectable throughout Phase 2 in both chirality scenarios:**
```
All checkpoints T=100..3000: ring1 detectable in same scenario AND opposite scenario
```

**Check 2 — Chirality comparison gives a definite answer:**
```
|sep_final(same) - sep_final(opposite)| > 2  → chirality-SENSITIVE
|sep_final(same) - sep_final(opposite)| <= 2 → chirality-BLIND
```
Either outcome is a valid finding. The experiment is designed to distinguish them.

**Check 3 — Both scenarios differ from baseline (informational):**
```
|sep_final(same, eps=0.005) - sep_final(same, eps=0.000)| > 1  (Channel E active)
```

**Check 4 — Trend direction per scenario (informational):**
```
Report: ATTRACTION / REPULSION / NEUTRAL for same and opposite separately.
```

## Decision rule

**Overall PASS** if Check 1 passes (structural) AND either:
- Check 2 gives sep_diff > 2 (chirality-sensitive finding confirmed), OR
- Check 2 gives sep_diff ≤ 2 with low variance (chirality-blind finding confirmed)

**Interpretation:**
- sep_final(same) ≠ sep_final(opposite) → phi topology of ring 2 matters;
  QNG force distinguishes particle from antiparticle at this separation
- sep_final(same) ≈ sep_final(opposite) → chi field is chirality-blind;
  the scalar chi field dominates; winding only matters at shorter separations
  or requires direct phi-phi coupling (not just chi-phi)

## Artifact paths

- `07_validation/audits/qng-ring-chirality-reference-v1/report.json`
- `07_validation/audits/qng-ring-chirality-reference-v1/summary.md`
