# Audit Summary — QNG-CPU-046

Test: `qng_multichannel_current_reference.py`
Theory: `DER-BRIDGE-028`
Decision: **PASS** (4/4 predictions)

## What was tested

Whether jointly regressing Δρ on all three current channels (phi, mismatch, mem)
gives R²_combined >> max(R²_single) per seed.

## Results by seed

| Seed     | R²_combined | R²_phi   | R²_mis   | R²_mem   | gain     | beats? |
|----------|-------------|----------|----------|----------|----------|--------|
| 20260325 | 0.147724    | 0.045617 | 0.012993 | 0.040113 | +0.102   | YES    |
| 42       | 0.535153    | 0.138356 | 0.353832 | 0.048822 | +0.181   | YES    |
| 137      | 0.601887    | 0.572227 | 0.001800 | 0.044895 | +0.030   | YES    |
| 1729     | 0.239188    | 0.034704 | 0.021469 | 0.101066 | +0.138   | YES    |
| 2718     | 0.502728    | 0.207112 | 0.208248 | 0.038489 | +0.294   | YES    |

## Pass/Fail

| Criterion                              | Result | Value          |
|----------------------------------------|--------|----------------|
| P1: R²_comb > best_single on ≥4/5     | PASS   | 5/5 seeds      |
| P2: mean R²_combined > 0.35            | PASS   | 0.4053         |
| P3: max R²_combined > 0.60             | PASS   | 0.6019         |
| P4: R²_combined > 0.30 on ≥3/5 seeds  | PASS   | 3/5 seeds      |

## Multi-channel coefficients

| Seed     | α_phi      | α_mis     | α_mem      | corr(φ,mis) | corr(mis,mem) |
|----------|------------|-----------|------------|-------------|---------------|
| 20260325 | +0.000479  | +0.018299 | -0.007194  | -0.107      | +0.607        |
| 42       | +0.000627  | +0.009003 | -0.001126  | -0.044      | +0.110        |
| 137      | +0.001854  | +0.009645 | -0.006041  | +0.076      | +0.771        |
| 1729     | +0.000125  | -0.010839 | +0.005667  | +0.072      | +0.906        |
| 2718     | -0.001536  | +0.023587 | -0.008800  | -0.037      | +0.409        |

## Critical findings

1. **Multi-channel confirmed universally**: R²_combined > best_single on all 5 seeds.
   Mean gain = +0.149 (from 0.256 to 0.405). The three channels carry partially
   independent information across all tested topologies.

2. **phi channel contribution is weak but non-zero**: α_phi ≈ 10⁻³ (same order as
   single-channel calibration). Changes sign on seed 2718 (topology-dependent, Tier-2).

3. **mismatch and mem are the dominant channels**: |α_mis| and |α_mem| are ~10–20x
   larger than α_phi. They often appear with opposite signs (mis positive, mem
   negative), suggesting they partially cancel — consistent with corr(mis,mem) = 0.11–0.91.

4. **Seed 137 marginal gain** (+0.030): phi already dominated (0.572). Adding mismatch
   and mem channels gives only small improvement — the phi channel is nearly sufficient
   on this topology.

5. **Largest gains on seeds with weak single channels**: seeds 20260325 (+0.102),
   1729 (+0.138), 2718 (+0.294) — the multi-channel structure rescues topologies
   where no single channel was strong.

## Physical interpretation

The QNG probability current is MULTI-CHANNEL:

```
∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0
```

where:
- `J_phi` carries U(1) phase-oscillator flux (weak, near-zero due to sync)
- `J_mis` carries sigma-mismatch-gradient flux (strong, positive coupling)
- `J_mem` carries chi-memory-gradient flux (opposite sign to J_mis, corrective)

The effective QNG density flow is dominated by the sigma-mismatch and chi-memory
gradient channels, with a weak phase correction. This is fundamentally a
**mismatch-driven diffusion** rather than a Schrödinger-like U(1) phase current.

The three channels are topology-selective (Tier-2 primacy among channels) but
jointly they provide Tier-1 improvement (R²_combined > best_single universally).

## Remaining open questions

- R²_combined = 0.405 (mean): still moderate — full continuity not yet closed
- α_phi sign-instability (Tier-2): phi coupling topology-dependent
- Dynamical law for the coupling constants α(topology)
- Whether a non-linear current (e.g., involving C_eff gradient) further improves
- Connection to the semigroup/propagator picture already established (CPU-028/030)
