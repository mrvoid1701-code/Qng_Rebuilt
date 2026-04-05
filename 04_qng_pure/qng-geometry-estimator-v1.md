# QNG Geometry Estimator v1

Type: `derivation`
ID: `DER-QNG-007`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit reference estimator that maps the coherence-sensitive effective field `C_eff` into a local geometric proxy.

## Inputs

- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-emergent-geometry-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-geometry-v1.md)
- [gr-observables-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-observables-v1.md)

## Scope restriction

This file does not claim the final spacetime metric of QNG.

It defines only a first testable local proxy on a toy ordered chart.

That is enough for the rebuild because the immediate question is:

- can coherence structure generate a controlled geometric object at all

before we ask whether that object is the final physical metric.

## Reference chart

For the current toy validation layer, nodes are read on the ordered cycle already present in the native test graph.

This gives a one-dimensional probe chart:

`u_i = i Delta_u`

with periodic boundary conditions.

## Discrete coherence probes

From `C_eff(i)`, define:

`grad_C(i) = (C_eff(i+1) - C_eff(i-1)) / (2 Delta_u)`

`lap_C(i) = (C_eff(i+1) - 2 C_eff(i) + C_eff(i-1)) / (Delta_u^2)`

and the nonnegative curvature-sensitive proxy:

`K_C(i) = max(0, -lap_C(i))`

## Reference estimator

The first local Euclideanized metric proxy is:

`g_ref(i) = diag( 1 + a K_C(i), 1 + b K_C(i) + c |grad_C(i)|^2 )`

with positive coefficients `a, b, c`.

## Why this form is useful

It has the right minimal structural features:

- depends on `C_eff`, not directly on raw phenomenology
- is local
- is positive definite by construction
- reacts to both local coherence curvature and coherence gradient

## Signature note

The reference proxy is Euclideanized on purpose.

At this stage we are checking:

- existence of a stable geometry-generating map

not yet:

- final Lorentzian signature recovery

## GRAV-C1 correction (added post DER-QNG-012)

**Forward reference — read before using this estimator for gravitational physics.**

`DER-QNG-012` §6.3 identifies a biharmonic obstruction: using `K_C(i) = -lap_C(i)` as
the gravitational potential proxy leads to `∇²Ψ ∝ ∇²S_src` (biharmonic), not
`∇²Ψ ∝ S_src` (Poisson). A uniform mass source would then produce zero potential — wrong.

**Convention GRAV-C1** (canonical from DER-QNG-012 onwards):
```
Phi(x) ∝ delta_C(x) = C_eff(x) - C_ref
```
The Newtonian gravitational potential is proportional to the coherence *deviation*
`delta_C`, **not** to the Laplacian of `C_eff`.

The `g_ref` estimator defined in this document (`K_C = max(0, -lap_C)`) remains a
valid local curvature proxy for geometric visualization purposes, but it is **not**
the Newtonian potential. Any phenomenology or claim that requires a Newtonian
potential must use `delta_C` directly via GRAV-C1.

See `DER-QNG-012` §6.3 and `DER-QNG-018` §1 for full derivation.

---

## Immediate interpretation

In the rebuild, the first geometry claim becomes:

- `C_eff` supports a local geometric proxy through discrete coherence curvature

This is already cleaner than the old compression:

- `Sigma` directly generates everything

## What would count as success

The reference estimator is useful if it satisfies:

1. positivity
2. bounded or controlled growth
3. sensitivity to coherence curvature
4. distinguishability between history-enabled and present-only runs

## What would count as failure

This line weakens if:

- the proxy is numerically unstable
- the proxy depends more on memory-load than on coherence
- or the proxy cannot retain a history imprint once built from `C_eff`

In that case, the split effective layer would need revision.
