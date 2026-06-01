# REPORT — demo Phase-28 soliton breathing mode (radial excitation)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase28_breathing_mode.py`
Verdict: **BREATHING_MODE_EXISTS**

Collective-coordinate breathing of the Skyrmion (E2=253.5, E4=17.6 from Phase 6):
- lambda* = sqrt(E4/E2) = 0.263 (soliton size, Derrick minimum)
- M_cl = 2 sqrt(E2 E4) = 133.6
- E''(lambda*) = 2 E4/lambda*^3 = 1924
- breathing freq omega_b = sqrt(E''/Lambda_b) = 2.755 (Lambda_b ~ E2)
- EXPERIMENT: integrate lambda(t) from 1.3 lambda* -> clean oscillation in
  [0.203,0.343], measured omega_b = 2.720 (matches analytic 2.755).

So the soliton-particle has internal structure: a definite size + a BREATHING
(radial) excited state -- the Roper N(1440) analog -- on top of the rotational
J-band (Phase 4d) and the topological spectrum.

Honest: the absolute breathing frequency depends on the collective kinetic mass
Lambda_b (O(1) factor) and the overall scale (alpha_s); omega_b/M_cl = 0.021 here
vs the Roper fraction 0.53 -- so the Roper identification is QUALITATIVE (the
radial excited state EXISTS). The robust result is the EXISTENCE of the breathing
mode (the soliton oscillates, has radial excitations).
