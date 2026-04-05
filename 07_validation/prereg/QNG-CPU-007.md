# QNG-CPU-007

Type: `test`
ID: `QNG-CPU-007`
Status: `draft`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Objective

Check that the first rebuilt trajectory lag proxy is nontrivial, history-sensitive, and direction-sensitive.

## Category

`phenomenology`

## Hardware

`CPU`

## Target

From rebuilt QNG quantities, construct:

- `L_eff`
- `a_QNG`
- `A_trj`
- `S_trj`

and verify:

- nontrivial lag strength
- history imprint
- directional sign reversal under acceleration reversal

## Reference implementation

- `tests/cpu/qng_trajectory_lag_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-trajectory-lag-proxy-reference-v1/report.json`
- `07_validation/audits/qng-trajectory-lag-proxy-reference-v1/summary.md`
