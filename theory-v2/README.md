# QNG Theory v2 — Clean Foundation

**Author**: C.D Gabriel
**Started**: 2026-04-26
**Status**: Clean rebuild based on locked findings from QNG-Theory Release-01

---

## What this is

A **clean reconstruction** of QNG theory using ONLY content that survived
all audits and falsifications from the development phase
(`QNG-Theory Release-01`). 

**Principle**: every claim here is either:
- DERIVED rigorously from substrate axioms
- AXIOMATIC EXTENSION (clearly labeled as such)
- OPEN PROBLEM (in `12-open-problems.md`)

No retracted claims, no speculative material in main files.

## What QNG IS, in one sentence

**QNG is a Quantum Gravity theory** — a discrete graph substrate where
gravity emerges from microscopic dynamics, particles are vortex structures
that ARE gravity-plus-energy configurations, and the fundamental constants
`c`, `G`, `ℏ` are **derived** (not postulated) from 4 substrate parameters
+ 1 stability principle. Predicts `Λ = 0` exactly. Reproduces General
Relativity in the static-source weak-field limit (6/6 Einstein tests PASS).

**The name is literal**: Quantum (substrate is quantum from start) + Node
(graph-based ontology) + Gravity (emergent at substrate level). Remove
"Node" — the detail of which substrate — and you get Quantum Gravity.

## Distinguishing feature

Among all Quantum Gravity approaches (string theory, LQG, CDT, asymptotic
safety, induced gravity, ...), QNG is **the only one that derives the
numerical values of c, G, ℏ from substrate parameters**. Every other QG
program takes these as input.

## File structure

```
theory-v2/
├── README.md                              (this file)
├── 00-ontology.md                         (substrate: lattice + scalar fields)
├── 01-hamiltonian.md                      (action S, dynamics)
├── 02-stability-principle.md              (the one axiom)
├── 03-derivation-c.md                     (c² = β_φ/(z·μ_φ))
├── 04-derivation-G.md                     (G = β_g/z)
├── 05-derivation-hbar.md                  (ℏ = √(β·μ·z)/C_cubic)
├── 06-unit-bridge-SI.md                   (Planck-scale lattice match)
├── 07-predictions-invariants.md           (ℏ·c, ℏ/c, G/c² invariants)
├── 08-predictions-numerical.md            (a_L = 0.305 ℓ_P, BH microstates)
├── 09-correspondence-newton.md            (Newtonian limit)
├── 10-correspondence-GR-static.md         (6/6 Einstein tests)
├── 11-extensions-axiomatic.md             (v11 graviton + v12 photon)
├── 12-open-problems.md                    (what's still missing)
├── 13-quantization-of-v11-graviton.md     (canonical quantization of h_ij)
├── 14-graviton-matter-coupling.md         (Newton + Donoghue comparison)
├── 15-quantum-gravity-predictions.md      (QG predictions vs string/LQG/CDT)
├── 16-sakharov-induced-nonlinearity.md    (non-linear gravity from matter loops)
├── 17-bh-entropy-from-substrate.md        (substrate microstate counting)
├── 18-sakharov-rigorous.md                (quantitative G_substrate vs G_induced)
├── 19-particles-in-qng.md                 (ontology + candidate mechanisms)
├── 20-particle-research-roadmap.md        (concrete path to particle identification)
├── 23-mathematical-foundations.md         (rigorous defenses: Stability, Lorentz, LIV, spin)
├── HISTORY.md                             (pointer to old folder for retractions)
├── SESSION_REPORT_2026_04_26.md           (autonomous block summary)
├── papers/                                (publishable drafts)
├── extensions/                            (v11, v12 detailed)
└── tests/
    ├── verify_constants.py                (one-shot verification of c, G, ℏ)
    ├── verify_graviton_modes.py           (v11 quantization checks)
    ├── verify_donoghue_lattice.py         (lattice correction to Donoghue 41/10π)
    ├── verify_oneloop_lattice.py          (actual numerical loop integration)
    └── verify_substrate_spectrum.py       (free-field particle spectrum)
```

## Reading order

For someone NEW to QNG:
1. README (this) → high-level
2. 00-ontology + 01-hamiltonian → what's the theory
3. 02-stability-principle → the key physical claim
4. 03-04-05 → derived constants
5. 07-08 → predictions
6. 12-open-problems → honest scope

For someone wanting to publish:
1. Read papers/ directory
2. Reference 03-05 for theoretical content

For someone wanting to extend:
1. Read 12-open-problems for what's still unsolved
2. Pattern v11/v12 for axiomatic extensions

## What's NOT here (and why)

The original folder `QNG-Theory Release-01/` contains:
- 100+ test scripts
- Many retracted derivations
- Failed hypotheses (DER-QNG-038 baryon ladder, DER-QNG-079 α-running, ...)
- Multiple gap iterations
- Audit trails

This v2 folder contains ONLY what survived audit. For history of
retractions and how findings evolved, see HISTORY.md.

## Status of contributions (per layer)

| Layer | Content | Status |
|---|---|---|
| 00-02 | Ontology + Stability axiom | LOCKED |
| 03-05 | Derived c, G, ℏ | LOCKED |
| 06 | SI unit-bridge | LOCKED (machine precision) |
| 07-08 | Predictions | LOCKED (DER-QNG-083) |
| 09-10 | GR correspondence | 6/6 PASS in v10 |
| 11 | v11+v12 extensions | DRAFT axiomatic |
| 12 | Open problems | ACKNOWLEDGED |

## Forward path

From this clean foundation, three research directions:

### Direction A: Quantum gravity (deeper)
Quantize h_ij in v11 → graviton as proper QFT. Connect to non-linear GR.

### Direction B: Dark matter (extension)
Investigate what v13 ontology would solve DM (currently structurally impossible
in v10/v11/v12 — see `12-open-problems.md`).

### Direction C: Particle physics
Resolve Gap 13 (scale separation) via one-loop α calculation. If success,
particle masses become derivable.

These three directions can proceed independently. Foundation in 00-12 is
unaffected by their outcomes.

## Quote-able summary

> "QNG derives Planck's ℏ from a discrete substrate plus one stability
> principle. From this foundation, c, G are also derived, Λ = 0 emerges
> structurally, and 8 testable predictions follow. The framework is
> consistent with all known General Relativity tests (6/6 Einstein
> static-source phenomenology) and predicts a specific Planck-scale
> cutoff at a_L = 0.305 ℓ_Planck."

— Gabriel 2026
