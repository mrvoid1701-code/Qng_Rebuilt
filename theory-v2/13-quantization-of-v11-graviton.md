# 13. Quantization of v11 Graviton

Direction A: from classical v11 (Section 11) to fully quantum gravity.

## Setup

In Section 11, v11 added the classical field `h_ij(n)` with Lagrangian:

```
L_h = (1/(2 μ_h)) · |π_ij|²  -  (c²/(4 μ_h)) · |∂_k h_ij|²
```

To quantize, we promote (h_ij, π_ij) to operators with canonical
commutator. This is **canonical quantization** following standard QFT
recipe.

## Canonical commutator

For each lattice node `n` and symmetric traceless index pair (ij):

```
[ ĥ_ij(n), π̂_kl(m) ] = i ℏ_QNG · P^TT_{ij,kl} · δ_{n,m}
```

where `P^TT_{ij,kl}` is the symmetric-traceless projector:

```
P^TT_{ij,kl} = (1/2)(δ_ik δ_jl + δ_il δ_jk) - (1/3) δ_ij δ_kl
```

This ensures the commutator only acts on the physical (5-component
symmetric traceless) part of h_ij.

## Mode expansion

Express h_ij as Fourier modes over the Brillouin zone:

```
ĥ_ij(x, t) = Σ_{k, λ} √(ℏ/(2 μ_h ω_k)) · ε_ij^λ(k) · [â_{k,λ} e^{i(k·x - ω_k t)} + h.c.]
```

with:
- `ω_k² = c² · 2(3 - cos k_x - cos k_y - cos k_z)` (lattice dispersion)
- `ε_ij^λ(k)` polarization tensors, λ ∈ {+, ×}
- `â_{k,λ}, â†_{k,λ}` creation/annihilation operators

The polarization tensors satisfy:
- Transverse: `k^i ε_ij^λ = 0`
- Traceless: `δ^ij ε_ij^λ = 0`
- Orthonormal: `ε_ij^λ ε^*_ij^λ' = δ_{λλ'}`

## Number of graviton modes per wavevector

Counting:
- 6 symmetric components per node
- −1 trace condition → 5
- −2 transversality (`k_i h_ij = 0`, two conditions) → 3
- −1 from longitudinal gauge fixing → **2 physical TT modes**

This matches GR exactly (gravitons have 2 polarizations).

## Vacuum state

The graviton vacuum |0⟩ is annihilated by all creation operators:
```
â_{k,λ} |0⟩ = 0  for all k, λ
```

Energy of vacuum: `E_vac_h = (ℏ/2) · Σ_{k,λ=2 modes} ω_k`

## Connection to Stability Principle

The graviton vacuum energy ADDS to the substrate vacuum energy of
Section 02. The Stability Principle was originally formulated for the
phase sector alone:

```
E_vacuum_phi = -β_φ · N / 2 + (ℏ_QNG/2) · Σ_k ω_k(phi) = 0
```

With v11 graviton sector, we have additional vacuum energy:

```
E_vacuum_h = (ℏ_QNG/2) · 2 · Σ_k ω_k(h)
```

(factor 2 for two polarizations)

For STRICT zero total vacuum (Λ = 0 exact), we'd need:

```
E_vacuum_phi + E_vacuum_h + E_vacuum_other = 0
```

Since ω_k(h) = ω_k(phi) (same lattice dispersion, by `c_g = c_phi`
matching), the graviton vacuum has the same magnitude as 2× phi modes.

This requires either:
- Compensating negative contribution from another sector (could be matter sector)
- Modification of Stability Principle to include all sectors

**Status**: this is OPEN issue. The original Stability Principle was for
phi alone and gave correct ℏ. With v11 quantum, full vacuum balance is
non-trivial.

**Tentative resolution**: Stability Principle should be applied to TOTAL
vacuum energy across all sectors. This generalizes the principle but
preserves its structure.

## Graviton propagator (free theory)

In transverse-traceless gauge, the propagator is:

```
G^TT_{ij,kl}(k, ω) = i · ℏ · P^TT_{ij,kl} / (μ_h · (-ω² + c²k²))
```

Imaginary-time / Wick-rotated form:
```
G^TT_{ij,kl}(k) = ℏ · P^TT_{ij,kl} / (μ_h · (k² + ω_E²/c²))
```

For SI dimensional analysis: this is standard graviton propagator.

## Lattice UV cutoff

A key feature: lattice graviton has WAVENUMBER CUTOFF at Brillouin
zone edge:

```
|k|_max = π/a_L  (Brillouin zone edge)
```

With a_L = 0.305 ℓ_Planck, this gives:
```
|k|_max ≈ π/(0.305 ℓ_P) ≈ 10.3 / ℓ_P
```

Equivalent UV energy: E_UV = ℏ·c·k_max ≈ 10.3 × E_Planck.

So QNG has a UV cutoff at about 10 Planck energies. Physics at
energies above this is OUTSIDE the substrate framework.

## Comparison with continuum graviton EFT

Standard effective field theory of gravity (Donoghue 1994):
```
G_grav(k) = i / (k² + iε)
UV cutoff: at Planck scale, perturbation breaks down
```

QNG lattice graviton:
```
G_grav(k) = i · ℏ · P^TT_{ij,kl} / (k_lattice² + ω²)
where k_lattice² = 2(3 - cos k_x - cos k_y - cos k_z)/a_L²
UV cutoff: |k| < π/a_L = π/(0.305 ℓ_P) → soft above ~10 E_Planck
```

For low momenta (`|k|·a_L << 1`), continuum form recovered.
For high momenta (`|k|·a_L ~ 1`), lattice corrections appear:
```
k_lattice² = |k|² - (|k|⁴·a_L²)/12 + O(|k|⁶ a_L⁴)
```

## QNG-specific quantum gravity prediction

The leading lattice correction to standard graviton propagator is at
order `|k|² a_L²`:

```
G_QNG(k)/G_continuum(k) ≈ 1 + (|k|² a_L²)/12 + ...
```

For Planck-scale graviton (|k| ~ 1/ℓ_P): correction is `(0.305)²/12 ≈ 0.0078`,
about 0.8% deviation from continuum.

**SPECIFIC PREDICTION**: at energies near Planck scale, graviton scattering
amplitudes deviate from continuum EFT by ~1% in form factor. Testable in
principle via future ultra-high-energy experiments OR via numerical
lattice quantum gravity simulations.

## Tree-level matter-graviton coupling

Coupling to matter (via stress-energy tensor T_ij):

```
H_int = -(8π·G/c⁴) · ĥ_ij(x) · T̂^{TT}_ij(x)
```

For two static masses separated by distance r:
```
V(r) = -G·M₁·M₂ / r  (Newtonian, recovered from tree-level h-exchange)
```

This is the graviton-mediated Newtonian potential, standard QFT result.

## One-loop correction (Donoghue 1994)

Standard QFT-of-gravity gives quantum correction:
```
V(r) = -G·M₁·M₂/r · [1 + (3G(M₁+M₂))/(rc²) + (41/10π)·Gℏ/(c³r²) + ...]
```

The `41/10π` coefficient is parameter-free QG prediction.

**QNG version**: would receive lattice corrections at high k. To leading
order in `(a_L/r)²`, the coefficient might be modified:
```
QNG: 41/10π × (1 + δ)  with δ ~ (a_L/r)²
```

For r >> a_L (any macroscopic scale), δ → 0 and QNG matches standard EFT.

For r ~ a_L (Planck-scale): full lattice analysis needed.

**Status**: this is the right calculation to do but requires multi-week
analytical work. SKETCHED in this section, NOT computed.

## Summary

v11 quantization:
- Standard canonical quantization of h_ij
- 2 TT modes per wavevector (matches GR)
- Lattice UV cutoff at |k| = π/a_L ≈ 10/ℓ_P
- Graviton propagator with explicit lattice correction (~1% at Planck)
- Newtonian potential recovered at tree level

QNG-specific predictions:
- **Lattice correction to graviton propagator** at Planck-scale momenta
- **Cutoff at finite UV scale** (no infinite ladder)
- **Vacuum energy reconciliation** required (open extension to Stability Principle)

## Status

This is the first systematic quantization of v11 in clean theory-v2.
Builds on:
- v11 classical Lagrangian (Section 11)
- Stability Principle (Section 02)
- Substrate scale a_L (Section 06)

Open issues:
- Full Stability Principle in multi-sector quantum theory
- Loop corrections specific to QNG vs continuum
- Donoghue coefficient comparison

Path forward: numerical verification + analytical perturbation expansion.
