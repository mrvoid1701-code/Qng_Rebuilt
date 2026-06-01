# QNG-GPU-022

Type: `prereg`
Status: `executed` (verdict: H_UNUSUAL_SLOPE_+1.54 — two-regime: H_tensorial PASS at s≤1, saturation at s=1.4)
Author: `C.D Gabriel`
Date: `2026-04-20`
Executed: `2026-04-20`
test_class: `derivation_verification`
hardware: `GPU`
upstream_derivation: `DER-QNG-046` (promotion checklist sub-item 2b)
predecessor: `QNG-GPU-021` (A-scan, H1 & H2 ruled out)
audit: `07_validation/audits/qng-v8-sigma-m-scan-v1/` (report.json + interpretation.md)

## Title

σ_m-deficit scan at fixed (k=3π/4, b=6, A=0.05) — distinguish tensorial
§1–§4 geometric coupling from path-curvature feedback as the source of
the A-independent bending residual identified by QNG-GPU-021.

## Purpose

The A-scan (QNG-GPU-021) ruled out O(A²) back-reaction (H1) and linear
kinetic-mode coupling (H2) as the dominant b > R bending residual
mechanism: α_resid was measured A-independent (slope +0.026, R²=0.88
over A ∈ {0.025, 0.050, 0.100}). Two candidates survive:

1. **Tensorial §1–§4** — DER-QNG-046 full tensorial EOM
   `m_eff²(x) = (g/(2μ_φ))·Δ(x)²·cos(φ_bg(x))`, integrated with the
   full pulse wavefunction (not the straight-line geometric-optics
   approximation used in §13). This is a direct linear functional of
   Δ², so scales as `s²` under Δ → s·Δ.

2. **Path-curvature feedback** — the scalar §13 prediction assumes
   the pulse travels on a straight line. The actual pulse is deflected
   by `α ∝ s²`, which brings it closer to the ring and samples a
   different Δ profile. The correction is second-order in the
   deflection angle, scaling as `(s²)² = s⁴`.

Scaling the ring deficit Δ → s·Δ (post-cache) while holding pulse
(k, A, b) fixed exposes these different orders.

## Hypothesis

### H_tensorial (DER-QNG-046 §1–§4 dominant)

`|α_resid(s)| ∝ s²` with statistical confidence: slope ∈ [1.7, 2.3]
on log-log fit of |α_resid| vs s, R² > 0.95.

⇒ b > R residual is the DER-QNG-046 tensorial geometric contribution
not captured by the §13 scalar reduction. Promotion item 4
(closed-form α) must be derived from tensorial EOM.

### H_path (path-curvature feedback dominant)

`|α_resid(s)| ∝ s⁴`: slope ∈ [3.7, 4.3], R² > 0.95.

⇒ b > R residual is a self-consistency correction to the scalar
§13 prediction. The scalar EOM is correct but must be iterated with
the actual deflected path. Promotion item 4 addressable by
self-consistent iteration of §13.

### H_mixed

Slope ∈ [2.3, 3.7] OR R² < 0.95 OR non-monotonic.

⇒ both mechanisms contribute. Wider s-scan or additional
discriminators needed.

### H_VOID (sign flip or α_resid → 0 at any s)

sgn(α_resid) flips within s-range, OR |α_resid(s=1)| < 3σ(baseline)
→ document and re-design.

## Configuration

- L = 28, R = 4, T_track = 250 lu, DT = 0.025 (Yoshida4 symplectic)
- c_φ = 0.10801 (from `BETA_PHI/(6 μ_φ)`)
- Source x = 4.0, detector x = 24.0, path = 20.0 lu
- Pulse: σ = 2.0, **A = 0.050** (fixed, mid-range from A-scan), k = 3π/4, b = 6
- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`,
  M_ring_base = 176.85 (cache HIT expected)
- **s_list = [0.7, 1.0, 1.4]** (committed pre-run)

Scaling protocol: after loading the cached ring, rescale
`sigma_m_scaled = SIGMA_M_REF - s · (SIGMA_M_REF − sigma_m)`.
Other fields (sigma_g, chi, phi, pi_m, pi_phi) unchanged. This
scales the σ_m deficit Δ(x) → s·Δ(x) while preserving φ_bg (winding
is zero on the v8 cache; see CPU-080).

Note: the scaled ring is NOT a Hamiltonian equilibrium at s≠1 and
will drift. The measurement protocol subtracts ring-bg evolution
(`phi_pulse = phi_rp − phi_bg`) which cancels any relaxation dynamics
common to both ring-only and ring+pulse runs.

### Runtime budget

- 1 vacuum run (s-independent) — 196 s
- 3 ring-bg runs (one per s) — 3 × 196 = 588 s
- 3 ring+pulse runs (one per s) — 3 × 196 = 588 s
- Total: 7 evolutions × 196 s ≈ 23 min

## Pre-registered analysis

For each s ∈ {0.7, 1.0, 1.4}:

1. Measure α_meas(s) via centroid Δy / path (standard protocol)
2. Measure α_scalar_th(s) via the DER-QNG-046 §13 integral on the
   SCALED Δ-profile
3. Compute α_resid(s) = α_meas(s) − α_scalar_th(s)

Sanity check: `α_scalar_th(s) / α_scalar_th(s=1) = s²` must hold to
within 1% (algebraic identity; failure indicates numerical bug).

Fit `log|α_resid|` vs `log s` by least squares (3 points, 1 free
slope, 1 intercept).

**Pre-committed verdict map:**

| Slope | R² | Verdict |
|-------|----|---------| 
| ∈ [1.7, 2.3] | > 0.95 | H_tensorial |
| ∈ [3.7, 4.3] | > 0.95 | H_path |
| ∈ [2.3, 3.7] | any | H_mixed |
| any | < 0.95 | H_mixed_noisy |
| sign flip | — | H_VOID |

## Commitments

1. **s-list committed PRE-RUN**: {0.7, 1.0, 1.4}. No widening post-hoc.
2. **Ring cache same as A-scan** (`ring_L28_R4_P1_300_P2_1000_*.npz`).
3. **A = 0.050 fixed** (mid-range from A-scan).
4. **k = 3π/4, b = 6 fixed** (same as A-scan).
5. **DT = 0.025, T_track = 250 lu** locked.
6. **Slope verdict bands committed pre-run**. No relaxation.
7. If `α_scalar_th(s)/α_scalar_th(1) ≠ s²` within 1%, VOID and
   report numerical instability (algebraic identity).
8. If ring drift destabilizes either bg or r+p evolution (e.g. φ
   blow-up, σ_m diverging), VOID and report.

## Artifacts

- Script: `tests/gpu/qng_v8_sigma_m_scan_probe.py` (to be written)
- Audit: `07_validation/audits/qng-v8-sigma-m-scan-v1/`
  - `report.json` — α_meas, α_scalar_th, α_resid for each s; slope, R²
  - `run.log` — console output
  - `interpretation.md` — slope fit, verdict, implications

## Decision rules (single-pass)

| Outcome | Implication for DER-QNG-046 |
|---------|------------------------------|
| H_tensorial | §1–§4 full EOM required for b > R; §13 scalar is structurally incomplete (not just path-uncorrected). Promotion item 4 targets tensorial closed form |
| H_path | §13 scalar is structurally correct; §13 + path-curvature iteration closes item 4. §1–§4 not required beyond what §13 already captures |
| H_mixed | Both mechanisms contribute comparably. Widen s-scan or add σ_g-scan as third discriminator |
| H_VOID | Re-design; possible numerical instability |

## References

### Upstream
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` (DER-QNG-046, §1–§4 tensorial EOM; §13 scalar reduction)

### Predecessor audits
- `07_validation/audits/qng-v8-bending-a-scan-v1/` (A-scan:
  A-independence, H1 & H2 ruled out)
- `07_validation/audits/qng-v8-bending-k-scan-v1/` (k-scan: eikonal
  in-core PASS, b > R sign residual identified)

### Downstream
- If H_tensorial: promotion item 3 (numerical m_eff²(x)) closes
  item 2b; item 4 opens tensorial closed-form program
- If H_path: §13 + iteration closes item 2b and item 4
- If H_mixed / VOID: park; design σ_g-scan or wider s-scan
