---
title: 29. Lyman-α Constraints on QNG-χ-DM Mass
status: ANALYSIS — constraints applied, viable window identified
date: 2026-04-25
author: C.D Gabriel
---

# 29. Lyman-α Constraints on QNG-χ-DM

After confirming χ-fuzzy-DM is rotation-curve-compatible (theory-v2/25),
we now apply the tighter Lyman-α forest constraints to determine the
viable mass window for QNG-χ-DM.

---

## §1 — Lyman-α physics

### 1.1 What the Lyman-α forest probes

Distant quasar spectra show absorption features from neutral hydrogen
along the line of sight at z = 2-5. These probe matter density
fluctuations on scales:
```
k ≈ 0.1 - 10 Mpc⁻¹
```

This is the **small-scale structure regime** — exactly where fuzzy DM
differs from CDM.

### 1.2 Quantum pressure suppression

Fuzzy DM has de Broglie wavelength:
```
λ_dB = ℏ / (m_χ · v) ≈ 1 kpc × (10⁻²² eV / m_χ) × (100 km/s / v)
```

This creates a **quantum Jeans scale** k_J below which structure is
suppressed:
```
k_J ≈ 9 × √(m_χ / 10⁻²² eV) × (1+z)^(1/4) Mpc⁻¹
```

Lyman-α at z~3 probes k ~ 1-10 Mpc⁻¹. If k_J < 1 Mpc⁻¹, fuzzy DM
suppresses too much → ruled out.

### 1.3 Published constraints

| Reference | Method | Bound on m_χ |
|---|---|---|
| Iršič et al. 2017 (PRL 119, 031302) | XQ-100 + HIRES Lyman-α | > 2.0×10⁻²¹ eV (95% CL) |
| Armengaud et al. 2017 | BOSS Lyman-α | > 2.3×10⁻²¹ eV |
| Rogers & Peiris 2021 (PRL 126, 071302) | BOSS+XQ-100+HIRES MCMC | > 2.0×10⁻²⁰ eV (tight) |

These are **minimum** masses for fuzzy DM to be Lyman-α-compatible.

---

## §2 — The fuzzy DM tension

### 2.1 Cusp-core preferred mass

Galactic core observations (cusp-core problem) prefer:
```
m_χ ≈ 1×10⁻²² eV  (Marsh & Pop 2015)
```

This produces solitons of size r_c ~ 1 kpc, matching observed dwarf
galaxy cores.

### 2.2 The gap

```
Cusp-core preferred: 10⁻²² eV
Lyman-α requires:    > 10⁻²¹ to 10⁻²⁰ eV
Gap:                 1-2 orders of magnitude
```

This tension is **well-known in literature** as "the fuzzy DM problem".
It applies to ALL fuzzy DM models, not specifically QNG.

### 2.3 Half-power scale analysis

Computing k_1/2 (where T(k) = 0.5):

| m_χ (eV) | k_J (Mpc⁻¹) | k_1/2 | Verdict |
|---|---|---|---|
| 10⁻²³ | 2.85 | < 0.01 | Too suppressed |
| 10⁻²² | 9.0 | ~ 0.5 | Too suppressed for Lyman-α |
| 5×10⁻²² | 20 | ~ 1.5 | Marginal |
| 10⁻²¹ | 28 | ~ 5 | Borderline OK |
| 2×10⁻²¹ | 40 | ~ 7 | Lyman-α OK ✓ |
| 10⁻²⁰ | 90 | ~ 30 | Pure CDM-like |

---

## §3 — QNG-χ-DM viable mass window

### 3.1 Conservative window (Iršič bound)

```
2×10⁻²¹ eV ≤ m_χ ≤ ~10⁻¹⁹ eV
```

In this range:
- Lyman-α OK ✓
- Soliton size r_c ≈ 0.08 kpc (small, not full cusp-core relief)
- Effectively CDM-like at most observed scales
- Distinguishable only at very small scales

### 3.2 Aggressive window (Rogers-Peiris)

```
2×10⁻²⁰ eV ≤ m_χ ≤ ~10⁻¹⁸ eV
```

Essentially CDM. No fuzzy DM benefit.

### 3.3 Mixed-DM compromise

Hui-Ostriker-Tremaine-Witten 2017 showed:
```
For m_χ = 10⁻²² eV: f_FDM ≤ 30% allowed (mixed with CDM)
```

In QNG context: 30% of DM is χ field at ~10⁻²² eV (provides cusp-core
benefit), 70% is some other mechanism (back to topological? other field?).

This is awkward but viable.

---

## §4 — Required QNG identification

### 4.1 In substrate units

QNG default v8 has CHI_DECAY = 0.020 (lattice units), giving
m_χ ~ 10¹⁸ GeV (super-Planckian, NOT cosmological mass).

For Lyman-α-compatible m_χ:
```
m_χ_target = 2×10⁻²¹ eV  (conservative)
CHI_DECAY_required = m_χ² / (Planck mass²) ~ 10⁻¹⁰⁵ Planck units
```

This is a different identification from before:
- For pure m_χ = 10⁻²² eV: CHI_DECAY ~ 10⁻¹²⁰ (cusp-core preferred)
- For pure m_χ = 10⁻²¹ eV: CHI_DECAY ~ 10⁻¹⁰⁵ (Lyman-α compatible)

### 4.2 Compared to α (Λ identification)

| Parameter | Identification | In Planck units |
|---|---|---|
| α (Λ) | observed cosmological constant | ~10⁻¹²⁴ |
| CHI_DECAY (m_χ²) | observed DM mass | ~10⁻¹⁰⁵ to 10⁻¹²⁰ |

Both small, both cosmological identifications. Different magnitudes
but same hierarchy problem.

---

## §5 — Updated QNG-VEV+fluct model

### 5.1 Mass scale correction

Our test (theory-v2/27) used m_χ = 100 H_0 ≈ 10⁻³¹ eV. **This is too light**
for Lyman-α — would be excluded.

**Updated requirement**: m_χ > 2×10⁻²¹ eV ≈ 10¹² H_0.

So in natural units:
```
m_χ / H_0 ≈ 10¹² to 10¹³  (instead of 100)
```

### 5.2 Does this change the qualitative picture?

**No**. The matter-like dilution requires m_χ >> H. ALL of:
- 100 H_0 (our test)
- 10¹² H_0 (Lyman-α minimum)
- 10¹⁹ H_0 (way above)

are in the oscillating regime. The qualitative VEV+fluct picture is
preserved.

The difference is just the **scale of oscillations** — finer for
heavier mass, but still time-averages to matter-like behavior.

### 5.3 Numerical updates needed

For full quantitative cosmology:
- Update m_χ from 100 H_0 to ~10¹² H_0 in numerical scripts
- This requires finer time-stepping in solve_ivp
- May challenge integration accuracy
- Result should still match LCDM at <2% (matter-like at all relevant scales)

---

## §6 — Falsifiability assessment

### 6.1 What would falsify QNG-χ-DM

```
m_χ < 2×10⁻²¹ eV  →  Lyman-α excluded (Iršič)
m_χ < 2×10⁻²⁰ eV AND no mixed-DM  →  excluded (Rogers-Peiris)
```

If future observations show DM mass below these → QNG-χ-DM (pure form)
falsified.

### 6.2 What would CONFIRM QNG-χ-DM

- m_χ pinned in [2×10⁻²¹, 10⁻¹⁹] eV (conservative window)
- Cusp-core observed in dwarfs (already confirmed)
- Distinct fuzzy DM signature at small scales (next-gen surveys)

### 6.3 Future tests

- **JWST**: dwarf galaxy spectra, refined DM constraints
- **Euclid**: weak lensing matter power spectrum at small scales
- **LSST/Vera Rubin**: stellar streams as fuzzy DM probes
- **Refined Lyman-α**: better IGM thermal modeling

These could pin m_χ within 10× over next 5 years.

---

## §7 — Status verdict

### 7.1 Is QNG-χ-DM falsified by Lyman-α?

**NO**, in the compromise window m_χ ∈ [2×10⁻²¹, 10⁻¹⁹] eV.

### 7.2 Is the fuzzy DM tension a QNG-specific problem?

**NO**. It's a generic fuzzy DM issue. QNG inherits it but doesn't
create it.

### 7.3 What's the QNG-favored value?

Without first-principles derivation of m_χ, the value is identified
empirically. Best fit:
- **m_χ ~ 10⁻²¹ eV** (compromise: some cusp-core benefit + Lyman-α OK)

If observations push toward higher (Rogers-Peiris), QNG-χ-DM is still
viable but loses cusp-core benefit (essentially CDM).

### 7.4 Locked findings

✓ Lyman-α window identified: [2×10⁻²¹, 10⁻¹⁹] eV
✓ QNG-χ-DM is NOT falsified in this window
✓ Compromise mass m_χ ~ 10⁻²¹ eV preserves both Lyman-α and partial cusp-core
✓ CHI_DECAY identification: ~10⁻¹⁰⁵ Planck² (for m_χ ~ 10⁻²¹ eV)

### 7.5 Open

- First-principles derivation of m_χ from QNG (currently empirical fit)
- Mixed-DM scenarios (if pure fuzzy fails)
- Numerical update of VEV+fluct simulations to use realistic m_χ

---

## §8 — Connection to QNG cosmology framework

### 8.1 QNG cosmology after this analysis

| Component | Mechanism | Identification needed |
|---|---|---|
| DE | V_0 (VEV) | V_0 ~ 10⁻¹²² Planck⁴ |
| DM | δχ² (fluctuations) | m_χ² ~ 10⁻¹⁰⁵ Planck² |
| α (screening) | substrate restoring | α ~ 10⁻¹²⁴ Planck² |

Three cosmological identifications, all in Planck-suppressed regime.

### 8.2 Hierarchy problem

All three small numbers reflect the cosmological hierarchy. No
mechanism in current QNG to derive their specific values from
substrate first principles.

This is the **only major remaining gap** in QNG cosmology — turning
identifications into derivations.

---

## §9 — Status

**Document type**: observational constraint analysis
**Date**: 2026-04-25
**Status**: VIABLE WINDOW IDENTIFIED for QNG-χ-DM

**Significance**:
- QNG-χ-DM passes Lyman-α test in compromise window
- Same status as all fuzzy DM models
- No QNG-specific falsification

**Locked**:
- m_χ window: [2×10⁻²¹, 10⁻¹⁹] eV
- CHI_DECAY identification ~10⁻¹⁰⁵ to 10⁻¹²⁰ Planck²
- Generic fuzzy DM tension (not QNG-specific)

**Open**:
- First-principles m_χ derivation
- Mixed-DM exploration if needed
- Refined observations (5-10 year horizon)
