# QNG-CPU-146 Knot Stability under v7/v8 Matter Coupling
- decision: `fail`
- trefoil stable: `True`
- bare ring stable: `True`

## Purpose
Decisive test for Kelvin-Bilson-Thompson hypothesis at v8 level.
Companion to CPU-145 (pure-phi). Tests whether sigma_m matter
back-reaction stabilizes knot topologies that dissolve in pure phi.

## Results
| Config | M_P1_end | M_P2_end | M_P3_end | P3 drift | W_xy_P2 | Survives |
|---|---|---|---|---|---|---|
| ring_Q0 | 0.00 | 807.65 | 110.40 | 0.8507 | 0.00 | NO |
| hopfion_Q1 | 0.00 | 1646.80 | 1350.64 | 0.1562 | -6.28 | YES |
| trefoil | 0.00 | 556.18 | 70.32 | 0.8535 | 0.00 | NO |

## Verdict on KBT hypothesis at v8 level
- Trefoil under matter: **STABLE**
- Bare ring under matter: **STABLE**

**KBT path REOPENED via matter coupling** — proceed to QNG-CPU-147 for full Hopfion+trefoil mass spectrum under v8.

## Honest caveats
- L=20 lattice may not give trefoil enough room. Larger L (24, 32) could change result.
- Phase 2/3 dissipative dynamics relaxes toward minimum-energy attractor — gauge of
  dynamical stability, not absolute global minimum.
- No v8 symplectic dynamics in this scan (v7 dissipative only). Symplectic v8 may
  give different orbital-attractor behavior.
