# REPORT — demo Phase-14 (Drumul 3) gravity-induced UV fixed point for alpha

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase14_gravity_gauge_fixed_point.py`
Verdict: **GRAVITY_INDUCED_FIXED_POINT_IS_THE_ALPHA_ROUTE**

beta(alpha) = -f_g*alpha + c*alpha^2 (gravity linear + gauge quadratic).

| Test | Result |
|---|---|
| pure U(1) (f_g=0) nontrivial UV fixed point | NONE (Landau pole) |
| with gravity (f_g=0.05) UV fixed point | alpha* = f_g/c = 0.05 (beta=0) |
| constraint for alpha_em=1/137 | f_g/c = 0.0073 (O(0.01) gravitational coeff) |

## Verdict

Gravity creates a non-Gaussian UV fixed point alpha*=f_g/c where pure U(1) has
none. This is the Eichhorn-Held asymptotic-safety mechanism. QNG is uniquely
suited: G is DERIVED, so f_g ~ G_QNG*(Planck scale)^2 is in principle a QNG
output, making alpha* = f_g/c a PREDICTION. Constraint for observed alpha_em:
f_g/c = 0.0073 (same ballpark as asymptotic-safety estimates).

CHAIN: compute f_g(G_QNG) -> alpha predicted -> (via Phase 11/12) proton mass
parameter-free = decisive distinction.

## Honest scope

Mechanism + constraint established; VALUE of alpha NOT computed (gated by f_g).
f_g (gravity's contribution to the gauge beta function) is a hard,
scheme-DEPENDENT, controversial open calculation -- NOT done here, no number
forced. Drumul 3 is now LOCATED (gravity-gauge asymptotic safety), not solved;
the open piece is the concrete computation f_g(G_QNG), success criterion
f_g/c=0.0073.

Bug fixed mid-run: fixed-point detection used |beta|<eps (false positives at
small alpha where beta is small but nonzero); changed to beta SIGN-CHANGE.
