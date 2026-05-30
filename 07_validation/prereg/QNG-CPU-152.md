---
test_id: QNG-CPU-152
title: Full v12 EM dynamics — refinement of CPU-151 prediction
category: structural / electromagnetic
hardware: cpu
type: pre-registration
status: completed (with REFINED interpretation)
date_filed: 2026-05-30
upstream:
  - DER-QNG-076 (v12 EM extension axiom)
  - DER-QNG-092 §F + §G (CPU-151 static prediction, Paper 7 P1)
  - CPU-146, CPU-148 (v7 baselines)
  - Paper 7 §3.5
---

# QNG-CPU-152 — Full v12 EM dynamics implementation

## Purpose

Paper 7 §3.5 (CPU-151) predicted that under v12 EM with dynamic A_ij,
topology-dependent decay rate spread would be factor 2.5 (ring slowest,
cinquefoil fastest). CPU-152 implements the full v12 dynamics and
tests whether this prediction holds in actual simulation.

## Inputs

L=20 cubic lattice. Six initial configurations: ring_Q0, hopfion_Q1,
hopfion_Q2, trefoil, figure_8, cinquefoil. Same construction as
CPU-148/146.

**v12 parameters (canonical)**:
- e_CHARGE = 0.3 (QED analog)
- mu_A = 1.0 (Maxwell mass)
- BETA_A = 0.05 (A relaxation rate)

Three-phase protocol: P1=300, P2=1500, P3=3000 steps.

Phi update uses gauge-invariant cos(phi_i - phi_j - e·A_ij).
A update: gradient flow on H_phi + H_A (Maxwell plaquette).

## Gates

**G1 (factor 2.5 spread test)**: spread of decay rate across local
knots (ring, trefoil, figure_8, cinquefoil) > factor 2.0 (margin
allowing some deviation from exact CPU-151 prediction).

**G2 (universality preservation)**: if G1 fails, check that within-knot
universality is preserved — that v12 doesn't ADD spurious topology
dependence either.

**G3 (Hopfion saturation)**: Q=1 and Q=2 Hopfions have similar decay
rates under v12.

## Decision

PASS_FULL if G1 + G3.
PASS_NEG if G1 fails but G2 confirms v7-universality preserved.
FAIL if v12 produces spurious topology dependence not predicted.

## Result (2026-05-30)

| Knot | τ_v12 (lu) | τ_v7 baseline | Ratio v12/v7 |
|---|---|---|---|
| ring_Q0 | 995 | 1000 | 0.995 |
| trefoil | 986 | 1011 | 0.975 |
| figure_8 | 1023 | 1050 | 0.974 |
| cinquefoil | 1043 | 1070 | 0.975 |
| hopfion_Q1 | 11476 | stable attractor | (slow decay observed) |
| hopfion_Q2 | 12572 | (not measured) | — |

Decay rate spread within local knot class: 995 to 1043 lu = factor 1.058
(5.8% spread).

|A_ij| stays at ~10⁻³ throughout the simulation. E_gauge stays at
<0.01 — essentially negligible.

**Gates evaluated**:
- G1: **FAIL** (spread is 1.06, not 2.0+)
- G2: **PASS** (v7 universality preserved within ~5%; no spurious
  topology dependence introduced)
- G3: **PASS** (Q=1 and Q=2 have similar decay timescales, ~12000 lu;
  slight difference 8% within Hopfion-Q ladder)

**Decision: PASS_NEG** — CPU-151 strong prediction falsified, but
framework consistency confirmed.

## Diagnosis

A_ij doesn't grow because of timescale mismatch:
- BETA_PHI = 0.02 per step → phi relaxes in ~50 steps
- BETA_A * e * BETA_PHI / Z = 0.05 * 0.3 * 0.02 / 6 ≈ 5×10⁻⁵ per step
  → A would need ~10⁵ steps to equilibrate to its "static" value
- Knots decay in ~10³ steps — much faster than A equilibration

Therefore A remains at |A| ~ 10⁻³ during knot decay, far below the
"static" equilibrium that CPU-151 assumed.

CPU-151's static analysis (E_gauge = Σ F_p² assuming A absorbs full
phi-curl) gave the EQUILIBRIUM gauge energy. CPU-152 shows that the
ACTUAL dynamics never reaches this equilibrium at canonical parameters.

## Implication for Paper 7 P1

The original P1 statement:
> "Under v12 EM, topology-dependent decay rate spread is factor 2.5"

Must be refined to:
> "Under v12 EM at canonical (small e=0.3, BETA_PHI=0.02) parameters,
> v7 within-knot universality is preserved (spread ~5%). CPU-151's
> factor 2.5 represents the EQUILIBRIUM spread that would emerge if A
> could fully relax; under v7 dissipative dynamics on relevant
> timescales, this equilibrium is not reached."

For SM-like topology-dependent lifetime diversity, QNG would need
either:
1. Much stronger gauge coupling (e ≫ 0.3) — physically motivated if
   QNG-e corresponds to GUT-scale unified coupling rather than low-energy QED
2. Symplectic v8 dynamics where A has explicit kinetic energy and can
   propagate freely
3. v13 SU(2)/SU(3) extensions providing fast decay channels via
   weak/strong interactions

## Status

Strong CPU-151 prediction: FALSIFIED for canonical parameters.
Framework consistency: CONFIRMED (v12 doesn't introduce spurious
non-universality).
Path forward: explore non-canonical parameters or v8 symplectic with A
dynamics (proposed CPU-160 series).

## Artifacts

- Report: `07_validation/audits/qng-v12-dynamics-v1/report.json`
- Test runner: `tests/cpu/qng_v12_dynamics_reference.py`

## Follow-up tests recommended

- CPU-160: same v12 dynamics with enhanced coupling (e=1.0, 3.0) to
  test if 2.5x spread emerges with stronger gauge interaction
- CPU-161: v12 dynamics under v8 symplectic (Yoshida4 integrator with
  A momentum)
- CPU-162: parameter scan e × BETA_PHI to map the regime where v12 EM
  contributes meaningfully vs negligibly to decay
