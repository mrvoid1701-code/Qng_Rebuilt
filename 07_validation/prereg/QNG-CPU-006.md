# QNG-CPU-006

Type: `test`
ID: `QNG-CPU-006`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check that the first QNG-to-QM coherence proxy produces bounded, phase-sensitive, and history-sensitive correlator-like observables.

## Category

`bridge`

## Hardware

`CPU`

## Target

Build from the rebuilt QNG rollout:

- `psi_QNG`
- nearest-neighbor `G_1`
- `J_QNG`

and verify:

- boundedness
- nontrivial transport
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_coherence_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-coherence-proxy-reference-v1/report.json`
- `07_validation/audits/qng-qm-coherence-proxy-reference-v1/summary.md`
