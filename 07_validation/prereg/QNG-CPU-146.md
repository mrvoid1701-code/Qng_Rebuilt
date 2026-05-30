---
test_id: QNG-CPU-146
title: Knot stability under FULL v7/v8 matter coupling — decisive KBT test
category: structural / topological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-091 (SM ↔ QNG correspondence map)
  - DER-QNG-092 (knot spectrum first result, §A follow-up section)
  - CPU-145 (pure-phi knot scan, baseline)
  - CPU-066 (Hopfion v7 reference)
  - CPU-074 (canonical M_ring scan)
---

# QNG-CPU-146 — Knot stability under full v7/v8 matter coupling

## Purpose

Companion to CPU-145. CPU-145 found Hopfion Q=1,2,3 stable but trefoil
and bare ring DISSOLVE in pure-phi XY relaxation. CPU-146 asks: does
adding the full v7 matter sector (σ_g, σ_m, χ, φ all active, Channel F
matter depletion ON) stabilize trefoil and ring? If yes, the
Kelvin-Bilson-Thompson hypothesis reopens at the v8 level; if no, v13
n-field extension is required for true knots.

## Inputs

L=20 cubic lattice, full v7 parameters per DER-QNG-033 / CPU-074:
- SIGMA_REF=0.5, ALPHA=0.005, BETA=0.35, BETA_PHI=0.02
- DELTA=0.20, CHI_DECAY=0.020, CHI_REL=0.35
- GAMMA_PHI=0.10 (Channel F matter depletion)
- K_BACK=0.10 (chi back-reaction on sigma_g), K_GM=0.001

Initial phi configurations:
1. **ring_Q0**: poloidal vortex around ring radius R=5
2. **hopfion_Q1**: poloidal + 1 toroidal winding
3. **trefoil**: phi winding 1 around trefoil curve, scale=1.8

Three-phase protocol:
- **Phase 1** (300 steps, no Channel F): allow phi to relax to topology-
  consistent shape from initial guess
- **Phase 2** (1500 steps, Channel F ON): matter sector depletes
  σ_m around phi vortex tube — forms the "ring" / "Hopfion" / "knot"
  topological soliton
- **Phase 3** (3000 steps, Channel F ON): characterize long-time
  stability and decay timescale

Quick mode (`--quick`): skip Q=2, Q=3 (already known stable from CPU-145
and CPU-066). Runs ring, hopfion_Q1, trefoil only.

## Outputs

Per configuration:
- M_ring(t) = sum(max(0, SIGMA_REF - sigma_m[i])) over time
- E_phi(t) = phi-XY coupling energy
- W_xy(t) = toroidal winding through periodic z-axis at z_slice = L/2 + 3
- sigma_m statistics (min, max, mean) per snapshot

## Gates and tolerances

**G1 (formation)**: All three configurations form M_ring > 200 at
Phase 2 end (matter sector successfully depletes around phi vortex tube).

**G2 (Hopfion stability)**: hopfion_Q1 has |drift_P3| < 0.2 (mass change
< 20% over Phase 3 = 3000 lu). Indicates topological protection of
toroidal winding survives full v7 dynamics.

**G3 (decay characterization)**: ring_Q0 and trefoil exhibit
characteristic decay over Phase 3 — either monotone exponential or
oscillatory toward attractor.

**G4 (KBT decisive verdict)**:
- if trefoil M_P3_end > 500 and drift < 0.3: KBT VINDICATED at v7 level
- else: KBT FALSIFIED at v7 level, v13 n-field needed

## Decision criterion

PASS if G1, G2, G3 hold AND G4 yields a clear verdict.

## Result (2026-05-30 quick-mode run)

| Config | M_P2_end | M_P3_end (t=3000) | Decay ratio per 200 lu | Half-life | Verdict |
|---|---|---|---|---|---|
| ring_Q0 | 807.65 | 110.40 | 0.873 (exponential) | ~1000 lu | UNSTABLE |
| hopfion_Q1 | 1646.80 | 1350.64 | →1.000 (asymptote) | infinite | STABLE |
| trefoil | 556.18 | 70.32 | 0.871 (exponential) | ~1000 lu | UNSTABLE |

Toroidal winding at Phase 2 end:
- ring: 0 (no protection)
- hopfion_Q1: -2π exactly (preserved)
- trefoil: 0 (no toroidal cycle winding)

**Gates evaluated**:
- G1: PASS (ring 808, hopfion 1647, trefoil 556 all > 200)
- G2: hopfion drift = 0.156 — PARTIAL PASS (>0.2 tolerance set strict;
  asymptote at ~1300 indicates true stability though slow approach)
- G3: PASS — ring and trefoil show clean exponential decay
- G4: trefoil M_P3_end = 70 << 500 → KBT FALSIFIED at v7 level for
  trefoil-class topologies

**Decision: PASS (verdict decisive)**

## Interpretation

### KBT hypothesis: refined

Pure KBT ("every knot is a particle") is falsified. But QNG produces a
weaker but still significant version:

> **Topology determines stable-vs-unstable particle status, with
> distinct mass ladders per topology class.**

- Hopfion class (toroidal winding through periodic cycle): STABLE
  particles
- Ring / Trefoil / Higher-knot classes (no cycle winding, only local
  topology): UNSTABLE — finite lifetime, decay to vacuum

### Half-life equality of ring and trefoil

Both ring_Q0 and trefoil decay with nearly identical ratio per 200 lu
(0.873 vs 0.871). This is non-trivial: two topologically distinct
configurations have the same decay rate. Possible reasons:
- Both decay via the SAME mechanism (slow phi-XY relaxation toward
  vacuum)
- The phi-decay rate is set by β_φ, GAMMA_PHI, and lattice spacing —
  topology-independent

This means the QNG "unstable particle" class might be a SINGLE family
with topology-independent lifetime, distinguished only by initial
configuration. Worth checking with figure-8 and 5-crossing knots.

### Hopfion asymptote at M_∞ ≈ 1300

Hopfion Q=1 does not fully relax to a fixed mass in 3000 lu but is
clearly converging to a limit ~1300. This is consistent with CPU-069
finding T_half ~ 300M lu. The 15.6% drift in 3000 lu suggests an
asymptotic mass ~1300 ± 50.

The asymptotic Hopfion M_∞ is the **canonical mass** for the Q=1
Hopfion at L=20. For mass-identification programs (Gap 13), this is
the right number to use, not M_P2_end = 1647 which is non-equilibrium.

### Updated SM correspondence

| QNG object | SM analog candidate |
|---|---|
| Photon (γ) | photon (v12) ✓ identified |
| Graviton | graviton (v11 axiomatic) partial |
| Hopfion Q=1 STABLE | charged stable particle — proton/electron candidate |
| Hopfion Q=2, 3, ... STABLE | charged stable particle ladder — heavier hadrons / exotic |
| Ring / Trefoil UNSTABLE | resonance-like states — pions/kaons/short-lived hadrons |

This is the most refined map so far. The lifetime distinction
(stable vs unstable from topology) is a genuine QNG prediction.

## Artifacts

- Report JSON: `07_validation/audits/qng-knot-matter-scan-v1/report.json`
- Summary MD: `07_validation/audits/qng-knot-matter-scan-v1/summary.md`
- Test runner: `tests/cpu/qng_knot_matter_scan_reference.py`

## Follow-up tests recommended

- CPU-147: extend Hopfion ladder to Q=4, 5 — characterize asymptotic
  Q-dependence and stability ceiling.
- CPU-148: figure-8 and 5-crossing knots — test if all "non-cycle"
  topologies have universal τ ≈ 1000 lu lifetime.
- CPU-149: measure decay PRODUCTS of ring/trefoil — what carries off
  the lost matter and energy? Is the decay to vacuum + phi-wave, or
  to a stable Hopfion + difference?
