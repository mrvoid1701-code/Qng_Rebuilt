# QNG-CPU-010

Type: `test`
ID: `QNG-CPU-010`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check that the first rebuilt timing-delay proxy is bounded, nontrivial, memory-sensitive, and history-sensitive.

## Category

`phenomenology`

## Hardware

`CPU`

## Target

From rebuilt QNG quantities, construct:

- `T_edge`
- `D_time`
- `W_time`

and verify:

- boundedness
- nontrivial delay burden
- memory-switch sensitivity
- history imprint
- nontrivial distortion structure

## Reference implementation

- `tests/cpu/qng_timing_delay_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-timing-delay-proxy-reference-v1/report.json`
- `07_validation/audits/qng-timing-delay-proxy-reference-v1/summary.md`
