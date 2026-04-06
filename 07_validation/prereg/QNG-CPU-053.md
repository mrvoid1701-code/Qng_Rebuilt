# QNG-CPU-053

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Ring force clean measurement — opposite chirality W+W- at d=8,10,12 with 6000 steps

## Purpose

QNG-CPU-050 showed attraction signal at d=8,10,12 but trajectories were noisy
(N=1 run each). QNG-CPU-049 showed opposite-chirality attraction (early=11.6,
late=6.7) but also noisy.

This test runs N=3 independent trials per separation and takes median statistics
to suppress drift noise. The single-ring drift reference (CPU-051 finding: rings
wander under eps=0.005) is the main confound; multiple trials give the
signal-to-noise ratio.

Target separations d=8,10 (peak attraction from CPU-050) and d=12 (CPU-049
reference). All opposite chirality W+W-.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng_ring_chirality_reference.py](../../tests/cpu/qng_ring_chirality_reference.py) — QNG-CPU-049
- [qng_ring_force_clean_reference.py](../../tests/cpu/qng_ring_force_clean_reference.py)

## Experimental design

**Lattice:** L=24, N=13824

**Separations:** d=8 (ring1 z=8, ring2 z=16), d=10 (ring1 z=7, ring2 z=17), d=12 (ring1 z=6, ring2 z=18)

**Chirality:** W+W- (opposite) — confirmed attractor from CPU-049.

**Trials:** N_trials=3 per separation. Each trial uses a fresh initialization
(Phase 1 produces slightly different equilibrated states due to internal lattice
dynamics, giving independent samples).

**Phase 2 steps:** 6000 (double CPU-049) for better trend statistics.

**Force observable per trial:**
```
attraction_score = mean(sep, T in [1500,3000]) - mean(sep, T in [3000,6000])
```
Positive = separation decreasing over time (attraction maintained).

**Aggregate per separation:**
```
median_score = median of [score_trial1, score_trial2, score_trial3]
```

**Single-ring control:** 3 trials of single ring W+ with eps=0.005 to measure drift amplitude.

## Checks

**Check 1 — Rings survive 6000 steps in all trials:**
```
z1 detectable at T=6000 for all trials and all separations.
```

**Check 2 — Median attraction score positive at d=10:**
```
median_score(d=10) > 0.5
```
(d=10 was peak from CPU-050)

**Check 3 — Force signal exceeds single-ring drift:**
```
median_score(d=10) > single_ring_drift_amplitude
```
where single_ring_drift_amplitude = std(sep of single ring over Phase-2 T=[1000,6000]).

**Check 4 — Monotonic score decrease with d (informational):**
```
Report: does score(d=8) > score(d=10) > score(d=12)?
```

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass.

## Artifact paths

- `07_validation/audits/qng-ring-force-clean-v1/report.json`
- `07_validation/audits/qng-ring-force-clean-v1/summary.md`
