# QNG-CPU-081

Type: `prereg`
Status: `executed` (verdict: H_transparent — max m_eff²/ω² = 0.032 at b=6 s=1.4; candidate #2 RULED OUT)
Author: `C.D Gabriel`
Date: `2026-04-20`
Executed: `2026-04-20`
Audit: `07_validation/audits/qng-v8-m-eff-profile-v1/`
test_class: `derivation_analysis`
hardware: `CPU`
upstream_derivation: `DER-QNG-046` (promotion checklist item 3)
predecessor: `QNG-GPU-022` (σ_m-scan, high-s saturation discovered)

## Title

Numerical m_eff²(x) profile analysis on cached v8 ring — test the
evanescent-tunneling candidate for the high-s saturation observed in
QNG-GPU-022.

## Purpose

The σ_m-scan (QNG-GPU-022) showed α_meas non-monotonic in s
(+1.825e−02 at s=1.0, +1.645e−02 at s=1.4). Four candidate
mechanisms were identified for this saturation; the present test
targets candidate #2 (m_eff² saturation → evanescent tunneling).

DER-QNG-046 §1–§4 tensorial EOM predicts an effective mass
`m_eff²(x) = (g/(2μ_φ))·Δ(x)²·cos(φ_bg(x))`
for pulse φ-waves propagating through the ring σ_m profile. The
Klein-Gordon dispersion `ω² = c_φ²k² + m_eff²` becomes evanescent
when m_eff² > ω² (group velocity imaginary; pulse tunnels /
attenuates exponentially).

Pulse parameters from GPU-021/022: k = 3π/4, ω = c_φ·k = 0.2545,
ω² = 0.0648, c_φ² = 0.01167.

If m_eff² > ω² anywhere along the pulse path, saturation is
explained by evanescence. If m_eff² ≪ ω² everywhere, candidate #2
is ruled out and saturation has a different origin (window clipping,
self-distortion, or path-curvature lensing).

## Hypothesis

### H_evanescent

`max_x m_eff²(x; s=1.4, b=6) ≥ ω² / 2 = 0.0324`
(defining "evanescent regime onset" as m_eff² reaching half the
pulse ω²; full evanescence at m_eff² ≥ ω²)

⇒ candidate #2 corroborated. High-s saturation explained by partial
wave reflection/tunneling through m_eff barrier.

### H_transparent

`max_x m_eff²(x; s=1.4, b=6) < ω² / 10 = 0.0065`

⇒ candidate #2 ruled out. The pulse sees negligible effective mass
along the b=6 path. Saturation is from #1/#3/#4.

### H_intermediate

`ω²/10 ≤ max_x m_eff²(x; s=1.4, b=6) < ω²/2`

⇒ partial contribution; evanescence not dominant but possibly
compounding with another mechanism.

## Configuration

Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (M_ring=176.85).

Parameters (from `qng_v8_canonical_gpu.py`):
- g = G_V_COUPLE = 0.22
- μ_φ = MU_PHI = 0.857
- BETA_PHI = 0.06
- SIGMA_M_REF = 1.0
- c_φ² = BETA_PHI/(6·μ_φ) = 0.01167
- k_pkt = 3π/4, ω² = c_φ² · k² = 0.0648

Analysis paths (matching GPU-021/022):
- x ∈ [4, 24] (integer grid), y = y_c + b, z = z_c = L/2
- b ∈ {4, 6} (in-core, out-of-core)
- s ∈ {0.7, 1.0, 1.4} (deficit scaling, same post-cache protocol as GPU-022)

For each (b, s):
1. Extract Δ(x) = SIGMA_M_REF − σ_m_scaled(x, y_c+b, z_c) along path
2. Extract φ_bg(x) along same path
3. Compute m_eff²(x) = (g/(2μ_φ))·Δ(x)²·cos(φ_bg(x))
4. Report max m_eff², mean m_eff², position of maximum
5. Compute reflection coefficient for 1D barrier (WKB-style):
   `R ≈ exp(−2 ∫_path √(max(m_eff² − ω², 0)) dx)` if anywhere evanescent

## Pre-committed verdict map

Primary verdict for candidate #2 (based on b=6, s=1.4):

| max m_eff² / ω² | Verdict |
|-----------------|---------|
| ≥ 1.0 | H_evanescent (strong — full barrier) |
| [0.5, 1.0) | H_evanescent (onset — partial) |
| [0.1, 0.5) | H_intermediate |
| < 0.1 | H_transparent |

Secondary reports:
- How much m_eff² changes from s=1.0 → s=1.4 (expected scaling: ×1.96 since m_eff² ∝ Δ²; if not, flag)
- b=4 vs b=6 contrast (in-core should have higher m_eff²)
- φ_bg sign structure along path (cos φ changes sign → m_eff² flips; could explain positive α_resid)

## Commitments

1. Single cached ring only: `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`
2. s-list committed: {0.7, 1.0, 1.4} (same as GPU-022 for traceability)
3. b-list committed: {4, 6} (one in-core, one out-of-core)
4. Verdict thresholds pre-committed (table above). No relaxation.
5. CPU only — no new GPU run. This is a post-processing analysis.

## Artifacts

- Script: `tests/cpu/qng_v8_m_eff_profile_reference.py` (to be written)
- Audit: `07_validation/audits/qng-v8-m-eff-profile-v1/`
  - `report.json` — max/mean m_eff², evanescent fractions, WKB R for each (b, s)
  - `m_eff_profile_*.npy` — raw path profiles (optional)
  - `interpretation.md` — verdict + candidate #2 resolution

## Decision rules (single-pass)

| Outcome | Implication |
|---------|-------------|
| H_evanescent (strong or onset) | Candidate #2 corroborated; saturation mechanism identified. Item 3 partially closed |
| H_intermediate | Candidate #2 compounding; still need GPU widened-window test for #1 |
| H_transparent | Candidate #2 ruled out; GPU widened-window test required as next step |

## References

### Upstream
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` (DER-QNG-046 §1–§4)

### Predecessor audits
- `07_validation/audits/qng-v8-sigma-m-scan-v1/` (σ_m-scan: saturation discovered)
- `07_validation/audits/qng-v8-bending-a-scan-v1/` (A-scan: H1/H2 ruled out)
- `07_validation/audits/qng-v8-bending-k-scan-v1/` (k-scan: eikonal in-core PASS)

### Downstream
- If H_evanescent: promotion item 3 partially closed; saturation documented
- If H_transparent: pre-register QNG-GPU-023 widened-detector re-run of σ_m-scan s=1.4
