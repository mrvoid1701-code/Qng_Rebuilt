# QNG QM Propagator Composition Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-016`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first two-step propagator-composition proxy for the rebuilt QNG QM sector.

## Inputs

- [qng-qm-propagator-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-propagator-proxy-v1.md)
- [qng-qm-generator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-generator-assembly-v1.md)
- [qng-qm-operator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-operator-assembly-v1.md)

## Scope

This file defines only a two-step composition proxy.

It does not claim:

- an exact semigroup theorem
- exact unitarity under composition
- a continuum causal propagator
- or a final Green-function structure

## Motivation

The rebuilt QM lane already has:

- a one-step diagonal propagator `P_diag`
- a one-step transport-dressed candidate `P_mix`

The next natural question is:

- does this propagator sector admit a disciplined two-step composition story

That is the minimum level at which kernel language starts behaving like evolution rather than one-step reparameterization.

## Two-step diagonal composition

Let:

- `P_diag(t -> t+1)`
- `P_diag(t+1 -> t+2)`

be the exact local-generator propagators at two consecutive steps.

Then define:

`P_diag^(2) = P_diag(t+1 -> t+2) P_diag(t -> t+1)`

This should reconstruct `psi_(t+2)` exactly when applied to `psi_t`.

## Two-step transport-dressed composition

Let:

- `P_mix(t -> t+1)`
- `P_mix(t+1 -> t+2)`

be the dressed one-step candidates.

Then define:

`P_mix^(2) = P_mix(t+1 -> t+2) P_mix(t -> t+1)`

This is not claimed to be exact.

It is the first composition proxy that asks whether transport-dressed QNG propagation remains:

- bounded
- nontrivially different from diagonal-only propagation
- and still aligned with the recovered two-step target state

## Why this matters

Without composition, the rebuilt QM lane only has:

- one-step generator language
- one-step propagator language

With composition, it can begin to ask:

- whether local propagation pieces can be chained coherently
- whether history and phase survive across composed propagation
- whether the dressed sector behaves like more than a cosmetic perturbation

## Minimal success condition

The first propagator-composition proxy is useful if:

1. diagonal two-step composition reconstructs the two-step target exactly
2. dressed composition remains bounded
3. dressed composition stays strongly aligned with the two-step target
4. dressed composition remains nontrivially different from diagonal composition
5. the composition sector retains phase sensitivity and history imprint

## What remains open

This still does not answer:

- whether the dressed composition has any exact semigroup meaning
- whether a continuum propagator can be recovered
- whether composition closes under a controlled operator algebra

So this is a composition proxy, not a full propagator theorem.
