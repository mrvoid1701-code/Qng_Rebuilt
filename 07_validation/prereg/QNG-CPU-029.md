# QNG-CPU-029

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Generation order cross-coupling: sigma → chi slaving in the static limit

## Purpose

Verify that the v3 update law (`DER-QNG-015`) correctly implements the generation order `σ → χ`:

1. With `delta = 0`, the v3 law is numerically identical to the v2 reference.
2. With `delta > 0`, chi accumulates a non-zero signal when sigma departs from reference, and is zero when sigma is at reference.
3. In the quasi-static approximation, the load field `L_eff` satisfies the slaving relation `L_eff ≈ -(delta/alpha) * delta_C` derived in `DER-QNG-014`.
4. `M_eff` is negatively correlated with `delta_C` (coherence deficit drives matter proxy).
5. The contractiveness condition `alpha + beta + delta < 1` is satisfied for all test configurations.

## Inputs

- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng-generation-order-v1.md](../../04_qng_pure/qng-generation-order-v1.md)
- [qng_generation_order_reference.py](../../tests/cpu/qng_generation_order_reference.py)

## Checks

1. v3 with `delta = 0` must match v2 output exactly (`max_diff < 1e-12`)
2. chi signal with `delta > 0` must be non-zero when sigma is perturbed from reference (`|mean_chi| > 0.001`)
3. chi signal with `delta > 0` must be near zero when sigma = sigma_ref everywhere (`|mean_chi| < 1e-6`)
4. slaving ratio `L_eff / (-delta_C)` must be within 20% of the predicted value `delta/alpha` (`|ratio - delta/alpha| / (delta/alpha) < 0.20`)
5. Pearson correlation between `M_eff` and `-delta_C` must be positive and significant (`correlation > 0.80`)
6. contractiveness condition `alpha + beta + delta < 1` must hold for the test configuration

## Decision rule

Pass if all preregistered checks pass.
