# QNG Covariance Stability v1

Type: `derivation`
ID: `DER-GOV-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test whether the physical signals identified in the rebuilt proxy sector
are stable across different graph topologies (different seeds), or whether
they are artifacts of a single fixed graph.

## Inputs

- [qng-einstein-equations-proxy-v1.md](../03_gr_qm_bridge/qng-einstein-equations-proxy-v1.md)
- [qng-lorentzian-signature-proxy-v1.md](qng-lorentzian-signature-proxy-v1.md)
- [qng-light-cone-proxy-v1.md](qng-light-cone-proxy-v1.md)

## Scope

This file defines only a first covariance/universality check across K=5
different random seeds (graph topologies + initial conditions).

It does not define:

- a formal proof of covariance
- a continuum limit
- a symmetry group analysis
- stability under all possible perturbations

## Motivation

All results from QNG-CPU-029 through QNG-CPU-035 were computed on a
single fixed seed (`20260325`). Any of these results could in principle
be an artifact of that particular 16-node graph topology.

Before building further on those results, it is necessary to test which
signals are universal (topology-independent) and which are
topology-dependent.

## Two-tier stability structure

Probing across seeds 42, 137, 1729, 2718, 31415 reveals a clear two-tier
structure:

**Tier 1 — Universal signals (topology-independent):**

- `corr(E_tt, E_xx)` is strongly negative on all seeds: range (−0.998, −0.856)
- `w_eff` (equation of state) is stable near −0.69: range (−0.743, −0.623), std/mean = 7%
- `|e_xx_coeff − e_tt_coeff|` (tensor component separation) is always large: > 0.86
- History amplifies c_eff variation on all seeds

**Tier 2 — Topology-dependent signals:**

- The SIGN of individual P_delta channel coefficients (`e_xx`, `e_tt`) flips
  between some topologies. For some graphs e_xx < 0 and e_tt > 0; for others
  e_xx > 0 and e_tt < 0.
- The MAGNITUDE of the amplification ratio varies: 2.8x to 23.4x

## Physical interpretation

The tier-1 signals are candidates for physical universals:

- The anti-correlation `corr(E_tt, E_xx) ≈ -0.97` is a structural property
  of the substrate, not an artifact
- The equation of state `w_eff ≈ -0.69` appears across all tested topologies
- The tensor components always respond DIFFERENTLY to the propagator channel
  (separation always > 0.5)

The tier-2 signals are topology-dependent. The specific direction of the
P_delta response depends on which graph we have. This does not invalidate
the tensor structure, but it does mean the SIGN of individual coefficients
in the 4-channel fit should not be used as universal discriminants.

## Minimal success condition

The covariance proxy is supported if the tier-1 signals are stable:

1. `corr(E_tt, E_xx) < -0.5` on all K seeds
2. `w_eff ∈ (-1.0, -0.3)` on all K seeds (equation of state stable)
3. `|e_xx_coeff − e_tt_coeff| > 0.5` on all K seeds (tensor separation stable)
4. `std_hist > std_nohist` for c_eff on all K seeds (history amplifies variation)
5. `std(w_eff) / mean(|w_eff|) < 0.20` (w_eff stable across seeds, < 20% variation)

## What this changes

- The anti-correlation and equation of state from QNG-CPU-033/035 are
  confirmed as universal
- The specific coefficient signs from the 4-channel fit (QNG-CPU-031,033)
  should be interpreted as topology-dependent, not universal
- Future claims should distinguish tier-1 from tier-2 signals

## What remains open

- stability under continuum limit (N → ∞)
- stability under different graph connectivity (beyond 16-node Erdős–Rényi)
- stability under changes in the number of steps
- formal symmetry analysis
