# Phase 5 — the genuine v13 baryon (and an honest correction to Phase 4)

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Probe: `demo-theory/tests/t_phase5_v13_skyrmion.py`
Artifact: `07_validation/audits/demo-phase5-v13-skyrmion-v1/`

---

## The discovery

v13's complex SU(2) doublet — assembled into the chiral field `U(x) ∈ SU(2)` —
hosts a **genuine baryon**, and it fixes three things at once that the U(1) `φ`
ring could not.

| Test | Result | Meaning |
|---|---|---|
| **T1** SU(2) hedgehog `B` | 0.77 → 0.86 → 0.91 (w=3,4,5) → **1** | genuine baryon, `B ∈ π₃(SU(2))=ℤ` |
| **T2** U(1) phase `B` | **−0.0000** (exact) | the `φ` ring is **not** a π₃ baryon (it is a π₁ vortex) |
| **T3** pion content | U(1): 1 ; SU(2): **3** | v13 gives the **pion triplet** (π⁺,π⁰,π⁻) |

The `B→1` convergence with hedgehog width (0.77→0.91) is the expected finite-
lattice discretization approach to the exact topological integer.

## The honest correction to Phase 4

Phase 4 called the QNG `φ`-rings "Skyrme-type baryons." **Phase 5 sharpens this
and partly corrects it:**

> The current QNG `φ`-ring is a **baby-Skyrmion** — its winding lives in
> `π₁(U(1))` (a vortex line), **not** in `π₃(SU(2))` where the real baryon number
> lives. A genuine baryon (B from π₃) **cannot be built from the U(1) phase
> alone** (T2: `B=0`). It **requires v13's SU(2) field** (T1: `B=1`).

So the Phase-4 statement "rings = baryons" is only *approximately* and
*topologically incompletely* true. The rings are baryon-*like* (they carry mass
= volume charge, and a collective-rotation J(J+1) band), but the exact baryon
*number* is a π₃ invariant that needs the SU(2) upgrade. This is more precise and
more honest.

## Why this elevates v13 from "a fix" to "the keystone"

v13 (adding the complex SU(2) doublet at nodes) was introduced in Phase 4b as
the matter the weak force acts on. Phase 5 shows the **same** ontology does three
independent jobs:

1. **(Phase 4b)** supplies the SU(2) **weak-force matter doublet** (gauge-
   invariant; W rotates isospin).
2. **(Phase 5 T1)** upgrades the baby-Skyrmion `φ`-ring to a **genuine B=1
   baryon** (π₃ topological charge).
3. **(Phase 5 T3)** completes the meson sector from one neutral pseudoscalar to
   the full **pion triplet** (the 3 SU(2) generators).

**One ontology addition closes three gaps.** That is the signature of a *right*
extension rather than an epicycle — the same field is forced by three different
physics requirements and satisfies all three.

## Inventory consequences

- **Baryons**: status sharpened — "baby-Skyrmion now (U(1), `B` from π₁),
  **genuine B=1 baryon after v13** (π₃)." Mass = volume charge (E4); rotational
  J(J+1) band (4d); absolute scale ⛔ (ℏ + Gap 13).
- **Mesons**: "one π⁰-like `φ`-quantum now → **pion triplet after v13**."

## Honest scope

- `B=0.86` (not exactly 1) is finite-lattice discretization; the trend → 1 is
  unambiguous, but a clean integer needs larger `L` or an improved topological
  charge operator (the standard "geometric" lattice `B`).
- This is the **kinematic/topological** content (the field hosts a B=1 texture).
  **Dynamical stability** (does the soliton hold its size, or collapse — Derrick's
  theorem) needs the Skyrme 4-derivative term — **Phase 6**.
- Absolute baryon mass still ⛔ (ℏ + Gap 13), unchanged.

## Next (Phase 6)

Derrick stability: a pure 2-derivative σ-model Skyrmion collapses; the
4-derivative **Skyrme term** stabilizes it at finite size. Demonstrate that
v13 + Skyrme term gives a **stable** B=1 soliton — i.e. the v13 baryon actually
exists as an object, not just a topological label.
