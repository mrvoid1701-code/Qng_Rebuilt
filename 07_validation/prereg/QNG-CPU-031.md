# QNG-CPU-031

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

GR back-reaction closure v3 — three-channel tensorial closure test

## Purpose

Test the first back-reaction closure that incorporates the QM propagator
dressing excess channel, and verify it against the individual tensor
components `E_tt` and `E_xx` for the first time.

## Inputs

- [qng-gr-backreaction-closure-v3.md](../../03_gr_qm_bridge/qng-gr-backreaction-closure-v3.md)
- [qng_gr_backreaction_closure_v3_reference.py](../../tests/cpu/qng_gr_backreaction_closure_v3_reference.py)

## Checks

1. `Psi_BR3` remains bounded (`max_abs < 0.15`)
2. `Psi_BR3` is nontrivially different from `Psi_BR2` (`l1 > 5e-4`)
3. propagator channel coefficient for `E_xx` is nonzero (`|e_xx| > 1e-3`)
4. propagator channel coefficients differ between components (`|e_xx - e_tt| > 1e-3`)
5. 4-channel `E_xx` fit improves over 3-channel fit (`ratio_4ch < ratio_3ch`)
6. history imprint retained on `Psi_BR3` (`l1 > 0.05`)

## Decision rule

Pass if all preregistered checks pass.
