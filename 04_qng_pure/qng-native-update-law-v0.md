# QNG Native Update Law v0

Type: `derivation`
ID: `DER-QNG-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State the weakest plausible form of a native QNG update law, before choosing a full concrete formula.

## Inputs

- [qng-primitives-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-primitives-v1.md)
- [qng-state-space-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-state-space-v1.md)

## Minimal required properties

Any acceptable native update law should satisfy:

1. locality
   It uses only local neighborhood information.
2. discreteness
   It updates in discrete substrate steps.
3. history dependence
   It depends on at least part of the local past.
4. boundedness or regularization
   It prevents uncontrolled blow-up of native state variables.
5. coarse-grainability
   Its outputs can be summarized into effective field quantities.

## Weak abstract form

The minimal law is:

`N_i(t+1) = U(N_i(t), H_i(t), Adj(i,t), Xi_i(t))`

where:

- `N_i(t)` is local present state
- `H_i(t)` is local history summary
- `Adj(i,t)` is the local relational neighborhood
- `Xi_i(t)` is optional update noise or fluctuation input

## Why this form matters

This abstract form already says something real:

- QNG is non-Markovian at the native level
- memory is structural, not just phenomenological
- geometry and phenomenology must emerge after this layer, not replace it

## Deliberate non-choices

This file does not yet decide:

- whether `Sigma` is primitive or derived
- whether `chi` is primitive or derived
- whether the update is gradient-like
- whether the update is variational
- whether noise is fundamental or effective

These choices should be made only after the abstract layer is accepted.

## Immediate next question

What is the smallest useful history summary `H_i(t)`?

That is likely the next key design problem in the rebuild.
