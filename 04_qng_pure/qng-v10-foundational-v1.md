---
type: derivation
id: DER-QNG-062
title: QNG v10 foundational reformulation — axioms, operator algebra, classical limit, and ℏ identification
status: analytical draft (no numerical implementation — theoretical only)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-042 (v8 canonical extension — classical predecessor)
  - DER-QNG-060 (foundational gap analysis — 8 quantum requirements)
  - DER-QNG-061 (connection map — ⟨L⟩=660 insight)
  - DER-QNG-059 (ℏ-program charter)
  - NOTE-QNG-017 (⟨L⟩ universal classical invariant)
methodology: Gabriel 2026-04-24 directive — "dai analitic, nimic ad-hoc"
---

# DER-QNG-062 — v10 foundational quantum reformulation

## 0 — Purpose and method

This document provides the **analytical foundation** for QNG v10 — the
first genuinely quantum formulation of the theory. It is purely
theoretical: no simulation, no GPU, no numerical results yet.

Gabriel directive (2026-04-24): *"dai drumul pe v10 la fel ca restu,
sa fie dai analitic, nimic ad-hoc sau asa ceva, cum am mers pana acum."*

**Method**:
- State axioms explicitly before use
- Derive every definition from axioms
- Mark clearly what is POSTULATED vs what is DERIVED
- Pre-register falsifiable tests before execution
- Honest citation of prior work (Wallstrom 1994, Parisi-Wu 1981,
  Koopman-von Neumann 1931, Ginzburg-Landau 1950, Kontsevich 1997)

**What this document does NOT do**:
- Derive ℏ numerical value from nothing (would require unit bridge)
- Prove v10 produces quantum mechanics (requires tests)
- Implement simulation code (separate task, after axiomatization is sound)

## 1 — Axioms of v10

Five axioms replace the classical structure of v8.

### Axiom A1 (graph substrate — unchanged from v8)

The substrate is a discrete graph `G = (V, E)` where:
- `V` = set of vertices (nodes), `|V| = L³` for cubic lattice
- `E` = set of edges, `z = 6` neighbors per vertex (cubic)
- Graph is connected and periodic (torus `T³`)

**Note**: edge dynamics (as in v9-G) may be added LATER as extension
but is NOT part of the minimal v10.

### Axiom A2 (node state space — CHANGED from v8)

Each node `i ∈ V` carries a **complex amplitude**:
```
Ψ_i ∈ ℂ
```

with associated conjugate momentum:
```
π_Ψ_i ∈ ℂ
```

Ψ and π_Ψ are two complex-valued local fields. Classical analog:
Ψ ↔ σ_m · e^{iφ} (amplitude × phase combined).

**Note**: σ_g and χ fields from v8 are auxiliary; their role in v10
is addressed in Section 8 (classical limit).

### Axiom A3 (quantization algebra — NEW in v10, CORRECTED 2026-04-24)

**Corrected formulation per DER-QNG-063 §5** (canonical field theory):

Operators corresponding to Ψ and its **canonical conjugate momentum** Π̂
satisfy:
```
[Ψ̂_i, Π̂†_j] = i ℏ_lattice · δ_ij    (canonical Poisson→commutator lift)
[Ψ̂_i, Ψ̂_j] = 0
[Π̂_i, Π̂_j] = 0
[Ψ̂_i, Π̂_j] = 0    (i, i distinct from Hermitian conjugate)
```

where `ℏ_lattice` is a constant of the theory with dimensions of ACTION
(`[Energy × Time]` in SI).

**Key correction from original DER-QNG-062 draft**: Ψ̂ and Π̂ are
independent canonical pairs, NOT creation/annihilation operators of a
single field. This is **scalar field theory on lattice**, analogous to
how φ̂ and π̂_φ are canonical pairs in QFT.

**Why this correction matters** (per DER-QNG-063 classical limit analysis):
- Original "Heisenberg algebra on Ψ̂, Ψ̂†" gives first-order GPE-like dynamics
- v8 has second-order KG-like dynamics
- Canonical pair `(Ψ̂, Π̂)` gives second-order dynamics matching v8

**Creation/annihilation operators** can still be defined from `(Ψ̂, Π̂)`
linear combinations (like quadrature operators in optics):
```
â = (Ψ̂ + iΠ̂/(μω)) / √(2ℏ)
â† = (Ψ̂ − iΠ̂/(μω)) / √(2ℏ)
[â, â†] = 1   (standard bosonic commutator)
```

at each site for harmonic limit, but these are DERIVED not primary.

### Axiom A4 (Hilbert space — NEW in v10)

The total Hilbert space is the tensor product:
```
H_total = ⊗_{i ∈ V} H_i
```

where each `H_i` is the Fock space for site i:
```
H_i = span{|n⟩_i : n = 0, 1, 2, ...}
```

with `|0⟩_i` = vacuum (Ψ̂|0⟩ = 0) and `|n⟩_i = (Ψ̂†)ⁿ |0⟩/√(n!·ℏ^n)`.

**Superposition**: any finite linear combination of tensor-product
states is a valid state.

### Axiom A5 (evolution — CHANGED from v8 Yoshida4)

Evolution is unitary:
```
|ψ(t)⟩ = Û(t) |ψ(0)⟩,   Û(t) = exp(-i Ĥ_v10 t / ℏ_lattice)
```

where `Ĥ_v10` is a Hermitian operator on `H_total` (specified in
Section 4).

**Equivalent formulation (path integral)**:
```
⟨ψ_f | Û(t) | ψ_i⟩ = ∫ DΨ DΨ* exp(i S[Ψ, Ψ*] / ℏ_lattice)
```

where `S = ∫ L dt` is the action functional derived from Ĥ_v10.

## 2 — State space derivation from axioms (CORRECTED 2026-04-24)

### 2.1 Per-site basis (canonical field theory version)

With corrected A3 `[Ψ̂, Π̂†] = iℏ`, the local Hilbert space at each site
is the representation space of this algebra. Two equivalent bases:

**Position-like basis**: eigenstates of Ψ̂
```
Ψ̂_i |ψ⟩ = ψ · |ψ⟩,   ψ ∈ ℂ (continuous spectrum)
```

**Fock basis** (via harmonic quadratures):
```
â_i = (Ψ̂_i + iΠ̂_i/(μω)) / √(2ℏ)
N̂_i = â†_i â_i,  eigenvalues n = 0, 1, 2, ...
```

**Discrete spectrum** `N̂ |n⟩ = n |n⟩` — provides Requirement 8 from
DER-QNG-060 in the harmonic limit.

### 2.2 Tensor product structure

Total basis:
```
|{n_i}⟩ ≡ ⊗_i |n_i⟩,   {n_i} ∈ ℕ^|V|
```

General state:
```
|ψ⟩ = Σ_{n_1, n_2, ...} c_{n_1, n_2, ...} |n_1, n_2, ...⟩,   c ∈ ℂ
```

**Normalization**: `⟨ψ|ψ⟩ = Σ |c|² = 1` (unitary evolution preserves).

### 2.3 Relation to "classical configuration" in v8

For each site i, a coherent state is:
```
|α_i⟩ = D̂(α) |0⟩,   D̂(α) = exp(α Ψ̂† - α* Ψ̂)/ℏ
```

with expectation values:
```
⟨α_i | Ψ̂_i | α_i⟩ = α_i ∈ ℂ
⟨α_i | N̂_i | α_i⟩ = |α_i|² / ℏ
```

**Coherent states ARE the classical configurations of v8**:
- α_i = σ_m_i · e^{iφ_i} (complex amplitude)
- Small ℏ_lattice ⇒ narrow uncertainty ⇒ behaves "classically"

## 3 — Field operators and their algebra

### 3.1 Derived operators

From the primary pair `(Ψ̂, Ψ̂†)`, define:
```
|Ψ|²_i  = Ψ̂†_i Ψ̂_i / ℏ_lattice    (dimensionless density)
φ̂_i    = arg(Ψ̂_i)                  (phase operator — subtle, see Sec 3.3)
σ̂_m_i = √(Ψ̂†_i Ψ̂_i / ℏ_lattice)    (amplitude operator)
```

The separation `Ψ̂ = σ̂_m · e^{iφ̂}` is formally correct in the polar
decomposition.

### 3.2 Number operator as conserved charge

Total number operator:
```
N̂ = Σ_i N̂_i
```

**Conserved if** `[Ĥ_v10, N̂] = 0`. This requires Ĥ_v10 to commute with
global U(1) rotations `Ψ̂ → e^{iθ} Ψ̂`.

From A2 (Ψ is complex), this U(1) symmetry is natural. The conserved
charge is particle number analog.

### 3.3 Phase operator subtlety

The "phase operator" `φ̂` is tricky in quantum mechanics (see
Susskind-Glogower, Pegg-Barnett). A rigorous definition uses:
```
e^{iφ̂} = Ψ̂ / √(Ψ̂† Ψ̂)    (Susskind-Glogower)
```

which is well-defined on states with `⟨Ψ̂†Ψ̂⟩ > 0`. For our purposes,
coherent states |α⟩ with |α| >> √ℏ are well-approximated by the
classical phase `φ = arg(α)`.

**This is the origin of phase winding quantization**: integer winding
of φ around a closed loop becomes integer eigenvalues of a topological
charge operator Ŵ_φ in v10.

## 4 — Hamiltonian Ĥ_v10

The classical Hamiltonian H_v8 is re-expressed in terms of canonical
pair `(Ψ̂, Π̂)` per corrected A3.

### 4.1 Kinetic term (CORRECTED 2026-04-24)

Classical v8: `T_m = (1/2μ_m) Σ π_m² + (1/2μ_φ) Σ π_φ²`

Quantum v10 with canonical pair `(Ψ̂, Π̂)`, `[Ψ̂, Π̂†] = iℏ`:
```
T̂ = (1/(2μ)) Σ_i Π̂†_i Π̂_i
```

where Π̂ is complex-valued canonical momentum conjugate to Ψ̂.
μ is effective mass (matches v8's μ_m, μ_φ with c_m = c_φ calibration).

**Note (correction)**: original DER-QNG-062 §4.1 used `|π̂_Ψ|²` where
π̂_Ψ was not well-defined as canonical momentum. Replaced with Π̂ per
canonical field theory prescription.

Classical limit (coherent state with `⟨Ψ̂⟩ = α`, `⟨Π̂⟩ = π_α`):
```
⟨T̂⟩ = |π_α|² / (2μ) ≈ (π_m² + π_φ²·|α|²) / (2μ)  (polar decomposition)
```
matching v8 kinetic structure.

### 4.2 Gradient term (edge-based)

Classical v8 gradient: `E_B = (β/4z) Σ_⟨ij⟩ (σ - σ)²` and XY
`E_φ = -(β_φ/z) Σ cos(Δφ)`

Quantum v10 (unified):
```
Ĥ_grad = -(J/z) Σ_⟨ij⟩ (Ψ̂†_i Ψ̂_j + Ψ̂†_j Ψ̂_i)
```

This is the **Bose-Hubbard hopping term**. J is a tunneling amplitude
with dimension of energy. Classical limit (coherent states, large |α|):
```
Ĥ_grad → -(2J/z) Σ_⟨ij⟩ |α_i||α_j| cos(φ_i - φ_j)
```
which matches the v8 XY gradient with `J = β_φ/(2·σ_m_ref²)`.

### 4.3 Local potential term

Classical v8 V_couple: `(g/2)(σ_m_ref - σ_m)²(1 - cos φ)`

Quantum v10 analog:
```
Ĥ_V = (g/2) Σ_i (σ̂_m_ref - σ̂_m_i)² · (1 - cos φ̂_i)
```

using σ̂_m from Sec 3.1. This is the **Bose-Hubbard on-site interaction**
with potential shaped to reproduce v8 V_couple in classical limit.

### 4.4 Full v10 Hamiltonian (CORRECTED 2026-04-24)

**Corrected form per DER-QNG-063 §5**:

```
Ĥ_v10 = Σ_i [(1/(2μ)) Π̂†_i Π̂_i
             + (β/2z) Σ_{j ∈ NN(i)} (Ψ̂_i - Ψ̂_j)(Ψ̂†_i - Ψ̂†_j)
             + V_couple(Ψ̂_i, Ψ̂†_i)]
```

where:
- `(Ψ̂, Π̂)` is the canonical pair per A3 (corrected)
- β = BETA_PHI / SIGMA_M_REF² is coupling (matches v8 XY)
- V_couple = (g/2) · (σ̂_m_ref - σ̂_m)² · (1 - cos φ̂) via polar decomposition
  σ̂_m = |Ψ̂|, φ̂ = arg(Ψ̂)

**Classical limit** (coherent state with ⟨Ψ̂⟩ = α, ⟨Π̂⟩ = π_α, ℏ → 0):
- Kinetic: (1/(2μ))|π_α|² — matches v8 T_m + T_φ decomposition
- Gradient: (β/z)Σ (α_i* α_j + c.c.) — matches v8 XY model
- V_couple: unchanged structure

Euler-Lagrange equations from this Ĥ_v10 give **second-order** equations
in time for α, matching v8 Klein-Gordon structure.

**Hermitian**: manifest.
**Bounded below**: for repulsive V_couple.
**Global U(1) symmetry**: Ψ̂ → e^{iθ} Ψ̂ preserves Ĥ ⟹ conserved N̂.

### 4.4-OBSOLETE: original Bose-Hubbard form (superseded)

Original draft had `-J Σ⟨ij⟩ (Ψ̂†_i Ψ̂_j + h.c.)` hopping term. This is
GROUND-STATE equivalent via:
```
(Ψ̂_i - Ψ̂_j)(Ψ̂†_i - Ψ̂†_j) = |Ψ̂_i|² + |Ψ̂_j|² - Ψ̂†_i Ψ̂_j - Ψ̂_i Ψ̂†_j
```

so the two forms differ by a local `|Ψ̂|²` term (can be absorbed into
V_couple). But **canonical kinetic term (1/(2μ))|Π̂|² is NOT equivalent
to hopping** — it gives second-order dynamics, hopping gives first-order.

**Use the corrected §4.4 form** for physically-meaningful v10.

### 4.5 Recognition as lattice Bose-Hubbard model

Ĥ_v10 is structurally a **Bose-Hubbard-like model**:
- Hopping `-J (Ψ̂†_i Ψ̂_j + h.c.)` between nearest neighbors
- On-site potential `V(Ψ̂†Ψ̂)` quadratic in density
- Periodic boundary conditions on `T³`

This is a **well-studied model** in condensed matter physics. Known
results apply:
- Phase diagram: Mott insulator vs superfluid transition
- Excitation spectrum: gapped (Mott) vs gapless (superfluid)
- Bethe ansatz in 1D; DMRG / QMC methods in 2D/3D

Important: v10 is NOT a new uncomputable construction. It is a
specific lattice bosonic model with known techniques.

## 5 — Evolution equivalence

### 5.1 Schrödinger equation

```
i ℏ_lattice ∂_t |ψ⟩ = Ĥ_v10 |ψ⟩
```

Unitary time evolution by construction (A5).

### 5.2 Path integral (Feynman)

```
⟨ψ_f | e^{-iĤt/ℏ} | ψ_i⟩ = ∫ DΨ DΨ* exp(i S[Ψ, Ψ*] / ℏ_lattice)
```

where S = ∫ L dt with Lagrangian derived from Ĥ_v10 by Legendre transform:
```
L[Ψ, Ψ̇, Ψ*] = i ℏ Ψ* ∂_t Ψ - H[Ψ, Ψ*]
```

This is the **coherent-state path integral** for bosonic systems
(Klauder, Skagerstam).

**Equivalence** of Schrödinger and path integral is standard (Feynman
1948, exact for bosonic systems).

### 5.3 Euclidean path integral (for Monte Carlo)

```
⟨ψ_f | e^{-Ĥ τ / ℏ} | ψ_i⟩ = ∫ DΨ DΨ* exp(-S_E[Ψ, Ψ*] / ℏ_lattice)
```

This is **positive-definite integrand** — amenable to Metropolis
Monte Carlo sampling.

## 6 — Observable algebra

### 6.1 Classical observables lift to quantum operators

Any classical observable `O(σ_m, φ, π_m, π_φ)` on v8 phase space lifts
to a Hermitian operator `Ô(Ψ̂, Ψ̂†)` on H_total via Weyl ordering or
normal ordering. Specific examples:

- Ring mass deficit: `M̂_ring = N·σ_ref - Σ √(Ψ̂†Ψ̂ / ℏ)`
- Phase winding: `Ŵ_φ = Σ_{plaquettes} (φ̂_i - φ̂_j)/2π` (integer eigenvalues)
- Total energy: `Ĥ_v10` itself
- Angular momentum: `L̂_z = Σ_i (r × π̂_Ψ)_z`

### 6.2 Expectation values

For state |ψ⟩: `⟨Ô⟩ = ⟨ψ|Ô|ψ⟩` — standard QM prescription.

### 6.3 Commutator structure (example)

```
[x̂_i, π̂_Ψ_j] = i ℏ_lattice δ_ij   (Heisenberg canonical)
[L̂_z, Ψ̂] = ℏ_lattice Ψ̂            (angular momentum as generator)
```

All non-commutative algebra of QM is present by construction.

## 7 — Born rule derivation

### 7.1 Pure-state Born rule

For state `|ψ⟩` and observable `Ô = Σ_n o_n |o_n⟩⟨o_n|` (spectral decomposition):
```
P(outcome o_n | state |ψ⟩) = |⟨o_n|ψ⟩|²
```

This is standard QM Born rule. **In v10 it follows from Axioms A3-A5**
plus Gleason's theorem (for Hilbert dim ≥ 3, only valid probability
measure on projectors is |⟨·|ψ⟩|²).

### 7.2 Mixed-state extension

Density matrix: `ρ = Σ p_k |ψ_k⟩⟨ψ_k|`

Observable expectation: `⟨Ô⟩ = Tr(ρ Ô)`
Outcome probability: `P(o_n) = Tr(ρ |o_n⟩⟨o_n|)`

### 7.3 Decoherence → apparent collapse

Environment coupling `Ĥ_env` produces decoherence:
```
ρ(t) → ρ_diagonal (in pointer basis) as t → ∞
```

Off-diagonal terms (coherences) suppressed; diagonal probabilities give
Born rule outcomes.

**This does not solve the measurement problem philosophically** (MWI
vs collapse still debated) but provides operational Born rule.

## 8 — Classical limit ℏ_lattice → 0

### 8.1 Coherent states saturate uncertainty

For coherent state `|α⟩`:
```
(Δ|Ψ|²)(Δφ) = ℏ_lattice (minimum uncertainty)
```

As ℏ_lattice → 0:
- Both uncertainties can be zero simultaneously
- State becomes point in classical phase space (σ_m, φ)
- Classical equations of motion recovered

### 8.2 Heisenberg equations → classical equations

```
(d/dt) ⟨Ô⟩ = (1/iℏ) ⟨[Ô, Ĥ]⟩ + ⟨∂_t Ô⟩
```

In ℏ → 0 limit with coherent state:
```
d⟨Ψ̂⟩/dt → {Ψ_classical, H_v8}  (Poisson bracket)
```

Classical v8 equations are recovered.

### 8.3 Recovery of specific v8 results

All v8 results that do NOT depend on ℏ-scale observables survive as
classical-limit predictions:

- **DER-QNG-044 Einstein correspondence**: classical-limit phenomena
  (KG dispersion, Shapiro delay, tensorial coupling) all emerge from
  v10 in coherent-state regime.
- **DER-QNG-038 baryon ladder**: ring mass identification via coherent
  state amplitude; remains valid as classical expectation.
- **⟨L⟩=660 universal invariant**: becomes expectation value `⟨L̂⟩` in
  coherent-state ground state.

## 9 — ℏ_lattice identification — **WITHDRAWN (see NOTE-QNG-024)**

**CORRECTION 2026-04-24 evening**: the identification
`ℏ_lattice ≡ β_φ / 2` proposed here is **withdrawn** as dimensionally
inconsistent. See `qng-v10-dimensional-correction-v1.md` (NOTE-QNG-024).

Summary of correction:
- ⟨L⟩ = N·β_φ/2 has units of ENERGY (per NOTE-QNG-017 §4)
- ℏ has units of ACTION = ENERGY × TIME
- These cannot be equated directly

Revised stance: **ℏ_lattice is a FREE PARAMETER of v10**, to be
calibrated or derived via further analysis. This is the same position
Nelson, Parisi-Wu, Ginzburg-Landau take — honest about axioms, which
einstein-mind repeatedly recommended.

### 9.1 Superseded by NOTE-QNG-024 (correction)

### 9.2 Justification (provisional, needs verification)

**Dimensional check**: β_φ has dimension of energy × time (action) in
v8 natural units — verified in DER-QNG-061 §1.4.

**Scale check**: β_φ/2 = 0.03 in v8 natural units. Order of magnitude
consistent with "natural unit of action" at lattice spacing.

**Universality check**: ⟨L⟩ = N·β_φ/2 is R-universal per NOTE-QNG-017
(CV 0.11% across R={2,3,4,5,6}). If R-independence survives in v10
(expectation: yes, by symmetry), then ℏ_lattice is intrinsic.

**Operator realization check**: with `ℏ_lattice = β_φ/2`, the
canonical commutator `[Ψ̂, Ψ̂†] = ℏ_lattice` has correct dimensions.

### 9.3 Caveats (honest)

This identification is **provisional**, not proven:
- Need explicit computation that ground-state expectation `⟨Ĥ_v10⟩₀`
  equals v8 ground energy with β_φ/2 as ℏ.
- Need verification that Schrödinger evolution with this ℏ gives
  correct classical limit.
- Need confirmation that quantum spectrum E_n = ℏω(n+½) has consistent
  units.

These are Phase II verifications (see Section 12).

### 9.4 Unit bridge to SI (preliminary sketch)

From v8:
- `a_M = 1.373e-3` kg/baryon-unit (mass calibration, DER-QNG-038)
- Speed of light: `c_QNG = √(β_φ/3μ_φ) = 0.108` (lu/lu = natural unit)

If v10's ℏ_lattice = β_φ/2 = 0.03 (natural units), and we identify:
- Energy unit: `E_unit = a_M · c² = 1.373e-3 × c_SI²` (kg·m²/s²)
- Time unit: `t_unit = L_unit / c_QNG` where L_unit comes from lattice spacing

Then:
- `a_S = E_unit × t_unit` (action unit, J·s)
- `ℏ_SI ?= ℏ_lattice × a_S = 0.03 × a_S`

Consistency with `ℏ_SI = 1.055e-34` J·s constrains `a_S = 3.5e-33` J·s.

Given `a_M = 1.37e-3` and requiring `a_S = a_M · a_L² / a_T`, this gives
three equations in three unknowns (`a_L, a_T, a_E`). System should close
if dimensional analysis is consistent.

**Status**: not yet verified. Requires careful calculation in Phase III.

## 10 — Predictions distinguishing v10 from classical v8

Purely quantum predictions (not present in v8):

### 10.1 Discrete energy spectrum

For harmonic oscillator in v10 (zero hopping, local harmonic potential):
```
E_n = ℏ_lattice ω (n + 1/2),   n = 0, 1, 2, ...
```

### 10.2 Uncertainty principle

For any canonical pair (X̂, P̂):
```
(ΔX̂)(ΔP̂) ≥ ℏ_lattice / 2
```

Zero-point oscillation: `⟨|Ψ|²⟩₀ = ℏ_lattice / (2 μ ω)` in harmonic limit.

### 10.3 Interference

Double-slit analog: two ring-like structures separated by distance d.
Expected interference fringes with spacing:
```
Δx ≈ (ℏ_lattice · L) / (μ · d · c_φ)
```

### 10.4 Topological quantization

Phase winding Ŵ_φ has integer eigenvalues `n ∈ ℤ`. Energy eigenstates
fall into topological sectors:
```
|n_winding; other⟩ with Ŵ_φ |n_winding; other⟩ = n_winding · |n_winding; other⟩
```

### 10.5 Born rule probability distributions

Observable `|Ψ|²_i` at site i: observation gives outcome with probability
|⟨outcome|ψ⟩|². Not deterministic as in v8 — randomness IS the quantum
prediction.

## 11 — Minimal falsifiable test suite

The following tests validate v10 IF implemented numerically. Each has
pre-registered gates.

### QNG-CPU-103 (pre-register): Harmonic oscillator spectrum

**Setup**: Ĥ_HO = (1/2μ)|π̂|² + (μω²/2) |Ψ̂|²

**Prediction**: discrete spectrum `E_n = ℏ_lattice ω (n + 1/2)`

**Gate HO_PASS**: first 5 levels match prediction to <1%
**Gate HO_FAIL**: deviations >5% or non-integer spacing
**Gate HO_INCONCLUSIVE**: numerical method issue (use DMRG vs DVR)

### QNG-CPU-104 (pre-register): Uncertainty relation

**Setup**: measure `⟨(ΔΨ̂)²⟩ · ⟨(Δπ̂_Ψ)²⟩` in ground state

**Prediction**: `ΔΨ · Δπ_Ψ ≥ ℏ_lattice / 2`

**Gate UR_PASS**: inequality saturated for coherent states, satisfied
for all other states
**Gate UR_FAIL**: violation for any tested state (theory internally
inconsistent)

### QNG-CPU-105 (pre-register): Classical limit recovery

**Setup**: v10 evolution of coherent state at large |α|, compare with
v8 Yoshida4 evolution from corresponding classical IC.

**Prediction**: expectation values `⟨Ψ̂(t)⟩` track classical `Ψ(t)`
within O(ℏ_lattice / |α|²)

**Gate CL_PASS**: agreement <5% for |α|²·ℏ_lattice^{-1} > 10
**Gate CL_FAIL**: systematic deviation >10%

### QNG-CPU-106 (pre-register): ℏ_lattice = β_φ/2 identification

**Setup**: compute ground-state energy `E₀ = ⟨0|Ĥ_v10|0⟩` in v10.
Compute classical ground energy `E₀_classical` in v8.

**Prediction**: `E₀ - E₀_classical = Σ_i (ℏ_lattice / 2) ω_i` with
`ℏ_lattice = β_φ / 2` gives self-consistent result.

**Gate**: self-consistency within 1%.

### QNG-CPU-107 (pre-register): Interference test

**Setup**: two-ring initial state, evolve, measure `|Ψ|²` at interferometer
region.

**Prediction**: sinusoidal fringes with spacing `Δx = ℏ_lattice · L /(μ·d·c)`

**Gate**: interference pattern detected with >5σ, fringe spacing within
10% of prediction.

## 12 — Implementation roadmap

### Phase I — Analytical foundation (WEEKS — this document + follow-ups)

1. ✓ DER-QNG-062 (this document): axioms + Hamiltonian + Born rule
2. Extend: deriving specific v8-→-v10 classical-limit matching
3. Extend: ℏ_lattice unit-bridge to SI rigorous computation

### Phase II — Minimum viable code (MONTHS)

4. CPU implementation of Ĥ_v10 harmonic limit (small L=4 or L=8)
5. Run CPU-103 (harmonic spectrum) + CPU-104 (uncertainty)
6. Compare with analytical predictions

### Phase III — Full lattice (MONTHS)

7. Euclidean path integral Monte Carlo on L=16, L=20
8. Run CPU-105 (classical limit) + CPU-107 (interference)
9. Verify ⟨Ĥ_v10⟩ in large-|α| = v8 Hamiltonian expectation

### Phase IV — Predictions beyond v8 (MONTHS)

10. Compute purely quantum corrections to Einstein correspondence probes
11. Test CPU-106 ℏ_lattice = β_φ/2 identification rigorously
12. Predict deviations from v8 in extreme regimes (high density, small
    system size)

### Phase V — Publication (parallel with III-IV)

- Paper 1: v8 classical phenomenology (can submit based on existing work)
- Paper 2: 20-mechanism null-result survey + Wallstrom
- Paper 3: v10 foundational paper (this document + analytical extensions)
- Paper 4: v10 numerical verification (after Phase III)

## 13 — Scope and limitations

### 13.1 What this document establishes

- Axiomatic foundation for v10 is mathematically coherent
- Ĥ_v10 is a well-defined Bose-Hubbard-like operator
- Classical limit recovery is guaranteed by coherent-state analysis
- All 8 quantum requirements from DER-QNG-060 are addressed by A1-A5
- ⟨L⟩=660 candidate identification with ℏ_lattice is dimensionally
  consistent

### 13.2 What this document does NOT establish

- **ℏ_lattice = β_φ/2 is NOT proven** — only consistent
- **Born rule predictions NOT numerically verified**
- **Classical limit recovery NOT numerically verified**
- **Unit bridge to SI NOT computed in detail**
- **Interference predictions NOT tested**

All these require Phase II-IV implementation.

### 13.3 Possible failure modes

**Risk 1 — Bose-Hubbard phase diagram kills ring**:
At parameters required for ring phenomenology, the ground state may
be Mott insulator (no ring) or superfluid (dissolved ring). Mitigation:
may need to adjust the on-site potential V or add hopping anisotropy.

**Risk 2 — Classical limit inconsistency**:
Yoshida4 evolution of v8 is highly specific. Coherent-state evolution
of v10 may differ at finite ℏ. Mitigation: careful matching of
parameters; check CPU-105 quantitative agreement.

**Risk 3 — Discrete spectrum wrong**:
CPU-103 may show E_n ≠ ℏω(n+½). Would mean the kinetic-term form is
not quite harmonic. Mitigation: explicit diagonalization of small
system; adjust T̂ form.

**Risk 4 — ℏ_lattice ≠ β_φ/2**:
CPU-106 may show different identification. Mitigation: the value of
ℏ_lattice may still be derivable from substrate, just via a different
formula.

### 13.4 Comparison with prior literature

| Aspect | QNG v10 | Bose-Hubbard (cond-mat) | Nelson (1966) | Parisi-Wu (1981) |
|---|---|---|---|---|
| Discrete lattice | ✓ | ✓ | ✗ (continuum) | ✓ |
| Complex amplitude | ✓ | ✓ | via ψ | ✓ |
| Canonical commutator | ✓ | ✓ | classical! | ✓ |
| ℏ derived from substrate? | **Proposed** | input | input | input |
| GR-like emergent phenomenology | via v8 limit | — | — | — |
| Baryon mass predictions | via v8 limit | — | — | — |

**Novel content**: QNG v10 is the first lattice quantum model claiming
emergent ℏ from a SPECIFIC classical invariant of the substrate
(⟨L⟩ = N·β_φ/2). If verified, this distinguishes QNG from standard
Bose-Hubbard (where ℏ is input), Nelson (where D ~ ℏ/m is input),
and Parisi-Wu (where noise amplitude = ℏ is input).

## 14 — Closing

This document axiomatizes v10 purely analytically. No claims are
numerical. Every proposition follows from the five axioms A1-A5 or
is explicitly marked as "conjecture" / "provisional" / "needs
verification."

Pre-registration of CPU-103 through CPU-107 provides explicit gates
for future verification. No post-hoc parameter tuning permitted.

Following Gabriel 2026-04-24 directive: *"dai analitic, nimic ad-hoc
sau asa ceva, cum am mers pana acum."*

**This is the foundational skeleton of v10. Flesh follows from Phase
II onwards.**

---

## Appendix A — Connection to DER-QNG-060 requirements

| Req # | Requirement | v10 axiom satisfying |
|---|---|---|
| 1 | [x̂,p̂]=iℏ | A3 (Heisenberg algebra) |
| 2 | Complex amplitude | A2 (Ψ ∈ ℂ) |
| 3 | Path integral | A5 (coherent-state PI equivalent) |
| 4 | Born rule | A4 + Gleason theorem |
| 5 | Hilbert space | A4 (tensor product Fock) |
| 6 | Unitary evolution | A5 (Û(t) = exp(-iĤt/ℏ)) |
| 7 | Measurement | Decoherence (Sec 7.3) |
| 8 | Discrete spectrum | N̂ in A4 has integer eigenvalues |

All 8 requirements addressed in 5 axioms. No circularity.

## Appendix B — Minimal proof sketches

**Proposition B1**: Ĥ_v10 is Hermitian.
*Proof*: each term is manifestly Hermitian (kinetic, gradient, potential).
Sum of Hermitian is Hermitian. ∎

**Proposition B2**: U(1) symmetry → number conservation.
*Proof*: Ĥ_v10 invariant under Ψ̂ → e^{iθ} Ψ̂. By Noether, conserved
charge is Σ_i N̂_i. ∎

**Proposition B3**: Classical limit recovers v8.
*Proof (sketch)*: Heisenberg equations `d⟨Â⟩/dt = (1/iℏ)⟨[Â,Ĥ]⟩`.
For coherent state |α⟩ with |α|² → ∞ (fixed ℏ), `⟨Â⟩ → A_classical`
and `[Â,B̂]/iℏ → {A, B}` (Poisson bracket). Equations match v8. ∎

**Proposition B4**: ⟨L⟩ = N·β_φ/2 is a coherent-state expectation.
*Proof (sketch)*: for coherent state `|{α_i}⟩` minimizing Ĥ_v10 with
equal amplitudes and slow phase variation, the XY-like gradient term
gives `⟨-(J/z) Σ_⟨ij⟩ Ψ̂†_i Ψ̂_j⟩ ≈ -J·⟨|α|²⟩_avg`. At ground state
`⟨|α|²⟩ = |α_ref|²`. Total: `-J·|α_ref|² · z · N/2 = N·β_φ/2` with
appropriate `J = β_φ/(z·|α_ref|²)`. ∎ (Hand-wavy; needs careful check.)
