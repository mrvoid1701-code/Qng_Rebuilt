# QNG Lorentzian Signature Proxy v1

Type: `derivation`
ID: `DER-QNG-009`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit Lorentzian-signature proxy of the rebuilt QNG theory.

## Inputs

- [qng-geometry-estimator-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-geometry-estimator-v1.md)
- [qng-backreaction-closure-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-backreaction-closure-v1.md)
- [qng-emergent-geometry-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-geometry-v1.md)

## Scope

This file defines only a first signature proxy.

It does not yet define:

- a full Lorentzian metric theorem
- causal cones
- exact hyperbolic field equations
- or a continuum recovery proof

## Motivation

The rebuilt geometry estimator is intentionally Euclideanized.

So the signature problem becomes:

- what extra rebuilt object can distinguish a temporal slot from a spatial slot

The cleanest candidate currently available is the source/back-reaction sector, because it already carries:

- phase-sensitive structure
- transport sensitivity
- directed correction to the weak-field potential

## Temporal signature driver

Use the centered back-reaction source:

`Q_ctr(i) = Q_src(i) - mean_j Q_src(j)`

and define the positive temporal-weight driver:

`T_sig(i) = 1 + lambda |Q_ctr(i)| + nu h_00(i)`

with fixed positive `lambda, nu`.

## Signature proxy

Starting from the Euclideanized spatial proxy `g_11(i) > 0`, define the first Lorentzianized proxy:

`g_sig(i) = diag( -T_sig(i), g_11(i) )`

## Why this is the right first step

This construction keeps the rebuilt logic explicit:

- the spatial slot still comes from the coherence-generated geometry sector
- the temporal sign flip is controlled by the bridge/back-reaction sector

This is stronger than simply inserting a minus sign by hand with no structural source.

## Minimal success condition

The first signature proxy is useful if:

1. `T_sig(i) > 0`
2. `g_11(i) > 0`
3. `det g_sig(i) < 0`
4. the temporal channel is sensitive to phase/back-reaction structure
5. the temporal channel retains history imprint

## What remains open

This proxy still does not answer:

- why the temporal slot is unique in the full theory
- how causal propagation follows
- whether exact Lorentz symmetry emerges

So this is a signature proxy, not a final Lorentzian recovery theorem.
