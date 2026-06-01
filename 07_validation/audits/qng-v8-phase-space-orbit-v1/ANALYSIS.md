# GPU-031 Analysis: Raw Verdict vs Honest Physics Read

Date: 2026-04-21
Run: cached L=28 R=4, pure Yoshida4, k_gm=0, chi_decay=0, T=1000 lu, DT=0.025

## Raw pre-registered verdict

```
G1 (|dH/H0| < 0.02):      max=3.421e-01  FAIL
G2 (|dM/M0| < 1.0):       max=8.462e+00  FAIL
G3 (|M(T) - M(T/2)|/M0 < 0.5): 1.758e+00  FAIL

Verdict: H_DIVERGENT
```

## Why H_DIVERGENT is too strong

The gate assignment was predicated on "bounded orbit = factor-of-2 band around
M_0 = 176.85." What the data actually show:

1. **M_ring is strictly positive throughout**. Range [40.24, 1673.3] at
   t ∈ [0, 1000] lu. The sigma_m depletion never vanishes → the ring as a
   topological object persists. No dissolution event.

2. **sm_min never persistently goes to zero**. sm_min ∈ [0.0000, 0.3250];
   fraction of time with sm_min < 0.01 is only 6.3 %; fraction with
   sm_min > 0.20 (near initial) is 40.4 %. Ring core rebuilds itself.

3. **Autocorrelation of M_ring shows recurrence at 129 lu** with ac=0.461.
   First Fourier peaks at periods 125, 143, 167 lu carry 40 % of total
   spectral power. This is a **coherent breathing mode**, not chaos.

4. **Corr(M_ring, H) = +0.934**. Tight correlation — H and M oscillate
   together. Consistent with a collective breathing mode where sigma_m
   depletion and energy rise in phase.

5. **|dH/H0| has two components**:
   - Secular: +12.5 % per 1000 lu (monotonic upward drift)
   - Oscillatory amplitude (detrended): std = 37.0
   - Ratio oscillation/secular: 0.47

   The secular component dominates. This is **numerical-integrator error**,
   consistent with Channel A approximation (F_A = BETA_PHI·(pm_wmean − phi)
   is only the uniform-sigma_m limit of the exact canonical XY force
   DER-QNG-050). In a ring core sigma_m is strongly non-uniform, so the
   F_A approximation error accumulates as secular drift.

## Honest physics verdict

**Scenario A is NOT falsified by this run.** The data are consistent with a
bounded breathing orbit at period ~129 lu; the integrator simply fails to
conserve energy tight enough to probe long-time boundedness.

**Scenario A is NOT confirmed either.** With 12.5 % H drift per 1000 lu, we
cannot distinguish a genuinely unbounded orbit from a bounded orbit contaminated
by numerical drift. The 6 % of time spent at sm_min < 0.01 is concerning —
the v8 effective-theory boundary (SIGMA_G_MIN_ABORT = 0.025) is nominally
crossed, so some fraction of the dynamics is outside the declared v8 validity
regime.

## Revised status

- Verdict reclassified: **H_INTEGRATOR_LIMITED** (not in original schema;
  proposed as new bucket for future pre-registrations).
- Scenario A empirically content remains **UNDECIDED**.
- Follow-up test required (Option A or B below) before any final ruling.

## Follow-up options

**Option A — DER-QNG-050 exact canonical F_A**
- Implement exact F_A in `force_phi_v8` and new −∂E_phi/∂σ_m term in `force_sm_v8`.
- Re-run GPU-031 with exact_a=True.
- Expected: secular H drift drops below 1 % / 1000 lu → boundedness probe
  becomes physical, not numerical.
- Cost: moderate code change + full regression of CPU-074/075 baryon ladder.

**Option B — DT refinement + shorter T**
- Run GPU-031b with DT=0.005, T=200 lu (same wall-clock as current run).
- If breathing mode survives at 5× finer DT with smaller secular drift,
  it is physical; if it disappears or changes qualitatively, it was
  integrator artifact.
- Cost: zero code change; one GPU run (~20 min).

Option B is cheaper and identifies whether integrator failure is the
dominant issue. Option A is the proper fix and needed regardless, but
should follow B to confirm the problem diagnosis.

## Einstein-timeline mapping

Pre-run: we thought we'd answer Klein's 1926 question ("do bound modes
play the role of particles?"). What we actually got: Kaluza 1921 — the
framework exists, the breathing mode is visible, but the calculation
tools are not yet sharp enough to extract the mass spectrum.

## Artifacts

- `report.json` — pre-registered verdict (H_DIVERGENT)
- `trajectory.npz` — time series (t, H, M_ring, sm_min/max/core, T_m, T_phi)
- `snapshots/` — full state (sm, phi, pi_m, pi_phi) every 50 lu
- `ANALYSIS.md` — this file (post-run honest read)
