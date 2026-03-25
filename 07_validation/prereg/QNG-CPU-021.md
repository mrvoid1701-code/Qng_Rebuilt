# QNG-CPU-021

Type: `test`
ID: `QNG-CPU-021`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check the first operator-level assembly step of the rebuilt QNG QM recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct a first linear operator family on the rebuilt QNG QM state space and verify:

- bounded operator norms
- exact linearity on probe vectors
- nontrivial generator action
- nontrivial generator/transport commutator
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_operator_assembly_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-operator-assembly-reference-v1/report.json`
- `07_validation/audits/qng-qm-operator-assembly-reference-v1/summary.md`
