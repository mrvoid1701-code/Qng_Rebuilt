# QNG-OBS-004

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `observational_fit`

## Title

Galaxy rotation curves — QNG Yukawa radial profile (2 global parameters)

## Purpose

OBS-001/002/003 established that:
- The flat chi-field (C_K ≈ const) fails to scale with baryonic mass (OBS-001 Check 3)
- The substrate amplitude 0.225 has no predictive power without unit conversion (OBS-002)
- MOND radial profile achieves 1.70x improvement with zero free parameters (OBS-003)

Einstein's physical diagnosis (2026-04-06): the flat approximation is wrong.
The correct test uses the full Yukawa kernel from DER-QNG-027:

```
V²_QNG(r) = V²_baryon(r) + A × C_K(r, λ)
C_K(r, λ) = (1 + r/λ) × exp(-r/λ)
```

Two global free parameters across all 175 galaxies:
- **λ** [kpc]: Yukawa screening length (physical, same for all galaxies)
- **A** [(km/s)²]: global amplitude (absorbs the rho_0 unit conversion)

For fixed λ, A_opt is determined analytically by global weighted least squares
across all data points simultaneously. Then λ is scanned on a log grid to find
the global chi² minimum.

This test has 2 free parameters for 3391 data points across 171 galaxies —
far more constrained than OBS-001 (171 free params). The comparison with MOND
(0 free params) is the key benchmark.

## Inputs

- [qng-am-fixing-v1.md](../../04_qng_pure/qng-am-fixing-v1.md) — DER-QNG-027
- [data/rotation/rotation_ds006_rotmod.csv](../../data/rotation/rotation_ds006_rotmod.csv)
- [qng_obs_mond_reference.py](../../tests/cpu/qng_obs_mond_reference.py) — OBS-003 MOND baseline
- [qng_obs_yukawa_reference.py](../../tests/cpu/qng_obs_yukawa_reference.py)

## Model

**Yukawa kernel:** C_K(r, λ) = (1 + r/λ) × exp(-r/λ)

**Global fit:** for fixed λ, solve for A_opt analytically:
```
A_opt(λ) = Σ_i [w_i × res_i × CK_i] / Σ_i [w_i × CK_i²]
```
where res_i = v²_obs,i - v²_baryon,i, CK_i = C_K(r_i, λ), w_i = 1/(v²_err,i)²,
and the sum is over ALL data points across ALL galaxies simultaneously.

**Lambda scan:** log-uniform grid from 0.1 kpc to 10000 kpc (200 points).
Best λ = argmin χ²_total(λ).

**Limiting cases:**
- λ → ∞: C_K → 1 (flat model, recovers OBS-001 global flat)
- λ ~ r_galaxy: genuine radial profile
- λ → 0: C_K → 0 (no correction)

## Checks

**Check 1 — Yukawa improves over baryon-only:**
```
median chi²/dof (Yukawa best-fit) < median chi²/dof (baryon-only)  [38.870]
```

**Check 2 — Yukawa improves over MOND:**
```
(median_baryon / median_Yukawa) > (median_baryon / median_MOND)
i.e., improvement_ratio_Yukawa > 1.702  [OBS-003 result]
```
MOND uses 0 free params; Yukawa uses 2. Yukawa must at minimum match MOND
to justify the radial profile as a valid model.

**Check 3 — Best-fit λ in physically interesting range:**
```
1 kpc < λ_best < 500 kpc
```
If λ_best → ∞, the Yukawa model degenerates to the flat model (OBS-002 failure).
If λ_best is in the galactic range, the radial profile is doing real work.

**Check 4 — A_opt positive:**
```
A_opt > 0
```
The chi-field must produce a positive correction. Negative A_opt means the
Yukawa profile is compensating for baryon over-prediction, not adding chi-field.

**Check 5 — Improvement justified vs MOND (AIC comparison):**
```
AIC_Yukawa < AIC_MOND
AIC = n × ln(chi²_total/n) + 2k
where k=2 for Yukawa, k=0 for MOND
```
Informational. If Yukawa AIC < MOND AIC, the 2-parameter model is preferred
over the 0-parameter model by the Akaike criterion.

## Decision rule

**Overall PASS** if Checks 1, 2, 3, 4 pass.

**Interpretation of PASS:**
The Yukawa radial profile of the chi-field fits galaxy rotation curves better
than MOND with a physically motivated screening length. This motivates:
- Fixing λ from first principles (λ = sqrt(β/(α·z)) × a_lattice)
- OBS-005: fixing A from rho_0 (zero free parameters total)

**Interpretation of FAIL:**
- Check 2 fails: Yukawa doesn't beat MOND even with 2 free params → wrong profile
- Check 3 fails (λ → ∞): the flat limit is preferred → radial structure irrelevant
- Check 3 fails (λ very small): Yukawa collapses to zero → no chi-field signal

## Artifact paths

- `07_validation/audits/qng-obs-yukawa-reference-v1/report.json`
- `07_validation/audits/qng-obs-yukawa-reference-v1/summary.md`
