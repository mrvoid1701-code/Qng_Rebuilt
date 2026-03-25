# QM-CPU-001

Type: `test`
ID: `QM-CPU-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Create the first CPU reference test for the QM pure layer.

## Category

`QM pure`

## Hardware

`CPU`

## Target

Check that QM documents remain QNG-free and graph-free at the primitive layer.

## Proposed checks

- verify `02_qm_pure/` does not introduce substrate-specific ontology
- verify thermal extension remains generic and not QNG-specific
- verify propagator language is introduced before graph discretization

## Pass condition

- zero QNG-native primitives in `02_qm_pure/`
- zero graph ontology treated as primitive

## Artifacts

- static audit report
- dependency summary
