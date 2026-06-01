---
id: NOTE-QNG-015
type: note
title: phi field is Meissner-expelled from σ_m deficits — reversed Higgs analogy
status: draft
date: 2026-04-22
upstream:
  - 07_validation/audits/qng-v8-stability-probe-v1/e2_dispersion.log  # A2
  - 07_validation/audits/qng-v8-jackiw-rebbi-v2/report.json           # GPU-035 v2
  - 07_validation/audits/qng-v8-b1-sm-well-v1/report.json             # GPU-037 B1
---

# Claim

In the v8 canonical extension (DER-QNG-042) with V_couple = (g/2)·(σ_ref − σ_m)²·(1 − cos φ), the phi field is **expelled** from regions of σ_m deficit rather than bound to them. This falsifies the "phi bound-state in ring cavity" interpretation of DER-QNG-038's baryon ladder.

# Evidence

**GPU-035 v2** (uniform σ_m deficit, freeze_sm):
- m²_φ = (g/(2μ_φ))·Δ² verified at 0.02% precision for Δ = 0.1 and Δ = 0.2
- Dispersion relation ω² = c_φ²·k² + m²_φ verified at <2% across k = 0..π/2
- The Jackiw-Rebbi DISPERSION law is rigorously confirmed.

**GPU-037 B1** (Gaussian σ_m well, freeze_sm, Gaussian phi centered on well):
- Initial phi² retention inside ball r<4 = **93.9%**
- Final retention at T=400 lu = **3.5%** (96.2% decay)
- H drift = 1.0e-13 (machine precision)
- Verdict: B1_EXPELLED

# Why the well expels phi

The small-phi expansion of V_couple gives:

    V_couple ≈ (g/4)·Δ(x)²·φ²
    m²_φ(x) = (g/(2μ_φ))·Δ(x)²

Since Δ² ≥ 0 always, the effective mass m²(x) is a **positive BUMP** wherever σ_m deviates from σ_ref, not a well. The phi KG equation

    μ_φ·φ̈ = β·∇²φ − m²(x)·φ

has NO bound states for a potential that is +bumped everywhere (this is elementary quantum mechanics: no bound states in a repulsive potential). phi initially localized on the bump decays into radiating modes that escape to the m=0 exterior.

# Reversed Higgs / inverted Anderson–Meissner

In the standard Anderson–Higgs mechanism for superconductors:
- Order parameter has VEV `v` in the bulk superconductor
- Photon acquires mass `m_A ∝ v` inside the superconductor
- Magnetic field is expelled from the bulk (Meissner effect)

The QNG picture **inverts** this:
- Order parameter σ_m has VEV σ_ref in the **vacuum**
- phi is **massless** in vacuum, acquires mass **in deficit regions** (σ_m < σ_ref)
- phi is expelled from the deficit regions

In the QNG geometry, what plays the role of the "superconductor" is the **ring / defect**, not the vacuum. The vacuum plays the role of the "normal metal." So:

- Vacuum = normal (phi free, massless, wave-like)
- Rings = superconductor-analog (phi heavy, expelled)

# Implications

## Falsified: "particle = phi bound in ring"

The original DER-QNG-038 reading — baryon ladder R→{p, Δ, N*, Δ(1700)} via phi bound-state spectrum inside the σ_m well — is dead. phi cannot be bound there.

## Still alive: Jackiw-Rebbi dispersion law

m²(x) = (g/(2μ_φ))·Δ(x)² is rigorously correct. But it describes a **mass landscape**, not a trapping potential.

## New ontology candidate: gravitational refraction

The same mass bump that expels phi also **slows** transmitted phi waves. This matches the GPU-035 Shapiro delay (+39% through a ring). The ring acts like a medium with position-dependent refractive index for phi — gravitational lensing via classical wave optics, not via bound states.

In this picture:
- phi = a propagating wave field (analogous to photon)
- σ_m landscape = the "refractive medium" (analogous to a star's atmosphere)
- gravitational delay = Fermat's principle on the effective metric

## What IS a "particle" in v8?

Three open candidates, testable:
1. **Soliton of the coupled (σ_m, phi, χ) field** — extended structure with non-trivial topology and oscillation, whose rest energy equals its total H_v8. GPU-031f/g orbital attractor may be this object. Single attractor → universal "310 unit" mass, R-insensitive (consistent with GPU-031g).
2. **Coherent phi wavepacket in vacuum** — massless, photon-like quanta. Would predict massless "particles" only — can't explain nucleon masses.
3. **No localized matter in v8** — only extended field configurations. All "mass ladders" are topological charges (CPU-074 M_ring) without rest-mass interpretation.

Option 1 is the frontrunner but needs explicit confirmation via quantization-of-the-attractor.

## Water-vortex analogy: inverted

The user's intuition — "energy in the ring, gravity makes a well, something sits at the bottom" — does NOT hold literally. The phi field is pushed OUT of the deficit, not pulled in. A better analogy:

- Ring = bubble in water (region of low condensate density, like air)
- phi = water surface waves
- The bubble REFRACTS surface waves around it, does NOT trap them

Surface waves going past a bubble bend around it (Shapiro-like delay) but do not get stuck in the bubble. Matter localization, if it exists at all in v8, must be a property of the bubble itself (σ_m structure), not of what is "inside" it.

# Tests that discriminate

- **C1** (GPU-037 ring spectrum): in-progress. Predicts NO core modes, possibly surface modes at deficit boundary.
- **Soliton-quantization test** (future): measure mass, momentum, and angular-momentum operators on the GPU-031f orbital attractor; check if they are consistent with a single-particle state.
- **Far-field lensing re-test** (DER-QNG-044 far-field RULED OUT): revisit using refraction/Fermat picture instead of bound-state picture.

# References

- `DER-QNG-038` baryon ladder (topological charge, not rest mass after this note)
- `DER-QNG-042` v8 canonical extension
- `DER-QNG-043` Lorentz emergent
- `DER-QNG-044` Einstein correspondence suite
- `QNG-GPU-035` Jackiw-Rebbi dispersion PASS
- `QNG-GPU-037` B1 phi expulsion PASS
