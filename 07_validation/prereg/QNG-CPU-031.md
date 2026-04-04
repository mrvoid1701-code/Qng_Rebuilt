# QNG-CPU-031

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Quasi-static point source in 3D: screened Poisson profile, G_QNG scaling with z, generation order

## Purpose

Verify that the v3 update law on a 3D cubic lattice (6×6×6 = 216 nodes, periodic boundary
conditions, z=6) reproduces the screened Poisson structure and the correct G_QNG scaling
predicted by `DER-QNG-012` and `DER-QNG-015`.

This test does NOT attempt to show a Φ ~ 1/r profile (insufficient radial range on a small
lattice). It tests structural predictions only:

1. The sigma profile decays exponentially from the source with the 3D-corrected screening
   length `λ_pred_3D = sqrt(β/(z·α))` where z=6.
2. `G_QNG_3D / G_QNG_1D = z_1D / z_3D = 2/6 = 1/3` — a direct prediction of the formula
   `G_QNG = β·Δu²/(z·t_s)`.
3. Generation order σ → χ operates correctly in 3D geometry.
4. The quasi-static Poisson residual is small in the bulk (field equation satisfied).

## Inputs

- [qng-native-update-law-v3.md](../../04_qng_pure/qng-native-update-law-v3.md)
- [qng-ceff-field-equation-v1.md](../../04_qng_pure/qng-ceff-field-equation-v1.md)
- [qng-generation-order-v1.md](../../04_qng_pure/qng-generation-order-v1.md)
- [qng_quasi_static_3d_light_reference.py](../../tests/cpu/qng_quasi_static_3d_light_reference.py)

## Checks

1. sigma profile decays monotonically from source at r=1, 2, 3
2. exponential fit quality: R² > 0.75 on available radial bins (fewer points than 1D)
3. observed 3D screening length within 30% of predicted: `λ_pred_3D = sqrt(β/(6·α))`
4. G_QNG ratio: `G_QNG_3D / G_QNG_1D` within 20% of predicted value `1/3`
5. generation order spatial correlation: `corr(σ_ref − σ_i, χ_i) > 0.60` across all nodes
6. quasi-static Poisson residual: mean `|β·(σ̄_i − σ_i) − α·(σ_i − σ_ref)|` < 0.01 for bulk nodes (r ≥ 2)

## Decision rule

Pass if all preregistered checks pass.
