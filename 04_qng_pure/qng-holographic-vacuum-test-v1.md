---
type: note
id: NOTE-QNG-029
title: Holographic vacuum energy test on QNG substrate — boundary L² scaling confirmed but magnitude off by factor N_H
status: NEGATIVE result with structural insight — boundary mechanism real but missing factor 1/N_H per mode
author: C.D Gabriel
date: 2026-05-06
upstream:
  - DER-QNG-066 (Stability Principle)
  - DER-QNG-067 (ℏ derivation)
  - DER-QNG-080 (Gap 13 A1 classical falsification)
  - DER-QNG-090 (cosmology diagnosis)
downstream: open — soft-mode weighting investigation needed
---

# NOTE-QNG-029 — Holographic vacuum test on QNG substrate

## Motivation

User intuition (drawing of central balance principle, 2026-05-06):
- Există un punct de echilibru între QM/GR și hot/cold
- Din acest centru ies ℏ și α (Λ)
- A single value of α should satisfy all observational constraints simultaneously

This intuition was tested over 5 stages today:

1. **Golden ratio identification** (`α = φ⁻ⁿ`) — TESTED, FALSIFIED:
   only one accidental match (α=0.005 ≈ 1/φ¹¹) at chance level
2. **Channel A invariant analog to |H|·T** — TESTED, NEGATIVE: 
   no R-universal quantity in existing CPU-058/074 data
3. **Multi-constraint scan in (α, β) plane** — REVEALING:
   peak is a curve (degeneracy along β/α = const), not a point
4. **Stability Principle 1/L^p test (PBC)** — TESTED:
   1/L⁴ scaling — too suppressed by 124 orders at L=N_H
5. **Holographic boundary test (Dirichlet)** — TESTED, this document.

## Test specification

**Hypothesis (Cohen-Kaplan-Nelson holographic dark energy analog in QNG):**
The Stability Principle (`E_vacuum = 0`) holds in bulk PBC, but a finite causal
horizon (Dirichlet boundary) introduces residual surface vacuum energy:

```
E_residual ≈ c_O × (R_H/ℓ_P)² × ℏω_typ
           ≈ c_O × N_H²        (in Planck natural units)
ρ_residual ≈ E_residual / V_H ≈ c_O × N_H²/N_H³ = c_O/N_H
Λ × ℓ_P²   ≈ 8π × c_O / N_H
```

If `c_O ~ O(1)` from substrate geometry, this would predict `Λ × ℓ_P² ~ 1/N_H`.

**Observed:** `Λ × ℓ_P² ≈ 2.84 × 10⁻¹²² ≈ 1/N_H²`.

So the question becomes: does QNG produce 1/N_H or 1/N_H² scaling?

## Numerical method

GPU computation (NVIDIA RTX 3060, 13 GB):
- Cubic lattice L³ with z=6 coordination
- KG dispersion: `ω²(k) = (β/μ) · 2 · (3 - cos kx - cos ky - cos kz)`
- Substrate parameters: β=0.35, μ=0.857, ℏ_QNG=0.229
- L scan: {16, 24, 32, 48, 64, 96, 128, 192, 256, 384}

Three sub-tests:
- **PBC (periodic):** k = 2πn/L, n ∈ {0,...,L-1}
- **Dirichlet (boundary):** ω² = (β/μ)·4·[sin²(πn_x/(2L+2)) + ...], n ∈ {1,...,L}
- **IR cutoff:** Dirichlet sum restricted to ω < ω_max for various ω_max

## Results

### Test 1: PBC scaling

| L | ℏ_required(L) | δℏ vs ℏ(∞) |
|---|---|---|
| 8 | 0.22942 | 4.0×10⁻⁵ |
| 32 | 0.22938 | 1.5×10⁻⁷ |
| 128 | 0.22938 | 5.9×10⁻¹⁰ |
| 256 | 0.22938 | 3.0×10⁻¹¹ |

**Fit:** `|δℏ(L)| ~ 1.71 × 10⁻¹ × L⁻⁴·⁰¹⁷`

**Verdict:** PBC vacuum is super-suppressed (1/L⁴). Stability Principle holds
strictly even at finite L — too strict for observed Λ. Predicted residual at
N_H = 10⁶¹: ~10⁻²⁴⁶ (124 orders too small).

### Test 2: Dirichlet boundary

| L | Σω_PBC | Σω_Dir | diff = Dir - PBC |
|---|---|---|---|
| 32 | 49998.30 | 50050.45 | 5.22×10¹ |
| 64 | 399986.65 | 400196.44 | 2.10×10² |
| 128 | 3199893.30 | 3200735.04 | 8.42×10² |
| 256 | 25599146.47 | 25602518.70 | 3.37×10³ |

**Fit:** `|diff(L)| ~ 5.02 × 10⁻² × L^2.005`

**Verdict:** Boundary contribution scales as L² (surface area). This IS the
holographic geometric signature. Coefficient `c_O ≈ 0.05`.

**But magnitude check:**
- Predicted `Λ × ℓ_P² (N_H) ≈ 3.34 × 10⁻⁶²`
- Observed `Λ × ℓ_P² ≈ 2.84 × 10⁻¹²²`
- **Off by factor 10⁶¹ ≈ N_H** — off by exactly one order of N_H

### Test 3: IR cutoff Dirichlet

Restricting sum to ω < ω_cutoff for ω_cutoff ∈ {0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0}:

| ω_max | Slope | Comment |
|---|---|---|
| 0.10 | 3.46 | volumetric |
| 0.50 | 3.05 | volumetric (L³) |
| 1.00 | 3.01 | volumetric (L³) |
| 5.00 | 3.00 | volumetric (L³, full) |

**Verdict:** Restricting to IR modes does NOT change scaling — still L³.
Volume term dominates regardless of mode cutoff.

## Diagnosis: missing factor 1/N_H per mode

Each mode at the boundary in QNG contributes energy `ℏω_typ ≈ 0.18` (Planck-scale).

**For holographic dark energy at observed magnitude:**
boundary modes need to contribute energy `ℏ × (1/R_H)` (soft IR), not `ℏω_typ` (hard UV).

That is: each boundary mode should be **suppressed by factor `ℓ_P/R_H = 1/N_H`**.

QNG substrate (as currently formulated) does NOT implement this suppression. All
modes contribute their natural lattice frequencies. This produces:
- `Λ_QNG ~ 1/N_H` (boundary mechanism)
- `Λ_observed ~ 1/N_H²`

**One factor of N_H is missing.**

## Comparison table (full diagnostic)

| Mechanism | Scaling | Λ × ℓ_P² (predicted) | vs. observed |
|---|---|---|---|
| PBC (Stability strict) | 1/L⁴ | 10⁻²⁴⁶ | ×10⁻¹²⁴ (too small) |
| Dirichlet bulk | L³ | 10⁺¹⁸³ | ×10⁺³⁰⁵ (catastrophic) |
| Dirichlet boundary (Δ) | L² | 10⁻⁶² | ×10⁺⁶⁰ (too large by N_H) |
| IR-only Dirichlet | L³ | divergent | not saved |
| **Required (observed)** | **L^?** | **10⁻¹²²** | **target** |

## What this means for Gap 5

**Confirmed structurally:**
- The user's drawing intuition (boundary → Λ) has a real geometric basis in QNG
- Surface scaling L² emerges naturally from Dirichlet boundary

**Refined gap statement:**
- Old: "α has no derivation in QNG"
- New: "α requires a factor `1/N_H` suppression per boundary mode that QNG
  does not currently provide; specifically, modes at the cosmological horizon
  must be IR-soft with energy `ℏ/R_H`, not UV-hard with energy `ℏω_max`"

This is a **MORE SPECIFIC** open problem. It points to:
- Soft-mode weighting at boundary
- Or temporal averaging over Hubble time (Padmanabhan-Verlinde argument)
- Or quantum gravitational mode-suppression at horizon

## Path forward

### Path 1: Soft-mode weighting investigation
Test whether QNG substrate has natural mechanism for IR-suppression at horizon.
Candidates:
- Decoherence of high-ω modes over Hubble time
- Causal isolation of UV modes outside horizon
- Quantum gravitational gap at IR

### Path 2: Temporal averaging
Compute time-averaged vacuum energy `<E_vac>_T = (1/T) ∫₀^T E_vac dt`
for evolution time `T = O(R_H)`. If oscillator modes with ω_typ × T >> 1 
average to suppression `1/(ω·T) = 1/N_H`, get correct factor.

Numerically: requires evolution `T = L` for `L = 32, 64, 128`. ~hours on GPU.

### Path 3: Accept observation
Treat α (and equivalently Λ) as observational input fixed by Hubble. QNG
provides framework but doesn't derive cosmological constant value.

This matches `DER-QNG-080` (Gap 13 A1 classical falsification) and 
`DER-QNG-090` (cosmology diagnosis): same conclusion via different routes.

## Falsified candidates (closed cleanly)

After today's session, the following can be moved to "closed/falsified":

1. **Golden ratio α = φ⁻ⁿ identification** (5 levels of fits, all chance-level)
2. **Channel A invariant analog to |H|·T** (no R-universal quantity exists)
3. **Multi-constraint uniqueness in (α,β) plane** (degenerate curve, not point)
4. **Naive Stability Principle gives Λ_obs** (1/L⁴ super-suppressed)
5. **Naive Dirichlet boundary gives Λ_obs** (off by N_H, magnitude wrong)

## Files generated

- `scripts/qng_alpha_beta_3d_landscape.png` (4-panel visualization)
- `tests/cpu/qng_holographic_vacuum_test.py` (this notebook content)

## Honest verdict

**This session did NOT close Gap 5.** It refined the problem statement and
eliminated 5 candidate mechanisms cleanly. The drawing intuition (centre of
balance → ℏ + α emerge) is **75% confirmed**:

- ✅ Centre exists (Stability Principle, DER-QNG-066)
- ✅ ℏ emerges from centre (DER-QNG-067)
- ✅ α has surface-mechanism geometry (L² scaling confirmed)
- ❌ α magnitude wrong by factor N_H (missing soft-mode weighting)

**One specific physical question remains:** what produces the factor 1/N_H
suppression for boundary modes at the cosmological horizon in QNG?

This is a more focused, concrete problem than "why is Λ small". Worth tracking
as an active sub-program of Gap 5.

## Cross-references

- `DER-QNG-066` Stability Principle (`qng-stability-principle-v1.md`)
- `DER-QNG-067` ℏ derivation paper (`qng-hbar-derivation-paper-draft-v1.md`)
- `DER-QNG-080` Gap 13 classical falsification (`qng-gap13-A1-step1-result-v1.md`)
- `DER-QNG-090` cosmology diagnosis (`qng-cosmology-diagnosis-v1.md`)
- `qng_alpha_beta_3d_landscape.png` (visualization in scripts/)

## Memory entry summary

Tested 5 candidate mechanisms for deriving α/Λ in QNG today (2026-05-06).
All 5 falsified or shown insufficient. Holographic boundary mechanism gives
correct geometric scaling (L² surface) but predicts Λ off by exactly factor
N_H. The missing piece is "soft-mode weighting" at the cosmological horizon —
each boundary mode must contribute `ℏ/R_H` (IR-soft) not `ℏω_max` (UV-hard).
Path 2 (temporal averaging) is the most concrete next test if this line is
pursued.
