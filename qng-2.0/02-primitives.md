# QNG 2.0 / 02 — the PRIMITIVES (ontology, rigorous)

Type: `definition`
Track: `qng-2.0`
Author: C.D Gabriel
Date: 2026-06-03

## Inputs

- [MANIFESTO.md](MANIFESTO.md) — design philosophy + the one primitive
- causal-set foundations validated in `theory-test-1` (rungs 1–6)
- QNG 1.0 field/QM engine (`demo-theory` P102–108)

## The fundamental objects (nothing else is primitive)

**PRIM-1 (spacetime = a causal set).** Spacetime is a locally finite partial order
`C = (E, ≺)`: a set of events `E` and a relation `≺` ("causally precedes") that is
- transitive: `x≺y ∧ y≺z ⇒ x≺z`,
- acyclic: never `x≺x` (no closed causal loops),
- locally finite: `|{z : x≺z≺y}| < ∞` for all `x≺y` (this IS discreteness).

There is NO background manifold, NO coordinates, NO metric, NO lattice. Geometry
(dimension, volume, metric, curvature) is RECONSTRUCTED from `≺` + counting (theory-test-1
rungs 1–3), never assumed.

**PRIM-2 (matter = a field on the events).** Matter is a complex field
`ψ : E → ℂ`, one amplitude per event. (This is QNG's matter degree of freedom: magnitude
`|ψ|` = matter density, phase `arg ψ` = QNG's φ. The "fields on a graph" of QNG 1.0
become "fields on a causal set.") Gauge/internal structure (later rungs) enriches the
value space `ℂ → ℂ^n` or a group; the scalar case is the foundation.

**PRIM-3 (one scale: the discreteness density).** The map to physical units is fixed by
ONE number: the mean density `ρ` = one event per fundamental 4-volume `V_0`. Setting
`V_0 = ℓ_P^4` defines the Planck length. This is the theory's single length input.

## The dynamics (one law)

**PRIM-4 (the double path integral).** Quantum dynamics is a sum over BOTH the causal set
AND the field:
```
        Z  =  Σ_{C}  ∫ Dψ   exp( i S[C, ψ] / ħ ),
        S[C, ψ]  =  S_grav[C]  +  S_field[C, ψ].
```
- `S_grav[C]` = the Benincasa–Dowker causal-set action (built from interval-cardinality
  counts; continuum limit `→ (1/16πG)∫√g R` ). Gravity = the order's curvature.
- `S_field[C, ψ]` = `Σ_x ψ*(x) (B + m²) ψ(x)` + interactions, where `B` is the
  Benincasa–Dowker discrete d'Alembertian (`→ □`). Matter dynamics = the field on the order.

**This is the whole theory.** Everything else (constants, GR, QM, matter spectrum) must be
DERIVED from PRIM-1…4. The mathematics is: order theory (posets) + discrete BD operators
+ a double path integral over `(C, ψ)`.

## What is primitive vs derived (honesty ledger)

| Object | Status |
|---|---|
| causal order `≺`, field `ψ`, density `ρ`, action `S` | **PRIMITIVE** (PRIM-1…4) |
| dimension, volume, metric, curvature | DERIVED from order+counting (tt1 R1–3) |
| Lorentz invariance | DERIVED (exact, Poisson order — tt1 R1) |
| Λ | DERIVED/predicted (≈1/√V — tt1 R4) |
| GR (Einstein eqns) | TO DERIVE (rung 2) — vary `S_grav+S_field` |
| QM (Schrödinger/Born) | TO DERIVE (rung 3) — the `∫Dψ` measure |
| c, G, ħ | TO PIN (rung "constants") — from `ρ`, `ħ`, the order |
| stable interacting matter solitons on a generic causet | **OPEN RISK** (rung 1) |

## Coherence already shown (rung 0)

A massive KG field on a Poisson causet has a DEFINITE MASS (on-shell `Q` clusters,
CV=0.019; `qng2_rung1_field_on_causet.py`) — so PRIM-2 fields live consistently on PRIM-1
order. The synthesis is well-defined; the rest is derivation.
