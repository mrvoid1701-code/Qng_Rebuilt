# REPORT — demo Phase-6 Skyrme stability (Derrick)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase6_skyrme_stability.py`
Verdict: **V13_BARYON_STABLE**

| Quantity | Value |
|---|---|
| E2 (sigma-model, 2-deriv) | 253.5 (>0) |
| E4 (Skyrme, 4-deriv) | 17.6 (>0) |
| sigma-model-only min | lambda -> 0.20 (edge = COLLAPSE) |
| with-Skyrme min | lambda* ~ 0.26-0.30 (STABLE) |
| classical mass M_cl = 2 sqrt(E2 E4) | 133.4 (natural units) |

## Verdict

Derrick's theorem confirmed: the pure 2-derivative chiral soliton collapses
(E=lambda*E2 minimized at lambda->0); the 4-derivative Skyrme term gives
E=lambda*E2+E4/lambda with a stable minimum at lambda*=sqrt(E4/E2). The v13
baryon EXISTS as a stable finite-size object with classical mass 2 sqrt(E2 E4).

Combined with Phase 5 (B=1 topology) and 4d (J(J+1) rotational band + moment of
inertia), the v13 baryon is structurally complete except the absolute MeV scale
(blocked by hbar + Gap 13). The Skyrme term is the natural 4-derivative piece of
the chiral Lagrangian that QNG's edge/higher-order couplings generate.

## Scope

E2,E4 for the fixed hedgehog profile (Derrick scaling minimum, standard
first-pass). Variational F(r) would refine M_cl. M_cl in natural units; MeV
needs hbar+Gap-13.
