# QNG Back-Reaction Closure v1

Type: `derivation`
ID: `DER-BRIDGE-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit back-reaction proxy that links the rebuilt QM-facing sector to the rebuilt GR-facing sector.

## Inputs

- [bridge-backbone-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/bridge-backbone-v1.md)
- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)
- [qng-qm-coherence-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-coherence-proxy-v1.md)

## Scope

This file defines only a first proxy closure.

It does not yet define:

- an exact semiclassical equation
- a stress-energy tensor
- a final source law
- or a unique continuum limit

## Starting point

The rebuilt bridge already has:

- a GR-facing weak-field potential proxy `Psi_QNG`
- a QM-facing correlator-like object `G_1`
- a phase-sensitive transport proxy `J_QNG`

So the minimal back-reaction task is:

- define one explicit exchange object that lets the QM-facing sector modify the GR-facing sector

## Source exchange proxy

Define the local QM source exchange object:

`Q_src(i) = |G_1(i)| (1 + zeta |J_QNG(i)|)`

with fixed positive `zeta`.

This object is:

- bounded
- coherence-sensitive
- transport-sensitive

## Closure step

Define the centered source:

`Q_ctr(i) = Q_src(i) - mean_j Q_src(j)`

Then define the back-reacted weak-field potential proxy:

`Psi_BR(i) = Psi_QNG(i) + beta Q_ctr(i)`

with fixed small positive `beta`.

Define the back-reacted acceleration proxy:

`a_BR(i) = - grad(Psi_BR)(i)`

## Why this is the right first closure

This is the minimal explicit closure object because it states:

- what comes from the GR-facing sector: `Psi_QNG`
- what comes from the QM-facing sector: `Q_src`
- how they are combined: additive weak-field correction

That is exactly the kind of separation the rebuild needs.

## What this already means

The rebuilt theory can now say more than:

- GR proxy exists
- QM proxy exists

It can also say:

- QM proxy structure can feed a controlled correction to the GR proxy structure

## What remains open

This still leaves open:

- exact interpretation of `Q_src`
- sign and scale in the continuum
- tensorial completion
- exact covariance properties

So this is a closure proxy, not a final closure law.
