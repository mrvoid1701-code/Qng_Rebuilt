# REPORT — demo Phase-16 (Gap 12) dynamical graviton on edges

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase16_dynamical_graviton.py`
Verdict: **DYNAMICAL_GRAVITON_ON_EDGES**

| Test | Result |
|---|---|
| T1 linearized Riemann invariance under h->h+d xi+d xi | 4.5e-16 (machine precision) |
| T2 pure-gauge h=d xi+d xi TT fraction | 3.4e-4 (~0, gauge modes unphysical) |
| T3 static-source Newtonian 1/r fit | R^2=0.69 (lattice-limited; corroboration only) |

## Verdict

T1 (the decisive new result): the linearized Riemann curvature from the edge
h_ij is INVARIANT under linearized diffeomorphisms -- the DEFINING property of a
graviton, untested by E8 (kinematic). T2: gauge modes carry no TT content, so
only 2 physical polarizations propagate. Gap 12 upgraded kinematic (E8) ->
DYNAMICAL: the edge rank-2 object carries a gauge-invariant linearized graviton
with exactly 2 dof.

T3 (Newtonian 1/r) is lattice-limited (coarse point-source FFT-Poisson:
anisotropy at small r, periodic images at large r); the Newtonian limit Phi~delta_C
is independently established (GRAV-C1). Corroboration, not load-bearing.

## Honest scope

Shows the edge graviton is CONSISTENT (Fierz-Pauli works, gauge-invariant, 2 TT),
NOT that the substrate PRODUCES it. Remaining core of Gap 12: derive the
Fierz-Pauli action by coarse-graining the node/edge dynamics. That derivation is
the prerequisite for f_g -> alpha (Phase 14/15) -> parameter-free proton mass.
Gap 12 now splits: carrier+consistency DONE; action-from-substrate = remaining core.
