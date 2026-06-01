# Phase 10 — the vortex IS a coarse-grained node (and why the scale is the only wall)

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Probe: `demo-theory/tests/t_phase10_vortex_node_rg.py`
Artifact: `07_validation/audits/demo-phase10-vortex-node-rg-v1/`
Prompt: Gabriel — *"maybe the vortex and the nodes have a connection, a
transformation — see and attack."*

---

## The transformation

Under block-spin **coarse-graining** (RG), a φ-vortex:

| Level | L | winding (topological charge) | core (lattice units) |
|---|---|---|---|
| 0 | 32 | |W| = 1 | point-like (sub-cell) |
| 1 | 16 | |W| = 1 | point-like |
| 2 | 8 | |W| = 1 | point-like |
| 3 | 4 | |W| = 1 | point-like |
| 4 | 2 | |W| = 1 | point-like |

> **The winding (topological charge) is preserved EXACTLY at every scale, while
> the vortex core stays point-like. A coarse-grained vortex IS an effective NODE
> carrying the conserved topological charge. The node is a coarse-grained vortex;
> the vortex is a node with its internal structure resolved.** Verdict:
> **VORTEX_IS_A_COARSE_GRAINED_NODE** — the connection/transformation Gabriel
> intuited is the **RG / coarse-graining map** between the two.

## Why this is the key to the whole session

This single fact explains the pattern we hit again and again — **what we could
compute vs what stayed blocked:**

```
   TOPOLOGICAL  (winding, charge, B, J, isospin)   = RG-INVARIANT = SCALE-FREE
        -> p=+1, n=0, pion triplet (Phase 7)          ... we COULD compute these
        -> Eightfold Way octet+decuplet (Phase 8)
        -> J(J+1) band structure (Phase 4d)

   DIMENSIONFUL (absolute mass, size)              = RG-FLOWING = SCALE-DEPENDENT
        -> absolute baryon masses                     ... these stayed BLOCKED
        -> the Planck->MeV scale (Gap 13)
```

Every **scale-free win** of this session is a **topological (RG-invariant)**
quantity; every **blocked** quantity is **dimensionful (RG-flowing)**. The
vortex↔node coarse-graining is precisely the operation that separates them.

## Gap 13 reframed (not solved — reframed)

The 22-order Planck→hadron hierarchy is, in this picture, an **RG DISTANCE**:
~`log₂(10²²) ≈ 73` block-spin steps at blocking factor 2. It is the number of
coarse-graining levels between the substrate (Planck) cell and the physical
(hadron) scale — **not a contradiction**, and **not a property of the
topological sector** (which is why the particle's identity — its charges and
quantum numbers — is scale-free and survives all 73 levels unchanged: a proton
stays a proton at every scale).

This is a genuine conceptual advance:
- it **explains** why the absolute scale is the one hard wall (it is the only
  RG-flowing quantity left, after topology took care of the rest);
- it **predicts** (consistent with everything found) that all quantum numbers
  are exactly scale-invariant while only masses run;
- it **locates** Gap 13 precisely: the missing piece is the RG flow of the
  *dimensionful couplings* over those ~73 levels, i.e. why the physical scale
  sits that far from Planck.

**Honest:** this does NOT compute the 22 orders. It reframes Gap 13 as an
RG-distance / dimensional-transmutation question and explains the scale-free vs
blocked split. The actual flow (and whether QNG's couplings produce exactly 22
orders) remains open — consistent with the main theory's finding that *classical*
running is L-independent (CPU-141) and only quantum/one-loop running could
generate it.

## Connection to the substrate's self-similarity

The vortex↔node map suggests the substrate is **self-similar across scales**:
nodes host vortices, which coarse-grain into effective nodes, which host
effective vortices, ... Each level multiplies the scale. The particle is a
fixed topological pattern that persists across levels; the scale is the level
count. This is the natural home for a dimensional-transmutation hierarchy and is
the cleanest forward attack on Gap 13.

## What to build next (the Gap-13 attack this opens)

- **Measure the RG flow numerically:** coarse-grain the *full* v8/v13 dynamics
  (not just the phase), track how the effective mass / coupling rescales per
  block step, and see whether the flow has a fixed point or a near-marginal
  direction that stretches the scale over many decades (dimensional
  transmutation). A near-marginal coupling gives an exponentially large
  hierarchy from O(1) input — the standard mechanism for 22 orders.
- This is the one remaining hard wall, and Phase 10 turns it from "mystery" into
  "measure the RG flow of the dimensionful sector."
