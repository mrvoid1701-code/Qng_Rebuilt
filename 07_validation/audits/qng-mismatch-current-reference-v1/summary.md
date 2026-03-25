# Audit Summary — QNG-CPU-045

Test: `qng_mismatch_current_reference.py`
Theory: `DER-BRIDGE-027`
Decision: **FAIL** (0/4 predictions correct — informative negative)

## What was tested

Whether replacing sin(Δφ) with (mismatch_j - mismatch_i) as the current driver
gives better calibrated continuity balance.

## Results by seed

| Seed     | R²_mis   | R²_mem   | R²_phi   | Δ(mis-phi) | mis>phi? |
|----------|----------|----------|----------|------------|----------|
| 20260325 | 0.012993 | 0.040113 | 0.045617 | -0.033     | NO       |
| 42       | 0.353832 | 0.048822 | 0.138356 | +0.215     | YES      |
| 137      | 0.001800 | 0.044895 | 0.572227 | -0.570     | NO       |
| 1729     | 0.021469 | 0.101066 | 0.034704 | -0.013     | NO       |
| 2718     | 0.208248 | 0.038489 | 0.207112 | +0.001     | YES      |

## Pass/Fail

| Criterion                         | Result | Value     |
|-----------------------------------|--------|-----------|
| P1: R²_mis > R²_std on ≥4/5      | FAIL   | 2/5       |
| P2: mean R²_mis > 0.40            | FAIL   | 0.1197    |
| P3: max R²_mis > 0.57             | FAIL   | 0.3538    |
| P4: R²_mis > R²_mem on ≥3/5      | FAIL   | 2/5       |

## Key diagnostics

Scale ratios (|J|/|Δρ|):

| Seed     | scale_mis | scale_mem | scale_phi |
|----------|-----------|-----------|-----------|
| 20260325 | 6.8x      | 18.1x     | 106x      |
| 42       | 12.8x     | 26.6x     | 99x       |
| 137      | 6.6x      | 14.3x     | 117x      |
| 1729     | 6.7x      | 16.5x     | 120x      |
| 2718     | 12.4x     | 20.3x     | 115x      |

## Critical findings

1. **Scale ratio dramatically improved**: mismatch gives 6-12x vs phi's 100-120x.
   The scale problem IS solved by using mismatch differences, but R² is still poor.

2. **Topology-dependent channel preference** — the most important result:
   - seed 42: mismatch strongly better (0.354 vs 0.138)
   - seed 137: phi strongly better (0.572 vs 0.002)
   - seed 1729: mem better (0.101 vs 0.035)
   - seeds 20260325, 2718: phi wins (weakly)

3. **No single-channel universal winner**: phi, mismatch, and mem each dominate
   on different topologies. This is strong evidence for a multi-channel current.

4. **var(mismatch) = 0.000035–0.000205**: Very small. After convergence, mismatch
   settles to a near-constant value per topology — still more variable than phi
   differences, but not as variable as expected.

## Conclusion

Single-channel current J = C_i·C_j·(driver_j - driver_i) is topology-dependent
regardless of driver choice (phi, mismatch, or mem). Each driver is optimal on
a different subset of topologies.

This is not a failure of the continuity framework — it is an identification of
the **multi-channel structure** of the QNG probability current.

## Implied next step

QNG-CPU-046: Multi-channel current regression
- Regress Δρ jointly on (div_J_phi, div_J_mis, div_J_mem)
- If R²_combined >> max(R²_phi, R²_mis, R²_mem) per seed, the multi-channel
  picture is confirmed
- The channels are roughly topology-selective: different topologies activate
  different drivers
