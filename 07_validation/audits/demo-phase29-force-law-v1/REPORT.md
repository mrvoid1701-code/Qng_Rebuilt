# REPORT — demo Phase-29 inter-soliton force (binding)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase29_force_law.py`
Verdict: **SOLITON_PAIR_IS_BOUND** (force attractive)

Static energy E(d) of a vortex-antivortex pair vs separation (gradient energy):
E rises monotonically (1.87 at sep 8 -> 16.5 at sep 88), so F = -dE/dd < 0
ATTRACTIVE -- the +/- pair is BOUND (consistent with Phase-27 annihilation).

HONEST: the precise law is NOT cleanly logarithmic here (log fit R^2=0.78, energy
grows ~linearly) because the UNRELAXED algebraic ansatz psi=(z+d)conj(z-d) is not
the minimum-energy config at each d and overestimates the gradient energy. A
clean 2D log-Coulomb law (A=pi*beta) needs relaxing the field at each separation
(not done). Robust result = QUALITATIVE: attractive, binding force. 3D ring/
Skyrmion force = CPU-049/050 Lennard-Jones-like (repulsive core + attractive
tail, equilibrium d~3 lambda = nuclear/molecular binding).
