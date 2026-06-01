# REPORT — demo Phase-9 (v14) domain-wall chiral fermion

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase9_v14_domain_wall.py`
Verdict: **V14_CHIRAL_FERMION_OK**

1D lattice Dirac + Wilson term + periodic kink-antikink mass domain wall
(Kaplan / Callan-Harvey).

| Test | Result |
|---|---|
| near-zero modes, no Wilson (r=0) | 4 (doublers) |
| near-zero modes, Wilson (r=1) | 2 (doublers gapped; next \|E\|=0.33) |
| localization | one mode per wall (sites 30, 90) |
| chirality (sigma_y projected into zero subspace) | +1.0 (wall 30), -1.0 (wall 90) |

## Verdict

The Wilson term gaps the doublers; exactly one chiral mode binds to each wall
with exact opposite chirality (left on kink, right on antikink). Separating the
walls (extra dimension / overlap) leaves a single chiral fermion. This SURMOUNTS
the Nielsen-Ninomiya wall of Phase 4c.

v14 (chiral fermions = quarks/leptons) is NOT blocked in principle -- solvable
with known lattice-chiral technology (domain-wall/overlap/Ginsparg-Wilson). The
single genuinely hard remaining wall is the ABSOLUTE SCALE (hbar program +
Gap 13), not chirality.

## Scope

Domain-wall mechanism in 1D (doubler removal + chiral wall modes). Full 4D SM
chiral fermion (SU(2)_L x U(1)_Y assignments, anomaly cancellation, Yukawa) is a
substantial standard-technology build on top. Absolute masses still blocked.

## Note

Initial setup used open BC + single wall -> spurious boundary mode (2 modes, one
at the edge). Fixed to periodic BC + kink-antikink (the correct domain-wall
geometry). Chirality measured by projecting sigma_y into the degenerate zero-mode
subspace and diagonalizing (eigh returns a mixed basis otherwise).
