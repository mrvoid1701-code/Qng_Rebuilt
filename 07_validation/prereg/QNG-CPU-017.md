# QNG-CPU-017

Type: `test`
ID: `QNG-CPU-017`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check the first local generator assembly step of the rebuilt QNG QM recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Assemble a local complex update generator from two successive rebuilt QNG state candidates and verify:

- boundedness
- nontriviality
- exact next-step reconstruction
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_generator_assembly_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-generator-assembly-reference-v1/report.json`
- `07_validation/audits/qng-qm-generator-assembly-reference-v1/summary.md`
