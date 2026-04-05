# QNG-CPU-008

Type: `test`
ID: `QNG-CPU-008`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check that the first rebuilt lensing proxy is bounded, nontrivial, geometry-sensitive, and history-sensitive.

## Category

`phenomenology`

## Hardware

`CPU`

## Target

From rebuilt weak-field quantities, construct:

- `Phi_lens`
- `alpha_lens`
- `D_lens`

and verify:

- boundedness
- nontrivial deflection
- geometry-gradient sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_lensing_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-lensing-proxy-reference-v1/report.json`
- `07_validation/audits/qng-lensing-proxy-reference-v1/summary.md`
