---
id: qng-quantization-program-v1
type: note
status: open_program
version: 1
created: 2026-04-22
depends_on:
  - qng-emergent-noise-v1        # DER-QNG-023 (η derived from ring FDT)
  - qng-v8-canonical-extension-v1 # DER-QNG-042 (H_v8)
  - qng-einstein-correspondence-v1 # DER-QNG-044
  - project_gpu031f_orbital_attractor  # universal R-insensitive basin
  - project_gpu037_b1_expelled    # φ is NOT bound in σ_m wells
  - project_gpu038_particle_probe # this session — scalar + H stable + M_ring oscillates
---

# QNG Quantization Program (NOTE-QNG-016)

## Question

**Is the orbital attractor a particle, or merely a particle-*like* classical
pattern?**

After GPU-038, we have a concrete classical object:
- H_v8 is conserved to ~0.03% over 2000 lu
- L_z ~ 10⁻¹⁵ (machine epsilon) across all samples → **scalar**
- M_ring oscillates wildly (−44 to +1594) → NOT a clean rest mass
- The rest-mass observable is ⟨H_v8⟩, not ⟨M_ring⟩

This has the structure of a **classical limit cycle with mass, size,
dispersion, and gravitational coupling**. It does NOT have, by construction,
the structure of a quantum particle (wavefunction, ℏ, commutators,
statistics).

This note articulates the gap and proposes two programs to close it.

## What the orbital attractor HAS (classical particle structure)

| Property | Value in v8 | Classical analog |
|----------|-------------|------------------|
| Rest energy | ⟨H_v8⟩ ≈ const, very small drift | E_rest |
| Topological charge | M_ring (conserved by gradient-flow; oscillating in symplectic v8) | N, B, winding |
| Size | R_eff ~ 4-5 lu | classical radius |
| Dispersion | ω² = c_φ²k² + m² (KG, verified GPU-035) | relativistic particle dispersion |
| Gravitation | Shapiro +39% (DER-QNG-044) | T^μν sourcing geometry |
| Stability | Ciclic limit, 2000 lu, universal R-insensitive basin | soliton / breather |
| Spin | L_z ~ 10⁻¹⁵ | spin 0 (scalar) |

This matches **classical Klein-Gordon field theory on curved substrate**
— the simplest relativistic model of matter + gravity.

## What is MISSING (quantum structure)

1. **ℏ** — no action quantum anywhere in H_v8. Parameters are `g, μ_m, μ_φ,
   β_g, β_m, β_φ, K_BACK, CHI_DECAY` — none has dimensions of action.
2. **Wavefunction / probability amplitude** — v8 evolves deterministically
   under Yoshida4. No superposition, no Born rule.
3. **Commutators** — classical Poisson brackets {σ, π} = 1, not [σ, π] = iℏ.
4. **Statistics** — indistinguishability and (anti)symmetrization absent.
   GPU-032e W+W+ and GPU-032d W+W- both gave ~2× single-ring basin
   (no Pauli separation).
5. **Discrete excited spectrum** — GPU-037 C1 showed 3 peaks, but they are
   Fourier modes of the box dressed by the ring, NOT genuine excited
   states of a particle.

## Two programs to bridge the gap

### Program α: Emergent QM from substrate noise (η ↔ ℏ)

**Core claim**: the noise amplitude η derived in DER-QNG-023 from ring FDT
plays the role of ℏ in the emergent quantum description.

Foundations:
- `η_ring = sqrt(2·α·sqrt(α·(α+2β)))` — derived, not a free parameter
- η is intrinsic to the substrate geometry and dynamics
- Classical noise + ring FDT give rise to fluctuation relations that
  mimic Heisenberg on sufficiently coarse scales

Expected structure (Nelson-Bohm-like):
- Quantum states emerge as ensemble distributions of classical cycles
- Born rule = stationary distribution of stochastic cycle occupancy
- Heisenberg Δx·Δp ≥ ℏ/2 emerges as classical variance product bounded
  below by η

Test candidate `QNG-CPU-082` (fluctuation invariant):
- Thermalize v8 substrate at amplitude ε (small perturbation)
- Measure ⟨(Δπ_m)²⟩⟨(Δσ_m)²⟩ across multiple configurations
- Test if product is independent of configuration (⇒ universal substrate
  constant with dimensions of action²)
- Verify numeric value matches η² predicted by DER-QNG-023

**Success criterion**: product is universal to within ±10% across at
least 5 independent configurations.

**Failure consequence**: η is a local FDT artifact, not a fundamental
action scale; program α is dead, only program β remains.

### Program β: Canonical quantization above v8

Take v8 as background classical theory, quantize action-angle variables
(J, θ) of the orbital attractor directly:

- Orbital cycle has well-defined period T (~185 lu from GPU-031f)
- Action J = ∮ p dq over one cycle (can be computed from GPU-038 traces)
- Bohr-Sommerfeld: J_n = 2π·ℏ·(n + ½)
- If J comes out as a rational multiple of 2π·ℏ_postulated, n levels
  give a discrete spectrum of "excited orbital" states

**Success criterion**: the computed J is quasi-constant across cycles and
matches a rational multiple of an independently determined ℏ-scale.

**Failure consequence**: J varies too widely across cycles (like M_ring
did in GPU-038) and cannot be quantized cleanly; program β is artificial.

## Why program α is preferred

Program α **derives** ℏ from the substrate (η is derived, not postulated).
Program β **imports** ℏ from outside.

Philosophically, if QNG is a theory of quantum gravity from a substrate,
ℏ must emerge — not be assumed. DER-QNG-023 already made this possible at
the level of the ring. The missing step is showing that the same η plays
the role of an action quantum globally.

This is the same move Einstein made: he didn't postulate Brownian motion's
diffusion constant, he derived it from molecular fluctuations (FDT
precursor). Program α is the QNG analog of his 1905 Brownian derivation,
extended to explain quantum indeterminacy.

## Immediate next actions

1. Run `QNG-CPU-082` — measure ⟨Δπ²⟩⟨Δσ²⟩ fluctuation invariant across
   3-5 cached ring configurations and compare with η² predicted by
   DER-QNG-023
2. If PASS: pre-register `DER-QNG-048` formally identifying η ↔ ℏ
3. If FAIL or ambiguous: open `DER-QNG-049` for program β (canonical
   quantization of orbital action J)

## Relation to existing gaps

- **Gap 5 (cosmological α)**: if η ↔ ℏ, then α substrate parameter
  becomes related to fundamental quantum scale → potential link
- **Gap 6 (Lorentz → QM)**: resolving this program closes the
  classical-quantum chasm that sits orthogonal to DER-QNG-043
- **Gap 10 (dimension)**: 3D ring-as-particle is dead (GPU-028); program
  α may be dimension-robust if FDT is dimension-agnostic

## Open questions

1. What is the physical role of `pi_phi` fluctuations? — φ is the phase
   of a complex field; π_φ is its conjugate. Heisenberg relation should
   naturally involve (phase, number) uncertainty.
2. Does the sine-Gordon structure of V_couple produce soliton-antisoliton
   pair production that mimics QFT pair creation? — would unify matter
   and antimatter naturally.
3. Can the orbital attractor "emit" phonons (waves) — like photon
   emission from an atom? GPU-037 C1 suggests φ modes are global, but a
   localized emission test has not been done.
