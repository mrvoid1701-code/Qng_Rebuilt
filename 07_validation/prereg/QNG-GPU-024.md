# QNG-GPU-024

Type: `prereg`
Status: `executed`
Author: `C.D Gabriel`
Date: `2026-04-20`
Verdict: `H_DISTORTION_MIXED` (pre-committed logic) — reinterpreted as candidate #3 RULED OUT (s-independent instability) + structural methodology finding: cached ring is metastable under Phase-2 dynamics. See `07_validation/audits/qng-v8-ring-stability-v1/interpretation.md`.
test_class: `derivation_verification`
hardware: `GPU`
upstream_derivation: `DER-QNG-046` (saturation follow-up, candidate #3)
predecessors: `QNG-GPU-022` (σ_m-scan), `QNG-CPU-081` (m_eff²; #2 out), `QNG-GPU-023` (wide-detector; #1 out)

## Title

Ring self-distortion probe — measure M_ring, center-of-mass, and
profile-shape drift during T_track=250 lu on post-cache rescaled rings
at s ∈ {0.7, 1.0, 1.4}. Direct diagnostic of candidate #3 (non-
equilibrium ring self-distortion) for GPU-022 high-s saturation.

## Purpose

After GPU-023 ruled out candidate #1 (detector clipping), candidate #3
(ring self-distortion from post-cache rescaling) is the leading
suspect for the GPU-022 high-s α_meas saturation. The hypothesis:

> The post-cache rescaling `σ_m → SIGMA_M_REF − s·(SIGMA_M_REF − σ_m)`
> leaves the ring OUT of v8 Hamiltonian equilibrium at s ≠ 1. During
> T_track=250 lu, the ring drifts, changes shape, or moves, and the
> ring-bg subtraction (`φ_pulse = φ_rp − φ_bg`) fails to cancel these
> dynamics because they differ between the bg-only and ring+pulse runs.

Direct test: evolve the scaled ring alone (no pulse) for T_track lu and
monitor structural quantities. If the s=1.4 ring drifts significantly
while the s=1.0 ring stays stable, candidate #3 is confirmed and the
expensive equilibrium-ring formation protocol becomes justified.

## Hypothesis

### H_DISTORTION_CONFIRMED

At least one of:
- `ΔM_ring(s=1.4) / M_ring(0) > 5%` over T_track=250 lu
- `|Δr_CM(s=1.4)| > 0.5` lu (ring center-of-mass drift)
- `RMS[σ_m(T) − σ_m(0)](s=1.4) / SIGMA_M_REF > 5%`

WHILE the s=1.0 ring satisfies the same metrics at **<1%** / **<0.1 lu**.

⇒ Post-cache rescaling IS the saturation source. Pre-register
QNG-GPU-025 full equilibrium ring-formation protocol.

### H_DISTORTION_REJECTED

s=1.4 ring shows <2% drift on all three metrics (same order as s=1.0).

⇒ Candidate #3 ruled out. Saturation comes from path-curvature lensing
(#4) OR a mechanism not yet enumerated. Candidate #4 promoted;
closed-form α derivation with path correction becomes the direct
route.

### H_DISTORTION_PARTIAL

s=1.4 metric ∈ (2%, 5%), i.e. drift exists but is smaller than
threshold for H_confirmed.

⇒ Partial contribution; other mechanism also at play.

### H_VOID

Numerical instability (σ_m diverges, NaNs).

## Configuration

- L = 28, R = 4
- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (M_ring=176.85)
- v8 parameters locked (same as GPU-022/023)
- Evolution: yoshida4_step, DT=0.025, v_couple_on=True, CHI_DECAY=0.020
- T_track = 250 lu (10000 steps) — matches bending measurement
- s_list = {0.7, 1.0, 1.4}
- Sampling every 10 lu (400 steps) for structural quantities

Metrics per sample:
1. `M_ring(t) = sum(SIGMA_M_REF − σ_m)` — global deficit
2. Ring center of mass: `r_CM = Σ r · Δ / Σ Δ` (weighted by Δ=SIGMA_M_REF−σ_m)
3. Profile RMS change: `sqrt(mean((σ_m(t) − σ_m(0))²)) / SIGMA_M_REF`

## Pre-committed verdict map

| s=1.4 metrics | s=1.0 reference | Verdict |
|---------------|-----------------|---------|
| any ≥ 5% or r_CM ≥ 0.5 lu | all < 1% and < 0.1 lu | H_DISTORTION_CONFIRMED |
| all < 2% and < 0.2 lu | — | H_DISTORTION_REJECTED |
| ∈ (2%, 5%) or r_CM ∈ (0.2, 0.5) | — | H_DISTORTION_PARTIAL |
| divergence | — | H_VOID |

## Commitments

1. s-list committed: {0.7, 1.0, 1.4}
2. Metrics committed above. No new metrics post-hoc.
3. T_track=250 identical to GPU-022/023.
4. No pulse injected (pure ring evolution).
5. Single cached ring, same hash as predecessors.

## Runtime

- 3 s values × 250 lu × 40 steps/lu = 3 × 10000 = 30000 steps
- 3 × ~196 s = ~10 min

## Artifacts

- Script: `tests/gpu/qng_v8_ring_stability_probe.py` (to be written)
- Audit: `07_validation/audits/qng-v8-ring-stability-v1/`
  - `report.json` — time series for each metric per s
  - `run.log`
  - `interpretation.md`

## Decision rules

| Outcome | Implication |
|---------|-------------|
| H_DISTORTION_CONFIRMED | Candidate #3 = saturation source. Pre-register GPU-025 equilibrium-ring formation protocol. Subtraction protocol for post-cache rescaling is structurally biased — flag all previous s-scan data |
| H_DISTORTION_REJECTED | Candidate #3 ruled out. Candidate #4 (path-curvature lensing) promoted. DER-QNG-046 item 4 (closed-form α with path correction) becomes direct next step |
| H_DISTORTION_PARTIAL | Both #3 and #4 contribute. Both formation protocol AND path-corrected derivation needed |
| H_VOID | Investigate numerical setup |

## References

### Upstream
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` (DER-QNG-046)

### Predecessor audits
- `07_validation/audits/qng-v8-sigma-m-scan-v1/` (GPU-022 saturation)
- `07_validation/audits/qng-v8-m-eff-profile-v1/` (CPU-081 #2 ruled out)
- `07_validation/audits/qng-v8-sigma-m-scan-wide-v1/` (GPU-023 #1 ruled out)
