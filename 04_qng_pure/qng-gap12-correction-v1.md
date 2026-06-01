---
type: note
id: NOTE-QNG-028
title: Gap 12 closure RETRACTED — savant review identifies overreach
status: honest correction supersedes DER-QNG-073 premature closure claim
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-071 (no-go proof)
  - DER-QNG-072 (v11 extension)
  - DER-QNG-073 (premature closure claim)
  - savant-physics-reviewer independent audit 2026-04-24
---

# NOTE-QNG-028 — Gap 12 closure claim RETRACTED

User directive was: "dai drumul la fel indici puzzeluri totu non ad-hoc,
si verificat, nu ne oprim pana cand gap12 nui facut fara tricuri totu
corect stiintific".

I claimed Gap 12 closure in DER-QNG-073. An independent savant-physics-
reviewer audit (2026-04-24) identifies **multiple overreaches** that do
not meet the "no tricks, scientifically correct" standard Gabriel
specified. This note retracts the closure claim and restates the true
status honestly.

## Overreaches identified

### Overreach 1: No-go theorem scope claim is too strong

DER-QNG-071 claims no-go for spin-2 from scalar substrate. The proof is
rigorous at the **free/linearized perturbative level** but **does not
close the non-perturbative composite sector loophole**.

**Counterexample class**: QCD stress tensor is built from spin-1/2 quarks
and spin-1 gluons. Yet spin-2 glueball states (J^PC = 2++) exist in the
non-perturbative QCD spectrum. My step D ("interactions couple modes but
do not change their spin structure at linear level") is TRUE only
perturbatively, not non-perturbatively.

For QNG v10, the relevant question: does the full non-perturbative
spectrum (not just linearized mode count) admit a two-particle (or
higher) bound state with spin-2 quantum numbers and independent
dispersion? Linearized analysis CANNOT answer this.

**Correct scope of DER-QNG-071**: No propagating spin-2 mode exists at
the **linear perturbative level** of QNG v10 around flat or ring
backgrounds. The non-perturbative composite spectrum is NOT analyzed
and remains structurally open.

### Overreach 2: CPU-121 does not confirm non-perturbative no-go

CPU-121 diagonalizes the linearized H_lin operator on a ring background,
finding 73 distinct eigenvalues with cubic-symmetric degeneracies. This
is a LINEAR single-field analysis. A non-perturbative composite spin-2
mode would appear as a **correlated two-particle resonance in the full
spectrum**, NOT as a single-field eigenvalue.

**Analogy (from savant)**: claiming photons have no spin-2 by counting
linearized Maxwell modes is the same methodological error. The spin-2
photon-photon scattering amplitude is non-perturbative; linearized
single-photon analysis cannot exclude it.

**Correct interpretation of CPU-121**: the linear sigma_g spectrum on a
ring background matches the scalar-on-cubic-lattice prediction. This is
consistent with the no-go at linear level only.

### Overreach 3: v11 is disguised linearized GR, not a "derivation"

DER-QNG-072's Lagrangian `L_h = (1/2μ_h)|π_ij|² - (1/2)c_g²(∂_k h_ij)²`
is the **Pauli-Fierz Lagrangian for free massless spin-2 field**, up to
normalization. The coupling `L_int = (8πG/c⁴) h_ij T^TT_ij` is
**exactly the linearized Einstein equation source coupling**.

I imported linearized GR wholesale. The "QNG-specific" element is only
c_g = c_phi from DER-QNG-042 §3.3 — but GR also predicts c_gravitational
= c_light, so this is no new content.

**Choices that were presented as "minimal" but are actually ad-hoc**:
- mu_h = mu_g: chosen by fiat "to give same dispersion", not derived
- 8π coupling: imported from GR (Einstein tensor convention)
- Node-valued vs edge-valued (Regge) h_ij: not determined by v10 structure

**Correct statement**: v11 is an **axiomatic import of linearized GR's
tensor sector**. It is not a derivation of the graviton from QNG
principles. This parallels (and is more damaging than) the Higgs
situation.

### Overreach 4: Hulse-Taylor 0.3% match is empty as evidence

CPU-123 explicitly notes: "v11 predicts SAME quadrupole formula as GR"
because v11 = linearized GR by construction and G_QNG/c_QNG = G_SI/c_SI
by unit-bridge.

Savant: "the 0.3% match IS THE GR PREDICTION, not a QNG prediction.
Zero discriminating power between v11 and standard GR."

Additionally, the precision is **artificially weak**: GR already
predicts PSR B1913+16 orbital decay to <0.04% (Weisberg & Huang 2016;
Kramer et al. 2021). My 0.3% is the numerical precision of my Python
script (approximate orbital elements, eccentricity correction), NOT
"agreement".

**Correct interpretation**: CPU-123 is a **numerical consistency check**
that my Python correctly evaluates the GR quadrupole formula. Not
evidence for v11 as a QG theory.

### Overreach 5: Missing non-linear completion

Linearized GR is NOT merely weak-field approximation of GR — it is a
**fundamentally different theory**. GR's non-linear structure (Einstein
tensor G_μν = R_μν - (1/2)g_μν R) requires:

1. Diffeomorphism invariance (gauge principle)
2. Graviton self-coupling (energy carries gravity)
3. Einstein-Hilbert action structure

v11 has **none of these**. It is linearized GR with no known path to
non-linear completion. Without Diff(M) gauge principle, there is no
theorem forcing the self-coupling to be Einstein-Hilbert specifically.

**Correct statement**: v11 is an EFT for linearized gravity on QNG
substrate, not a UV-complete quantum gravity theory. The "real" Gap 12
is the non-linear completion, which is wide open.

### Overreach 6: "QNG is a QG candidate" claim is too strong

Savant: "v11 does not quantize h_ij. It adds a classical h_ij field to
a quantum matter sector. This is standard effective field theory of
gravity as practiced since the 1990s (Donoghue 1994, Burgess 2004). It
is a respectable EFT but it is not a quantum gravity theory in the
technical sense."

**Correct statement**: v11 is an EFT of gravity embedded in a discrete
graph substrate. Not a QG theory in the sense of string theory, LQG,
CDT, or asymptotic safety. Those theories address UV completion,
quantization of h_ij itself, and BH microstate accounting. v11 does not.

## True status of Gap 12

With the corrections above, the honest status is:

| Element | Status |
|---|---|
| No-go theorem at linear perturbative level | VALID |
| No-go theorem at non-perturbative composite level | NOT PROVEN |
| CPU-121 confirming linear-level no-go | VALID (but restricted) |
| v11 as "closure" of Gap 12 | RETRACTED — v11 is axiomatic import, not closure |
| v11 as consistent linearized GR extension | VALID |
| Hulse-Taylor as v11 evidence | RETRACTED — empty, just GR formula |
| Non-linear completion of v11 | OPEN (the real Gap 12) |
| Quantization of h_ij | OPEN |
| QNG as "QG theory" | OVERCLAIM — QNG is EFT of gravity |

## What remains valid from this session

1. **DER-QNG-071 restricted**: spin-2 cannot appear at linear
   perturbative level in pure scalar substrate.
2. **DER-QNG-072 v11 structure**: if we ADD a rank-2 tensor field by
   axiom, it reproduces linearized GR with correct spin-2 structure.
3. **v11 is consistent** with all v10 static-source phenomenology
   (DER-QNG-068 6/6 PASS preserved).
4. **The REAL Gap 12 is now sharpened**: it is the non-linear completion
   (Einstein-Hilbert structure emergent from QNG) and/or the non-
   perturbative composite spin-2 sector of v10.

## Corrective actions needed

Per savant recommendations:

1. Mark DER-QNG-071 scope correctly (linear perturbative only).
2. Retitle CPU-121 to reflect linear scope.
3. Relabel v11 as "axiomatic import of linearized GR tensor sector" in
   all docs.
4. Retire CPU-123 Hulse-Taylor claim as "QNG evidence"; keep as
   consistency check only.
5. Update THEORY_STATE: Gap 12 is NOT closed; it is bisected into
   (12a) linear-level no-go + v11 axiomatic addition, and
   (12b) non-linear completion + non-perturbative composite sector,
   which remain OPEN.
6. Reframe QNG status: NOT a QG theory; IS an EFT of gravity with
   derived constants and substrate-level foundation.

## Honest final answer to user's question "avem QG?"

**Still no.** v11 with the honest labeling is:
- An EFT of gravity consistent with GR at linearized level
- With c, G, ℏ derived from substrate
- With scalar + tensor sectors added
- With open non-linear and quantization questions

This is a strong foundation but not quantum gravity in the technical
sense of the QG community.

## What a TRUE Gap 12 closure would require

From the savant's recommendations, a genuine closure would be one of:

(A) **Prove non-perturbative composite spin-2 modes exist in pure v10**
    (no need for v11 axiomatic extension). Would require non-perturbative
    spectral analysis on ring or more complex background.

(B) **Derive v11's h_ij dynamics from a deeper QNG principle**, such
    that L_h = Pauli-Fierz emerges rather than being imported. This
    requires a mechanism analogous to induced gravity (Sakharov) or
    holography (Maldacena) in QNG-specific language.

(C) **Give up the "derived from substrate" claim and explicitly declare
    v11 as a two-sector theory** (scalar substrate + axiomatic tensor
    sector), with publication emphasizing the substrate-based
    derivation of c, G, ℏ, and scalar gravity, NOT the full QG claim.

Path C is the most honest given current state. Paths A and B are
research programs of substantial difficulty.

## User-facing apology

I owe Gabriel an explicit acknowledgment:
- I declared Gap 12 closed prematurely
- I claimed v11 was "closure" when it was axiomatic import
- I presented Hulse-Taylor 0.3% as evidence when it was empty
- I overreached on QG claim

These were not conscious "tricks" but were errors of insufficient
skepticism. The savant review caught them. Gabriel's directive was
correct: rigor > velocity.

The correct status is documented here. Further work on Gap 12 should
pursue Path A (non-perturbative composite analysis) or Path B (derive
v11 dynamics from deeper principle) if we want a real closure.
