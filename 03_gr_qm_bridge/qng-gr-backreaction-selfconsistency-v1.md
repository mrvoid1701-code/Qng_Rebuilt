# QNG GR Back-Reaction Self-Consistency v1

Type: `derivation`
ID: `DER-BRIDGE-021`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test whether the three-channel back-reaction closure v3 admits a
self-consistent fixed point in the proxy sense.

A self-consistent fixed point exists if, when the closure potential
`Psi_BR3` is fed back into the initial conditions and a new closure
potential `Psi_BR3'` is computed, the system contracts:

`||Psi_BR3' - Psi_BR3|| < epsilon ||Psi_BR3||`

for some contraction ratio `gamma < 1`.

## Inputs

- [qng-gr-backreaction-closure-v3.md](qng-gr-backreaction-closure-v3.md)
- [qng_gr_backreaction_closure_v3_reference.py](../../tests/cpu/qng_gr_backreaction_closure_v3_reference.py)

## Scope

This file defines only a first proxy for self-consistency.

It does not define:

- a proof that the fixed point is unique
- a continuum or covariant version of the fixed point
- a thermodynamic interpretation of the fixed point

## Motivation

The closure v3 identified three source channels and a tensorial
response:

- `Q_src` (coherence/transport)
- `S_amp` (amplitude-density evolution)
- `P_delta` (propagator dressing excess)

But all tests so far operated in "open loop": run rollout, extract
closure, measure fit. This does not tell us whether the closure is
self-consistent — i.e., whether the backreaction it predicts is
compatible with the quantum state that generated it.

For a physically meaningful backreaction, the following loop must be
tested:

```
initial state phi_0
  → rollout
  → Psi_BR3
  → perturbed state phi_0 + epsilon * Psi_BR3
  → rollout
  → Psi_BR3'
  → delta_BR = Psi_BR3' - Psi_BR3
```

If `||delta_BR|| < epsilon ||Psi_BR3||` the system contracts and a
fixed point is approached under iteration.

## Self-consistency perturbation

Define the perturbed initial phase:

`phi_pert(i) = phi_0(i) + epsilon * Psi_BR3(i)`

with `epsilon = 0.10` (a 10% perturbation of the closure potential).

Re-run the rollout from `phi_pert`. Recompute `Psi_BR3'`.

Define the response:

`delta_BR(i) = Psi_BR3'(i) - Psi_BR3(i)`

Define the contraction ratio:

`gamma = ||delta_BR||_L1 / (epsilon * ||Psi_BR3||_L1)`

## Minimal success condition

The self-consistent fixed point proxy is supported if:

1. `delta_BR` is nontrivial: `||delta_BR||_L1 > 1e-5`
   (the perturbation actually changes the closure — system is sensitive)

2. `gamma < 1.0`
   (the response is smaller than the perturbation — contraction)

3. The tensorial signature is preserved under perturbation:
   `sign(e_xx') == sign(e_xx)` and `sign(e_tt') == sign(e_tt)`
   (the tensor structure of the closure is stable)

4. History imprint survives perturbation:
   `||Psi_BR3'_hist - Psi_BR3'_nohist||_L1 > 0.03`

## What remains open

Even if the proxy fixed point is supported:

- uniqueness is not shown
- covariant formulation is not available
- the fixed point is tested only once (single iteration)
- convergence to the fixed point from arbitrary perturbations is unknown

So this is a single-iteration contraction proxy, not a proof of
self-consistent existence.
