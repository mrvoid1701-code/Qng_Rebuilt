# QNG-CPU-020

Type: `test`
ID: `QNG-CPU-020`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check the first source-response consistency step of the rebuilt QNG bridge.

## Category

`bridge`

## Hardware

`CPU`

## Target

Fit the linearized-curvature proxy against:

- geometry-only baseline
- geometry plus bridge source channel

and verify:

- substantial source-augmented improvement
- nonzero source coefficient
- history imprint

## Reference implementation

- `tests/cpu/qng_source_response_consistency_reference.py`

## Artifacts

- `07_validation/audits/qng-source-response-consistency-reference-v1/report.json`
- `07_validation/audits/qng-source-response-consistency-reference-v1/summary.md`
