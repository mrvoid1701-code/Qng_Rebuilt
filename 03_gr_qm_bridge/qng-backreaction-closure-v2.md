# QNG Back-Reaction Closure v2

Type: `derivation`
ID: `DER-BRIDGE-013`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first two-channel back-reaction proxy linking the rebuilt QM-facing sector to the rebuilt GR-facing sector.

## Inputs

- [qng-backreaction-closure-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-backreaction-closure-v1.md)
- [qng-qm-density-source-balance-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-density-source-balance-v1.md)
- [qng-qm-propagator-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-propagator-proxy-v1.md)

## Scope

This file defines only a first upgraded closure proxy.

It does not define:

- an exact semiclassical field equation
- a stress-energy tensor
- a unique continuum bridge law

## Motivation

The first closure proxy used one bridge source:

`Q_src`

But the rebuilt QM lane now supports a second source-like object:

`S_amp(i,t) = rho_t(i) (exp(2 A_loc(i,t)) - 1)`

which captures density evolution induced by the local generator.

That means the bridge now has two distinct source channels:

- coherence/transport source
- amplitude-density source

## Two-channel source

Keep the first bridge source:

`Q_src(i) = |G_1(i)| (1 + zeta |J_QNG(i)|)`

and define the amplitude-density source:

`S_src(i) = S_amp(i)`

Center both:

`Q_ctr(i) = Q_src(i) - mean_j Q_src(j)`

`S_ctr(i) = S_src(i) - mean_j S_src(j)`

## Closure step

Define the upgraded back-reacted weak-field potential:

`Psi_BR2(i) = Psi_QNG(i) + beta_q Q_ctr(i) + beta_s S_ctr(i)`

with fixed small coefficients:

- `beta_q > 0`
- `beta_s > 0`

Define the upgraded acceleration proxy:

`a_BR2(i) = - grad(Psi_BR2)(i)`

## Why this matters

The bridge now stops pretending that one source-like object must carry all QM feedback.

The rebuilt QM lane has already separated:

- coherence/transport structure
- density-source structure

So the bridge should mirror that separation.

## Minimal success condition

The upgraded closure is useful if:

1. `Psi_BR2` remains bounded
2. `Psi_BR2` differs nontrivially from `Psi_BR`
3. the new closure retains phase sensitivity and history imprint
4. the upgraded source side improves source-response fit beyond v1

## What remains open

This still does not answer:

- whether the two channels are fundamental or effective
- whether a tensorial completion exists
- whether the same two-channel form survives beyond the toy chart

So this is an upgraded closure proxy, not a final bridge theorem.
