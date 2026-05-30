---
type: derivation
id: DER-QNG-099
title: QNG extensions roadmap — v13 strangeness + Faddeev fermion sector
status: SKETCH — analytical design for extensions toward SM majority
author: C.D Gabriel
date: 2026-05-30
upstream:
  - DER-QNG-098 (Hopfion = nucleon spectrum)
  - DER-QNG-091 (SM correspondence map)
---

# DER-QNG-099 — Extensions roadmap toward SM majority

## Context

DER-QNG-098 established Hopfion Q-ladder identifies the nucleon family
(5-6 baryons at <1% precision). For OTHER SM particle families:

- Strange baryons (Λ, Σ, Ξ, Ω): require strangeness quantum number
- Leptons (e, μ, τ, ν): require fermionic spin-1/2 structure
- Heavy mesons (J/ψ, B): require flavor sectors (charm, bottom)
- W, Z bosons: require SU(2) gauge
- Gluons: require SU(3) gauge

This document sketches the MINIMAL extensions needed for each family.
Goal: reach majority of SM particles in QNG.

## §1 — v13 Strangeness extension (priority HIGH)

### Motivation

The lightest strange baryon Λ(1116) doesn't fit Hopfion ladder:
- Λ/p = 1.189 — between Q=1 (1.0) and Q=2 (1.241) in QNG ladder
- No clean position in nucleon ladder

The pattern: SM strange baryons have IDENTICAL or near-identical
J^P as nucleon family but offset by ~178 MeV (Λ-p) per unit of S.

### Proposed structure

Add a new scalar field **σ_s(node)** representing strangeness density:
- σ_s = 0 at vacuum
- σ_s = 1 inside a "strange tube"
- σ_s ∈ [0, 1] range

Strangeness Hamiltonian addition:
```
H_s = β_s · σ_s² + κ_s · σ_s · (1 - cos(φ_s))
```

Where φ_s is a separate phase field for strangeness, and κ_s couples
σ_s to its phase.

Strangeness quantum number per soliton:
```
S = -∫ σ_s dV (negative because strange quarks have S = -1)
```

### Mass formula prediction

Lambda mass ≈ proton mass + strangeness energy:
- m_Λ = m_p + α_s × ∫σ_s² dV

For ∫σ_s² = 1 (single strangeness unit), α_s = 178 MeV calibration.

### Predicted strange baryons

| QNG configuration | SM particle | Predicted mass |
|---|---|---|
| Hopfion Q=1 + 1 σ_s unit | Λ | 938 + 178 = 1116 MeV ✓ |
| Hopfion Q=1 + 2 σ_s units | Ξ | 938 + 356 = 1294 MeV (vs 1315: 1.6%) |
| Hopfion Q=1 + 3 σ_s units | Ω | 938 + 534 = 1472 MeV (vs 1672: -12%) |

The Ω discrepancy suggests non-linear scaling (perhaps Σ × σ_s² instead
of linear).

### Implementation cost

- Add σ_s field to substrate: ~1 day coding
- Calibration via Λ mass: ~1 day
- Test against Σ, Ξ, Ω: ~1 week

**Potential gain**: ~8 strange baryons added (Λ, Σ±, Σ0, Ξ0, Ξ-, Ω-,
plus excitations).

## §2 — Faddeev n-field for fermions (priority HIGH)

### Motivation

QNG currently has only S¹-valued phi field. Topological invariants
limited to π_1(S¹) = ℤ (vortex winding).

For FERMIONIC spin-1/2 particles, need higher topology:
- π_3(S²) = ℤ (Hopf invariant) → Faddeev solitons
- Wess-Zumino term gives spin 1/2 naturally

### Proposed structure

Add a S²-valued field n(node):
- n is a unit 3-vector
- Parametrize as n = (sin θ cos φ_n, sin θ sin φ_n, cos θ)
- where θ, φ_n are new field components

Faddeev-Niemi Hamiltonian:
```
H_n = (1/2) ∑_<ij> (n_i - n_j)² + (λ/4) ∑_p F_ij²
```

Where F_ij = n · (∂_i n × ∂_j n) is the topological field strength.

### Hopf invariant

For closed Faddeev solitons:
```
Q_Hopf = (1/(4π²)) ∫ F · A d³x
```

where A is a gauge potential for F.

Vakulenko-Kapitansky bound:
```
H ≥ c × Q_Hopf^(3/4)
```

### Spin from Wess-Zumino

Adding WZ term:
```
S_WZ = (k/24π²) ∫ ε^μνρ tr(n ∂_μ n ∂_ν n ∂_ρ n) d³x dt
```

makes Q_Hopf-charged solitons fermions with spin J = k/2.

For k=1: J=1/2 (electron candidate).

### Predicted leptons

| QNG configuration | SM particle | Predicted relation |
|---|---|---|
| Q_Hopf = 1 ground state | electron? | m_e via Vakulenko-Kapitansky bound |
| Q_Hopf = 1 with internal excitation | muon? | factor ~207 above electron |
| Q_Hopf = 2 or higher | tau? | factor ~3477 above electron |

**Cost**: Implement Faddeev simulation (~2 weeks coding) + calibration
+ tests.

**Potential gain**: 3-6 leptons added (e, μ, τ, plus neutrinos if
neutral solitons allowed).

## §3 — Composite states (mesons)

### Light mesons via composite QNG

Mesons could be composite states of QNG objects:
- π+: (W+ ring) + (W- ring) ≠ neutron candidate (we found wrong mass)
- ρ0: (W+ ring) + (W- ring) at different angular momentum?
- η: composite at neutral configuration

The W+W- composite at D=10 gave 938 MeV (= neutron mass). At other
separations D=4-8 it gave 844-928 MeV.

If we vary the ANGULAR MOMENTUM of the W+W- pair (rotational state of
the composite), we might get different mesons:
- L=0: pion-like ground state
- L=1: ρ vector meson?
- L=2: ???

This requires identifying the rotational degrees of freedom and their
energies.

**Implementation**: ~1 week to test composite states with various
internal quantum numbers.

**Potential gain**: ~10-20 mesons (light + strange).

## §4 — W, Z bosons via v14 SU(2)

### Motivation

SM has SU(2)_L × U(1)_Y → SU(2)_em × U(1)_em after Higgs mechanism.
QNG has only U(1)_em via v12.

For W, Z, need non-Abelian gauge field with isospin structure.

### Proposed structure

Add **W_ij** field on edges (3 components, SU(2) gauge):
```
W_ij = W^a_ij τ^a (where τ^a are Pauli matrices)
```

Gauge-invariant kinetic:
```
F^a_p = ∂W^a + ε^abc W^b W^c
```

Coupling to matter via covariant phi gradient.

### Mass via Higgs-like mechanism

W, Z get mass from χ-VEV similar to SM Higgs:
- m_W ≈ g × <χ>
- For SM m_W = 80 GeV with g ≈ 0.65, need <χ> ≈ 246 GeV

Gap 13 mass-scale issue applies (Planck → 246 GeV).

### Cost and gain

- Implementation: ~1 month (complex)
- Calibration: substantial
- Gain: 2 particles (W±, Z) but completes electroweak sector

## §5 — Gluons via v15 SU(3)

Most complex extension. Requires implementing lattice QCD-like
dynamics with confinement. Quarks become QNG solitons in SU(3)-colored
field.

**Cost**: Years of work to do properly.

**Lower priority**: gluons are not "stable" in any normal sense (always
confined), and their identification in QNG would require massive
infrastructure.

## §6 — Neutrinos (most difficult)

Neutrinos require:
- Fermionic structure (Faddeev + WZ)
- AND neutral (forbidden by v12 charge-topology link)

Possible workaround: neutrinos are LIGHT Faddeev solitons with
ELECTRIC charge cancellation through composite structure (similar to
the W+W- neutron attempt).

Or: neutrinos are sterile (right-handed only) and don't couple to
the QNG charge structure at all.

**Status**: open theoretical problem.

## §7 — Priority ranking for autonomous extension

To reach SM "majority" (~25-30 particles) efficiently:

| Priority | Extension | Particles added | Cost | Cumulative count |
|---|---|---|---|---|
| 1 | Extend Hopfion ladder Q=6..15 at L=48 | 5-10 nucleon excitations | 30-50 min compute | 11-16 |
| 2 | v13 strangeness | 6-8 strange baryons | 1-2 weeks | 17-24 |
| 3 | Composite mesons | 10-20 light + strange mesons | 1 week | 27-44 |
| 4 | Faddeev fermions | 6 leptons | 2-4 weeks | 33-50 |
| 5 | v14 SU(2) for W,Z | 2 bosons | 1 month | 35-52 |
| 6 | v15 SU(3) gluons | 8 gluons (confined) | Years | 43+ |

**Target majority**: ~30 SM particles → reachable through priorities 1, 2, 3.

## §8 — Current autonomous run

CPU-175 (in progress): Phase 1 of priority 1, extending Hopfion ladder
to L=48 Q=1..15 + R variation. Expected to add 5-10 nucleon
identifications.

After CPU-175 completes:
- Document Q=6..15 identifications
- Test R variation for distinct families
- Move to priority 2 (v13 strangeness sketch in code)
- Continue until session "majority" target

## §9 — Implementation status

**Already done** (this session + DER-QNG-098):
- Hopfion ladder Q=1..5: nucleon family (5-6 particles)
- Foton, graviton: gauge bosons (2 particles)

**Total at session start of autonomous run**: ~8 particles

**Target**: ≥15-20 particles identified across families.

## §10 — Falsifiability

For each extension, well-defined falsifiers:

**v13 strangeness P_F**: if Λ mass ≠ proton + 178 MeV under QNG
strangeness mechanism, falsified.

**Faddeev fermion P_F**: if Hopf-charged solitons don't carry spin 1/2
via Wess-Zumino term, lepton mapping fails.

**Composite meson P_F**: if W+W- internal excitations don't give
standard meson mass ratios (π:ρ:K), falsified.

This roadmap is a HONEST plan, not a guarantee. Each extension may
fail. But the structure is clear and the priorities are ranked by
cost vs gain.
