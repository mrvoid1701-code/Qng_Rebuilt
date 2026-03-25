# QNG State Space v1

Type: `note`
ID: `NOTE-QNG-003`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Clarify the internal levels of the QNG state before writing equations.

## Layer split

The QNG state should be separated into three levels:

1. `ontic state`
   The native substrate state at the node/update level.
2. `effective field state`
   Coarse-grained objects such as stability fields, emergent geometry, or effective source densities.
3. `phenomenological state`
   Domain-facing quantities used in trajectory, lensing, rotation, timing, or cosmology.

## Why this is necessary

The old workspace often let these three levels bleed into one another.

Examples of confusion to avoid:

- treating `Sigma` as both a primitive ontic variable and a coarse-grained field
- treating `tau` as both a native variable and a phenomenological fit parameter
- treating an emergent metric as if it were primitive once a numerical estimator worked

## Working discipline

For the rebuild:

- ontic state must be defined without observational data
- effective field state may depend on coarse-graining rules
- phenomenological state must depend on upstream theory, never the reverse
