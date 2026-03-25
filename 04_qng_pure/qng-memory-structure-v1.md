# QNG Memory Structure v1

Type: `derivation`
ID: `DER-QNG-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the memory structure of QNG without prematurely tying it to one phenomenological fit story.

## Inputs

- [qng-primitives-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-primitives-v1.md)
- [qng-state-space-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-state-space-v1.md)

## Legacy lesson

The old project clearly suggests that memory is central, but it bundled together:

- native memory
- lag observables
- `tau`
- `chi`
- and domain-specific fitting

too early.

## Clean rebuild principle

The rebuild separates memory into three levels:

1. `native memory`
   The theory has history dependence in its update law.
2. `effective lag`
   A coarse-grained delayed response appears in emergent equations.
3. `phenomenological tau`
   A domain-facing lag parameter is inferred from data.

These are related, but they are not the same object.

## Minimal native claim

The weakest native memory statement is:

`U_t` depends on present local state and at least part of the past local state`

This is enough to make QNG non-Markovian at the native level.

## Effective lag claim

At an effective field level, one may later obtain terms of the form:

`a_lag ~ -(tau_eff) (v . nabla) nabla X`

for some effective field `X`.

But in this rebuild, `tau_eff` is not primitive.

## Fragility warning

The old repo's weakest assumption cluster sits here:

- `chi = m/c`
- universal `tau`
- fixed kernel family

So this rebuild should lock only the weakest memory claim first:

- history dependence exists

and postpone stronger claims until they are separately justified.

## Immediate consequence

When we later define `tau`, we must mark it explicitly as one of:

- derived from native memory
- effective closure parameter
- phenomenological fit parameter

It may not silently slide between these roles.
