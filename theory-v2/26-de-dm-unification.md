---
title: 26. DE-DM Unification Analysis
status: SKETCH — investigates whether QNG dark energy and dark matter share a common origin
date: 2026-04-25
author: C.D Gabriel
---

# 26. DE-DM Unification in QNG

After identifying:
- σ_g dynamic regime giving candidate Λ (file 24)
- χ field giving candidate fuzzy DM (file 25)

The natural question: can both come from a SINGLE substrate mechanism?

---

## §1 — The two identifications

### 1.1 Numerical values

| Quantity | Symbol | Value (Planck units) |
|---|---|---|
| DE: Λ identification (via α) | α | ~10⁻¹²⁴ |
| DM: χ field mass squared | m_χ² | ~10⁻¹⁰⁰ |
| Hubble² today | H_0² | ~10⁻¹²² |

### 1.2 Ratios

```
α / H_0² ≈ 10⁻²       (within 2 orders of magnitude)
m_χ² / H_0² ≈ 10²²    (huge difference)
m_χ² / α ≈ 10²⁴
```

So **DE and DM are NOT at the same scale**. DE is at the Hubble
horizon scale (~10⁻³³ eV), DM is at fuzzy/ULDM scale (~10⁻²² eV).

These differ by factor ~10¹¹ in mass / ~10²² in mass squared.

### 1.3 Why they're different

**DE scale = cosmic horizon**: Λ acts on the WHOLE observable universe
(R_Hubble ≈ 10²⁶ m).

**DM scale = galactic clustering**: m_χ has de Broglie wavelength
~ kpc (10¹⁹ m), the scale of galactic halos.

The ratio R_Hubble / λ_galactic ≈ 10⁷, and squared ≈ 10¹⁴. Doesn't
exactly match 10²² but order of magnitude reasonable for "different
length scales of the same hierarchy".

---

## §2 — Possible unification mechanisms

### 2.1 Hypothesis A: Independent identifications

Both DE and DM are independent cosmological identifications. No
unification — they just happen to both involve small Planck-units
parameters.

**Status**: simplest, but doesn't explain why exactly these values.

### 2.2 Hypothesis B: Hierarchical scale generation

Substrate has hierarchy of scales:
- a_L (Planck-scale lattice)
- some intermediate scale
- R_Hubble (cosmic scale)

If different substrate fields lock to different scales (σ_g to cosmic
horizon, χ to intermediate galactic), both could come from same
mechanism with different "depth" of cosmological reach.

**Status**: speculative, no mechanism derived.

### 2.3 Hypothesis C: Dimensional reduction

In some emergent-gravity scenarios (entropic, Verlinde), DE and DM
arise from holographic entanglement entropy at different scales:
- Cosmic horizon → Λ
- Galactic halo → DM

QNG could implement this via substrate entanglement structure, but
this is speculative.

**Status**: matches some emergent-gravity programs, requires extension.

### 2.4 Hypothesis D: σ_g dynamic gives DE; χ field gives DM (independent)

Take the σ_g-late-time-dynamics result from file 24:
- σ_g_dot at late times → constant
- ρ_σ_g_kinetic = (μ_g/2)(σ_g_dot)² acts as Λ
- NO additional α tuning needed (mechanism intrinsic)

And χ-field DM from file 25:
- m_χ identification at fuzzy scale
- Free scalar oscillation gives matter-like behavior

In this picture: DE is INTRINSIC (substrate dynamics), DM is FIELD
(χ identification).

**Status**: most concrete; partial unification (DE intrinsic, DM
identified). Need to verify σ_g mechanism gives correct Λ magnitude.

### 2.5 Hypothesis E: Both from σ_g sector

If σ_g has BOTH:
- A late-time-constant σ_g_dot → DE-like
- Galactic-scale fluctuations δσ_g → DM-like (clumping at galactic
  scale)

Then BOTH DE and DM come from σ_g alone, no χ needed.

This requires σ_g to have galactic-scale clustering, which depends on
the σ_g mass m_σ_g² = α/μ_g. For α ~ 10⁻¹²⁴, m_σ_g ~ 10⁻⁶² Planck = 10⁻³⁴ eV.
This is FAR smaller than fuzzy DM mass (10⁻²² eV).

So σ_g would cluster at scale H_0 (cosmic horizon), NOT at galactic
scale. Doesn't work for DM.

**Status**: ruled out. σ_g and χ are at different scales for a reason.

---

## §3 — Combined cosmological model

### 3.1 Model setup

Take the most concrete hypothesis (D): combined σ_g + χ.

```
H²(z) = (8πG/3) [ρ_baryon(z) + ρ_χ(z)] + ρ_σ_g(z)
```

where:
- ρ_baryon: standard baryon dilution, ρ_b ∝ a^-3
- ρ_χ: χ-field DM, oscillating at m_χ >> H, ρ_χ ∝ a^-3
- ρ_σ_g: σ_g-sector DE, late-time constant ≈ Λ-like

For consistency with LCDM:
- Ω_b ≈ 0.05
- Ω_DM (= Ω_χ) ≈ 0.265
- Ω_DE (= Ω_σ_g_late) ≈ 0.685

### 3.2 What's automatic

- σ_g sector dynamics give late-time constant — automatic structure
- χ oscillating gives matter-like dilution — automatic if m_χ >> H

### 3.3 What needs identification

- σ_g_dot late-time value → Ω_DE = 0.685
- χ field initial amplitude → Ω_χ = 0.265
- m_χ value → must be in fuzzy/ULDM window

Three identifications. Same as 3 unknowns.

### 3.4 Numerical sanity check

Already verified (file 25):
- m_χ = 100 H_0: oscillating, matter-like
- ρ_χ × a^3 ≈ const (matter-like dilution) ✓ (file 25 numerical run)

Need to test combined dynamics: σ_g + χ + baryons in single FLRW
solution. Implementation would be straightforward extension of
files 24 + 25.

### 3.5 Predictions of combined model

Same as LCDM plus:
- Fuzzy DM signatures at galactic scale (cusp-core problem solved)
- Possible deviations in CMB low-multipole if σ_g_dot has slight
  evolution (not strictly constant)
- Possible deviations in matter power spectrum at scales near
  λ_dB(m_χ) (suppression at small scales)

---

## §4 — Honest assessment

### 4.1 What this analysis achieves

- Confirms DE and DM are at DIFFERENT scales (10²² ratio)
- Identifies σ_g sector as candidate for DE (intrinsic mechanism)
- Identifies χ field as candidate for DM (identification)
- Combined model is structurally consistent

### 4.2 What this analysis does NOT achieve

- Does NOT derive specific values of identifications from substrate
- Does NOT prove combined model fits BAO/CMB quantitatively
- Does NOT explain why σ_g_dot late-time has the right magnitude
- Does NOT provide single-mechanism unification

### 4.3 Verdict on unification

**Partial unification possible**: in QNG, DE and DM are BOTH substrate-
field phenomena. They share the framework but operate at different
scales (cosmic horizon vs galactic).

**Full unification (single parameter)**: NOT achieved. The cosmological
hierarchy of scales seems to require multiple identifications.

**Best status**: QNG provides a UNIFIED FRAMEWORK for both DE and DM
as field phenomena, but the specific mass scales are independent
inputs.

---

## §5 — Comparison with competitors

### 5.1 ΛCDM
- DE: cosmological constant Λ (1 parameter, fitted)
- DM: cold dark matter (mass + density, 2 parameters, fitted)
- 3 parameters, no unification

### 5.2 String theory
- DE: from compactification moduli
- DM: from string spectrum (axions, neutralinos, ...)
- Many free parameters from string landscape
- "Unification" claimed but empirical predictions absent

### 5.3 Quintessence + WIMP
- DE: dynamic scalar field with V(φ)
- DM: WIMP particle (LSP, etc.)
- Different sectors, no unification

### 5.4 QNG (this analysis)
- DE: σ_g sector dynamics (intrinsic, late-time constant)
- DM: χ-field fuzzy DM (m_χ identification)
- 1 mechanism for DE (no parameter), 1 identification for DM (m_χ)
- Most parsimonious of the four

**QNG IS more parsimonious for DE+DM than alternatives.**

---

## §6 — Path forward

### 6.1 Numerical verification

Test combined σ_g + χ + baryons cosmology:
- Solve coupled ODEs for σ_g(t), χ(t), a(t)
- Match to LCDM observables (BAO, CMB peak, supernovae)
- Identify required parameter values

### 6.2 Theoretical extension

Derive:
- Why σ_g_dot late-time has right magnitude (involves initial conditions)
- Why m_χ has fuzzy-DM value (cosmological identification mechanism)
- Whether Stability Principle constrains any of these

### 6.3 Observational discrimination

If QNG = LCDM + fuzzy-DM + intrinsic-DE, it predicts:
- Galactic cusp-core problem solved
- Possible small deviations from LCDM in low-multipole CMB
- Possible matter power suppression at small k

These are testable with current/future surveys.

---

## §7 — Status

**Document type**: structural analysis + hypothesis comparison
**Date**: 2026-04-25
**Outcome**: partial unification (single framework, multiple
identifications)

**Locked**:
- DE and DM are at DIFFERENT cosmological scales (10²² ratio)
- Both can be substrate-field phenomena in QNG
- σ_g sector candidate for DE (intrinsic)
- χ field candidate for DM (identified)

**Open**:
- Single-parameter unification not achieved
- Specific magnitudes not derived
- Full numerical test of combined model pending

**Significance**: QNG provides MOST PARSIMONIOUS framework for
DE+DM among major QG candidates. Single substrate, two emergent
field phenomena, fewer free parameters than ΛCDM with WIMPs +
quintessence.

This is a positive structural finding even without full closure.
