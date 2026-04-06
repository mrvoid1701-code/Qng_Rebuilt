# QNG-OBS-002

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `observational_fit`

## Title

Galaxy rotation curves — QNG global fixed a_M (zero free parameters)

## Purpose

QNG-OBS-001 showed that a per-galaxy free a_M improves chi²/dof 2.26x but
is uncorrelated with baryonic mass (Check 3 FAIL). That test had 171 free
parameters — one per galaxy. It proved fit improvement is possible but not
that QNG predicts it.

This test removes all freedom. a_M is fixed globally at A_vortex_ring = 0.225,
the sigma deficit amplitude measured in QNG-CPU-043. This value comes directly
from the vortex ring simulation — no fitting to rotation data.

```
V²_QNG(r) = V²_baryon(r) + 0.225
```

applied identically to all 175 galaxies. Zero free parameters.

From DER-QNG-027: Delta_V² = a_M × alpha × M_baryon with a_M = 0.52 × (m/rho_0).
The value 0.225 is A_vortex_ring — the dimensionless sigma deficit amplitude,
not yet the full a_M with physical units. This test uses it as a proxy for the
chi-field amplitude before rho_0 is fixed.

A PASS means a single number from a small 3D lattice simulation explains
rotation curve excess across 175 galaxies — a genuine zero-parameter prediction.

## Inputs

- [qng-am-fixing-v1.md](../../04_qng_pure/qng-am-fixing-v1.md) — DER-QNG-027
- [QNG-OBS-001.md](QNG-OBS-001.md) — per-galaxy baseline
- [data/rotation/rotation_ds006_rotmod.csv](../../data/rotation/rotation_ds006_rotmod.csv)
- [qng_obs_rotation_global_reference.py](../../tests/cpu/qng_obs_rotation_global_reference.py)

## Model

**Baryon-only:** V²_pred(r) = V²_baryon(r)

**QNG global:** V²_pred(r) = V²_baryon(r) + A_VORTEX
  where A_VORTEX = 0.225 (fixed, from QNG-CPU-043)

**Weighted chi²:** weight = 1 / (V²_err)², V²_err = 2 × v_obs × v_err

## Checks

**Check 1 — Global QNG improves median chi²/dof:**
```
median chi²/dof (QNG global) < median chi²/dof (baryon-only)
```

**Check 2 — Improvement ratio >= 1.5x:**
```
median_chi2_baryon / median_chi2_qng >= 1.5
```
Conservative gate. OBS-001 with free a_M gave 2.26x. If a fixed value from
the simulation gives >= 1.5x, the vortex amplitude has genuine predictive power.

**Check 3 — QNG improves majority of galaxies:**
```
fraction(chi²_QNG < chi²_baryon) > 0.50
```
At least half must be better fit. Gate is lower than OBS-001 (0.60) because
a fixed value cannot adapt to each galaxy.

**Check 4 — Median residual bias small:**
```
|median(v²_obs - v²_baryon - A_VORTEX) / median(v²_obs)| < 0.30
```
The global correction should not systematically over- or under-correct by
more than 30% of the observed signal.

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass (Check 4 informational).

**Interpretation of PASS:**
A_vortex_ring = 0.225 from the vortex simulation predicts rotation curve excess
without any fitting to galaxy data. This is the core QNG claim: the chi-field
amplitude is set by the substrate, not by the galaxies.

**Interpretation of FAIL:**
- Check 2 fails (ratio < 1.5x): fixed value either over- or under-corrects
  systematically. The substrate amplitude needs physical unit conversion (rho_0
  fixing) before it can be compared to (km/s)² units.
- Check 3 fails: the fixed value makes more than half of galaxies worse —
  the constant is too large or too small globally.

## Artifact paths

- `07_validation/audits/qng-obs-rotation-global-reference-v1/report.json`
- `07_validation/audits/qng-obs-rotation-global-reference-v1/summary.md`
