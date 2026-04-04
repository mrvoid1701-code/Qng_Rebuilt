# QNG Generation Order v1

Type: `derivation`
ID: `DER-QNG-014`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Show that the v2 update law (`DER-QNG-010`) does not implement any generation order between the three node-state components `(σ, χ, φ)`. State the minimal cross-coupling that creates the hierarchy `σ → χ`, and derive its consequence for the effective matter sector: under the new coupling, Assumption M.1 of `DER-QNG-013` (a declared bridge) becomes a derived result in the static limit.

## Inputs

- [qng-primitives-v1.md](qng-primitives-v1.md)
- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-emergent-field-v1.md](qng-emergent-field-v1.md)
- [qng-ceff-field-equation-v1.md](qng-ceff-field-equation-v1.md)
- [qng-matter-source-identification-v1.md](qng-matter-source-identification-v1.md)

## Scope

Operates at the ontic layer (node update law) and the effective-field layer (continuum limit). Does not import observational data or phenomenological fits. The proposed cross-coupling term is declared as a candidate extension to the update law and must be versioned separately before numerical implementation.

---

## Section 1: The v2 Law Has Decoupled Components

### 1.1 Linear fixed-point analysis

From `DER-QNG-010`, the deterministic, no-history update (`η = 0`, `γ = 0`) is:

```
N_i(t+1) = Proj[ N_i(t) - α·(N_i(t) - N_ref) + β·(N̄_i(t) - N_i(t)) ]
```

with `N_ref = (σ_ref, 0, 0)`. Writing the chi component explicitly:

```
χ_i(t+1) = Proj_chi[ (1 - α - β)·χ_i(t) + β·χ̄_i(t) ]
```

This equation contains **only** `χ_i(t)` and `χ̄_i(t)`. No term couples it to `σ_i(t)`.

The sigma component equation is analogously:

```
σ_i(t+1) = Proj_sigma[ (1 - α - β)·σ_i(t) + β·σ̄_i(t) + α·σ_ref ]
```

This contains **only** `σ_i(t)` and `σ̄_i(t)`. No term couples it to `χ_i(t)`.

**At leading order, `σ` and `χ` are dynamically decoupled.** The two components evolve as two separate consensus processes on the same graph, with independent reference values.

### 1.2 Fixed-point under decoupled dynamics

For a homogeneous initial condition `χ_i(0) = 0` for all `i`: `χ̄_i = 0`, so `χ_i(t+1) = 0` for all `t`. **Chi cannot be generated from a zero baseline by the v2 law, regardless of how far sigma departs from its reference.**

### 1.3 History channel does not resolve the decoupling

The history channel (`γ > 0`) introduces `M_i` and `D_i`, which are computed from the norm across all three components. This creates an **indirect** coupling: sigma deviation drives `M_i`, and `M_i` gates the history correction for all components including chi.

However, the history-channel chi correction is:

```
[Δ_hist]_chi = γ·M_i·(1 - D_i)·(χ̄_i - χ_i^hist)
             = γ·M_i·(1 - D_i)·(χ̄_i - (1 - M_i)·χ_i)
```

when `chi_ref = 0`. If `χ_i = χ̄_i = 0` everywhere, this term is identically zero regardless of `M_i`. **The indirect coupling through memory cannot generate chi from sigma deviations starting from a uniform chi = 0 baseline.**

### 1.4 Consequence for the matter sector

`DER-QNG-013` defines:

```
M_eff(i) = sigmoid(a_M·L_eff(i)·(1 - C_eff(i)) + a_D·D_i(t) + a_P·|sin(P_i(t))|) - 1/2
```

where `L_eff` is the coarse-grained chi field. Because `L_eff` is decoupled from `C_eff` at linear order, the identification `ρ_eff = ρ₀·M_eff/Δu³` cannot be derived from the sigma dynamics alone. It must be postulated — this is Assumption M.1 (declared bridge). The decoupling is exactly why that assumption cannot be promoted to a derivation under the v2 law.

---

## Section 2: The Generation Order Requirement

### 2.1 Statement

A native **generation order** `σ → χ` is present if and only if there exists a term in the chi channel of the update law that depends on `σ_i(t)` (or equivalently on `σ_ref - σ_i(t)`, the local coherence deficit).

The physical motivation is internal to the node ontology:

- `σ_i` measures local compatibility or coherence of the substrate element with its reference configuration
- `χ_i` measures local load or tension in the substrate element
- When coherence drops below reference (`σ_i < σ_ref`), the substrate element is strained; tension should accumulate
- When coherence exceeds reference (`σ_i > σ_ref`), the substrate element is over-stabilized; tension should release

This is the minimal coupling consistent with the interpretation of `χ` as a response to coherence strain. It requires no external input and introduces no phenomenological quantity.

### 2.2 Minimal cross-coupling

The minimal term satisfying the generation order requirement is:

```
Δ_cross(i, t) = (0,  δ·(σ_ref - σ_i(t)),  0)
```

where:

- `δ ∈ [0, 1)` is the cross-coupling strength (one new free parameter)
- Only the chi component is affected
- The sign is fixed: coherence deficit (`σ_ref - σ > 0`) generates positive tension (`χ` increases); coherence surplus generates negative tension

**Parameter interpretation:** `δ` encodes how strongly a coherence departure at a node drives tension at that same node. It is purely local — no neighbor information is required. Setting `δ = 0` recovers the v2 law exactly.

### 2.3 Contractiveness check

The complete update law with the cross-coupling retains its contractiveness property. The chi component before `Proj` becomes:

```
χ_i(t+1)_pre = (1 - α - β)·χ_i(t) + β·χ̄_i(t) + δ·(σ_ref - σ_i(t))  [+ history term]
```

The additional term `δ·(σ_ref - σ_i)` is bounded: `σ_i ∈ [0,1]`, `σ_ref ∈ (0,1)`, so `|δ·(σ_ref - σ_i)| ≤ δ`. The contractiveness condition from `DER-QNG-010` is modified to require `α + β + δ < 1` (sufficient condition, not necessary). Since `δ < 1` is declared above, this is satisfiable with existing parameter choices.

---

## Section 3: Static-Limit Consequence for the Effective Fields

### 3.1 Static fixed-point equation for chi with cross-coupling

In the static limit (`∂_t = 0`), with full relational coupling but no noise or history (to isolate the leading-order effect), the chi fixed-point equation is:

```
0 = -α·χ_i* + β·(χ̄_i* - χ_i*) + δ·(σ_ref - σ_i*)
```

Rearranging:

```
(α + β)·χ_i* = β·χ̄_i* + δ·(σ_ref - σ_i*)
```

### 3.2 Continuum limit

Applying the same coarse-graining and continuum limit as in `DER-QNG-012` (Section 2), replacing `χ_i* → L_eff(x)` and `σ_i* → C_eff(x)`:

```
(α + β)·L_eff = (β·Δu²/z)·∇²L_eff + δ·(C_ref - C_eff)
```

Or in terms of the coherence deviation `δ_C = C_eff - C_ref`:

```
D_diff₀·∇²L_eff - α·L_eff = δ·δ_C
```

where `D_diff₀ = β·Δu²/(z·t_s)` from `DER-QNG-012`.

### 3.3 Leading-order solution in the weak-field regime

In the weak-field regime (`|δ_C| ≪ C_ref`, i.e., `ε₃ → 0`), the right-hand side is a small source. The homogeneous solution decays on the screening scale `λ_screen`. For `r ≪ λ_screen` (Newtonian regime, well below screening):

```
L_eff(x) ≈ (δ/α) · (C_ref - C_eff(x)) = -(δ/α) · δ_C(x)
```

**Leading-order result:** In the Newtonian regime, the load field is proportional to the negative coherence deviation:

```
L_eff = -(δ/α) · δ_C + O(δ²/α², ε₃)
```

---

## Section 4: Consequence for M_eff — Assumption M.1 Becomes Derivable

### 4.1 Substitution into the M_eff formula

From `DER-QNG-013`, the centered M_eff formula is:

```
M_eff(i) = sigmoid(a_M·L_eff·(1 - C_eff) + a_D·D_i + a_P·|sin(P_i)|) - 1/2
```

Substituting `L_eff ≈ -(δ/α)·δ_C` and noting that in the reference state `D_i ≈ 0`, `P_i ≈ 0` (low-memory limit, `ε₄ → 0`):

```
M_eff(i) ≈ sigmoid(-a_M·(δ/α)·δ_C·(1 - C_eff)) - 1/2
```

In the weak-field limit (`C_eff ≈ C_ref`, `1 - C_eff ≈ 1 - C_ref ≡ const`):

```
M_eff(i) ≈ sigmoid(-κ·δ_C) - 1/2
```

where `κ = a_M·(δ/α)·(1 - C_ref)` is a positive constant composed entirely of substrate parameters.

For small `|δ_C|` (linear response), `sigmoid(-κ·δ_C) - 1/2 ≈ -(κ/4)·δ_C`:

```
M_eff(i) ≈ -κ_eff · δ_C(i)
```

where `κ_eff = κ/4 = a_M·(δ/α)·(1 - C_ref)/4`.

### 4.2 Effective density — derived form

The effective density from `DER-QNG-013`:

```
ρ_eff(i) = ρ₀ · M_eff(i) / Δu³ ≈ -ρ₀ · κ_eff · δ_C(i) / Δu³
```

Since `Φ_QNG = -(a·a_sigma/2D_diff₀)·δ_C` (Convention GRAV-C1, `DER-QNG-012`):

```
δ_C = -(2D_diff₀/(a·a_sigma)) · Φ_QNG
```

Substituting:

```
ρ_eff(i) = ρ₀·κ_eff·(2D_diff₀) / (Δu³·a·a_sigma) · Φ_QNG(i)
```

### 4.3 Status of Assumption M.1

**Before the generation order coupling (`δ = 0`):**
`L_eff` is independent of `C_eff` at linear order. The identification `ρ_eff = f(M_eff)` requires a declared bridge — Assumption M.1 cannot be derived.

**After the generation order coupling (`δ > 0`):**
In the Newtonian limit (static, weak-field, low-memory), `L_eff` is determined by `δ_C` through the cross-coupling. The matter proxy `M_eff` reduces to a linear function of `δ_C`. The identification `ρ_eff ∝ δ_C ∝ Φ_QNG` follows from substrate dynamics alone.

**Assumption M.1 is upgraded from a declared bridge to a derived result** in the simultaneous limit `ε₁, ε₂, ε₃, ε₄ → 0` with the generation-order coupling active.

---

## Section 5: Impact on the Newtonian Limit Program

The addition of the cross-coupling `δ` modifies the status of the open gaps in `DER-QNG-011`:

| Gap | Status before | Status after |
|-----|---------------|--------------|
| Gap 3 (matter identification) | Declared bridge (M.1) | Derived in Newtonian limit |
| Gap 4 (numerical G_QNG) | Blocked by Gap 3 | Now computable once Gap 2 resolved |
| Step N5 | Declared | Derivable |
| Step N6 | Ready pending DER-QNG-013 | Fully derivable |

The G_QNG formula from `DER-QNG-012` is unchanged:

```
G_QNG = (a·a_sigma·β·Δu²) / (2π·z·t_s)
```

The matter normalization constant `ρ₀` now carries the additional relation:

```
ρ₀·κ_eff·(2D_diff₀) / (Δu³·a·a_sigma) = 1 / (4π·G_QNG)
```

This provides one constraint equation on `(ρ₀, δ, a_M, C_ref)`. Combined with the CODATA constraint (Step N7), the free parameter count is reduced.

---

## Section 6: What This Document Does Not Do

1. It does not modify the v2 update law. The cross-coupling is a **candidate extension**, to be written as `qng-native-update-law-v3.md` after this document is reviewed.
2. It does not verify the contractiveness inequality numerically.
3. It does not analyze the `δ ≠ 0` correction to the history channel update (a subleading effect at order `ε₄`).
4. It does not establish whether `δ` is independently constrained by the QM-facing ladder or the Lorentzian signature proxy — those couplings are open.
5. The correction `L_eff ≈ -(δ/α)·δ_C` is leading order only. The subleading term involves the gradient structure `∇²L_eff` and contributes at order `(Δu/λ_screen)²` — negligible in the Newtonian regime but relevant for galaxy-scale phenomenology.

---

## Section 7: Open Questions Raised

1. **Is `δ` independently bounded?** The cross-coupling strength must satisfy `δ < 1 - α - β` (sufficient contractiveness). Does the requirement that the QM-facing ladder recovers correctly impose a further bound?

2. **Does the generation order extend to `φ`?** The present document establishes `σ → χ` only. Whether `χ → φ` (phase coherence generated by load tension) is a further extension, and whether it affects the QM-facing closure, is open.

3. **Screening scale vs. galaxy scale:** The leading-order result breaks down at `r ~ λ_screen = Δu·sqrt(β/(z·α))`. If `λ_screen` is of galactic order, the subleading terms in `L_eff` become relevant for rotation curve phenomenology — possibly the first QNG-specific departure from classical Newtonian gravity.

4. **History correction to `δ`:** With `γ > 0`, the cross-coupling generates chi, which accumulates memory `M_i`, which then feeds back through the history channel. The leading correction to `G_QNG(full)` includes a term proportional to `δ·γ/(α·β)`. Sign and magnitude are not yet computed.

---

## Cross-references

- Native update law v2: `DER-QNG-010` (`qng-native-update-law-v2.md`)
- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
- Matter source identification: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
- Newtonian limit program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- Effective field layer: `DER-QNG-005` (`qng-emergent-field-v1.md`)
