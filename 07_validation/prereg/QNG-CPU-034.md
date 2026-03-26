# QNG-CPU-034

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

Light cone proxy — per-node effective speed of light from linearized metric

## Purpose

Test whether the linearized Lorentzian metric produces a well-defined
per-node null speed `c_eff(i) = sqrt(-g_tt(i)/g_xx(i))`, close to
flat-space normalization but with spatial variation amplified by history.

## Inputs

- [qng-light-cone-proxy-v1.md](../../04_lorentzian/qng-light-cone-proxy-v1.md)
- [qng_light_cone_proxy_reference.py](../../tests/cpu/qng_light_cone_proxy_reference.py)

## Checks

1. `c_eff(i) > 0` on all nodes (null cone well-defined)
2. `mean(c_eff)` in `(0.9, 1.1)` (near normalized speed of light)
3. `std(c_eff) > 1e-3` (nontrivial spatial variation)
4. history shifts mean: `|mean_hist - mean_nohist| > 1e-3`
5. history amplifies variation: `std_hist > std_nohist`

## Decision rule

Pass if all preregistered checks pass.
