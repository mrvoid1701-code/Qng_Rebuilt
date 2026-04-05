# QNG-CPU-018

Type: `test`
ID: `QNG-CPU-018`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check the first mode/spectrum assembly step of the rebuilt QNG QM recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct state and generator mode spectra from rebuilt QNG quantities and verify:

- Parseval consistency
- nontrivial generator spectrum
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_mode_spectrum_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-mode-spectrum-reference-v1/report.json`
- `07_validation/audits/qng-qm-mode-spectrum-reference-v1/summary.md`
