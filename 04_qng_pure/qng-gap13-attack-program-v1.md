---
type: derivation
id: DER-QNG-077
title: Gap 13 attack program — scale separation Planck → MeV/GeV
status: CONCEPTUAL ANALYSIS — identifies candidate mechanisms, no full solution
author: C.D Gabriel
date: 2026-04-25
upstream:
  - DER-QNG-074 (Gap 13 statement)
  - DER-QNG-075 (Gap 14 lattice dependence)
---

# DER-QNG-077 — Gap 13 attack program

## The problem (recap)

QNG substrate operates at Planck scale via unit-bridge:
- Lattice spacing: a_L = 0.305 ℓ_Planck ≈ 5×10⁻³⁶ m
- Mass per node: a_M = 1.524 m_Planck ≈ 3.3×10⁻⁸ kg
- Time step: a_T = 0.033 t_Planck ≈ 1.8×10⁻⁴⁵ s

Observed particles at MeV-GeV scale:
- Electron: 0.511 MeV/c² ≈ 9.1×10⁻³¹ kg = 4.2×10⁻²³ × m_Planck
- Proton: 938 MeV/c² ≈ 1.7×10⁻²⁷ kg = 7.7×10⁻²⁰ × m_Planck

**Scale separation needed: 10²² to 10²³**.

This is the OBSTRUCTION. Without resolving it, QNG cannot make
quantitative particle predictions.

## Mechanisms in standard physics that bridge scales

Survey of how standard physics generates large/small scales:

### M1: Renormalization group (RG) flow

Couplings depend on energy scale via β-functions.
- Asymptotic freedom (QCD, non-Abelian): coupling DECREASES at UV, INCREASES at IR
- Asymptotic non-freedom (QED, Abelian): coupling INCREASES at UV, DECREASES at IR

For QNG: substrate (UV/short distance/Planck) → observation (IR/long distance/MeV).

If substrate parameter `g_UV` has β-function such that `g_IR / g_UV ~ 10⁻¹¹`,
mass scale would be `m_IR ~ g_IR² × m_UV ~ 10⁻²² × m_Planck` ✓

RG factor needed: 10⁻¹¹ in coupling. For one-loop:
```
g_IR² = g_UV² / (1 + β_0 g_UV² ln(M_UV/M_IR))
```

For ln(10²²) ≈ 50, β_0 g_UV² ≈ 10¹⁰ (huge). Doesn't work for usual β_0 ~ 1.

UNLESS β_0 is enormously enhanced — possibly from substrate-specific structure.

### M2: Dimensional transmutation

Coupling at UV runs to strong coupling at scale Λ_QCD-like via:
```
Λ = M_UV exp(-1/(β_0 g²(M_UV)))
```

For Λ/M_UV ≈ 10⁻²², need 1/(β_0 g²) ≈ 50.
With g²(M_UV) ≈ 0.1 (mild coupling), β_0 ≈ 0.2 — plausible for weakly-coupled gauge theory.

This is how QCD generates GeV scale from Planck input. The TRICK: the
coupling has running such that it explodes at IR, generating a NEW scale
naturally without fine-tuning.

**For QNG**: candidate sectors with this behavior:
- α (cosmological restoring constant): if α has running such that
  α_IR/α_UV ≈ 10⁻¹²², we'd recover the observed cosmological scale
- φ phase coupling β_φ: if asymptotically non-free, becomes strong at IR

### M3: Symmetry breaking + Higgs-like VEV

Spontaneous symmetry breaking generates scales via:
```
m_particle = y × <φ> ~ y × v
```

For electron: m_e = y_e × v with v=246 GeV, y_e ≈ 3×10⁻⁶.

Doesn't itself generate the v=246 GeV scale (that's an input). But
generates particle-mass HIERARCHY from Yukawa coupling differences.

For QNG: σ_m has VEV σ_ref = 0.5. Could generate masses if there are
analogs of Yukawa couplings. But why σ_ref = 0.5 and not 10⁻²² ?

### M4: Compactification / extra dimensions

KK reduction of 5D → 4D gives:
```
m_n = n / R
```

where R is compactification radius. If R is large (TeV⁻¹), gives TeV-scale masses.

For QNG: substrate is 3D cubic. If extra "implicit" dimension exists
with very large compactification, could give light masses.

But QNG was tested as "dimension-agnostic at linear level" (GPU-026).
No evidence for extra dimensions yet.

### M5: Compound objects / collective excitations

A single substrate quantum at Planck mass; a BOUND STATE could be lighter.

In condensed matter:
- Phonons: collective excitations of lattice atoms, much lighter than atomic mass
- Magnons, polarons, plasmons: collective modes
- Goldstone bosons: massless modes from broken symmetry (not light, but zero)

For QNG: φ-Goldstone modes are MASSLESS (XY symmetry global). They're
the photons we ALREADY have (also v12 photon is gauged Goldstone).

Could there be MASSIVE collective modes that are LIGHT compared to
substrate scale? Like plasma frequencies in solid?

In XY model, the spin-wave frequency is ω(k) ~ √(β/μ) k for small k.
Lowest non-zero mode: k_min = 2π/L. Frequency: ~√(β/μ) × 2π/L.

In thermodynamic limit L → ∞: ω → 0. So lowest mode is gapless.

For finite L, ω_min sets a "mass gap". On L=20: ω_min ~ √(0.06/0.857) × 2π/20 = 0.026 (natural). In SI: ω/a_T = 0.026/1.8e-45 = 1.4e43 Hz. Energy: ℏω = 0.026 × 0.233 = 6×10⁻³ (natural) = 6×10⁻³ × E_Planck = 6×10¹⁶ GeV. STILL Planck-scale.

So finite-L modes don't give MeV scale.

### M6: Tunneling / instanton effects

In QFT, instanton contributions to mass can be exponentially suppressed:
```
m_inst ~ M_UV × exp(-S_inst/ℏ)
```

For S_inst ~ 50 (in units of ℏ), m_inst/M_UV ~ exp(-50) ~ 10⁻²² ✓

This is the right magnitude!

For QNG: if some massive bound state has formation action S ≈ 50 ℏ_QNG,
its quantum mass would be Planck × exp(-50) ≈ MeV. EXACT scale.

This is interesting. Need to compute action of relevant configurations.

For a vortex ring of mass M_ring × t_lifetime, action S ~ M c² t.
For a stable ring in v8 with lifetime ~ T_orbital ~ 200 lu:
S ~ M_ring × c_phi² × 200 ~ 729 × 0.012 × 200 ~ 1700 (natural)

In ℏ units: S/ℏ = 1700 / 0.233 ≈ 7300. 

Tunneling factor exp(-7300/2) — utterly negligible. So ring instanton
contribution is negligibly small mass.

So instantons don't help.

### M7: Conformal anomaly / scale generation from dimensionless couplings

In conformal field theories, scales emerge from dimensionless inputs via
trace anomalies. This is closely related to dimensional transmutation.

Maybe: QNG's substrate parameters β, μ are dimensionless; observed scales
emerge from their RATIOS through anomalies.

But this requires conformal symmetry of substrate (broken by lattice spacing).

## Proposed mechanism for QNG (working hypothesis)

**Hypothesis**: Gap 13 is solved via DIMENSIONAL TRANSMUTATION (M2)
applied to the cosmological coupling α.

```
α_substrate = 0.005 (input)
α_observed = α_substrate × exp(-1/(β_α × something))
```

If β_α is small enough, the exponential suppression generates the
22-order gap naturally.

Concretely: if QNG α has RG flow with β-function:
```
β(α) = -β_0 α² + O(α³)
```

at one loop, with β_0 ~ 0.05 (small coefficient), then:
```
α(M_IR)/α(M_UV) = 1/(1 + β_0 α(M_UV) ln(M_UV/M_IR))
```

For ln(M_Planck/M_observed) ≈ 50, β_0 ≈ 0.05, α(M_UV) = 0.005:
α(M_IR) ≈ α(M_UV) / (1 + 0.05 × 0.005 × 50) = 0.005 / 1.0125 ≈ 0.0049

NOT 22 orders of magnitude. Standard one-loop running doesn't work.

For exponential suppression (dimensional transmutation): need DIFFERENT β-function structure.

Actually for Λ_QCD / M_UV = exp(-1/(β_0 g²(M_UV))):
With g² = 0.1, β_0 = 0.5: exp(-20) ≈ 2×10⁻⁹. Only 9 orders.
With g² = 0.05, β_0 = 1: exp(-20). Still only 9 orders.
For 22 orders: need 1/(β_0 g²) ≈ 50. So β_0 g² = 0.02.

Plausible for weakly coupled, large-N theories.

## Concrete program of investigation

This document IDENTIFIES the candidate mechanisms but does not solve
Gap 13. The full attack requires:

### Step A1: Compute QNG β-functions

For each substrate coupling (β_φ, β_g, μ_φ, α, CHI_REL, CHI_DECAY):
- Identify dimensionless coupling in continuum limit
- Compute one-loop β-function
- Check if any exhibits dimensional transmutation

### Step A2: Look for natural dimensional transmutation candidates

In QNG:
- α coupling is closest analog to a "running cosmological constant"
- φ coupling could exhibit XY-model-style critical behavior
- σ_g coupling could give gravity running (asymptotic safety analog)

For each, compute β-function and check exponential factor.

### Step A3: Identify particle-mass scale generation

Once one substrate coupling generates a new scale Λ via dimensional
transmutation, particle masses arise from:
```
m_particle = c_substrate × Λ_generated × O(1) factor
```

Match Λ_generated to observed particle scales (MeV for leptons, GeV for hadrons).

### Step A4: Test phenomenological consequences

Once scale separation is plausible, redo:
- DER-QNG-038 baryon ladder under proper RG-corrected calibration
- Electron mass identification under v12
- DM mass spectrum

## Estimated effort

Steps A1-A4 are SUBSTANTIAL theoretical work:
- A1: 2-4 weeks (compute β-functions for QNG)
- A2: 1-2 weeks (identify which coupling has the right structure)
- A3: 1-2 weeks (link to particle masses)
- A4: 2-4 weeks (verify observationally)

Total: 6-12 weeks of focused theoretical work.

This is much heavier than any previous QNG investigation.

## What this means for Paper 1-4

Until Gap 13 is solved:
- Paper 1 (ℏ): UNAFFECTED — substrate-derived constant
- Paper 2 (Λ=0): UNAFFECTED — structural
- Paper 3 (framework): includes Gap 13 as honest open program
- Paper 4 (Yukawa): MAJOR REVISION — BAO failure linked to Gap 13

If Gap 13 is solved (via dimensional transmutation):
- Paper 4 could potentially be VALIDATED — α(IR) emerges naturally
- Particle ID becomes possible
- DM scale could be derived

## Honest pause

This document is an INITIAL CONCEPTUAL ANALYSIS of Gap 13. Full attack
requires substantial follow-up work (months). The theoretical machinery
needed (RG flow, dimensional transmutation in lattice substrate) is not
yet developed in QNG.

For now, Gap 13 remains OPEN HIGH. The theory is at a stage where
substrate constants are derived, structural extensions exist (v11, v12),
but quantitative phenomenological match to particle physics requires
mechanism that bridges 22 orders of magnitude.

Recommended next session priorities:
1. Compute β-function of α coupling (Step A1, narrowed)
2. Or shelf Gap 13 and continue with empirical validations of solid claims
3. Or write Paper 5 covering v11+v12 extensions properly

This concludes the EM + DM + Gap 13 exploration session of 2026-04-25.
