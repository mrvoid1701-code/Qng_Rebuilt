# GPU-028 interpretation — no V_couple form rescues the 3D ring

**Date**: 2026-04-21
**Script**: `tests/gpu/qng_v8_alt_v_couple_search.py`
**Run log**: `run.log`
**Report**: `report.json`
**Verdict**: `NO_RESCUE`

## What was tested

Four V_couple variants, each applied to the cached L=28 R=4 ring under
30000 iter gradient flow (dt=0.05). Baseline and three alternatives:

| label | form | F_phi extra term |
|---|---|---|
| a_phi_mass | (g/2)·Δ²·φ²/2 | `-0.5·g·Δ²·φ` (linear, preserves continuous U(1) as mass) |
| b_double_pitch | (g/2)·Δ²·(1-cos 2φ) | `-g·Δ²·sin(2φ)` |
| c_quartic | (g/4)·Δ²·(1-cos φ)² | `-0.5·g·Δ²·(1-cos φ)·sin φ` |
| d_control_V0 | 0 (no V_couple) | none |

## Result

**All four DISSOLVED.**

| label | M_0 | M_final | iter to dissolve | wall (s) |
|---|---|---|---|---|
| a_phi_mass | 176.85 | 0.046 | 18000 | 34.2 |
| b_double_pitch | 176.85 | 0.016 | 12000 | 22.9 |
| c_quartic | 176.85 | 0.070 | ≥30000 | 57.7 |
| d_control_V0 | 176.85 | 0.098 | ≥30000 | 54.0 |

## Interpretation

The ring dissolves under gradient flow **regardless of the V_couple
form chosen**. Three findings:

1. **V_couple is not the primary culprit.** Removing V_couple entirely
   (d) does not save the ring — it dissolves nearly identically to the
   canonical sine-Gordon (GPU-024d v2 Run A). This was already shown by
   GPU-024d v2 Run B; GPU-028 reconfirms.

2. **No coupling that ties phi to sigma_m deficit** (via any local
   functional form tried) **rescues the ring.** (a), (b), (c) all have
   different symmetry structure:
   - (a) preserves continuous U(1) as a mass term (no topological
     obstruction)
   - (b) has Z₂ residual symmetry (winding preserved mod 2π in theory,
     but the mechanism still forces phi toward a single vacuum at each
     deficit site)
   - (c) weakens the sine-Gordon pull (quartic vs quadratic)

   All three accelerate or match baseline dissolution. **Any
   phi-deficit coupling adds dissipation without providing stabilization.**

3. **The obstruction is structural to v8 gradient flow + Channel F off**,
   not to any particular V_couple choice. The cached ring exists only as
   a v7 gradient-flow equilibrium (where Channel F is active and
   balances sigma_m diffusion). Once Channel F is turned off for
   measurement purity, no combination of kinetic and potential
   v8 terms supports the ring as a static solution.

## Consequence

**Scenario (B) — "alternative V_couple rescues the ring"** is **ruled
out** for the three natural symmetry alternatives. The only ways this
could be escaped:

- A coupling that involves **non-local** operators (gauge fields,
  derivatives of phi coupling to sigma_m) — not "trivial" to justify
  ontologically
- A radically different potential shape that has been missed

Neither is likely to emerge from pencil analysis without new physics
input. **Scenario (A) — "particle = dynamic orbit in phase space,
not static soliton"** is therefore the load-bearing path forward.

## What the ordering tells us

Dissolution speed ranking: b < a < c ≈ d (faster → slower)

- **b fastest**: sin(2φ) gradient is steeper at small phi than sin(φ),
  so the Z vacuum pulls harder. Doubled-pitch is an ANTI-rescue.
- **a intermediate**: linear pull on phi from the phi² term; unwinds
  phi at rate proportional to the mass parameter `g·Δ²`.
- **c ~= d**: quartic term (1-cos φ)² is quadratic in (1-cos φ), so
  small phi deviations feel a weaker restoring force. For small
  residual winding, c behaves almost like d (no V_couple).

**Implication**: what matters is the LOCAL slope of V at phi=0.
Steeper slope → faster dissolution. The v7 ring's stabilizing
mechanism (Channel F) had to be strong enough to BEAT this local
slope, and it did so because Channel F produces a deficit-driven
phi disorder pull. Without Channel F, the local potential always
wins at the core.

## Downstream actions

- **Pivot formalization**: the QNG particle ontology shifts from
  "static topological soliton" to "bounded dynamical orbit of the v8
  Hamiltonian". DER-QNG-038 baryon mass identification remains as a
  **v7 conservation statement**; its physical meaning as "rest mass"
  requires a new bridge via invariant-orbit analysis.

- **Next probe (theoretical, not code)**: define what "bounded orbit"
  means in the v8 phase space. Candidates:
  - Poincaré section on L=28 R=4 trajectory under full v8 symplectic
    → look for invariant tori
  - Spectrum of Floquet multipliers around periodic orbits (if any)
  - KAM-like persistence of v7 equilibrium ring as v8 phase-space
    object

- **Next probe (code, cheap)**: run the cached ring under v8
  symplectic (not gradient flow) for 5000 lu, collect full phase-
  space trajectory sample, check boundedness. This is exactly
  GPU-024 + longer runtime, already feasible.

## Pre-reg table update

Add `QNG-GPU-028` (executed, NO_RESCUE). Increment prereg count.

## Status

**DER-QNG-047 (no static ring in 3D)** is not just about 3D — it's
about **v8 as a whole, under the canonical + natural-symmetry
V_couple family**. The ring-as-static-soliton ontology is **fully
deprecated**.
