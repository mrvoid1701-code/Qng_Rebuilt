# QNG-CPU-019

Type: `test`
ID: `QNG-CPU-019`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check the first linearized-curvature consistency step of the rebuilt QNG GR recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct the linearized curvature proxy from the assembled weak-field metric candidate and verify:

- boundedness
- geometry-sector correlation
- acceleration-gradient correlation
- history imprint

## Reference implementation

- `tests/cpu/qng_gr_linearized_curvature_reference.py`

## Artifacts

- `07_validation/audits/qng-gr-linearized-curvature-reference-v1/report.json`
- `07_validation/audits/qng-gr-linearized-curvature-reference-v1/summary.md`
