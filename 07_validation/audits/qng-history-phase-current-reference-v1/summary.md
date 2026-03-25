# Audit Summary — QNG-CPU-044

Test: `qng_history_phase_current_reference.py`
Theory: `DER-BRIDGE-026`
Decision: **FAIL** (1/4 predictions correct)

## What was tested

Whether replacing `phi` with `history.phase` (accumulated local phase gradient
memory) as the phase field in the U(1) current construction improves the
calibrated continuity balance R²_calib.

## Results by seed

| Seed     | R²_hp    | R²_std   | Δ         | α*_hp     | beats? |
|----------|----------|----------|-----------|-----------|--------|
| 20260325 | 0.004343 | 0.045617 | -0.041274 | +0.000205 | NO     |
| 42       | 0.003364 | 0.138356 | -0.134992 | +0.000089 | NO     |
| 137      | 0.332877 | 0.572227 | -0.239351 | +0.001981 | NO     |
| 1729     | 0.106360 | 0.034704 | +0.071656 | +0.000269 | YES    |
| 2718     | 0.140734 | 0.207112 | -0.066377 | -0.001906 | NO     |

## Pass/Fail

| Criterion                          | Result | Value       |
|------------------------------------|--------|-------------|
| P1: R²_hp > R²_std on ≥3/5 seeds  | FAIL   | 1/5 seeds   |
| P2: α*_hp > 0 on ≥3/5 seeds       | PASS   | 4/5 seeds   |
| P3: mean R²_hp > 0.20              | FAIL   | 0.1175      |
| P4: max R²_hp > 0.50               | FAIL   | 0.3329      |

## Key diagnostics

Phase field comparison:

| Seed     | var(phi) | var(h.phase) | corr(phi,h.phase) | scale_hp | scale_std |
|----------|----------|--------------|-------------------|----------|-----------|
| 20260325 | 0.1144   | 0.0473       | 0.865             | 111x     | 106x      |
| 42       | 0.0483   | 0.0161       | 0.870             | 120x     | 99x       |
| 137      | 0.1716   | 0.0481       | 0.975             | 90x      | 117x      |
| 1729     | 0.1904   | 0.0237       | 0.841             | 111x     | 120x      |
| 2718     | 0.0509   | 0.0194       | 0.962             | 97x      | 115x      |

## Critical findings

1. **phi and history.phase are highly correlated** (corr 0.84–0.97 across all seeds).
   history.phase is NOT an independent phase variable — it is a compressed,
   smoothed version of the phi gradient that tracks phi closely.

2. **var(h.phase) < var(phi) universally**: history.phase has 3–8x smaller
   variance than phi. Smaller phase differences → smaller sin(...) values
   → weaker current signal → worse R².

3. **scale ratio unchanged**: Both phase fields give |J|/|Δρ| ≈ 90–120x.
   The scale mismatch bottleneck is unchanged by phase field choice.

4. **Only seed 1729 improved**: The one case where history.phase beats phi
   is topology-dependent (Tier-2) and the improvement is marginal (0.034→0.106).

## Conclusion

The hypothesis that history.phase provides better phase gradient structure
is **falsified**. The reason:

- history.phase is a smoothed version of phi with smaller variance
- Smaller variance = smaller differences = weaker current
- The bottleneck for R²_calib is NOT which phase variable is used
- The bottleneck is the STRUCTURAL mismatch between phase-difference currents
  and density evolution

## What this implies for the theory

The continuity equation bottleneck now has three ruled-out diagnoses:
1. Amplitude form (C_eff vs sqrt(C_eff)) — RULED OUT by QNG-CPU-043
2. Phase variable choice (phi vs history.phase) — RULED OUT by QNG-CPU-044
3. Scale mismatch only — RULED OUT (α*≈10⁻³ calibration already absorbed it)

The remaining possibility:
- The current J = Σ C_i·C_j·sin(Δφ) is the WRONG FUNCTIONAL FORM for QNG density flow
- A different current structure (e.g., involving memory, mismatch, or sigma directly)
  may be needed — or the continuity framework itself needs to be replaced

The QM recovery bottleneck is now identified more precisely: it is the
**current functional form**, not amplitude, scale, or phase variable.
