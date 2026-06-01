---
type: derivation
id: DER-QNG-069
title: Gap 12 — Tensor graviton ontology missing from v10 scalar substrate
status: STRUCTURAL GAP IDENTIFIED (requires new ontology OR emergent mechanism)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-036 (E_v7 sigma_g dynamics)
  - DER-QNG-042 (v8 canonical + mu_g derivation)
  - DER-QNG-068 (DER-QNG-044 closure)
  - CPU-118 (graviton dispersion v10)
  - einstein-mind consultation 2026-04-24
---

# DER-QNG-069 — Gap 12: Tensor graviton ontology

## Statement of gap

QNG v10 substrate encodes gravity via the scalar field `sigma_g` per
node. Its wave perturbation `delta sigma_g` satisfies

```
d²(delta sigma_g)/dt² = c_g² * nabla²(delta sigma_g),
c_g² = beta_g / (z · mu_g),
```

verified numerically in CPU-118. Per DER-QNG-042 §3.3, `mu_g` is fixed
by the condition `c_g = c_m = c_phi = c`, making all three wave speeds
equal — a structural protection consistent with GW170817.

**The quantum of this wave is spin-0.** `sigma_g` is a scalar field
on the graph; its canonical quantization gives a spin-0 particle
(Brans-Dicke-like breathing mode). This DOES NOT match the GR graviton,
which is spin-2 with two transverse-traceless polarizations (h+, h_x).

**Observational status**: LIGO/Virgo binary mergers (GW150914, GW170817
and others) are consistent with GR's spin-2 tensor modes at high
precision. Pure-scalar gravity is strongly constrained observationally.

## einstein-mind consultation (2026-04-24)

Verbatim from `/.claude/agent-memory/einstein-mind/tensor-graviton-gap.md`:

> **Verdict**: this is a genuine structural gap in QNG that needs new
> ontology. The sigma_g wave measured in CPU-118 is the analog of a
> propagating Newtonian potential, not the graviton. A scalar field per
> node has zero indices; no coarse-graining of zero-index objects
> produces independently-propagating traceless-transverse modes.
> Composites like (∂_μΨ)(∂_νΨ) are dynamically dressed scalars, not
> new degrees of freedom. LIGO's observation of h+ and h_× at c rules
> out scalar-only gravity.

## One internal path to test before conceding

Per einstein-mind:

> **The one internal path worth testing before conceding ontology**:
> fluctuations of sigma_g around a sigma_m-inhomogeneous background
> (the CPU-074 ring). If residual-symmetry decomposition reveals two
> independent transverse polarizations with matching dispersion at
> fixed k, there is emergent tensor structure. If only one scalar mode
> appears per k, the gap is ontological.

**Proposed test (QNG-GPU-047)**:
1. Start with cached CPU-074 ring (R=4) in sigma_m sector.
2. Add small plane-wave perturbation to sigma_g with wavevector k
   along various orientations (parallel and perpendicular to ring axis).
3. Evolve linearized dynamics.
4. Decompose delta sigma_g modes in residual symmetry group of the
   background (cylindrical near ring; broken from full SO(3)).
5. Count independent propagating modes at fixed k; measure dispersion
   of each.
6. If 2 transverse modes emerge with omega = c_g·k, tensor structure is
   present in coarse-graining. If only 1 longitudinal mode, gap is hard.

## Expected outcome (honest)

Einstein-mind's prior: "Most likely outcome: you will need a new
primitive — a symmetric rank-2 object, most naturally edge-valued."

**This parallels the hbar program finding**: scalar edge noise was
structurally insufficient (CPU-092/093/094). QNG substrate may need
richer edge content for BOTH hbar emergence AND spin-2 graviton.

## Implications if gap is hard

If ring-background test confirms only scalar mode:

1. **QNG v10 is a scalar gravity theory**, structurally, at the
   substrate level.
2. **Phenomenology with GR features** (Shapiro, bending, Pound-Rebka,
   WEP — all PASS in DER-QNG-068) comes from the **background
   Newtonian-gauge metric** `g_munu = diag(-(1+2Phi/c²), (1-2Phi/c²)·δ_ij)`
   where Phi = sigma_g deviation. This is formally the scalar sector
   only, which happens to match GR at Newtonian + first post-Newtonian
   order.
3. **Tensor gravitational waves must come from NEW ONTOLOGY**:
   - An edge-valued symmetric rank-2 field (most natural)
   - OR a second graph structure carrying tensor indices
   - OR full-blown reformulation (spin networks, LQG-like)

## Implications if gap closes via ring-background mechanism

If CPU-118 follow-up shows 2 transverse propagating modes in sigma_g
around ring background:

1. QNG v10 has emergent tensor gravity from coarse-graining.
2. The graviton is a COMPOSITE operator, not a fundamental field.
3. This would be a novel prediction worth publishing separately.

## Connection to other gaps

- **Gap 11 (v8 vacuum instability)**: closed via R1 orbital attractor
  (DER-QNG-050/051, GPU-031f).
- **Gap 5 (cosmological α)**: open; identification Λ ↔ α.
- **Gap 12 (tensor graviton, this note)**: NEW, most serious of current
  open gaps because observationally testable at leading order.

## Recommended next action

1. **Immediately**: schedule QNG-GPU-047 (ring-background sigma_g mode
   decomposition) as high-priority test.
2. **In parallel**: draft `qng-edge-tensor-ontology-v1.md` designing
   a rank-2 edge primitive extension.
3. **Conservative position for paper**: QNG v10 matches GR at
   post-Newtonian level for static-source phenomenology; graviton
   polarization structure is open.

## Verification log

- CPU-118 dispersion: omega² = c_g²·k² massless PASS at fit level
- c_g = c_phi confirmed with mu_g from DER-QNG-042 §3.3
- einstein-mind consultation completed; agent memory recorded at
  `.claude/agent-memory/einstein-mind/tensor-graviton-gap.md`
- NOT verified: ring-background 2-mode decomposition (QNG-GPU-047 pending)
