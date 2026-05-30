---
test_id: QNG-CPU-145
title: Knot energy spectrum — ring vs Hopfion family vs trefoil topology
category: structural / topological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-091 (SM ↔ QNG correspondence map, Tier A.2)
  - DER-QNG-092 (Knot spectrum result document)
  - DER-QNG-076 (v12 EM, charge-topology link)
  - CPU-066 (Hopfion Q=0,1 reference)
  - CPU-074 (canonical M_ring)
  - NOTE-QNG-017 (⟨L⟩ universal Lagrangian invariant)
---

# QNG-CPU-145 — Knot energy spectrum reference

## Purpose

First QNG test of the Kelvin–Bilson-Thompson topological-knot hypothesis
for particle identification (DER-QNG-091 §7 Tier A.2). The hypothesis:
distinct stable particles in SM correspond to distinct topologically
stable knot configurations of the QNG phi field, with masses determined
by topological soliton energies.

This test measures the relaxed XY-coupling energy of five topologically
distinct phi configurations on an identical lattice and ranks their
"topological mass" (excess energy above vacuum).

## Inputs

**Lattice**: L=24 cubic, N=L³=13824 nodes, periodic BC, z=6 coordination.

**Substrate parameters** (v8 canonical, unchanged):
- BETA_PHI = 0.06
- Sectors active in test: phi only (sigma_g, sigma_m, chi frozen at uniform)
- Relaxation: pure XY gradient flow, η = 0.20, n_steps = 20000, conv_tol = 1e-6

**Configurations**:
| Label | Initial phi field |
|---|---|
| ring_Q0 | poloidal vortex around xy-loop at R=5 |
| hopfion_Q1 | poloidal + 1·toroidal |
| hopfion_Q2 | poloidal + 2·toroidal |
| hopfion_Q3 | poloidal + 3·toroidal |
| trefoil | phi winding 1 around trefoil curve r(t)=(s sin t + 2s sin 2t, s cos t − 2s cos 2t, −s sin 3t), s=2.5 |

Initial phi field for trefoil uses transverse-frame projection:
phi(P) = atan2(v · B̂(t*), v · N̂(t*)) where t* minimizes |P − r(t)| and
(N̂, B̂) = (T̂ × ẑ, T̂ × N̂) is the local transverse frame.

## Outputs

For each configuration:
- E_initial: phi-XY energy of initial config
- E_final: phi-XY energy after relaxation
- ΔE: E_final − E_vacuum (= E_final + β_φ·N/2)
- Topological diagnostics: Hopf-invariant proxy, xy-plane winding, poloidal-winding

## Gates and tolerances

**Gate G1 (numerical correctness)**: vacuum energy E_vac = −β_φ·N/2 = −414.72 at L=24.
Tolerance: |E_relaxed − E_vac| ≤ 0.5 for configs that fully dissolve.

**Gate G2 (Hopfion preservation)**: hopfion_Q1, Q2, Q3 retain non-zero
toroidal winding (W_xy_above ≠ 0) through relaxation. Predicted:
|W_xy_above − (−Q · 2π)| < 0.1 for each.

**Gate G3 (energy ordering)**: ΔE(Q1) < ΔE(Q2) < ΔE(Q3) (monotone in
topological charge).

**Gate G4 (decision)**: at least 3 distinct topology classes maintain
ΔE > 0.1 at end of relaxation (= survive as bound solitons).

## Decision criterion

PASS if Gates G1, G2, G3 all hold AND Gate G4 holds (≥3 stable
topologies).

## Result (2026-05-30 run)

| Config | ΔE | W_xy_above | W_poloidal | Status |
|---|---|---|---|---|
| ring_Q0 | 0.0346 | 0.00 | 0.00 | DISSOLVED |
| hopfion_Q1 | 9.7557 | −6.28 (−2π) | −6.28 | STABLE |
| hopfion_Q2 | 12.1134 | −12.57 (−4π) | (varies) | STABLE |
| hopfion_Q3 | 15.6117 | −18.85 (−6π) | (varies) | STABLE |
| trefoil | 0.0779 | 0.00 | 0.00 | DISSOLVED |

**Gates evaluated**:
- G1: PASS (dissolved configs reach Δ < 0.1 of E_vac)
- G2: PASS (Hopfion windings preserved to expected −Q·2π exactly)
- G3: PASS (ΔE monotone Q1 < Q2 < Q3)
- G4: PASS (3 of 5 stable: Q1, Q2, Q3)

**Decision: PASS**

## Interpretation

Pure-phi XY sector of QNG v8/v12 hosts a hierarchy of Hopfion solitons
indexed by integer toroidal winding Q ∈ {1, 2, 3}. The bare vortex ring
(no toroidal winding) and the trefoil knot are NOT topologically
protected in pure phi — they dissolve under gradient flow. This is
expected: phi is an S¹-valued field, and pure-S¹ topology protects only
winding around topologically non-trivial loops (here: periodic-BC cycles
of the lattice), not local vortex tubes or higher-dimensional knots.

**Mass ratios observed**:
- ΔE(Q2)/ΔE(Q1) = 1.242
- ΔE(Q3)/ΔE(Q1) = 1.600
- ΔE(Q3)/ΔE(Q2) = 1.289

These do NOT match SM lepton ratios (m_μ/m_e = 207, m_τ/m_μ = 17). The
Hopfion family forms a discrete spectrum more similar to harmonic
oscillator excitations than to particle generations.

**Significance**:
1. CONFIRMS that QNG hosts a topologically protected discrete soliton
   spectrum (first such evidence beyond the single Q=1 Hopfion of CPU-069).
2. NEGATIVELY CONFIRMS the simple Kelvin-Bilson-Thompson hypothesis as
   formulated: pure-phi knots beyond Hopfion (trefoil, figure-8) require
   additional structure (S²-valued n-field via Faddeev-Skyrme, or matter
   sector coupling).
3. ESTABLISHES the energy/winding relation that any future "knots-as-
   particles" attack must explain or modify.

## Artifacts

- Report JSON: `07_validation/audits/qng-knot-energy-scan-v1/report.json`
- Summary MD: `07_validation/audits/qng-knot-energy-scan-v1/summary.md`
- Test runner: `tests/cpu/qng_knot_energy_scan_reference.py`

## Follow-up tests (queued)

- QNG-CPU-146: same scan with FULL v8 matter coupling (σ_m + Channel F)
  to test if matter sector stabilizes trefoil and bare ring.
- QNG-CPU-147: Q=4, 5 Hopfion extension to characterize asymptotic
  Q-dependence (test E_Q ∝ Q^p hypothesis).
- QNG-CPU-148: Faddeev-Skyrme n-field substrate as v13-prototype to test
  if true 3-manifold knots emerge with n: R³ → S².
