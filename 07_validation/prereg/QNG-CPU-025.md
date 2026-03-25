# QNG-CPU-025

Type: `test`
ID: `QNG-CPU-025`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check the upgraded two-channel bridge closure and source-response step.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct the upgraded bridge with coherence/transport and density-source channels and verify:

- bounded upgraded closure
- nontrivial difference from v1 closure
- phase sensitivity
- history imprint
- improved source-response fit over v1
- nonzero second source coefficient

## Reference implementation

- `tests/cpu/qng_bridge_closure_v2_reference.py`

## Artifacts

- `07_validation/audits/qng-bridge-closure-v2-reference-v1/report.json`
- `07_validation/audits/qng-bridge-closure-v2-reference-v1/summary.md`
