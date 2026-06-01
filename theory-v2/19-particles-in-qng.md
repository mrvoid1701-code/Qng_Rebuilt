---
title: 19. What Are Particles in QNG?
status: HONEST framework — multiple candidate mechanisms documented; clean identification is OPEN
---

# 19. Particles in QNG: Ontological Analysis

Now that we have substrate-derived c, G, ℏ + Λ = 0 + GR static-source
correspondence + axiomatic v11/v12 extensions for graviton/photon, the
natural question: **what are particles in QNG?**

This document examines the candidate mechanisms HONESTLY, with their
current status and what would be needed to make them definitive.

## Free-field excitations at substrate level

Under v10 canonical quantization, each substrate scalar field has
quantum excitations. These are the FREE-FIELD particle candidates:

| Field | Excitation | Mass (free) | Status |
|---|---|---|---|
| σ_g | gravitational potential mode | massless (with α small) | Section 11: → graviton via v11 |
| σ_m | matter density mode | massless free | NOT identified with SM particle |
| φ | phase mode | massless Goldstone (free) | Bound states with V_couple |
| χ | responsiveness mode | m² = CHI_DECAY = 0.020 | macroscopic mass under unit-bridge (Gap 13) |
| h_ij (v11) | graviton | massless | spin-2 ✓ |
| A_ij (v12) | photon | massless | spin-1 ✓ |

The **bare substrate excitations** include graviton, photon, plus
4 scalar modes. These are NOT the particles of the Standard Model
(electrons, quarks, etc.) directly.

For SM particles to emerge, we need ADDITIONAL structure.

## Candidate mechanisms for SM particles

### Candidate A: Vortex rings as baryons

**Hypothesis** (was DER-QNG-038, now retracted):
- σ_m vortex ring with radius R = 4 → nucleon
- R = 5 → Δ(1232)
- R = 6 → N*(1520)
- R = 7 → Δ'(1700)

**Issues found** (Gap 13, Gap 14):
- Gap 13: scale separation ~10²² between substrate and hadronic scale
- Gap 14: M_ring ratios are L-dependent (lattice-finite-size)
- The `<1% match` at L=20 was finite-size coincidence, not structural

**Status**: RETRACTED. Vortex rings are likely NOT directly the SM
baryons.

### Candidate B: Jackiw-Rebbi modes in σ_m wells

**Hypothesis**: phi quantum bound states inside σ_m vortex profiles.

In V_couple = (g/2)(σ_ref - σ_m)²(1 - cos φ), expansion gives effective
phi mass:
```
m²_φ(r) = (g/(2 μ_φ)) · (σ_ref - σ_m(r))²
```

In a σ_m vortex ring, σ_m varies, hence m²_φ varies. Phi quantum has
position-dependent mass, suggesting bound states.

**GPU-035 verified** at 0.02% precision: m²_φ formula correct.

**Issue (GPU-037 Meissner)**: Gaussian phi initial condition in σ_m well
shows 96% expulsion in T=400. Phi field IS NOT bound to σ_m wells —
it's EXPELLED.

**Status**: phi-bound-states-in-rings hypothesis FALSIFIED via GPU-037.

### Candidate C: Multi-ring bound states

**Hypothesis**: 2 or more rings can form bound states (analogs of
mesons or baryons).

GPU-032 series tested:
- W+W- at d=4: unbound (transient binding only)
- W+W+ at d=4: unbound
- 3-ring +++ : anomalous "sub-single" result (interpretation unclear)

**Status**: simple multi-ring bound states NOT confirmed in v8 R1
dynamics. May exist at different parameters or topologies but not
demonstrated.

### Candidate D: Charge-bearing excitations under v12

**Hypothesis**: under v12 with U(1) gauge field, the substrate
configurations with phi-winding around vortex cores have integer
charge q = N·e.

These ARE topologically stable + electrically charged.

But:
- All such configurations have charge ±e or ±2e, etc.
- No neutral stable configurations (DM no-go DER-QNG-082)
- Mass scale is Planck (Gap 13)

**Status**: provides CHARGE QUANTIZATION but not specific particle
identification at correct mass scale.

### Candidate E: Quasi-particle excitations (collective modes)

**Hypothesis**: particles are COLLECTIVE excitations of the substrate,
analogous to phonons in solids.

In condensed matter, phonons are quasi-particles emerging from
collective lattice vibrations. They have specific dispersion, lifetime,
and interactions.

For QNG, similar approach:
- Phonon-like excitations of σ_m, φ, χ fields
- Spin-wave-like excitations
- Topological soliton-like excitations

**Status**: this is the cleanest theoretical framework but identifying
SPECIFIC SM PARTICLES with specific QNG quasi-particles requires
detailed dispersion analysis.

### Candidate F: Bound states in non-trivial backgrounds

**Hypothesis**: SM particles are bound states of multiple quanta in
NON-TRIVIAL substrate backgrounds (e.g., near vortex rings, around
gravitational sources).

This is similar to:
- Atoms = electrons bound to nucleus (background = Coulomb potential)
- Hadrons = quarks bound by QCD (background = gluon condensate)

For QNG:
- Particles = phi/σ_m quanta bound in collective σ_m or σ_g background

**Status**: COULD work but requires identification of specific
backgrounds and matching with SM particle properties.

## Why finding particles is HARD in QNG

The fundamental obstruction is **Gap 13 (scale separation)**:

- Substrate operates at Planck scale (a_L = 0.305 ℓ_P)
- Each lattice site has mass a_M = 1.524 m_Planck
- SM particles have masses MeV-GeV (10²² × smaller than Planck)

Without a mechanism that bridges this 22-order gap, NO QNG
configuration directly gives MeV-GeV particle masses. Any candidate
ends up at Planck mass scale.

**Possible scale-bridging mechanisms** (all open):
- Dimensional transmutation (analog of Λ_QCD): not yet derived
- One-loop quantum corrections: large but not specifically MeV-scale
- Cosmological evolution: parameters could effectively differ
- Hidden gauge sector: would require v13 extension

## Concrete framework for particle identification

For a SPECIFIC particle in QNG, we'd need:

1. **Background configuration**: which σ_m profile (ring, hopfion, etc.)
   does it live in?

2. **Quantum numbers**:
   - Charge q (under v12 U(1)): determined by phi-winding
   - Spin j: from polarization tensor structure
   - Other QNs (color, weak isospin): NOT yet in QNG

3. **Mass**: from bound state energy E_n in the background

4. **Stability**: lifetime against decay into other states

A specific particle would be labeled `(background, n, q, j, ...)`.

## Path forward: where to look

Given the issues with Candidates A-F, the most promising path:

### Path 1: Quantum vortex ring analysis (Candidate D + E combined)

Take a single QNG vortex ring (R=4 or other), apply v10 canonical
quantization to small fluctuations around it. Compute:
- Spectrum of σ_m + φ + χ excitations in ring background
- Their phi-winding numbers (charges)
- Their masses

This is computational. Could match (or not) specific SM particles.

### Path 2: Jackiw-Rebbi outside the ring (revised)

GPU-037 showed phi is EXPELLED from σ_m core. Maybe phi quanta are
TRAPPED OUTSIDE the ring (Meissner-style)?

Test: compute phi-bound-states with sigma_m profile having an EXCESS
(σ_m > σ_ref) rather than deficit. Different mass profile.

### Path 3: Multi-field bound states

Couple σ_m + φ + χ excitations and look for BOUND modes that match
SM particle properties.

### Path 4: Resolve Gap 13 first

Before any specific identification, understand how scale separation
works. If Gap 13 is closed (e.g., dimensional transmutation found),
then candidate masses fall into MeV-GeV range naturally.

## What's actually achievable now

In the current state (post-autonomous-block):

**Concrete things we can do**:
- Compute substrate excitation spectrum for free fields (analytical)
- Compute bound states of phi in given σ_m background (numerical, has been done partially)
- Verify charge quantization in v12 (CPU-138 done)
- Compute substrate-derived masses (would be Planck-scale, NOT SM)

**Things blocked**:
- Direct SM particle identification (Gap 13)
- Mass spectrum match with electron/proton (Gap 13)
- Yukawa-like couplings (no Higgs analog)

## Honest verdict

Particles in QNG are an **OPEN PROGRAM** at the level of specific SM
identification. The framework (substrate + v10/v11/v12) provides
HOOKS for particles to exist, but matching specific SM particles
to QNG configurations is blocked by Gap 13 + several falsified
candidates.

**What QNG genuinely DOES say**:
- Particles ARE substrate structures
- Their gravitational signature is via σ_g coupling
- Their electromagnetic charge is via phi-winding (v12)
- They live in some background configuration

**What QNG DOES NOT yet say**:
- Specific identification (which SM particle = which QNG configuration)
- Specific masses at MeV-GeV scale (Gap 13)
- Yukawa coupling structure
- Origin of generation structure (3 generations of quarks/leptons)

## Reframe: paper-level honesty

For paper publication, "particles in QNG" should be presented as:

> "QNG provides a substrate framework where particles are quantum
> excitations of the discrete graph substrate. The framework supports
> charge quantization (via v12 phi-winding), gravitational coupling
> (via σ_g), and a discrete spectrum of bound states. The specific
> identification of QNG configurations with Standard Model particles
> is an open program, blocked primarily by the scale separation
> problem (Gap 13: 22-order difference between Planck substrate scale
> and observed hadronic scale)."

This is honest. QNG provides the FRAMEWORK; specific particle ID
requires further work.

## Open questions specific to particle physics in QNG

1. **Why 3 generations?** Standard Model has 3 quark/lepton families.
   QNG would need to predict this from substrate structure.

2. **Quark confinement?** SU(3) gauge structure not in QNG yet
   (would need v13 with non-Abelian gauge).

3. **Higgs mechanism?** No analog in current QNG. Particle masses
   need different mechanism.

4. **Why these specific masses?** Electron 0.511 MeV, proton 938 MeV,
   etc. These specific values need substrate origin.

5. **Neutrino sector?** Nearly massless neutral particles. Could be
   QNG's sterile excitations? But sterile = not coupled to anything,
   so undetectable.

Each of these is a multi-week-to-multi-year research program.

## Status

After this analysis:
- **Particles in QNG = open program** (honest)
- Substrate framework supports particles existing (yes)
- Specific SM identification requires resolving Gap 13 + extensions
- v11/v12 already provide graviton + photon
- Higgs-like mechanism for mass generation: open

This is HONEST scope. Same level as:
- Standard Model: doesn't derive particle masses (Yukawa couplings input)
- String theory: claims to derive but landscape of 10⁵⁰⁰ vacua
- LQG: matter coupling generally hard

QNG is no worse than standard physics for not deriving particles.
Where QNG is BETTER: it derives c, G, ℏ which others don't.

## References

- DER-QNG-038 (retracted baryon ladder)
- DER-QNG-082 (DM no-go, related to particle structure)
- GPU-035 (Jackiw-Rebbi confirmed at 0.02%)
- GPU-037 (Meissner expulsion: phi NOT bound to σ_m wells)
- GPU-038 (orbital attractor is global, not particle)
