---
title: 21. v13 — Fermion (spin-1/2) Extension for Leptons
status: AXIOMATIC extension following v11/v12 pattern; gives Dirac spinors for leptons
---

# 21. v13 — Fermion Extension

Following the pattern of v11 (spin-2 graviton) and v12 (spin-1 photon),
we add v13: a Dirac spinor field for spin-1/2 fermions (electrons,
muons, taus, and neutrinos).

## Pattern recognition

| Layer | Field added | Spin | Particle | Status |
|---|---|---|---|---|
| v10 | (σ_g, σ_m, φ, χ) scalars | 0 | substrate matter | LOCKED |
| v11 | h_ij rank-2 tensor (per node) | 2 | graviton | DRAFT axiom |
| v12 | A_ij rank-1 gauge (per edge) | 1 | photon | DRAFT axiom |
| **v13** | **ψ_n Dirac spinor (per node)** | **1/2** | **leptons** | **DRAFT axiom (new)** |

Each layer adds the **minimal field structure** needed for the
corresponding spin sector.

## v13 Definition

### Field

At each lattice node `n`, add a 4-component complex Dirac spinor:

```
ψ_n ∈ ℂ⁴
```

with components ψ_n^α (α = 1, 2, 3, 4 are spinor indices).

This adds **8 real DOF per node** (largest single addition so far).

### Lagrangian (Wilson lattice fermion)

```
L_ψ = i · ψ̄_n · γ^μ · D_μ ψ_n  -  m · ψ̄_n · ψ_n  +  L_Wilson
```

where:
- γ^μ are Dirac matrices (4 standard)
- D_μ = ∂_μ - i·e·A_μ (gauge-covariant derivative, couples to v12)
- m is the Dirac mass (input parameter)
- L_Wilson is the Wilson term to cure fermion doubling

### Wilson term (lattice technical detail)

Naive lattice fermions have **fermion doubling**: 2^d species per
expected, where d = spatial dimensions. For 3D substrate, 8 species
instead of 1.

Wilson 1974 solution: add term `r · a_L · ψ̄_n · ∇²_lattice · ψ_n`
(where r is Wilson parameter). This gives fictitious mass to doubler
modes, leaving only 1 physical species at low energy.

**Tradeoff**: breaks chiral symmetry explicitly. For QED, this is
acceptable (chirality emerges at low energy after fine-tuning of
counterterms). For weak interactions (chiral), it's harder.

Alternative: Staggered fermions (Kogut-Susskind), Domain wall
fermions, Overlap fermions (Neuberger). All have specific tradeoffs.

For QNG: choose Wilson fermions for simplicity in v13.

## Quantization

Spinor field with anti-commutator:

```
{ ψ̂_n^α, ψ̂_m†^β } = ℏ · δ_{nm} · δ^{αβ}
```

(Note: ANTI-commutator for fermions, not commutator. This implements
Pauli exclusion.)

Mode expansion:
```
ψ_n(t) = Σ_{k,s} (b_{k,s} u^s(k) e^{i(k·r_n - ω_k t)} + d†_{k,s} v^s(k) e^{-i(k·r_n - ω_k t)})
```

with b, d annihilation operators for particle and antiparticle, u/v
spinor wavefunctions, s = ±1/2 spin states.

## Spin-1/2 verification

Under spatial rotation by angle θ around axis n̂:
```
ψ → exp(-i·θ·n̂·S/2) ψ
```

where S is spin matrix. For 4π rotation: ψ → ψ (return to identity).
For 2π rotation: ψ → -ψ (sign flip — spinor characteristic).

This is the **defining property of spin-1/2**: requires 4π for full
return, gives -1 under 2π.

### Verification on lattice

For a Dirac spinor on cubic lattice:
- Number of independent components per k: 2 (after Dirac equation
  imposes 2-of-4 constraint)
- Spin: ±1/2 along motion direction
- Helicity: chirality eigenvalue (left/right)

Test: rotate ψ around z-axis by 2π. ψ should pick up factor -1.

## Coupling to v12 photon

The covariant derivative D_μ = ∂_μ - i·e·A_μ couples ψ to A_μ.

For QED-like dynamics:
```
S_QED = ∫ d⁴x [-(1/4)F_μν F^μν + ψ̄(iγ^μ D_μ - m)ψ]
```

Standard QED. On lattice, all standard QED phenomena emerge:
- Coulomb interaction (one-photon exchange)
- Electron magnetic moment g = 2 (to leading order)
- Anomalous magnetic moment α/(2π) at one loop
- Vacuum polarization
- Lamb shift contributions

These are well-known lattice QED results. v13 + v12 reproduces them.

## Mass spectrum

Dirac spinor has mass m_ψ = INPUT parameter (substrate constant).

Under unit-bridge: m_ψ_natural maps to m_ψ_SI. With substrate at
Planck scale (Gap 13), m_ψ would naturally be Planck-scale mass.

For electron: m_e_SI = 9.11×10⁻³¹ kg = 0.000511 GeV/c² ≈ 4.2×10⁻²³ × m_Planck.

Setting m_ψ_natural = 4.2×10⁻²³ would be **fine-tuning** of the same
order as the Higgs hierarchy problem. This is **Gap 13 in QNG**.

So v13 ALONE doesn't solve electron mass. Need:
- Either: mechanism to generate effective mass at MeV scale (running, etc.)
- Or: accept m_ψ as input (same as Yukawa coupling in SM)

## Lepton identification (with caveats)

If we allow mass as input, v13 immediately identifies:

| Particle | Spin | Charge (v12) | Mass | QNG status |
|---|---|---|---|---|
| Electron e⁻ | 1/2 | -e | 0.511 MeV | v13 ψ with m_ψ=0.511 MeV |
| Muon μ⁻ | 1/2 | -e | 105.7 MeV | v13 ψ' with m_ψ'=105.7 MeV |
| Tau τ⁻ | 1/2 | -e | 1.777 GeV | v13 ψ'' with m_ψ''=1.777 GeV |
| Positron e⁺ | 1/2 | +e | 0.511 MeV | antiparticle of electron |
| Neutrino ν_e | 1/2 | 0 | ~10⁻⁹ GeV | requires neutral fermion |

**Charged leptons**: directly identified as v13 spinors with appropriate
mass parameters. Charge ±e from gauge coupling to v12.

**Neutrinos**: spin-1/2 BUT charge 0. Cannot couple to v12 photon. Need:
- Either: separate neutral fermion field (Majorana-style)
- Or: weak interaction (v14 would need SU(2) gauge)

For v13 alone: charged leptons IDENTIFIED. Neutrinos open.

## Generation structure

Each generation has same charge structure but different mass.
Standard Model: 3 generations of fermions (electron-muon-tau).

**Why 3?** OPEN even in SM. Just an empirical fact.

For QNG: could be 3 generations of v13 spinors, with specific mass
parameters m_e, m_μ, m_τ.

Or: could be ONE spinor field with internal "generation index" structure.

Without deeper principle, generation count is INPUT.

## v13 caveats

Same as v11 and v12:

1. **Axiomatic addition** — not derived from substrate dynamics
2. **Lagrangian imported** from QED + Wilson lattice fermions
3. **Mass parameter input** — Gap 13 obstruction same as in SM Yukawa

But:
- Spin-1/2 structure is correct
- Couples consistently to v12 (giving QED)
- Pauli exclusion automatic (anti-commutator)
- Antiparticles included naturally (v in mode expansion)

## What v13 buys us

Adding v13:
- Identifies charged leptons (electron, muon, tau)
- Provides matter content for QED on lattice
- Enables Compton scattering, pair production, annihilation
- Gives lepton family structure

What it doesn't yet do:
- Derive masses (input only)
- Include neutrinos (need additional structure)
- Include quarks (need SU(3) — v14 or later)
- Address generation count (3 input)

## Verification needed

For v13 to be promoted to LOCKED:

1. Numerical check: Wilson fermion on QNG lattice, verify dispersion,
   spin-1/2 transformation
2. QED on lattice (v12 + v13): verify photon-electron interaction
3. Anomalous magnetic moment: should give standard QED result α/(2π)
4. Pair production/annihilation: photon → e⁺e⁻ kinematics correct

These are standard lattice QED tests with well-known results.

## Status

v13 is **DRAFT axiomatic extension** following v11/v12 pattern.

Adds spin-1/2 Dirac fermions to QNG. Identifies charged leptons:
electron, muon, tau via parameter input m_ψ.

Same status as v11 and v12: legitimate axiomatic extension matching
observation, NOT derivation from substrate.

After v13: QNG has spin-0 (substrate scalars) + spin-1/2 (v13) +
spin-1 (v12) + spin-2 (v11). All standard particle spin sectors
covered.

## Connection with the line of reasoning

User's framing: "linia aceea unde leam gasit" — the line where we
found photon and graviton.

The line is: **identify which spin sectors are missing → add minimal
field with that spin**. v11 added spin-2 (rank-2 tensor), v12 added
spin-1 (edge gauge), now v13 adds spin-1/2 (Dirac spinor).

Following this line consistently:
- v13 adds leptons (this file)
- v14 could add weak gauge SU(2) → W, Z bosons
- v15 could add strong gauge SU(3) → gluons, quark color
- v16 could add Higgs → mass mechanism for v13/v14 fields

Each step is AXIOMATIC EXTENSION, not derivation. But each gives more
particles.

## Honest scope

v13 is the natural next step. It DOES give us 3 charged leptons (or 6
including antiparticles). That doubles the QNG particle count from 2
(graviton + photon) to ~6 (+ e⁻, e⁺, μ⁻, μ⁺, τ⁻, τ⁺).

But:
- Masses are input (Gap 13)
- Neutrinos still open (need additional structure)
- Quarks open (need v14 with SU(3))
- Strong/weak forces open

QNG with v10+v11+v12+v13 is comparable to **QED + linearized GR**.
This is what working theoretical physicists call "Standard Model
matter sector minus quarks/weak/Higgs".

## Files referenced

- Section 11: v11 + v12 axiomatic extensions
- Section 19: particles ontology
- Section 20: research roadmap
- Wilson 1974: lattice gauge theory + fermions
- Standard QED textbooks for spin-1/2 properties

## References

- Wilson, K. (1974). "Confinement of quarks." Phys. Rev. D 10, 2445.
- Kogut, J., Susskind, L. (1975). Staggered fermions.
- Neuberger, H. (1998). Overlap fermions.
- Standard QED textbooks for Dirac spinor properties.
