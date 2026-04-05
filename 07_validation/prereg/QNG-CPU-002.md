# QNG-CPU-002

Type: `test`
ID: `QNG-CPU-002`
Status: `draft`
Author: `C.D Gabriel`
test_class: `internal_consistency`

## Objective

Run the first executable CPU reference model for the native QNG update law.

## Category

`QNG pure`

## Hardware

`CPU`

## Target

Validate the minimum commitments of `qng-native-update-law-v1`:

- boundedness
- one-step locality
- genuine dependence on history

## Reference implementation

- `tests/cpu/qng_native_update_reference.py`

## Gates

- `sigma_bounds_pass`
- `phi_bounds_pass`
- `history_bounds_pass`
- `locality_pass`
- `memory_sensitivity_pass`

## Artifacts

- `07_validation/audits/qng-native-update-reference-v1/report.json`
- `07_validation/audits/qng-native-update-reference-v1/summary.md`
