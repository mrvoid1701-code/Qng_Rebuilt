# QNG Matter Sector Proxy v1

Type: `derivation`
ID: `DER-QNG-008`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit matter-like proxy of the rebuilt QNG theory without identifying it with physical matter too early.

## Inputs

- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-chi-status-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-chi-status-v1.md)
- [qng-qm-coherence-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-coherence-proxy-v1.md)

## Scope

This file defines only a first matter-like proxy.

It does not yet define:

- particle species
- a stress-energy tensor
- a mass spectrum
- or a final matter ontology

## Motivation

The rebuilt theory now separates:

- `C_eff` as coherence-sensitive geometry-facing content
- `L_eff` as memory-load content
- `J_QNG` as phase-sensitive transport content

The first matter-sector question is therefore:

- what local combination behaves less like pure geometry and more like localized load or transport-bearing content

## Matter-like proxy

Define the local matter-like proxy:

`M_eff(i) = clip01( alpha L_eff(i) (1 - C_eff(i)) + gamma |J_QNG(i)| )`

with fixed positive `alpha, gamma`.

> **Annotation (reviewer flag):** `clip01` is a computational boundedness guard — it clamps the result to [0, 1] as a numerical convenience. It has no stated physical origin and is not a physically motivated regularization. Future versions must replace `clip01` with either: (a) a sigmoid function with a physically interpretable scale, or (b) a boundedness argument derived from the substrate dynamics. Until replaced, `M_eff` is dimensionless and does not carry mass units or mass scaling.

## Interpretation

This proxy increases when:

- memory-load is large
- coherence is locally reduced
- phase-sensitive transport is present

That is the minimal profile expected from a matter-like sector candidate in the rebuilt theory.

## Why this is cleaner than the legacy path

The old workspace often drifted too quickly from `chi` to mass semantics.

The rebuild inserts a safer intermediate layer:

- memory-load
- coherence defect
- transport activity
- matter-like proxy

This keeps matter interpretation downstream of structure, not upstream of it.

## Immediate use

`M_eff` is the first candidate object that could later feed:

- source-like terms
- matter/geometry separation
- future stress-like closures

## What remains open

This proxy does not yet answer:

- whether `M_eff` is fundamental or derived
- whether it scales with any physical mass notion
- whether it should source geometry directly

So it is a matter-sector proxy, not a final matter sector.
