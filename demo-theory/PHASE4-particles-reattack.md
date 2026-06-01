# Phase 4 — Re-attacking the particles with the edge/node framework

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Author: `C.D Gabriel`
Tests: `t_phase4a_custodial_audit.py`, `t_phase4b_v13_matter.py`,
`t_phase4c_fermion_doubling.py`
Depends on: `DER-QNG-101` (Hodge no-go), Phase-3 (`SU2_EDGES_CONFINE`)

---

## The reframing that Phase 1–3 forces

Before, the particle program (DER-QNG-038 baryon ladder, the Hopfion "18
identifications" the May session judged "mostly numerology") tried to map
**topological node solitons (σ_m rings / Hopfions) directly onto elementary
particles** — sometimes onto baryons, sometimes onto leptons/mesons. The
edge/node split now explains *why* that was shaky and draws the correct map:

```
   QNG OBJECT                  CORRECT IDENTITY                 STATUS
   ─────────────────────────   ──────────────────────────────  ─────────────────
   edge vector A_ij            photon (spin-1)                  ✓ done (v12)
   edge matrix SU(2)/SU(3)     W/Z/gluons + CONFINEMENT         ✓ edges host (Ph3)
   edge rank-2 (symmetric)     graviton (spin-2)                E8 kinematic
   node scalar phi             phase / frequency (QM)           ✓
   node soliton sigma_m ring   topological MASSIVE soliton      ✓ (mass=volume, E4)
      = a baryon-like object (Skyrme-type), NOT an elementary fermion
   elementary chiral fermion   quark / lepton                   MISSING (v13 + v14)
```

**The core correction: QNG's rings are not elementary particles — they are
topological solitons, and the natural reading is baryon-like (Skyrme-type), not
quark- or lepton-like.**

## Phase-4 test results

### 4a — No custodial SU(2) in (σ_g, σ_m)  (`demo-phase4a-custodial-v1`)

Operational symmetry test: the physical channel asymmetry (Channel F acts on
σ_m, not σ_g) **breaks** the (σ_g, σ_m) rotation (commutator 0.21–0.76); the
control (perfectly matched fields) restores it only as **SO(2) = U(1)**, never
SU(2). **`NO_CUSTODIAL_SU2`** — tesla-mind's isospin-doublet conjecture fails at
both levels (channel breaking + real fields can't carry SU(2)). The matter
doublet must be new ontology.

### 4b — v13 matter doublet is a consistent construction (`demo-phase4b-v13-matter-v1`)

A complex node doublet `ψ ∈ ℂ²` coupled to SU(2) edge links via the covariant
hopping `|ψ_i − U_ij ψ_j|²`: **gauge-invariant to machine precision** (`ΔS=0`),
and an SU(2) gauge background **rotates the isospin** (a pure "up" doublet →
"down" → "up" as it is transported — the weak current, n↔p). **`V13_MATTER_
CONSISTENT`**. The door works: *if* QNG adds a complex node doublet, the full
non-abelian matter+gauge structure is consistent. It is honest new ontology
(no natural source in the existing real scalars — confirmed by 4a).

### 4c — The chirality wall (`demo-phase4c-fermion-doubling-v1`)

A naive lattice Dirac fermion has zeros at `k=0` AND `k=±π` → 2 species/dim →
**16 doublers in 3+1D** (Nielsen-Ninomiya). The Wilson term decouples them but
**explicitly breaks chiral symmetry**. **`CHIRALITY_WALL_CONFIRMED`**: the
parity-violating weak sector needs a lattice-chiral-fermion solution
(Ginsparg-Wilson / overlap / domain-wall) — a real v14-level construction, the
same one every lattice-QCD program solves. Edges host forces (easy); chiral
fermions are hard (but solved technology).

## The Skyrme reframing of the baryon ladder (the productive new lead)

This is the most useful "re-attack" outcome. The QNG ring already has every
feature of a **Skyrmion** — the topological-soliton picture of baryons
(Skyrme 1961; Adkins-Nappi-Witten 1983):

| Skyrme model | QNG ring | match |
|---|---|---|
| baryon = topological soliton of a phase field | ring = soliton of `φ` with winding | ✓ |
| **baryon number = topological winding** | **`M_ring` = conserved topological charge** | ✓ (CPU-074) |
| mass set by the soliton (not constituents) | **mass = volume charge** (E4) | ✓ |
| J = I tower from **collective quantization** | even R → I=½, odd R → I=3/2 (DER-QNG-038) | ✓ pattern |
| no radial excitations in the rotational band | **Roper N\*(1440) ABSENT** (DER-QNG-038) | ✓ (striking) |

> **The DER-QNG-038 "baryon ladder" is best understood not as a constituent-quark
> spectrum but as a SKYRMION collective-quantization spectrum.** This explains —
> rather than fits — the even/odd-R → I=½ / I=3/2 pattern and the *absence* of the
> radial Roper resonance (collective coordinates are rotational, not radial). It
> moves the result from "numerology in a dense PDG spectrum" toward a principled,
> established framework.

**The honest gap in the analogy:** a true Skyrmion needs an **SU(2)-valued**
field `U(x) = exp(iτ·π/f)`; QNG's `φ` is only **U(1)**. So QNG rings are
currently *baby-Skyrmion / U(1)-vortex* solitons, not full Skyrmions. **v13's
complex doublet is exactly what upgrades them**: when the v13 SU(2) matter field
develops topological windings, it gives genuine Skyrmions = baryons — and it is
*also* the matter the weak force acts on. **v13 plausibly solves the baryon-
soliton picture AND the elementary-matter problem at once.** (Conjecture, labeled.)

## The layered map this produces

| Layer | Adds | Hosts | Status |
|---|---|---|---|
| v8 | node scalars + momenta | mass (volume charge), φ-waves, σ_g gravity (scalar) | locked |
| v11 | edge rank-2 | graviton tensor modes | axiom; E8 kinematic |
| v12 | edge U(1) `A_ij` | photon | confirmed (Ph2) |
| **v13** | **edge SU(2)/SU(3) + complex node multiplet** | **W/Z/gluons, confinement, genuine Skyrmion baryons** | edges confirmed (Ph3); matter consistent (4b); **new ontology** |
| **v14** | **lattice-chiral fermions** | **quarks, leptons (parity violation)** | **wall** (4c); needs Ginsparg-Wilson-class construction |

## Honest bottom line for "re-attacking particles"

1. **QNG natively makes two kinds of object**: force carriers (edges) and
   topological massive solitons (node σ_m rings). The rings are **baryon-like
   Skyrmions**, with mass = topological volume charge.
2. **The prior identifications were conflating sectors.** Mapping rings to
   leptons/mesons/elementary particles was the numerology; mapping rings to
   **baryons as Skyrmions** is principled and explanatory (J/I pattern, no Roper).
3. **Elementary fermions (quarks/leptons) are genuinely absent** and need v13
   (complex multiplet — shown consistent, 4b) + v14 (lattice chirality — the
   wall, 4c). This is the SAME well-understood problem as lattice QCD, not a
   QNG-specific mystery.
4. **The forces are the easy part** (edges, confirmed). The matter is the hard
   part (chiral fermions). This is the exact inverse of how the program treated
   it before — and it tells us precisely where the next real work is.

## Next moves (concrete)

- **Skyrme quantization of the QNG ring** (highest value): apply collective
  quantization to a QNG `φ`-soliton and check the J(J+1) rotational energy
  spectrum against the R-ladder masses. Would turn the Skyrme analogy into a
  derivation. (CPU-class, tractable.)
- **v13 Skyrmion**: build the SU(2) doublet soliton (genuine winding), measure
  its topological charge and mass — does it reproduce the ring ladder better
  than the U(1) vortex?
- **Confinement vs ring force** (deferred from Phase-3 P5): the CPU-050 ring-ring
  potential is non-monotonic (molecular/residual), NOT linear-confining — so it
  is the *nuclear-residual* analog between color-neutral solitons, consistent
  with (not the same as) the edge color confinement. Clarified, not a new test.
