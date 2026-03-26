# Prereg QNG-CPU-043: Madelung Amplitude Proxy

Status: `locked`
Locked before: first run of `qng_madelung_amplitude_reference.py`
Theory doc: `DER-BRIDGE-025` (`qng-qm-madelung-amplitude-v1.md`)

## Test objective

Compare ψ_M = sqrt(C_eff)·exp(i·phi) [Madelung, ρ=C_eff] against
ψ_std = C_eff·exp(i·phi) [standard, ρ=C_eff²] on calibrated continuity R².

## Setup

- n_nodes = 16, steps = 24 (default Config)
- Seeds: [20260325, 42, 137, 1729, 2718]
- Reference: QNG-CPU-042 results (α*_std, R²_std per seed)

## Locked predictions

### P1: α*_M > 0 on ≥4/5 seeds
Same directional correctness as QNG-CPU-042 — EXPECTED TRUE

### P2: max(R²_M) > 0.5 on ≥1 seed
Seed 137 expected to give R²_M ≥ 0.5 — EXPECTED TRUE

### P3: mean R²_M > mean R²_std = 0.200
Madelung improves average balance — OPEN

### P4: cv(|α*_M|) ≤ 0.76
Not worse stability than standard — OPEN

## Reference values from QNG-CPU-042

α*_std per seed: [0.000695, 0.000689, 0.001988, 0.000143, -0.001963]
R²_std per seed: [0.0456, 0.1384, 0.5722, 0.0347, 0.2071]
mean R²_std: 0.200

## Decision rule

PASS if P1 + P2 pass AND (P3 OR P4) passes.
CONDITIONAL if P2 fails but P1 + P3 pass.
FAIL if P1 fails on >2 seeds.
