# Phase 14 (Drumul 3) — α from a gravity-induced UV fixed point

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01 — the correct route located; value gated by f_g(G)`
Probe: `demo-theory/tests/t_phase14_gravity_gauge_fixed_point.py`
Artifact: `07_validation/audits/demo-phase14-gravity-gauge-fp-v1/`

---

## The route Phase 13 pointed to, made concrete

Phase 13 proved the Stability Principle is blind to α_em and redirected to an
**RG-fixed-point** principle. Phase 14 makes that concrete via the mechanism QNG
is uniquely suited for — a **gravity-induced UV fixed point** (Eichhorn-Held):

```
   d α / d ln μ  =  − f_g · α   +   c · α²
                    (gravity,      (gauge loops,
                     linear)        c>0 for U(1)+matter)
```

| Test | Result |
|---|---|
| pure U(1) (f_g=0): β = c α² | **no nontrivial UV fixed point** (Landau pole) |
| with gravity (f_g>0) | **UV fixed point at α\* = f_g/c** (demonstrated, β(α\*)=0) |
| constraint for α_em = 1/137 | **f_g/c = 0.0073** (an O(0.01) gravitational coefficient) |

> Pure U(1) has only the trivial fixed point (and a Landau pole). The
> **gravitational term creates a non-Gaussian UV fixed point** `α* = f_g/c`. At
> that fixed point the trans-Planckian coupling is FIXED — and the IR value of
> α is then determined. **α is no longer a free input; it is the fixed-point
> ratio f_g/c.**

## Why QNG is the natural home (the QNG-specific content)

Generic asymptotic safety needs gravity + gauge with gravity's contribution f_g.
**QNG has exactly this, and more: G is DERIVED** (theory-v2 ch.04). So:
- `c` (gauge-loop coefficient) is known (matter content).
- `f_g` (gravitational coefficient) is `∝ G · (Planck scale)²` — **in principle a
  QNG OUTPUT**, since G_QNG is derived.
- Therefore `α* = f_g/c` would be a **QNG PREDICTION**, not an input.

The constraint to land on the observed α_em = 1/137 is `f_g/c ≈ 0.0073` — an
O(0.01) gravitational coefficient, the **same ballpark** as typical
asymptotic-safety estimates of the gravitational anomalous dimension.

## The decisive-distinction chain (now fully located)

```
   compute f_g(G_QNG)  ──→  α* = f_g/c = α_em   (Drumul 3, parameter-free α)
                                  │
                                  ▼
   Phase 12: M_proton = k·Λ_QCD,  Λ_QCD = m_Planck·exp(−2π/(b₀ α_s))
                                  │
                                  ▼
   parameter-free PROTON MASS  =  the decisive distinction from all other theories
```

If `f_g` is computed from `G_QNG`, then α is predicted, then (via Phase 11/12)
the proton mass is predicted **with no free inputs** — which no other theory can
do. **This is the single highest-value target, now precisely located: compute
`f_g(G_QNG)`** — gravity's contribution to the gauge beta function, from QNG's
derived gravitational sector.

## Honest scope (critical — no number forced)

- The **mechanism** (gravity creates a UV fixed point) and the **constraint**
  (`f_g/c = α_em`) are established. **The VALUE of α is NOT computed** — it is
  gated by `f_g`.
- `f_g` (gravity's contribution to the gauge beta function) is a **hard,
  scheme-DEPENDENT** calculation — genuinely **controversial** even in the
  asymptotic-safety literature (whether gravity contributes to gauge running at
  all, and the sign/size of f_g, are debated). I do **not** claim to have
  computed it.
- So Drumul 3 is **located, not solved**: the route is gravity-gauge asymptotic
  safety; the open computation is `f_g(G_QNG)`; the success criterion is
  `f_g/c = 0.0073`.

## Status of Drumul 3 after Phases 13 + 14

| Step | Status |
|---|---|
| Stability Principle for α_em | **ruled out** (Phase 13, proven) |
| The correct route | **gravity-induced UV fixed point** `α*=f_g/c` (Phase 14) |
| QNG suitability | **uniquely suited** — G derived → f_g a potential QNG output |
| The open computation | **`f_g(G_QNG)`** — gravity's gauge-beta contribution (hard, scheme-dependent) |
| Success criterion | `f_g/c = 1/137 = 0.0073` |

Drumul 3 is now a **well-posed, QNG-specific calculation** (compute f_g from the
derived gravitational sector), not a vague "derive α." That is real progress:
the hardest number in physics is reduced, in QNG, to one concrete (if hard)
gravitational computation — with the payoff that it would make the proton mass
parameter-free.
