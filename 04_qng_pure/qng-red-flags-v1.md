# QNG Red Flags v1

Type: `note`
ID: `NOTE-QNG-005`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Record the main warning signs inherited from the legacy project so the rebuild does not repeat them.

## Red flag 1

`chi = m/c` was treated as more central than the evidence currently supports.

Current rebuild rule:

- do not hard-lock this as ontology

## Red flag 2

`Sigma` played too many roles at once:

- primitive variable
- stability measure
- effective field
- geometry generator
- source for phenomenology

Current rebuild rule:

- keep these roles separated until justified

## Red flag 3

`tau` drifted between:

- native memory parameter
- effective lag scale
- phenomenological fit parameter

Current rebuild rule:

- every use of `tau` must declare its layer

## Red flag 4

Successful numerics were sometimes allowed to harden definitions too quickly.

Current rebuild rule:

- numerical success supports a candidate estimator
- it does not automatically settle ontology

## Red flag 5

Phenomenology sometimes carried hidden theory-building load.

Current rebuild rule:

- phenomenology may test theory
- phenomenology may suggest theory
- phenomenology may not define theory
