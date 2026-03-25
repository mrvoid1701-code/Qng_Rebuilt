# QNG Primitives v1

Type: `definition`
ID: `DEF-QNG-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first candidate primitive vocabulary for QNG in a way that is stricter than the legacy workspace.

## Primitive candidates

The current candidate primitive set is:

- `G(t)` : dynamic relational substrate
- `N_i(t)` : local node state
- `U` : local update operator

At this stage, these are the only objects tentatively allowed to be primitive.

## Candidate local state

The old project repeatedly used a local state of the form:

`N_i(t) = (V_i(t), chi_i(t), phi_i(t))`

with an additional stability quantity `Sigma_i(t)`.

For the rebuild, this must be split more carefully:

- `V_i` may be primitive or may be derived from update history
- `chi_i` may be primitive or may be an effective memory/load variable
- `phi_i` may be primitive or may be a phase-like auxiliary variable
- `Sigma_i` should not automatically be declared primitive unless the theory truly requires it at the ontological layer

## Current working decision

For now:

- `G(t)` is treated as primitive
- `U` is treated as primitive
- `N_i(t)` is treated as primitive container language
- the primitive/derived status of `V_i`, `chi_i`, `phi_i`, `Sigma_i` remains open

This is deliberate.  
The old repo locked some of these too early.

## Immediate exclusions

The following are not primitive in this rebuild:

- `tau`
- mission-specific amplitudes
- phenomenological kernel fits
- PPN-facing observables
- emergent metric components

These must all be derived or effective.

## Open pressure points

The rebuild must decide whether `Sigma` is:

1. a primitive field
2. a derived stability functional of more primitive variables
3. an effective coarse-grained object

This is one of the most important decisions in the new architecture.
