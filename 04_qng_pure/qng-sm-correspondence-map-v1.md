---
type: derivation
id: DER-QNG-091
title: Standard Model ↔ QNG correspondence map — auditing which SM particles QNG v10/v11/v12 can host today
status: ANALYSIS — comprehensive audit, identifies what is identified vs blocked vs structurally missing
author: C.D Gabriel
date: 2026-05-30
upstream:
  - DER-QNG-062 (v10 foundational, complex Psi + canonical operators)
  - DER-QNG-072 (v11 tensor extension, graviton)
  - DER-QNG-076 (v12 EM extension, gauge field A_ij)
  - DER-QNG-071 (no-go scalar substrate -> spin-2)
  - DER-QNG-074 (Gap 13 scale tension)
  - DER-QNG-075 (Gap 14 M_ring lattice dependence)
  - DER-QNG-077 (Gap 13 attack program)
  - DER-QNG-080 (classical alpha-running falsified)
  - DER-QNG-082 (DM no-go)
  - DER-QNG-083 (predictions from hbar)
  - DER-QNG-038 (baryon ladder, v7 — retracted under v8 orbital)
---

# DER-QNG-091 — SM ↔ QNG correspondence map

## §1. Purpose

The user question: *"can we derive particle masses from QNG, at least a
few families?"* — is the right strategic question, but it cannot be
answered until a prior question is closed:

> **Which QNG object corresponds to which SM particle?**

This document audits, family by family, what QNG v10/v11/v12 actually
identifies today, what is blocked, and by which obstruction. Without
this map, mass-derivation attempts have nothing to derive masses *of*.

This is NOT a derivation of particle masses. It is the prerequisite
audit that any mass-derivation program must rest on.

## §2. The v12 ontological constraint (load-bearing for everything below)

The single most important structural fact about QNG under v12 is the
**charge-topology link** established by DER-QNG-076 + DER-QNG-082:

> Every topologically stable field configuration in v12 carries
> electric charge q = ±N·e, where N is the phi-winding around the
> defect's stabilising loop.

Consequence:
- A configuration that is BOTH topologically stable AND electrically
  neutral is forbidden in v12 (DM no-go, DER-QNG-082).
- Neutral particles must be either composite (bound states of opposite
  charges) or require a v13 extension (new field beyond U(1)).

The photon and the (v11) graviton are exceptions because they are the
gauge fields themselves, not topological excitations of matter fields.

This constraint cuts the QNG candidate pool by roughly half compared to
SM expectations: half the SM particles are neutral.

## §3. The map

For each SM family the entries report:
- **QN required**: spin, charge, isospin, color, generation
- **QNG candidate**: explicit topological / dynamical object, or NONE
- **QN supplied**: which required quantum numbers the candidate carries
  naturally
- **Obstructions**: by class (see §5)
- **Verdict**: IDENTIFIED / PARTIAL / GAP-13-BLOCKED /
  STRUCTURALLY-BLOCKED / NONE

### 3.1 Gauge bosons (4 families in SM)

#### 3.1.1 Photon (γ)

| Field | Status |
|---|---|
| QN required | J=1, Q=0, massless, 2 polarizations, U(1) gauge boson |
| QNG candidate | Edge gauge field `A_ij` (v12) |
| QN supplied | J=1 ✓, Q=0 ✓ (gauge boson), massless ✓ (gauge invariance), 2 transverse polarizations ✓, c_γ = c_φ ✓ (protected) |
| Obstructions | NONE for QN structure. Coupling constant `e` is INPUT (Gap 9-analog). |
| **Verdict** | **IDENTIFIED** (v12) |

This is the ONLY SM particle currently identified at the structural
level in QNG without reservation.

#### 3.1.2 Graviton (g)

| Field | Status |
|---|---|
| QN required | J=2, Q=0, massless, 2 polarizations (TT) |
| QNG candidate | Tensor field `h_ij` (v11, DER-QNG-072) |
| QN supplied | J=2 ✓ (rank-2 symmetric traceless), Q=0 ✓, massless ✓, 2 TT polarizations ✓ |
| Obstructions | v11 is AXIOMATIC. The tensor field is added to the substrate, NOT derived from {σ_g, σ_m, χ, φ}. No-go theorem (DER-QNG-071) proves scalar substrate alone cannot host propagating spin-2. |
| **Verdict** | **PARTIAL** (kinematic identification works; ontological derivation does not) |

#### 3.1.3 W boson (W±)

| Field | Status |
|---|---|
| QN required | J=1, Q=±1, massive (~80 GeV), SU(2) gauge boson |
| QNG candidate | NONE |
| QN supplied | — |
| Obstructions | Class II (missing structure): QNG has only U(1) gauge field in v12. No SU(2) field. Requires v13 non-Abelian extension. |
| **Verdict** | **STRUCTURALLY BLOCKED** |

#### 3.1.4 Z boson (Z⁰)

| Field | Status |
|---|---|
| QN required | J=1, Q=0, massive (~91 GeV), SU(2)×U(1) mixed |
| QNG candidate | NONE |
| QN supplied | — |
| Obstructions | Class II (no SU(2)) + Class III (neutral stable forbidden, but Z is unstable so only Class II is decisive) |
| **Verdict** | **STRUCTURALLY BLOCKED** |

#### 3.1.5 Gluons (g_a, 8 colors)

| Field | Status |
|---|---|
| QN required | J=1, color triplet, SU(3) gauge bosons |
| QNG candidate | NONE |
| QN supplied | — |
| Obstructions | Class II: QNG has no SU(3) field. Requires v13 non-Abelian extension with N=3. |
| **Verdict** | **STRUCTURALLY BLOCKED** |

**Gauge boson summary**: 1 of 5 fully identified (photon), 1 partial
(graviton via axiomatic v11), 3 structurally blocked (W, Z, g).

### 3.2 Leptons (6 species: e, μ, τ, ν_e, ν_μ, ν_τ)

#### 3.2.1 Charged leptons (e⁻, μ⁻, τ⁻)

| Field | Status |
|---|---|
| QN required | J=1/2, Q=−1, no color, point-like at SM scale, three generations |
| QNG candidate | **NONE explicit**. Possible candidates (none demonstrated): (a) lone vortex line with phi-winding 1; (b) Hopfion Q=1 (CPU-069 + CPU-143: STABLE under v7 dynamics, charged ±e under v12); (c) "minimal" orbital attractor at R<3 (none constructed) |
| QN supplied (best case, Hopfion) | Q=±e ✓ (Wilson loop), J=? (Hopf invariant Q=1 may give J=1/2 via skyrmion-like spin-statistics but NOT derived in QNG), generations=? (no mechanism), m=? (Gap 13) |
| Obstructions | Class II (no fermion sector — spin-1/2 NOT derived); Class I (Gap 13 absolute mass). Three-generation mechanism unidentified. |
| **Verdict** | **NONE** (best candidate Hopfion has wrong spin or underived; no generation mechanism at all) |

**Note**: Under v8 orbital interpretation, ring solitons at R=3, 4, 5
were tentatively identified with hadrons (DER-QNG-038, since suspended).
None of these correspond to leptons. The simplest stable QNG object,
the R=4 ring, is too massive (M_ring=729) and topologically rich (ring
of finite radius) to be lepton-like (point-like at SM scale).

#### 3.2.2 Neutrinos (ν_e, ν_μ, ν_τ)

| Field | Status |
|---|---|
| QN required | J=1/2, Q=0, no color, very light (<eV), three generations, Majorana-or-Dirac unresolved |
| QNG candidate | NONE |
| QN supplied | — |
| Obstructions | Class II (no fermion sector) + Class III (neutral + stable forbidden in v12). Requires both v13 non-Abelian (for sterile neutrino-like) AND a fermion ontology. |
| **Verdict** | **STRUCTURALLY BLOCKED** |

**Lepton summary**: 0 of 6 identified.

### 3.3 Quarks (6 flavors × 3 colors = 18 particle species)

#### 3.3.1 All quark flavors (u, d, s, c, b, t)

| Field | Status |
|---|---|
| QN required | J=1/2, Q=±1/3 or ±2/3, SU(3) color triplet, six flavors, three generations |
| QNG candidate | NONE |
| QN supplied | — |
| Obstructions | Class II: fractional charges Q=±1/3, ±2/3 are forbidden by v12 charge quantization (Wilson loop integer). Color SU(3) absent. No fermion sector. Triple block. |
| **Verdict** | **STRUCTURALLY BLOCKED** |

**Quark summary**: 0 of 18 identified.

### 3.4 Hadrons (composite, illustrative subset)

#### 3.4.1 Proton (p⁺)

| Field | Status |
|---|---|
| QN required | J=1/2, Q=+1, baryon number B=+1, isospin I_3=+1/2, m=938 MeV |
| QNG candidate | Orbital attractor at R=4, L=20 (GPU-031f: ⟨M_ring⟩_t = +309.45, period 185.2 lu, duty 38.5%) |
| QN supplied | Q=+e ✓ (Wilson loop on phi-winding-1 ring), stable ✓ (orbital attractor confirmed). J=? (spin-1/2 not derived from ring topology). I_3=? (no QNG mechanism). m=? (Gap 13 blocks absolute scale; Gap 14 blocks lattice-size independence). |
| Obstructions | Class I (Gap 13 + Gap 14: cannot derive m=938 MeV; ratio match to other hadrons broken under v8 orbital — GPU-031g R5/R4=1.088 vs needed 1.310). Spin-1/2 derivation missing. |
| **Verdict** | **PARTIAL** — topological charge q=+e identified, scale and spin unsolved |

#### 3.4.2 Neutron (n⁰)

| Field | Status |
|---|---|
| QN required | J=1/2, Q=0, B=+1, I_3=−1/2, m=940 MeV |
| QNG candidate | NONE elementary. Possible composite: (proton-like ring W+) + (electron-like Hopfion W−) in bound state. CPU-050 showed W+W− has Lennard-Jones-like potential with equilibrium at d≈3λ — bound state exists structurally. |
| QN supplied (composite) | Q=0 ✓ (charge cancellation), stable ✓ at separation d≈3λ if bound-state lifetime > 15 min (UNDEMONSTRATED). B and I_3 not derivable until p, e identifications fixed. |
| Obstructions | Class III (no neutral elementary in v12); requires composite interpretation, which conflicts with SM where neutron is itself an elementary quark composite (udd) at much shorter scale than nuclear binding. |
| **Verdict** | **NONE** (composite reinterpretation differs from SM picture; not validated; mass also Gap-13 blocked) |

#### 3.4.3 Other hadrons (Δ, N*, pions, kaons, hyperons)

| Field | Status |
|---|---|
| QNG candidate (v7 retracted) | DER-QNG-038 v7 ladder: R=5→Δ(1232), R=6→N*(1520), R=7→Δ(1700). |
| Status | **RETRACTED** under v8 orbital (DER-QNG-074 + GPU-031g): R5/R4 ratio 1.088 vs needed 1.310 (17% off). Mass ladder is a v7 gradient-flow conservation statement only. |
| Pions, kaons (mesons, q-q-bar pairs) | NONE — mesons are quark composites; QNG has no quarks. |
| **Verdict** | **NONE** (mesons) or **PARTIAL** (Δ etc. via v7 ladder, no longer v8) |

**Hadron summary**: 1 partial (proton, topology only), all others NONE
or structurally blocked.

### 3.5 Higgs boson (H)

| Field | Status |
|---|---|
| QN required | J=0, Q=0, m=125 GeV, scalar VEV v=246 GeV |
| QNG candidate | The χ-field VEV (V_0 in VEV+fluctuation DE+DM model, THEORY_STATE §0). V_0 ≈ 0.686 substrate units gives Ω_DE = 0.686 at cosmological scale. |
| QN supplied | J=0 ✓ (χ is a scalar), Q=0 ✓ (χ does not couple to A_ij at leading order — UNCHECKED), VEV exists ✓. m_Higgs = ? (Gap 13). |
| Obstructions | Class I (Gap 13 absolute scale: substrate V_0 is dimensionless ~0.7, not 246 GeV). Class III-adjacent: Q=0 means χ-fluctuations should be DM-like, not Higgs-like — these roles are conflated in VEV+fluctuation model. |
| **Verdict** | **PARTIAL** (scalar VEV exists; identification with Higgs vs DE vs DM not separated; scale unsolved) |

### 3.6 Dark matter

| Field | Status |
|---|---|
| Phenomenological requirements | Cold, non-baryonic, ~26.5% of universe, weakly self-interacting, gravitationally clustered |
| QNG candidate | All explored: χ-as-DM (FALSIFIED CPU-132 — sub-Planck correlation length), vortex rings (charged under v12 — RULED OUT), σ_g defects (FALSIFIED CPU-142 — π_n(R)=0), Hopfions (charged ±e under v12 — RULED OUT), modified gravity at galactic scale (NOT PREDICTED CPU-134). |
| Obstructions | Class III: charge-topology link of v12 forbids stable neutral particle ontologically. |
| **Verdict** | **STRUCTURALLY BLOCKED** (DER-QNG-082) |

**Note**: Despite this, the VEV+fluctuation DE+DM unification proposal
(THEORY_STATE §0) claims δχ fluctuations behave matter-like
phenomenologically at cosmological scale. This is a phenomenological
match, not an identification of a particle DM. DM as PARTICLE is
structurally absent; DM-LIKE BEHAVIOR may emerge from χ dynamics.

## §4. Aggregate status

Identification level across SM particle content:

| Category | Total species | Identified | Partial | Blocked | None |
|---|---|---|---|---|---|
| Gauge bosons | 5 (γ, g, W, Z, gluon) | 1 (γ) | 1 (g via v11) | 3 (W, Z, gluon) | 0 |
| Charged leptons | 3 | 0 | 0 | 0 | 3 |
| Neutrinos | 3 | 0 | 0 | 3 | 0 |
| Quarks | 18 (6×3) | 0 | 0 | 18 | 0 |
| Hadrons (sample) | ~10 | 0 | 1 (p, partial) | several | rest |
| Higgs | 1 | 0 | 1 | 0 | 0 |
| Total approximate | ~40 | **1 (~2.5%)** | **3 (~7.5%)** | ~24 (~60%) | ~12 (~30%) |

**QNG today identifies ~2.5% of SM unambiguously and ~10% in partial
form**, with ~60% structurally blocked by missing ontology (SU(2),
SU(3), fermion sector, neutral-elementary).

This is a brutal but honest assessment.

## §5. Three classes of obstruction

### Class I — Gap 13 / Gap 14 (scale only)

Affects: proton candidate, Higgs candidate.

Form: the QNG candidate object exists, its topological / kinematic
quantum numbers match, but absolute mass/scale is blocked by 22-order
substrate-to-observation tension (Gap 13) or by L-dependent finite-size
artefacts (Gap 14).

Closure path: Gap 13 closure via quantum one-loop α-running (DER-QNG-081
sketch, 6-12 weeks total) or alternative scale-bridging mechanism.

### Class II — Missing structure

Affects: W, Z, gluons, all quarks, all leptons (as fermions),
neutrinos.

Form: the substrate ontology does not contain a field with the required
gauge symmetry (SU(2), SU(3)) or representation (spin-1/2 fermion).

Closure path: v13 axiomatic extension (or equivalent). This continues
the pattern v10→v11→v12→v13 (each adding the minimal field needed to
match the next observation), which Gabriel has flagged as a concern.

Alternative closure path: a substrate mechanism whose emergent low-energy
content INCLUDES SU(2), SU(3) and fermions without explicit axiomatic
introduction. Not currently known.

### Class III — Charge-topology link forbids neutral elementary

Affects: neutrinos, neutron (elementary), Z (irrelevant — also Class
II), DM, Higgs (partly — VEV is sector-level, fluctuations are
charge-neutral but ambiguous).

Form: in v12, π_1(target manifold) = Z gives topological stability AND
quantizes phi-winding charge simultaneously. The two are linked. No
neutral stable elementary.

Closure path: either accept composite interpretation (W+ ring + W- ring
at d≈3λ as "neutron"; phenomenologically untested), or v13 extension
that decouples stability from charge.

## §6. Implications for mass-derivation program

The user's question "can we derive particle masses" decomposes into:

**Step 1 (this document, IDENTIFIED CLASS)**: identify which QNG object
corresponds to each SM particle. ANSWER: only photon is fully
identified; ~7.5% are partial; ~90% are blocked or absent.

**Step 2 (BLOCKED until Step 1 closes for a given family)**: derive the
mass of that QNG object from substrate dynamics.

For the families where QNG has a candidate (photon, graviton, proton,
Higgs):
- Photon: m=0 is structural ✓ (already derived: gauge invariance)
- Graviton: m=0 is structural ✓ (v11 axiom)
- Proton: m blocked by Gap 13 / Gap 14
- Higgs: m blocked by Gap 13

For the families where QNG has NO candidate (charged leptons,
neutrinos, quarks, W, Z, gluons): mass derivation is structurally
blocked before scale is even considered.

**Brutal conclusion**: even if Gap 13 were closed tomorrow, QNG could
derive masses for at most 2-3 particles (photon already done, graviton
trivially, proton possibly). The "few families" of the original user
question requires Class II closures (v13 or equivalent) BEFORE Gap 13
closure becomes relevant.

## §7. Recommended attack ordering (revised)

In light of this audit, the most strategic next moves are:

### Tier A — closeable in current QNG (do these first)

**A.1**: Derive J of the proton-candidate orbital attractor at R=4.
Specifically: compute the angular momentum carried by the cached
GPU-031f orbital ⟨L_orbit⟩ and ⟨L_internal⟩, identify if J=1/2 emerges
from the topology of the phi-winding (Hopf invariant on the orbit) or
not. Effort: 1-2 sessions of numerical analysis on existing data.

**A.2**: Derive the spin of the Hopfion (CPU-069 stable, charged ±e).
Q_Hopf = 1 is a topological invariant. Standard skyrmion result:
in 3+1D, Q_Hopf integer-valued solitons can carry half-integer spin via
the Wess-Zumino term. Check if QNG Hopfion configuration has the right
effective Wess-Zumino term. Effort: 1-2 sessions (analytical) + 1-2
sessions (numerical verification).

If A.1 or A.2 succeeds → first QNG-derived fermion candidate, even with
absolute scale unsolved. This UNBLOCKS Class II for at least one
particle.

**A.3**: Test the (W+ ring) + (W- ring) bound state at d≈3λ for
metastability over many orbital periods (>10⁴ lu). If lifetime > naive
positronium analogue, neutron-composite interpretation gains support.
Effort: 1 GPU run, ~3-5 hours.

### Tier B — Gap 13 dependent

**B.1**: One-loop quantum α-running computation (DER-QNG-081 sketch
exists). 2-4 weeks analytical, then numerical verification.

**B.2**: If Gap 13 closes — re-derive proton mass via running coupling
and unit-bridge correction. Could give absolute mass ~MeV-GeV scale.

### Tier C — v13 extension design (Class II closures)

**C.1**: Identify minimum non-Abelian extension that closes the most
SM-particle families per axiom added. Candidates:
- SU(2) for W/Z and weak-isospin
- SU(3) for color and quark confinement
- Fermion sector via Kaehler-Dirac or staggered fermions on lattice
- Combined: each takes years of theoretical development.

C.1 is the largest investment but the only one that brings most of SM
into QNG scope.

## §8. Honest verdict on the original strategic question

The user asked: *"can we derive particle masses, at least a few
families?"*

**Answer based on this audit**:

- "Few" was generous in framing. QNG currently identifies particles of
  ONE family (gauge bosons, partially), not several.
- For the photon family, mass is already derived (m=0 from gauge
  invariance) — but that is one particle, not a "family of masses".
- For the proton family, mass is blocked by Gap 13.
- For lepton, quark, W/Z, neutrino, DM families, mass derivation
  requires v13-equivalent extensions before scale is even relevant.

**Realistic next milestones** (in order of feasibility):

1. **Demonstrate spin-1/2 from QNG topology** (Tier A.1 or A.2): would
   produce QNG's first fermionic identification, even without absolute
   mass. Estimated effort: 1-2 weeks.
2. **Compute QNG proton J^P (numerical)**: spin and parity from cached
   orbital data. Effort: 1 week.
3. **Close Gap 13 via one-loop α-running** (Tier B.1): would unlock
   proton, Higgs, and graviton absolute masses. Effort: 6-12 weeks.
4. **Design v13 minimal extension** for W/Z/quarks/leptons (Tier C.1):
   would bring most of SM into QNG scope. Effort: months to years.

The user's intuition that *"QNG = GR + QM should give more about
particles than SM"* is correct in principle but **falsified
operationally today**: QNG currently gives LESS about particles than SM
(SM has ~40 particles identified by phenomenology; QNG has ~1-3).

This is not a failure — it is the honest state of the program. The
substrate-level derivations (c, G, ℏ, Λ=0, photon dispersion, Newtonian
limit, KG, Shapiro, WEP, Pound-Rebka, gravity coupling) are real
strengths. The particle-physics derivation is the open work.

## §9. Recommended single-session deliverable

Based on this audit, the highest-leverage single session would attack
**Tier A.1 or A.2 — derivation of spin-1/2 from QNG topology**. Either
gives QNG's first derived fermionic quantum number, opens the path
toward leptons via QNG topology, and uses only existing data plus
analytical work (no Gap 13 dependence, no v13 axiom).

Recommended target: **Tier A.2 (Hopfion + Wess-Zumino spin)**, because
the Hopfion is already topologically stable (CPU-069), already charged
under v12 (CPU-143), and the Wess-Zumino mechanism for half-integer
spin from integer-Q topological solitons is a well-established result
(Witten 1983, Wilczek-Zee 1983). Adapting it to QNG should produce a
concrete prediction within 1-2 weeks.

If A.2 succeeds: QNG has identified at minimum one charged lepton
candidate (Hopfion = electron-analog?), opening Class II partial
closure for the lepton sector.

If A.2 fails: we know that QNG Hopfions are NOT lepton candidates,
narrowing the search.

Either outcome is real progress.

## §10. Cross-references and pointers

- v12 EM and charge link: `qng-v12-em-extension-v1.md` (DER-QNG-076)
- v11 graviton: `qng-v11-tensor-extension-v1.md` (DER-QNG-072) +
  `qng-gap12-no-go-proof-v1.md` (DER-QNG-071)
- Gap 13 scale: `qng-gap13-scale-tension-v1.md` (DER-QNG-074),
  `qng-gap13-attack-program-v1.md` (DER-QNG-077),
  `qng-gap13-A1-step1-result-v1.md` (DER-QNG-080),
  `qng-gap13-oneloop-sketch-v1.md` (DER-QNG-081)
- Gap 14 lattice: `qng-gap14-mring-lattice-dependence-v1.md` (DER-QNG-075)
- DM no-go: `qng-dm-final-no-go-v1.md` (DER-QNG-082)
- Baryon ladder (retracted under v8): `qng-baryon-ladder-derivation-v1.md`
  (DER-QNG-038)
- Hopfion: CPU-066 to CPU-072 audit folders; CPU-143 v12 charge
- Proton orbital attractor: GPU-031f audit (`qng-v8-r1-long-time-v1`)

## §11. What this document does NOT do

This is an AUDIT, not a derivation. It catalogues identifications and
gaps but does not produce any new physical content. Its value is
strategic: it prevents wasted effort on tracks that are structurally
blocked, and identifies the highest-leverage attack vectors given the
current theory state.

The next concrete derivation (recommended Tier A.2 above) requires a
separate working session and a separate document.
