# 15. Quantum Gravity Predictions from QNG

Consolidates QG-specific predictions of QNG that distinguish it from:
- Standard EFT of gravity (Donoghue program)
- String theory
- Loop quantum gravity (LQG)
- Causal dynamical triangulations (CDT)
- Asymptotic safety (Reuter-Weinberg)

## QNG Quantum Gravity Status

### What QNG GIVES at Quantum Gravity level

After quantizing v11 (Section 13) + matter coupling (Section 14):

1. **Massless spin-2 graviton** with 2 TT polarizations (matches all observations)
2. **Newtonian potential** at tree level (V = -GM/r recovered)
3. **Donoghue 1-loop correction** at macroscopic distances (matches EFT)
4. **Specific UV cutoff** at lattice scale a_L = 0.305 ℓ_Planck
5. **Lattice corrections** to graviton propagator at high k

### What QNG DOES NOT GIVE

- Full non-linear GR (still linearized only)
- Black hole microstate counting (just upper bound from horizon area)
- Explicit dimensional transmutation to MeV/GeV (Gap 13)
- Hidden gauge sectors (SU(2), SU(3))

## Distinguishing QNG from competitors

### QNG vs Standard EFT of Gravity (Donoghue)

| Feature | EFT (Donoghue) | QNG |
|---|---|---|
| Newton recovery | ✓ tree level | ✓ tree level |
| Donoghue 41/10π | parameter-free | parameter-free at macro |
| UV cutoff | arbitrary (typically Planck) | **specific: a_L = 0.305 ℓ_P** |
| Sub-Planck physics | undefined (EFT breaks) | **lattice substrate** |
| Renormalizability | non-renormalizable | UV-completed by lattice |

**QNG-unique**: specific cutoff scale, NOT just "around Planck".

### QNG vs String Theory

| Feature | String theory | QNG |
|---|---|---|
| Number of dimensions | 10 (SUSY) or 26 (bosonic) | 3+1 (matches observation) |
| Compactification | required | not needed |
| Free parameters | many (vacua landscape) | 4 substrate params |
| BH microstates | string-state counting | **substrate site counting (~135)** |
| UV completion | string oscillators | lattice cutoff |
| Fundamental scale | string length l_s | a_L = 0.305 ℓ_P |

**QNG-unique**: 4 input parameters vs 10⁵⁰⁰ landscape; specific BH count.

### QNG vs Loop Quantum Gravity (LQG)

| Feature | LQG | QNG |
|---|---|---|
| Spin networks | yes, evolves via spin foams | not applicable; cubic lattice |
| Discrete area | √(j(j+1))·8πℏG/c³ spectrum | A in units of a_L² |
| Lorentz invariance | spinfoam constructed to preserve | lattice anisotropies expected |
| Continuum limit | semiclassical states (Heisenberg-Weyl) | thermodynamic L→∞ limit |
| Numerical results | spin-foam state sums | substrate field simulations |

**QNG advantage**: simpler ontology, more immediate numerical access.
**LQG advantage**: built-in Lorentz invariance via spinfoam structure.

### QNG vs Causal Dynamical Triangulations (CDT)

| Feature | CDT | QNG |
|---|---|---|
| Lattice type | random simplicial | regular cubic |
| Geometry | dynamical (triangles can move) | fixed lattice |
| Dimension | emergent (4D from random) | 3D substrate (input) |
| Phase structure | rich phase diagram | single phase (cubic XY) |

**QNG choice**: regular cubic for tractability; emergent dimension is
not addressed (substrate is 3D by construction).

### QNG vs Asymptotic Safety (Reuter)

| Feature | Asymptotic Safety | QNG |
|---|---|---|
| RG flow | UV fixed point (non-trivial) | classical α not running (CPU-141) |
| Predicted constants | derived from RG flow | derived from substrate axioms |
| Renormalizability | controlled by fixed point | UV-completed by lattice |
| Free parameters | RG-fixed | substrate parameters input |

**QNG difference**: derives constants from substrate algebra, not from
RG flow. CPU-141 verified classical α is L-independent (no flow).

## Quantum Gravity predictions (summary)

| # | Prediction | Source | Testability |
|---|---|---|---|
| QG-1 | Spin-2 graviton, 2 TT polarizations | v11 design | LIGO-confirmed (already) |
| QG-2 | c_g = c_φ = c exact | DER-QNG-042 §3.3 | GW170817 (10⁻¹⁵) |
| QG-3 | Newtonian potential V = -GM/r | tree level | Solar System (passed) |
| QG-4 | Donoghue 41/10π × Gℏ/(c³r²) | matches QFT | future precision tests |
| QG-5 | UV cutoff at a_L = 0.305 ℓ_P | substrate scale | future technology |
| QG-6 | Lattice correction ∝ (a_L/r)² | propagator structure | sub-Planck scales |
| QG-7 | Planck-mass BH = 135 substrate sites | horizon counting | numerical lattice QG |
| QG-8 | Λ = 0 exactly | Stability Principle | observational bound |
| QG-9 | Black hole singularity regularized | lattice cutoff | sub-Planck BH dynamics |
| QG-10 | Non-Lorentz-invariant at lattice scale | cubic lattice | future tests |

## Key NEW QNG predictions (not in other frameworks)

### Most testable in principle:
**QG-7**: Planck-mass BH has ~135 substrate microstates.
- String theory: depends on compactification, ~e^A/4 generally
- LQG: discrete area, but different prefactor
- QNG: SPECIFIC NUMBER 135

If lattice QG simulations match QNG's 135 best, supports QNG.

### Most theoretically interesting:
**QG-9**: BH singularity regularized at substrate scale.
- Standard GR: singularity at r=0
- String theory: fuzzball-like resolution at horizon
- LQG: discrete area limits
- QNG: lattice cutoff inside r < a_L

### Most observationally accessible:
**QG-8**: Λ = 0 exactly. Tighten bound from current 10⁻¹²² to ideally < 10⁻¹⁰⁰.

## Lorentz invariance status

**Status**: QNG has cubic lattice, which BREAKS continuous Lorentz
invariance at lattice scale.

**Mitigation**:
- At low momenta (`k << 1/a_L`), Lorentz invariance approximately
  recovered (continuum limit)
- Anisotropies become measurable at scales `k ~ 1/a_L ≈ 10/ℓ_P`
- For all current experiments, Lorentz invariance is preserved to
  precision available

**Comparison**: LQG, CDT also have lattice-induced LI breaking.
String theory has built-in LI but at cost of extra dimensions.

QNG explicitly accepts this trade-off: lattice is fundamental;
LI breaking is sub-Planck and doesn't conflict with observation.

## Future research lines

For making QG predictions concrete:

### Line A: Numerical QG on QNG lattice
- Simulate gravitational physics on small QNG lattice
- Verify Newton's law numerically
- Measure Donoghue-like quantum corrections
- Compare with continuum EFT

### Line B: Lattice corrections to BH thermodynamics
- Compute Hawking spectrum on QNG substrate
- Test if it deviates from continuum at high k
- Specific signatures distinguishable from other QG theories

### Line C: Connect to observation
- BBN bounds on c, ℏ time-variation
- Cosmic ray observations of LI breaking at high E
- LIGO future precision on GW polarization

## Status

This document consolidates QG predictions from clean QNG foundation.

**LOCKED**:
- Spin-2 graviton (axiomatic via v11)
- Tree-level Newton (consistent)
- Substrate UV cutoff (specific number 0.305 ℓ_P)
- Λ = 0 (Stability Principle)

**SKETCHED but not computed**:
- Modified Donoghue coefficient
- BH spectrum modifications
- Loop corrections specific to QNG

**OPEN**:
- Non-linear gravity completion
- Specific BH interior physics
- Hidden gauge sectors

## References

- DER-QNG-072 (v11 spin-2)
- Donoghue 1994 (EFT of gravity)
- Bjerrum-Bohr et al. 2003 (refined EFT)
- Reuter-Weinberg asymptotic safety
- Section 13 (this folder): quantization
- Section 14: matter coupling
