# GPU-031d Analysis: Ring formation under DER-QNG-050 exact F_A fails

Date: 2026-04-21
Run: L=20 R=4, three-phase formation protocol, exact_a=True throughout —
ABORTED at t=200 in Phase 1.

## Outcome: saturation at Phase 1

| t (lu) | M_ring    | H         | sm_min | sm_max | T_m     |
|-------:|----------:|----------:|-------:|-------:|--------:|
| 0      | 0         | -226      | 0.500  | 0.500  | 0       |
| 100    | -3838     | +164502   | 0.155  | 0.999  | 165317  |
| 200    | -3711     | +674830   | 0.367  | 0.998  | 675619  |

The ring cannot even BEGIN to form. In Phase 1 (v_couple=False), with
only a phi 2π-winding initial condition and uniform sigma_m=0.5, the
exact F_sm_XY condensation drives sigma_m to saturate near 1.0 across
the bulk within ~100 lu. By t=200, M_ring has flipped sign (-3711 means
sm_mean > SIGMA_M_REF; i.e., most nodes have sm near 1) and kinetic
energy in pi_m has exploded 60000x above the channel's intended scale.

## Interpretation

This is a direct confirmation of DER-QNG-051: the v7 E_phi Hamiltonian
with sigma_m weighting has no bounded ground state under canonical
dynamics. The condensation force has no counter-term strong enough to
hold sigma_m below saturation.

## Consequence

Scenario A (particle = bounded dynamical orbit in v8 phase space) is
not testable as currently formulated. The cached ring used in
GPU-030/031/031b/031c was an artifact of the v7 gradient-flow
truncation; under the full canonical action, no such ring exists.

## Recommended next step

See DER-QNG-051 (04_qng_pure/qng-v8-matter-vacuum-instability-v1.md)
for four options (R1 pure XY / R2 sigma_m^4 / R3 compact sigma_m /
R4 accept + v9 unification). R1 is the cheapest test; R4 is the
honest verdict.
