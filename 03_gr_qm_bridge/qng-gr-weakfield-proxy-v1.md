# QNG To GR Weak-Field Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first clean GR-facing proxy map from the rebuilt QNG geometry estimator to weak-field observables.

## Inputs

- [bridge-backbone-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/bridge-backbone-v1.md)
- [gr-observables-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-observables-v1.md)
- [qng-geometry-estimator-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-geometry-estimator-v1.md)

## Scope

This file makes only a proxy-level weak-field claim.

It does not yet claim:

- exact Einstein dynamics
- final Lorentzian signature
- or a full metric recovery theorem

## Starting point

The current QNG reference estimator gives a local positive proxy:

`g_ref(i) = diag(g_00(i), g_11(i))`

with both entries close to `1`.

That already suggests a weak-field reading:

- small deviation from a flat local reference metric

## Proxy observables

Define the local lapse-like perturbation:

`h_00(i) = g_00(i) - 1`

Define the local spatial perturbation:

`h_11(i) = g_11(i) - 1`

Define the local potential-like proxy:

`Psi_QNG(i) = h_00(i) / 2`

Define the local acceleration proxy on the ordered toy chart:

`a_QNG(i) = - grad(Psi_QNG)(i)`

## Why this is the right bridge level

These are exactly the kinds of objects listed in the GR rebuild as weak-field observables:

- lapse perturbation
- spatial metric perturbation
- effective Newtonian-potential proxy
- acceleration signature

So this is the first point where QNG can honestly speak to GR without claiming too much.

## Weak-field regime criterion

The bridge is currently meaningful only when:

`max_i |h_00(i)| << 1`

`max_i |h_11(i)| << 1`

In that regime, comparison to GR-facing weak-field language is structurally allowed.

## Rebuild lesson

The correct order is now explicit:

1. native QNG dynamics
2. effective field split
3. geometry estimator
4. weak-field proxy observables

This is much cleaner than the old repo, where phenomenology and geometry were often fused too early.

## Immediate downstream question

The first bridge test should ask:

- are the weak-field proxy observables nontrivial
- bounded
- and history-sensitive

before asking whether they fit any external dataset.
