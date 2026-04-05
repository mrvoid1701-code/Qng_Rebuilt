# QNG C_eff Field Equation v1

Type: `derivation`
ID: `DER-QNG-012`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Derive the leading-order closed partial differential equation governing `C_eff(x, t)` from the coarse-grained native update law v2 (`DER-QNG-010`). This is Step N2 of the Newtonian limit derivation program (`DER-QNG-011`).

## Inputs

- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-emergent-field-v1.md](qng-emergent-field-v1.md)
- [qng-geometry-estimator-v1.md](qng-geometry-estimator-v1.md)
- [qng-newtonian-limit-program-v1.md](qng-newtonian-limit-program-v1.md)

## Scope

This document operates at the effective-field layer (Level 3 of the ontological backbone). All results are leading order in the continuum limit `ε₁ → 0` and quasi-static limit `ε₂ → 0`. The weak-field and low-memory approximations (`ε₃`, `ε₄`) are applied in subsequent steps.

---

## Section 1: Starting Point — Discrete Update Law

From `DER-QNG-010`, the full deterministic update (`η = 0`) is:

```
N_i(t+1) = Proj[ N_i(t)
                 - α·(N_i(t) - N_ref)
                 + β·(N̄_i(t) - N_i(t))
                 + γ·M_i(t)·(1 - D_i(t))·(N̄_i(t) - N_i^hist(t)) ]
```

The effective coherence field `C_eff(i)` is defined at the effective-field layer (`qng-emergent-field-v1.md`) as the coarse-grained sigma component:

```
C_eff(i, t) = <sigma_i(t)>_coarse
```

where the average is taken over nodes within a coarse-graining cell of linear size `ℓ ≫ Δu`.

The neighborhood mean of the sigma component is:

```
σ̄_i(t) = (1/k_i) · Σ_{j ∈ Adj(i)} σ_j(t)
```

---

## Section 2: Coarse-Graining the Sigma Channel

### Step 2.1 — Isolate the sigma component

From the full update law, the sigma component before `Proj` is:

```
σ_i(t+1)_pre = σ_i(t)
               - α·(σ_i(t) - σ_ref)
               + β·(σ̄_i(t) - σ_i(t))
               + γ·M_i(t)·(1 - D_i(t))·(σ̄_i(t) - σ_i^hist(t))
```

where `σ_i^hist(t) = M_i(t)·σ_ref + (1 - M_i(t))·σ_i(t)`.

### Step 2.2 — Low-memory approximation (ε₄ → 0)

In the low-memory limit `ε₄ = γ/β ≪ 1`, the history correction channel is treated as a small perturbation. At leading order in ε₄, the history channel contributes a correction to the effective equation at order ε₄. Retaining only the leading-order terms:

```
σ_i(t+1)_pre ≈ (1 - α - β)·σ_i(t) + β·σ̄_i(t) + α·σ_ref  [+ O(ε₄)]
```

### Step 2.3 — Rearrange as an increment

Define `δσ_i(t) = σ_i(t+1) - σ_i(t)` (treating `Proj` as approximately identity in the weak-field, σ near interior regime):

```
δσ_i(t) ≈ -α·(σ_i(t) - σ_ref) + β·(σ̄_i(t) - σ_i(t))
```

### Step 2.4 — Identify the discrete Laplacian

For a regular graph with coordination number `z` and node spacing `Δu`, the discrete second-difference is:

```
(σ̄_i - σ_i) = (1/z) · Σ_{j ∈ Adj(i)} (σ_j - σ_i)
             = (Δu²/z) · [∇²_discrete σ](i)  +  O(Δu⁴)
```

where `∇²_discrete` converges to the continuum Laplacian as `Δu → 0` on a sufficiently isotropic graph (Gap 1 of DER-QNG-011 — isotropy assumed under Assumption D2; see `AX-QNG-004` in `qng-graph-isotropy-assumption-v1.md`).

### Step 2.5 — Continuum limit (ε₁ → 0)

Replacing the discrete increment `δσ_i / t_s` by a time derivative, and `σ_i → C_eff(x, t)`:

```
∂_t C_eff = -α/t_s · (C_eff - σ_ref) + (β·Δu²)/(z·t_s) · ∇²C_eff
```

where `t_s` is the native substrate timestep.

---

## Section 3: Matter Source Term

In the presence of a local matter source, the coherence field is depleted by the matter sector. From the effective-field layer (`qng-emergent-field-v1.md`), the source channel enters as an additive term `S_src(x, t)` at the effective-field level:

```
∂_t C_eff = -α/t_s · (C_eff - σ_ref) + (β·Δu²)/(z·t_s) · ∇²C_eff - S_src(x, t)
```

where `S_src ≥ 0` represents local depletion of coherence by concentrated matter (positive = source depletes coherence). The sign convention is fixed: matter reduces `C_eff` locally.

---

## Section 4: Leading-Order C_eff Field Equation

### Primary result

Define the substrate constants:

```
Γ₀ = α / t_s                      [relaxation rate, dimension: 1/time]
D_diff₀ = β·Δu² / (z·t_s)         [diffusion coefficient, dimension: length²/time]
```

The leading-order C_eff field equation is:

```
∂_t C_eff = -Γ₀·(C_eff - C_ref) + D_diff₀·∇²C_eff - S_src
```

where `C_ref ≡ σ_ref` is the substrate reference coherence.

This is a **reaction-diffusion equation** with:
- A linear relaxation term (restoring force toward `C_ref`) controlled by `Γ₀`
- A Laplacian diffusion term controlled by `D_diff₀`
- A matter source term `S_src`

### Classification

The equation is a **screened diffusion / reaction-diffusion PDE** of the type:

```
∂_t u = D·∇²u - Γ·u + f(x, t)
```

with `u = C_eff - C_ref` and `f = -S_src`. It is parabolic in space-time.

---

## Section 5: Quasi-Static Reduction (ε₂ → 0)

In the quasi-static limit, time derivatives of `C_eff` are negligible compared to spatial relaxation. Setting `∂_t C_eff = 0`:

```
D_diff₀·∇²δ_C - Γ₀·δ_C = S_src
```

where `δ_C = C_eff - C_ref` is the coherence deviation from reference.

This is a **screened Poisson equation** (Yukawa/Helmholtz type). Its solutions have Yukawa form:

```
δ_C(r) ~ -S₀ / (4π·D_diff₀·r) · exp(-r / λ_screen)
```

where the screening length is:

```
λ_screen = sqrt(D_diff₀ / Γ₀) = Δu · sqrt(β / (z·α))
```

The screening length is a pure ratio of substrate parameters.

### Poisson limit (Γ₀ → 0, α → 0)

When self-relaxation is negligible compared to diffusion on the scales of interest (`r ≪ λ_screen`):

```
D_diff₀·∇²δ_C = S_src
```

i.e., a **pure Poisson equation** for the coherence deviation.

---

## Section 6: Connection to the Gravitational Potential

### 6.1 Biharmonic obstruction

The geometry estimator (`qng-geometry-estimator-v1.md`) defines:

```
h_00(i) = -a · ∇²_discrete C_eff(i)     [lapse perturbation]
```

and the gravitational potential proxy:

```
Ψ_QNG(i) = h_00(i) / 2 = -(a/2) · ∇²C_eff(i)
```

Applying `∇²` to obtain the Poisson equation for `Ψ_QNG`:

```
∇²Ψ_QNG = -(a/2) · ∇⁴C_eff
```

From the quasi-static Poisson equation for `δ_C`:

```
∇²δ_C = S_src / D_diff₀
```

This gives:

```
∇²Ψ_QNG = -(a/2D_diff₀) · ∇²S_src
```

This is a **biharmonic (∇⁴) obstruction**: the Poisson equation for `Ψ_QNG` involves `∇²S_src`, not `S_src` directly. A spatially uniform source `S_src = const` would give `∇²Ψ_QNG = 0` — incorrect.

### 6.2 Resolution: Potential proxy redefinition

**Convention GRAV-C1:** Define the gravitational potential proxy directly from the coherence deviation:

```
Φ_C(x) = -(a · a_sigma / 2D_diff₀) · δ_C(x)
        = -(a · a_sigma / 2D_diff₀) · (C_eff(x) - C_ref)
```

where `a_sigma` is the coherence weighting coefficient from the geometry estimator.

The quasi-static Poisson equation for `δ_C` then gives directly:

```
∇²Φ_C = -(a·a_sigma / 2D_diff₀) · ∇²δ_C = -(a·a_sigma / 2D_diff₀) · S_src / D_diff₀
```

Setting `S_src = -4π·D_diff₀²·ρ_eff / (a·a_sigma)` (sign: matter depletes coherence), one obtains:

```
∇²Φ_C = 4π·G_QNG·ρ_eff
```

with:

```
G_QNG = a·a_sigma·D_diff₀ / (2π)
       = a·a_sigma·β·Δu² / (2π·z·t_s)
```

**This is the leading-order expression for Newton's constant in QNG substrate parameters.**

### 6.3 Consequence for the geometry estimator

The biharmonic obstruction means the original proxy `Ψ_QNG = h_00/2 = -(a/2)∇²C_eff` is NOT the correct Newtonian potential. The correct proxy is `Φ_C ∝ δ_C = C_eff - C_ref`. The geometry estimator convention must be revised at Step N4: this is a structural finding of this derivation, not a free choice.

---

## Section 7: Approximation Validity

| Approximation | Condition | Physical meaning |
|---|---|---|
| Continuum (ε₁) | `Δu ≪ L_phys` | Graph is dense relative to scales of interest |
| Quasi-static (ε₂) | `v_source ≪ c_substrate` | Sources evolve slowly |
| Weak-field (ε₃) | `|δ_C/C_ref| ≪ 1` | Coherence deviation is small |
| Low-memory (ε₄) | `γ/β ≪ 1` | History correction is subleading |
| Poisson regime | `r ≪ λ_screen` | Observation scale below screening length |

The screened Poisson equation is valid for all `Γ₀`. The pure Poisson equation holds for `r ≪ λ_screen = Δu·sqrt(β/(z·α))`.

---

## Section 8: G_QNG — Summary Formula

```
G_QNG = (a·a_sigma·β·Δu²) / (2π·z·t_s)
```

| Symbol | Origin | Domain |
|---|---|---|
| `a` | Geometry estimator coefficient | > 0 |
| `a_sigma` | Coherence weighting in geometry estimator | > 0 |
| `β` | Relational coupling strength (DER-QNG-010) | (0, 1) |
| `Δu` | Node spacing in continuum limit | > 0 |
| `z` | Mean node degree | Integer ≥ 2 |
| `t_s` | Native substrate timestep | > 0 |

G_QNG has dimension `[length²/time]` in substrate units. To match the SI CODATA value, the substrate length and time units must be fixed relative to meters and seconds — this is the constraint equation from Step N7 of the derivation program.

**History correction (subleading):**

At order `ε₄ = γ/β`:

```
G_QNG(full) = G_QNG(0) · (1 + α_hist·ε₄ + O(ε₄²))
```

where `α_hist` is determined by the structure of `U_hist`. Its sign — whether memory strengthens or weakens effective gravity — is a prediction, not a free parameter.

---

## Section 9: Open Issues

| # | Issue | Impact |
|---|---|---|
| I1 | Graph isotropy (Gap 1 of DER-QNG-011): derivation assumes isotropic `∇²` | Blocks rigorous 3D claim |
| I2 | Geometry estimator convention must be updated to use `Φ_C`, not `Ψ_QNG` | Blocks Step N4 assembly |
| I3 | `F_matter` — precise form of matter source mapping `S_src → ρ_eff` | Blocks Step N5 (see DER-QNG-013) |
| I4 | `ρ₀` — substrate has no intrinsic mass scale; requires CODATA constraint | Blocks Step N7 |
| I5 | History correction sign `α_hist` — not computed yet | Subleading, non-blocking |
| I6 | Validity of `Proj ≈ identity` in the weak-field regime | Implicit assumption in Step 2.3 |

---

## Cross-references

- Native update law v2: `DER-QNG-010` (`qng-native-update-law-v2.md`)
- Newtonian limit program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- Matter source identification: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
- Geometry estimator: `DER-QNG-002` (`qng-geometry-estimator-v1.md`)
- Effective field layer: `DER-QNG-005` (`qng-emergent-field-v1.md`)
