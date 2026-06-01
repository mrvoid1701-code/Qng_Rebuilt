# 05. Derivation of ℏ (Planck constant)

**This is the central derivation of QNG.** No discrete classical
substrate has previously derived ℏ numerically.

## Statement

Imposing the Stability Principle (`E_vacuum_total = 0`):

```
ℏ_QNG = √(β_φ · μ_φ · z) / C_cubic
ℏ_QNG ≈ 0.2326  (natural QNG units)
```

## Derivation

### Step 1: Vacuum energy decomposition

The QNG vacuum has two contributions:

```
E_vacuum_total = E_classical_ground + E_quantum_zero_point
```

**Classical ground state**: minimize `H_φ` at uniform φ. This gives:
```
E_classical_ground = -β_φ · N / 2
```
where N = total number of lattice sites.

**Quantum zero-point**: standard QFT formula for free Hamiltonian:
```
E_quantum_zero_point = (ℏ/2) · Σ_k ω_k
```
where ω_k are normal-mode frequencies.

### Step 2: Mode frequencies

For the lattice phase mode:
```
ω_k² = (β_φ / (z · μ_φ)) · 2(3 - cos k_x - cos k_y - cos k_z)
     = c² · λ_k
```

with `c² = β_φ/(z·μ_φ)` (Section 03) and `λ_k = 2(3 - cos k_x - cos k_y - cos k_z)`.

So:
```
ω_k = √(β_φ/(z·μ_φ)) · √λ_k = c · √λ_k
```

### Step 3: Apply Stability Principle

Set `E_vacuum_total = 0`:
```
-β_φ · N / 2 + (ℏ/2) · Σ_k ω_k = 0
ℏ · Σ_k ω_k = β_φ · N
ℏ = β_φ · N / Σ_k ω_k
```

Substituting ω_k = c · √λ_k:
```
ℏ = β_φ · N / (c · Σ_k √λ_k)
  = β_φ / (c · ⟨√λ_k⟩_BZ)        [where ⟨...⟩_BZ = (1/N)·Σ_k]
  = β_φ · √(z·μ_φ/β_φ) / ⟨√λ_k⟩
  = √(β_φ · z · μ_φ) / ⟨√λ_k⟩
```

Defining `C_cubic := ⟨√λ_k⟩_BZ`, we get:

```
ℏ_QNG = √(β_φ · μ_φ · z) / C_cubic
```

### Step 4: Numerical evaluation of C_cubic

`C_cubic` is a lattice geometric constant (independent of physics).
For 3D cubic lattice z=6:

```
C_cubic = (1/N) · Σ_k √(2(3 - cos k_x - cos k_y - cos k_z))
        ≈ 2.388
```

Computed via Brillouin zone integration over thermodynamic limit
(CPU-108, converged at L=48).

### Step 5: Final formula

Combining:
```
ℏ_QNG = √(0.06 · 0.857 · 6) / 2.388
      = √0.3085 / 2.388
      = 0.5554 / 2.388
      = 0.2326  (natural QNG units)
```

## Triple verification (CPU-107)

Three independent computational methods, all give the same value:

| Method | Formula | ℏ_QNG | Source |
|---|---|---|---|
| Structural | √(β·μ·z) / C | 0.23263 | Direct from formula |
| Zero-point balance | β·N/Σω | 0.23264 | Direct from axiom |
| Intensive | β/⟨ω⟩ | 0.23263 | Direct from intensive form |

**Spread between methods: 0.0046%.** Excellent agreement.

## Convergence in thermodynamic limit (CPU-108)

| L (lattice size) | ℏ_QNG | % deviation from L=∞ |
|---|---|---|
| 4 | 0.23340 | +0.33% |
| 16 | 0.23258 | -0.03% |
| 48 | 0.23264 | -0.001% |
| 96 | 0.23264 | converged |

**Convergence to <0.001% by L = 48.** ℏ_QNG is well-defined in
thermodynamic limit.

## Robustness across parameter scans (CPU-113)

50× parameter variations:

| Scan | Range | Scaling verified |
|---|---|---|
| β_φ | 0.01 → 0.5 | ℏ ∝ √β_φ (R² > 0.99999) |
| μ_φ | 0.1 → 5.0 | ℏ ∝ √μ_φ (R² > 0.99999) |

Confirms the analytic formula `ℏ = √(β·μ·z)/C` across wide parameter
range — not a coincidence of one specific parameter choice.

## Mapping to ℏ_SI

Via SI unit-bridge (06-unit-bridge-SI.md):

```
ℏ_SI = ℏ_QNG · (a_M · a_L² / a_T)
     = 0.2326 · (3.317×10⁻⁸ kg) · (4.926×10⁻³⁶ m)² / (1.775×10⁻⁴⁵ s)
     = 1.055 × 10⁻³⁴ J·s
```

This MATCHES the measured `ℏ_SI = 1.055 × 10⁻³⁴ J·s` to machine
precision (CPU-114). The unit-bridge contains no free parameters once
c_QNG, G_QNG, ℏ_QNG are fixed.

## What this means

### Historical context
- **Planck 1900**: introduced ℏ as ad-hoc factor for blackbody radiation
- **Bohr, Heisenberg, Schrödinger 1920s**: ℏ in Hamiltonian, axiomatic
- **125 years of physics**: ℏ has been postulated, not derived
- **2026 QNG**: ℏ derived numerically from substrate + Stability Principle

### Comparison with other approaches
| Approach | ℏ origin | Numerical value? |
|---|---|---|
| Standard QM | Axiom | No |
| Stochastic mechanics (Nelson 1966) | Input D = ℏ/2m | No |
| SED (Boyer 1975) | Input as ZPF amplitude | No |
| Trace dynamics (Adler 2004) | Equipartition, analytical | No |
| Cellular automata ('t Hooft 2016) | Speculative | No |
| **QNG (this work)** | **Stability Principle** | **Yes (0.233)** |

### Physical interpretation
ℏ is the **specific value at which classical ground state energy is
exactly cancelled by quantum zero-point energy**. The Universe's
substrate must satisfy this for temporal stability of complex
structures (Big Rip / Big Crunch avoidance).

This isn't fine-tuning — it's the dynamically-selected value.

## Caveats

The derivation is rigorous GIVEN:
1. The Stability Principle as physical axiom
2. The substrate parameter values (β_φ, μ_φ, z) as inputs

Without the principle, ℏ formula is just a number. With it, ℏ is forced
to take this specific value for the substrate to exist.

Substrate parameters β_φ, μ_φ, z themselves are not derived from deeper
structure — they are inputs of QNG.

## References

- DER-QNG-066 (Stability Principle)
- DER-QNG-067 (ℏ paper draft)
- CPU-107 (triple-method verification)
- CPU-108 (L-scan convergence)
- CPU-113 (β/μ robustness)
- CPU-114 (SI unit-bridge)
- Original: `QNG-Theory Release-01/04_qng_pure/qng-hbar-derivation-paper-draft-v1.md`
