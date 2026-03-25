# QNG-CPUGPU-002

Type: `test`
ID: `QNG-CPUGPU-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check numerical agreement between the CPU reference rollout and the first GPU rollout for the same native QNG update law.

## Category

`validation infrastructure`

## Hardware

`CPU+GPU`

## Target

Confirm that CPU and GPU executions agree for:

- `use_history = true`
- `use_history = false`

under the same graph, seed, initial state, and update parameters.

## Pass condition

The maximum absolute CPU/GPU discrepancy across tracked state channels must remain below a declared tolerance.

## Reference implementation

- `tests/gpu/qng_cpu_gpu_agreement.py`

## Artifacts

- `07_validation/audits/qng-cpu-gpu-agreement-v1/report.json`
- `07_validation/audits/qng-cpu-gpu-agreement-v1/summary.md`
