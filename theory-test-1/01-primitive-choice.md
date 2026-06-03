# theory-test-1 / 01 — the primitive: CAUSAL ORDER ONLY

Type: `definition`
Track: `theory-test-1`
Author: C.D Gabriel
Date: 2026-06-03

## Inputs

- [CHARTER.md](CHARTER.md) — constraints C1–C7

## The primitive

The fundamental object is a **causal set** (causet): a set `C` of discrete elements
("events") with a single relation `≺` ("precedes"), required to be:

- **transitive**: `x ≺ y` and `y ≺ z` ⟹ `x ≺ z`,
- **irreflexive/acyclic**: no `x ≺ x` (no closed causal loops),
- **locally finite**: between any `x ≺ z`, only finitely many `y` with `x ≺ y ≺ z`
  (this is the discreteness — C3).

**That is ALL.** No coordinates, no metric, no graph embedding, no fields. "Order +
number = geometry" (Hawking–Malament–Sorkin): the causal order fixes the conformal
geometry, and **counting elements** fixes the volume — together they give the full
Lorentzian metric. Spacetime is to be RECOVERED, never assumed.

## Why this is maximally independent of QNG (and honest about it)

| | QNG | theory-test-1 |
|---|---|---|
| primitive | node fields (σ_g, σ_m, χ, φ) on a graph | events + causal order only |
| background | a fixed-ish **cubic lattice** (a background!) | **none** — order is all there is |
| dimension | put in by hand (3+1 cubic) | **must EMERGE** from the order |
| Lorentz | **emergent** (lattice breaks it; recovered at low E) | **exact in the mean** (Poisson sprinkling has no preferred frame) |
| dynamics | deterministic field update | sum-over-causets (a quantum partition function) |

So this box differs from QNG on every axis that matters — especially **C6 (background
independence)**, which QNG compromises and this does not. If we still end up at GR + QM +
similar constants, that convergence is a genuine result about box-uniqueness.

## Plan (rungs up the ladder)

1. **Geometry from order** — recover the spacetime DIMENSION from pure causal order
   (Myrheim–Meyer). First test: `tests/tt1_dimension_from_order.py`. [this establishes
   the box produces geometry at all — C1/C6 backbone]
2. **Volume + metric** — order + counting → Lorentzian distance (longest-chain) → metric.
3. **GR limit** — curvature from the causet (Benincasa–Dowker d'Alembertian / action). [C1]
4. **Constants** — Sorkin's Λ ~ ±1/√V from Poisson fluctuations of the number-volume
   relation. [C5 — the first constant, and a famous from-scratch prediction]
5. **QM** — sum-over-causets as a quantum amplitude; decoherence / quantum measure. [C2]
6. **Compare to QNG** at each rung.

## Status
- [x] primitive declared.
- [ ] rung 1 (dimension from order) — `tests/tt1_dimension_from_order.py`.
