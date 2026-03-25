# Prereg QNG-CPU-044

Type: `prereg`
ID: `QNG-CPU-044`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-026`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether replacing `phi` with `history.phase` as the phase field in the
U(1) current construction improves the calibrated continuity balance R²_calib.

Construction:
- `J_hp_{i→j} = C_eff_i · C_eff_j · sin(history.phase_j - history.phase_i)`
- `div(J_hp)_i = C_eff_i · Σ_j C_eff_j · sin(history.phase_j - history.phase_i)`
- `α*_hp = -Σ(Δρ · div(J_hp)) / Σ(div(J_hp)²)`
- `R²_hp = 1 - Var(Δρ + α* · div(J_hp)) / Var(Δρ)` where `ρ = C_eff²`

Comparison baseline: R²_std from QNG-CPU-042
Seeds: [20260325, 42, 137, 1729, 2718]

## Locked predictions

### P1: R²_hp > R²_std on ≥3/5 seeds

Rationale: `history.phase` tracks local phase mismatch (gradient memory),
not the absolute phase. Near-synced phi gives small differences and weak
current signals. history.phase has larger cross-node variance and directly
encodes the gradient structure needed for the continuity current.

### P2: α*_hp > 0 on ≥3/5 seeds

Rationale: If history.phase gradients correlate with density outflow,
sign should be positive. Expected to hold on at least the same seeds
that had α*>0 under the standard construction.

### P3: mean R²_hp > 0.20

Rationale: If phase gradient hypothesis is correct, mean should exceed
the 0.20 benchmark from QNG-CPU-042 and QNG-CPU-043.

### P4: max R²_hp > 0.50 on ≥1 seed

Rationale: Seed 137 showed R²=0.572 with standard phi. If history.phase
is better, it should at least match or improve on that seed.

## Falsification conditions

- FAIL if R²_hp ≤ R²_std on all 5 seeds (no improvement anywhere)
- FAIL if P1, P2, P3, P4 all fail simultaneously

A partial pass (≥2/4 predictions correct) still constitutes meaningful
information about the phase gradient bottleneck.

## Reference values (from QNG-CPU-042)

R²_std by seed:
- seed 20260325: 0.045617
- seed 42: 0.138356
- seed 137: 0.572227
- seed 1729: 0.034704
- seed 2718: 0.207112
- mean: 0.1996
- cv(|α*_std|): 0.7612
