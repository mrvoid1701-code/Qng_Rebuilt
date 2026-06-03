# QNG 2.0 — a coherent synthesis quantum-gravity theory

Type: `manifesto`
Track: `qng-2.0` (fresh start; supersedes the `demo-theory` QNG 1.0 line conceptually)
Author: C.D Gabriel
Started: 2026-06-03

## The design philosophy (read this first)

QNG 2.0 is built by combining the **correct, load-bearing strengths** of the leading QG
containers — but **NOT by gluing pieces**. Theories are not Lego: string theory needs a
continuous 10D background + supersymmetry; causal sets need pure discreteness + no
background; QNG 1.0 needs a fixed lattice + fields. Their PRIMITIVES conflict, so a naive
merge is incoherent.

The right way (and the one the `theory-test-1` comparison, rung 6, pointed to): take each
theory's design LESSON — what it is good at and WHY — and choose **ONE coherent primitive**
that can host all the strengths at once.

## The one primitive

> **A quantum, dynamical FIELD living on a GROWING CAUSAL SET.**

In one line: **QNG 1.0's dynamical-field engine, rebuilt on a causal-set foundation
instead of a fixed cubic lattice**, with holographic finiteness as the consistency law.

State: a causal set `C` (events + order `≺`, locally finite) **together with** fields
`Φ: C → (values)` carrying QNG's degrees of freedom (a complex matter field, a phase, a
geometry field). Dynamics: a double path integral
```
        Z = Σ_{causal sets C}  ∫ DΦ  exp( i S[C, Φ] )
```
S[C,Φ] = (causal-set gravitational action, Benincasa-Dowker) + (field action built from
the causet d'Alembertian B). Order theory + discrete BD operators + this double integral
is the mathematics of QNG 2.0.

## Provenance — which strength comes from where (and WHY it's coherent)

| Strength | Inherited from | Mechanism in QNG 2.0 |
|---|---|---|
| background independence | causal sets | no grid; geometry (incl. dimension) emerges from order |
| **exact Lorentz invariance** | causal sets | Poisson order has no preferred frame (fixes QNG 1.0's lattice breaking) |
| **Λ ~ 1/√V ≠ 0** | causal sets | Poisson number-volume fluctuation (fixes QNG 1.0's Λ=0/Gap-5) |
| **field dynamics, QM, matter** | QNG 1.0 | fields Φ on the causet; Schrödinger/Born/matter=\|ψ\|² engine |
| finite d.o.f. per region | string/holography (B-H) | discreteness + holographic bound as a CONSISTENCY condition |
| GR limit | causal sets + QNG | BD d'Alembertian → □ + curvature; coarse-grained field → Einstein |

The combination is coherent because all strengths now ride on ONE primitive: fields on a
causet. Causal-set foundations + QNG dynamics are compatible (a field is just a function
on the event set); string's lesson enters only as a bound, not as 10D/SUSY baggage.

## What QNG 2.0 must fix vs QNG 1.0 (the point of the upgrade)

1. **Background dependence** — 1.0 used a fixed cubic lattice; 2.0 uses an order with no grid.
2. **Lorentz only emergent** — 1.0's lattice breaks Lorentz (η_LV); 2.0 is Lorentz-exact.
3. **Λ = 0 / Gap 5** — 1.0 forced Λ=0 then needed a separate holographic V_0; 2.0 predicts Λ~1/√V.

…while KEEPING 1.0's wins (the "+" the user asked for): the derived QM (Schrödinger, Born
rule as attractor, decoherence), matter=\|ψ\|², the hadron/topology results, c/G/ℏ.

## The honest risk (must be tested, not assumed)

Putting QNG's fields on a random causal set is NOT guaranteed to work. Open questions the
track must SETTLE numerically, not paper over:
- Can a STABLE matter soliton (QNG's rings/Skyrmions) exist on a non-manifold-like random
  causet, or only on manifold-like ("faithfully embeddable") ones? (the swerves/locality problem)
- Does the field dynamics stay local (the BD operator is mildly non-local)?
- Does the matter sector that QNG 1.0 built survive the foundation swap?

If any fails, that is a RESULT (a real constraint), reported as openly as a success.

## Rung plan

- R0: **coherence proof** — a field lives on a causal set with a well-defined wave operator
  (massive KG) on a background-free, Lorentz-exact substrate. `tests/qng2_rung1_field_on_causet.py`
- R1: matter — can a stable localized soliton (QNG ring/Skyrmion analogue) live on the causet?
- R2: GR — coarse-grained field + BD action → Einstein equations with the causet Λ.
- R3: QM — the field path integral → Schrödinger/Born (import QNG 1.0's arc onto the causet).
- R4: constants — c, G, ℏ from the field-on-causet action; Λ from counting (already, rung4 tt1).
- R5: predictions — where QNG 2.0 differs from BOTH parents + from QNG 1.0 (testable).

## Honesty rules (inherited, non-negotiable)
No forced numbers / no numerology. Label derived vs identified vs assumed. Report
failures as prominently as successes. Verify COHERENCE (no conflicting axioms) at each rung.
