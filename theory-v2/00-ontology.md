# 00. QNG Ontology

The substrate. What QNG IS at the most fundamental level.

## Spatial structure

A **3-dimensional cubic lattice** with periodic boundary conditions.
- Each lattice site has 6 nearest neighbors (coordination number z = 6).
- Lattice spacing `a_L` is the fundamental length scale (determined later
  by SI unit-bridge to be ~0.3 × ℓ_Planck).

## Fields per node

At each lattice node `n`, we assign 4 real-valued scalar fields:

| Field | Domain | Physical role |
|---|---|---|
| `σ_g,n` | `[0, 1]` | Gravitational field amplitude (sources gravity) |
| `σ_m,n` | `[0, 1]` | Matter density amplitude (sources mass) |
| `φ_n` | `[-π, π]` | Phase angle (XY phase, U(1) global symmetry) |
| `χ_n` | `ℝ` | Responsiveness field (matter-gravity coupling) |

**Combined complex amplitude**: `Ψ_n = σ_m,n · e^(iφ_n)` ∈ ℂ.

## Why these fields

| Field | Why included |
|---|---|
| σ_g | Sources gravitational potential (per Newtonian limit derivation) |
| σ_m | Carries matter content (vortex rings = topological structures) |
| φ | XY phase model — well-studied, hosts vortex defects, has natural U(1) |
| χ | Auxiliary responsiveness needed for consistent screened Poisson |

## Per-node degrees of freedom

4 real scalars per node. For lattice of size L (`N = L³` nodes):
- Total DOF: 4N
- For L = 28: ~88,000 DOF in a small simulation

## Static reference values (vacuum)

| Field | Reference value |
|---|---|
| σ_g_ref | 0.5 |
| σ_m_ref | 0.5 |
| φ_uniform | 0 (any constant) |
| χ_vacuum | 0 |

These define the "empty space" configuration around which fluctuations
are studied.

## Substrate parameters (the 5 inputs)

| Parameter | Value | Physical role |
|---|---|---|
| `β_φ` | 0.06 | XY phase coupling strength |
| `μ_φ` | 0.857 | Phase inertia (kinetic mass) |
| `β_g` | 0.35 | σ_g neighbor diffusion / gravity coupling |
| `z` | 6 | Lattice coordination (cubic 3D) |
| `α` | 0.005 | σ_g restoring constant (cosmological scale) |

These are INPUT (not derived from deeper structure). The theory derives
`c, G, ℏ, Λ=0` and many more quantities from these 5 numbers + Stability
Principle.

## What QNG IS NOT

For clarity:

- NOT a quantization of GR (gravity is emergent from σ_g dynamics)
- NOT a UV completion of the Standard Model (no built-in EM, weak, strong)
- NOT continuum from the start (lattice is fundamental, continuum is
  a long-wavelength limit)
- NOT a completed theory (open problems documented in 12-open-problems.md)

## What QNG IS

- A **substrate** for fundamental constants
- An **effective field theory framework** above lattice scale a_L
- A **derivation machine**: given parameters, produces c, G, ℏ, Λ
- A **starting point** for axiomatic extensions when observation requires
  (v11 spin-2 graviton, v12 spin-1 photon)

## References

- Original ontology development: `QNG-Theory Release-01/04_qng_pure/qng-v10-foundational-v1.md`
- This document: clean restatement of substrate ontology, no ambiguities
