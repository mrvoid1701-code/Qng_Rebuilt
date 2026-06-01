---
id: DER-QNG-101
type: derivation
status: locked
title: Hodge no-go — force carriers must be edge-valued, not node scalars
author: C.D Gabriel
date: 2026-06-01
depends_on:
  - DER-QNG-076 (v12 EM extension, A_ij edge gauge field)
  - DER-QNG-069 (Gap 12 tensor graviton)
  - demo-theory E5/E7/E8 (2026-06-01)
upstream_objects:
  - node state (sigma_g, sigma_m, chi, phi) — all SCALARS per node
  - edge field theta_ij = phi_i - phi_j (1-form)
evidence:
  - 07_validation/audits/demo-e5-transverse-light-v1/
  - 07_validation/audits/demo-e7-phi-chi-photon-v1/
  - 07_validation/audits/demo-e8-graviton-tensor-v1/
---

# DER-QNG-101 — Hodge no-go: force carriers must live on the edges

## 0. Claim

> **No scalar field defined on the NODES of the QNG graph can carry a
> transverse (gauge-boson) mode. A force carrier with transverse polarizations
> must be a directional object, and on a graph that is an EDGE-VALUED field.
> Therefore the v12 photon `A_ij` (edge vector, spin-1) and the Gap-12 graviton
> (edge rank-2, spin-2) are FORCED choices, not arbitrary additions.**

This resolves the open ambiguity recorded in `qng-gap12-correction-v1.md` and
`qng-gap12-closure-v1.md` ("node-valued vs edge-valued not uniquely
determined") in the direction of **edge-valued**.

## 1. The structural theorem (Hodge / d∘d = 0)

Let `f` be any scalar field on the nodes. Its only natural derived vector is
the edge field (discrete exterior derivative, a 1-form on edges):

```
   theta_ij = f_i - f_j  =  (d f)   ⟹   theta = d f  is EXACT
```

By the discrete Poincaré identity `d∘d = 0`, an exact 1-form is **curl-free**:
`curl(theta) = curl(d f) = 0` identically. By the Hodge decomposition a 1-form
splits as `omega = d alpha + delta beta + harmonic`; an exact form has only the
`d alpha` (longitudinal) piece. The transverse (co-exact `delta beta`) sector
is **identically empty** for `theta = d f`.

A transverse, divergence-free vector mode — the defining feature of a gauge
boson (`E ⊥ k`, 2 polarizations) — therefore **cannot be sourced by the
gradient of any node scalar.** This is geometry, not dynamics: no coupling
between node scalars can move a degree of freedom into the transverse sector,
because the boundary is the Hodge boundary.

## 2. Numerical confirmation (demo-theory E5, E7)

- **E5** (`demo-e5-transverse-light-v1`): for a single-valued node scalar `phi`,
  the transverse fraction of `theta = d phi` is `9.4e-32` (machine zero).
  Topological winding produces a transverse component but it is bound to defects
  and not dynamically sustained. → a scalar cannot be light.
- **E7** (`demo-e7-phi-chi-photon-v1`): `chi` is also a node scalar, so
  `curl(d chi) = 2.2e-16` (machine zero) — it cannot be a magnetic analog. No
  coupling of two node scalars sources a sustained transverse mode
  (`7.4e-32`). **But** a fundamental **edge-vector** field under Maxwell
  dynamics `∂²_t A = −c² curl curl A` reproduces the photon exactly: **2
  transverse polarizations propagating at `c_phi`, longitudinal frozen** (Gauss
  constraint).

## 3. The spin-2 corollary (demo-theory E8)

The same argument one rank higher: the node scalar `sigma_g` gives a spin-0
quantum (main-theory Gap 12, `DER-QNG-069`), not the spin-2 graviton. A
symmetric rank-2 object, however, supports transverse-traceless modes:

- **E8** (`demo-e8-graviton-tensor-v1`): the TT projector on a symmetric rank-2
  field keeps **exactly 2 dof** per wavevector (`2.000000 ± 4e-16`), and the two
  TT polarizations propagate degenerately at `c_phi`. Kinematic confirmation
  that a rank-2 carrier hosts the graviton `(h₊, h×)`.

On a graph, the natural rank-2 directional object is **edge-valued** (a Regge
edge-stretch / metric perturbation per link), matching the Gap-12 expectation
("a symmetric rank-2 object, most naturally edge-valued").

## 4. Division of labor (the resulting ontology)

```
   NODES  (scalars: sigma_g, sigma_m, chi, phi)   EDGES  (gauge fields)
   ───────────────────────────────────────────   ───────────────────────────────
   matter / density / phase                       spin-1 vector A_ij  -> LIGHT
   give: LONGITUDINAL modes (sound, Goldstone)     spin-2 rank-2       -> GRAVITON
   set: MASS = volume charge (demo E4)             give: TRANSVERSE modes (forces)
   curl(d scalar) = 0  ->  NO transverse           curl != 0  ->  transverse EXISTS
```

The node/edge split **is** the Hodge (exact / co-exact) split.

## 5. Scope and honest limits

- The theorem forbids node **scalars**. A node **vector/tensor** (a directional
  field carried at nodes, not derived from a scalar) is a logical alternative
  carrier. The edge realization is the **natural graph choice** for a directional
  d.o.f. (an edge is intrinsically oriented) and is the one v12/Gap-12 adopt;
  the theorem makes "not a node scalar" rigorous, and "edge-valued" the natural —
  not the only conceivable — realization.
- This **forces the existence and type** of the carrier; it does **not** derive
  the gauge group or coupling. Why U(1) with coupling `e` (`alpha_fine`) is
  unexplained — Gap 17. Whether the edge admits non-abelian (SU(2)/SU(3))
  structure is the open "edge-content" program (next).
- E8 is **kinematic** (mode count + lightcone); it does not derive graviton
  dynamics from the substrate (Gap 12 dynamics remain open, GPU-047).

## 6. Consequences for the theory ledger

- **Gap 12 ambiguity resolved**: the graviton carrier is edge-valued (forced by
  §1, type-confirmed by §3). Gap 12 reduces to its *dynamical* part only.
- **v12 (`DER-QNG-076`) upgraded in status**: the edge gauge field `A_ij` is not
  a minimal-but-arbitrary addition — it is the unique-type forced carrier of
  light. Its CPU-136 confirmation (spin-1, 2 polarizations) is the original-
  theory realization of demo E7.
- **Mass/force separation locked**: mass is a node quantity (volume charge,
  demo E4); forces are edge quantities. The two cannot be conflated.
