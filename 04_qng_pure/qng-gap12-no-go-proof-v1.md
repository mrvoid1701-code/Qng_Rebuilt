---
type: derivation
id: DER-QNG-071
title: Gap 12 step 1 — No-go theorem for spin-2 from pure scalar substrate
status: analytical proof
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-069 (Gap 12 statement)
  - einstein-mind consultation 2026-04-24
---

# DER-QNG-071 — No-go theorem: scalar substrate → no propagating spin-2

## Statement

Let a classical/quantum field theory be defined on a spatial manifold
(or lattice) with dynamical fields `{Ψ_α}_α` that all transform as
SCALARS under spatial rotations `SO(3)` at each point. Then no linear
combination or composite built from `{Ψ_α}` and their spatial
derivatives carries an **independent propagating spin-2 mode**.

Equivalently: the physical Hilbert space of asymptotic one-particle
states decomposes only into spin-0 (and possibly spin-1 if there is a
vector field) irreducible representations of `SO(3)`; no spin-2
representation appears with independent dispersion.

## Definitions

**Scalar field**: `Ψ(x)` such that under rotation `R ∈ SO(3)`,
`Ψ'(Rx) = Ψ(x)`. Equivalently, the field VALUE at each point is
invariant under local rotation.

**Spin of a propagating mode**: the representation of the little group
(`SO(2)` for massless, `SO(3)` for massive) that the one-particle
state carries. Spin-2 = the j=2 representation.

**Independent mode**: a plane-wave solution with dispersion relation
`ω = ω(k)` not algebraically constrained by other modes' dispersions.

## Proof

### Step A: Spin = field transformation at a point

The spin of a propagating mode is determined by how the FIELD VALUE at
a fixed point transforms under rotations, not by the spatial
distribution of the wave. This is a standard fact (Weinberg, QFT vol. I,
§5.1): the Lorentz/Poincaré representation of the field is carried by
its INDEX STRUCTURE, not by its derivatives.

A scalar field has no indices. Its value at each point is a scalar,
invariant under rotation. Therefore at each point its transformation
under the little group is trivial (j=0 irrep).

### Step B: Gradients of scalars are constrained vectors

The spatial gradient `∇Ψ` carries one Cartesian index, transforming as
a vector under rotations. Naively this suggests a spin-1 mode. But
`∇Ψ` is NOT an independent field: its dispersion is determined by Ψ's
EOM:

```
(∂_t² - c² ∇²) Ψ = 0  ⇒  ω² = c² |k|²
```

A plane wave Ψ_k(x,t) = A exp(ik·x - iωt) has gradient
`(∇Ψ)_i = i k_i Ψ_k`. This is ALGEBRAICALLY proportional to the
scalar mode: it does not propagate independently. In Fourier space
it is Ψ_k "dressed" with a factor `ik_i`. It does NOT carry an
independent degree of freedom.

### Step C: Higher composites are also dressed scalars

Consider a composite rank-2 tensor built from gradients:

```
T_ij(x) = (∂_i Ψ)(∂_j Ψ)   (symmetric, rank-2)
```

In Fourier space, for a superposition of plane waves Ψ = Σ_k A_k
exp(ik·x - iω_k t):

```
T_ij(x,t) = -Σ_{k,k'} k_i k'_j A_k A_{k'} exp(i(k+k')·x - i(ω_k+ω_{k'})t)
```

This has momentum `k+k'` and frequency `ω_k + ω_{k'}`. **No new
dispersion**: the composite's Fourier mode at (q, Ω) is populated only
if there exist k, k' with k+k' = q AND ω_k + ω_{k'} = Ω. The spectrum
is entirely determined by convolutions of the scalar spectrum.

In particular, the TRACELESS-TRANSVERSE (TT) projection of T_ij in the
direction of q is:

```
T^TT_ij(q) = P_ik P_jl T_kl - (1/2) P_ij P_kl T_kl
```

where `P_ij = δ_ij - q_i q_j/|q|²` is the transverse projector.

For the linear ((∂_i Ψ)(∂_j Ψ)) construction with single plane wave
source q = 2k, we have `T_ij ∝ k_i k_j`. Then:

```
P_ik k_k = k_i - k_i (q·k)/|q|² = k_i - k_i (2|k|²)/(4|k|²) = k_i/2
```

Does not vanish, so h^TT_ij constructed from single-wave composite does
not vanish. BUT it is still entirely determined by A_k (single amplitude
→ single dispersion ω_k). It is a constrained object, not an independent
field.

More rigorously: the canonical-momentum conjugate to T_ij vanishes
identically because T_ij = (∂Ψ)(∂Ψ) contains no independent time
derivative. The only canonical pair is (Ψ, Π_Ψ). Hence no independent
Hamiltonian evolution for T_ij, no independent propagating mode.

### Step D: Coupled multi-scalar sectors

Consider N independent scalar fields `{Ψ_α}_α=1..N`, each with its own
canonical momentum `Π_α`. The Hamiltonian is quadratic in canonical
variables:

```
H = Σ_α [Π_α²/(2μ_α) + (1/2)c_α² (∇Ψ_α)²]  (+ interactions)
```

Free theory has N independent dispersion relations ω_α² = c_α² |k|².
Each is a spin-0 mode. Total: N spin-0 modes.

Interactions couple the modes but do not change their spin structure at
linear level (coupling constants → scattering amplitudes, not new
kinetic poles). After diagonalizing the coupling matrix, we get N
linear combinations of the original fields, still all spin-0.

**No spin-2 emerges.**

### Step E: Gauge/vector fields would give spin-1, not spin-2

If the substrate had a vector field `A_i(x)` (one Cartesian index at
each point), under rotation it transforms as a vector: spin-1. Two
transverse polarizations (like photon). Still not spin-2.

### Step F: Spin-2 requires rank-2 fundamental field

A propagating spin-2 mode requires a fundamental field `h_ij(x)` that
transforms as a symmetric rank-2 tensor under rotations at each point.
Only such a field can carry the j=2 representation in its index
structure.

Lattice representations include:
- Node-valued: h_ij(x_node) with 6 symmetric components per node
- Edge-valued: scalar "edge stretch" λ_{ij} per edge (i,j), from which
  a rank-2 metric emerges via Regge calculus (law of cosines)

Both are MINIMAL additions. The edge-valued form is most parallel to
lattice gauge theory (gauge connections on edges) and to the hbar-edge
program's finding that scalar-on-edges was insufficient — QNG may need
a richer edge primitive for both hbar emergence AND spin-2 graviton.

## Conclusion

**QNG v10 in current form (scalars on nodes + edges with scalar
update laws) CANNOT host a propagating spin-2 graviton.** Gap 12 is
structurally decisive: no amount of non-linear coupling, coarse-
graining, or background-selection can produce spin-2 from pure scalar
fundamental fields.

To close Gap 12 rigorously, QNG must be extended with a genuinely
rank-2 primitive field. The minimal extension (DER-QNG-072, QNG v11)
uses a scalar edge-stretch field λ_{ij}, which is the Regge-calculus
encoding of lattice geometry.

## What this does NOT say

This theorem does NOT say:

- "QNG fails to reproduce gravity." v10 reproduces Newtonian-gauge
  phenomenology (Shapiro, bending, Pound-Rebka, WEP — all PASS in
  DER-QNG-068). The missing piece is the transverse-traceless tensor
  modes.
- "Scalar gravity is wrong." Brans-Dicke, f(R), and related scalar-
  tensor theories are viable with additional tensor content. QNG v10
  is analogous but currently missing the tensor content.
- "Composites of scalars are meaningless." They carry real physical
  information (e.g., stress-energy tensor), but they do not propagate
  as independent degrees of freedom in the sense of Wigner
  classification.

## Verification strategy

The theorem is rigorous at the field-theoretic level. To verify
numerically, we set up a QNG v10 simulation on a sigma_m-broken
background (ring) and count independent propagating modes in the
sigma_g sector:

- Expected: all modes are spin-0 (single mode per wavevector k; no
  transverse-traceless pair)
- Measured: if 2 TT modes appear, theorem is wrong and QNG has
  hidden structure; if 1 mode, theorem is confirmed.

This is executed in `tests/cpu/qng_cpu121_ring_mode_count.py`
(step 2 of Gap 12 closure).

## References

- Weinberg, S. (1995). The Quantum Theory of Fields, Vol. I, §5.1,
  "Scalar Fields" and §5.9, "Massive Particles of Higher Spin".
- Regge, T. (1961). "General relativity without coordinates." Nuovo
  Cim. 19, 558.
- einstein-mind consultation 2026-04-24: "A scalar field per node has
  zero indices; no coarse-graining of zero-index objects produces
  independently-propagating traceless-transverse modes."

## Self-verification

- Step A: standard QFT (Weinberg §5.1). Verified against textbook.
- Step B: gradient of scalar = ik * scalar in Fourier; no new pole.
- Step C: canonical momentum of (∂Ψ)² vanishes identically — confirmed
  by direct calculation δL/δ∂_t(∂_iΨ)(∂_jΨ) = 0 since no ∂_t appears.
- Step D: diagonalization of quadratic Hamiltonian preserves total
  number of canonical degrees of freedom — standard Hamiltonian
  mechanics.
- Step E: vector field gives 2 transverse polarizations under SO(2)
  little group — standard electromagnetism.
- Step F: matches Regge 1961 and standard lattice gravity literature.
