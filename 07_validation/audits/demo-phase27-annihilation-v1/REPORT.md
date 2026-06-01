# REPORT — demo Phase-27 soliton annihilation -> radiation

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase27_soliton_annihilation.py`
Verdict: **ANNIHILATION_TO_RADIATION**

Dynamical particle-antiparticle experiment on the QNG phi-soliton (2D, KG).

A. vortex(+1) + antivortex(-1): ATTRACT -> ANNIHILATE.
   defects (plaquette vorticity): (1,1) -> (0,0); defect spread 13.5 -> 0 lu.
B. RADIATION: outer-annulus (r>L/3) energy rises 2.53 -> 4.23 (+67%) as the
   released energy propagates out at ~c_phi.

So the pair annihilates (net topological charge 0, conserved through to 0) and
its energy escapes as massless phi-radiation -- genuine matter-antimatter ->
radiation, a dynamical substrate behavior (not assumed).

Notes: on a torus net winding must be 0, so the +1/-1 pair is the clean
experiment; like-charge repulsion needs compensating defects (4-body). U(1)
phi-vortex (baby-Skyrmion); SU(2) Skyrmion would annihilate similarly with richer
(pion-radiation) structure. Fixes mid-run: replaced fragile coherence-argmin
tracker with plaquette vorticity (+1 vortex / -1 antivortex); built smooth
multi-vortex via complex product psi=prod(z-a)^q (no branch-cut artifacts).
