# QNG QM Multi-Channel Current v1

Type: `derivation`
ID: `DER-BRIDGE-028`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-027` (mismatch current — multi-channel structure identified)

## Objective

Test whether combining all three current channels (phi, mismatch, mem) in a
joint linear regression gives significantly better calibrated continuity balance
than any single channel.

## Background

QNG-CPU-045 identified topology-selective channel preference:

- seed 42: mismatch dominates (R²_mis=0.354 vs R²_phi=0.138)
- seed 137: phi dominates (R²_phi=0.572 vs R²_mis=0.002)
- seed 1729: mem dominates (R²_mem=0.101 vs R²_phi=0.035)
- No universal single-channel winner

This pattern strongly implies that the QNG probability current is a linear
superposition of three channels, each dominant on a different topology class.

Physical motivation for multi-channel structure:

1. **phi channel** (U(1) oscillator): Near-synced phase gives tiny sin(Δφ) but
   the few nodes with large phase gradients carry significant flux. Strong where
   topology creates persistent phase frustration.

2. **mismatch channel** (sigma gradient memory): Tracks local sigma disagreement.
   Strong where topology creates persistent sigma heterogeneity.

3. **mem channel** (chi gradient memory): Tracks local chi disagreement. Strong
   where chi dynamics create persistent load gradients.

These three channels are driven by different native field dynamics and are
expected to be partially independent — so their combination should improve R².

## Construction

### Three div-currents

```
div(J_phi)_i  = C_eff_i · Σ_j C_eff_j · sin(phi_j - phi_i)
div(J_mis)_i  = C_eff_i · Σ_j C_eff_j · (mismatch_j - mismatch_i)
div(J_mem)_i  = C_eff_i · Σ_j C_eff_j · (mem_j - mem_i)
```

### Multi-channel continuity ansatz

```
∂_t ρ + α_phi · div(J_phi) + α_mis · div(J_mis) + α_mem · div(J_mem) = 0
```

where ρ = C_eff².

### OLS normal equations (3×3 system)

Define residual:
```
r_i = Δρ_i + α_phi · dJ_phi_i + α_mis · dJ_mis_i + α_mem · dJ_mem_i
```

Minimize Σ r_i². The 3×3 normal equations:

```
[Σ dJ_phi²      Σ dJ_phi·dJ_mis  Σ dJ_phi·dJ_mem] [α_phi]   [-Σ Δρ·dJ_phi]
[Σ dJ_phi·dJ_mis  Σ dJ_mis²      Σ dJ_mis·dJ_mem] [α_mis] = [-Σ Δρ·dJ_mis]
[Σ dJ_phi·dJ_mem  Σ dJ_mis·dJ_mem  Σ dJ_mem²    ] [α_mem]   [-Σ Δρ·dJ_mem]
```

Solved by Gaussian elimination (pure Python, no external libraries).

### Combined R²

```
R²_combined = 1 - Var(Δρ + α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem) / Var(Δρ)
```

## Claims

### Claim A: R²_combined > max(R²_phi, R²_mis, R²_mem) on ≥4/5 seeds

Prediction: OPEN

Argument: If channels are partially independent, joint regression improves R²
beyond the best single channel. The topology-selective preference observed in
CPU-045 suggests that phi and mismatch/mem carry complementary information.

### Claim B: mean R²_combined > 0.35

Prediction: OPEN

Argument: Single-channel means: phi=0.200, mis=0.120, mem=0.055. If combining
captures the topology-selective bests (seed 42: mis 0.354, seed 137: phi 0.572,
seed 1729: mem 0.101), the weighted mean should exceed 0.35.

### Claim C: max R²_combined > 0.60

Prediction: OPEN

Argument: Seed 137 already has R²_phi=0.572 from phi alone. Adding mismatch
and mem channels (even if small on that seed) may push it above 0.60.

### Claim D: R²_combined > 0.30 on ≥3/5 seeds

Prediction: OPEN

Argument: At minimum, seeds where a single channel gives R²>0.10 should
improve further with joint regression. Seeds 42 (0.354), 137 (0.572), 1729
(0.101), 2718 (0.207) all had at least one strong channel — 4 seeds could
reach R²>0.30 with combination.

## Physical interpretation

If R²_combined >> max(R²_single) universally:
- The QNG probability current is genuinely multi-channel
- The three native channels (phase, sigma-mismatch, chi-memory) each carry
  independent flux information
- The correct continuity equation is:
  `∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) = 0`
- This is a three-component diffusion law, not a pure U(1) phase current
- The relative coefficients (α_phi, α_mis, α_mem) characterize the topology

If R²_combined ≈ max(R²_single):
- The channels carry the same information (high cross-correlation)
- The continuity framework needs a fundamentally different structure
  (non-linear, multi-step, or tensor-valued)

## Validation

Test: `QNG-CPU-046` — `qng_multichannel_current_reference.py`
Decision: PASS (4/4 predictions)

Results:
- P1: R²_comb > best_single on ≥4/5 — PASS (5/5)
- P2: mean R²_combined > 0.35 — PASS (0.4053)
- P3: max R²_combined > 0.60 — PASS (0.6019, seed 137)
- P4: R²_combined > 0.30 on ≥3/5 — PASS (3/5: seeds 42, 137, 2718)

Key findings:
- R²_combined > best_single on ALL 5 seeds (gain: +0.030 to +0.294)
- Mean R² improved from 0.256 (best single) to 0.405 (multi-channel)
- Dominant channels: mismatch + mem (|α| ~10-20x larger than α_phi)
- phi contribution: weak, sign-unstable (Tier-2); mis+mem are the real drivers
- Multi-channel structure is Tier-1 universal: combination beats single on all seeds
- Effective QNG continuity: ∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0
- Physical interpretation: mismatch-driven diffusion with chi-memory correction,
  plus weak phase-oscillator flux
