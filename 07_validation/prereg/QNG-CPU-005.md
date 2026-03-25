# QNG-CPU-005

Type: `test`
ID: `QNG-CPU-005`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check that the first QNG-to-GR weak-field proxy map produces bounded, nontrivial, and history-sensitive GR-facing observables.

## Category

`bridge`

## Hardware

`CPU`

## Target

Build from the QNG geometry proxy:

- `h_00`
- `h_11`
- `Psi_QNG`
- `a_QNG`

and verify:

- weak-field smallness
- nontrivial acceleration structure
- history imprint

## Reference implementation

- `tests/cpu/qng_gr_weakfield_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-gr-weakfield-proxy-reference-v1/report.json`
- `07_validation/audits/qng-gr-weakfield-proxy-reference-v1/summary.md`
