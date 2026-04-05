# QNG-CPU-015

Type: `test`
ID: `QNG-CPU-015`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check the first linearized GR assembly consistency step of the rebuilt QNG recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Assemble a weak-field Lorentzian metric candidate from rebuilt QNG quantities and verify:

- Lorentzian sign pattern
- weak-field smallness
- metric-derived acceleration consistency
- history imprint

## Reference implementation

- `tests/cpu/qng_gr_linearized_assembly_reference.py`

## Artifacts

- `07_validation/audits/qng-gr-linearized-assembly-reference-v1/report.json`
- `07_validation/audits/qng-gr-linearized-assembly-reference-v1/summary.md`
