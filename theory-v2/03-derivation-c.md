# 03. Derivation of c (speed of light)

## Statement

The speed of light is derived from substrate parameters as:

```
c² = β_φ / (z · μ_φ)
c  ≈ 0.108  (natural QNG units)
```

## Derivation

Starting from the XY phase Hamiltonian (01-hamiltonian.md):

```
H_φ = -(β_φ / (2z)) · Σ_<i,j> cos(φ_i - φ_j)  +  (1/(2μ_φ)) · Σ_n |Π_n|²
```

For small phase fluctuations `δφ_i = φ_i - φ̄`, expand the cosine to
quadratic order:

```
cos(δφ_i - δφ_j) ≈ 1 - (1/2)(δφ_i - δφ_j)²
```

This gives the linearized Hamiltonian:

```
H_φ_lin ≈ const + (β_φ/(4z)) · Σ_<i,j> (δφ_i - δφ_j)²  +  (1/(2μ_φ)) Σ |Π|²
```

The Euler-Lagrange equation is:

```
μ_φ · ∂_t² δφ_n = (β_φ/z) · Δ_lattice δφ_n
```

where `Δ_lattice` is the discrete 6-neighbor Laplacian on cubic lattice.

In the continuum limit (`a_L → 0`), `Δ_lattice → ∇²`:

```
∂_t² δφ = (β_φ / (z · μ_φ)) · ∇² δφ
```

This is a Klein-Gordon wave equation with **propagation speed**:

```
c² = β_φ / (z · μ_φ)
```

## Numerical value

Using parameter values:
- β_φ = 0.06
- μ_φ = 0.857
- z = 6

```
c² = 0.06 / (6 × 0.857) = 0.0117
c  = √0.0117 ≈ 0.108  (natural QNG units)
```

## Verification methods

### Verification 1: Direct lattice dispersion
For a plane wave `δφ ~ exp(i(k·x - ωt))`, the lattice dispersion is:

```
ω²(k) = (β_φ/(z·μ_φ)) · 2(3 - cos k_x - cos k_y - cos k_z)
```

For small k: `ω² ≈ c² · |k|²` (continuum limit recovered).

CPU verification: GPU-026 measured ω(k) at k = 1, 2, 3 (in lattice units)
and matched prediction within 3.8/6.0/4.5%.

### Verification 2: Einstein E² = m²c⁴ + p²c²
GPU-035 confirmed Jackiw-Rebbi dispersion:
```
E² = (ℏ ω)² with ω² = c² k² + m²
```
where m² = (g/2μ_φ)·(σ_ref - σ_m)². Verified at 0.02% precision.

### Verification 3: Cross-sector consistency
DER-QNG-042 §3.3 derived the matching condition `c_g = c_m = c_φ` by
fixing `μ_g = β_g·μ_φ/β_φ ≈ 5.0` and `μ_m` similarly. This makes all
substrate wave speeds equal — consistent with GW170817 to 10⁻¹⁵.

## Why this is non-trivial

In standard physics, c is **postulated** (Einstein 1905). It's a
fundamental constant by axiom.

In QNG, c **emerges** from substrate dynamics:
- β_φ is the strength of nearest-neighbor phase coupling
- μ_φ is the inertia for phase oscillations
- z = 6 is the lattice coordination

The combination `β_φ/(z·μ_φ)` is a substrate-derived velocity squared.
This is analogous to:
- Sound speed in solid: `c_sound² = K/ρ` (bulk modulus / density)
- Light speed in QNG: `c² = β_φ/(z·μ_φ)` (phase coupling / inertia)

## Implications

- c is no longer fundamental — it's emergent from substrate
- If substrate parameters effectively varied (high T, near horizons),
  c could vary in specific ways (see 07-predictions-invariants.md)
- The numerical value 0.108 in lattice units maps to c_SI = 2.998×10⁸ m/s
  via unit-bridge (06-unit-bridge-SI.md)

## References

- DER-QNG-019 (Newton limit + c_φ derivation)
- DER-QNG-042 §3.3 (matching condition c_g = c_m = c_φ)
- CPU-103, GPU-026, GPU-035 (numerical verifications)
- Original: `QNG-Theory Release-01/04_qng_pure/qng-c-phi-audit-v1.md`
