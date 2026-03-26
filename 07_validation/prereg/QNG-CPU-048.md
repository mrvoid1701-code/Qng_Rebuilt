# Prereg QNG-CPU-048

Type: `prereg`
ID: `QNG-CPU-048`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-030`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether degree-normalizing the multi-channel divergence current restores
N-stability of R²_combined across N ∈ {8, 16, 32}.

Degree-normalized current:
```
divN(J_X)_i = (1/deg_i) · C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · Δf_{ij}
```
where deg_i = |neighbors(i)|.

Multi-channel regression (same OLS as CPU-046/047):
```
Δρ + α_phi·divN(J_phi) + α_mis·divN(J_mis) + α_mem·divN(J_mem) ≈ 0
```

Seeds: [20260325, 42, 137, 1729, 2718]
N values: [8, 16, 32]

## Reference values (from QNG-CPU-047, unnormalized)

| N  | mean R²_combined | mean_degree |
|----|-----------------|-------------|
| 8  | 0.5864          | 3.20        |
| 16 | 0.4053          | 4.33        |
| 32 | 0.2688          | 6.92        |

N-stability metric (unnormalized): cv_N = 0.369

## Locked predictions

### P1: mean R²_combined(N=32) ≥ 0.30 with normalization

Rationale: Without normalization, N=32 gives 0.269 (below 0.30 threshold).
Degree normalization removes the dominant N-scaling factor (degree ratio N32/N16 ≈ 1.6).
If degree-dilution is the main cause, normalized R² should recover to ≥0.30 at N=32.

### P2: cv_N(R²_norm) < cv_N(R²_std) = 0.369

Rationale: Normalization removes the degree-scaling component → std(R² across N)
should decrease relative to mean → smaller coefficient of variation.

### P3: multi-channel beats single-channel at N=32, ≥4/5 seeds

Rationale: Degree normalization preserves relative channel structure.
The topology-selective preference is a relational property (phi vs mismatch vs mem),
not an absolute scale property. So combination should still beat single at N=32.

### P4: mean R²_norm(N=32) > mean R²_std(N=32) = 0.269

Rationale: Normalization compensates degree-dilution directly.
Any recovery of the lost signal should appear as R²_norm > R²_std at N=32.

## Falsification conditions

- FAIL if R²_norm(N=32) < R²_std(N=32) = 0.269 (normalization makes things worse)
- FAIL if cv_N(R²_norm) > cv_N(R²_std) (normalization increases N-variance)

A partial pass (≥2/4) distinguishes "degree-dilution is the dominant effect"
from "structural changes at large N overwhelm degree correction."
