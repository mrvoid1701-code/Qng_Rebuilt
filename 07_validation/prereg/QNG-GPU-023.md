# QNG-GPU-023

Type: `prereg`
Status: `executed` (verdict: H_CLIP_REJECTED_REVERSE — candidate #1 RULED OUT; narrow detector was ~20% biased; saturation persists with wide window)
Author: `C.D Gabriel`
Date: `2026-04-20`
Executed: `2026-04-20`
Audit: `07_validation/audits/qng-v8-sigma-m-scan-wide-v1/`
test_class: `derivation_verification`
hardware: `GPU`
upstream_derivation: `DER-QNG-046` (promotion checklist item 2b, saturation follow-up)
predecessors: `QNG-GPU-022` (σ_m-scan, high-s saturation discovered), `QNG-CPU-081` (m_eff² profile, candidate #2 ruled out)

## Title

Widened-detector re-run of σ_m-scan at s ∈ {0.7, 1.0, 1.4}, fixed (k=3π/4,
b=6, A=0.05) — test candidate #1 (detector window clipping) as the source
of the high-s α_meas saturation observed in QNG-GPU-022.

## Purpose

QNG-GPU-022 found α_meas non-monotonic in s (+1.83e−02 at s=1.0, +1.65e−02
at s=1.4) despite a linear-regime extrapolation to ≈+2.56e−02 at s=1.4
(slope 2.09 in log-log, s=0.7→1.0). Four candidate mechanisms were
identified for this saturation:

1. **Detector window clipping** — detector uses 15 y-bins centred on
   y_pulse. Strong deflection at s=1.4 may push the pulse (or its tail)
   beyond this window, truncating the centroid estimate.
2. ~~**m_eff² saturation / evanescent tunneling**~~ — RULED OUT by
   QNG-CPU-081 (max m_eff²/ω² = 0.032 at b=6, s=1.4 < threshold 0.1).
3. **Ring self-distortion** — the post-cache s>1 rescaling leaves the
   ring out of Hamiltonian equilibrium; it may drift/distort during
   T_track and contaminate α_meas via imperfect ring-bg subtraction.
4. **Path-curvature lensing** — the scalar prediction's straight-line
   integral misses self-consistent path correction at high deflection.

This test targets candidate #1 by widening the detector window from
±7 bins (15 total) to ±12 bins (25 total) and re-running the same
(s, k, b, A) protocol. If α_meas at s=1.4 RECOVERS the linear
extrapolation (~+2.56e−02), candidate #1 is confirmed. If it stays near
+1.65e−02, candidate #1 is ruled out and candidate #3 becomes the lead.

## Hypothesis

### H_window_clip

`α_meas(s=1.4, wide) ≥ 2.30e−02` (within 10% of slope-2 extrapolation
from s=0.7→1.0 interval, i.e. ≥90% of +2.56e−02).

**AND** the log-log slope on the widened data matches H_tensorial bands
`∈ [1.7, 2.3]` with R² > 0.95.

⇒ Candidate #1 confirmed. Saturation is an artefact of narrow detector;
true α_meas follows tensorial §1–§4 (slope 2.00) throughout the scan.

### H_clip_rejected

`|α_meas(s=1.4, wide) − α_meas(s=1.4, narrow)| < 10% × α_meas(s=1.4, narrow)`
(i.e. wide and narrow agree to within 10%, both near +1.65e−02).

⇒ Candidate #1 ruled out. Saturation is real physics (candidates #3/#4).
The post-cache rescaling protocol (#3) becomes the leading suspect;
test via alternative ring-formation protocol in a future run.

### H_partial_clip

Widened α_meas(s=1.4) falls between 1.85e−02 (15% above narrow) and
2.30e−02 (below slope-2 extrapolation).

⇒ Candidate #1 partial contributor; other mechanism (#3 or #4) also
active. Narrower s-scan or alternative ring formation needed.

### H_VOID

`α_meas(s=1.4, wide)` sign-flips relative to narrow, OR amplitude collapses
(|α_meas| < 3σ of vacuum noise), OR numerical instability.

⇒ Re-design; possible pulse-field wrap interference from widened window.

## Configuration

Identical to QNG-GPU-022 except detector window:

- L = 28, R = 4, T_track = 250 lu, DT = 0.025 (Yoshida4 symplectic)
- c_φ = 0.10801 (from `BETA_PHI/(6 μ_φ)`)
- Source x = 4.0, detector x = 24.0, path = 20.0 lu
- Pulse: σ = 2.0, **A = 0.050** (fixed), k = 3π/4, **b = 6**
- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (cache HIT)
- **s_list = [0.7, 1.0, 1.4]** (identical to GPU-022 for direct comparison)
- **Detector y-half-width = 12** (25 total bins) — up from 7 in GPU-022

Detector bins: `y_det = arange(y_pulse − 12, y_pulse + 13) mod L`.
With y_pulse = 20 on L=28 lattice, window is y ∈ {8, 9, ..., 27, 0, 1, 2, 3, 4}.
Wraps minimally; no overlap with ring core (y=14).

Scalar prediction: identical formula on same (possibly scaled) ring,
UNCHANGED by detector width.

### Runtime budget

- 1 vacuum run (s-independent) — 196 s
- 3 ring-bg runs (one per s) — 3 × 196 = 588 s
- 3 ring+pulse runs (one per s) — 3 × 196 = 588 s
- Total: 7 evolutions × 196 s ≈ 23 min

## Pre-registered analysis

For each s ∈ {0.7, 1.0, 1.4}:

1. Measure α_meas(s, wide) via widened-window centroid Δy / path
2. Compute Δα = α_meas(s, wide) − α_meas(s, narrow) using GPU-022 values
3. Re-fit log-log slope on widened α_resid points

**Pre-committed verdict map:**

| Condition on α_meas(s=1.4, wide) | Slope (wide) | Verdict |
|-----------------------------------|--------------|---------|
| ≥ +2.30e−02 | ∈ [1.7, 2.3] | H_window_clip |
| within 10% of +1.65e−02 | any | H_clip_rejected |
| ∈ [+1.85e−02, +2.30e−02) | any | H_partial_clip |
| sign flip or collapse | — | H_VOID |

Secondary diagnostics:
- Δα_meas(s=1.0, wide vs narrow) — should be negligible if narrow was
  already unclipped at s=1.0. Acts as control.
- Δα_meas(s=0.7, wide vs narrow) — likewise control, should be ≈0.

## Commitments

1. **Detector half-width = 12** committed PRE-RUN. No retuning.
2. **s-list = {0.7, 1.0, 1.4}** identical to GPU-022.
3. **Cached ring** identical to GPU-022 (same hash).
4. **A, k, b, DT, T_track** locked to GPU-022 values.
5. **Verdict bands committed pre-run**. No relaxation.
6. If scalar s²-sanity deviates >1% from algebraic identity, VOID.
7. If ring-bg blows up for any s (sigma_m diverges, φ → NaN), VOID.

## Artifacts

- Script: `tests/gpu/qng_v8_sigma_m_scan_wide_probe.py` (to be written)
- Audit: `07_validation/audits/qng-v8-sigma-m-scan-wide-v1/`
  - `report.json` — α_meas_wide, α_meas_narrow (from GPU-022), Δα per s;
    slope + R² on widened data
  - `run.log` — console output
  - `interpretation.md` — verdict + saturation mechanism resolution

## Decision rules (single-pass)

| Outcome | Implication |
|---------|-------------|
| H_window_clip | Candidate #1 confirmed. Saturation is artefactual. Tensorial §1–§4 slope 2 holds across full s range. Document and move on |
| H_clip_rejected | Candidate #1 ruled out. Candidate #3 (self-distortion) becomes lead. Pre-register alternative ring-formation protocol (direct Phase-2 tuning for target M_ring) |
| H_partial_clip | Both #1 and (#3 or #4) contribute. Design alternative ring formation AND widen s-scan to separate |
| H_VOID | Investigate; possible wrap interference from widened window |

## References

### Upstream
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` (DER-QNG-046 §1–§4)

### Predecessor audits
- `07_validation/audits/qng-v8-sigma-m-scan-v1/` (σ_m-scan: saturation discovered)
- `07_validation/audits/qng-v8-bending-a-scan-v1/` (A-scan: H1/H2 ruled out)
- `07_validation/audits/qng-v8-m-eff-profile-v1/` (m_eff² profile: candidate #2 ruled out)

### Downstream
- If H_window_clip: saturation mystery closed; tensorial §1–§4 fully validated on scanned s range
- If H_clip_rejected: pre-register QNG-GPU-024 (alternative ring formation for candidate #3)
