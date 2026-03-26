# Prereg QNG-CPU-047

Type: `prereg`
ID: `QNG-CPU-047`
Status: `locked`
Author: `C.D Gabriel`
Theory: `DER-BRIDGE-029`

## Locked before run

This file is written and committed BEFORE running the test.
Predictions cannot be changed after execution.

## What is being tested

Whether the multi-channel continuity law established at N=16 (QNG-CPU-046)
is N-stable: tested at N ∈ {8, 16, 32} across 5 seeds.

Multi-channel law:
```
∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0
```

Seeds: [20260325, 42, 137, 1729, 2718] — same as CPU-046
N values: [8, 16, 32]

## Key structural prediction

`build_graph` creates ring + Erdos-Renyi (p=0.18). Expected mean degree:
- N=8:  ~3.0
- N=16: ~4.2 (reference, CPU-046 result)
- N=32: ~7.1

More neighbors → stronger phi synchronization → smaller sin(Δφ) → weaker phi channel.
Mismatch/mem have larger neighborhood sums → stronger signal.

## Locked predictions

### P1: R²_combined > R²_best_single at N=32, ≥4/5 seeds

Rationale: The multi-channel structure is a genuine property of QNG substrate
dynamics, not a finite-size artifact at N=16. At larger N, the topology becomes
denser but the three channels should remain complementary. The single biggest risk
is that at N=32 all channels become highly correlated (redundant) due to stronger
synchronization.

### P2: mean R²_combined ≥ 0.30 at N=8 AND N=32

Rationale: R²=0.405 at N=16. If the law is N-stable, both smaller (N=8) and
larger (N=32) systems should maintain R² above 0.30 (80% of the N=16 mean).

### P3: |α_phi / α_mis| decreases from N=8 to N=32 on ≥3/5 seeds

Rationale: Denser graphs → more phi synchronization → phi channel weakens
relative to mismatch. The ratio |α_phi/α_mis| should be smaller at N=32
than at N=8 on most seeds.

### P4: best_N (R²_combined maximized) ≠ N=8 on ≥4/5 seeds

Rationale: N=8 is too small for stable statistics (only 8 nodes). The law
should perform better at N=16 or N=32 than at N=8 on most seeds.

## Falsification conditions

- FAIL if R²_combined ≤ R²_best_single at N=32 on ALL 5 seeds (law collapses at large N)
- FAIL if mean R²_combined < 0.20 at any N (law is N-specific, not N-stable)

## Reference values (from QNG-CPU-046, N=16)

| Seed     | R²_combined | R²_best_single | gain     |
|----------|-------------|----------------|----------|
| 20260325 | 0.147724    | 0.045617       | +0.102   |
| 42       | 0.535153    | 0.353832       | +0.181   |
| 137      | 0.601887    | 0.572227       | +0.030   |
| 1729     | 0.239188    | 0.101066       | +0.138   |
| 2718     | 0.502728    | 0.208248       | +0.294   |
| mean     | 0.405336    | 0.256198       | +0.149   |
