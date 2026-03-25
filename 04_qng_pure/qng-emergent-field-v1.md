# QNG Emergent Field v1

Type: `derivation`
ID: `DER-QNG-006`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first clean effective-field layer that emerges from native QNG dynamics before any geometry claim is made.

## Inputs

- [qng-ontology-backbone-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-ontology-backbone-v1.md)
- [qng-memory-structure-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-memory-structure-v1.md)
- [qng-history-summary-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-history-summary-v1.md)
- [qng-native-update-law-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-native-update-law-v1.md)
- [qng-sigma-status-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-sigma-status-v1.md)

## Why this file is needed

The rebuild has already clarified that native QNG should start from:

- relational substrate
- local history-sensitive update

not from a predeclared effective field.

So the next clean step is:

- define what the effective layer actually summarizes

without forcing it to be one legacy symbol too early.

## Main rebuild decision

The first effective layer should not be one scalar by default.

The old workspace compressed too much into one symbol.  
The rebuild therefore starts with a split effective layer:

1. `C_eff`
   an effective coherence or compatibility field
2. `L_eff`
   an effective memory-load field

This is the first major structural correction to the old theory.

## Native-to-effective map

At coarse-graining scale `ell`, define:

`C_eff(i; ell) = F_C( avg_ell[N], avg_ell[H] )`

`L_eff(i; ell) = F_L( avg_ell[N], avg_ell[H] )`

where:

- `avg_ell` denotes local coarse-graining over a window of scale `ell`
- `F_C` summarizes local compatibility or coherence
- `F_L` summarizes retained local memory burden or delayed-response load

## First candidate interpretation

Using the current native toy variables:

- node state contains `sigma_i, chi_i, phi_i`
- history summary contains `M_i, D_i, P_i`

the natural first interpretation is:

- `C_eff` should increase with local bounded stability and local phase compatibility
- `C_eff` should decrease with local mismatch or tension
- `L_eff` should increase with retained memory amplitude and with stored local load

## Candidate formulas

The first reference-level candidate is:

`C_eff = clip01( a_sigma <sigma> + a_D (1 - <D>) + a_P (1 + cos <P>) / 2 )`

`L_eff = clip01( b_M <M> + b_chi <|chi|> )`

with nonnegative weights.

This is not yet the final theory.  
It is the first explicit separation between:

- coherence-like content
- memory-load content

## Consequence for `Sigma`

In the rebuilt theory, `Sigma_effective` is no longer the first object in the effective layer.

Instead, the clean interpretation is:

- `Sigma_effective` may later be a chosen compression of `(C_eff, L_eff)`
- or it may be replaced entirely if the two-field split proves more stable

This is a stronger position than the old workspace because it prevents one scalar from silently carrying incompatible jobs.

## Bridge intuition

This split also matches the separated targets inherited from GR and QM:

- geometry wants a coherence-sensitive object
- delayed or hysteretic response wants a memory-load-sensitive object

So the two-field split is better aligned with the GR/QM rebuild than a single overloaded scalar.

## Immediate downstream use

The first emergent-geometry attempt should depend primarily on `C_eff`, not directly on native variables.

The first delayed-response phenomenology attempt should depend primarily on `L_eff`, not directly on native ontology.

## What this already teaches us

The old project's main compression error was probably not just a bad parameter value.

It was more structural:

- one symbol was asked to represent both local coherence and retained memory burden

The rebuild now treats those as separate until evidence says otherwise.
