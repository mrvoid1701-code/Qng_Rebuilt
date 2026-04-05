# GR-CPU-001

Type: `test`
ID: `GR-CPU-001`
Status: `draft`
Author: `C.D Gabriel`
test_class: `internal_consistency`

## Objective

Create the first CPU reference test for the GR pure layer.

## Category

`GR pure`

## Hardware

`CPU`

## Target

Check that the weak-field regime remains internally separated from exact GR and from observational proxy language.

## Proposed checks

- verify declared regime labels are present in GR documents
- verify no QNG-native symbols appear in `01_gr_pure/`
- verify action and limit files depend only on GR-layer files

## Pass condition

- zero QNG-native primitives in `01_gr_pure/`
- no phenomenology references in `01_gr_pure/`
- dependency chain remains internal to GR pure

## Artifacts

- static audit report
- dependency summary
