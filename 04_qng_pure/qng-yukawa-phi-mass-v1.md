# QNG v8: Yukawa phi-mass coupling — structural form (DER-QNG-041)

Type: `derivation`
ID: `DER-QNG-041`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-18`

---

## Inputs

- [qng-v8-canonical-extension-v1.md](qng-v8-canonical-extension-v1.md) — DER-QNG-042 (v8 canonical framework)
- [qng-sigma-m-potential-v1.md](qng-sigma-m-potential-v1.md) — DER-QNG-040 (V(sigma_m) GL term)
- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036 (v7 Hamiltonian)
- [qng-gap8-stability-analysis-v1.md](qng-gap8-stability-analysis-v1.md) — DER-QNG-034 (Gap 8 stability)

---

## Objective

After the quintuple-FAIL chain (GPU-009..018) diagnosed the IR halo as a
phi Goldstone mode, the only remaining structural direction is explicit
breaking of the global U(1) shift `phi → phi + c`. Formalize the minimal
such breaking compatible with v7 and propose its falsification test.

The coupling FORM is the subject of this derivation. The coupling
strength `g` is a pre-registered EFT parameter (Gap 9), honestly labeled.
GPU-019 tests whether the FORM produces the predicted structural changes;
it does NOT claim to derive `g` from v7 primitives.

## 1. Goldstone diagnosis (structural fact, 2026-04-18)

Every term in the v5+H / v7 phi channel is invariant under the global
shift `phi_i → phi_i + c`:

- Relational smoothing: `phi_i - phi_j` is shift-invariant
- Channel E: `ε · chi_i` is phi-independent
- Channel F: `|Z_i|` = modulus of phi-sum, shift-invariant
- V(σ_m) (DER-QNG-040): decouples from phi entirely

Goldstone's theorem therefore forces a gapless phi mode, whose long-range
correlations produce the observed power-law halo
`dis(r) · σ_m ~ r^(-α)` with α ≈ 2.4 at L=80 (R² = 0.998).

**No σ_m-only modification can cure this.** GPU-018 confirmed the
prediction: V(σ_m) at λ=0.19 leaves α=2.49 unchanged. The halo is a
phi mode; a cure must act on phi directly.

## 2. Minimal shift-symmetry breaking

### 2.1 Candidate form

Add to E_v7:

```
V_couple = g · σ_g · (1 - cos phi)
```

- Preserves `phi → phi + 2π` (lattice phi periodicity)
- Breaks `phi → phi + c` for generic c (explicit; the cosine is not
  invariant under arbitrary shifts, though it respects the 2π periodicity)
- Carrier is σ_g (gravitational sigma), NOT σ_m. Rationale below.

### 2.2 Linearized phi mass

Expanding around the vacuum `phi = 0`:

```
1 - cos phi ≈ (phi²)/2 - (phi⁴)/24 + ...
```

The leading quadratic term gives an effective phi mass-squared:

```
m²_phi = g · σ_g
```

In the bulk where `σ_g ≈ σ_g_ref = 0.5`:

```
m²_phi_bulk = 0.5 · g
```

Healing length (phi screening length) `lambda_phi = 1/sqrt(g · σ_g_ref)`
controls exponential decay of phi disorder:

```
<sin²(Δphi/2)>(r) ~ exp(-r/lambda_phi) / r    (far-field)
```

Replacing the power-law halo.

### 2.3 Ring formation preserved

σ_g is a *uniform condensate* in v7 (it equals σ_ref everywhere except
where chi back-reaction perturbs it via K_GM). σ_g does NOT collapse to
zero inside rings — rings are σ_m-sector objects. Therefore m²_phi is
approximately R-independent and does not interfere with Channel F
depletion of σ_m at the ring core.

This is the key structural distinction from σ_m-carrier variants:
σ_g-coupling gaps phi universally without position-dependent frustration
of ring formation.

## 3. Why σ_g is the right carrier (Tesla + Einstein consensus)

Three structural considerations, all pointing the same way:

### 3.1 Condensate vs soliton (Tesla)

In the QCD-GMOR analog `m_π² ∝ m_q · ⟨q̄q⟩`, the carrier is the *vacuum
condensate* ⟨q̄q⟩, which is spatially uniform. In QNG:

- σ_g ≈ σ_g_ref uniformly → genuine condensate → well-defined bulk
  phi mass
- σ_m depletes inside rings → soliton-like profile → position-dependent
  phi mass → frustrated Channel F

### 3.2 Channel F non-interference

At σ_m-coupling: phi mass dips to zero inside rings (σ_m → 0), but this
is exactly where Channel F creates the depletion. The coupling would
frustrate the ring formation mechanism.

At σ_g-coupling: phi mass is bulk-uniform; rings form unimpeded; only
the halo structure is modified.

### 3.3 Occam / minimal-interference principle

σ_g-coupling introduces ONE new physics (phi mass) without touching
the existing sigma_m / Channel F subsystem. σ_m-coupling would introduce
one new physics AND modify two existing mechanisms (ring formation,
Goldstone). The former is cleaner.

## 4. The g parameter — Gap 9 EFT labeling

**Tesla derivation** (breathing-mode match):
```
g_Tesla = β_φ / (R_min² · σ_g_ref²)
```
With β_φ = 0.02 (BETA_PHI_RING, from CPU-043), R_min = 3 (empirical CPU-043..045),
σ_g_ref = 0.5:
```
g_Tesla ≈ 0.0089
```

**Einstein derivation** (topological matching λ_φ = R_min):
```
g_Einstein = 1 / (R_min² · σ_g_ref) = 1 / (9 · 0.5) ≈ 0.22
```

**Savant critique of both**:

- Tesla's dimensional analysis carries `σ_g_ref^(-2)` (inverse condensate²),
  but `m²_φ = g · σ_g` implies `g` should carry `σ_g_ref^(-1)`, not
  `σ_g_ref^(-2)`. Tesla's expression is dimensionally inconsistent with
  the proposed Lagrangian.
- Einstein's `R_min = 3` is an EMPIRICAL observation from CPU-043..045,
  not a v7 primitive. Using it as derivation input is circular because
  adding phi mass will itself shift R_min (heavier phi tightens ring
  core). Self-referential.

Neither derivation survives falsification-rigor scrutiny. **g is labeled
Gap 9: EFT coupling, to be committed before GPU-019 as a log-spaced
5-point scan.** The FORM is structural; the VALUE is phenomenological.

## 5. Modification to E_v7

The v7 potential energy becomes:

```
E_v8 = E_v7 + Σ_i V_couple(σ_g_i, phi_i)
     = E_v7 + g · Σ_i σ_g_i · (1 - cos phi_i)
```

### 5.1 Update channels

The gradient-flow for each field:

**phi channel:**
```
Δphi_i ⊃ -η_phi · ∂V_couple/∂phi_i = -η_phi · g · σ_g_i · sin phi_i
```
Add to existing `Δrel_phi + Channel E + Channel F`.

**σ_g channel:**
```
Δσ_g_i ⊃ -η_sigma · ∂V_couple/∂σ_g_i = -η_sigma · g · (1 - cos phi_i)
```
Add to existing `Δrel_σ_g + σ_g Channel G + ...`.

Where η_phi and η_sigma are the existing channel learning rates (no new
parameters beyond `g`).

### 5.2 Stability constraint

The new phi Hessian diagonal element is `g · σ_g_ref` (at phi = 0).
Stability under the synchronous update requires:

```
η_phi · g · σ_g_ref < 1
```

With η_phi = 1.0 and σ_g_ref = 0.5: `g < 2`. Well within the scan window
[0.009, 0.6]. No stability issue from V_couple.

## 6. Falsification gates (Savant's 5-commit contract)

Full pre-registration: `07_validation/prereg/QNG-GPU-019.md`.

### 6.1 Gate A — halo exponential gap

At L=80, R=5, after PHASE2=1500: fit `dis(r)·σ_m` on r ∈ [3, 37] to:
```
Model 1: A · r^(-α)                        (power-law)
Model 2: A · exp(-r/λ_φ) / r                (Yukawa)
```

**PASS** requires: AIC(Model 2) - AIC(Model 1) < -6 AND α_effective > 3.5
(where α_effective is the Model 1 fit's exponent — above the v5+H baseline
band [2.4, 3.0]).

**FAIL** if α_effective ≤ 3.0 (indistinguishable from Goldstone) OR
Model 1 preferred by AIC.

### 6.2 Gate C — Yukawa self-consistency

Measure λ_φ independently from:
- (C1) Halo shape at single ring (Gate A Model 2 fit)
- (C2) Inter-ring force F(d) between two W+W- rings fit to
  `A · exp(-d/λ_F) / d²` over d ∈ [6, 20]

**PASS** requires: `|λ_φ - λ_F| / λ_φ < 0.20` (Savant's 20% tolerance,
accounting for force-fit noise).

**FAIL** if they disagree by more than 20% — would indicate phi is
quasi-Goldstone with localized halo but non-Yukawa force tail.

### 6.3 Gate E — mass ratio L-convergence

Measure M(R=5) / M(R=4) at L ∈ {60, 80, 100}. Define:
```
spread = |ratio(L=100) - ratio(L=60)| / ratio(L=80)
```

**PASS** requires: `spread < 0.03` AND `ratio(L=100)` within 10% of
target 1.313 (= 1232/938, the delta/nucleon SM ratio).

**FAIL** if ratio diverges with L (like V(σ_m) did, collapsing toward 1)
OR converges outside [1.18, 1.45].

### 6.4 Gate selection rule (Savant's "lowest-g-passing")

Run all five g values in {0.009, 0.03, 0.08, 0.22, 0.6}. Accept the
**lowest g** at which Gate A passes AND Gate C passes AND Gate E passes.
If no g satisfies all three, GPU-019 FAILS. No post-hoc widening of
ranges; no choosing g by fitting secondary metrics.

## 7. Decision rule for GPU-019

- **PASS_H1** at some g*: Gates A, C, E all pass at lowest passing g.
  DER-QNG-041 form confirmed. g* locked as current-best EFT value; Gap 9
  open as "find v8 primitive that derives g*".
- **PARTIAL_H2**: Gate A passes at some g but Gate C or E fails.
  Form correct but incomplete; possibly need Anderson-Higgs
  `|σ_m ∇phi|²` augmentation (see DER-QNG-042 candidate note). Re-reg
  as GPU-019B.
- **FAIL_H3**: Gate A fails at all g. Yukawa form structurally wrong.
  Advance to DER-QNG-042 (Anderson-Higgs) as the Savant-proposed
  alternative.
- **VOID**: stability or ring-formation breaks at all tested g. Revise
  stage ranges.

## 8. Fallback structure: DER-QNG-042 (reserved ID)

If DER-QNG-041 fails Gate A at all g, the next candidate is:

```
V_AH = kappa_AH · σ_m · |∇phi|²      (Anderson-Higgs / covariant derivative)
```

This preserves the global U(1) shift (|∇phi|² is gradient, not phi
itself), but uses σ_m to locally absorb the Goldstone — the Anderson-Higgs
mechanism in condensed-matter form. phi remains massless in the vacuum
but the halo is suppressed *dynamically* by coupling to σ_m gradients.

NOT implemented in this derivation. Reserved as DER-QNG-042 if needed.

## 9. Relation to DER-QNG-034, DER-QNG-036, DER-QNG-040

- **DER-QNG-034** (marginal stability for σ_g): UNCHANGED. σ_g-V_couple
  adds a phi-dependent term but does not shift σ_g's own stability
  criterion (the new Hessian element is cross-coupling, not σ_g
  diagonal).
- **DER-QNG-036** (H_v7 Hamiltonian): EXTENDED. E_v8 = E_v7 + ΣV_couple;
  all channels remain gradient flow of the new E_v8.
- **DER-QNG-040** (V(σ_m)): SUPERSEDED by structural diagnosis. V(σ_m)
  commutes with phi-shift and was therefore incapable of curing halo.
  Falsified 2026-04-18.

## 10. Honest statement of limits

This derivation does NOT:

- Derive `g` from v7 primitives (Gap 9, acknowledged)
- Explain WHY phi has the particular periodicity 2π (AX-QNG level question)
- Address Lorentz covariance (NOTE-QNG-013 remains open)
- Close Gap 5 (α ↔ Λ identification; Einstein speculates connection
  but no derivation)

It DOES provide:

- A structurally minimal phi-mass mechanism consistent with v7 stability
- A committed FORM that fails falsifiably at any g if wrong
- An honest EFT labeling of `g` with pre-registered scan
- A next-candidate fallback (DER-QNG-042) if form fails

---

## Summary

Adding `V_couple = g · σ_g · (1 - cos phi)` to E_v7 is the minimal
explicit breaking of the phi U(1) shift symmetry compatible with ring
formation. The coupling strength `g` is labeled Gap 9 (EFT) and
pre-registered as a 5-point log-spaced scan [0.009, 0.6]. GPU-019
tests whether the FORM produces a Yukawa halo, self-consistent inter-ring
force, and L-converged mass ratio. PASS would lock the form; FAIL would
redirect to DER-QNG-042 (Anderson-Higgs covariant derivative coupling).

Status: `candidate` pending QNG-GPU-019.
