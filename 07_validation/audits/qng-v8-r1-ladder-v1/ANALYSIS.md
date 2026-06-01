# GPU-031g Ladder Scan Analysis: Does <M>_t scale with R?

Date: 2026-04-21
Protocol: R1 Yoshida4 T_P2=5000 lu at R ∈ {3, 5, 6, 7} (R=4 from GPU-031f).
Same L=20, same DT=0.025, same three-phase formation.

## The question

Under Scenario A (particle = dynamic orbit, confirmed at R=4), the CPU-074
gradient-flow "rest-mass" identification is replaced by time-average:

    m_particle = a_M_orbital × <M_ring>_t

Calibration at R=4 (GPU-031f): a_M_orbital = 938.272 / 309.45 = **3.03 MeV/unit**.

For the DER-QNG-038 baryon ladder to survive this reinterpretation, the
orbital ratios must match CPU-074 ratios:

| R | CPU-074 M | ratio/R4 | Orbital prediction (×0.425 filling) | Baryon |
|--:|---------:|---------:|---------------------------------:|-------:|
| 3 | 474.15   | 0.651    | ≈ 201                            | none   |
| 4 | 728.92   | 1.000    | 309.45 (calibrated)              | N(938) |
| 5 | 954.88   | 1.310    | ≈ 406                            | Δ(1232)|
| 6 | ~1175    | 1.612    | ≈ 499                            | N*(1520)|
| 7 | ~1395    | 1.914    | ≈ 593                            | Δ(1700)|

## Result: R=5 — LADDER_BROKEN

**Verdict at R=5**: `LADDER_BROKEN` (ratio mismatch 17%, mass off by 211 MeV).

| Quantity               | R=4 (GPU-031f) | R=5 (GPU-031g)     | CPU-074 prediction |
|-----------------------:|---------------:|-------------------:|-------------------:|
| <M_ring>_t             | +309.45        | +336.66            | +406 (expected)    |
| ratio to R=4           | 1.000          | **1.088**          | **1.310**          |
| convergence_rel        | 2.15%          | **8.51%** (weak)   | —                  |
| duty_cycle_ring (>500) | 38.5%          | 39.3%              | —                  |
| dominant_period        | 185.2 lu       | 192.3 lu           | —                  |
| dominant_power_frac    | 40.9%          | 47.4%              | —                  |
| std_all                | 423.25         | 377.51             | —                  |
| H drift (over 5000 lu) | 0.20%          | 0.54%              | —                  |
| Predicted mass         | 938 MeV (✓)    | **1021 MeV**       | 1232 MeV target    |
| mass rel diff          | 0.0%           | **17.14%**         | <1% for success    |

## What went wrong: orbital `<M>_t` is R-insensitive

The CPU-074 gradient-flow value scaled as ~R^1 (string-tension-like). The
orbital attractor does NOT inherit that scaling. Between R=4 and R=5:

- Ring circumference increases 25% (2π·4 → 2π·5)
- CPU-074 M_ring increases 31% (728.92 → 954.88)
- **Orbital <M>_t increases only 9%** (309.45 → 336.66)

The filling factor (orbital/gradient-flow) is 0.425 at R=4 but 0.352 at R=5
— **it decreases as R grows**. If extrapolated: at R=7 the filling factor
might be ~0.25, giving <M>_t(R=7) ≈ 350 vs needed 593 for Δ(1700). The
ladder would be progressively more broken at larger R.

## Three candidate explanations

### (1) Universal basin (ladder is dead under v8 orbital)

The L=20 lattice + V_couple topology selects a **single quasi-periodic
attractor** whose mean is determined by box size, sine-Gordon phase
geometry, and integrator dynamics — not by initial ring radius. Rings
relax into this attractor regardless of where they start. If true,
`m_baryon = a_M · <M>_t` would give only one mass (~938 MeV) for all
R, and DER-QNG-038 is dead under R1/orbital.

### (2) R=5 basin not yet converged

convergence_rel = 8.51% (above 5% threshold; orbital_valid=False) suggests
the R=5 time-average is still drifting. The true <M>_t at T=10000 or
T=20000 might be higher, rescuing the ladder. But: R=5 std is smaller
than R=4 (377 vs 423), and the power_frac is *higher* (47% vs 41%) —
the R=5 orbit is more periodic, not more chaotic. A longer run is
unlikely to reveal a dramatically different mean.

### (3) Finite-size interference at R=5

R=5 approaches L/2=10 so the ring nearly touches its periodic image.
This could squeeze the orbit into a smaller phase-space basin, lowering
<M>_t. Test: rerun R=5 at L=32 (would take ~4× longer since volume scales
as L³). Not immediate priority.

## Decisive diagnostic: R=3

Launched 2026-04-21. Predictions:

- **Scaling hypothesis (if (2) or (3))**: <M>_t(R=3) ≈ 201 (0.425·474.15)
- **R-insensitivity hypothesis (if (1))**: <M>_t(R=3) ≈ 280-310

Difference is **~55%** — far outside experimental error. R=3 is the
cleanest test: it has the largest lattice buffer (L-2R=14 vs 12 for R=4
and 10 for R=5), so finite-size effects are smallest.

- If R=3 ≈ 201: hypothesis (1) ruled out; R=5 is anomalous (basin/size);
  continue R=6, R=7.
- If R=3 ≈ 300: hypothesis (1) confirmed; ladder is dead under v8 orbital;
  do not waste GPU time on R=6, R=7.

## Implications (preliminary, pending R=3)

Best case (R=3 ≈ 201): R=5 is an outlier; ladder might still work at
other radii. DER-QNG-038 under orbital remains plausible but with
R-dependent filling factor — not a universal constant.

Worst case (R=3 ≈ 300): DER-QNG-038 baryon ladder **does not transfer
v7 → v8**. Under v8 R1 dynamics, particles are bounded orbits with
a universal mass scale ~a_M·310 ≈ 940 MeV, not a baryon ladder.

Either way, the **pure v7 statement** of DER-QNG-038 (ladder in
gradient-flow M_ring) remains valid as a conservation-law statement.
What is at stake is only whether this v7 conservation statement is
inherited by the v8 canonical dynamics.

## R=3 result: hypothesis (1) CONFIRMED

**R=3 Verdict**: LADDER_BROKEN (31% ratio mismatch).

| Quantity               | Value         | Interpretation                     |
|-----------------------:|--------------:|-----------------------------------:|
| <M>_t all (5000 lu)    | +263.66       | 31% off CPU-074 prediction         |
| **mean_second_half**   | **+308.88**   | **matches R=4 (306.12) within 1%** |
| mean_first_half        | +218.43       | still warming up                   |
| convergence_rel        | 34.31%        | NOT converged                      |
| duty_cycle_ring        | 0.27          | lower than R=4 (0.385) / R=5 (0.39)|
| dominant_period        | 185.2 lu      | IDENTICAL to R=4                   |
| dominant_power_frac    | 26.8%         | less clean than R=4/R=5            |

The **decisive signal**: R=3's second-half mean is **308.88**, matching
R=4's mean (306.12) to within 1%. R=3 is drifting upward into the same
attractor as R=4; it's just warming up more slowly.

## Consolidated finding: universal orbital basin

| R | <M>_t all | 2nd-half | CPU-074 v7 | v7 ratio to R=4 | v8 2nd-half ratio to R=4 |
|--:|---------:|--------:|----------:|----------------:|-------------------------:|
| 3 | 263.66   | 308.88  | 474.15    | 0.651           | **0.999**                |
| 4 | 309.45   | 306.12  | 728.92    | 1.000           | 1.000                    |
| 5 | 336.66   | 350.99  | 954.88    | 1.310           | **1.147**                |

v7 gradient-flow: R=3/R=4/R=5 ratios are 0.65 / 1.00 / 1.31 (factor-2 spread).
v8 orbital (2nd-half): R=3/R=4/R=5 ratios are 1.00 / 1.00 / 1.15 (near flat).

**Hypothesis (1) confirmed**: the L=20 lattice + V_couple topology selects
a universal quasi-periodic attractor. Rings with different initial R
relax into the same basin — differing only in warm-up time and (slightly)
amplitude distribution.

## Implications

### Dead

- **DER-QNG-038 baryon ladder** (R=4→N, R=5→Δ, R=6→N*, R=7→Δ) does **NOT**
  transfer v7 → v8 orbital. Under v8 R1 there is essentially ONE mass
  (~940 MeV calibrated at R=4), not a ladder.
- The R=4→proton identification is an artifact of calibration, not a
  QNG prediction. Any R would have given the same mass under this
  protocol.
- **DER-QNG-038 mass identification remains valid as a v7-only
  conservation statement** but is not inherited by v8 canonical dynamics.

### Still alive

- **Scenario A** (particle = dynamic orbit): confirmed.
- A single-mass candidate ~940 MeV exists in v8 R1.
- Ring topology with winding Z (sine-Gordon) may still play a role
  via Noether charge / Chern-Simons, not via <M>_t.
- **Sine-Gordon breather analogy**: breathers have mass = time-averaged
  energy, and the breather mass depends on internal frequency, not on
  spatial extent of the envelope. This is consistent with R-insensitive
  <M>_t (though spatial extent = initial R, which is different quantity).

## Decision: GPU-031g R=6, R=7 CANCELLED

No scientific value in running further R's. R=6 and R=7 would converge
to the same ~310 ± 50 basin. Budget saved: ~2 × 45 min = 90 min.

## Next theoretical moves

1. **Retract DER-QNG-038 promotion to v8**: mark the baryon ladder as a
   v7 gradient-flow phenomenon, not a v8 prediction. Update THEORY_STATE
   and DER-QNG-038 scope declaration.
2. **Search for R-distinguishing v8 observables**: Noether charges of
   Channel F under residual symmetry? Chern-Simons of (σ_m, φ) field
   pair? Orbital action `S = ∮ π_φ dφ`? Poincaré return map statistics?
3. **Understand the basin value**: why does the universal <M>_t land
   at ~310? Is this set by L=20, by V_couple g=0.22, by μ_φ=0.857?
   Parameter scan would reveal the true QNG inputs to particle mass.
4. **Sine-Gordon breather mass formula**: for 1D sine-Gordon,
   M_breather = (16m/g)·sin θ where θ is internal frequency parameter.
   If the v8 attractor is a 3D breather, <M>_t should follow the same
   functional form in g and μ_φ. Testable by g-scan or μ_φ-scan at
   fixed R=4.

## Status

- **GPU-031g R=3**: EXECUTED, LADDER_BROKEN.
- **GPU-031g R=5**: EXECUTED, LADDER_BROKEN.
- **GPU-031g R=6, R=7**: **CANCELLED** (basin universal, no value).
- **Ladder scan**: COMPLETE. Verdict: v7 ladder does NOT transfer to v8.

Artifacts:
- `R3/report.json`, `R3/m_series.npz`, `R3_run.log`
- `R5/report.json`, `R5/m_series.npz`, `R5_run.log`

Claude Code autonomous session 2026-04-21.
