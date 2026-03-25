# Validation Backbone

Type: `note`
ID: `NOTE-VAL-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define what validation is allowed to do in this rebuilt workspace.

## Validation role

Validation may:

- test claims
- stress assumptions
- compare CPU and GPU implementations
- detect fragile margins
- expose hidden dependence on representation choices

Validation may not:

- create ontology
- silently alter definitions
- upgrade exploratory numerics into theory primitives

## Hardware split

The workspace treats CPU and GPU as distinct validation lanes:

- CPU = correctness lane
- GPU = scale lane

## Cross-lane requirement

Any important numerical object that exists on both lanes should eventually have:

- one CPU reference test
- one GPU reproduction test
- one CPU/GPU agreement threshold

## Early milestone

Before full phenomenology begins, this rebuild should have:

- one CPU reference test for a GR-layer object
- one CPU reference test for a QM-layer object
- one CPU/GPU agreement test on a bridge or QNG-core object
