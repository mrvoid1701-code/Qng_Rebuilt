# QNG-CPU-035

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Einstein equations proxy — equation of state and cosmological constant identification

## Purpose

Test whether the linearized tensor components `E_tt` and `E_xx` satisfy a
proxy form of the Einstein equations consistent with a vacuum energy / dark
energy source (w ≈ -1), and whether the memory sector introduces a
measurable quantum correction to the effective equation of state.

## Inputs

- [qng-einstein-equations-proxy-v1.md](../../03_gr_qm_bridge/qng-einstein-equations-proxy-v1.md)
- [qng_einstein_equations_proxy_reference.py](../../tests/cpu/qng_einstein_equations_proxy_reference.py)

## Checks

1. `corr(E_tt, E_xx) < -0.8` with history
2. `w_eff ∈ (-1.5, -0.5)` with history (dark energy equation of state)
3. `|corr_hist| > |corr_nohist|` (history sharpens anti-correlation)
4. `|w_hist - w_nohist| > 0.1` (history shifts equation of state)
5. 4-channel source fit ratio for E_tt: `ratio_4ch_tt < 0.5`

## Decision rule

Pass if all preregistered checks pass.
