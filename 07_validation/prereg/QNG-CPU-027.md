# QNG-CPU-027

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

QM propagator composition proxy test

## Purpose

Test whether the rebuilt QM propagator lane supports a disciplined two-step composition story.

## Inputs

- [qng-qm-propagator-composition-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-propagator-composition-proxy-v1.md)
- [qng_qm_propagator_composition_reference.py](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/tests/cpu/qng_qm_propagator_composition_reference.py)

## Checks

1. diagonal two-step composition must reconstruct the recovered two-step target
2. dressed two-step composition must remain bounded
3. dressed two-step composition must remain strongly aligned with the recovered target
4. dressed two-step composition must remain nontrivially different from diagonal composition
5. composition must retain phase sensitivity
6. composition must retain history imprint

## Decision rule

Pass if all preregistered checks pass.
