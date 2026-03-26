# Prereg QNG-CPU-046

Type: `prereg`
ID: `QNG-CPU-046`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-028`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether jointly regressing Δρ on all three current channels simultaneously
gives R²_combined >> max(R²_phi, R²_mis, R²_mem) per seed.

Multi-channel continuity ansatz:
```
Δρ ≈ -(α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem))
```
where:
- div(J_phi)_i = C_eff_i · Σ_j C_eff_j · sin(phi_j - phi_i)
- div(J_mis)_i = C_eff_i · Σ_j C_eff_j · (mismatch_j - mismatch_i)
- div(J_mem)_i = C_eff_i · Σ_j C_eff_j · (mem_j - mem_i)

Solved by 3×3 OLS normal equations.

Seeds: [20260325, 42, 137, 1729, 2718]

## Motivation from CPU-045 results

Single-channel best R² per seed:
- seed 20260325: phi 0.046
- seed 42:       mis 0.354
- seed 137:      phi 0.572
- seed 1729:     mem 0.101
- seed 2718:     phi 0.207

If channels are partially independent across topologies, combination should
improve over the single-channel bests, particularly on seeds where a dominant
channel exists and secondary channels add complementary information.

## Locked predictions

### P1: R²_combined > max(R²_phi, R²_mis, R²_mem) on ≥4/5 seeds

Rationale: Topology-selective preference in CPU-045 implies channels carry
different information per topology. Joint OLS must improve R² when channels
have non-trivial partial correlation with Δρ conditional on other channels.

### P2: mean R²_combined > 0.35

Rationale: If combination captures seed-42 mismatch (0.354), seed-137 phi (0.572),
and seed-1729 mem (0.101) while not degrading other seeds, weighted mean
should exceed 0.35 (well above single-channel mean of 0.20).

### P3: max R²_combined > 0.60

Rationale: Seed 137 already has phi=0.572. Adding mismatch and mem channels
as secondary contributors should push R² above 0.60 on that seed.

### P4: R²_combined > 0.30 on ≥3/5 seeds

Rationale: Seeds 42 (best=0.354), 137 (best=0.572), 2718 (best=0.207) all
already approach or exceed 0.30 with single channels. Combination should
consolidate these into ≥0.30 on all three seeds.

## Falsification conditions

- FAIL if R²_combined ≤ max(R²_single) on ≥4/5 seeds (channels carry same info)
- FAIL if P1, P2, P3, P4 all fail (implies framework, not channel selection, is wrong)

A partial pass (≥2/4) distinguishes "channels carry some independent info"
from "framework is fundamentally wrong."

## Reference single-channel values (from QNG-CPU-045)

| Seed     | R²_phi   | R²_mis   | R²_mem   | best     |
|----------|----------|----------|----------|----------|
| 20260325 | 0.045617 | 0.012993 | 0.040113 | 0.045617 |
| 42       | 0.138356 | 0.353832 | 0.048822 | 0.353832 |
| 137      | 0.572227 | 0.001800 | 0.044895 | 0.572227 |
| 1729     | 0.034704 | 0.021469 | 0.101066 | 0.101066 |
| 2718     | 0.207112 | 0.208248 | 0.038489 | 0.208248 |
| mean     | 0.199603 | 0.119668 | 0.054677 | 0.256198 |
