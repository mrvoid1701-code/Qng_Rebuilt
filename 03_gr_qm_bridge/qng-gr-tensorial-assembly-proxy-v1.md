# QNG GR Tensorial Assembly Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-018`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first tensorial assembly step for the rebuilt GR recovery program:
construct individual components of the linearized Einstein tensor proxy
and test whether they align differentially with distinct source channels.

## Inputs

- [qng-gr-effective-source-matching-v1.md](qng-gr-effective-source-matching-v1.md)
- [qng-gr-linearized-curvature-v1.md](qng-gr-linearized-curvature-v1.md)
- [qng-gr-linearized-assembly-v1.md](../../01_gr_pure/README.md)

## Scope

This file defines only a first linearized Einstein-tensor-component proxy
in a 1+1D toy chart.

It does not define:

- a covariant Einstein tensor in arbitrary dimensions
- a stress-energy tensor
- a full continuum field equation
- or a Bianchi-identity-level consistency check

## Motivation

The rebuilt GR lane currently produces one scalar per node:

`R_lin(i) = Lap(h_tt)(i) - Lap(h_xx)(i)`

This is the trace-like combination of the linearized Ricci-like components.

A genuine tensor structure requires at least two independent per-node
curvature numbers whose source-side signatures differ.

In the 1+1D linearized picture the two natural components are:

- `E_tt(i) = Lap(h_xx)(i)` — time-time Einstein proxy
- `E_xx(i) = Lap(h_tt)(i)` — space-space Einstein proxy

Note: `R_lin = E_xx - E_tt`, so the existing scalar is already their difference.

The tensorial question is: do `E_tt` and `E_xx` individually carry different
source-side information, or are they redundant once their difference is known?

## Tensorial components

### Time-time component

`E_tt(i) = Lap(h_xx)(i)`

This is driven by the spatial perturbation `h_xx`, which in the current
assembly comes from the geometry proxy `g_11`. It should be more sensitive
to geometry-native and matter-like sources than to transport sources.

### Space-space component

`E_xx(i) = Lap(h_tt)(i)`

This is driven by the temporal perturbation `h_tt = -2 Psi_BR`, which
comes from the back-reaction closure. It should be more sensitive to
transport and coherence sources than to static matter-like sources.

### Trace and traceless decomposition

Define:

`E_trace(i) = E_tt(i) + E_xx(i)`

`E_traceless_tt(i) = E_tt(i) - 0.5 * E_trace(i)`

The trace is the scalar part. The traceless part carries the anisotropy.

## Differential source alignment

The tensorial step is useful if the two components align with different
source channels:

- `E_tt` should correlate more with static/matter-like sources (`M_eff`, `K_C`)
- `E_xx` should correlate more with transport/kinetic sources (`Q_src`, `S_src`)

This differential alignment is the minimum signal that the tensor is
carrying information beyond what the scalar `R_lin` already carries.

## Minimal success condition

The first tensorial assembly proxy is useful if:

1. both `E_tt` and `E_xx` are individually bounded
2. `E_tt` and `E_xx` are nontrivially different from each other (`l1 > 0.10`)
3. `E_xx` correlates more with the transport source `Q_src` than `E_tt` does
4. `E_tt` correlates more with the matter source `M_eff` than `E_xx` does
5. the trace `E_trace` remains bounded
6. the traceless part is nontrivially nonzero
7. both components retain history imprint

## What remains open

This still does not answer:

- whether the tensor components are covariant under graph relabeling
- whether a full 3+1D Einstein tensor can be assembled
- whether the Bianchi identity `nabla_mu G^{mu nu} = 0` is satisfied
- whether the differential alignment is unique or representation-dependent

So this is a tensorial assembly proxy, not a covariant Einstein tensor theorem.
