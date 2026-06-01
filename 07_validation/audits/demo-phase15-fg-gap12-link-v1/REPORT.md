# REPORT — demo Phase-15 (Drumul 3 frontier) f_g <-> Gap 12 link

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase15_fg_gap12_link.py`
Verdict: **FG_NEEDS_GAP12 + PLAUSIBLE_WITH_DERIVED_G**

## Structural link

Drumul 3's final step (compute f_g -> alpha via Phase 14's fixed point) requires
the graviton propagator + gauge-graviton vertex at one loop. QNG's graviton is
only KINEMATIC so far (E8: rank-2 edge, 2 TT pols); its DYNAMICS are Gap 12
(open). So:

  Drumul 3 (f_g -> alpha)  REQUIRES  Gap 12 (dynamical graviton).

The two hardest open problems are LINKED. Solving Gap 12 enables computing
f_g(G_QNG), hence alpha (Drumul 3), hence (Phase 11/12) a parameter-free proton
mass.

## Plausibility (NOT a derivation)

f_g ~ k_loop * G_QNG * mu^2; at the fixed point mu^2~1 (substrate units), so
f_g ~ k_loop * G_QNG with G_QNG=0.0583 (DERIVED). Reproducing alpha_em=0.0073
needs k_loop = f_g/G_QNG = 0.125 -- an O(0.1) one-loop coefficient (loop factors
~1/(4-8pi)~0.04-0.08, x O(1) numerator ~0.1). So the required gravitational
coefficient is in the NATURAL range; the scenario is not fine-tuned, and the
derived G_QNG sits in the right ballpark.

## Honest scope

Order-of-magnitude plausibility only. f_g is NOT computed (needs Gap-12 graviton
dynamics + a scheme choice; scheme-dependent and controversial). alpha remains
uncomputed. What is established: Drumul 3 reduces to Gap 12 + one loop integral,
with G_QNG in the right ballpark for a natural loop coefficient.
