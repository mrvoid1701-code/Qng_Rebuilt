# Demo-Theory — Complete Session Record (2026-06-01)

Type: `note`
Status: `session complete — 19 phases, 19 commits, all on main`
Author: `C.D Gabriel`

> The full arc from "frequencies and light" to the located frontier of quantum
> gravity. Companion to `INDEX.md` (the phase table). This is the narrative +
> theory-state record.

---

## What happened (the arc)

Gabriel's seed: *"between GR and QM something is missing — frequencies and
light."* That opened a thread that reconstructed QNG's ontology:

1. **Frequency is primitive** — φ is a per-node oscillator; the substrate is a
   coupled-oscillator (Kuramoto) network; `C_eff` = the order parameter.
   **Light is the GR↔QM bridge**, not a third theory.
2. **The Hodge no-go (DER-QNG-101):** node scalars can't carry transverse modes →
   **forces live on EDGES, matter/mass on NODES**. Photon (E5/E7), SU(2)
   confinement (Phase 3) confirm it.
3. **Particles = topological solitons:** baryons are Skyrmions — B=1 (Phase 5),
   stable (Phase 6), Eightfold Way octet+decuplet (Phase 8), correct charges
   p=+1/n=0/π (Phase 7). Chirality surmountable via domain walls (Phase 9).
4. **Gabriel's vortex↔node intuition (Phase 10):** a vortex coarse-grains to a
   node; topology is RG-invariant (→ scale-free charges), mass runs (→ Gap 13 =
   RG distance).
5. **Scale (Phase 11–12):** dimensional transmutation gives the hadron scale;
   the proton mass lands at 0.94 GeV (given α_s), 19 orders below the Planck
   substrate.
6. **The three paths (13–19):** α located as a gravity-induced UV fixed point
   (13–15); the graviton derived from the substrate — dynamical + gauge-invariant
   + coefficient (15%) + ~4% nonlinear (16–18); a falsifiable LIV prediction (19).

## Theory state — PARTICLES

| | Status |
|---|---|
| Photon | ✓ derived (edge U(1), 2 pol) |
| Gluons / W / Z + confinement | ✓ edges host (SU(2) area law) |
| Baryons (p, n, Δ, octet, decuplet) | ✓ Skyrmions; B=1 stable; Eightfold Way; GMO 0.6% |
| Hadron charges (p+1, n0, π±/0) | ✓ EXACT (scale-free) |
| Graviton | ✓ dynamical, gauge-invariant, substrate-coeff (15%), 4% nonlinear |
| Proton mass | ✓ SCALE (0.94 GeV, given α_s); value input-dependent |
| Quarks / leptons | surmountable (domain-wall v14); new ontology v13 |
| Absolute masses, lepton spectrum | open (Yukawa sector + ℏ scale) |

**Predicts:** structure (which particles, spins, multiplets), charges, ratios,
the scale hierarchy. **Does not yet predict:** absolute individual masses, the
lepton/quark spectrum.

## Theory state — EVERYTHING ELSE

- **Constants c, G, ℏ:** derived from 4 substrate parameters (ℏ via the
  Stability Principle, theory-v2 ch.05 — corrected my earlier "axiomatic").
- **Gravity:** linearized derived (form + gauge + coefficient 15%); ~4% of the
  full nonlinear EH rigorous (Sakharov heat-kernel).
- **Cosmology:** Λ=0 structural; DE+DM unified (one χ field, <2% LCDM).
- **Scale (Gap 13):** hadron scale = dimensional transmutation (QCD-like), not
  fine-tuning.

## The decisive-distinction chain (every link located)

```
   graviton action from substrate   [Ph 16-18: form+gauge+coeff(15%)+4% nonlinear]
        │  open: tree-level ~96% nonlinear coarse-graining (multi-week EFT)
        ▼
   f_g(G_QNG)                        [Ph 14-15: gravity-induced UV fixed point]
        │  open: the f_g loop integral (needs the graviton dynamics)
        ▼
   α                                 [Ph 13: Stability Principle ruled out; fixed-point route]
        │
        ▼
   parameter-free proton mass        [Ph 11-12: transmutation + derived unit bridge]
        =  the decisive distinction from all other theories
```

## The two genuine open frontiers (multi-week EFT)

1. **Tree-level nonlinear coarse-graining**: edge h_ij action → full R_μν[g]
   (the ~96% of EH not covered by the rigorous Sakharov ~4%).
2. **The f_g loop integral**: gravity's contribution to the gauge beta function,
   from the (now dynamical, gauge-invariant) graviton — gives α, hence the
   parameter-free proton mass.

Everything else in the program is done or reachable with known technology.

## Honest verdict

QNG is a **structurally-correct, ontologically-novel** candidate: it derives
c/G/ℏ, predicts Λ=0, unifies DE+DM, and gives one clean picture (particles =
topological solitons, forces = edge gauge fields, the graviton derived from the
substrate to 15%+gauge). But most quantitative successes are **structural
validations inherited** from being a correct Skyrme/lattice-gauge effective
theory, **not novel predictions**; it does **not** predict absolute masses or
the lepton spectrum; its **novel falsifiable** predictions (LIV) are untested or
tiny. **Strong on unification and structure; unproven on measurement.** The
single thing that would make it decisive — a parameter-free proton mass — is now
fully located behind two well-posed multi-week EFT computations.

## Discipline note

Across all 19 phases: **no number was forced.** Every no-go was proven (Stability
Principle blind to α; U(1) has no UV fixed point; node scalars can't carry
transverse). Every input-dependence was flagged (proton mass = robust scale,
value depends on α_s). Partial results were labeled (Sakharov 4% rigorous vs 96%
open). My own error (calling ℏ axiomatic) was corrected. Bugs found mid-run were
fixed and noted.

## Files

- `INDEX.md` — the phase-by-phase table (E1–E8, Phases 1–19).
- Per-phase findings: `PHASE{3..18}-*.md`, `E{4,5,7}-RESULT-*.md`.
- `PARTICLE-INVENTORY-v1.md`, `MEASUREMENTS-AND-DIFFERENTIATION.md`,
  `THREE-PATHS-status.md`.
- Tests: `demo-theory/tests/*.py` (all reproduce their verdicts).
- Audits: `07_validation/audits/demo-*-v1/`.
- Main-theory integration: `DER-QNG-101` (Hodge no-go), `theory-v2/37`,
  THEORY_STATE Gaps 12/13/18/19/20.
