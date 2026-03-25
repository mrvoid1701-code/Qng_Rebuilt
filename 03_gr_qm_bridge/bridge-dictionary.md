# GR-QM Bridge Dictionary

Type: `note`
ID: `NOTE-BRIDGE-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Track the minimal interface between GR language and QM language before QNG-native constructs are introduced.

## Allowed bridge themes

- classical action vs quantum generator
- stress-energy vs expectation-value source terms
- geometric background vs quantum state evolution
- propagator language vs metric response language
- exact theory vs effective semiclassical approximation

## Minimal bridge statements

The bridge layer may talk about:

- semiclassical sourcing such as `G_{mu nu} ~ <T_{mu nu}>`
- vacuum effects acting back on effective geometry
- classical limit and correspondence principles
- representational moves from continuum objects to discrete approximations

## Forbidden in this file

- nodes as primitive spacetime ontology
- graph adjacency as primitive physics
- `Sigma`, `chi`, `tau`
- any QNG-specific update law

## Why this separation matters

If we skip this layer, then QNG ends up doing too much work at once:

- replacing GR
- replacing QM
- and defining the bridge

That makes it harder to see whether a failure belongs to:

- GR assumptions
- QM assumptions
- bridge assumptions
- or QNG-native assumptions
