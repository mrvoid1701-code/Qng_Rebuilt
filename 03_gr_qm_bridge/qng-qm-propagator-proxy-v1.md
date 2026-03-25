# QNG QM Propagator Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-012`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first propagator-level proxy for the rebuilt QNG QM sector.

## Inputs

- [qm-propagator.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/02_qm_pure/qm-propagator.md)
- [qng-qm-generator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-generator-assembly-v1.md)
- [qng-qm-operator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-operator-assembly-v1.md)
- [qng-qm-density-source-balance-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-density-source-balance-v1.md)

## Scope

This file defines only a first propagator proxy family.

It does not claim:

- an exact Green function theorem
- a final Hamiltonian kernel
- a continuum propagator
- or exact unitary evolution

## Motivation

The rebuilt QM lane now has:

- a complex state candidate `psi_t`
- a local generator proxy `K_loc`
- an operator family `(G_eff, T_eff, N_eff)`
- a density source balance law

The next natural question is:

- can these ingredients define a meaningful one-step propagator candidate

## Diagonal one-step propagator

From the local generator:

`K_loc(i,t) = A_loc(i,t) + i Omega_loc(i,t)`

define the diagonal propagator:

`P_diag(i,j) = exp(K_loc(i,t)) delta_{ij}`

so that:

`psi_{t+1}(i) = sum_j P_diag(i,j) psi_t(j)`

This is the exact one-step propagator induced by the recovered local generator.

## Transport-dressed propagator candidate

Define the transport-dressed one-step candidate:

`P_mix = P_diag (I + lambda T_eff)`

with small fixed dressing parameter `lambda`.

This object is not claimed to be exact.

It is a first propagator candidate that combines:

- local generator evolution
- transport structure from the ordered probe graph

## Why this matters

This is the first point where the rebuilt QM lane can speak in kernel language:

- one-step propagator
- exact diagonal local propagation
- transport-dressed propagation candidate

This moves the rebuilt QM sector closer to a propagator interpretation without pretending that exact continuum propagation has been recovered.

## Minimal success condition

The first propagator proxy is useful if:

1. `P_diag` reconstructs `psi_{t+1}` exactly
2. `P_mix` is bounded
3. `P_mix` is nontrivially different from `P_diag`
4. the propagator sector retains phase sensitivity and history imprint
5. the dressed propagator action remains aligned with the recovered next-step state

## What remains open

This proxy still does not answer:

- whether the correct propagator is diagonal or transport-dressed
- whether a path-integral or Green-function interpretation survives
- whether any exact unitary or causal structure is present

So this is a propagator proxy, not an exact QM propagator theorem.
