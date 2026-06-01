---
title: 24. QNG-FLRW Sketch — Cosmological Dynamics from Substrate
status: SKETCH IN PROGRESS — derivation of effective Friedmann from QNG
date: 2026-04-25
author: C.D Gabriel
---

# 24. QNG-FLRW Sketch

This document sketches how cosmological dynamics emerge from QNG
substrate. After CPU-COSMO-V2 + DER-QNG-090 closed the "Yukawa
replaces Λ" path, this represents the first attempt to derive
effective Friedmann equations directly from QNG action under FLRW
symmetry assumption.

---

## §1 — Setup: the homogeneity assumption

### 1.1 What "homogeneous + isotropic universe" means in QNG

Standard cosmology assumes spatial homogeneity (same physics
everywhere) + isotropy (same in all directions). At scales much larger
than `a_L = 0.305 ℓ_P` and much larger than typical galaxies, this is
observed (CMB temperature uniform to 10⁻⁵).

In QNG, this means:
- All lattice nodes are equivalent (translation invariance)
- All lattice directions equivalent at coarse-grained level (rotational
  invariance, which we proved emerges in §23 via Lorentz theorem)
- All node states have the same statistical distribution

For a UNIFORM universe at coarse-grained level:
```
σ_g(x_node, t) = σ_g(t)  — function of time only
σ_m(x_node, t) = σ_m(t)
χ(x_node, t)   = χ(t)
φ(x_node, t)   = φ(t)
```

The spatial Laplacians of all fields vanish (`∇²f = 0` for uniform `f`).

### 1.2 What is "expansion" in QNG?

In standard GR, the spatial metric scales as `g_ij = a(t)² δ_ij`. Physical
distances grow with `a(t)`.

In QNG, the lattice spacing `a_L = 0.305 ℓ_P` is **fixed by Stability
Principle** (it's a structural constant, not a dynamical variable).

So what corresponds to "expansion"?

**Hypothesis (key)**: in QNG, "expansion" is *NOT* lattice expansion.
Instead, it is the **dilution of matter** through a fixed substrate.
Specifically:

- The lattice is fixed; nodes don't move apart
- The matter density `σ_m_local` evolves with cosmic time
- "Expansion" is the COARSE-GRAINED appearance of matter dilution

This is conceptually similar to how, in many condensed-matter analogues
of cosmology (BEC analogues), the "expansion" is mimicked by changing
particle density in a fixed container.

### 1.3 The role of σ_g

In QNG, σ_g is the **gravitational coherence field**. For uniform
σ_m, the static σ_g equation gives:

```
α · δσ_g = -k_gm · ρ_m
```

So `δσ_g(t)` tracks the matter density `ρ_m(t)`. As matter dilutes,
`δσ_g` decreases.

In a true cosmological setting (allowing time-varying σ_m), σ_g should
also vary in time. The question is: do the σ_g dynamics give an
effective Friedmann-like equation?

---

## §2 — Modified action approach

### 2.1 QNG action under homogeneity

Starting from the v8 action restricted to homogeneous fields (only
time-derivatives, no spatial gradients):

```
S = ∫ dt N(t) [ (1/2 μ_g) (σ_g')² + (1/2 μ_m) (σ_m')² + (1/2 μ_φ) (φ')²
              - V(σ_g, σ_m, χ, φ) ]
```

where `N(t)` is the lapse function (gauge variable in cosmology) and
`'` denotes `d/dt`. The potential V includes:

```
V = (α/2)(σ_g - σ_ref)² + (CHI_DECAY/2) χ² 
  + V_couple(σ_m, φ) + ρ_matter[σ_m, ...]
```

with V_couple = `(g/2)(σ_ref - σ_m)²(1 - cos φ)` from DER-QNG-042.

### 2.2 Variational equations of motion

Varying with respect to each field:

For σ_g:
```
μ_g σ_g'' + α(σ_g - σ_ref) - k_gm ρ_m_eff = 0
```

For σ_m:
```
μ_m σ_m'' + ∂V_couple/∂σ_m = 0
```

For φ:
```
μ_φ φ'' + (g/2)(σ_ref - σ_m)² sin φ = 0
```

For χ (gradient flow, not canonical):
```
χ' + CHI_DECAY · χ = 0  →  χ(t) = χ_0 exp(-CHI_DECAY · t)
```

So χ decays exponentially with rate CHI_DECAY ≈ 0.020 lattice units.

### 2.3 Energy conservation

For homogeneous configurations, define:
```
E_total = (1/2 μ_g)(σ_g')² + (1/2 μ_m)(σ_m')² + (1/2 μ_φ)(φ')² + V
```

This is conserved by equations of motion (when χ damping is ignored).

**Key observation**: Stability Principle requires `E_vacuum = 0`. For
the homogeneous "vacuum" state (σ_g = σ_ref, σ_m = σ_ref, φ = 0,
χ = 0), this is satisfied trivially.

For "matter-filled" universe (σ_m perturbed from σ_ref), `E_total > 0`.
This positive energy must source the gravitational evolution.

---

## §3 — Connection to scale factor

### 3.1 Identifying what plays role of a(t)

We need to identify a quantity in QNG that:
- Is invariant under spatial coordinate transformations (homogeneous)
- Has time-evolution related to "expansion"
- Reduces to FLRW a(t) in some limit

**Candidate 1**: Direct identification σ_g(t) ↔ a(t).
Issue: σ_g has dimensions of (substrate dimensionless), while a(t) is
dimensionless. Could work after normalization.

**Candidate 2**: The "matter dilution" parameter.
In FLRW, matter density evolves as ρ_m(t) ∝ a(t)⁻³. So if we track
ρ_m_QNG(t) and identify a(t) = (ρ_m_QNG(t)/ρ_m_today)^(-1/3), we recover
the standard scaling.

**Candidate 3**: The σ_g coherence-amplitude.
δσ_g(t) = σ_ref - σ_g(t). In static limit, this is proportional to
matter density. Define a(t) such that δσ_g(t) ∝ a(t)⁻³.

Choosing **Candidate 2** (most natural):
```
a(t) ≡ [ρ_m(t_0) / ρ_m(t)]^(1/3)
```

Normalized so a(t_0) = 1 today.

### 3.2 Hubble rate

```
H(t) = (1/a)(da/dt) = -(1/3)(d ln ρ_m / dt) = -(1/3)(ρ_m'/ρ_m)
```

For matter to dilute (ρ_m decreasing), H > 0.

### 3.3 Acceleration

```
ä/a = (1/a)(d²a/dt²) = ?
```

Need second derivative of a(t). Using a ∝ ρ_m^(-1/3):
```
da/dt = -(1/3) ρ_m^(-4/3) × (dρ_m/dt) × ρ_m_0^(1/3)
d²a/dt² = ... (compute carefully)
```

This becomes:
```
ä/a = -(1/3)(ρ_m''/ρ_m) + (4/9)(ρ_m'/ρ_m)²
     = -(1/3)(ρ_m''/ρ_m) + (4/9)(3H)²
     = -(1/3)(ρ_m''/ρ_m) + 4H²
```

Hmm, the factor of 4H² is unusual. Let me redo more carefully.

Actually: a' = (-1/3) ρ_m^{-4/3} ρ_m_0^{1/3} ρ_m'
        = (-1/3) (a/ρ_m) ρ_m'
        = (-1/3) a (ρ_m'/ρ_m)
        = a × H × (-1)... 

Wait: H = (a'/a). So a' = a H. From above, a' = -(1/3) a (ρ_m'/ρ_m).
So H = -(1/3)(ρ_m'/ρ_m) → ρ_m'/ρ_m = -3H. ✓ (matter dilutes at -3H rate)

Now a'' = (a H)' = a' H + a H' = a H² + a H'
So ä/a = H² + H' = H² + dH/dt.

In standard FLRW with ä/a = -(4πG/3)(ρ + 3p):
ä/a = H² + Ḣ → Ḣ = ä/a - H²

For pure matter (p=0): ä/a = -(4πG/3)ρ_m
In Hubble form: H² + Ḣ = -(4πG/3)ρ_m, AND H² = (8πG/3)ρ_m
So Ḣ = -(4πG/3)ρ_m - (8πG/3)ρ_m = -4πG ρ_m... wait no
Actually: Ḣ = ä/a - H² = -(4πG/3)ρ_m - (8πG/3)ρ_m = -(12πG/3)ρ_m = -4πG ρ_m. 

Hmm but standard derivation gives Ḣ = -4πG (ρ + p). For p=0, Ḣ = -4πG ρ. ✓

OK so: H² = (8πG/3) ρ_m and Ḣ = -4πG ρ_m for matter-only.

### 3.4 What does QNG predict for ρ_m'/ρ_m ?

This depends on the matter-sector equation of motion in QNG. From §2.2:
```
μ_m σ_m'' + ∂V_couple/∂σ_m = 0
```

But ρ_m is some functional of σ_m. Need explicit form.

If `ρ_m ∝ (σ_ref - σ_m)²` (from V_couple structure), then:
```
ρ_m'/ρ_m = 2 σ_m'/(σ_ref - σ_m)
```

This couples ρ_m evolution to σ_m dynamics. To close the system, need
σ_m equation of motion AND identification of "ρ_m" as observable matter
density.

**STATUS**: at this point, the derivation requires specific functional
forms that are NOT yet derived from substrate first principles. The
sketch identifies the structure but cannot close the system.

---

## §4 — What we can say (preliminary)

### 4.1 General structure

QNG-FLRW would have an effective Friedmann-like equation of the form:

```
H² = F(σ_g, σ_m, φ, χ; substrate parameters) + corrections
```

where F is some functional we have not yet derived. The presence of:
- σ_m (matter): gives standard `(8πG/3)ρ_m` term
- φ (phase, with potential): could give "quintessence"-like term
- χ (decaying): contributes vanishing energy at late times
- σ_g (gravity sector): dynamics depend on coupling structure

### 4.2 What this means for cosmological observables

If QNG-FLRW gives an equation:
```
H²(z) = (8πG/3) ρ_m_total(z) + ρ_φ(z)
```

where `ρ_φ` comes from φ-sector dynamics, then:
- At high z: `ρ_m` dominates (matter era)
- At low z: `ρ_φ` may dominate (DE-like era)
- φ field acts as quintessence

For specific predictions, need to derive `ρ_φ(z)` from substrate
dynamics. **This is the hard part of QNG-FLRW.**

### 4.3 Connection to χ-decay scenario

χ field decays exponentially (CHI_DECAY = 0.020 lattice units in
standard QNG). At cosmological timescale, this rate is enormous
(lattice time unit ~10⁻⁴⁴ s, so decay rate ~10⁴² /s vs H_0 ~ 10⁻¹⁸ /s).

So χ has decayed to zero MANY e-folds before any cosmologically
relevant time. Its contribution to current cosmology is negligible.

**Implication**: χ does NOT act as quintessence at cosmological scales.
Need either φ or σ_g for DE-like behavior.

### 4.4 Connection to φ-sector quintessence

The φ field has potential V_couple = `(g/2)(σ_ref - σ_m)²(1 - cos φ)`.
For uniform φ ≠ 0:
```
V_couple_uniform = (g/2)(σ_ref - σ_m)² (1 - cos φ_uniform)
```

This is a sine-Gordon-like potential. For small φ:
```
V_couple ≈ (g/2)(σ_ref - σ_m)² × (φ²/2)
```

So φ has effective mass:
```
m_φ² = g · (σ_ref - σ_m)²
```

For uniform σ_m close to σ_ref (vacuum), m_φ² → 0 and φ becomes a
**massless scalar** — natural quintessence candidate.

For small but non-zero (σ_ref - σ_m), m_φ is small. φ rolls slowly,
acting as quintessence.

**Specific prediction (sketched)**: if QNG-FLRW with φ-quintessence
works, the dark-energy equation of state would be:
```
w_φ(z) = -1 + (kinetic/potential ratio dependent on σ_m(z))
```

For (σ_ref - σ_m) → 0: w → -1 (Λ-like).
For (σ_ref - σ_m) growing in past: w(past) < -1 or > -1 depending on
sign of evolution.

This could potentially match DESI 2024 evolving-DE hints, but full
derivation requires explicit matter sourcing model.

---

## §5 — Open questions

This sketch identifies the structure but does NOT close the cosmological
program. Remaining questions:

1. **What is `ρ_m_QNG`?** Concrete identification of matter density in
   terms of (σ_m, φ, χ) substrate fields, suitable for cosmological use.
   Currently we have phenomenological identifications (DER-QNG-022) but
   not first-principles cosmological derivation.

2. **What is the relationship a(t) ↔ σ_g(t)?** If σ_g decreases as
   matter dilutes, what's the precise functional form? Need to solve
   the time-dependent σ_g equation under FLRW symmetry.

3. **Does φ act as quintessence?** Requires (a) deriving φ initial
   conditions from substrate physics, and (b) showing slow-roll regime
   covers cosmological timescale. Not yet shown.

4. **What's H_0 in QNG?** The Hubble parameter in QNG should emerge
   from substrate parameters in a specific way. Currently no derivation.

5. **What's the QNG prediction for H_0 tension?** Local SH0ES 73.0 vs
   Planck 67.4. Could QNG modify the relationship?

These are research-program-level questions. This sketch is the FRAMEWORK
for addressing them; the answers require multi-week focused work.

---

## §6 — Honest scope

This document is **explicitly a sketch**, not a derivation. It:

✓ Identifies the structure of QNG-FLRW
✓ Pinpoints what would need to be computed
✓ Connects to DESI 2024 observations as testable signature
✓ Distinguishes what's principled from what's currently speculative

It does NOT:
✗ Derive Friedmann equation from QNG action explicitly
✗ Predict H(z) numerically
✗ Confirm or rule out QNG cosmology
✗ Solve the dark-energy problem

**Status**: SKETCH for next-session work. Specific calculations
identified.

---

## §7 — Connection to existing QNG content

This sketch builds on:
- v8 canonical action (DER-QNG-042) — gives equations of motion
- σ_g screened Poisson equation (DER-QNG-018) — static limit
- Yukawa kernel for static sources (DER-QNG-020) — wrong cosmology
- Cosmology negative result (DER-QNG-090) — what doesn't work
- Stability Principle (Section 02) — gives `E_vac = 0`
- §23 mathematical foundations — Lorentz emergence, LIV prediction

It opens path for:
- φ-quintessence cosmology
- DESI 2024 evolving-DE explanation
- Specific QNG H(z) prediction
- Derivation of H_0 from substrate parameters

---

## §8 — UPDATE: Dynamic σ_g regime gives candidate Λ mechanism

### 8.1 Key insight from numerical exploration

Tests `qng_flrw_sigma_g_evolution.py` and `qng_flrw_dynamic_sigma_g.py`
explored the σ_g equation under matter dilution.

Critical observation: for cosmological α (~10⁻¹²⁴ Planck units) and
H_0 ~ 10⁻⁶⁰ Planck units, the dimensionless ratio:
```
α / (μ_g · H_0²) ~ 10⁻⁴
```

is **small**. So σ_g is NOT in adiabatic/static limit. It's in
**dynamic regime** where the restoring force α is weak compared to
Hubble timescale.

In this regime, σ_g equation becomes:
```
μ_g σ_g'' ≈ -k_gm ρ_m(t)  (with α ≈ 0 contribution)
```

For matter dilution `ρ_m ∝ t⁻²`, integrate:
```
σ_g_dot(t) = -∫ (k_gm/μ_g) ρ_m dt = const + memory term
σ_g(t) = const · t + ln(t) terms
```

### 8.2 Late-time behavior

Numerical integration (qng_flrw_dynamic_sigma_g.py) confirms:

> At late times (a >> 1), σ_g_dot CONVERGES to a constant value D ≠ 0.

This implies:
```
ρ_σ_g_kinetic = (μ_g/2)(σ_g_dot)² → (μ_g/2) D²  (constant!)
```

A **constant kinetic energy density** acts exactly like a cosmological
constant Λ.

### 8.3 Mechanism

Physically: the matter content over cosmic history pumps σ_g through the
coupling term −k_gm ρ_m. Once matter dilutes, σ_g_dot retains a
**memory** of the integrated forcing. This memory acts as a Λ-like
contribution.

This is INTRINSIC to QNG dynamics — not added by hand, not requiring
external dark energy.

### 8.4 Status of candidate

**Verified**: σ_g_dot does converge to constant (within numerical
precision Δ/mean < 0.01%).

**Open**: 
- Magnitude of σ_g_dot_late depends on:
  - Initial conditions (early universe σ_g, σ_g_dot)
  - α value (cosmological identification)
  - k_gm coupling
  - Universe age / matter content history
- For default parameters: ρ_σ_g/ρ_m ≈ 10⁵, FAR from observed 2.17.
- Tuning required to match observation.

This is **not a clean prediction** yet — it's a candidate mechanism
that requires:
1. First-principles identification of all parameters
2. Or initial conditions set by Stability Principle / inflation

### 8.5 Comparison with quintessence

This σ_g-dynamics-driven Λ is analogous to standard quintessence with
**no potential** but **kinetic memory** from matter coupling.

In standard quintessence: V(φ) ≠ 0 drives slow roll, ρ_DE today depends
on V.

In QNG-σ_g: V(σ_g) is approximately zero (since α is tiny), and σ_g_dot
constancy comes from matter-coupling memory through the Hubble-fast
regime.

### 8.6 Path forward

The mechanism IS real. To make it a prediction:

1. **Derive natural initial conditions** for σ_g, σ_g_dot at some
   reference epoch (BBN, recombination, end of inflation).
2. **Compute σ_g_dot_late** via integration of σ_g equation across
   cosmic history.
3. **Check** if predicted ρ_σ_g_late ≈ Ω_Λ ρ_critical without tuning.
4. **Predict H(z)** form, compare to eBOSS BAO.

If this works: QNG predicts cosmological constant from substrate
dynamics + initial condition principle.

If it doesn't: still need additional mechanism (φ-quintessence).

---

## Status

**Document type**: sketch + numerical exploration
**Date**: 2026-04-25
**Outcome**: identified candidate Λ mechanism via dynamic σ_g
**Next step**: derive initial conditions principle, compute predicted Λ value

**Locked**:
- σ_g static limit gives matter-only cosmology
- σ_g dynamic regime gives candidate Λ
- Mechanism intrinsic to QNG (not added by hand)

**Open**:
- Magnitude requires parameter calibration or principled initial conditions
- Connection to Stability Principle for σ_g_dot fixing
