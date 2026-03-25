# QNG-CPU-016

Type: `test`
ID: `QNG-CPU-016`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check the first source-augmented continuity-style QM assembly step of the rebuilt QNG recovery program.

## Category

`bridge`

## Hardware

`CPU`

## Target

Construct a complex state-density, current candidate, and source candidate from rebuilt QNG quantities and verify:

- bounded density
- nontrivial current
- continuity-style residual improvement
- source-augmented residual improvement
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_qm_continuity_assembly_reference.py`

## Artifacts

- `07_validation/audits/qng-qm-continuity-assembly-reference-v1/report.json`
- `07_validation/audits/qng-qm-continuity-assembly-reference-v1/summary.md`
