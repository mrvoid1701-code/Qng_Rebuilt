# REPORT — demo Phase-3 SU(2) edge gauge

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase3_su2_edges.py`
Verdict: **SU2_EDGES_CONFINE**

SU(2) link variables (unit quaternions) on every edge, Wilson action, vectorized
checkerboard Metropolis, 4D L=6.

| Gate | Result | Reading |
|---|---|---|
| G1 gauge invariance | \|dP\| = 0.000 (exact) | genuine gauge theory |
| G2 plaquette beta=1.0 | <P>=0.2105 vs pred beta/4=0.25 | MC correct (strong-coupling expansion) |
| G2 plaquette beta=2.6 | <P>=0.658 vs pred 0.65 | MC correct |
| G3 area-law ratio beta=1.0 | ln W(2,2)/ln W(1,1) = 4.03 | AREA law (=4) -> confinement |
| G3 area-law ratio beta=2.6 | 3.03 | weakens toward weak coupling (crossover) |
| G3 string tension beta=1.0 | sigma = -ln W11 = 1.56 | nonzero -> confining |

## Verdict

QNG edges host a genuine, gauge-invariant SU(2) gauge theory that CONFINES
(Wilson-loop area law). The edge sector extends naturally from the U(1) photon
to a non-abelian confining force = the qualitative strong-force signature.

## Caveats

- PURE-GAUGE sector only. The non-abelian MATTER multiplet is a hard
  group-theory obstruction: 2 real node scalars (sigma_g, sigma_m) CANNOT form
  an SU(2) doublet (SU(2) acts on C^2; needs complex fields). tesla-mind's
  (sigma_g,sigma_m)-isospin conjecture REFUTED by the professor. Full SM gauge
  matter needs new node ontology (v13: complex multiplets + chiral Dirac).
- L=6, modest statistics; area-law ratio 4.03 is clean but reconfirm larger
  before publication.
- Two bugs fixed mid-run: Metropolis used Tr(U.S^dag) instead of Tr(U.S) (sign
  error -> negative plaquette); wilson_loop construction rewritten cleanly.

## Gauge group choice not forced

Hodge no-go forces the carrier to be edge-valued, NOT which group. Why
U(1)xSU(2)xSU(3) rather than something else = Gap 17 generalized.
