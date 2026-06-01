# QNG-CPU-099

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel` (autonomous execution 2026-04-22)
Date: `2026-04-22`
test_class: `v9_topology_probe`
hardware: `CPU`
upstream_derivation: `NOTE-QNG-019 (v9 charter) + AUDIT-QNG-V9A-001 (V9A-MARGINAL)`
prerequisites: `QNG-GPU-100 snapshots`

## Title

Graph-cohomology / topological-winding enumeration on the V9-A
orbital attractor — test whether H_1(T^3, Z) sectors are non-trivial
and R-universal, i.e. whether topology alone produces a rigid action
scale inside v8.

## Background

CPU-098 closed V9-A as MARGINAL: no classical loop integral on the
orbital attractor quantizes to integer multiples of a universal theta_0.
One residual category untested empirically is **discrete topology of
the substrate itself**: the z=6 cubic lattice with periodic BC has
H_1(T^3, Z) = Z^3 (three non-contractible 1-cycles). If the orbital
attractor lives in a non-trivial H_1 sector AND that sector is
R-invariant, then topological winding provides an action-scale
candidate that CPU-098 did not test.

The DER-QNG-052 (V9-C) construction relies on Z-winding sectors in the
path integral. This probe checks whether those sectors are classically
populated by the orbital attractor — i.e. whether the classical
dynamics self-selects a topological sector that V9-C could then
quantize without needing external ℏ.

## Design

Load `snapshots.npz` from `07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/`.
Each snapshot contains (sigma_m, pi_m, phi, pi_phi) on a 20^3 = 8000
node lattice with periodic BC.

For each snapshot t, compute the three integer winding numbers of phi
along each principal T^3 cycle:

  n_x(y, z, t) = (1 / 2pi) * sum_i [phi(i+1, y, z, t) - phi(i, y, z, t)]_wrapped
  n_y(x, z, t) = (1 / 2pi) * sum_j [phi(x, j+1, z, t) - phi(x, j, z, t)]_wrapped
  n_z(x, y, t) = (1 / 2pi) * sum_k [phi(x, y, k+1, t) - phi(x, y, k, t)]_wrapped

where `[delta]_wrapped = ((delta + pi) mod 2pi) - pi`.

This yields L^2 = 400 winding numbers per direction per snapshot.

### Test A — Non-triviality

Check fraction of (y, z, t) pairs where `n_x != 0` (and similarly for
n_y, n_z). If essentially zero, H_1 sector is trivial.

### Test B — Cycle invariance

Period-average the spatial histogram of winding. Check whether the
histogram is snapshot-invariant (adiabatic conservation).

### Test C — R-universality

Compare winding distributions across R in {3, 4, 5}. If identical
distribution → topologically selected sector; if R-dependent → no
universal topological sector.

### Test D — Action candidate

If at least one winding number is non-zero and R-universal, construct

  S_top(R) = mean_snapshots [ sum_i pi_phi_i * n_local_i ]

and test universality across R.

## Gates

- **V9-TOP-PASS**: at least one of n_x, n_y, n_z has non-zero mean
  (|<n>| >= 0.5), cycle-invariant (CV < 10%), and R-universal
  (same mean at R=3, 4, 5 within 5%). S_top(R) universal within 5%
  AND action-dimensional.
- **V9-TOP-TRIVIAL**: all windings zero (within |n| < 0.5 everywhere
  across all snapshots / all R). Topology does not lift V9A status.
- **V9-TOP-R_DEPENDENT**: winding is non-zero but varies with R.
  Topological sector is selected but not universal — not an action
  quantum.

## Auxiliary diagnostics

- Distribution of `|phi_i - phi_j|` to gauge whether orbital attractor
  sits close to the XY ground state (phi = const) or explores winding
  branches
- Correlation of local winding defect concentrations with ring core
  position (are topological defects bound to ring?)

## Artifacts

- Script: `tests/cpu/qng_cpu099_graph_winding.py`
- Output: `07_validation/audits/qng-cpu099-graph-winding-v1/`
  - `winding_distribution_R{3,4,5}.json`
  - `report.json` (verdict + per-R means + action candidate)
  - `REPORT.md` (narrative verdict)

## Downstream

- If V9-TOP-PASS: topology rescues V9-A; re-open V9-A as topological-
  quantum program; DER-QNG-052 promotion defers pending reconciliation.
- If V9-TOP-TRIVIAL: one more category closed; Wallstrom+Liouville+
  Noether+discrete-topology blockade confirmed; V9-C becomes obligatory.
- If V9-TOP-R_DEPENDENT: sector selected dynamically but no
  universality; flag as classical topology without quantum — sub-finding.
