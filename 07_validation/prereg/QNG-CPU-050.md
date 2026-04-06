# QNG-CPU-050

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Ring force vs separation — Yukawa profile at force level (opposite chirality)

## Purpose

QNG-CPU-049 confirmed that opposite-chirality rings (W+W-) attract and
same-chirality rings (W+W+) repel. The attraction signal was cleaner (Δ=4.9).

The chi field between rings is Yukawa-screened with λ=3.41 lattice units
(confirmed by DER-QNG-019, QNG-CPU-036). If the force between rings is
mediated by the chi field, the force strength should decay as:

```
force_strength ~ exp(-d / lambda)
```

This test measures the attraction signal (W+W-) at five separations
d = 4, 6, 8, 10, 12 and checks whether the decay is consistent with
the Yukawa profile λ=3.41.

**Prediction:** force signal decreases monotonically with d; ratio of
adjacent separations consistent with exp(-Δd/λ).

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng_ring_chirality_reference.py](../../tests/cpu/qng_ring_chirality_reference.py) — QNG-CPU-049
- [qng_ring_force_separation_reference.py](../../tests/cpu/qng_ring_force_separation_reference.py)

## Experimental design

**Lattice:** L=24, N=13824

**Chirality:** W=+1 (ring 1) and W=-1 (ring 2) — opposite chirality only.
Same-chirality baseline run at d=12 for comparison.

**Separations tested:**
- d=4  (ring1 z=10, ring2 z=14) — 1.2λ
- d=6  (ring1 z=9,  ring2 z=15) — 1.8λ
- d=8  (ring1 z=8,  ring2 z=16) — 2.3λ
- d=10 (ring1 z=7,  ring2 z=17) — 2.9λ
- d=12 (ring1 z=6,  ring2 z=18) — 3.5λ  (CPU-049 baseline)

All rings centered at (L/2, L/2), R=4, epsilon=0.005.

**Force observable:** attraction_score = mean_early_sep - mean_late_sep
(positive = attraction, negative = repulsion)
where early = T∈[100,500], late = T∈[1000,3000].

**Protocol:** Phase 1 (300 steps), Phase 2 (3000 steps), check every 100 steps.

**Yukawa prediction:** attraction_score(d) ~ A × exp(-d / lambda_fit)
Fit lambda_fit from the 5 data points; compare to lambda_theory = 3.41.

## Checks

**Check 1 — Both rings detectable at all separations:**
```
All 5 separation runs: rings detectable throughout Phase 2.
```

**Check 2 — Attraction signal decreases monotonically with d:**
```
attraction_score(d=4) > attraction_score(d=6) > ... > attraction_score(d=12)
(or at least monotonically non-increasing with one allowed violation)
```

**Check 3 — Yukawa fit gives lambda_fit consistent with lambda_theory:**
```
|lambda_fit - lambda_theory| / lambda_theory < 0.5
(lambda_theory = 3.41)
```

**Check 4 — Attraction at d=12 matches CPU-049 (reproducibility):**
```
|attraction_score(d=12) - cpu049_score| < 3
```

## Decision rule

**Overall PASS** if Checks 1, 2 pass.

Check 3 is the key physics result: if lambda_fit ≈ 3.41, the force law is
confirmed as Yukawa-mediated with the correct screening length. If lambda_fit
differs significantly, the force has a different spatial structure than the
chi field profile predicts.

## Artifact paths

- `07_validation/audits/qng-ring-force-separation-v1/report.json`
- `07_validation/audits/qng-ring-force-separation-v1/summary.md`
