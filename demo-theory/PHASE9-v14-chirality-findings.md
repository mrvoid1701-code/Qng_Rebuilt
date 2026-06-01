# Phase 9 (v14) — chiral fermions on the QNG lattice (the wall is surmountable)

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Probe: `demo-theory/tests/t_phase9_v14_domain_wall.py`
Artifact: `07_validation/audits/demo-phase9-v14-domain-wall-v1/`

---

## The question

Phase 4c established the chirality wall: a naive lattice Dirac fermion has 16
doublers (Nielsen-Ninomiya), and the Wilson term that removes them breaks chiral
symmetry. The weak force is chiral (parity-violating), so quarks/leptons seemed
to need a v14 construction beyond reach. **Is v14 actually blocked, or solvable?**

## Result: **V14_CHIRAL_FERMION_OK**

A 1D lattice Dirac Hamiltonian with a Wilson term and a periodic **kink–antikink
mass domain wall** (Kaplan / Callan-Harvey domain-wall fermion):

| Test | Result |
|---|---|
| no Wilson (r=0) | **4** near-zero modes (wall modes ×doublers) |
| Wilson (r=1) | **2** near-zero modes (doublers gapped; next \|E\|≈0.33) |
| localization | one mode at each wall (sites 30, 90) |
| **chirality** | eigenvalues **+1.0** (wall 30) and **−1.0** (wall 90) — exact, opposite |

> The Wilson term gaps the doublers, and **exactly one chiral mode binds to each
> wall** — a left-handed fermion on the kink, a right-handed one on the antikink,
> with chirality eigenvalues ±1.0 (measured by projecting the chirality operator
> into the zero-mode subspace and diagonalizing). Separate the walls (the
> extra-dimension / overlap construction) and a **single chiral fermion** survives
> at low energy. **This surmounts the Nielsen-Ninomiya wall of Phase 4c.**

## What this changes

**The chirality wall (v14) is NOT blocked in principle.** Chiral fermions —
i.e. quarks and leptons — are achievable on the QNG substrate using **known
lattice-chiral technology** (domain-wall, overlap, Ginsparg-Wilson). It is a
*real construction* (it needs an extra dimension, or equivalently the overlap
operator), but it is a **solved problem in lattice field theory**, not a
mystery. QNG's discrete-lattice nature is, if anything, the natural home for
exactly these constructions.

So of the two walls that bounded the particle program:

| Wall | Status after Phase 9 |
|---|---|
| **v14 chirality** (elementary fermions) | **SURMOUNTABLE** — known lattice-chiral tech (this phase) |
| **Absolute scale** (ℏ program + Gap 13) | **STILL THE HARD ONE** — Planck→MeV, 22 orders, unresolved ℏ |

**The single genuinely hard remaining obstruction is the absolute scale**, not
chirality and not the gauge/matter structure.

## Honest scope

- This is the domain-wall *mechanism* demonstrated in 1D (the cleanest setting):
  doubler removal + wall-localized chiral modes with exact ±1 chirality. The full
  4D Standard-Model chiral fermion (with the correct SU(2)_L×U(1)_Y assignments,
  anomaly cancellation, and Yukawa couplings) is a substantial build on top — but
  every ingredient is standard lattice-gauge technology.
- "Surmountable in principle" ≠ "done." It means the obstruction is a known
  engineering problem, not a no-go. That is a real change in status from "wall."
- Absolute masses remain blocked (ℏ + Gap 13), unchanged.

## Updated outlook for the particle sector

With v14 surmountable, the QNG particle program reduces to essentially ONE deep
problem — the **absolute scale (ℏ + Gap 13)** — plus the *engineering* of the
v13/v14 ontology (complex multiplets + domain-wall fermions), all of which is
known technology. The *structure* (forces on edges, hadrons as Skyrmions, the
Eightfold Way, chiral fermions via domain walls) is in place or reachable; the
*scale* is the frontier.
