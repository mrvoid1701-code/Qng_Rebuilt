# QNG Poisson Equation Assembly v1

Type: `derivation`
ID: `DER-QNG-018`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Execute Step N6 of the Newtonian limit derivation sequence (`DER-QNG-011`): assemble
the full Poisson equation ∇²Φ_QNG = 4π·G_QNG·ρ_eff from its parts, resolve the
S_src sign/prefactor inconsistency in `DER-QNG-012`, and derive the internal
consistency identity `G_QNG = α·λ²_screen` which relates Newton's constant to the
gravitational screening length.

## Inputs

- [qng-ceff-field-equation-v1.md](qng-ceff-field-equation-v1.md)
- [qng-matter-source-identification-v1.md](qng-matter-source-identification-v1.md)
- [qng-generation-order-v1.md](qng-generation-order-v1.md)
- [qng-newtonian-limit-program-v1.md](qng-newtonian-limit-program-v1.md)

## Scope

Effective-field layer and Newtonian limit. Substrate units throughout (Δu=1, t_s=1).
Sets `a·a_sigma = 2π` as the geometry estimator normalization convention.

---

## Section 1: Conventions and Unit Setup

**Substrate units:** Δu = 1, t_s = 1.

**Geometry normalization:** `a·a_sigma = 2π` (convention GRAV-C2, set here).

**Derived substrate constants** (from DER-QNG-012):
```
D_diff₀ = β·Δu²/(z·t_s) = β/z          [diffusion coefficient]
Γ₀      = α/t_s         = α             [relaxation rate]
λ_screen = √(D_diff₀/Γ₀) = √(β/(z·α))  [screening length]
```

**Gravitational potential proxy** (convention GRAV-C1 from DER-QNG-013, sign fixed):
```
Φ_QNG(i) = -(a·a_sigma / 2D_diff₀) · δ_C(i) = -(πz/β) · δ_C(i)
```

where `δ_C(i) = σ_i - σ_ref < 0` near matter. Therefore `Φ_QNG > 0` near matter.

**Newtonian sign convention:** The attractive gravitational potential satisfies `Φ_Newton < 0`
near mass. Define:
```
Φ_Newton(i) = -Φ_QNG(i) = (πz/β) · δ_C(i) < 0  near matter
```

The Poisson equation in the conventional form ∇²Φ_Newton = 4πGρ requires ∇²Φ_Newton > 0
at a source (where ρ > 0). We verify:
```
∇²Φ_Newton(i) = (πz/β) · ∇²δ_C(i)
```
Near a source: ∇²δ_C > 0 (the coherence dip has positive Laplacian at its minimum).
So ∇²Φ_Newton > 0 at source ✓ — consistent with Newtonian sign convention.

---

## Section 2: S_src Correction (DER-QNG-012 Inconsistency)

**Bug in DER-QNG-012 §6.2:** The formula
```
S_src = -4π·D_diff₀²·ρ_eff / (a·a_sigma)    [DER-QNG-012 §6.2, incorrect]
```
is inconsistent with the G_QNG formula `G_QNG = a·a_sigma·D_diff₀/(2π)` stated in
the same document.

**Derivation of the correct S_src:**

From the quasi-static Poisson equation (DER-QNG-012 §5, with Γ₀→0):
```
D_diff₀ · ∇²δ_C = S_src
```

From the Poisson equation requirement:
```
∇²Φ_Newton = (πz/β) · ∇²δ_C = (πz/β) · S_src / D_diff₀
            = (πz²/β²) · S_src          [using D_diff₀ = β/z in substrate units]
```

Setting ∇²Φ_Newton = 4π·G_QNG·ρ_eff = 4π·(β/z)·ρ₀·M_eff:
```
(πz²/β²) · S_src = 4π · (β/z) · ρ₀ · M_eff
S_src = 4 · (β/z)³ · ρ₀ · M_eff
```

**Correct S_src formula (replacing DER-QNG-012 §6.2):**
```
S_src = 4 · D_diff₀³ · ρ₀ · M_eff
```

In substrate units with ρ₀ = 1:
```
S_src = 4 · (β/z)³ · M_eff
```

**Verification:** Substitute back:
```
∇²Φ_Newton = (πz²/β²) · 4·(β/z)³·M_eff = 4π·(β/z)·M_eff = 4π·G_QNG·M_eff ✓
```

---

## Section 3: Assembled Poisson Equation

**Complete Poisson equation (Step N6 closure):**

```
∇²Φ_Newton(x) = 4π · G_QNG · ρ_eff(x)
```

with:

| Quantity | Formula | Units |
|----------|---------|-------|
| `Φ_Newton` | `(πz/β) · δ_C = (πz/β)·(σ_i - σ_ref)` | dimensionless |
| `G_QNG` | `β/(z·t_s·Δu⁻²) = β/z` (substrate) | `[Δu²/t_s]` |
| `ρ_eff` | `ρ₀·M_eff/Δu³` | `[ρ₀]` |
| `M_eff` | `sigmoid(a_M·L_eff·(1-C_eff)+a_D·D_i+a_P·|sin(P_i)|) - 1/2` | dimensionless |
| `λ_screen` | `Δu·√(β/(z·α))` | `[Δu]` |

**Screened Poisson (complete, including relaxation term):**
```
∇²Φ_Newton - (1/λ²_screen) · Φ_Newton = 4π · G_QNG · ρ_eff / D_diff₀
```

In the pure Poisson limit (`r ≪ λ_screen`, or equivalently `α → 0`): the screening
term drops and the standard Poisson equation holds.

---

## Section 4: Internal Consistency Identity

Combining G_QNG and λ_screen from the same substrate parameters:

```
G_QNG · (1/λ²_screen) = (β/z) · (z·α/β) = α
```

Therefore:

**Identity N6.1:**
```
G_QNG = α · λ²_screen
```

**Physical meaning:** Newton's constant and the gravitational screening length are not
independent parameters — they are both determined by the same substrate constants
(β, z, α) and satisfy this exact algebraic identity. A measurement of either G_QNG
or λ_screen immediately fixes the other, given α.

**Consequence:** In any regime where gravity is Newtonian, the screening length is:
```
λ_screen = √(G_QNG / α)
```

For G_QNG to give the measured SI Newton's constant (Step N7, DER-QNG-019), α must
be correspondingly small in physical units:
```
α = G_SI · (t_s/Δu²) / (t_s · c²_substrate) [in physical units]
```

The screening length in physical units is then of order:
```
λ_screen_SI = Δu · √(β/(z·α)) = Δu · √(G_SI · t_s · z / (Δu² · β))
```

For λ_screen_SI to be consistent with astrophysical constraints (screening of gravity
must not alter solar system dynamics), λ_screen must be either sub-Planck (no
observable effect) or cosmological (gravitational bound states well within λ).
This constraint is stated in DER-QNG-019.

---

## Section 5: Testable Predictions for QNG-CPU-035

From Identity N6.1, the following are numerically testable on the quasi-static
equilibrium simulation:

**P35.1 — G_QNG = α·λ²_screen across multiple β values:**
Run simulations at β ∈ {0.20, 0.35, 0.50} (fixed z=2, α=0.005). At each β:
- Measure λ_fit from exponential fit to the σ profile
- Compute G_QNG = β/z from formula
- Check: α·λ_fit² / G_QNG ≈ 1 within 10%

**P35.2 — Linear scaling G_QNG ∝ β:**
G_QNG(β₂)/G_QNG(β₁) = β₂/β₁ (algebraic identity, numerically exact)

**P35.3 — Quadratic scaling λ²_screen ∝ β/α:**
λ_screen(β₂)²/λ_screen(β₁)² = β₂/β₁ (measurable from profile fits)

---

## Section 6: Status

| Step | Status after this document |
|------|--------------------------|
| N1 (graph isotropy) | Open — assumed under D2 |
| N2 (C_eff field equation) | Complete — DER-QNG-012 |
| N3 (quasi-static reduction) | Complete — DER-QNG-012 §5 |
| N4 (weak-field linearization) | Complete — DER-QNG-012 §6 (with corrected Φ_Newton) |
| N5 (source identification) | Complete — DER-QNG-013 + DER-QNG-014 |
| **N6 (Poisson assembly)** | **Complete** — this document |
| N7 (CODATA + unit mapping) | See DER-QNG-019 |

**The Newtonian limit derivation sequence is complete through N6.**

---

## Cross-references

- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
- Matter source: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
- Generation order: `DER-QNG-014` (`qng-generation-order-v1.md`)
- Newtonian program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- CODATA constraint: `DER-QNG-019` (`qng-codata-constraint-v1.md`)
- Test: `QNG-CPU-035`
