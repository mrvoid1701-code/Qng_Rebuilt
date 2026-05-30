---
test_id: QNG-CPU-151
title: Plaquette curl analysis — v12 gauge currents per knot type
category: structural / electromagnetic
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-076 (v12 EM extension, gauge field A_ij)
  - DER-QNG-091 (SM ↔ QNG correspondence map)
  - DER-QNG-092 §F (this work)
  - CPU-148 / CPU-149 (knot lifetime baselines)
---

# QNG-CPU-151 — Plaquette curl analysis per knot type

## Purpose

CPU-148/149 found that local-topology knots in v7 share the SAME
decay rate per fixed L (no topology-dependence). Under v12 EM coupling,
A_ij becomes dynamical and absorbs phi-gradient energy. Different
knot topologies have different gauge-current densities (plaquette
curls), so v12 should produce TOPOLOGY-DEPENDENT decay rates via
photon emission.

This test computes the v12 photon emission prediction WITHOUT running
full v12 dynamics, by computing the static plaquette curl F_p for each
knot.

## Inputs

L=24 cubic lattice. Six initial configurations:
- ring_Q0 (vortex ring R=5)
- hopfion_Q1, Q2 (Hopfion family Q=1, 2)
- trefoil, figure_8, cinquefoil (knot vortices)

For each, compute:
- F_p = sum(wrap_pi(phi_i - phi_j)) around each plaquette (xy, yz, xz)
- N_flux = number of plaquettes with |F_p| > π
- E_gauge = sum over plaquettes of F_p² (proportional to v12 gauge KE)
- max |F|, mean |F|

## Gates

**G1**: All knots show non-zero plaquette curl (G1 = N_flux > 0 for all).

**G2**: E_gauge depends on topology — relative spread (max/min) > 1.5.
If spread < 1.5, v12 universality would persist (against expectation).

**G3 (Hopfion Q-saturation)**: E_gauge for Hopfion Q=1 and Q=2 agree
to within 10%. This is a sub-prediction: under v12, photon emission
rate from Hopfion ladder might be Q-independent.

## Decision

PASS = G1 AND G2.

## Result (2026-05-30)

| Configuration | rope_len | N_flux | E_gauge | E_gauge / E_ring |
|---|---|---|---|---|
| ring_Q0 | 31.42 | 82 | 3237 | 1.000 |
| hopfion_Q1 | 62.83 | 198 | 7817 | 2.415 |
| hopfion_Q2 | 94.25 | 196 | 7738 | 2.390 |
| trefoil | 51.89 | 194 | 7659 | 2.366 |
| figure_8 | 54.14 | 156 | 6159 | 1.902 |
| cinquefoil | 48.47 | 204 | 8054 | 2.488 |

**Gates evaluated**:
- G1: PASS — all N_flux > 80
- G2: PASS — spread max/min = 2.488/1.000 = 2.49
- G3: PASS — Hopfion Q=1 vs Q=2 differ by only 1.0% (7817 vs 7738)

**Decision: PASS**

Pearson correlation between rope length and E_gauge: 0.61
Linear fit: E_gauge ~ 3044 + 65 * rope_length

## Predictions delivered

### Prediction P1 (topology-dependent photon decay)

Under v12 EM, the decay rate ratio is approximately:

τ(ring) : τ(figure-8) : τ(Hopfion Q1) : τ(trefoil) : τ(Hopfion Q2) : τ(cinquefoil)
≈ 1.00 : 0.53 : 0.41 : 0.42 : 0.42 : 0.40

Spread factor 2.5, with ring being slowest-decaying.

### Prediction P2 (Hopfion Q-saturation under v12)

Hopfion-Q ladder excitations Q=1 and Q=2 should have NEARLY IDENTICAL
decay rates under v12 (agreement to 1%), despite different intrinsic
phi-XY energies (Q=1: ΔE=9.76, Q=2: ΔE=12.11 from CPU-145).

This is a non-trivial prediction: the v12 EM decay channel saturates
at low Q rather than scaling with topological charge.

### Prediction P3 (insufficient for SM diversity)

Spread factor 2.5 from v12 alone is dramatically smaller than the SM
particle lifetime spread (~10²⁰). Full SM-like lifetimes require
either:
- v13 SU(2) weak interaction
- Reinterpretation of the QNG→SM map such that Hopfion family →
  baryon ground states and local knots → baryon resonance class
  (which has factor ~5 spread, closer to 2.5 prediction)

## Artifacts

- Report: `07_validation/audits/qng-knot-plaquette-curl-v1/report.json`
- Test runner: `tests/cpu/qng_knot_plaquette_curl_reference.py`

## Follow-up tests recommended

- **CPU-152**: implement full v12 dynamics with A_ij + plaquette
  Maxwell term, confirm the 2.5x topology spread directly
- **CPU-153**: test the Hopfion-Q saturation prediction with Q=3, 4, 5
  configurations under static plaquette analysis
- **CPU-154**: investigate which SM resonance class has the observed
  ~2-5x lifetime spread (baryon resonances are the leading candidate)
