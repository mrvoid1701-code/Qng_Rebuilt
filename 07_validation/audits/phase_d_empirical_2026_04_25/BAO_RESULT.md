# A1 — eBOSS DR16 BAO test result (CPU-131)

Date: 2026-04-25
Status: **MAJOR FLAG on Paper 4**

## Test setup

eBOSS DR16 BAO measurements at 5 data points:
- LRG z=0.698: D_M/r_d=17.86±0.33, D_H/r_d=19.33±0.53
- ELG z=0.845: D_V/r_d=18.33±0.57
- QSO z=1.480: D_M/r_d=30.21±0.79, D_H/r_d=13.26±0.55

QSO clustering data verified loaded from `eBOSS_QSO_clustering_data-SGC-vDR16.fits`
(125,499 quasars, z range [0.8, 2.2], median 1.52 — consistent with z_eff=1.48
published value).

## Three models tested

1. **ΛCDM** (Ω_m=0.315, Ω_Λ=0.685, h=0.674): standard cosmological constant
2. **Pure matter** (Ω_m=1, Λ=0): no dark energy at all
3. **QNG-Yukawa toy** (Ω_m_eff(z) = 0.31 + 0.69·z/(1+z)): toy interpolation
   suggesting how Yukawa screening might modify effective matter density

## Results

| Model | χ²/dof | Verdict |
|---|---|---|
| ΛCDM | 0.98 | EXCELLENT FIT |
| Pure matter | 103.20 | CATASTROPHIC FAILURE |
| QNG-Yukawa toy | 32.61 | FAILS by ~30σ-equivalent |

## Detailed comparison

| z_eff | obs | measured | ΛCDM | pure-mat | QNG-toy |
|---|---|---|---|---|---|
| 0.698 | D_M/r_d | 17.86±0.33 | 17.54 ✓ | 14.08 ✗ | 21.06 ✗ |
| 0.698 | D_H/r_d | 19.33±0.53 | 20.28 ✓ | 13.68 ✗ | 17.75 ✗ |
| 0.845 | D_V/r_d | 18.33±0.57 | 18.68 ✓ | 13.75 ✗ | 19.23 ✓-ish |
| 1.480 | D_M/r_d | 30.21±0.79 | 30.23 ✓ | 22.09 ✗ | 30.94 ✓-ish |
| 1.480 | D_H/r_d | 13.26±0.55 | 12.91 ✓ | 7.75 ✗ | 9.12 ✗ |

The QNG toy parameterization PARTIALLY works at high z (where Ω_m_eff → 1) but
fails at low z (where Yukawa screening is supposed to mimic Λ). The toy function
S(z) cannot simultaneously fit D_M and D_H at the same z because they probe
H(z) and integrated H(z') with different z-weightings.

## Implications for Paper 4

### Status of Paper 4 §5.2 prediction (BAO modification)

Paper 4 §5.2 predicts:
> Concrete prediction: large-scale structure growth at modes k < 0.01 h/Mpc
> (large clusters and beyond) is suppressed relative to ΛCDM by a few percent.

This was framed as a falsifiable prediction. **The BAO data at z=0.7-1.5
constrain QNG H(z) to be CLOSE TO ΛCDM**, not significantly modified.

**With our toy parameterization**, QNG predicts ~5-30% deviations in BAO
distance measurements — vastly inconsistent with observed 1-3% precision.

### Status of "Yukawa replaces Λ" claim

Paper 4's central claim (§3.2): Yukawa screening with λ_screen ~ R_Hubble
replaces the role of Λ in producing late-time acceleration.

**The toy implementation FAILS to produce H(z) consistent with eBOSS BAO.**

This does NOT prove the substrate claim is wrong — only that:
1. The simple parameterization S(z) = Ω_m + (1-Ω_m)·z/(1+z) is too crude
2. A proper derivation of QNG-modified Friedmann (which we have NOT performed)
   might give different H(z)
3. **OR**: the Yukawa mechanism really cannot replace Λ at the precision
   required by modern BAO data

Without the proper derivation, **Paper 4's central claim is currently
unsubstantiated empirically**.

### Recommended Paper 4 status downgrade

Current Paper 4 frames the cosmological match as:
> The substrate-required value of α matches the observed cosmological scale to
> within a factor of seven across 125 orders of magnitude — a striking
> consistency.

This is misleading when BAO precision testing is properly done. The proper
honest framing is:

> The substrate-derived Yukawa kernel, when applied to cosmology, MUST match
> H(z) to better than 1% at z=0.7, 0.85, 1.48 to be consistent with eBOSS DR16
> BAO measurements (χ²/dof = 0.98 for ΛCDM). Whether the QNG Yukawa kernel can
> achieve this requires a proper derivation of the modified Friedmann equation
> with substrate-derived screening, currently OPEN.

## Three honest options for Paper 4

### Option A: Major revision

Reframe Paper 4 as:
- Title: "Yukawa-Screened Newtonian Gravity from QNG: Substrate Derivation"
- Drop the "replaces Λ" claim
- Keep: Yukawa kernel derivation (rigorous)
- Keep: Sub-cosmological scale tests (Solar System OK)
- Add: BAO test result showing simple toy parameterization fails
- Add: open question whether full QNG Friedmann can match BAO

### Option B: Withhold submission until QNG Friedmann derived

Don't submit Paper 4 until:
- Modified Friedmann equation explicitly derived from substrate
- Solved for H(z), D_M(z), D_H(z), D_V(z)
- Verified χ²/dof < 5 vs eBOSS BAO

This is the rigorous path but takes months.

### Option C: Withdraw Paper 4 entirely

If proper Friedmann derivation reveals QNG Yukawa CANNOT mimic Λ at BAO
precision, Paper 4's central claim is structurally wrong.

In this case:
- Paper 1 (ℏ) still stands
- Paper 2 (Stability Principle / Λ=0) stands as a structural claim, but
  the question "what is Λ_obs" becomes OPEN (need other mechanism, not Yukawa)
- Paper 3 (framework) stands with Paper 4 explicitly retracted

## Status of papers after Phase D

| Paper | Status after CPU-127/128/129/130/131 |
|---|---|
| Paper 1 (ℏ) | UNAFFECTED — ready to submit |
| Paper 2 (Λ=0 / Stability Principle) | PARTIALLY AFFECTED — Λ_obs explanation needs other mechanism |
| Paper 3 (comprehensive framework) | CONFIRMED — all honest-scope disclaimers validated empirically |
| Paper 4 (Yukawa cosmological) | **MAJOR REVISION REQUIRED** — BAO test failed for toy implementation |

## Recommendation

**Adopt Option A**: revise Paper 4 to be:
- Honest about derived/proven content (Yukawa kernel form, sub-cosmological tests)
- Explicit about cosmological identification being CONJECTURE
- Includes BAO test failure as a known constraint
- Reframes "factor 7 match" as "rough order-of-magnitude" not "tight prediction"

This preserves the structural physics content of Paper 4 while removing the
unsupported empirical claim.

**Keep Paper 4 in alpha series with major caveat**, then either:
- Develop full Friedmann derivation in follow-up work
- Or accept that Paper 4's main claim is open / retracted

## Files

- Test: `tests/cpu/qng_cpu131_eboss_bao_test.py`
- This report: `07_validation/audits/phase_d_empirical_2026_04_25/BAO_RESULT.md`
- Phase D report: `07_validation/audits/phase_d_empirical_2026_04_25/REPORT.md`
