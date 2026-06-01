# REPORT — demo Phase-10 vortex<->node transformation (coarse-graining / RG)

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase10_vortex_node_rg.py`
Verdict: **VORTEX_IS_A_COARSE_GRAINED_NODE**

Block-spin coarse-graining (factor 2) of a winding-1 phi vortex, 5 levels
(L: 64->32->16->8->4->2):

| Level | L | |winding| | core (lattice) |
|---|---|---|---|
| 0-4 | 32..2 | 1 (exact, all levels) | point-like (sub-cell) |

## Verdict

The winding (topological charge) is preserved EXACTLY under coarse-graining
while the vortex core stays point-like -> a coarse-grained vortex IS an effective
NODE carrying the conserved topological charge. The vortex<->node connection is
the RG / coarse-graining map.

KEY CONSEQUENCE: this separates TOPOLOGICAL quantities (winding, charge, B, J,
isospin = RG-invariant = SCALE-FREE = the charges/Eightfold-Way/J-band we COULD
compute) from DIMENSIONFUL quantities (mass, size = RG-flowing = scale-dependent
= BLOCKED, Gap 13). It explains the whole session's compute/blocked pattern.

Gap 13 (Planck->MeV, 22 orders) reframed as an RG DISTANCE (~log2(10^22)=73
block steps at b=2) -- not a contradiction, and not in the topological sector
(particle identity is scale-free across all levels). Does NOT compute the 22
orders; reframes them as dimensional transmutation / RG flow of the dimensionful
couplings (open; consistent with CPU-141 classical-running-is-flat).

## Scope / fix

2D phi-vortex, order-parameter (e^{i phi}) block averaging. Winding sign (-1) is
just the perimeter-walk orientation; |W|=1 is the charge. Next: coarse-grain the
FULL v8/v13 dynamics to measure the dimensionful RG flow (the Gap-13 attack this
opens).
