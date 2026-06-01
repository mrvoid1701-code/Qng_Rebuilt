---
type: axiom
id: DER-QNG-076
title: QNG v12 — U(1) gauge field extension closing Gap 15 (electromagnetism)
status: DRAFT axiom (extends v11 with edge gauge field)
author: C.D Gabriel
date: 2026-04-25
upstream:
  - DER-QNG-072 (v11 tensor extension)
  - DER-QNG-074 (Gap 13 scale tension)
  - DER-QNG-075 (Gap 14 M_ring lattice dependence)
  - CPU-135 (EM existing-fields audit; Gap 15 identified)
---

# DER-QNG-076 — QNG v12 EM extension

## Motivation (Gap 15)

CPU-135 demonstrates that no existing QNG v10/v11 field can host
electromagnetic dynamics:
- All matter fields (σ_g, σ_m, φ, χ) are scalar (spin-0).
- φ has only GLOBAL U(1) symmetry, not LOCAL gauge symmetry.
- Scalar gradients have curl = 0 (gauge-trivial in EM sense).
- Composite vectors are constrained, not independent DOF.

Closing Gap 15 (EM absence) requires new ontology carrying rank-1
vector index structure. We add a U(1) gauge field on lattice edges,
following standard compact lattice gauge theory (Wilson 1974).

## Definition (v12 extension)

### Fields

All v10 + v11 fields are preserved. We add:

**Definition** (gauge field on edges): For each directed lattice edge
`(i, j)` (where j is a nearest neighbor of i in cubic lattice), a real
scalar `A_{ij} ∈ ℝ` with anti-symmetry constraint:

```
A_{ji} = -A_{ij}
```

For a 3D cubic lattice with `N = L³` nodes, there are `3L³` independent
directed edges (3 principal directions per node).

### Plaquette field strength

For each plaquette (oriented quadrilateral on the lattice), the discrete
field strength is the sum of edge variables around the plaquette:

```
F_p = A_{ij} + A_{jk} + A_{kl} + A_{li}
```

For 3D cubic lattice, there are 3 plaquette types per node (in xy, yz,
xz planes). Total: `3L³` independent plaquettes.

### Continuum limit interpretation

In continuum, A_{ij} → A_μ(x) (vector potential), F_p → F_μν(x)
(field strength tensor):

```
F_μν = ∂_μ A_ν - ∂_ν A_μ
```

This is the standard Maxwell field strength.

### Hamiltonian (kinetic + potential)

Free EM Lagrangian:
```
L_A = (1/2 μ_A) Σ_edges (∂_t A_{ij})² - (1/4 μ_A) Σ_plaquettes F_p²
```

In continuum:
```
L_A = -(1/4 μ_A) F_μν F^μν
```

Standard Maxwell action.

### Coupling to matter

The φ-phase term in v10 Hamiltonian is modified to be gauge-invariant
via minimal coupling:

```
H_phi_v12 = -(β_φ/(2z)) Σ_<ij> cos(φ_i - φ_j - e A_{ij})
```

where `e` is the elementary electric charge in QNG natural units.

Under local U(1) gauge transformation:
```
φ_i → φ_i + α_i  (local phase rotation)
A_{ij} → A_{ij} + (1/e)(α_j - α_i)  (gauge transformation of A)
```

The Hamiltonian H_phi_v12 is invariant. This is the LOCAL U(1) gauge
symmetry that QNG v10 lacked.

### Coupling constant `e`

In standard QED, `e ≈ 0.303` (in natural units with α_fine ≈ 1/137).

In QNG, `e` is set by substrate parameters. Currently UNDERIVED — added
as input pending future first-principles derivation. Same status as the
matter coupling `g` in DER-QNG-041 (Gap 9).

## Photon dispersion

Free A field plane wave: `A_{ij}(t) = A₀ ε_a exp(i(k·r_{edge} - ωt))`

where `ε_a` is a polarization vector (3 components in 3D, reduced to 2
after gauge fixing).

Plaquette field strength evaluated on plane wave gives:
```
F_p² ∝ |k × A|² (transverse component squared)
```

EOM from L_A:
```
(1/c_A²) ∂_t² A = ∇² A  (transverse modes)
```

Dispersion:
```
ω² = c_A² |k|²
```

with `c_A² = 1/(μ_A · 1) = 1/μ_A` (in lattice units with edge-spacing 1).

To match `c_A = c_φ = c_g` (per DER-QNG-042 §3.3 protection), we need:

```
μ_A = 1/c_φ² = z·μ_φ/β_φ
```

For QNG parameters: `μ_A = 6 × 0.857 / 0.06 = 85.7`.

## Polarization

For `k` along z-axis, transverse gauge condition `k·A = 0` gives:
- A_z = 0 (longitudinal eliminated)
- A_x, A_y free (transverse polarizations)

Two physical components — matches photon's 2 polarizations exactly.

Spin-1 transformation: under rotation by π/2 around z-axis:
- A_x → A_y, A_y → -A_x
- One full rotation (2π) returns to identity (consistent with spin-1)

## Predictions

1. **Massless photon** (m_γ = 0 from gauge invariance) — matches all
   precision EM tests.
2. **Two polarizations** — matches photon physics.
3. **c_γ = c_φ = c_g = c** — protected by DER-QNG-042 §3.3 + similar
   for v12.
4. **Coupling to charged matter**: any field with nontrivial U(1)
   transformation is "charged"; couples via cos(φ - eA) term.
5. **Maxwell equations** in continuum limit — by construction.

## Implications: closes Gap 15 + opens Gap 16

### Closes Gap 15

QNG with v12 contains electromagnetism at the linearized level. Maxwell
equations emerge in continuum limit. Standard electrodynamics
phenomenology (charges, fields, photons) reproducible.

### Opens Gap 16: charge quantization

The coupling `e` must be discretized for compact U(1) — vortex rings
should carry quantized integer charge (electric charge quantization).
This is NOT yet derived; would require analyzing topology of A-field
configurations around σ_m vortex rings.

## Status

**v12 is a DRAFT axiom extension to close Gap 15**. To promote to
LOCKED AXIOM:

1. Numerical implementation: CPU code with A_{ij} field + dynamics
2. Verify photon dispersion ω² = c² k²
3. Verify 2 transverse polarizations
4. Verify gauge invariance under local U(1)
5. Match Maxwell equations in continuum limit

Test: `tests/cpu/qng_cpu136_v12_photon_verification.py` (next).

## Honest scope

Same caveat as v11: v12 is an **axiomatic addition** of standard lattice
U(1) gauge theory to QNG. It is NOT a derivation of EM from substrate
principles. The Lagrangian is imported from QED/lattice gauge theory.

This parallels how the Standard Model adds the Higgs by axiom for
observation matching: legitimate theory construction, not "trick".

In QNG total: v10 substrate (matter) + v11 (gravity tensor) + v12 (EM gauge).
Each layer adds the minimal field needed to match observation at the
appropriate spin level.

## Next steps

1. Verify v12 photon properties numerically (CPU-136).
2. Compute charge of σ_m vortex ring under v12 — does ring carry electric
   charge naturally? (Would close Gap 16.)
3. Reinvestigate dark matter under v12: are there vortex configurations
   that decouple from A field (no charge → invisible to EM, gravitating
   only via σ_g) → DM candidates? Connect with Phase 2 of DM exploration.
