# theory-test-1 — an INDEPENDENT quantum-gravity container (the "is the box unique?" experiment)

Type: `charter`
Track: `theory-test-1` (deliberately SEPARATE from QNG; we try NOT to converge to it)
Author: C.D Gabriel
Started: 2026-06-03

## Purpose

Build a quantum-gravity "container" **from scratch**, starting only from the constraints
we already know any QG must satisfy, with a primitive ontology **deliberately different
from QNG's** (no node-graph with (σ, χ, φ) fields). Then derive upward — geometry → GR,
amplitudes → QM, and let the constants fall out of the dynamics — and **compare to QNG**:

- If an independent primitive still lands on QNG-like structure → evidence the QG box is
  **nearly unique** (strong result).
- If it lands somewhere genuinely different → **multiple** viable QG containers (also a
  strong result).

Either outcome is informative. The discipline is the same as the QNG track: **no forced
numbers, tensions flagged as openly as wins, honest about what is derived vs assumed.**

## The constraints (the "shape of the box" — what we ALREADY know any QG must satisfy)

These are primitive-agnostic. Any candidate container must meet them. WHY-we-know is in
brackets — this is what we can already see without the full theory.

- **C1 — GR limit.** Reduces to Einstein's equations (G_μν = 8πG T_μν) at large scale /
  weak field. [GR is experimentally exact from lab to cosmology.]
- **C2 — quantum.** Superposition, unitarity, an action quantum (ℏ). [QM is experimentally
  exact; gravity's source T_μν is quantum.]
- **C3 — finite d.o.f. per finite region (holographic / discrete).** Entropy ∝ AREA, not
  volume. [Bekenstein-Hawking S = A/4; holographic bound. The single strongest hint.]
- **C4 — UV-finite.** No infinities; a minimum scale or a UV fixed point. [Perturbative GR
  is non-renormalizable; needs a cutoff or special UV behavior.]
- **C5 — constants emerge.** c, G, ℏ (and ideally Λ) come OUT of the structure, not put in
  by hand. [A fundamental theory should not have these as free inputs.]
- **C6 — background independence.** Geometry EMERGES; no pre-given spacetime grid.
  [General covariance; Einstein's hole argument. NOTE: this is exactly where QNG
  COMPROMISES — it uses a fixed-ish lattice. A fresh box can be MORE ambitious here.]
- **C7 — Lorentz recovered.** No observable preferred frame at low energy (emergent or
  exact); only a tiny Planck-scale signature allowed. [Michelson-Morley + all LIV bounds.]

## Method (the order matters)

1. **Fix C1–C7** (this charter). Primitive-agnostic.
2. **Choose a PRIMITIVE deliberately different from QNG** (the one decision that shapes
   everything — see `01-primitive-choice.md`).
3. **Derive upward**: primitive + its dynamics → emergent geometry (test C1, C6, C7) →
   quantum amplitudes (test C2) → constants (test C5) → finiteness (C3, C4).
4. **Compare to QNG** at each rung: same? different? why?

Each step is a `theory-test-1/NN-*.md` derivation + a `theory-test-1/tests/tt1_*.py`
numerical check writing to `07_validation/audits/tt1-*/`.

## Honesty rules (inherited)

- No forced numbers / no numerology. A coincidence is rejected unless mechanism-backed.
- "Derived" vs "identified" vs "assumed" labelled explicitly (cf. QNG P109 audit).
- Tensions and failures recorded as prominently as successes.
- We actively TRY to avoid QNG; if we converge anyway, that convergence is a RESULT, not a goal.

## Status

- [x] C1–C7 charter written.
- [ ] Primitive chosen (`01-primitive-choice.md`) — **awaiting decision.**
- [ ] Emergent geometry / GR limit.
- [ ] Quantum amplitudes / QM limit.
- [ ] Constants.
- [ ] Comparison to QNG.
