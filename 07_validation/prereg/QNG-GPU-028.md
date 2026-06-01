# QNG-GPU-028

Type: `prereg`
Status: `executed — NO_RESCUE`
Author: `C.D Gabriel`
Date: `2026-04-21`
test_class: `structural_diagnostic`
hardware: `GPU`
upstream: `QNG-GPU-024d v2` (H_NO_RING_IN_ANY_REGIME); `DER-QNG-048` (4D topology analysis); `DER-QNG-047` (no static ring in 3D)

## Title

Alternate V_couple forms — does any natural phi-deficit coupling stabilize the 3D ring?

## Purpose

GPU-024d v2 showed that both canonical V_couple (sine-Gordon) and
V_couple=0 dissolve the cached L=28 R=4 ring under v8 gradient flow
when Channel F is off. Remaining open: does some *other* natural
V_couple form — preserving some subgroup of U(1), or with different
local pull structure — admit a ring fixed point?

This test is the cheap prereq for GPU-027 (4D torus search). Per
DER-QNG-048 recommendation: if no alternative V_couple form rescues
the 3D ring, the obstruction is generic (V_couple + no Channel F),
not dimension-dependent, and GPU-027 is redundant.

## Configuration

- L=28, R=4, cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`,
  M_ring_base = 176.85
- dt_relax = 0.05 (overdamped gradient flow)
- N_ITER = 30000 (matches GPU-024d v2 Run B)
- g = G_V_COUPLE = 0.22 across all runs
- Channel F: OFF across all runs

## Variants

| label | V form | F_phi extra |
|---|---|---|
| a_phi_mass | (g/2)·Δ²·φ²/2 | `-0.5·g·Δ²·φ` (mass term; preserves U(1)) |
| b_double_pitch | (g/2)·Δ²·(1-cos 2φ) | `-g·Δ²·sin(2φ)` (Z₂ residual) |
| c_quartic | (g/4)·Δ²·(1-cos φ)² | `-0.5·g·Δ²·(1-cos φ)·sin φ` (weaker slope at 0) |
| d_control_V0 | 0 | 0 (baseline; matches GPU-024d v2 B) |

Δ ≡ `SIGMA_M_REF - sigma_m` (deficit).

## Hypothesis map

Threshold: SURVIVES (M_final ≥ 50), SHRUNK (1 ≤ M < 50), DISSOLVED (M < 1).

- **V_COUPLE_RESCUED** — at least one of (a), (b), (c) SURVIVES ⇒
  obstruction is sine-Gordon-specific; alternative potential admits
  static ring. GPU-027 (4D) becomes interesting.
- **V_COUPLE_PARTIAL** — all dissolve, but some significantly slower
  than (d). Partial stabilization; needs finer scan.
- **NO_RESCUE** — all behave like (d). Obstruction is structural
  (V_couple + Channel F off), not V_couple form. Pivot to Scenario A
  (dynamic orbit ontology).

## Result

**Verdict: NO_RESCUE.**

| label | M_initial | M_final | iter to dissolve | wall (s) | state |
|---|---|---|---|---|---|
| a_phi_mass | 176.85 | 0.046 | 18000 | 34.2 | DISSOLVED |
| b_double_pitch | 176.85 | 0.016 | 12000 | 22.9 | DISSOLVED |
| c_quartic | 176.85 | 0.070 | ≥30000 | 57.7 | DISSOLVED |
| d_control_V0 | 176.85 | 0.098 | ≥30000 | 54.0 | DISSOLVED |

Dissolution-speed ranking: b (fastest) < a < c ≈ d.

**Interpretation**: the LOCAL slope of V at φ=0 sets dissolution rate.
(b) has steepest slope (sin(2φ) at small φ is 2φ), dissolves fastest.
(c) and (d) have shallow slope near φ=0, dissolve slowest. (a) linear
pull ∝ g·Δ²·φ intermediate. No form provides a *stabilizing*
contribution — every term is dissipative on the ring.

## Downstream actions

- `DER-QNG-047` (`qng-v8-no-static-ring-v1.md`) → extend: no static
  ring in 3D under *any* natural V_couple family (canonical sine-
  Gordon, phi-mass, doubled-pitch, quartic, or V=0).
- `DER-QNG-048` (`qng-v8-4d-topology-analysis-v1.md`) → verdict
  confirmed: V_couple is not rescuable via natural symmetry
  alternatives. Class A (4D codim-2 T²) predicted to dissolve too.
  GPU-027 (4D) demoted from conditional to "confirmation test only".
- Pivot to Scenario A: particle = bounded orbit in v8 phase space,
  not static soliton. Next probe = symplectic long-run on cached ring
  + Poincaré section + Floquet analysis.

## Artifacts

- Script: `tests/gpu/qng_v8_alt_v_couple_search.py`
- Audit: `07_validation/audits/qng-v8-alt-v-couple-v1/`
  - `report.json`
  - `run.log`
  - `interpretation.md`
