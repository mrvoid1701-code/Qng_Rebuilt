---
id: NOTE-QNG-019
type: note
title: v9 design charter — aesthetic constraints and structural options
version: v1
date: 2026-04-22
status: charter (pre-design, requires Gabriel approval before implementation)
upstream:
  - DEC-QNG-006 (edge-stochastic closure)
  - NOTE-QNG-018 §8 (13-program failure record)
  - NOTE-QNG-016 (v8 as classical field theory awaiting quantization)
---

# v9 Charter

## Purpose of this document

This is a design charter, not a design. It records the aesthetic
constraints Gabriel imposed on any v9 extension and enumerates the
structural options that survive the v8-internal ℏ-emergence
exhaustion (DEC-QNG-006). No implementation begins until Gabriel
reviews this charter and selects a direction.

## Aesthetic constraints (Gabriel 2026-04-22)

Direct quotes:
- "delicat si mai frumos decat ar trebuii"
- "nu bolt-on"  (earlier refusal of naive Langevin on χ)
- "emergence din substrat" (preserved as aspirational)

Operationalized:
1. **No bolt-on**: v9 must be a structural extension with independent
   physical motivation, not an ad hoc ℏ-injection.
2. **Structural protection**: the proposed ℏ scale must be
   structurally PROTECTED against continuous tuning. All 13 failed
   programs could be tuned to zero; v9 must have a mechanism that
   prevents this.
3. **Preserve v8 locked layer**: Jackiw-Rebbi mass (GPU-035), KG
   dispersion (GPU-012), Lorentz isotropy (DER-QNG-043), Shapiro
   delay (DER-QNG-044), orbital attractor ⟨M_ring⟩ (GPU-031f) must
   survive intact. v9 is an extension, not a replacement.
4. **Wallstrom audit**: v9 must be shown to NOT be equivalent to
   Madelung hydrodynamics + noise (that route is blocked by Wallstrom
   1994).
5. **No symbol overloading**: if v9 introduces new primitives, they
   carry new names; do not re-purpose χ, σ_m, φ, or π_φ semantics.

## Structural options

Four candidate directions survive the v8 exhaustion. None are
commitments; all require Gabriel-level review.

### Option V9-A — Topological protection via geometric phase

**Idea**: ring orbital attractor (GPU-031f) has period ≈ 185 lu and
Noether charge M_ring. If v9 adds a **Berry-phase-like term** to
H_v8 counting the winding of (σ_m, π_m) around the orbit, the
action around one orbit is

  S_Berry = ∮ π_m dσ_m  +  θ · n_winding

where n_winding is an INTEGER (topological) and θ is the v9
coupling. At the classical level S_Berry is continuous; but if the
orbit is closed (attractor), the integral S_Berry modulo 2π becomes
a topological invariant — an emergent quantum of action.

**Aesthetic**: high. Integer winding is intrinsic to v8 (phi field
has Z winding already tested in CPU-080), ring attractor is known
periodic. Nothing imposed — ℏ candidate = θ, tuned by ring geometry.

**Risk**: S_Berry modulo 2π is not a true ℏ — it's a geometric phase
on orbits. Quantization of θ itself needs further mechanism.

**Minimal test**: compute ∮ π_m dσ_m on GPU-031f orbit at R∈{3,4,5};
if value clusters at integer multiples of some θ_0 → v9-A candidate.

### Option V9-B — Fluctuation-dissipation on conjugate momenta

**Idea**: add noise Ξ(t) to π_m and π_φ with dissipation γ on the
same channel, satisfying FDT relation

  ⟨Ξ(t) Ξ(t')⟩ = 2 γ k_B T δ(t-t')

At equilibrium the Gibbs distribution has ⟨π²⟩ = μ T. This is pure
thermodynamics, no ℏ. BUT if v9 demands that T itself is structurally
PROTECTED at a value T_0 (maybe via Hawking-like temperature of
emergent horizon, or Unruh-like acceleration scale of ring orbit)
then ⟨π²⟩ = μ T_0 becomes a universal scale.

**Aesthetic**: medium. FDT is beautiful but T_0 must be structurally
derived — if tunable, no ℏ.

**Risk**: Wallstrom 1994 blocks the Madelung + noise path.
FDT on (π_m, σ_m) is NOT Madelung (which is on wavefunction modulus
& phase). Needs formal audit.

**Minimal test**: add γ and Ξ to pi_m with exact FDT, scan γ, check
if ⟨π_m²⟩ plateaus at a structurally-determined value independent
of γ.

### Option V9-C — Path integral quantization (Option c from NOTE-QNG-018)

**Idea**: accept H_v8 is classical. Impose

  Z = ∫ Dφ Dπ_φ Dσ_m Dπ_m exp(i S[H_v8] / ℏ)

where ℏ is an external constant of nature, Weyl-corresponded to
H_v8. This is standard canonical quantization.

**Aesthetic**: honest but concedes emergence. Gabriel called this
"mai delicat" in the 2026-04-22 conversation — it does not pretend
emergence where there isn't one.

**Risk**: demotes QNG from "fundamental theory including ℏ" to
"classical substrate underlying quantum mechanics" — philosophically
smaller claim.

**Minimal test**: not simulation — requires analytic work. Compute
path integral of H_v8 at tree + 1-loop and check if it matches
standard lattice gauge / lattice scalar field quantization.

### Option V9-D — Non-abelian generalization

**Idea**: v8 is U(1)/Z (phi winding). Promote to SU(2) or Z_N with
n-ality structure. Non-abelian commutators [J_a, J_b] = i ε_abc J_c
naturally carry a structural scale; ℏ = scale of Lie algebra.

**Aesthetic**: high. Matches SM gauge structure. Lie algebras are
structurally rigid — scale cannot be tuned to zero without breaking
the algebra.

**Risk**: heavy rewrite of substrate. Violates constraint 3
(preserve v8 locked layer) unless the non-abelian structure is an
ADDITION, not a replacement.

**Minimal test**: replace phi in Jackiw-Rebbi sector with SU(2)
doublet, re-run GPU-035 dispersion test, check if new mass ratios
appear.

## Priority ranking (for Gabriel review)

Best alignment with aesthetic constraints:

1. **V9-A (geometric phase)** — closest to "emergence from substrate,"
   testable immediately on existing GPU-031f data. Start here.
2. **V9-C (path integral)** — honest minimal option, no further
   simulation, closes the program cleanly if V9-A/B fail.
3. **V9-B (FDT)** — elegant but requires identifying structurally
   protected T_0 (Unruh-analog is one candidate).
4. **V9-D (non-abelian)** — most ambitious, most disruptive. Reserve
   for after V9-A/B/C are exhausted.

## Decision structure

Before any implementation:
- Gabriel reviews this charter.
- Gabriel selects direction(s) — possibly several in parallel.
- Per-direction design document is drafted with concrete Hamiltonian
  modifications, predicted observables, falsification criteria.
- Only then do tests begin.

This is deliberately slow compared to the breakneck autonomous pace
of 2026-04-22 ℏ-hunt. "Delicat si frumos" requires patience.

## Status

Charter only. No implementation authorized. Last updated 2026-04-22.
