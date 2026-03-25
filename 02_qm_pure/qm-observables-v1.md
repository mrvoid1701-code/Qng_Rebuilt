# QM Observables v1

Type: `definition`
ID: `DEF-QM-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the QM-facing observables that later layers are allowed to compare against.

## Canonical observables

- operator spectra
- expectation values
- uncertainties
- two-point functions
- occupation numbers
- entanglement measures

## Layer split

The rebuild will distinguish:

1. `exact operator-level observables`
2. `mode-level observables`
3. `thermal/statistical observables`

## Rule for later layers

If QNG later claims agreement with QM, it must specify the exact level:

- canonical/operator level
- propagator/correlator level
- thermal/statistical level

This prevents ambiguity about what “QM agreement” actually means.
