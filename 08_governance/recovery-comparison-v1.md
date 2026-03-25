# Recovery Comparison v1

Type: `note`
ID: `NOTE-GOV-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Compare the current rebuilt GR-recovery path and QM-recovery path so the project can prioritize the right hard problems.

## Why this file is needed

The rebuild now has:

- a staged GR recovery program
- a staged QM recovery program

But they are not equally mature.

This matters because the next theoretical effort should go where the gap is largest, not where the wording is most ambitious.

## GR recovery status

The GR side currently has:

- weak-field proxy sector
- Lorentzian signature proxy
- back-reaction proxy available as supporting bridge structure
- linearized assembly step marked `proxy-supported`
- linearized curvature step marked `proxy-supported`
- effective source matching step marked `proxy-supported`

The strongest GR-side result so far is:

- the assembled weak-field Lorentzian metric candidate is internally consistent with the back-reacted acceleration proxy
- and already supports a bounded linearized-curvature proxy coherent with the geometry sector
- and now admits a better scalar source fit when the bridge-density and matter channels are added explicitly

This means the GR side has already crossed the line from:

- isolated proxy objects

to:

- coherent weak-field assembly
- coherent weak-field assembly with a first effective scalar source composite

## QM recovery status

The QM side currently has:

- correlator-like proxy sector
- local transport proxy
- density source balance step marked `proxy-supported`
- local generator assembly step marked `proxy-supported`
- local operator assembly step marked `proxy-supported`
- local operator-algebra proxy step marked `proxy-supported`
- propagator proxy step marked `proxy-supported`
- propagator composition proxy step marked `proxy-supported`
- local mode/spectrum step marked `proxy-supported`

The bridge itself currently also has:

- a source-response consistency step marked `proxy-supported`
- an upgraded two-channel closure v2 marked `proxy-supported`
- an upgraded two-channel source-response v2 step marked `proxy-supported`

But it does not yet have:

- a convincing continuity-style balance
- a closed operator algebra
- a stronger field-theoretic balance law

The most important negative result so far is:

- source-free continuity is weak
- source-augmented continuity is still weak

The most important positive correction is:

- density evolution is strongly captured by the local amplitude source induced by the rebuilt generator

This means the QM side has crossed the line from:

- isolated correlator proxy

to:

- local generator-plus-operator picture
- local generator-plus-operator-algebra picture
- local generator-plus-density-source-plus-operator-algebra picture
- local generator-plus-density-source-plus-operator-algebra-plus-propagator picture
- local generator-plus-density-source-plus-operator-algebra-plus-propagator-plus-composition picture

but not yet to:

- coherent field-theoretic balance law

The bridge side has also crossed a new line:

- it no longer relies only on one coherence/transport source
- it now supports a two-channel response structure with a density-source channel added explicitly

## Direct comparison

At the current rebuild stage:

- GR recovery is ahead of QM recovery

More precisely:

- GR has a better assembled weak-field story
- GR now also has a first scalar source-matching story beyond geometry-only fitting
- QM now has a better local update/generator/density-source/operator/algebra/propagator story than a conservation story
- bridge closure is now stronger than the original one-channel source-response picture

## What this implies

The rebuilt theory currently looks less like:

- "GR and QM are recovered in parallel at the same depth"

and more like:

- "GR is currently strongest at metric assembly"
- "QM is currently strongest at local complex update and operator structure"
- "QM already has a nontrivial commutator sector, but not a closed canonical algebra"
- "QM density evolution is presently source-dominated rather than continuity-dominated"
- "QM now also admits a one-step propagator reading, but not yet an exact continuum propagator theorem"
- "QM now also admits a bounded two-step propagator-composition reading, but not yet a semigroup theorem"
- "bridge closure now improves when the QM density-source channel is added explicitly"

This is an important asymmetry.

## Best interpretation

The asymmetry is not necessarily bad.

It may mean that the rebuilt QNG substrate is naturally closer to:

- geometric weak-field assembly on the GR side
- generator-style local evolution on the QM side

than to:

- exact field-equation closure on the GR side
- exact continuity or operator algebra on the QM side

## Current strongest recovery path

The strongest recovery path is:

- native update
- effective split
- geometry proxy
- Lorentzian signature proxy
- GR linearized assembly
- GR linearized curvature
- GR effective source matching

## Current weakest recovery path

The weakest recovery path is:

- correlator proxy
- current proxy
- continuity-style closure

That is the main place where the rebuilt theory still resists a standard QM reading.

## Practical consequence

If the next goal is maximum theory strengthening, the best order is:

1. strengthen QM recovery beyond local generator assembly
2. return to tensorial or covariance-aware GR recovery beyond scalar source matching
3. only after that attempt deeper bridge closure upgrades
