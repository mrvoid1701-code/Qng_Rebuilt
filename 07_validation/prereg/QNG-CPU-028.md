# QNG-CPU-028

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

QM semigroup closure proxy test

## Purpose

Test whether the rebuilt QM propagator lane satisfies an approximate semigroup
closure property under three-step composition, and whether the per-step overlap
decay is controlled.

## Inputs

- [qng-qm-semigroup-closure-proxy-v1.md](../../03_gr_qm_bridge/qng-qm-semigroup-closure-proxy-v1.md)
- [qng_qm_semigroup_closure_reference.py](../../tests/cpu/qng_qm_semigroup_closure_reference.py)

## Checks

1. diagonal three-step composition must reconstruct the three-step target exactly
2. dressed three-step composition must remain bounded (`max_row_sum < 3.0`)
3. dressed three-step composition must align with the three-step target (`overlap > 0.95`)
4. dressed three-step composition must remain nontrivially different from diagonal (`l1 > 0.25`)
5. per-step decay ratio must be stable (`ov_3 / ov_2 > 0.93`)
6. three-step composition must retain phase sensitivity

## Decision rule

Pass if all preregistered checks pass.
