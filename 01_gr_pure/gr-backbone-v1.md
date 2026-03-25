# GR Backbone v1

Type: `derivation`
ID: `DER-GR-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State the minimum GR backbone that the rebuilt project will treat as canonical before any QNG reinterpretation.

## Inputs

- [gr-primitives.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-primitives.md)
- [gr-action.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-action.md)
- [gr-limits.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/01_gr_pure/gr-limits.md)

## Canonical backbone

The GR backbone in this workspace is:

1. spacetime is represented at the GR layer by a Lorentzian metric `g_{mu nu}`
2. geometry is derived from `g_{mu nu}` through the Levi-Civita connection
3. curvature is encoded by `R^rho_{ sigma mu nu}`, `R_{mu nu}`, `R`, and `G_{mu nu}`
4. matter couples through `T_{mu nu}`
5. dynamics are fixed by metric variation of the GR action

## Core field equation

The exact GR anchor is:

`G_{mu nu} + Lambda g_{mu nu} = 8 pi G T_{mu nu}`

This equation is the top-level exact statement.  
Anything weaker or more operational must declare itself as a derived regime.

## Geodesic backbone

The exact geometric motion statement is:

`d^2 x^rho / d lambda^2 + Gamma^rho_{mu nu} (dx^mu / d lambda) (dx^nu / d lambda) = 0`

This is the exact geometric reference for any later effective acceleration law.

## Weak-field regime

The weak-field split is:

`g_{mu nu} = eta_{mu nu} + h_{mu nu}`

with `|h_{mu nu}| << 1`.

At this level the rebuild allows:

- Newtonian potential language
- linearized curvature
- approximate lapse and spatial metric factors
- post-Newtonian expansions

But these are downstream of exact GR, not replacements for it.

## PPN and observational proxies

PPN quantities such as `gamma`, `beta`, and Shapiro-like observables belong to the observational proxy layer.

They are useful because:

- they connect GR structure to measurable weak-field diagnostics
- they can later serve as bridge checks against QNG-derived effective geometry

But they are not themselves the theory.

## Why this matters for the rebuild

The old workspace often moved quickly from:

- effective potential
- to proxy metric
- to observational gate

without always making it explicit which GR level was being used.

This rebuild forces the hierarchy:

`exact GR -> weak-field GR -> proxy observables`

## Future downstream uses

This GR backbone is expected to support:

- bridge-level semiclassical sourcing
- QNG-level emergent metric comparisons
- phenomenology-level weak-field diagnostics

without letting those downstream layers redefine GR itself.
