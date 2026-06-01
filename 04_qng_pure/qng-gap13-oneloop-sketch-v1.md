---
type: derivation
id: DER-QNG-081
title: Gap 13 one-loop α calculation — analytical sketch
status: SKETCH — identifies the loop diagrams and structure; full numerical evaluation pending
author: C.D Gabriel
date: 2026-04-25
upstream:
  - DER-QNG-080 (Gap 13 Step 1 — classical falsification)
  - DER-QNG-079 (BREAKTHROUGH retained as historical)
---

# DER-QNG-081 — One-loop α calculation: analytical sketch

## Goal

After CPU-141 ruled out classical α-running, the only remaining path
to α-flow in QNG is QUANTUM one-loop corrections. This document
sketches the analytical framework for computing β(α) at one loop.

If β(α) gives power-law behavior with exponent ~ 2, the breakthrough
hypothesis (DER-QNG-079) could be VINDICATED at quantum level.

## QNG action setup

The QNG v10 action (Euclidean, schematic) for σ_g sector:

```
S = ∫ dt d³x [ (1/2μ_g) (∂_t σ_g)² + (ν/2)(∇σ_g)² + (α/2)(σ_g - σ_ref)²
              + (CHI_REL) σ_g · ∇²χ + DELTA · σ_g · χ
              - (CHI_DECAY/2) χ²
              + (k_gm) σ_g · ρ_m + ...]
```

The bare 2-point function for σ_g (in momentum space):
```
G_σg^(0)(k, ω) = 1 / (μ_g ω² + ν k² + α)
```

For static (ω = 0): G_σg^(0)(k) = 1/(ν k² + α).

## One-loop diagrams contributing to α renormalization

The mass-like α parameter receives corrections from any 1PI two-point
diagram. At one loop:

### Diagram 1: χ tadpole

A single χ loop attached to σ_g via the σ_g - χ coupling.

```
Vertex: V_σχ = CHI_REL × ∇² + DELTA (when expanded around uniform σ_g)
χ propagator: G_χ(k) = 1/(CHI_DECAY + (CHI_REL/z) k²)
```

Loop contribution to σ_g 2-point function at zero external momentum:
```
δα_χ = (CHI_REL × ∇²/L² + DELTA)² · ∫ d³k/(2π)³ × G_χ(k)
```

The ∇²/L² piece probes typical k ~ 1/L (low momentum), the DELTA piece
is unsuppressed.

For the DELTA² term:
```
δα_χ_DELTA = DELTA² × ∫ d³k/(2π)³ × G_χ(k)
            = DELTA² × ∫₀^Λ_UV (k²dk/(2π²)) / (CHI_DECAY + (CHI_REL/z) k²)
            = DELTA² × (z/(CHI_REL)) × [Λ_UV - √(z·CHI_DECAY/CHI_REL) × arctan(...)]
            ≈ DELTA² × (z/CHI_REL) × Λ_UV
```

Numerically (Λ_UV = π in lattice units):
```
δα_χ_DELTA ≈ 0.04 × (6/0.35) × π = 0.04 × 17.1 × π ≈ 2.15
```

This is **MUCH LARGER than bare α = 0.005**! Confirms non-perturbative
regime — one-loop correction is 430× the tree-level value.

### Diagram 2: σ_m tadpole (matter source loop)

If σ_m is treated as quantum field, its tadpole contributes:
```
δα_σm = (k_gm × m_σm)² × G_σm tadpole
```

For matter ring sector with k_gm = 0.001 (small):
```
δα_σm ≈ 10⁻⁶ × tadpole — much smaller than χ tadpole
```

### Diagram 3: σ_g self-loop (via cubic coupling V_couple)

The V_couple = (g/2)(σ_ref - σ_m)² (1 - cos φ) introduces nonlinear
σ_g - σ_m coupling. At higher order, σ_g self-coupling appears.

For now, leading order is δα_χ ≈ 2.15.

## Implication: non-perturbative regime

The bare α is 0.005, one-loop correction is ~2.15. **The perturbative
expansion fails completely.**

This is consistent with an "infrared free" or "trivial" theory where
the bare coupling renormalizes dramatically.

In Wilsonian RG, when one-loop corrections are this large, must use
non-perturbative methods:
- Functional renormalization (Wetterich equation)
- Lattice Monte Carlo at multiple scales
- Exact fixed-point analysis

## Possible scenarios

### Scenario A: α flows to UV fixed point

Asymptotic safety analog: α has a UV fixed point at finite value α* > 0.
At Planck scale, α = α* . At lower scales, α flows according to non-trivial
β-function near fixed point.

If β(α) near fixed point has structure β(α) ~ -c (α - α*) p (power-law
in deviation), then α(L) ~ α* + (α₀ - α*) (L₀/L)^p.

For p = 2 to emerge, would need specific structure of fixed point.

### Scenario B: α flows to zero non-trivially

If β(α) has structure such that α(L) → 0 as L → ∞ with α ~ 1/L²
power-law, this would VALIDATE the dimensional argument as quantum
mechanism.

But this is a strong constraint on β-function — need to derive it
explicitly.

### Scenario C: α is genuinely fixed (no running)

Possible: the χ-tadpole δα ≈ 2.15 is a CONSTANT shift, not running.
Once renormalized, the shifted α' = α + δα is fixed at all scales.

This would mean α_eff_observed ≈ 2.15, not 0.005. Then:
λ_screen_observed = √(ν/α_eff) = √(0.0583/2.15) = 0.165 (lattice units)

That's MUCH smaller than 3.42 predicted from bare α = 0.005.

CPU-141 measured λ ≈ 2.67 (with lattice cutoff effects). NOT 0.165.

So integrated-out χ does NOT give the observed screening. Probably
because the integration is more subtle (involves derivatives, not just
masses).

## What the calculation actually requires

For a rigorous Gap 13 closure via quantum α-flow:

### Step 1: Build proper QNG effective action

```
Γ[σ_g] = -ln ∫ Dχ Dσ_m Dφ exp(-S[σ_g, χ, σ_m, φ]) | restricted to σ_g modes
```

Compute Γ at each scale L by truncating modes with |k| > 1/L.

### Step 2: Identify quadratic part of Γ

The effective α(L) is the coefficient of (σ_g - σ_ref)² in Γ at scale L.

### Step 3: Wilsonian flow equation

```
∂Γ/∂L = β(α, ν, μ, ...) · L^(some power)
```

### Step 4: Solve flow equation

Flow from Planck scale (L = a_L) down to observation scale (L = R_Hubble).
Track α(L). Check if α(R_Hubble) ~ 10⁻¹²⁴.

### Step 5: Verify with numerical Monte Carlo

Lattice MC at different scales, measure effective α at each. Compare
with analytical RG flow.

## Effort estimate

This is a graduate-thesis-level calculation:
- Step 1-2: 1-2 weeks (set up effective action machinery)
- Step 3: 2-3 weeks (derive flow equation)
- Step 4: 1 week (solve, plot)
- Step 5: 1-2 weeks (numerical verification)

**Total: 5-8 weeks of focused theoretical work.**

## Recommended next session priorities

Given this is a multi-week project, single-session work should:

1. **Set up the EFFECTIVE ACTION framework** explicitly for QNG
2. **Compute the χ-loop integral** rigorously (not just estimate)
3. **Identify if non-trivial fixed point exists** in 1-loop β(α)

If 1-loop suggests fixed point at α* ≠ 0 with power law p ~ 2 nearby,
breakthrough hypothesis would be PARTIALLY VINDICATED.
If 1-loop suggests no power-law, hypothesis is fully falsified and
must abandon α-running mechanism.

## Honest pause

This document SKETCHES the calculation; it does NOT solve it. The
sketch identifies:
- The relevant Feynman diagrams (χ tadpole dominant)
- The non-perturbative regime (one-loop >> tree)
- The need for functional RG / Wetterich equation
- The honest effort estimate (5-8 weeks)

For the autonomous-block remaining, will move to consolidation:
update GAP_INVENTORY, THEORY_STATE, and memory entries to reflect
DER-QNG-079 falsification + DER-QNG-080 finding.

This is real progress on the Long Option attack, even though we're
ending up at "honest acknowledgment that Gap 13 needs heavy theoretical
work" rather than "Gap 13 closed".
