# Prereg QNG-CPU-045

Type: `prereg`
ID: `QNG-CPU-045`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-027`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether replacing the phase-difference current `J_phi = C_i·C_j·sin(Δφ)` with
a mismatch-gradient current `J_mis = C_i·C_j·(mismatch_j − mismatch_i)` gives
better calibrated continuity balance.

Also tests memory-gradient current `J_mem = C_i·C_j·(mem_j − mem_i)` for comparison.

Construction:
- `div(J_mis)_i = C_eff_i · Σ_j C_eff_j · (mismatch_j − mismatch_i)`
- `div(J_mem)_i = C_eff_i · Σ_j C_eff_j · (mem_j − mem_i)`
- `α*_X = −Σ(Δρ · div(J_X)) / Σ(div(J_X)²)` where `ρ = C_eff²`
- `R²_X = 1 − Var(Δρ + α*_X · div(J_X)) / Var(Δρ)`

Comparison baseline: R²_std from QNG-CPU-042
Seeds: [20260325, 42, 137, 1729, 2718]

## Motivation for these predictions

`mismatch` = exp. mov. avg. of |sigma_new − sigma_neigh|
`C_eff = 0.45·sigma + 0.35·(1−mismatch) + 0.20·(1+cos(phase))/2`

Therefore: `ΔC_eff ≈ −0.35·Δmismatch` (direct linear path, no angle approximation).

Unlike sin(Δφ) which is near-zero due to phi synchronization,
mismatch differences are O(0.1−0.3) — much larger signal.

## Locked predictions

### P1: R²_mis > R²_std on ≥4/5 seeds

Rationale: Mismatch has a direct linear contribution to C_eff (−0.35 weight).
Mismatch gradients should correlate with ΔC_eff substantially better than
phase differences which are near-zero universally.

### P2: mean R²_mis > 0.40

Rationale: The direct path from mismatch to C_eff suggests much stronger
continuity balance than mean R²≈0.20 from phase currents.

### P3: max R²_mis > 0.57

Rationale: Seed 137 was the best seed under phi (R²=0.572). If mismatch
is the correct current driver, it should at least match or exceed this.

### P4: R²_mis > R²_mem on ≥3/5 seeds

Rationale: mismatch has a direct path into C_eff (−0.35 coefficient);
mem (chi-mismatch) enters C_eff only indirectly via sigma dynamics.
mismatch should therefore be a better predictor of ΔC_eff than mem.

## Falsification conditions

- FAIL if R²_mis ≤ R²_std on all 5 seeds
- FAIL if P1, P2, P3, P4 all fail

A partial pass (≥2/4) is informative: tells us whether the problem is the
functional form specifically or the entire continuity framework.

## Reference values (from QNG-CPU-042)

R²_std by seed:
- seed 20260325: 0.045617
- seed 42: 0.138356
- seed 137: 0.572227
- seed 1729: 0.034704
- seed 2718: 0.207112
- mean: 0.1996
