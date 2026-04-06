# QNG-OBS-003

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `observational_fit`

## Title

Galaxy rotation curves — MOND comparison on DS006 sample

## Purpose

QNG-OBS-001 showed the per-galaxy flat-ether model improves chi²/dof 2.26x
but a_M is uncorrelated with baryonic mass. QNG-OBS-002 showed the dimensionless
substrate value (0.225) has no predictive power in physical units — the unit
conversion factor (rho_0) is unknown.

MOND (Modified Newtonian Dynamics, Milgrom 1983) makes a zero-free-parameter
prediction for the same 175 galaxies using only a_0 = 1.2e-10 m/s² from
literature. This test establishes what a mature empirical model achieves on
the same dataset, providing a reference baseline for QNG.

## Model

**MOND interpolating function (simple form, Bekenstein-Milgrom):**
```
mu(x) = x / sqrt(1 + x²)    where x = a / a_0
```

**MOND equation:** mu(a/a_0) × a = a_N

where a_N = V²_baryon(r) / r is the Newtonian acceleration from baryons only.

**Solving for a_MOND analytically (simple interpolating function):**
```
t² = (x² + sqrt(x⁴ + 4x²)) / 2    where x = a_N / a_0
a_MOND = sqrt(t²) × a_0
V²_MOND(r) = a_MOND × r
```

**Unit conversions:**
- r in kpc, V² in (km/s)²
- a_N [m/s²] = V²_baryon [(km/s)²] × 1e6 / (r [kpc] × 3.0857e19)
- V²_MOND [(km/s)²] = a_MOND [m/s²] × r [kpc] × 3.0857e19 / 1e6

**a_0 = 1.2e-10 m/s²** (Milgrom constant, literature value)

Zero free parameters — a_0 is not fitted.

## Inputs

- [data/rotation/rotation_ds006_rotmod.csv](../../data/rotation/rotation_ds006_rotmod.csv)
- [qng_obs_mond_reference.py](../../tests/cpu/qng_obs_mond_reference.py)
- QNG-OBS-001 audit for side-by-side comparison

## Checks

**Check 1 — MOND improves median chi²/dof over baryon-only:**
```
median chi²/dof (MOND) < median chi²/dof (baryon-only)
```

**Check 2 — MOND improvement ratio >= 2.0x:**
```
median_baryon / median_MOND >= 2.0
```
MOND is a well-validated model — it should improve substantially over
baryon-only. Gate 2.0x is the expected minimum for a sample like DS006.

**Check 3 — MOND improves majority of galaxies:**
```
fraction(chi²_MOND < chi²_baryon) > 0.60
```

**Check 4 — Compare against QNG-OBS-001:**
```
Report ratio: (median_baryon / median_MOND) vs (median_baryon / median_QNG_OBS001)
```
Informational. If MOND ratio > QNG-OBS-001 ratio, MOND fits better than
per-galaxy QNG flat model. If QNG-OBS-001 ratio > MOND ratio, the QNG flat
model (with per-galaxy freedom) beats MOND.

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass.

**Interpretation:**
- PASS with MOND ratio > QNG-OBS-001 ratio: MOND fits better than QNG flat
  (even with per-galaxy freedom). The chi-field must have a MOND-like radial
  profile, not a flat one.
- PASS with MOND ratio < QNG-OBS-001 ratio: QNG flat with per-galaxy freedom
  beats MOND. The flat chi-field absorbs more variance than MOND's radial profile.
- FAIL: MOND doesn't improve substantially — data quality issue or wrong a_0.

## Artifact paths

- `07_validation/audits/qng-obs-mond-reference-v1/report.json`
- `07_validation/audits/qng-obs-mond-reference-v1/summary.md`
