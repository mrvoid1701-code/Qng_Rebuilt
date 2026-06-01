# QNG-CPU-100

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel` (autonomous execution 2026-04-22)
Date: `2026-04-22`
test_class: `v9_entropic_probe`
hardware: `CPU`
upstream_derivation: `NOTE-QNG-019 (v9 charter) + AUDIT-QNG-V9A-001`
prerequisites: `QNG-GPU-100 snapshots`

## Title

Verlinde-entropic / holographic probe — test whether a classical
entropy-to-area or entropy-to-action ratio on the V9-A orbital attractor
yields an R-universal action scale that could act as a candidate hbar.

## Background

Verlinde's 2010 entropic-gravity program and earlier Bekenstein-Hawking
area-entropy give the structural form `S = A / (4 hbar G)`. If
v8 has an emergent horizon-like object (the ring), a classical entropy
computation on the orbital attractor at different R should allow testing
whether any natural area/entropy ratio is R-universal.

CPU-098 ruled out the loop-integral (Berry) category; CPU-099 ruled out
the topological-winding (H_1) category. This probe tests the
thermodynamic / information-theoretic category.

## Design

For each R in {3, 4, 5}, load the reduced time series from
`07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/reduced_series.npz`
and the snapshots from `snapshots.npz`.

Compute six candidates per R:

### C1 — Shannon entropy of (sigma_m, pi_m) distribution over orbit

Coarse-grain (sigma_m_i, pi_m_i) over all nodes and all snapshots into a
2D histogram with 40x40 bins. Compute
  S_sm = -sum_bin p_bin log p_bin

### C2 — Shannon entropy of (phi, pi_phi) distribution over orbit

Analogous to C1 on (phi_i, pi_phi_i).

### C3 — "Horizon area" proxy of ring

A_ring(R) = 4 pi^2 R^2  (torus surface area)

### C4 — Bekenstein-like ratio  ρ1(R) = S_sm / A_ring(R)

If R-universal → gives natural inverse-action scale.

### C5 — Bekenstein-like ratio  ρ2(R) = S_phi / A_ring(R)

### C6 — Orbit-action candidate

  S_orbit(R) = <S_total> * T_cycle(R)
where `<S_total> = S_sm + S_phi`. Test universality.

### C7 — Entropy production per cycle

  sigma_prod(R) = (S_sm(last quarter orbit) - S_sm(first quarter orbit)) / T_cycle(R)

If non-zero and R-universal, system has emergent irreversibility that
could produce arrow-of-time but not an action quantum.

## Gates

- **VERLINDE-PASS**: at least one of ρ1, ρ2, S_orbit, or any simple
  combination is R-universal within 5% AND is action-dimensional.
- **VERLINDE-MARGINAL**: R-universality within 20% but not 5%.
- **VERLINDE-FAIL**: all candidates vary >20% across R.

## Auxiliary

- Phase-space occupation volume V_occupied(R) per orbit — classical
  Liouville: V_occupied = const (invariant); check numerically.
- Compare to the Berry-integral "classical action" already computed
  in CPU-098.

## Artifacts

- Script: `tests/cpu/qng_cpu100_verlinde_entropic.py`
- Output: `07_validation/audits/qng-cpu100-verlinde-entropic-v1/`
  - `entropies_R{3,4,5}.json`
  - `report.json` + `REPORT.md`

## Downstream

- If VERLINDE-PASS: opens thermodynamic path to hbar; register as
  DER-QNG-053 candidate.
- If VERLINDE-FAIL: 15th hbar program closed; Dirac (CPU-101) is final
  unexplored category.
