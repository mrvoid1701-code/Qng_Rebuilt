# QNG-GPU-001

Type: `test`
ID: `QNG-GPU-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Probe the local GPU environment before writing accelerated QNG kernels.

## Category

`validation infrastructure`

## Hardware

`GPU`

## Target

Collect local availability data for:

- `nvidia-smi`
- `cupy`
- `torch`

## Reference implementation

- `tests/gpu/gpu_env_probe.py`

## Artifacts

- `07_validation/audits/gpu-env-probe-v1/report.json`
