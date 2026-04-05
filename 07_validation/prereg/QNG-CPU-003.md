# QNG-CPU-003

Type: `test`
ID: `QNG-CPU-003`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check that the first rebuilt effective-field split can be extracted from native QNG rollout data in a bounded and structurally meaningful way.

## Category

`qng core`

## Hardware

`CPU`

## Target

From native rollout outputs, construct:

- `C_eff`
- `L_eff`

and verify:

- boundedness
- structural alignment with native ingredients
- distinguishability between history-enabled and present-only runs

## Reference implementation

- `tests/cpu/qng_effective_field_reference.py`

## Artifacts

- `07_validation/audits/qng-effective-field-reference-v1/report.json`
- `07_validation/audits/qng-effective-field-reference-v1/summary.md`
