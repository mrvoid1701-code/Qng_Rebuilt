# GR Action Backbone

Type: `derivation`
ID: `DER-GR-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Fix the GR action backbone before any discrete or emergent reinterpretation is attempted.

## Inputs

- [gr-primitives.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-primitives.md)

## Action structure

The GR backbone starts from the standard split:

`S_total = S_gravity + S_matter`

with

`S_gravity = (1 / 16 pi G) integral d^4x sqrt(-g) (R - 2 Lambda)`

and

`S_matter = integral d^4x sqrt(-g) L_matter`

## Variation targets

Varying with respect to the metric gives the Einstein equation:

`G_{mu nu} + Lambda g_{mu nu} = 8 pi G T_{mu nu}`

where

`T_{mu nu} = -(2 / sqrt(-g)) delta S_matter / delta g^{mu nu}`

## Why this file exists

In the rebuild, the GR action must be fixed before:

- any graph discretization
- any emergent metric proposal
- any field-specific QNG reinterpretation

Otherwise the project silently mixes:

- exact GR
- effective GR-like diagnostics
- QNG-specific closures

## Allowed future specializations

Later files may derive:

- weak-field expansion of the action
- scalar-field matter specialization
- ADM split
- PPN proxy reductions

But they must remain visibly downstream of this file.

## Open work

- write the weak-field expansion explicitly
- separate exact Einstein equation from diagnostic proxies used in validation
