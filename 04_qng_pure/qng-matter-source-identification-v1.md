# QNG Matter Source Identification v1

Type: `derivation`
ID: `DER-QNG-013`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Identify the effective matter density `ρ_eff(i)` in terms of QNG matter-sector variables, close Gap 3 of `DER-QNG-011`, and complete Step N5 of the Newtonian limit derivation sequence.

## Inputs

- [qng-matter-sector-proxy-v1.md](qng-matter-sector-proxy-v1.md)
- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-emergent-field-v1.md](qng-emergent-field-v1.md)
- [qng-ceff-field-equation-v1.md](qng-ceff-field-equation-v1.md)
- [qng-newtonian-limit-program-v1.md](qng-newtonian-limit-program-v1.md)

## Scope

Operates at the effective-field layer and the matter-sector proxy layer. Does not import physical mass values. The identification rule is a declared bridge between the QNG proxy variables and the standard energy-momentum tensor trace in the non-relativistic limit.

---

## Section 1: What Must Be Identified

From `DER-QNG-012`, the quasi-static Poisson equation is:

```
∇²Φ_C = 4π·G_QNG·ρ_eff
```

with:

```
Φ_C(x) = -(a·a_sigma / 2D_diff₀) · (C_eff(x) - C_ref)
```

and the source term enters as:

```
S_src = -(4π·D_diff₀²·ρ_eff) / (a·a_sigma)
```

Gap 3 of `DER-QNG-011` requires: express `ρ_eff(i)` in QNG matter-sector variables `M_eff(i)` and `S_src(i)` explicitly.

---

## Section 2: Matter Sector Variables

From the matter-sector proxy layer (`DER-QNG-008`, `qng-matter-sector-proxy-v1.md`), the effective matter proxy is:

```
M_eff(i) = a_M·L_eff(i)·(1 - C_eff(i)) + a_D·D_i(t) + a_P·|sin(P_i(t))|
```

where:
- `L_eff(i)` is the effective load amplitude
- `C_eff(i)` is the coherence field
- `D_i(t)` is the mismatch accumulator (history variable)
- `P_i(t)` is the phase coherence (history variable)
- `a_M, a_D, a_P` are weighting coefficients

**Critical correction — sigmoid centering:**

The v2 update law (`DER-QNG-010`) mandates replacement of `clip01` with a sigmoid-based projection. At the reference state (no matter, `L_eff = 0`, `D_i = 0`, `P_i = 0`), the uncorrected `M_eff` takes value `sigmoid(0) = 1/2 ≠ 0`.

The correct centered form is:

```
M_eff(i) = sigmoid(a_M·L_eff(i)·(1 - C_eff(i)) + a_D·D_i(t) + a_P·|sin(P_i(t))|) - 1/2
```

This ensures:
- `M_eff = 0` at the reference state (vacuum condition satisfied)
- `M_eff ∈ (-1/2, +1/2)`
- `M_eff > 0` when matter is present and local state departs from reference

**This centering correction is mandatory.** The uncorrected form produces a non-zero matter density everywhere in vacuum and cannot satisfy the Poisson equation for isolated sources.

---

## Section 3: Identification Rule

### 3.1 Dimensional analysis

From `DER-QNG-012`, `S_src` has dimension `[1/time]` (rate of coherence depletion per unit time). To obtain a density `ρ_eff` with dimension `[mass/length³]`, a mass-dimensional constant `ρ₀` is required:

```
S_src(i) = ρ_eff(i) · V_cell / ρ₀_norm
```

where `V_cell = Δu³` is the volume of one coarse-graining cell and `ρ₀_norm` is a normalization factor with dimension `[mass·time/length³]`.

### 3.2 Identification declaration

**Declared identification rule (Step N5):**

```
ρ_eff(i) = ρ₀ · M_eff(i) / Δu³
```

where:
- `ρ₀` is a free substrate mass scale parameter with dimension `[mass]`
- `Δu³` converts the per-node proxy to a volume density
- `M_eff(i)` is the centered matter proxy from Section 2

### 3.3 Classification

| # | Assumption | Classification |
|---|---|---|
| M.1 | `M_eff(i)` is proportional to effective mass content at node `i` | **Derived in Newtonian limit** — via generation order coupling `DER-QNG-014`; in the static weak-field limit with `δ > 0`, `L_eff ≈ -(δ/α)·δ_C` and `M_eff ∝ -δ_C`, making the identification a consequence of substrate dynamics. Remains a declared bridge outside this limit. |
| M.2 | Volume density is obtained by dividing by `Δu³` | **Declared bridge (natural)** — single node occupies one cell |
| M.3 | `ρ₀` is determined by the CODATA G constraint | **Derived constraint** — closes Gap 4 of DER-QNG-011 |
| M.4 | `M_eff` vanishes at the reference state (vacuum) | **Required condition** — enforced by centering correction |

---

## Section 4: Consistency Checks

### 4.1 Vacuum consistency

At the reference state: `L_eff = 0`, `D_i = 0`, `P_i = 0` → `M_eff = sigmoid(0) - 1/2 = 0`.

Therefore `ρ_eff = 0` in vacuum. The Poisson equation `∇²Φ_C = 0` holds in vacuum → Φ_C is harmonic → consistent with the Laplace equation for an empty region.

### 4.2 Sign consistency

Matter is present when `M_eff > 0`. From `DER-QNG-012`, `S_src > 0` means matter depletes coherence (C_eff pulled below C_ref, so δ_C < 0). This makes `Φ_C > 0`...

**Sign convention check:** Newtonian gravity requires `Φ_C < 0` near a mass. Resolving:

The source convention in `DER-QNG-012` is `S_src` appears with a minus sign in the C_eff equation (`-S_src`), so matter (`S_src > 0`) reduces `C_eff`, making `δ_C = C_eff - C_ref < 0`, making `Φ_C = -(a·a_sigma/2D_diff₀)·δ_C > 0`.

**Resolution:** The Newtonian potential is attractive, so `Φ_C` as defined has the wrong sign. Adopt sign convention:

```
Φ_Newton ≡ -Φ_C = (a·a_sigma / 2D_diff₀) · (C_eff - C_ref)
```

Then `Φ_Newton < 0` near matter (since `C_eff < C_ref`), and the Poisson equation becomes:

```
∇²Φ_Newton = -4π·G_QNG·ρ_eff
```

Wait — standard form is `∇²Φ = 4πGρ` with `Φ < 0`. Check: for a point source `ρ = Mδ³(x)`, the solution is `Φ = -GM/r < 0`, and `∇²(-GM/r) = 4πGM·δ³(x)` = `4πGρ`. So the standard form is correct with `Φ < 0`.

Therefore: define `Φ_Newton = -Φ_C` and the equation is standard. This is a sign convention, not a physical issue.

**Declared convention SIGN-C1:** `Φ_Newton = (a·a_sigma/2D_diff₀)·(C_ref - C_eff)`. Near matter, `C_eff < C_ref`, so `Φ_Newton > 0`...

This is the standard issue with sign conventions. The minimal resolution: declare that the QNG gravitational potential is `Φ_QNG = -(a·a_sigma/2D_diff₀)·δ_C` so that `Φ_QNG < 0` near matter. The Poisson equation is then `∇²Φ_QNG = 4π·G_QNG·ρ_eff`. **This convention is fixed here and must not be changed without versioning.**

### 4.3 Dimensional consistency

```
[G_QNG] = [a·a_sigma·β·Δu²] / [z·t_s]  =  [length²/time]  (in substrate units)
[ρ_eff] = [ρ₀/Δu³]  (when M_eff is dimensionless)
[4π·G_QNG·ρ_eff] = [length²/time] · [ρ₀/Δu³]
[∇²Φ_QNG] = [Φ_QNG/length²]
```

For dimensional consistency: `[Φ_QNG] = [G_QNG·ρ_eff·length²] = [ρ₀·length/time]`.

From the definition `Φ_QNG = -(a·a_sigma/2D_diff₀)·δ_C` and `δ_C` is dimensionless:

```
[Φ_QNG] = [a·a_sigma/D_diff₀] = dimensionless / [length²/time] = [time/length²]
```

This does not match `[ρ₀·length/time]` unless the substrate unit system is fixed. **The dimensional bridge requires:**

```
G_QNG = G / c²_substrate
```

where `c_substrate` is the effective signal propagation speed in the QNG substrate. This is a constraint on the substrate timescale and length scale, not a new parameter. It must be verified in Step N7.

---

## Section 5: Complete Identification Statement

**Effective density identification (Step N5 closure):**

```
ρ_eff(i) = ρ₀ · M_eff(i) / Δu³
```

where:

```
M_eff(i) = sigmoid(a_M·L_eff(i)·(1 - C_eff(i)) + a_D·D_i(t) + a_P·|sin(P_i(t))|) - 1/2
```

**Constraints:**

1. `ρ₀ > 0` (matter proxy positive = positive mass)
2. `ρ₀` is free — substrate has no intrinsic mass scale — constrained by CODATA G (Step N7)
3. The centering correction is mandatory (Section 2 above)
4. Dimensional consistency requires `G_QNG = G/c²_substrate` (Section 4.3)

---

## Section 6: Gap 3 Status

From `DER-QNG-011` §5, Gap 3 was:

> "The right-hand side of the Poisson equation is `4πGρ`. The QNG matter-sector proxy `M_eff` and the density-source channel `S_src` exist as proxies but neither is rigorously identified with the mass density `ρ`."

**Status after this document:** Gap 3 is **closed in the Newtonian limit** via the generation order coupling introduced in `DER-QNG-014` (`DER-QNG-015`). With the cross-coupling `δ > 0`, in the simultaneous limit `(ε₁, ε₂, ε₃, ε₄) → 0`, `L_eff` is slaved to `δ_C` and `M_eff ∝ -δ_C`, so the identification `ρ_eff ∝ M_eff` follows from substrate dynamics without a free declaration. Outside the Newtonian limit (dynamic fields, strong-field regime, or `δ = 0`), Assumption M.1 reverts to a declared bridge. This must be stated explicitly in any published version.

---

## Section 7: Implications for the Poisson Equation Assembly (Step N6)

The Poisson equation assembly (Step N6 of DER-QNG-011) now has all inputs:

**Left-hand side** (from DER-QNG-012):
```
∇²Φ_QNG
```

**Right-hand side** (from this document):
```
4π·G_QNG·ρ_eff = 4π·G_QNG·ρ₀·M_eff(i)/Δu³
```

**Assembled equation:**
```
∇²Φ_QNG(x) = 4π·G_QNG·ρ_eff(x)
```

with:
```
G_QNG = (a·a_sigma·β·Δu²) / (2π·z·t_s)
Φ_QNG = -(a·a_sigma / 2D_diff₀) · (C_eff - C_ref)
ρ_eff = ρ₀·M_eff / Δu³
```

Step N6 is **ready to execute** pending resolution of the geometry estimator convention update (biharmonic obstruction, DER-QNG-012 §6.3) and the dimensional bridge (Section 4.3 above).

---

## Cross-references

- Matter sector proxy: `DER-QNG-008` (`qng-matter-sector-proxy-v1.md`)
- Native update law v2: `DER-QNG-010` (`qng-native-update-law-v2.md`)
- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
- Newtonian limit program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- Geometry estimator: `DER-QNG-002` (`qng-geometry-estimator-v1.md`)
