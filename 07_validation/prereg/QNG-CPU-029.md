# QNG-CPU-029

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

GR tensorial assembly proxy test

## Purpose

Test whether the rebuilt GR lane can produce two individually meaningful
linearized Einstein-tensor components (`E_tt`, `E_xx`) with differential
source alignment — moving beyond the single scalar `R_lin`.

## Inputs

- [qng-gr-tensorial-assembly-proxy-v1.md](../../03_gr_qm_bridge/qng-gr-tensorial-assembly-proxy-v1.md)
- [qng_gr_tensorial_assembly_reference.py](../../tests/cpu/qng_gr_tensorial_assembly_reference.py)

## Checks

1. both `E_tt` and `E_xx` must be individually bounded (`max_abs < 0.25`)
2. `E_tt` and `E_xx` must be nontrivially different (`l1 > 0.10`)
3. `E_xx` must correlate more with `Q_src` than `E_tt` does
4. `E_tt` and `E_xx` must have opposite-sign alignment with `Q_src` (`corr_e_xx_q_src - corr_e_tt_q_src > 0.10`)
5. traceless part must be nontrivially nonzero (`mean abs > 0.001`)
6. both components must retain history imprint (`l1 > 0.05` each)

## Decision rule

Pass if all preregistered checks pass.
