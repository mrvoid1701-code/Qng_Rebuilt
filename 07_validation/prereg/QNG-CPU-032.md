# QNG-CPU-032

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Back-reaction self-consistency — single-iteration contraction proxy

## Purpose

Test whether the three-channel closure v3 admits a proxy fixed point
under a 10% phase perturbation. A contracting response (gamma < 1)
is the first evidence that the closure approaches a self-consistent
semiclassical state.

## Inputs

- [qng-gr-backreaction-selfconsistency-v1.md](../../03_gr_qm_bridge/qng-gr-backreaction-selfconsistency-v1.md)
- [qng_gr_backreaction_selfconsistency_reference.py](../../tests/cpu/qng_gr_backreaction_selfconsistency_reference.py)

## Checks

1. response nontrivial: `||delta_BR||_L1 > 1e-5`
2. contraction: `gamma < 1.0`
3. tensorial sign preserved for E_xx: `sign(e_xx') == sign(e_xx)` (`e_xx < 0`)
4. tensorial sign preserved for E_tt: `sign(e_tt') == sign(e_tt)` (`e_tt > 0`)
5. history imprint survives perturbation: `||Psi_BR3'_hist - Psi_BR3'_nohist||_L1 > 0.03`

## Decision rule

Pass if all preregistered checks pass.
