# QNG Gap 7: Wave-Matter Compatibility

Type: `note`
ID: `NOTE-QNG-017`
Status: `open`
Author: `C.D Gabriel`
Date: `2026-04-07`

## Summary

CPU-056 identified a structural conflict in the QNG substrate:

- **Channel G** (sigma_i += k_back × chi_i) is REQUIRED for the Klein-Gordon wave
  equation (DER-QNG-028/030) and is the foundation of v6 / Lorentz covariance.
- **Channel G** is INCOMPATIBLE with stable vortex rings at any k_back >= 0.002.
  Stability threshold: k_back < 0.0015.
  All physically relevant k_back values (wave equation requires k_back ~ 0.10+) are
  10-100x above this threshold.

The substrate cannot simultaneously support:
  (a) propagating Klein-Gordon waves (wave-like matter, Lorentz sector)
  (b) stable vortex rings as localized particles (matter sector)

This is **Gap 7**.

## Physical root cause

The chi field at the ring core is large: chi_core ~ 10-12 (maintained by DELTA
coupling — sigma depletion drives chi positive). Channel G feeds chi back into sigma:

  sigma_i += k_back × chi_i

At the ring core, chi_core > 0 → Channel G RESTORES sigma toward sigma_ref.
This directly opposes Channel F (which depletes sigma at the ring core).

Stability requires: Channel F depletion > Channel G restoration
  gamma_phi × D_core × sigma_core > k_back × chi_core
  0.10 × 0.55 × 0.27 ~ 0.015 > k_back × 10
  → k_back < 0.0015

Wave equation requires: k_back ~ chi_rel/6 × v²/c² ≈ 0.01–0.10.

The two requirements are incompatible in the current v5/v6 architecture.

## Einstein's deeper question (2026-04-07)

The conservative Hamiltonian H = T + E is evaluated on the v5 ring state
(CPU-057 snapshot protocol), but the v5 ring is an attractor of a DISSIPATIVE
system. The question is whether the conservative H dynamics admits stable
solitonic excitations at all.

**Derrick's theorem argument (3D):**

For a ring of radius R in the substrate:
  T ~ k_back/2 × sum_chi² ~ R² (chi_rms ~ R, confirmed CPU-058)
  E_ring ~ -B × R (phi gradient energy scales with ring circumference)

  H(R) ~ A × k_back × R² - B × R

  dH/dR = 2A × k_back × R - B

  → dH/dR = 0 at R_eq = B/(2A × k_back)

This suggests there IS an equilibrium ring radius R_eq for fixed k_back.
BUT: whether this is a stable minimum (d²H/dR² > 0) or unstable depends on
full dynamics including phi field radiation.

In pure conservative dynamics (no Channel F), the XY-like phi field will
radiate spin waves and the ring will shrink. This is analogous to vortex ring
decay in superfluid dynamics (Kelvin waves → phonon radiation → ring shrinkage).

## Resolution paths

**Path A: Separation of scales**
If the ring radius R is much larger than the chi correlation length (1/chi_decay),
and k_back is small, the two sectors (wave propagation / ring stability) may
be approximately decoupled. Need: k_back_wave << k_back_ring_kill.
From analysis: k_back_kill ~ 0.0015, k_back_wave ~ 0.01. Factor of 7 short.
Increasing chi_decay would reduce chi_core and relax k_back_kill — but chi_decay
controls chi lifetime and affects KG mass.

**Path B: Different ring topology**
The v5 ring uses Channel F (phi disorder) for stability. A different ring type
with NEGATIVE chi_core (sigma above sigma_ref inside ring) would not be destroyed
by Channel G. This requires a new ring-initialization protocol or a different
substrate topology.

**Path C: Different conservative structure**
The conservative dynamics could be modified so that the ring is a GENUINE
soliton of H — i.e., a stationary point of H under the ring's topological
constraint. This requires a different kinetic term T or additional conserved
charge that provides topological stability (Skyrme-like mechanism).

**Path D: Two-field substrate**
Introduce two sigma-like fields: one for the gravitational sector (sigma_g,
supports wave propagation) and one for the matter sector (sigma_m, supports
ring stability). This separates the two competing requirements but adds
significant complexity to the substrate.

## What must be tested next

**CPU-059 (designed):** Take pre-formed v5 ring, switch to pure Hamiltonian
conservative dynamics (no dissipation — no Channel A, no Channel F, no chi_decay),
observe ring lifetime under conservative flow.

Expected: ring dissolves in O(100-500) Hamiltonian steps as phi field radiates
and chi field spreads. This would confirm the ring is NOT a soliton of H.

If ring survives: surprising finding, requires re-examination of Derrick argument
for the full H including phi + chi_rel + delta cross-terms.

## Dependencies

- DER-QNG-028: KG wave equation derivation (v6 requires Channel G)
- DER-QNG-032: H = T + E Hamiltonian
- CPU-056: Channel G kills ring (k_back < 0.0015 required for stability)
- CPU-057: snapshot H on v5 ring — positive mass confirmed
- CPU-058: H ~ R², pion/proton ratio at R=2/R=5 (1% match)

## Status

| Item | Status |
|------|--------|
| Gap 7 identified and documented | DONE (this note) |
| CPU-059 — conservative dynamics ring test | PENDING |
| Path A analysis (separation of scales) | OPEN |
| Path B — negative chi ring | OPEN |
| Path C — topological soliton design | OPEN |
| Resolution of Gap 7 | OPEN |
