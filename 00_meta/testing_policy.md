# Testing Policy

Testing in this workspace is hardware-explicit from day one.

## Hardware classes

- `CPU`: deterministic or reference implementations
- `GPU`: accelerated implementations, large sweeps, tensor-heavy numerics
- `CPU+GPU`: cross-validation runs where the same theory object is checked on both paths

## Requirements for every test

Every test file must declare:

- `test_id`
- `category`
- `hardware`
- `inputs`
- `expected outputs`
- `pass/fail gates`
- `numerical tolerances`
- `artifact paths`

## CPU lane role

CPU is the canonical correctness lane.

Use CPU for:

- symbolic checks
- reference numerics
- small-scale reproducibility
- comparison baselines
- deterministic audits

## GPU lane role

GPU is the scale and stress lane.

Use GPU for:

- large graph sweeps
- spectral batches
- Monte Carlo ensembles
- parameter scans
- heavy linear algebra

## Cross-hardware rule

If a result exists in both CPU and GPU form:

- the CPU version defines correctness
- the GPU version must match within declared tolerance
- any mismatch is recorded as a validation issue, not patched silently

## Directory rule

- `tests/cpu/` contains CPU runners and references
- `tests/gpu/` contains GPU runners and acceleration wrappers
- `07_validation/` contains test specs and evidence, not the executable code itself
