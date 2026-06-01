# REPORT — demo Phase-37 quantum gravity: what replaces the black-hole singularity?

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase37_blackhole_core.py`
Verdict: **SINGULARITY_REPLACED_BY_FINITE_NODE_CORE**

Question (user): in QNG, what is at the center of a black hole instead of a singularity?

GR: center = singularity (density, curvature -> infinity). QNG forbids this for
two discrete reasons: (a) scalars are BOUNDED, sigma_g, sigma_m in [0,1] — matter
= sigma_m concentration, gravity = sigma_g depletion, so there is a hard ceiling
of one node-mass per cell; (b) the lattice has a minimum cell a_L = 0.305 l_P.

**T1 — central potential is FINITE.** Solving the QNG screened-Poisson equation
for a concentrated source on a 3D lattice (FFT Green's function) gives
Phi(0) = 0.243 (stable across L=16,24,32). The continuum -1/r DIVERGES at r=0;
the lattice regulates the UV → no infinite potential.

**T2 — maximum density is FINITE.** At most one node-mass a_M=1.524 m_Pl per cell
a_L^3 → rho_max = a_M/a_L^3 = 53.7 Planck densities. The GR singularity (rho →
infinity) is replaced by this finite ceiling.

**T3 — singularity → finite core.** A black hole of mass M has its center
replaced by a maximally-packed node-core of radius r_core ~ (M/rho_max)^(1/3)
(e.g. ~5.7e24 l_P for a solar-mass BH). Inside, sigma_g is floored at 0 (maximum
depletion) → curvature SATURATES rather than diverging — a regular (non-singular)
black hole / "Planck star".

Honest scope: static-potential + bounded-density argument, not a dynamical
collapse simulation; O(1) coefficients in rho_max, r_core depend on the
coarse-graining map. Robust content: (i) lattice potential finite at the center
(no 1/r blow-up); (ii) bounded scalars + minimum cell → finite maximum density.
Same discreteness that capped the graviton frequency (Phase 36) — the Planck
lattice is the natural regulator that tames gravity's infinities.
