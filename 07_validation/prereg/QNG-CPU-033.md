# QNG-CPU-033

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Lorentzian signature proxy — memory-driven time/space metric asymmetry

## Purpose

Test whether the rebuilt QNG substrate generates a Lorentzian signature
proxy via opposite-sign linearized metric components `h_tt` and `h_xx`,
and whether the history/memory sector is the mechanism that drives this
signature.

## Inputs

- [qng-lorentzian-signature-proxy-v1.md](../../04_lorentzian/qng-lorentzian-signature-proxy-v1.md)
- [qng_lorentzian_signature_proxy_reference.py](../../tests/cpu/qng_lorentzian_signature_proxy_reference.py)

## Checks

1. `mean(D_sig) < 0` with history (signature discriminant negative)
2. `corr(h_tt, h_xx) < -0.5` with history (anti-correlated components)
3. fraction of nodes with `h_xx > 0 > 0.90` (spacelike robustness)
4. history amplifies discriminant: `|mean(D_sig)_hist| > 10 * |mean(D_sig)_nohist|`
5. history sharpens anti-correlation: `|corr_hist| > |corr_nohist|`

## Decision rule

Pass if all preregistered checks pass.
