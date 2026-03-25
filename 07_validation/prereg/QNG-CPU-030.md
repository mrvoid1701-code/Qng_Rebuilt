# QNG-CPU-030

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`

## Title

GR tensorial source matching proxy test

## Purpose

Test whether fitting `E_tt` and `E_xx` separately with four-channel sources
produces a better combined residual than fitting the scalar `R_lin` alone,
and whether the transport-source coefficient has confirmed opposite sign
in the two components.

## Inputs

- [qng-gr-tensorial-source-matching-proxy-v1.md](../../03_gr_qm_bridge/qng-gr-tensorial-source-matching-proxy-v1.md)
- [qng_gr_tensorial_source_matching_reference.py](../../tests/cpu/qng_gr_tensorial_source_matching_reference.py)

## Checks

1. `E_xx` fits well with sources (`ratio_exx < 0.90`)
2. geometry coefficient for `E_xx` is positive: `a_xx > 0`
3. geometry coefficient for `E_tt` is negative: `a_tt < 0`
4. geometry sign separation is clear: `a_xx - a_tt > 1.0`
5. split model improves over scalar: `(ratio_exx + ratio_ett) / 2 < ratio_rlin`
6. history imprint retained: `l1_diff(pred_E_xx_hist, pred_E_xx_nohist) > 0.05`

## Decision rule

Pass if all preregistered checks pass.
