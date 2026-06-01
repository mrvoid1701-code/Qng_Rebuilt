# 11. Axiomatic Extensions: v11 (graviton) and v12 (photon)

The base QNG (v10) has only scalar fields per node. To match observed
spin-2 graviton (LIGO/Virgo) and spin-1 photon (electromagnetism), we
add minimal axiomatic extensions.

**Important framing**: these are AXIOMATIC additions, not derivations.
They parallel how the Standard Model adds the Higgs by fiat to match
observation.

## v11: Spin-2 Graviton Extension

### Motivation (Gap 12)

Theorem (DER-QNG-071): pure scalar substrate cannot host propagating
spin-2 modes. Spin = field transformation at a point; scalar fields
have trivial transformation, hence spin-0 only.

CPU-121 numerically confirmed: ring-background mode count gives
cubic-symmetric degeneracies (1, 2, 1, 1, 1, 2) — scalar pattern, NOT
the uniform 2× polarization pairing that would signal emergent tensor.

LIGO/Virgo observe spin-2 tensor gravitational waves. To match, must
extend ontology.

### v11 definition

Add at each lattice node `n`:
- Symmetric traceless rank-2 tensor field `h_ij(n)`
- 5 free components per node (6 symmetric - 1 trace)

### v11 Lagrangian

```
L_h = (1/(2 μ_h)) · |π_ij|²  -  (1/4 μ_h) · |∂_k h_ij|² · c_g²
```

This is **linearized General Relativity in transverse-traceless gauge**
(Pauli-Fierz Lagrangian). Coupling to matter:

```
L_int = (8π·G/c⁴) · h_ij · T^TT_ij[matter]
```

### v11 properties (CPU-122 verified)

- **Massless dispersion**: ω² = c_g² · |k|²
- **Two TT polarizations** per wavevector (h+, h_x)
- **Spin-2 transformation**: π/2 rotation flips sign (e^{i 2θ} structure)
- **c_g = c_φ exactly** via DER-QNG-042 §3.3 (μ_h = μ_g = β_g·μ_φ/β_φ)
- **GW170817 consistent**: c_g/c_light < 10⁻¹⁵

### What v11 inherits

For static sources: `T^TT_ij = 0` → h_ij = 0. So all DER-QNG-068
phenomenology (Section 10) is preserved.

For dynamical sources (binary pulsars, GW): h_ij sourced by stress-energy,
gives quadrupole radiation formula:
```
P = (32/5) · G · μ²·a⁴·ω⁶ / c⁵  (Hulse-Taylor)
```

CPU-123: predicts -2.405×10⁻¹² s/s vs observed -2.398×10⁻¹² s/s (0.3%
match — but this is INHERITED from GR, not new prediction).

### Honest scope of v11

- It is **axiomatic addition** of linearized GR's tensor sector
- Lagrangian is **imported** from QED/lattice gauge theory (Pauli-Fierz)
- Coupling coefficient 8π is GR's convention
- The ONLY substrate-derived element: c_g = c_φ via DER-QNG-042 §3.3
- Hulse-Taylor 0.3% match is GR's prediction with QNG c, G, ℏ

This is legitimate theory construction (parallels Higgs). NOT a
derivation of gravitational tensor sector.

## v12: Spin-1 Photon Extension

### Motivation (Gap 15)

Theorem (CPU-135): pure QNG v10 has only scalar fields. φ has GLOBAL
U(1) symmetry but not LOCAL — gradients of scalar are curl-free
(gauge-trivial in EM sense). No vector field can host photon.

LIGO observation: matter and radiation interact electromagnetically.
To match, must add EM.

### v12 definition

Add gauge field on lattice EDGES (not nodes):
- A_{ij} ∈ ℝ on each directed edge (i, j)
- Anti-symmetric: A_{ji} = -A_{ij}
- 3L³ edge variables for cubic L³ lattice

Field strength on plaquettes: F_p = A_{ij} + A_{jk} + A_{kl} + A_{li}
(sum around 4-edge plaquette).

### v12 Lagrangian

```
L_A = (1/(2 μ_A)) · (∂_t A_{ij})²  -  (c_A²/(4 μ_A)) · F_p²
```

Standard compact U(1) lattice gauge theory (Wilson 1974).

Coupling to charged matter:
```
H_φ_v12 = -(β_φ/(2z)) · cos(φ_i - φ_j - e·A_{ij})
```

This is **minimal coupling** with elementary charge `e` (input parameter).

### v12 properties (CPU-136 verified)

- **Massless photon dispersion**: ω² = c² k²
- **Two transverse polarizations** per wavevector
- **Local U(1) gauge invariance**: φ → φ + α(x), A_{ij} → A_{ij} + (α_j - α_i)/e
- **c_A = c_φ = c**: structurally protected via μ_A choice

### Charge quantization (Gap 16, formal)

Compact U(1) theory: charges are quantized integer multiples of e.
For QNG vortex with phi-winding number N:
```
q = N · e
```

CPU-138: standard QNG ring has N=1, hence q = ±e.

### Retroactive validation: CPU-049

The earlier observation that "W+W+ rings repel, W+W- attract" was
interpreted as "phi-mediated chirality interaction" but is **structurally
identical to electromagnetic Coulomb force** under v12.

This is the ONLY example where v12 retrodicts existing data without
new fitting. Otherwise v12 is purely consistent (matches QED at
linearized level by construction).

### Honest scope of v12

- It is **axiomatic addition** of compact U(1) lattice gauge theory
- Lagrangian imported from Wilson 1974
- Coupling `e` is INPUT, not derived
- Fine structure constant α = e²/(4π·ε_0·ℏc) — input via e

Same status as v11: legitimate extension, not derivation.

## Pattern: v10 → v11 → v12

The progression:
- **v10** (substrate): scalar matter sector (σ_g, σ_m, φ, χ)
- **v11** (graviton): adds h_ij rank-2 tensor for spin-2
- **v12** (photon): adds A_{ij} edge gauge for spin-1

Each layer adds the MINIMAL field content needed for the corresponding
spin sector. This is a theory-construction PATTERN, not ad-hoc.

## Connection to Standard Model + GR

v10 + v11 + v12 give:
- Substrate matter sector (v10)
- Linearized GR (v11)
- Electromagnetism (v12)

Missing for full SM:
- Weak SU(2) — would require v13 or further extension
- Strong SU(3) — would require v14 or further
- Higgs mechanism — would require additional scalar field

These extensions follow the same pattern: add minimal field type for
each missing observable spin/symmetry. None are derived from substrate.

## What's still SUBSTRATE-DERIVED

Despite v11 + v12 being axiomatic:
- c, G, ℏ values still derived from v10 + Stability Principle
- All 8 predictions from Section 07-08 still hold
- Λ = 0 still structural

The axiomatic extensions ADD to the framework but don't override the
foundational substrate derivation.

## References

- DER-QNG-069 (Gap 12 statement)
- DER-QNG-071 (no-go theorem for spin-2 from scalars)
- DER-QNG-072 (v11 design)
- DER-QNG-076 (v12 design)
- DER-QNG-082 (DM no-go relating to v12 charges)
- CPU-122, CPU-136 (numerical verification)
- savant-physics-reviewer 2026-04-24 (independent audit of v11 axiomatic status)
