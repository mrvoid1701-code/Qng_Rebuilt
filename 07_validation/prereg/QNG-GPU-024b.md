# QNG-GPU-024b

Type: `prereg`
Status: `executed`
Author: `C.D Gabriel`
Date: `2026-04-20`
Verdict: `H_INTRINSIC` (pre-committed). Re-read: chi_decay has zero effect under k_gm=0 (A=B byte-identical); V_couple off alters trajectory but doesn't stabilize (C drift 713%). Only untested term is Channel F — leading suspect. Follow-up: QNG-GPU-024c with new `channel_f` flag. Interpretation: `07_validation/audits/qng-v8-ring-stability-diag-v1/interpretation.md`.
test_class: `structural_diagnostic`
hardware: `GPU`
upstream: `QNG-GPU-024` (ring stability finding — cached ring metastable under Phase-2)
predecessors: `QNG-GPU-024`, `CLAUDE.md` three-phase protocol

## Title

Ring stability diagnostic — which Hamiltonian term drives the Phase-2
chaos? Run cached s=1.0 ring under three reduced-dynamics configurations
to localize the driver of the M_ring oscillations observed in GPU-024.

## Purpose

GPU-024 showed the cached ring is metastable under full Phase-2 dynamics
(v_couple_on=True, chi_decay=0.020): M_ring jumps 177 → ~1400 within 50 lu.
Before scheduling the expensive GPU-025 Phase-3-mode bending re-run, we
need a **quick diagnostic** answering: which term is the chaos driver?

Three candidates:
- **V_couple** `(g/2)·(σ_m_ref − σ_m)²·(1 − cos φ)` — the sine-Gordon
  Yukawa coupling. Known to break U(1) → Z (CPU-080). Non-linear, could
  drive parametric instabilities.
- **χ dissipation** (`chi_decay = 0.020`) — though formally dissipative,
  it may destabilize certain modes at the cached equilibrium.
- **Channel F** (`GAMMA_PHI * disorder * sm`) — built into
  `compute_sm_force_v8`, not exposed in `yoshida4_step` signature (quick
  test cannot switch it off without code modification).

## Hypothesis map

Three runs at s=1.0, T=250 lu, cached ring L=28 R=4:

| Config | v_couple_on | chi_decay | Channel F |
|--------|-------------|-----------|-----------|
| A (control, = GPU-024) | True | 0.020 | active |
| B (chi_decay off) | True | 0.0 | active |
| C (coupling off) | False | 0.0 | active |

Expected GPU-024 reproduction: A ≈ +702% drift (s=1.0 result).

### H_V_COUPLE_DRIVER

A chaotic, B chaotic, C stable (<5% M_ring drift).
⇒ V_couple is the chaos driver. Consistent with sine-Gordon Z vacuum
non-linearity. Phase-3 measurement must turn off V_couple OR use a
V_couple-compatible stable ring ansatz.

### H_CHI_DECAY_DRIVER

A chaotic, B stable (<5%), C stable.
⇒ χ dissipation at CHI_DECAY=0.020 destabilizes the ring. Surprising
given DER-QNG-034 stability analysis. Phase-3 with chi_decay=0 is the
measurement mode; GPU-025 can proceed with minimal code change.

### H_CHANNEL_F_DRIVER

A chaotic, B chaotic, C chaotic.
⇒ Neither V_couple nor chi_decay is the sole driver. Channel F (always
active in this diagnostic) is the probable culprit. Requires
`yoshida4_step` modification to add channel_f flag before GPU-025.

### H_INTRINSIC

A chaotic, B chaotic, C chaotic, AND trajectories differ significantly
from each other.
⇒ Multiple couplings interact; no single-term fix. Theory audit of
v8 ring equilibrium becomes mandatory before GPU-025.

## Decision rules

Drift threshold: **<5% M_ring rel drift** counts as "stable" (matches
pre-committed ADIC thresholds from GPU-024).

| Config outcome | Verdict |
|----------------|---------|
| A=chaos, B=chaos, C=stable | H_V_COUPLE_DRIVER |
| A=chaos, B=stable, C=stable | H_CHI_DECAY_DRIVER |
| A=chaos, B=chaos, C=chaos, B≈C traj. | H_CHANNEL_F_DRIVER |
| A=chaos, B=chaos, C=chaos, trajectories differ | H_INTRINSIC |

## Configuration

- L=28, R=4, cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`
- s=1.0 only (one scaling, three configs = 3 evolutions)
- T_track = 250 lu, sample every 10 lu
- Same M_ring, r_CM, RMS_drift metrics as GPU-024

## Commitments

1. Three configs committed above. No post-hoc additions.
2. Metric thresholds identical to GPU-024.
3. Single s = 1.0 only (saves runtime; chaos already observed in all s).

## Runtime

- 3 × 196 s ≈ 10 min.

## Decision tree → next test

| Verdict | Next test |
|---------|-----------|
| H_V_COUPLE_DRIVER | GPU-025 with `v_couple_on=False` (breaks Hamiltonian though — needs theory audit of whether V_couple-off measurement is physically meaningful) |
| H_CHI_DECAY_DRIVER | GPU-025 minimal: reuse yoshida4_step with `chi_decay=0` during T_track (quickest path) |
| H_CHANNEL_F_DRIVER | Modify yoshida4_step to expose channel_f flag → then GPU-025 |
| H_INTRINSIC | Halt all bending measurements; theory audit of H_v8 ring equilibrium |

## Artifacts

- Script: `tests/gpu/qng_v8_ring_stability_diagnostic.py`
- Audit: `07_validation/audits/qng-v8-ring-stability-diag-v1/`
