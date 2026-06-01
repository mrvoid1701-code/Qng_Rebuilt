# REPORT — demo Phase-8 SU(3) Eightfold Way

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase8_su3_eightfold.py`
Verdict: **EIGHTFOLD_WAY_FROM_SKYRME**

WZW constraint Y_R = N_c*B/3 = 1 (N_c=3 edge-color Phase 3, B=1 Skyrmion Phase 5)
selects the lowest SU(3)-flavor baryon multiplets:

| Multiplet | rep | dim | J | content |
|---|---|---|---|---|
| Octet | (1,1) | 8 | 1/2 | N, Lambda, Sigma, Xi |
| Decuplet | (3,0) | 10 | 3/2 | Delta, Sigma*, Xi*, Omega |

Spin from the isospin of the Y=1 state (octet 1/2->J=1/2; decuplet 3/2->J=3/2).
Matches the observed Eightfold Way of light baryons.

Scale-free mass relations (verified on PDG, not blocked by hbar/Gap-13):
- Gell-Mann-Okubo octet: 2(N+Xi)=3Lambda+Sigma -> 4514 vs 4541 (0.6%).
- Decuplet equal spacing: 153/148/139 MeV (~147); apex = Omega- (I=0,Y=-2,J=3/2).

## Scope

Representation theory + Skyrme WZW selection with QNG's N_c (edge-color) and
B (Skyrmion). Multiplet STRUCTURE is reproduced. Intra-multiplet splitting
MAGNITUDE needs flavor-SU(3) breaking (strange mass); absolute masses need
hbar+Gap-13. Requires promoting v13 SU(2) -> SU(3) flavor ontology.
