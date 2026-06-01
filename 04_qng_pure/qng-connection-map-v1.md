---
type: derivation
id: DER-QNG-061
title: QNG connection map — explicit topology of nodes, edges, constants and their interconnections; gap visualization
status: foundational visualization (Gabriel 2026-04-24 directive)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-060 (foundational analysis — 8 quantum requirements)
  - DER-QNG-059 (ℏ-program charter)
  - DER-QNG-042 (v8 canonical extension)
  - DER-QNG-044 (Einstein correspondence)
purpose:
  - Visualize ALL connections between nodes, edges, constants
  - Mark explicitly which connections exist, which are missing
  - Show where v10 needs new structure
---

# DER-QNG-061 — QNG connection map

## Purpose (Gabriel 2026-04-24)

> *"Vreau sa vedem conexiunile cu dintre noduri muchii si asa mai
> departe, constantele ca sa putem vedea conexiunile lipsa, gen muchia
> cutare se conecteaza la constanta cutare prin intermediul cutare,
> nodurile se conecteaza prin asa... ca sa si observam imaginar."*

This document maps **every** connection in QNG explicitly:
- which node-state connects to which other via which channel
- which channel uses which constant
- which constant determines which derived quantity
- where the connections END (gaps that v10 must fill)

## Section 1 — Atomic inventory

### 1.1 Per-node primitives (v8)

```
Node i ∈ V(G):
  ┌──────────────────────────────────────────────┐
  │  σ_g_i  ∈ [0, 1]    (gravitational charge)   │
  │  σ_m_i  ∈ [0, 1]    (matter charge)          │ ←┐ canonical pair
  │  π_m_i  ∈ ℝ         (conjugate momentum)     │ ←┘
  │  φ_i    ∈ [-π, π]   (phase, real-valued)     │ ←┐ canonical pair
  │  π_φ_i  ∈ ℝ         (conjugate momentum)     │ ←┘
  │  χ_i    ∈ [-1, 1]   (auxiliary, dissipative) │  no conjugate
  └──────────────────────────────────────────────┘
```

**Note**: σ_g and χ have NO conjugate momentum. They are auxiliary fields
in v8, not full canonical degrees of freedom.

### 1.2 Edge structure

```
Lattice: cubic L³, z=6 neighbors per node
Edge e = (i, j) with j ∈ NN(i), |NN(i)| = 6

NN(i) = {i±x̂, i±ŷ, i±ẑ}    (with periodic boundary conditions)
```

Edges carry **NO state** in v8 — they are pure adjacency markers.
This is one of the key gaps (see Section 6).

### 1.3 Global constants (v8)

| Symbol | Value | Role |
|---|---|---|
| BETA_G | 0.35 | σ_g gradient stiffness |
| BETA_M | 0.35 | σ_m gradient stiffness |
| BETA_PHI | 0.06 | φ gradient stiffness (XY) |
| ALPHA | 0.005 | restoration to σ_ref |
| MU_M | 10.0 | σ_m effective mass |
| MU_PHI | 0.857 | φ effective mass |
| K_BACK | 0.10 | χ → σ_g feedback strength |
| K_GM | 0.01 | σ_m → σ_g coupling (Channel A) |
| CHI_DECAY | 0.020 | γ damping of χ |
| CHI_REL | 0.35 | χ source from σ_g Laplacian |
| DELTA_CHI | 0.20 | χ source from σ_g deviation |
| GAMMA_PHI | 0.001 | Channel F dissipation |
| g (V_couple) | 0.22 | Yukawa φ-mass coupling |
| SIGMA_M_REF | 0.5 | σ_m vacuum value |
| SIGMA_G_REF | 0.5 | σ_g vacuum value |

### 1.4 Derived constants (computed from above)

| Symbol | Formula | Value | Role |
|---|---|---|---|
| c_φ² | BETA_PHI / (3·μ_φ) | 0.0117 | wave speed squared (KG dispersion) |
| ω_orbit | 2π / T_cycle | 0.0346 | orbital frequency for R=4 |
| ⟨L⟩_universal | N · BETA_PHI / 2 | 660 | XY ground state invariant |
| G_QNG | β_g / z | 0.058 | Newtonian gravitational analog |
| λ_screen | sqrt(α / β_g · z) | ≈ 12.6 | Yukawa screening length |
| a_M | 1.373e-3 | mass calibration baryon |
| λ_max | +0.00150 | Lyapunov for R1 attractor |

## Section 2 — Channels: state-to-state interactions

Each channel is a way one state-variable evolves due to others. Format:
```
Channel X: target ← source via constant
```

### 2.1 Channel A (sm ↔ sg coupling)

```
                K_GM
   σ_m  ────────────────►  σ_g
   σ_g  ────────────────►  σ_m  (back-reaction in v7-symmetric)

  ┌───────────────────────────────────────────────────────┐
  │  dσ_g_i  +=  -K_GM · (σ_m_ref − σ_m_i)                │
  │  dσ_m_i  +=  +K_GM · (σ_g_i − σ_g_ref)   (v7-sym)     │
  └───────────────────────────────────────────────────────┘
```

**Constants involved**: K_GM, σ_m_ref, σ_g_ref
**Connection**: σ_m deficit at ring → σ_g deviation locally → gravitational potential

### 2.2 Channel B (gradient stiffness)

```
                BETA_G          BETA_M          BETA_PHI
   σ_g  ◄──────────────►  σ_g    σ_m ────►  σ_m   φ ──►  φ

  ┌────────────────────────────────────────────────────────┐
  │  E_B_g = (BETA_G/4z) · Σ_⟨ij⟩ (σ_g_i − σ_g_j)²        │
  │  E_B_m = (BETA_M/4z) · Σ_⟨ij⟩ (σ_m_i − σ_m_j)²        │
  │  E_φ   = -(β_DER/z) · Σ_⟨ij⟩ σ_m_i σ_m_j cos(φ_i-φ_j) │
  │       (or pure XY in R1: -(β_R1/z) Σ cos(φ_i-φ_j))    │
  └────────────────────────────────────────────────────────┘
```

**Constants involved**: BETA_G, BETA_M, BETA_PHI, MU_PHI
**Edge usage**: explicit nearest-neighbor sum over edges

### 2.3 Channel D (χ ← σ_g)

```
              CHI_REL · (σ_g_bar − σ_g)              -CHI_DECAY · χ
   σ_g  ─────────────────────────────►  χ  ◄──────────────────────
              DELTA_CHI · (σ_g_ref − σ_g)
   σ_g  ─────────────────────────────►  χ

  ┌────────────────────────────────────────────────────────┐
  │  dχ_i  +=  -CHI_DECAY · χ_i                            │
  │             + CHI_REL · (σ̄_g_i − σ_g_i)                │
  │             + DELTA_CHI · (σ_g_ref − σ_g_i)            │
  └────────────────────────────────────────────────────────┘
```

**Constants involved**: CHI_DECAY, CHI_REL, DELTA_CHI, σ_g_ref
**Critical observation**: σ̄_g is the neighbor mean — uses edges implicitly

### 2.4 Channel F (φ-disorder dissipation)

```
                GAMMA_PHI · disorder · σ_m
   φ  ───────────────────────────────►  σ_m  (depletion)

  ┌────────────────────────────────────────────────────────┐
  │  dσ_m_i  +=  GAMMA_PHI · disorder_i · σ_m_i            │
  │  where disorder_i = (1 - |Z_i|), Z_i = exp(iφ_i) bar   │
  └────────────────────────────────────────────────────────┘
```

**Constants involved**: GAMMA_PHI
**Note**: makes σ_m depleted where phase is incoherent → ring topology

### 2.5 Channel G (χ → σ_g feedback)

```
                K_BACK · χ
   χ  ──────────────────────────────►  σ_g

  ┌────────────────────────────────────────────────────────┐
  │  dσ_g_i  +=  K_BACK · χ_i                              │
  └────────────────────────────────────────────────────────┘
```

**Constants involved**: K_BACK
**Critical**: this is the "back-coupling" that tries to close the
σ_g↔χ loop. In v8 this is what makes χ kinetic-like (T_g = K_BACK/2 · χ²)

### 2.6 V_couple (Yukawa φ-mass)

```
              g · (σ_m_ref − σ_m)² · (1 − cos φ)
   σ_m, φ  ───────────────────────────────────────► coupled potential

  ┌────────────────────────────────────────────────────────┐
  │  V_couple = (g/2) · (σ_m_ref − σ_m)² · (1 − cos φ)     │
  │  Forces:                                               │
  │   F_σm = -g · (σ_m_ref − σ_m) · (1 − cos φ)            │
  │   F_φ  = -(g/2) · (σ_m_ref − σ_m)² · sin φ             │
  └────────────────────────────────────────────────────────┘
```

**Constants involved**: g, σ_m_ref
**Effect**: gives φ a position-dependent effective mass m²_φ ∝ (σ_m_ref − σ_m)²

## Section 3 — Connection diagram (master view)

```
                    ┌──────────────────┐
                    │   GRAPH G(V,E)   │  (cubic lattice, z=6, FIXED)
                    └────────┬─────────┘
                             │ adjacency only — no state on edges
                             ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                    NODE STATE per i                         │
   │                                                             │
   │   σ_g_i ◄──── K_BACK ──────  χ_i  ◄── CHI_DECAY · γ         │
   │     │                          ▲                            │
   │     │ K_GM (Ch A)              │ CHI_REL (laplacian)        │
   │     ▼                          │ DELTA_CHI (deviation)      │
   │   σ_m_i  ────────────► φ_i    σ_g_i ──────┘                 │
   │     │       g (V_couple)       │                            │
   │     │ MU_M                     │ MU_PHI                     │
   │     │ canonical pair           │ canonical pair             │
   │     ▼                          ▼                            │
   │   π_m_i                       π_φ_i                         │
   │                                                             │
   │   E_B_g, E_B_m, E_φ:  gradient terms via BETA_*             │
   │   Channel F:  GAMMA_PHI · (1-|Z|) · σ_m  (φ→σ_m diffusion)  │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │                  EMERGENT PHENOMENOLOGY                     │
   │                                                             │
   │   c_φ²  =  BETA_PHI / (3·MU_PHI) = 0.0117                   │
   │   G_QNG =  BETA_G / z = 0.058                               │
   │   ω_orb =  2π / T_cycle ≈ 0.0346 (R=4)                      │
   │   ⟨L⟩   =  N·BETA_PHI/2 = 660 (XY ground state)             │
   │   a_M   =  1.373e-3 (mass scale calibration)                │
   │   λ_max =  +0.00150 (Lyapunov, weak chaos)                  │
   │                                                             │
   │   Einstein correspondence (DER-QNG-044):                    │
   │     ✓ KG dispersion (uses c_φ)                              │
   │     ✓ Shapiro delay (uses K_GM, BETA_PHI)                   │
   │     ✓ Tensorial coupling (uses g, σ_m_ref)                  │
   │     ✗ E=mc² (rings dynamic, no static rest mass)            │
   │     ✗ Far-field 1/b (ratio 0.96 not 2.0)                    │
   │     ? WEP + Pound-Rebka (inconclusive)                      │
   └─────────────────────────────────────────────────────────────┘
```

## Section 4 — Constant-to-channel cross-reference

| Constant | Channel(s) | Affects |
|---|---|---|
| BETA_G | B (gradient) | σ_g spatial smoothness, G_QNG, λ_screen |
| BETA_M | B (gradient) | σ_m spatial smoothness |
| BETA_PHI | B/A' (XY) | φ stiffness, c_φ², ⟨L⟩ |
| ALPHA | restoration | σ deviation cost from ref |
| MU_M | kinetic T_m | σ_m effective mass, π_m dynamics |
| MU_PHI | kinetic T_φ | φ effective mass, π_φ dynamics, c_φ² |
| K_BACK | G (χ→σ_g) | χ feedback, T_g coefficient |
| K_GM | A (σ_m→σ_g) | gravitational source, Shapiro delay |
| CHI_DECAY | D (γ) | χ damping rate |
| CHI_REL | D (Laplacian) | χ source from σ_g neighbors |
| DELTA_CHI | D (deviation) | χ source from σ_g vs σ_ref |
| GAMMA_PHI | F | σ_m depletion in disorder |
| g | V_couple | Yukawa φ-mass, ring stability |
| σ_m_ref | A, V_couple | matter vacuum value |
| σ_g_ref | A, D, restoration | gravitational vacuum value |

## Section 5 — Topology of conserved quantities

### 5.1 Continuous symmetries → continuous conservation

```
H_v8 conserved             ←────  time translation
P_x, P_y, P_z conserved    ←────  spatial translations
M_ring conserved (Phase 3) ←────  internal symmetry of σ_m sum
```

**Note**: NO compact symmetry (per CPU-101 DIRAC analysis). All
continuous symmetries are NON-COMPACT. This is the structural reason
no Bohr-Sommerfeld-type quantization emerges naturally.

### 5.2 Discrete topology → integer conservation

```
W_φ = ∮ dφ / 2π ∈ ℤ  ←──── π_1(U(1)) = ℤ
   "winding number around closed loop"
```

This IS an integer-valued conserved quantity — closest thing v8 has
to "quantization."

But: W_φ is **TOPOLOGICAL**, not **DYNAMICAL**. It changes only via
discrete topological transitions, not continuously. So it doesn't
provide a "smooth" integer spectrum like quantum harmonic oscillator
energy levels.

### 5.3 What's missing in topology

Quantum mechanics has TWO kinds of integer quantization:
- Topological (winding, Chern number, Berry phase) — v8 HAS
- Spectral (E_n = ℏω(n+1/2), L_z = ℏm) — v8 LACKS

Spectral quantization requires:
- Compact symmetry (e.g., U(1) → integer angular momentum)
- Or: discrete spectrum operator (Hamiltonian with bound states)

v8 has neither. Hence DER-QNG-038 baryon ladder is empirical not
spectral.

## Section 6 — Connection MAP — what's missing (gaps for v10)

This is the critical visualization. Marks where connections END that
quantum mechanics REQUIRES.

```
                    ┌──────────────────┐
                    │   GRAPH G(V,E)   │
                    │  ┌─ EDGES ARE ───┐│  ← MISSING: edges should
                    │  │  STATE-LESS   ││    carry state too (v9-G)
                    │  └───────────────┘│
                    └────────┬─────────┘
                             │
                             ▼
   ┌──────────────────────────────────────────────────────────┐
   │ NODE STATE                                                │
   │                                                           │
   │  σ_m, φ           ◄═══ MISSING ═══►   Ψ ∈ ℂ              │
   │  separate         (complex unification)                   │
   │  reals                                                    │
   │                                                           │
   │  {σ_m, π_m} = 1   ◄═══ MISSING ═══►   [σ̂_m, π̂_m] = iℏ   │
   │  classical Poisson  (deformation quantization)            │
   │                                                           │
   │  Yoshida4 single   ◄═══ MISSING ═══►   ∫Dq exp(iS/ℏ)     │
   │  trajectory         (path integral)                       │
   │                                                           │
   │  Liouville         ◄═══ MISSING ═══►   Unitary U†U=I     │
   │  preserves volume   (preserves norm)                      │
   │                                                           │
   │  Definite values   ◄═══ MISSING ═══►   |ψ|² probability   │
   │                     (Born rule)                           │
   │                                                           │
   │  Single config     ◄═══ MISSING ═══►   Hilbert superpos.  │
   │                     (linear combinations)                 │
   │                                                           │
   │  Passive readout   ◄═══ MISSING ═══►   Measurement coll.  │
   │                     (state collapse)                      │
   │                                                           │
   │  Continuous E      ◄═══ MISSING ═══►   E_n = ℏω(n+½)     │
   │                     (discrete spectrum)                   │
   └──────────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────┐
   │ ALSO MISSING: connection from substrate to ℏ_value        │
   │                                                           │
   │   No constant in v8 has dimension of action.              │
   │   ⟨L⟩=660 is dimensionless; needs unit-bridge to J·s.     │
   │                                                           │
   │   v10 must define ℏ_lattice = (some product of            │
   │   substrate constants) × (lattice spacing)^? = J·s        │
   └──────────────────────────────────────────────────────────┘
```

## Section 7 — The "missing channels" for v10

### 7.1 Channel Q1 — Quantization deformation

```
          NEW CHANNEL: deformation quantization
          ────────────────────────────────────
   {σ_m, π_m} = 1     ────►     [σ̂_m, π̂_m] = iℏ_lattice · I

   Implementation: replace symplectic pair with operator pair
   on Heisenberg algebra.
```

**Constant introduced**: ℏ_lattice (with dimension of action)

### 7.2 Channel Q2 — Complex amplitude unification

```
          NEW CHANNEL: amplitude+phase fusion
          ────────────────────────────────────
   (σ_m_i, φ_i)  ────►   Ψ_i = σ_m_i · e^{iφ_i}  ∈ ℂ

   Implementation: Ginzburg-Landau order parameter
```

**Replaces**: separate σ_m and φ fields
**Dynamics**: Schrödinger-like `iℏ ∂_t Ψ = Ĥ Ψ`

### 7.3 Channel Q3 — Path integral evolution

```
          NEW CHANNEL: history sum
          ────────────────────────────────────
   single Yoshida4   ────►   ⟨Ψ_f|U(t)|Ψ_i⟩ = ∫ DΨ exp(iS[Ψ]/ℏ)

   Implementation: Monte Carlo sampling over discrete histories
```

**Constant used**: ℏ in path weight `exp(iS/ℏ)`

### 7.4 Channel Q4 — Edge state (graphity)

```
          NEW CHANNEL: edge state evolution
          ────────────────────────────────────
   STATE on EDGES e=(i,j):  w_ij ∈ ℂ (or [0,1])

   Implementation: edge weights become dynamical variables
```

**This is v9-G** (DER-QNG-058). Promotes edges from passive adjacency
to active state-carriers.

### 7.5 Channel Q5 — Measurement-decoherence

```
          NEW CHANNEL: environment coupling
          ────────────────────────────────────
   Pure state Ψ_pure  ────►  Density matrix ρ
   ρ = Σ p_i |ψ_i⟩⟨ψ_i|

   Implementation: trace over environmental DOF, off-diagonal terms
   suppress (decoherence)
```

**Provides**: Born rule + apparent state collapse via decoherence

## Section 8 — Verifiable connection table — v8 vs v10

| Connection | v8 has? | v10 needs? | Mechanism in v10 |
|---|---|---|---|
| Node state ℝ⁶ | ✓ | ✗ | Replace with Ψ ∈ ℂ |
| Edge state | ✗ | ✓ | New (v9-G) |
| Poisson bracket | ✓ | ✗ | Replace with commutator |
| Heisenberg algebra | ✗ | ✓ | NEW |
| Symplectic evolution | ✓ | ✗ | Replace with unitary |
| Path integral | ✗ | ✓ | NEW |
| Real Hamiltonian | ✓ | ✗ | Replace with Hermitian operator |
| Hilbert space | ✗ | ✓ | NEW |
| Born rule | ✗ | ✓ | NEW (decoherence) |
| Topological winding | ✓ | ✓ | KEEP (already integer) |
| ⟨L⟩=660 invariant | ✓ | ? | KEEP as classical limit |
| Shapiro delay | ✓ | ✓ | KEEP as classical limit |
| Baryon ladder | ✓ | ? | Re-derive as quantum operator spectrum |
| ℏ_value | empirical | ✓ | DERIVE from ℏ_lattice |

## Section 9 — Diagram: full v10 vision

```
                ┌───────────────────────┐
                │ FUNDAMENTAL: ℏ_lattice│  ← derived from substrate
                └──────┬───────────────┘    by NEW Quantization Channel
                       │
                       ▼
   ┌──────────────────────────────────────────────────────┐
   │  GRAPH G(V, E)                                       │
   │  • V: nodes (countable, fixed in v10-min)            │
   │  • E: dynamical edges (v9-G + ℏ_lattice scale)       │
   └──────────────────┬───────────────────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────────────────┐
   │  NODE STATE: Ψ_i ∈ ℂ                                 │
   │  • Replaces (σ_m_i, φ_i) with Ψ = σ_m · e^{iφ}       │
   │  • Operator algebra: [Ψ̂, Ψ̂†] = ℏ_lattice · I        │
   │  • Hilbert space: |state⟩ = ⊗_i |Ψ_i⟩                │
   └──────────────────┬───────────────────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────────────────┐
   │  EVOLUTION: path integral                            │
   │  ⟨Ψ_f|Ψ_i⟩ = ∫ DΨ exp(i S[Ψ] / ℏ_lattice)            │
   │  Hamiltonian Ĥ = T̂ + V̂ Hermitian operator          │
   └──────────────────┬───────────────────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────────────────┐
   │  OBSERVABLES & MEASUREMENT                           │
   │  ⟨Ô⟩ = ⟨Ψ|Ô|Ψ⟩                                       │
   │  P(outcome o_n) = |⟨o_n|Ψ⟩|²    (Born rule)         │
   │  Decoherence via environmental tracing               │
   └──────────────────┬───────────────────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────────────────┐
   │  EMERGENT PHENOMENOLOGY (preserved from v8 in        │
   │  classical limit ℏ_lattice → 0):                     │
   │  • GR-like (Einstein correspondence)                 │
   │  • Baryon mass ladder                                │
   │  • Topological winding                               │
   │  PLUS NEW (from quantum structure):                  │
   │  • Discrete energy spectrum E_n = ℏω(n+½)           │
   │  • Interference, superposition                       │
   │  • Non-local correlations                            │
   │  • Born-rule probabilities                           │
   └──────────────────────────────────────────────────────┘
```

## Section 10 — Where ℏ_lattice comes from in v10

This is the deepest question. v10 needs a constant `ℏ_lattice` with
dimension of action `[Energy × Time] = [Mass × Length² / Time]`.

### Candidate sources (NOT proofs, just options):

**Option A — Lattice spacing × kinetic scale**
```
ℏ_lattice ~ μ_φ · a² / dt = 0.857 × 1² / 0.025 = 34.3
                              (in QNG natural units)
```
Trivially has action dimension. But arbitrary unless connected to
something deeper.

**Option B — Topological action scale**
```
ℏ_lattice ~ ⟨L⟩_universal = 660
                              (already an action invariant per NOTE-QNG-017)
```
This already has dimension of action. Gabriel's "⟨L⟩=660" finding
becomes ℏ_lattice itself!

**Option C — Edge fluctuation scale**
```
ℏ_lattice ~ 〈edge_weight × edge_correlation_time〉
```
Requires v9-G full implementation.

**Option D — Discrete Bohr-Sommerfeld**
```
ℏ_lattice = ∮ p dq / 2π · (some integer)
```
Requires identifying which orbit and which integer.

### Provisional recommendation

**Option B (⟨L⟩=660)** is the most natural. It is:
- Already a derived classical invariant (NOTE-QNG-017)
- Already R-universal (CV 0.11%)
- Already has dimension of action (β_phi · N has units of action·node-count)
- Per-node: ⟨L⟩/N = β_phi/2 = 0.03 (intensive action constant)

If we set `ℏ_QNG = β_phi/2 = 0.03` in QNG natural units, then:
- All quantum mechanics happens at this energy-time scale
- Calibration to ℏ_SI requires unit-bridge with c, G already set
- It's not a new free parameter — it's already an INVARIANT we found

**This would be a major insight**: ⟨L⟩=660 was the answer to "what is
ℏ in QNG" all along — but we couldn't see it because we didn't have
the operator structure to interpret it as such.

## Section 11 — Closing: visualization summary

The connection map shows v8 has:
- **Real-valued node states** (no complex Ψ)
- **Stateless edges** (no graph dynamics)
- **Classical Poisson brackets** (no operator algebra)
- **Single-trajectory evolution** (no path integral)
- **Liouville conservation** (not unitary)
- **Definite values** (no Born rule)

For each gap, v10 adds a specific channel:
- Q1: Heisenberg algebra deformation
- Q2: Complex amplitude unification
- Q3: Path integral evolution
- Q4: Edge state (graphity)
- Q5: Decoherence-measurement

**ℏ_lattice candidate already exists in v8** as ⟨L⟩=660 — we just
didn't recognize it as such because we lacked operator structure.

This map is the BLUEPRINT for v10. Each missing connection is an
explicit task for foundational implementation.

---

*"Imaginar, vizual" — what we couldn't see before:*

```
v8 connection topology:        v10 connection topology:

    σ_m ──── φ                      Ψ (= σ_m · e^{iφ}) ─── Ψ̂†
     │       │                       │      ↕ [Ψ̂,Ψ̂†]=iℏ
     ▼       ▼                       ▼
    π_m     π_φ        ━━►          π̂_Ψ
     │       │                       │
     {,}=1  {,}=1                   [,]=iℏ
     classical                       quantum
```

The minimal change: replace **two real fields + two Poisson brackets**
with **one complex field + one Heisenberg commutator**. That single
change touches **6 of the 8 missing requirements** simultaneously.
