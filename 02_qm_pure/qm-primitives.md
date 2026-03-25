# QM Primitives

Type: `definition`
ID: `DEF-QM-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State the minimal QM vocabulary that must exist before any QNG-native object is introduced.

## Primitive objects

The QM layer starts from:

- state space
- observable algebra
- Hamiltonian or generator of evolution
- measurement rule

In the rebuild, these must be stated independently of any graph ontology.

## Minimal canonical vocabulary

The initial clean vocabulary is:

- state `|psi>`
- operators `hat O`
- canonical pair `(hat q, hat p)` or equivalent field pair
- commutator `[hat q, hat p] = i hbar`
- Hamiltonian `hat H`
- unitary evolution

## Derived objects

From the primitive layer we derive:

- propagators
- mode expansions
- zero-point quantities
- uncertainty products
- entanglement measures
- thermal occupation numbers

## Strict exclusions

The following do not belong in `QM pure`:

- graph Laplacian as a primitive object
- node-local QNG fields
- QNG-specific emergent metric claims
- phenomenology-facing fit parameters

Graph-based quantum structures may appear later in the bridge or QNG layers.

## Immediate dependency rule

Any future file in `QM pure` must identify whether it is:

- exact QM
- semiclassical QM
- thermal/statistical extension

These should remain distinct.
