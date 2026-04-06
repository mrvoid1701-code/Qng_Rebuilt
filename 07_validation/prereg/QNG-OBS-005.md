# QNG-OBS-005

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-06`
test_class: `observational_fit`

## Title

Galaxy rotation curves — QNG ring Yukawa disk convolution (2 global parameters)

## Purpose

OBS-001 through OBS-004 all failed. The Newton audit (2026-04-06) identified the
root cause: every OBS test used either a flat profile or a point-source Yukawa
kernel C_K(r) = (1+r/λ)exp(-r/λ). Neither correctly represents the chi-field
from a vortex ring source nor from a disk of rings.

DER-QNG-031 derives the correct ring Yukawa kernel K_ring(ρ, z; R, λ) and shows:
- The far-field (r>>R) reduces to point-source Yukawa (OBS-004 was testing the right
  functional form in that limit; its λ→∞ result is a genuine physical finding)
- The disk convolution is qualitatively different: the chi-field at ρ_obs is the
  superposition from all baryonic rings at radii R_i ≠ ρ_obs

This test implements the disk convolution: for each galaxy, the chi-field at each
observation radius ρ_obs is the sum of K_ring_velocity contributions from all
baryonic matter rings at radii R_i in that galaxy, weighted by V²_baryon(R_i).

Key question: does the cross-ring contribution (R_i ≠ ρ_obs) produce a radial
profile that fits rotation curves better than the single-scale Yukawa of OBS-004?

## Model

**Single vortex ring velocity profile (derived in DER-QNG-031 §4):**

For a ring source at radius R in the z=0 plane, the circular velocity contribution
at observation radius ρ_obs (midplane, z=0) is:

```
K_vel(ρ_obs, R; λ) = ρ_obs × (1/2π) ∫₀²π exp(-d/λ) × (ρ_obs - R cos u)
                      × (1/λ + 1/d) / d²  du

d(u) = sqrt(ρ_obs² + R² - 2 ρ_obs R cos u + ε²)   [ε = 0.05 kpc softening]
```

This is the radial force (times ρ_obs) from the chi-field of a single ring source.

**Disk convolution model:**

For a galaxy with observed baryonic profile {(R_i, V²_b(R_i))}:

```
V²_chi(ρ_obs) = A × Σ_i V²_b(R_i) × K_vel(ρ_obs, R_i; λ) / K_norm
```

where K_norm is a normalization factor (Σ_i V²_b(R_i)) ensuring that A has
units (km/s)² and is comparable to the flat-ether amplitude of OBS-001.

**Full prediction:**

```
V²_model(ρ_obs) = V²_baryon(ρ_obs) + V²_chi(ρ_obs)
```

**Global free parameters (2):**
- **λ** [kpc]: Yukawa screening length (same for all galaxies)
- **A** [(km/s)²]: global amplitude (absorbs ρ₀ × G_QNG unit conversion)

For fixed λ, A_opt is solved analytically by global WLS (same as OBS-004).

**Relation to OBS-004:**  
Setting R_i = ρ_obs = r (no cross-ring contribution), K_vel → (1+r/λ)exp(-r/λ)/r,
and V²_chi → A × (1+r/λ)exp(-r/λ) — exactly OBS-004. This test is a strict
generalization. FAIL → OBS-004 failure recovered. PASS → disk geometry matters.

## Inputs

- [qng-ring-yukawa-profile-v1.md](../../04_qng_pure/qng-ring-yukawa-profile-v1.md) — DER-QNG-031
- [data/rotation/rotation_ds006_rotmod.csv](../../data/rotation/rotation_ds006_rotmod.csv)
- [qng_obs_mond_reference.py](../../tests/cpu/qng_obs_mond_reference.py) — OBS-003 baseline (1.702×)
- [qng_obs_yukawa_reference.py](../../tests/cpu/qng_obs_yukawa_reference.py) — OBS-004 baseline (FAIL)
- [qng_obs_ring_reference.py](../../tests/cpu/qng_obs_ring_reference.py)

## Checks

**Check 1 — Ring model improves over baryon-only:**
```
median chi²/dof (ring best-fit) < median chi²/dof (baryon-only)  [38.870]
```

**Check 2 — Ring model improves over MOND (1.702×):**
```
improvement_ratio_ring > 1.702
```
Ring model uses 2 free params (same as OBS-004). Must beat 0-param MOND.

**Check 3 — Best-fit λ in physically interesting range:**
```
1 kpc < λ_best < 5000 kpc
```
λ→∞ allowed (flat Coulomb limit); λ in galactic range preferred (ring geometry active).

**Check 4 — A_opt positive:**
```
A_opt > 0
```

**Check 5 — Ring improves over point-Yukawa OBS-004 [informational]:**
```
improvement_ratio_ring > improvement_ratio_OBS004
```
If ring model beats OBS-004, the disk convolution is doing real work.
(OBS-004 reported improvement_ratio; stored in OBS-004 report.json.)

**Check 6 — a_M correlation [informational]:**
```
Pearson r(A_per_galaxy, M_proxy_per_galaxy) > 0.40
```
Measure per-galaxy A by fitting each galaxy independently. Compute Pearson r
against MOND proxy mass (= V_flat² × R_last / G_QNG). Gate: r > 0.40.
This is the Check 3 that killed OBS-001.

## Decision rule

**Overall PASS** if Checks 1, 2, 3, 4 pass.

**Interpretation of PASS:**
The disk convolution ring model fits rotation curves with ≥ MOND quality at 2 free
parameters. This motivates fixing λ from first principles and testing A ∝ M_baryon.

**Interpretation of FAIL:**
- If improvement_ratio < 1.702: disk convolution still not sufficient → profile shape wrong
- If λ→∞: Coulomb limit confirmed; need to explain flat rotation curve from matter geometry
- If Check 6 also fails: a_M–mass problem persists; matter source identification blocking

## Artifact paths

- `07_validation/audits/qng-obs-ring-reference-v1/report.json`
- `07_validation/audits/qng-obs-ring-reference-v1/summary.md`
