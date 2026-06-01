# REPORT — demo Phase-4d Skyrme collective quantization

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase4d_skyrme_quantization.py`
Verdict: **SKYRME_FRAMEWORK_VIABLE**

| Test | Result |
|---|---|
| moment of inertia I(R) (toroidal sigma_m, diameter axis) | R=3: I=5149; R=4: 10491; R=5: 18046 (I/(M R^2) 1.2->0.76, -> thin-ring 0.5) |
| J(J+1) band fit (N 1/2+, Delta 3/2+) | M0=865.8 MeV, c=97.7 MeV |
| predict J=5/2 | 1720 MeV vs N(1680) observed -> 2.4% error |
| R-vs-J | DER-QNG-038 conflated SIZE (R) and SPIN (J) |

## Verdict

QNG supplies a well-defined ring moment of inertia I(R) ~ 0.5 M R^2, so
collective quantization is well-posed. The lowest baryons fit a single J(J+1)
rotational band (5/2 prediction 2.4% from N(1680)). DER-QNG-038's R->particle
ladder conflated size and spin: N and Delta are the SAME B=1 soliton at J=1/2
vs 3/2, not different-R solitons. Rings = Skyrmions = a rotational baryon band.

## Honest blocker

The ABSOLUTE rotational scale is hbar^2/(2I) -- blocked by the unresolved hbar
program AND the Gap-13 Planck->MeV unit bridge. QNG gives the soliton + I(R)
structure; absolute baryon masses remain blocked. The win is STRUCTURAL
(principled framework replacing R-numerology), not a mass derivation.

## Scope

Moment of inertia computed for an IDEALIZED toroidal sigma_m profile (not a full
v8 dynamical ring). The J(J+1) band fit is the universal Skyrme/collective-
quantization consequence that QNG inherits by being a topological-soliton theory;
the QNG-specific content is the soliton (winding=M_ring) and I(R).
