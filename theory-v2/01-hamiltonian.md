# 01. QNG Hamiltonian

The action principle for QNG dynamics. All field equations follow from this.

## Free Hamiltonian

```
H_QNG = H_φ + H_σg + H_σm + H_χ + H_couple
```

### Phase sector

```
H_φ = -(β_φ / (2z)) · Σ_<i,j> cos(φ_i - φ_j)        (XY interaction)
     + (1 / (2μ_φ)) · Σ_n |Π_n|²                     (kinetic, momenta conjugate to Ψ)
```

Standard XY model on cubic lattice. The cosine interaction is what gives
phase modes their dispersion `ω² = c²k²` in continuum limit.

### Gravity sector (σ_g)

```
H_σg = (α/2) · Σ_n (σ_g,n - σ_g_ref)²              (restoring/cosmological term)
      + (β_g/(2z)) · Σ_<i,j> (σ_g,i - σ_g,j)²        (neighbor smoothing)
```

This gives σ_g a screened Poisson equation with screening length
`λ = √(β_g/(z·α))` (verified at CPU-141: λ_eff ≈ 2.67 lattice units
matches predicted ~3.42 modulo lattice cutoff).

### Matter sector (σ_m)

```
H_σm = similar to σ_g (kinetic + neighbor + restoring)
      + V_couple(σ_m, φ)                            (matter-phase coupling for vortex stability)
```

Where `V_couple = (g/2)·(σ_ref - σ_m)²·(1 - cos φ)` provides Jackiw-Rebbi
mass term for φ in regions of σ_m deficit.

### Responsiveness sector (χ)

```
H_χ = (CHI_DECAY/2) · Σ_n χ_n²                       (relaxation)
     + (CHI_REL/(2z)) · Σ_<i,j> (χ_i - χ_j)²         (diffusion)
     + (DELTA) · Σ_n χ_n · (σ_g_ref - σ_g,n)         (matter-gravity coupling, Channel D)
```

χ encodes how matter responds to gravitational potential. Not a propagating
particle in v10 — rather a constraint field.

### Couplings (cross-sector)

```
H_couple = H_φ-σm + H_σg-σm + ...
```

Detailed couplings are in original ontology files. The key ones are:
- `k_gm` couples σ_g sources to σ_m (gravitational source)
- `K_BACK` couples χ back to σ_g (closes the matter-gravity loop)

## Canonical quantization (v10)

Promote (Ψ, Π) to operators with canonical commutator:

```
[Ψ̂_n, Π̂†_m] = i · ℏ_QNG · δ_{n,m}
```

where ℏ_QNG is the value DERIVED from Stability Principle (next section).

## Equations of motion (key examples)

### Phase: Klein-Gordon equation
For small δφ around φ_0:
```
μ_φ · ∂_t² δφ = β_g/z · ∇²_lattice δφ
```
Continuum limit: `∂_t²δφ = c² ∇²δφ` with `c² = β_φ/(z·μ_φ)`.

### σ_g: screened Poisson
```
α·δσ_g - (β_g/z)·∇²·δσ_g = source
```
Yukawa solution: `δσ_g(r) ~ exp(-r/λ)/r`.

## Substrate parameter values (inputs)

| Parameter | Value | Notes |
|---|---|---|
| β_φ | 0.06 | phase coupling |
| μ_φ | 0.857 | phase inertia (derived from c_g = c_φ matching, DER-QNG-042 §3.3) |
| β_g | 0.35 | σ_g coupling |
| z | 6 | cubic lattice coordination |
| α | 0.005 | restoring (cosmological) |
| g | 0.22 | V_couple strength (DER-QNG-041, Gap 9 placeholder) |
| CHI_DECAY | 0.020 | χ relaxation |
| CHI_REL | 0.35 | χ diffusion |
| DELTA | 0.20 | χ-σ_g coupling |
| K_BACK | 0.10 | χ back-reaction |

These are 10 numbers. **Not all independent**: μ_φ derived from c_g=c_φ
matching condition. So really ~9 independent inputs.

## Why this Hamiltonian

Each term is justified by a specific physical role:
- XY phase: well-known model with vortex defects, gives natural U(1)
- σ_g screened Poisson: needed for Newtonian gravity limit
- σ_m sigmoid coupling: enables vortex ring formation (CPU-074)
- χ Channel D: closes consistent matter-gravity loop

This is NOT minimal in mathematical sense (could be simpler), but it's
**phenomenologically minimal** — every term is needed for some specific
QNG result.

## References

- DER-QNG-036 (H_v7 Hamiltonian construction)
- DER-QNG-042 (v8 canonical extension)
- DER-QNG-062/063 (v10 quantum reformulation)
- Original: `QNG-Theory Release-01/04_qng_pure/qng-v10-foundational-v1.md`
