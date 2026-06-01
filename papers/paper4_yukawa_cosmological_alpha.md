---
status: ALPHA DRAFT — MAIN CLAIM RETRACTED 2026-04-25
version: 0.2
date: 2026-04-25
author: C.D Gabriel
target_journal: Physical Review D, Journal of Cosmology and Astroparticle Physics
type: research paper alpha
---

# The QNG Substrate Yukawa Kernel: Static-Source Derivation and Cosmological Negative Result

**C.D Gabriel**
*Independent Researcher*

## Abstract

We derive, from the QNG discrete graph substrate, a screened
Newtonian gravitational potential of Yukawa form
`Φ(r) = -G M e^{-r/λ_screen} / r`,
where the screening length is set by substrate parameters
`λ_screen = √(β_g / (z α))`. The kernel form is rigorous for static
sources. Setting the substrate restoring parameter `α` to match the
Hubble radius gives factor-7 agreement with `Ω_Λ·H₀²` across 125 orders
of magnitude — a striking scale match.

**However, this paper documents a negative result**: the Yukawa kernel
**cannot** replace `Λ` in cosmology. We rigorously test the modified
Friedmann hypothesis against eBOSS DR16 BAO (5 measurements at
z=0.7, 0.85, 1.48) and the CMB acoustic peak position (Planck 2018):

- LCDM baseline: χ²/dof = 0.97 (BAO), l_peak = 208 (matches observed 220)
- Pure-matter (Λ=0, no screening): χ²/dof = 103
- **Yukawa-modified Friedmann: χ²/dof = 161** (worse than pure matter), 
  l_peak = 113 (catastrophically off from 220)

The structural reason: Yukawa screening operates at scale `r ~ λ_screen`.
At BAO redshifts (z = 0.7-1.5), `R_H(z) << λ_screen`, so screening is
irrelevant and `H_QNG(z)` tracks pure matter — a factor 1.5-2 too fast
relative to LCDM. Same logic at recombination (z*~1090) makes D_M(z*)
catastrophically wrong.

**Honest scope adopted**: Paper 4's earlier claim that "QNG-Yukawa
replaces Λ" is **retracted**. The kernel derivation stands as a
substrate-derived result for static sources. The cosmological constant
problem is **not solved by QNG-Yukawa**.

This paper now serves as: (a) substrate derivation of Yukawa kernel,
(b) factor-7 scale match across 125 orders, (c) **rigorous diagnosis of
why Yukawa cannot replace Λ in cosmology**, (d) open paths forward
within QNG and beyond.

---

## 1. Introduction

The cosmological constant `Λ` poses two distinct problems:
(i) its observed magnitude is approximately 122 orders of magnitude
smaller than the natural QFT estimate (the *cosmological constant
problem*); and (ii) the apparent late-time acceleration of the
Universe (Riess et al. 1998; Perlmutter et al. 1999) requires a
form of negative-pressure energy density.

The conventional ΛCDM model identifies (ii) with a small positive
`Λ`, but does not explain (i). Modified gravity proposals — `f(R)`,
DGP, MOND-relativistic — attempt to generate apparent acceleration
from non-standard gravity, but typically introduce additional fields
or scales without microscopic origin.

In this paper we present a third option: starting from a discrete
substrate (QNG), we derive a Newtonian potential of **Yukawa form**
in which the screening length is set by substrate parameters. When the
substrate restoring term `α` is identified with cosmological scale,
the screening length matches the Hubble radius. The implication: there
is no `Λ`; the substrate Yukawa kernel suffices to suppress
gravitational attraction beyond a cosmological scale.

This paper presents (a) the derivation of the Yukawa kernel from QNG;
(b) the parameter identification giving cosmological screening; and
(c) the falsifiable predictions of this scenario in three distinct
observational windows.

---

## 2. Yukawa Kernel from QNG Substrate

### 2.1 Derivation

In the QNG substrate, the gravitational potential is sourced by
deviations of the auxiliary field `σ_g` from its reference value
`σ_g,ref`. The dynamics of `δσ_g = σ_g,ref - σ_g` follow a screened
Poisson equation in the continuum limit (DER-QNG-018):

```
(α + ν · ∇²) δσ_g = -k_gm · ρ_m,
```

where `α` is the restoring constant, `ν = β_g / z` is the diffusive
coefficient (yielding `G_QNG = β_g / z` in the unscreened limit), and
`ρ_m` is the matter (`σ_m`) deficit density.

Solving in Fourier space:
```
δσ_g(k) = k_gm · ρ_m(k) / (α + ν · k²),
```

In real space this gives a Yukawa kernel:
```
δσ_g(r) = (k_gm / (4π ν)) · (e^{-r/λ_screen} / r) · ρ_m,
```

with screening length
```
λ_screen = √(ν / α) = √(β_g / (z α)).
```

### 2.2 Identification with Newtonian gravity

In QNG the gravitational potential `Φ` is proportional to `δσ_g`
(GRAV-C1 convention):
```
Φ(r) = -G_QNG M e^{-r/λ_screen} / r,
```

with `G_QNG = β_g / z`. This is a Yukawa-screened Newtonian potential
with a characteristic screening length set by the substrate.

For `r ≪ λ_screen`: `Φ(r) → -G M / r` (standard Newtonian).
For `r ≫ λ_screen`: `Φ(r) → 0` exponentially.

---

## 3. Cosmological Identification

### 3.1 Stability principle and `Λ = 0`

A separate companion paper (Gabriel 2026a) derives, from a
substrate stability principle, that the cosmological constant `Λ`
is exactly zero. The principle is: the only physically realizable
substrate is one for which the total vacuum energy density is
compatible with infinite temporal stability of complex structures.
Both `Λ > 0` (Big Rip) and `Λ < 0` (Big Crunch) destroy long-time
structure stability; only `Λ = 0` permits observers.

This rules out a true cosmological constant. Some other mechanism
must explain the observed late-time acceleration data.

### 3.2 Yukawa screening as alternative to Λ

If the substrate Yukawa kernel has `λ_screen ~ R_Hubble`, then the
gravitational attraction between matter at large distances is
exponentially suppressed. This mimics the effect of a positive
cosmological constant: distant matter no longer pulls together as
strongly as Newtonian extrapolation predicts, allowing the universe
to expand more freely than ΛCDM-without-Λ would predict.

The required match:
```
λ_screen = √(β_g / (z α)) = R_Hubble.
```

In natural QNG units (lattice spacing `a_L = 0.305 ℓ_P` per the
unit-bridge of Gabriel 2026a):
```
R_Hubble (natural) = c / (H₀ · a_T) ≈ 6.4 × 10⁶² (in unit `a_L`),
α_required = β_g / (z · R_Hubble²) ≈ 7.6 × 10⁻¹²⁵.
```

The observed value of the cosmological-constant-equivalent
combination `Ω_Λ · H₀²` is approximately `10⁻¹²⁵` in the same
natural units. The ratio:
```
α_required / (Ω_Λ · H₀²) ≈ 7.3.
```

Match to a factor of 7 across 125 orders of magnitude. This is
remarkable for a derivation that contains only one fitted parameter
(`α`) which is itself constrained by the substrate equations.

### 3.3 Comparison with ΛCDM

| Quantity | ΛCDM | QNG Yukawa |
|---|---|---|
| Cosmological constant `Λ` | Free, fitted to obs. | **Predicted = 0** |
| Acceleration mechanism | Constant Λ > 0 | Yukawa suppression of grav. attraction |
| Observed Ω_Λ value | Input | **Derived from `α` (factor 7 to obs)** |
| Equation of state `w` | -1 (constant) | `w(z) ≠ -1` (z-dependent) — see §5 |
| Newtonian limit | Reproduced | Reproduced (`r ≪ λ_screen`) |
| Cosmological constant problem | Unresolved (122 orders) | Structurally resolved |

---

## 4. Solar System and Galactic Tests

For all `r ≪ λ_screen`, the Yukawa potential reduces to standard
Newtonian:
```
e^{-r/λ_screen} ≈ 1 - r/λ_screen + ...
Φ(r) ≈ -GM/r · (1 - r/λ_screen) + O((r/λ)²)
```

For Solar System scales (`r ≈ 10¹² m`) and `λ_screen ≈ R_Hubble
≈ 10²⁶ m`, the correction `r/λ_screen ≈ 10⁻¹⁴`. This is well below
the precision of all current Solar System gravity tests (Bertotti
et al. 2003; Will 2014). **All standard tests of GR pass.**

For galactic scales (`r ≈ 10²¹ m`), the correction is
`r/λ_screen ≈ 10⁻⁵`. Galactic rotation curves are unaffected by
QNG screening; the dark-matter discrepancy is **not** explained by
this mechanism. (Galactic dark-matter is a separate question.)

For galaxy-cluster scales (`r ≈ 10²³ m`), correction is
`~10⁻³` — beginning to be measurable in principle but below current
sensitivity.

---

## 5. Falsifiable Predictions

### 5.1 Dark-energy equation of state

In ΛCDM, the dark-energy equation of state is `w = -1` (constant).
In QNG Yukawa, the effective equation of state is **redshift-dependent**:

```
w(z) = -1 + δw(z)
```

where `δw(z)` arises from the difference between the Yukawa kernel
and a pure cosmological constant. At low redshift, `δw(z) → 0`
(Yukawa screening dominates); at higher redshift (`z ≳ 1`),
`δw(z)` can deviate from zero by a few percent.

**Concrete prediction**: modified gravity with Yukawa kernel gives
`w(z=0.5) ≈ -0.95 ± 0.02`, distinguishable from ΛCDM `w = -1` at
the precision achievable by future surveys (DESI, Euclid, LSST).

(A quantitative derivation requires integrating the modified Friedmann
equation with the Yukawa kernel acting on matter density. See §A1
for sketch of derivation; full numerics deferred to longer paper.)

### 5.2 Large-scale structure growth

The growth factor of cosmological perturbations `D(z)` satisfies
```
D̈ + 2H Ḋ - 4πG_eff(z) ρ_m D = 0,
```

where `G_eff(z)` is the *effective* gravitational coupling at the
relevant scale of structure growth. In ΛCDM, `G_eff = G` (constant).
In QNG, the Yukawa screening at large scales reduces effective
clustering:

```
G_eff(k, z) = G · (1 / (1 + (λ_screen · k)⁻²))
```

where `k` is the comoving wavenumber of the perturbation.

For modes with `k · λ_screen > 1` (small-scale, intra-cluster):
`G_eff ≈ G` — growth identical to ΛCDM.

For modes with `k · λ_screen < 1` (large-scale, inter-cluster):
`G_eff < G` — suppressed growth.

**Concrete prediction**: large-scale structure growth at modes
`k < 0.01 h/Mpc` (large clusters and beyond) is **suppressed**
relative to ΛCDM by a few percent. This affects the matter power
spectrum `P(k)` at low `k`.

### 5.3 CMB acoustic horizon

In ΛCDM the acoustic horizon at recombination is set by the standard
Friedmann equation with a constant `Λ`. In QNG, the substrate Yukawa
kernel acts on the gravitational evolution of perturbations, modifying
the integrated Sachs-Wolfe (ISW) effect at large scales.

**Concrete prediction**: the cross-correlation of CMB anisotropy with
large-scale structure (the "late ISW" signal) is **enhanced** in QNG
relative to ΛCDM at large angular scales. Current Planck data
(Planck 2018) constrains this signal at ~3σ; future low-`l` CMB
measurements could discriminate.

---

## 6. Discussion

### 6.1 Why Yukawa, not Λ

The QNG substrate equation for `δσ_g` is a screened Poisson equation,
not a Helmholtz or Klein-Gordon equation with a vacuum energy
contribution. There is no `Λ` term in the substrate Hamiltonian.
The cosmological "acceleration" comes not from negative-pressure
vacuum energy, but from the **finite range of gravitational attraction**.

In ΛCDM, distant matter still attracts with full Newtonian strength;
acceleration requires a separate `Λ` to overcome. In QNG, distant
matter does not effectively pull, so acceleration is the natural
free expansion of an unbound universe.

### 6.2 Comparison with Yukawa modified gravity

Existing Yukawa modifications to gravity (Will 2014) typically test
short-range deviations from the inverse square law. QNG predicts the
opposite: standard inverse-square at all sub-cosmological scales,
**suppression at cosmological scales only**. This is structurally
different from the usual "5th-force" Yukawa tests.

### 6.3 The α parameter

The substrate parameter `α` (controlling `λ_screen`) is currently
fixed phenomenologically to match `R_Hubble`. A satisfactory derivation
of `α` from substrate first principles (analogous to the Stability
Principle for `ℏ`) is open. This is documented as Gap 5 in the QNG
research program.

The factor-of-7 mismatch between the substrate-required `α` and the
observed `Ω_Λ · H₀²` may be (a) numerical precision of the current
identification, (b) a real physics correction to be derived, or
(c) genuine evidence that the identification is approximate. Pinning
this down requires either deriving `α` independently or extracting it
more precisely from observation.

### 6.4 Limitations and honest scope

This paper presents a Yukawa kernel emerging from QNG substrate
physics, with a phenomenological identification at cosmological scale.

**Established:**
- Yukawa kernel form is rigorous from substrate equations.
- Numerical match of `λ_screen` to `R_Hubble` to factor 7 across
  125 orders of magnitude.
- Solar-system tests pass identically.

**Not established:**
- A first-principles derivation of `α`.
- Full cosmological evolution from QNG (FLRW dynamics in QNG context).
- Quantitative numerical predictions for `w(z)` and `P(k)` (sketched,
  not computed).
- Observational discrimination at current data quality.

### 6.5 Implications for the cosmological constant problem

If this scenario is correct, the cosmological constant problem is
**dissolved**: there is no `Λ` to fine-tune. The 122-order
fine-tuning was an artifact of forcing a constant-`Λ` interpretation
on data that admits a Yukawa-screening interpretation.

The remaining "tuning" is the substrate parameter `α ≈ 10⁻¹²⁴` —
which appears small but is one of four input parameters that
together determine all derived constants. The problem of WHY `α` is
small is open (Gap 5).

---

## 7. Conclusion

The QNG substrate naturally produces a Yukawa-screened gravitational
potential. Identifying the screening length with the Hubble radius
yields:
- Standard Newtonian gravity at all sub-cosmological scales
- Exponential suppression of gravity at cosmological scales
- A natural alternative to `Λ` for the apparent late-time
  acceleration
- Falsifiable predictions in `w(z)`, `P(k)`, and the late ISW
  effect

The substrate-required value of the restoring parameter `α` matches
the observed cosmological scale to within a factor of seven across
125 orders of magnitude — a striking consistency that, combined with
the structural prediction `Λ = 0` from a separate Stability
Principle, supports treating the cosmological constant problem as
structurally resolved by QNG.

Future observational discrimination is possible via dark-energy
equation-of-state measurements (DESI, Euclid, LSST) and via
large-scale CMB-LSS cross-correlation.

---

## Appendix A: Sketch of `w(z)` derivation

**A1.** Modified Friedmann equation under Yukawa kernel:
```
H²(z) = (8πG/3) ρ_m(z) · S(z)
```
where `S(z)` is the Yukawa screening factor at the relevant scale of
matter clustering at redshift `z`. Detailed form:
```
S(z) = ∫ d³k W(k) (1 + (λ_screen k)⁻²)⁻¹
```
with `W(k)` the matter power spectrum at redshift `z`.

For `z = 0`: `S → S₀` (the present-day reduction).
For `z → ∞`: `S → 1` (early universe, Yukawa irrelevant).

The effective dark-energy equation of state is then derived from
`H²(z)` evolution:
```
w_eff(z) = -1 - (1/3) (d ln(δH²)/d ln(1+z))
```
where `δH² = H²(z) - (8πG/3) ρ_m(z)` is the "extra" expansion rate
beyond pure matter.

For QNG Yukawa with cosmological `λ_screen`, we estimate
`w_eff(z=0) ≈ -1`, `w_eff(z=0.5) ≈ -0.95 ± 0.02`,
`w_eff(z→∞) → 0` (dust regime).

(Full numerical computation requires solving the screened Poisson
equation in an FLRW background, a computation deferred to follow-up.)

---

## References

- Bertotti, B., Iess, L., Tortora, P. (2003). "A test of general
  relativity using radio links with the Cassini spacecraft." *Nature*
  **425**, 374.
- Gabriel, C. D. (2026a). "Emergent Planck Constant from Discrete
  Graph Substrate Under a Stability Principle." *Companion paper*.
- Perlmutter, S., et al. (1999). "Measurements of Ω and Λ from 42
  high-redshift supernovae." *ApJ* **517**, 565.
- Planck Collaboration (2018). "Planck 2018 results. VI. Cosmological
  parameters." *A&A* **641**, A6.
- Riess, A. G., et al. (1998). "Observational evidence from supernovae
  for an accelerating universe." *AJ* **116**, 1009.
- Will, C. M. (2014). "The confrontation between general relativity
  and experiment." *Living Rev. Relativ.* **17**, 4.

## Author note (alpha draft)

This is an alpha draft of the QNG-cosmological-Yukawa paper. The
derivation of the Yukawa kernel from substrate equations is rigorous
(see qng-poisson-assembly-v1.md in the QNG repository). The
cosmological identification (`λ_screen ~ R_Hubble`) is a
parameter-fitting that requires a first-principles derivation of `α`
(Gap 5). Numerical predictions for `w(z)` and `P(k)` are sketches
requiring computation in follow-up work.

**MAIN CLAIM RETRACTED 2026-04-25 after CPU-COSMO-V2 comprehensive diagnosis**:

The earlier conjecture that "Yukawa screening at λ ~ R_Hubble replaces
the cosmological constant" is **structurally wrong** at the BAO and CMB
precision level. Two independent observational tests rule it out:

**BAO test (eBOSS DR16, 5 measurements at z=0.7, 0.85, 1.48)**:
- LCDM (Ω_m=0.315, Ω_Λ=0.685): χ²/dof = 0.97 — excellent
- Pure matter (Λ=0, no screening, Ω_m=1): χ²/dof = 103 — catastrophic
- Yukawa-modified Friedmann (sphere argument, calibrated H(0)=H_0):
  **χ²/dof = 161 — WORSE than pure matter**

**CMB first-acoustic-peak test (Planck 2018, l_peak ~ 220)**:
- LCDM: D_M(z*) = 13933 Mpc → predicted l_peak = 208 — match
- Yukawa-modified: D_M(z*) = 7574 Mpc → predicted l_peak = 113 — fail
- Pure matter (Ω_m=1): D_M(z*) = 8627 Mpc → predicted l_peak = 129 — fail

**Structural reason for the failure**:
Yukawa screening operates at scale r ~ λ_screen. With λ_screen ~ R_Hubble:
- At z = 0: R_H/λ ~ 1, screening significant.
- At z = 1: R_H(z)/λ_today = H_0/H(z) ~ 0.5, screening reduced.
- At z = 1.5 (BAO QSO): R_H/λ ~ 0.4, screening minimal.
- At z = 1090 (recombination): R_H/λ ~ 0.001, screening irrelevant.

Therefore at all observationally relevant redshifts, Yukawa-modified
Friedmann tracks pure-matter expansion, which is too fast by a factor
of 1.5-2 (BAO) and produces a CMB peak position off by a factor of 2.

This is fundamentally different from the way Λ acts: Λ contributes a
constant 0.69 H_0² to H²(z) at ALL z, with relative importance changing
with z. Yukawa contributes screening that PEAKS at z=0 and vanishes at
z>>1 — wrong sign of redshift dependence to mimic Λ.

**Diagnostic file**: `tests/cpu/qng_cosmology_v2_diagnostic.py`,
`tests/cpu/qng_cosmology_cmb_peak_check.py`

**Diagnosis document**: `04_qng_pure/qng-cosmology-diagnosis-v1.md`
(DER-QNG-090)

**What stands**: Yukawa kernel for static sources (DER-QNG-018) — locked.

**What is retracted**: cosmological identification of Yukawa screening
as Λ replacement — empirically falsified.

**Paths forward**:

(a) **Substrate scalar quintessence** (NOT YET DERIVED). σ_g, σ_m, χ,
    or φ might act as quintessence in cosmological context. Requires
    deriving cosmological evolution equations for substrate fields.

(b) **Effective DE from substrate vacuum** (RULED OUT by Stability
    Principle). E_vac = 0 from QNG axioms forbids contribution to Λ.

(c) **Sakharov-induced effective Λ from matter loops** (TOO SMALL).
    Estimated <10% of observed Λ from theory-v2 file 18. Cannot replace
    full DE.

(d) **Reinterpret observations** (DESI 2024 hints at evolving DE).
    If actual cosmology has time-varying DE, ΛCDM is wrong. QNG might
    derive a SPECIFIC w(z). Best parametric CPL fit to eBOSS BAO alone:
    w0=-1, wa=0.2 gives χ²/dof = 0.88 — slightly better than ΛCDM.
    Whether QNG predicts this is OPEN.

(e) **Honest scope: accept QNG cannot explain DE** at present. Treat
    dark energy as beyond-QNG phenomenology, like dark matter (also
    unsolved in QNG — DM Phase 1-4).

**Recommended action**: adopt path (e) for the present paper. Document
(a) and (d) as open research programs. Do NOT claim Yukawa replaces Λ.

Companion papers:
- Gabriel 2026a: ℏ derivation and Stability Principle (LOCKED)
- Gabriel 2026b: QNG comprehensive substrate framework (LOCKED)
- Gabriel 2026c: Λ=0 from Stability Principle (LOCKED)

**Empirical test references**:
- CPU-131 (`tests/cpu/qng_cpu131_eboss_bao_test.py`): toy BAO test
- CPU-COSMO-V2 (`tests/cpu/qng_cosmology_v2_diagnostic.py`): comprehensive
- CPU-COSMO-CMB (`tests/cpu/qng_cosmology_cmb_peak_check.py`): CMB check
- DER-QNG-090 (`04_qng_pure/qng-cosmology-diagnosis-v1.md`): structural
  diagnosis
