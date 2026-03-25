# QNG-CPU-024

Type: `test`
ID: `QNG-CPU-024`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check the first propagator proxy step of the rebuilt QNG QM recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct the first one-step propagator proxy family and verify:

- exact diagonal reconstruction of the next-step state
- bounded transport-dressed propagator
- nontrivial dressing effect
- phase sensitivity
- history imprint
- alignment of the dressed action with the recovered target state

## Reference implementation

- `tests/cpu/qng_qm_propagator_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-propagator-proxy-reference-v1/report.json`
- `07_validation/audits/qng-qm-propagator-proxy-reference-v1/summary.md`
