# QNG Lensing Data Interface v1

Type: `test`
ID: `TEST-LENS-002`
Status: `draft`
Author: `C.D Gabriel`

## Purpose

This document is a pre-registration specification. It declares the interface between the QNG lensing proxy defined in `qng-lensing-proxy-v1.md` (DER-LENS-001) and the real cluster offset data in `data/lensing/cluster_offsets_real.csv`. No numerical comparison against the real data may be run until this document exists in the repository and has been reviewed. Results obtained before this document was committed are exploratory only and do not constitute a registered test.

## Inputs

- [qng-lensing-proxy-v1.md](qng-lensing-proxy-v1.md)
- data/lensing/cluster_offsets_real.csv
- data/lensing/README_ds006_cluster_offsets.md (if present)

---

## Section 1: Observable Description

### 1.1 What is cluster_offsets_real.csv?

A cross-matched catalog pairing two independent centroid estimates for each galaxy cluster: one from baryonic (X-ray) emission, one from the SZ pressure signal. The offset between them is the primary observable.

Built by `scripts/build_ds006_cluster_offsets.py` cross-matching:

- **Baryon catalog (MCXC):** Meta-Catalogue of X-ray detected Clusters (Piffaretti et al. 2011, A&A 534, A109). 1743 clusters from ROSAT-based surveys (NORAS, REFLEX, BCS, SGP, NEP, MACS, CIZA), homogenised to overdensity delta=500. Position = X-ray centroid/peak in 0.1–2.4 keV band.

- **SZ catalog (PSZ2):** Second Planck SZ catalogue (Planck Collaboration 2016, A&A 594, A27). 1653 SZ detections, 1203 confirmed clusters. Position = SZ decrement peak after beam deconvolution using matched multi-filter (MMF3) detection on 30–857 GHz Planck maps.

Cross-matching: by MCXC ID if present in PSZ2; otherwise by sky proximity (max 5 arcmin separation).

### 1.2 Column schema

| Column | Units | Description |
|--------|-------|-------------|
| `system_id` | — | Cluster identifier (MCXC name format JHHMM.m+DDMM) |
| `baryon_x` | degrees | X-component of baryon centroid in local tangent-plane frame (anchored to 0.0) |
| `baryon_y` | degrees | Y-component of baryon centroid (anchored to 0.0) |
| `lens_x` | degrees | X-component of lensing/SZ centroid in same frame |
| `lens_y` | degrees | Y-component of lensing/SZ centroid in same frame |
| `sigma_grad_x` | degrees | X-component of proxy gradient direction (currently = lens_x; see §5.3 warning) |
| `sigma_grad_y` | degrees | Y-component of proxy gradient direction (currently = lens_y; see §5.3 warning) |
| `sigma` | degrees | Offset uncertainty (uniform 0.3 deg placeholder; see §1.5) |
| `baryon_ra_deg` / `baryon_dec_deg` | degrees J2000 | Absolute baryon centroid coordinates |
| `lens_ra_deg` / `lens_dec_deg` | degrees J2000 | Absolute SZ centroid coordinates |
| `sep_arcmin` | arcminutes | Great-circle separation between centroids |
| `match_mode` | — | `id` (matched by catalog ID) or `sky` (matched by proximity) |

The 2D offset vector for cluster i: `delta = (lens_x(i), lens_y(i))` since baryon centroid is anchored at origin.

### 1.3 How was the "lensing centroid" computed?

> **Terminology note:** The `lens_x/lens_y` columns follow the QNG DS-006 pipeline naming convention. The PSZ2 centroid is an SZ pressure centroid — NOT a weak gravitational lensing shear centroid. The GR deflection formula `alpha = 4GM/c²b` was NOT directly applied to produce these positions.

The PSZ2 centroid is derived from the SZ effect using MMF3 detection with a generalized NFW (GNFW) pressure profile (Arnaud et al. 2010) whose angular scale is inferred assuming a GR FLRW cosmology (H₀, Ω_m, Ω_Λ from Planck 2015). Position = maximum-likelihood SZ signal centroid.

### 1.4 What is the baryon centroid?

MCXC X-ray position = X-ray surface brightness centroid or peak in 0.1–2.4 keV ROSAT band. PSPC beam FWHM ~25–60 arcsec (off-axis dependent). Nominal positional uncertainties 10–30 arcsec per sub-catalog. MCXC homogenisation propagates source positions without re-reduction.

### 1.5 Uncertainty model

`sigma` is fixed at **0.3 degrees (18 arcmin)** uniformly — a placeholder. Actual per-cluster uncertainty should account for ROSAT PSPC positional error, Planck beam (~7 arcmin at 100 GHz), SZ photometric noise, and cluster morphology. The uniform sigma is deliberately conservative and may only be used for the structural cosine test, not for magnitude-calibrated inference.

---

## Section 2: GR Assumptions Embedded in the Observable

### 2.1 MCXC (baryon/X-ray side)

- ROSAT photon-to-position mapping assumes flat spacetime detector geometry
- X-ray surface brightness centroiding uses beta-model or simple centroiding in a GR background
- M₅₀₀ inferred via hydrostatic equilibrium in a GR potential (used for catalog homogenisation, not positional centroid directly)
- LCDM cosmology (H₀=70, Ω_m=0.3, Ω_Λ=0.7) assumed for luminosity homogenisation — does not affect sky coordinates

### 2.2 PSZ2 (SZ/pressure-centroid side)

- SZ decrement centroiding uses GNFW pressure profile fitted in GR LCDM cosmology
- Angular diameter distance D_A(z) computed in GR FLRW (Planck 2015 best-fit LCDM)
- Hydrostatic equilibrium assumed to set characteristic angular scale when spectroscopic z is available
- Multi-frequency foreground cleaning calibrated with GR-standard CMB power spectra (LCDM)

### 2.3 Cross-matching

- Haversine formula assumes GR static background for local sky patch
- 5 arcmin tolerance reflects empirical knowledge from GR LCDM simulations of merging clusters

### 2.4 Summary

All centroid positions are angular sky coordinates. The GR lensing deflection formula was NOT applied to produce them. GR enters through: NFW/GNFW profile shape assumptions, LCDM D_A(z) for angular scale setting, and hydrostatic equilibrium for mass-based radius normalisation. These conditioned the centroid uncertainty and profile-fit width, not the centroid sky coordinates directly.

---

## Section 3: Proxy Output Description

### 3.1 What DER-LENS-001 produces

```
Phi_lens(i) = (h_00(i) + h_11(i)) / 2       [lensing potential proxy]
alpha_lens(i) = -grad(Phi_lens)(i)           [signed deflection proxy]
D_lens = sum_i |alpha_lens(i)|               [total unsigned deflection strength]
```

### 3.2 What alpha_lens(i) is and is not

**IS:** A signed dimensionless scalar on each graph node. Encodes sign and direction of local substrate gradient. Sensitive to C_eff gradient and sigma-memory term.

**IS NOT:** In physical units (not arcseconds, not radians). In 2D — it is a scalar on a 1D ordered graph and cannot specify north/south/east/west displacement for any specific cluster. Cluster-specific — defined on a generic graph, not on specific sky positions.

---

## Section 4: Crossing Assumptions

| # | Assumption | Classification |
|---|---|---|
| 4.1 | Sign of `alpha_lens(i)` corresponds to a preferred physical direction in the substrate | **Declared bridge** — mapping 1D graph gradient to 3D/2D sky direction not yet derived |
| 4.2 | Graph node ordering corresponds to cluster catalog ordering | **Declared bridge** — no physical principle derived for this mapping |
| 4.3 | C_eff gradient direction is isotropically distributed across clusters under the null | **Earned assumption** — all-sky sample with no preferred direction |
| 4.4 | Observed 2D offset vector direction carries information about substrate gradient direction | **Declared bridge with physical motivation** — this is the hypothesis being tested |
| 4.5 | Uniform sigma=0.3 deg does not bias the cosine direction test | **Declared bridge (conservative)** — large sigma inflates variance, not bias |
| 4.6 | Proxy gradient direction = `atan2(sigma_grad_y, sigma_grad_x)` per pre-committed convention | **Declared bridge — convention must be fixed before running** |

---

## Section 5: The Test — Declared Before Running

### 5.1 Structural prediction

The QNG lensing proxy predicts that the lensing centroid is systematically displaced from the baryon centroid in a direction **correlated with the C_eff gradient direction** encoded in `alpha_lens(i)`. The distribution of observed 2D offset vectors across the cluster sample is predicted to be anisotropic — preferentially aligned with the local substrate gradient, not isotropically distributed.

This is a **directional alignment prediction only**. It does not predict the magnitude of offsets in arcminutes.

### 5.2 Null hypothesis

Offsets are isotropically distributed in 2D sky angle. The cosine of the angle between any observed offset vector and any reference direction is uniformly distributed on [-1, +1] with mean zero. This is the expectation under GR with baryonic processes (mergers, sloshing) generating offsets in directions uncorrelated with any external gradient field.

### 5.3 Test statistic

```
T = (1/N) * sum_{i=1}^{N} cos(theta_obs(i) - theta_proxy(i))
```

where:
- N = cluster pairs with `sep_arcmin > 0.05` arcmin (fixed before running)
- `theta_obs(i) = atan2(lens_y(i), lens_x(i))`
- `theta_proxy(i) = atan2(sigma_grad_y(i), sigma_grad_x(i))`

Expected value under null: **E[T] = 0**

> **CRITICAL WARNING:** In the current build, `sigma_grad_x = lens_x` and `sigma_grad_y = lens_y`. This makes the test **trivially circular** — T will always be +1.0. The `sigma_grad` columns must be replaced by an independent proxy gradient assignment derived from the QNG geometry estimator output BEFORE any comparison is run. Running the test on the current CSV without fixing this is not a valid test.

### 5.4 Negative controls

**(1) Randomised gradient directions:** Replace each `theta_proxy(i)` with U[0, 2π]. Recompute T. Repeat 1000 times. This defines the null distribution. The main test passes only if real T lies in the tail at p < 0.05.

**(2) Shuffled cluster-proxy assignments:** Randomly permute the proxy-to-cluster mapping. Recompute T. Repeat 1000 times. Tests whether the signal depends on the specific cluster ordering rather than aggregate directional structure.

**(3) GR-only baseline (no memory):** Recompute proxy with sigma-memory term set to zero (C_eff = C_GR). Recompute T. A valid QNG signal requires |T_real| > |T_GR-baseline|.

### 5.5 Pass criterion

The test passes if and only if ALL of the following hold simultaneously:

1. |T_real| > T₀₉₅ from control (1) — p < 0.05
2. Mean of T from control (1) is consistent with zero
3. T from control (2) is NOT significant at p < 0.05
4. |T_real| > |T_GR-baseline| from control (3)

A result satisfying only condition 1 is an anomaly requiring investigation, not a pass.

---

## Section 6: What This Test Does and Does Not Prove

### 6.1 If the test passes

**Does mean:** Statistically significant directional consistency between the QNG proxy and the observed offset distribution; signal not reproduced by randomised directions or shuffled assignments; enhanced by memory term vs. GR baseline.

**Does NOT mean:** QNG is correct. Offsets are caused by QNG. A quantitative prediction of offset magnitudes. Interface assumptions (Section 4) are validated.

### 6.2 If the test fails

Two distinct failure modes must be investigated separately before concluding QNG is inconsistent with data:

**Failure mode A — Proxy structure wrong:** The geometry estimator assigns gradient directions unrelated to the physical centroid offset mechanism. Requires revision of DER-LENS-001 or its upstream inputs.

**Failure mode B — Interface assumptions wrong:** One or more crossing assumptions in Section 4 is sufficiently invalid that the test cannot detect a real signal. The bridge in §4.1 (1D graph gradient → 2D sky direction) is the most likely failure surface.

---

## Section 7: What Must Be Resolved Before a Magnitude Comparison

| Prerequisite | Status | Required for |
|---|---|---|
| **Matter sector closure:** derive `h_00(i) ~ f(M_eff, r_eff, C_eff)` grounded to physical mass | Open | Converting proxy to arcsecond prediction |
| **Dimensional bridge:** physical scale of one graph edge in Mpc/arcsec at cluster distance | Open | Calibrating `alpha_lens` to physical deflection angle |
| **4×4 metric resolution:** identify correct lensing combination of `h_μν` (cf. Bardeen Φ+Ψ) | Open | Correct GR-QNG comparison at quantitative level |
| **Per-cluster sigma:** replace uniform 0.3 deg with individual positional uncertainties | Open | Any magnitude-calibrated confidence statement |
| **Proxy gradient projection:** fix convention mapping 1D gradient sign to 2D sky angle | **Blocking — must fix before ANY run on real data** | Basic validity of the cosine test |

---

## Open Items Checklist

- [ ] Replace `sigma_grad_x/y` with independent proxy gradient from QNG geometry estimator
- [ ] Fix and document the 1D→2D gradient projection convention
- [ ] Replace uniform sigma=0.3 deg with per-cluster positional uncertainties
- [ ] Derive matter sector grounding: `h_00(i) ~ f(M_eff, r_eff, C_eff)`
- [ ] Derive dimensional bridge: physical scale per graph edge
- [ ] Resolve 4×4 metric for lensing sector
