# QNG-GPU-024c

Type: `prereg`
Status: `executed — H_NO_EQUILIBRIUM`
Author: `C.D Gabriel`
Date: `2026-04-20`
Executed: `2026-04-20`

## Result

**Verdict: H_NO_EQUILIBRIUM**. Both D (469%) and E (452%) chaotic at
~5% threshold. Channel F ruled out as sole driver. GPU-025 halted;
escalated to GPU-024d (gradient-flow static ring search); see
`qng-v8-ring-stability-channelf-v1/interpretation.md`.

test_class: `structural_diagnostic`
hardware: `GPU`
upstream: `QNG-GPU-024b` (V_couple and chi_decay ruled out as sole drivers)

## Title

Ring stability diagnostic — is Channel F (`-GAMMA_PHI*disorder*sm`)
the chaos driver? Test via newly-added `channel_f` flag in
`yoshida4_step` / `verlet_substep` / `force_sm_v8`.

## Purpose

GPU-024b narrowed the chaos driver to Channel F by elimination:
chi_decay has zero effect under k_gm=0 (A=B byte-identical);
V_couple off changes trajectory but does NOT stabilize. Channel F
was the only untested term, hardcoded in `compute_sm_force_v8`.

Code modification added (2026-04-20): `force_sm_v8` and its callers
now accept a `channel_f` flag (default True, backwards compatible).
`channel_f=False` skips the `-GAMMA_PHI*disorder*sm` term.

## Configuration

- L=28, R=4, cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`
- s=1.0 (unmodified cached ring, M_ring_base=176.85)
- T_track=250 lu, sample every 10 lu
- Two configs:
  - **D** (physical candidate): v_couple_on=True, chi_decay=CHI_DECAY_V7, channel_f=False
  - **E** (null test, all nonlinear off): v_couple_on=False, chi_decay=0, channel_f=False

## Hypothesis map

Threshold: **<5% M_ring rel drift** = "stable" (same as GPU-024/024b).

### H_CHANNEL_F_DRIVER

D stable (<5% drift).
⇒ Channel F confirmed as chaos driver. Phase-3 measurement mode is
`v_couple_on=True + channel_f=False`. GPU-025 can proceed with this
minimal patch. Ring has a stable equilibrium in v8 3D provided
Channel F is switched off during measurement.

### H_MIXED

D chaotic (>5%), E stable.
⇒ Channel F + V_couple together drive the chaos; no single-term
fix. V_couple-off measurement mode is non-physical (breaks the v8
Hamiltonian). Measurement-mode definition becomes a structural
problem; GPU-025 needs further thought.

### H_NO_EQUILIBRIUM

D chaotic, E chaotic.
⇒ The cached ring does NOT admit a stable fixed point under any
accessible v8 3D Hamiltonian regime. The instability is intrinsic
to the ring-on-3D-cubic-lattice configuration. Consequences:
- Re-opens NOTE-QNG-014 (action principle) with sharpened claim:
  H_v8 has no static ring equilibrium
- Strengthens DER-QNG-044 finding "rings are dynamic patterns"
  into a structural theorem-like statement
- Dimension hypothesis (user, 2026-04-20) promoted: 3D lattice may
  structurally fail to admit ring equilibrium; 4D test (QNG-GPU-026)
  becomes diagnostic, not exploratory

### H_ANOMALOUS

D stable, E chaotic. Unlikely but recorded for completeness.

## Decision tree

| Verdict | Next action |
|---------|-------------|
| H_CHANNEL_F_DRIVER | Write GPU-025 σ_m-scan with `channel_f=False` during T_track. ~20 min runtime. |
| H_MIXED | Halt GPU-025; theory audit of measurement-mode definition in v8 |
| H_NO_EQUILIBRIUM | Halt GPU-025; (1) NOTE-QNG-014 sharpened reopening, (2) pre-register GPU-026 4D KG dispersion diagnostic |

## Runtime

- 2 × 196 s ≈ 7 min

## Artifacts

- Script: `tests/gpu/qng_v8_ring_stability_channelf.py`
- Audit: `07_validation/audits/qng-v8-ring-stability-channelf-v1/`
