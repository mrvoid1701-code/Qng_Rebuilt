# QNG Equation Stack v1

Type: `note`
ID: `NOTE-QNG-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the equation stack order that future QNG derivations must follow.

## Stack order

1. `native update equation`
   Governs substrate evolution.
2. `effective field equation`
   Governs coarse-grained objects.
3. `effective geometry equation`
   Governs emergent metric or geometric response.
4. `phenomenological reduction`
   Produces domain-facing observables.

## Why this matters

The old repo often jumped directly from:

- an effective geometry estimate
- to an acceleration law
- to a phenomenological fit

without making the full stack explicit.

## Current gap inherited from legacy work

The clearest unresolved issue is that the effective field equation was not fully stabilized:

- `Sigma` often behaved like the central field
- but its own equation of motion remained partial and partly postulated

This means the rebuilt QNG stack should not pretend to be complete until the effective field equation is stated cleanly.

## Immediate use

Every future derivation in `QNG pure` should say which layer of the stack it belongs to.
