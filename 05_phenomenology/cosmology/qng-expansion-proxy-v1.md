# QNG Expansion Proxy v1

Type: `derivation`
ID: `DER-COS-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first cosmology-facing proxy that descends from rebuilt QNG quantities without introducing new primitive background variables.

## Inputs

- [README.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/05_phenomenology/cosmology/README.md)
- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)

## Scope

This file defines only a toy-chart expansion-activation proxy.

It does not yet define:

- a Friedmann equation
- a scale factor
- a redshift relation
- or a data-facing cosmology fit

## Motivation

The rebuilt theory already provides:

- `C_eff` as coherence-sensitive support
- `L_eff` as retained memory-load
- `Psi_QNG` as weak-field binding proxy

The minimal cosmology-facing question is therefore:

- can the rebuilt substrate define a net expansion-like activation that increases with coherence and memory-load while being suppressed by local binding

## Local expansion activation proxy

Define:

`X_cos(i) = C_eff(i) (1 + eta L_eff(i)) (1 - |Psi_QNG(i)|)`

with fixed positive `eta`.

## Global cosmology proxies

Define the mean activation:

`H_cos = mean_i X_cos(i)`

Define the activation contrast:

`C_cos = max_i X_cos(i) - min_i X_cos(i)`

## Interpretation

`H_cos` is the first global expansion-like proxy in the rebuild.

`C_cos` measures how inhomogeneous that activation is on the toy chart.

## Why this is the right first cosmology object

This proxy:

- uses only rebuilt upstream quantities
- keeps cosmology downstream of the core theory
- avoids inventing a new background degree of freedom
- is simple enough to validate immediately

## Immediate test criteria

The first CPU test should check:

1. boundedness
2. positive nontrivial activation
3. coherence sensitivity
4. memory-switch sensitivity
5. history imprint
