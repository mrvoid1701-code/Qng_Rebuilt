# QNG Source-Response Consistency v1

Type: `derivation`
ID: `DER-BRIDGE-010`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit source-response consistency step linking the rebuilt source-like sector to the rebuilt GR linearized-curvature sector.

## Inputs

- [qng-backreaction-closure-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-backreaction-closure-v1.md)
- [qng-gr-linearized-curvature-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-linearized-curvature-v1.md)
- [qng-matter-sector-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-matter-sector-proxy-v1.md)

## Scope

This file defines only a first source-response consistency check.

It does not yet define:

- an Einstein equation
- a final stress tensor
- a unique source decomposition
- or a full semiclassical closure theorem

## Motivation

The rebuilt project now has:

- a geometry-side linearized-curvature proxy `R_lin`
- a source-side bridge object `Q_src`
- a matter-like proxy `M_eff`

The next closure question is:

- does adding a source-like channel improve the response fit beyond a geometry-only baseline

## Baseline response

Use the geometry-sector curvature proxy `K_C` as the baseline explanatory object for `R_lin`.

## Source-augmented response

Use the first bridge source object `Q_src` as the added source-side channel.

The first response consistency model is therefore:

`R_lin(i) ~ a K_C(i) + b Q_src(i)`

with fitted coefficients on the toy chart.

## Why `Q_src` is the right first source channel

`Q_src` is better suited than `M_eff` for the first closure step because:

- it already lives at the bridge level
- it enters the existing back-reaction proxy
- it is directly built from coherence and transport

`M_eff` remains important as a matter-like interpretation layer, but `Q_src` is the cleaner first response partner.

## Minimal success condition

The first source-response step is useful if:

1. the geometry-only baseline fits imperfectly but meaningfully
2. the source-augmented fit improves substantially
3. the fitted source coefficient is nonzero
4. the source-augmented relation retains history imprint

## Interpretation

If this works, then the rebuilt bridge now supports more than:

- a source-like object
- and a curvature-like object

It supports:

- a first disciplined source-response consistency relation

This is the correct next step beyond proxy closure.
