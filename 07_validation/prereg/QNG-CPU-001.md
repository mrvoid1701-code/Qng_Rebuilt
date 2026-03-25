# QNG-CPU-001

Type: `test`
ID: `QNG-CPU-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Run the first CPU-side structural audit suite after `qng-native-update-law-v1`.

## Category

`QNG pure`

## Hardware

`CPU`

## Scope

This first test phase audits theory structure rather than numerics.

## Checks

- `theory_purity_audit.py`
- `dependency_audit.py`

## Pass condition

- GR pure contains no QNG-native forbidden terms
- QM pure contains no QNG-native forbidden terms
- all substantive theory docs contain explicit inputs/dependency markers where expected

## Artifacts

- console logs
- later: static audit summary in `07_validation/audits/`
