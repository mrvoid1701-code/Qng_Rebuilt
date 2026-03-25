# QNG-CPU-004

Type: `test`
ID: `QNG-CPU-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check that the first geometry estimator built from `C_eff` produces a positive and history-sensitive local geometric proxy.

## Category

`qng core`

## Hardware

`CPU`

## Target

From `C_eff`, build the reference local geometry proxy and verify:

- positive definiteness
- coherence-curvature sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_geometry_estimator_reference.py`

## Artifacts

- `07_validation/audits/qng-geometry-estimator-reference-v1/report.json`
- `07_validation/audits/qng-geometry-estimator-reference-v1/summary.md`
