# QNG-CPU-030

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Quasi-static point source: screened Poisson profile and generation order slaving

## Purpose

Verify that the v3 update law (`DER-QNG-015`) recovers the quasi-static screened Poisson
structure predicted by the C_eff field equation (`DER-QNG-012`) when a localized coherence
source is applied to a 1D ring graph. Specifically:

1. A forced sigma depletion at the source node creates a coherence deficit that decays
   away from the source, consistent with exponential (Yukawa) falloff in 1D.
2. The observed screening length matches the predicted value
   `λ_pred = sqrt(β / (z·α))` within 30%.
3. With `δ > 0`, chi is elevated near the source (generation order signal visible
   in the spatial profile).
4. The chi profile correlates positively with the local sigma deficit
   (generation order direction confirmed spatially).
5. The G_QNG formula `G_QNG = β·Δu² / (z·t_s)` (in substrate units with
   `a·a_sigma = 2π`) is positive and finite for the test parameters.

## Inputs

- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng-ceff-field-equation-v1.md](../../04_qng_pure/qng-ceff-field-equation-v1.md)
- [qng-generation-order-v1.md](../../04_qng_pure/qng-generation-order-v1.md)
- [qng_quasi_static_source_reference.py](../../tests/cpu/qng_quasi_static_source_reference.py)

## Checks

1. sigma profile decays monotonically from source: sigma increases with ring distance from source
2. exponential fit quality: R² of log-linear fit to |δ_sigma(r)| > 0.80 for r in [2, 15]
3. observed screening length within 30% of predicted: `|λ_obs/λ_pred - 1| < 0.30`
4. chi elevated near source: mean |χ| for r ≤ 3 is greater than mean |χ| for r ≥ 10
5. generation order direction: correlation between σ_ref - σ(r) and χ(r) > 0.60 across all nodes
6. G_QNG substrate formula gives a positive finite value

## Decision rule

Pass if all preregistered checks pass.
