# QNG-CPU-023

Type: `test`
ID: `QNG-CPU-023`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check the first density-source balance law of the rebuilt QNG QM recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Verify that the rebuilt local generator induces a source-dominated density balance:

- exact source reconstruction of `delta rho`
- nontrivial source strength
- sub-leading transport coefficient in a transport-corrected fit
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_density_source_balance_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-density-source-balance-reference-v1/report.json`
- `07_validation/audits/qng-qm-density-source-balance-reference-v1/summary.md`
