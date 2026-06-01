---
title: 20. Research Roadmap — Finding Particles in QNG
status: ROADMAP — concrete path from current state to particle identification
---

# 20. Research Roadmap: Finding Particles in QNG

Given the current state (file 19 — particles are open program),
this document outlines the CONCRETE research path to unlock
particle identification.

## The blocking problem

Gap 13: scale separation Planck → MeV/GeV (22 orders).

Until this is resolved, NO QNG configuration can directly match SM
particle masses.

## Three parallel research lines

### Line 1: Quantum field theory at QNG substrate (most rigorous)

**Goal**: derive effective theory at hadronic scale by integrating
out high-energy substrate modes.

**Method**: Wilsonian renormalization group flow.

**Steps**:
1. Quantize all v10 fields canonically (already done for h_ij in v11)
2. Compute one-loop effective action for low-energy degrees of freedom
3. Identify which composite operators survive at hadronic scale
4. Match with SM particle structure

**Effort**: 6-12 months of focused theoretical work.

**Could deliver**: derivation of running couplings, mass scales, and
specific particle spectra.

**Tools needed**: lattice QFT software, Wetterich-style functional RG.

### Line 2: Multi-field bound states (intermediate)

**Goal**: find specific bound states of QNG fields that match SM.

**Method**: solve linearized field equations in non-trivial backgrounds.

**Steps**:
1. Take vortex ring or other background as seed
2. Compute coupled (σ_m, φ, χ) linearized eigenmodes
3. Identify bound states (localized + below propagation threshold)
4. Compute their quantum numbers (charge, spin, etc.)
5. Compare with SM particle table

**Effort**: 1-3 months.

**Could deliver**: specific candidate particles with computed
quantum numbers.

**Issue**: GPU-037 already showed phi expels from σ_m wells.
Combined fields may give different result, but unclear.

### Line 3: Topological charge classification (fastest first step)

**Goal**: classify all stable topological structures in QNG and
their charge content.

**Method**: enumerate topological invariants.

**Steps**:
1. Vortex rings (different R, twist) — done
2. Hopfions (Q=1, 2, ...) — partially done (CPU-066 to 072)
3. Skyrmion-like (would need extra ontology)
4. Linked vortex configurations
5. For each, compute charge under v12 and gravitational signature

**Effort**: 2-4 weeks.

**Could deliver**: complete catalog of QNG topological structures
with quantum numbers. Match candidates to SM particles.

**Already partially done**: vortex rings have charge ±N·e (v12).
Hopfions also charged. No neutral structures (DM no-go).

## Specific concrete tests possible NOW

These can be done in one session each (not multi-week):

### Test T1: Vortex ring excitation spectrum

For a stable QNG ring, compute spectrum of small fluctuations:
- σ_m oscillations (breathing, deformation modes)
- φ phase fluctuations
- Coupled (σ_m, φ) modes

Each mode = potential particle candidate (in non-quantitative sense
due to Gap 13).

**Status**: partially done (GPU-037 C1 showed 3 discrete peaks). Need
proper interpretation as candidate particles.

### Test T2: Charge content of all simple topologies

For:
- Vortex ring (different R)
- Hopfion (Q=1 base, Q=2 if exists)
- 2-ring bound states (W+W±)
- 3-ring bound states (different chiralities)

Compute charge under v12 for each.

**Status**: ring N=1 → q=±e done (CPU-138). Hopfion Q=1 → q=±e done
(CPU-143). Multi-ring partial.

### Test T3: Bound state attempt with HEAVIER source

GPU-037 used Gaussian phi in σ_m well (expelled).

What about phi in **σ_g well** (gravitational, not matter)? σ_g wells
arise from any matter source, not just σ_m vortex.

Concrete test: phi quantum on Schwarzschild-like σ_g background.
Does it have bound states?

**Status**: not tested. Could be done in 1-2 sessions.

### Test T4: χ excitation spectrum

χ has m_χ = √CHI_DECAY = 0.141 in natural units = ~10²² GeV/c² in SI.

If we could find LIGHT χ excitations (e.g., bound to specific
backgrounds where mass is renormalized down), they could be DM
candidates.

**Status**: untested.

## Realistic timeline

For QNG to have FULL SM particle identification:

| Goal | Time estimate | Probability of success |
|---|---|---|
| Substrate spectrum free-field (DONE) | done | 100% (locked) |
| Vortex topology charge content (DONE) | done | 100% (locked) |
| Multi-field bound state hunt (T1, T3, T4) | 1-2 months | 30% (most paths blocked) |
| Resolve Gap 13 via RG (Line 1) | 6-12 months | 30% (heavy theory) |
| v13 axiomatic extension (SU(2)/SU(3)) | 3-6 months to design | 70% (parallel of v11/v12) |
| Match SM masses quantitatively | 1-3 years (after Gap 13) | unknown |

## What's worth doing SOON

**Highest value, lowest effort**:
- T1 (vortex ring spectrum) — 1 session
- T3 (phi on Schwarzschild-like background) — 1-2 sessions
- T4 (chi excitations) — 1 session

**Highest value, multi-week**:
- Line 1 RG flow attack (Gap 13 resolution)
- Line 3 topology catalog (specific charge content)

**Highest value, axiomatic extension**:
- v13 design for SU(2) gauge field (would unlock W, Z bosons)
- v13 design for sterile neutral field (would unlock DM)

## Key insight from this analysis

The "particles open" status is NOT a unique QNG problem. Standard Model
itself has 19+ free parameters (Yukawa couplings, etc.). String theory
has 10⁵⁰⁰ vacua. LQG has dynamics issues.

**QNG's particle gap is at the SAME LEVEL as competitor frameworks.**

What QNG offers UNIQUELY (constants derived) is independent of particle
identification. Paper 1 + Paper 2 (ℏ + Λ=0) are publishable NOW.
Particles can come later.

## Strategic recommendation

For paper publication strategy:

1. **Submit Paper 1 (ℏ derivation) FIRST** — establishes priority
2. **Submit Paper 2 (Stability + Λ=0) SECOND** — foundational claim
3. **Paper 3 (framework)** — comprehensive review, includes honest particle status
4. **Paper 4 (Yukawa cosmological)** — needs major revision (BAO failed)
5. **Paper 5 (QG via v11)** — derived from theory-v2/files 11-15
6. **Paper 6 (Particles, future)** — after Gap 13 resolution

This sequencing ensures foundational claims (Papers 1-3) are out FIRST,
before the harder problems (Papers 4-6).

## Open invitation

For physicists reading QNG documentation: the particle problem is OPEN
and is a research opportunity. Concrete tests T1-T4 above could give
meaningful results in 1-2 months of focused work.

Anyone with substrate-quantum-field-theory experience could contribute
significantly to making QNG's particle identification rigorous.

This is HONEST scope. Not a failed program — an open one.

## What we ALREADY have (re-emphasized)

After all this analysis:

**Definitively QG content**:
- Quantized graviton (v11)
- Quantized photon (v12)
- Lattice UV cutoff at a_L = 0.305 ℓ_P
- All static-source GR phenomenology

**Particles framework** (substrate level):
- 4 scalar excitations from substrate
- Topological structures with quantized charges
- Mechanism for bound states (V_couple Jackiw-Rebbi)

**Particles SM-identification** (specific):
- Photon ✓
- Graviton ✓ (axiomatic)
- All others: OPEN program with concrete next steps

## References

- Section 19: ontological analysis of particle candidates
- DER-QNG-038 (retracted), DER-QNG-082 (DM no-go)
- GPU-035 (Jackiw-Rebbi), GPU-037 (Meissner expulsion)
- Standard Model literature for SM particle table
- This file: roadmap for forward research
