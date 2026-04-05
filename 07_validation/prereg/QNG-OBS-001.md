# QNG-OBS-001

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `observational_fit`

## Title

Galaxy rotation curves — QNG flat-ether model vs baryon-only on DS006 sample

## Purpose

First real-data test of the QNG matter sector. Tests whether the QNG prediction
for rotation curve excess (Delta_V^2 = a_M x alpha x M_baryon — a flat contribution
from the chi field) fits better than baryon-only across 175 galaxies.

From DER-QNG-027 (a_M fixing program): the chi field from a galaxy's baryonic mass
creates a Yukawa-screened contribution to V^2. For galaxy scales r << lambda_Hubble,
this reduces to a PER-GALAXY CONSTANT:

```
V^2_QNG(r) = V^2_baryon(r) + a_M_galaxy
```

where a_M_galaxy is a single free parameter per galaxy (the amplitude of the
chi-field contribution). The QNG-specific prediction is:

```
a_M_galaxy ∝ V^2_baryon_max   (baryonic Tully-Fisher scaling)
```

This follows from Delta_V^2 = a_M x alpha x M_baryon and the baryonic Tully-Fisher
relation M_baryon ∝ V^4_max → a_M ∝ V^2_max.

A PASS confirms that (1) QNG fits better than baryon-only, and (2) a_M_galaxy
scales with baryonic content as predicted — the ether amplitude is not random,
it tracks the baryonic mass of the host galaxy.

## Inputs

- [qng-am-fixing-v1.md](../../04_qng_pure/qng-am-fixing-v1.md) — DER-QNG-027
- [data/rotation/rotation_ds006_rotmod.csv](../../data/rotation/rotation_ds006_rotmod.csv)
- [qng_obs_rotation_reference.py](../../tests/cpu/qng_obs_rotation_reference.py)

## Data description

File: `rotation_ds006_rotmod.csv`
Columns: system_id, radius [kpc], v_obs [km/s], v_err [km/s], baryon_term [(km/s)^2],
         history_term [(km/s)^2]

- baryon_term = V^2_baryon: total baryonic (stellar + gas) Newtonian contribution
- history_term = max(0, v_obs^2 - baryon_term): pre-computed residual

Sample: 175 galaxies, 3391 data points.

## Model

**Baryon-only:** V^2_pred(r) = V^2_baryon(r)

**QNG flat model:** V^2_pred(r) = V^2_baryon(r) + a_M_galaxy
  where a_M_galaxy fitted per galaxy by weighted least squares.

**Weighted least squares:** weight = 1 / (V^2_err)^2
  where V^2_err = 2 x v_obs x v_err (error propagation from v to v^2).

**Baryonic mass proxy:** M_proxy = max(baryon_term) over all radii in the galaxy.
  Proportional to V^2_max_baryon — a standard proxy for total baryonic mass.

## Checks

**Check 1 — QNG improves median chi^2/dof:**
```
median chi^2/dof (QNG) < median chi^2/dof (baryon-only)
```
QNG must improve fit quality across the sample. Expected: ~2x improvement
(already observed in preliminary scan: 38.3 → 16.8).

**Check 2 — QNG improves majority of galaxies:**
```
fraction(chi^2_QNG < chi^2_baryon) > 0.60
```
At least 60% of galaxies must be better fit by QNG than baryon-only.

**Check 3 — a_M scales with baryonic content (QNG-specific prediction):**
```
Pearson correlation r(a_M_galaxy, M_proxy) > 0.40
```
The ether amplitude must correlate with total baryonic mass. This is the key
QNG prediction: more massive galaxies have more chi-field contribution.
A random scatter would give r ~ 0; a physical mechanism gives r > 0.4.

**Check 4 — Majority of galaxies require positive ether:**
```
fraction(a_M_galaxy > 0) > 0.60
```
At least 60% of galaxies must need a positive chi-field contribution. Galaxies
with a_M < 0 are baryon-dominated (baryon model over-predicts) — acceptable
for a minority.

**Check 5 — a_M negative galaxies are more baryon-dominated:**
```
mean M_proxy(a_M < 0) > mean M_proxy(a_M > 0)
```
Galaxies where the QNG term is negative (baryons over-predict) should be
more massive/baryon-rich on average. This is physically consistent: in massive
ellipticals and bulge-dominated systems, the baryonic mass model may include
all the matter.

## Decision rule

**Overall PASS** if Checks 1, 2, 3, 4 pass (Check 5 is informational).

**Interpretation of PASS:**
The QNG flat-ether model fits galaxy rotation curves better than baryon-only,
and the ether amplitude scales with baryonic mass as predicted. This confirms
that the chi field of the QNG substrate produces a flat rotation excess
proportional to total baryonic mass. This motivates:
- QNG-OBS-002: fitting a GLOBAL a_M (one parameter for all galaxies)
- QNG-OBS-003: comparison with MOND (does QNG fit better, worse, or differently?)
- Fixing a_M from first principles (DER-QNG-027 + rho_0 constraint)

**Interpretation of FAIL:**
- Check 1 fails: QNG doesn't improve over baryon-only. The flat model is wrong.
  The chi field might have a different radial profile (not flat).
- Check 3 fails: a_M doesn't scale with mass. The ether amplitude is random —
  inconsistent with QNG where chi is sourced by matter.
- Check 4 fails: most galaxies have a_M < 0. The baryon model systematically
  over-predicts, suggesting a data quality issue or wrong stellar M/L ratios.

## Artifact paths

- `07_validation/audits/qng-obs-rotation-reference-v1/report.json`
- `07_validation/audits/qng-obs-rotation-reference-v1/summary.md`
