# QNG GR Back-Reaction Closure v3

Type: `derivation`
ID: `DER-BRIDGE-020`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first three-channel back-reaction closure that incorporates the
propagator dressing excess from the QM semigroup sector, and test the closure
against the individual tensor components `E_tt` and `E_xx` for the first time.

## Inputs

- [qng-backreaction-closure-v2.md](qng-backreaction-closure-v2.md)
- [qng-qm-semigroup-closure-proxy-v1.md](qng-qm-semigroup-closure-proxy-v1.md)
- [qng-gr-tensorial-assembly-proxy-v1.md](qng-gr-tensorial-assembly-proxy-v1.md)

## Scope

This file defines only a first three-channel closure proxy with tensorial
response testing.

It does not define:

- an exact semiclassical field equation
- a covariant stress-energy tensor
- a final bridge law

## Motivation

The two-channel closure v2 already closes over:

- coherence/transport source `Q_src`
- amplitude-density source `S_amp`

But the QM lane has since added a third semigroup-stable structure: the
dressed-propagator dressing excess `P_delta`, which measures per-node the
amplitude difference between the transport-dressed propagation and the
diagonal-only propagation.

`P_delta(i) = |psi_mix(i)| - |psi_diag(i)|`

This excess is:

- nonzero when transport dressing is active
- zero when transport coupling is switched off
- history-sensitive (semigroup test confirmed this)

It is a genuinely new QM-side signal not captured by `Q_src` or `S_amp`.

Furthermore, the tensorial sector now has two independent curvature objects
`E_tt` and `E_xx`. The closure v3 should be tested against both, not just
the scalar `R_lin`.

## Three-channel closure definition

Keep the v2 potential:

`Psi_BR2(i) = Psi_BR1(i) + beta_s * S_ctr(i)`

Add the propagator dressing channel:

`P_ctr(i) = P_delta(i) - mean_j P_delta(j)`

Define the v3 closure potential:

`Psi_BR3(i) = Psi_BR2(i) + beta_p * P_ctr(i)`

with fixed small coefficient `beta_p > 0`.

## Tensorial response test

Define the updated acceleration proxy:

`a_BR3(i) = -grad(Psi_BR3)(i)`

Test the v3 closure by fitting the tensor components individually:

`E_xx(i) ~ a_xx K_C(i) + b_xx Q_src(i) + c_xx S_amp(i) + e_xx P_delta(i)`

`E_tt(i) ~ a_tt K_C(i) + b_tt Q_src(i) + c_tt S_amp(i) + e_tt P_delta(i)`

The propagator channel coefficient `e_xx` must be nonzero.

The tensor components must have different closure signatures:
`e_xx != e_tt` — the propagator dressing contributes differently to
the two curvature components.

## Minimal success condition

The three-channel tensorial closure is useful if:

1. `Psi_BR3` remains bounded
2. `Psi_BR3` is nontrivially different from `Psi_BR2`
3. the propagator channel coefficient for `E_xx` is nonzero: `|e_xx| > 1e-3`
4. the propagator channel coefficients differ between components: `|e_xx - e_tt| > 1e-3`
5. the 4-channel `E_xx` fit improves over the 3-channel fit: `ratio_4ch < ratio_3ch`
6. phase sensitivity and history imprint are retained

## What remains open

This still does not answer:

- whether three channels are sufficient or whether more are needed
- whether the closure satisfies a Ward-identity-like constraint
- whether the propagator channel survives covariantization
- whether the backreaction satisfies a self-consistent semiclassical
  equation across multiple iterations

So this is a three-channel tensorial closure proxy, not an exact
backreaction theorem.
