# QNG-GPU-021

Type: `prereg`
Status: `executed` (verdict: H3_MIXED_LOW_R2 — slope +0.026, R²=0.88; A-independent residual)
Author: `C.D Gabriel`
Date: `2026-04-20`
Executed: `2026-04-20`
test_class: `derivation_verification`
hardware: `GPU`
upstream_derivation: `DER-QNG-046` (promotion checklist sub-item 2a)
audit: `07_validation/audits/qng-v8-bending-a-scan-v1/` (report.json + interpretation.md)

## Title

Pulse-amplitude scan (A-scan) at fixed (k=3π/4, b=6) — separate
O(A²) back-reaction from amplitude modulation / kinetic-mode coupling
for the b > R bending sign residual identified by the GPU k-scan
(audit `qng-v8-bending-k-scan-v1`).

## Purpose

The k-scan (QNG-GPU-020 family, audit `qng-v8-bending-k-scan-v1`,
2026-04-20) confirmed eikonal recovery of the DER-QNG-046 scalar
prediction at b=4 (in-core) — `ratio = α_meas/α_scalar_th = +1.154` at
k=3π/4. At b=6 (out-of-core) the magnitude recovers (|ratio|=1.264) but
the **sign disagrees**: measured α stays positive across all k while
scalar prediction flips between +0.31, −0.13, −0.014.

DER-QNG-046 §11 lists three candidate mechanisms for residual α not
captured by the scalar EOM:

1. **O(A²) back-reaction** — the pulse modulates σ_m by O(A²),
   returning a deflection scaling as A².
2. **Amplitude modulation** — pulse scattering off the ring far-field
   σ_m gradient produces centroid drift scaling as A.
3. **Kinetic-mode coupling** — pi_φ ↔ pi_m channel not in the scalar
   V_couple-only reduction; scaling depends on coupling form.

The A-scan exploits the different A-scalings to discriminate.

## Hypothesis

### H1 (back-reaction dominant)

`α_meas(A) ∝ A²` with statistical confidence (R² > 0.95 on log-log
fit of |α| vs A, slope ∈ [1.7, 2.3]).

⇒ b > R residual is non-linear self-coupling of the pulse on the
ring; DER-QNG-046 EOM correct to linear order; quadratic-pulse
extension needed for b > R quantitative use.

### H2 (linear amplitude modulation / kinetic-mode dominant)

`α_meas(A) ∝ A` (slope ∈ [0.7, 1.3] on log-log).

⇒ b > R residual is a linear-order channel missed by the scalar
reduction. DER-QNG-046 §1–§4 EOM is **incomplete**; a kinetic
(pi-mediated) term must be added to recover b > R bending.

### H3 (mixed / saturated)

Slope ∈ [1.3, 1.7] OR R² < 0.95 OR α(A) non-monotonic.

⇒ both mechanisms contribute at comparable order at this A range.
A wider scan or different geometry needed; do not promote DER-QNG-046
on b > R basis.

### H4 (sign flip)

`sgn(α_meas)` changes within the A-range.

⇒ unstable regime; pre-registered VOID. Document and re-design.

## Configuration

- L = 28, R = 4, T_track = 250 lu, DT = 0.025 (Yoshida4 symplectic)
- c_φ = 0.10801 (BETA_PHI/(6 μ_φ))
- Source x = 4.0, detector x = 24.0, path = 20.0 lu
- Pulse: σ = 2.0 (fixed), **A_list = [0.025, 0.050, 0.100]**
- k_pkt = 3π/4 (eikonal regime, fixed)
- b = 6 (out-of-core, fixed)
- Cached ring: `ring_L28_R4_P1_300_P2_1000_*.npz` (cache HIT expected)

3 amplitudes × 3 evolutions (vacuum / ring-bg / ring+pulse) = 9
evolutions × ~196 s = ~30 min on GPU.

Note: ring-bg evolutions are A-independent → can be reused. With
caching, runtime drops to 1 ring-bg + 3 vacuums + 3 ring+pulse =
7 evolutions ≈ 23 min. Implementation should reuse ring-bg.

## Pre-registered analysis

For each A:
1. Measure α_meas (centroid Δy / path length, same protocol as k-scan)
2. Measure α_scalar_th (DER-QNG-046 scalar prediction; A-independent —
   sanity check it's the same number across runs)
3. Compute residual α_resid = α_meas − α_scalar_th

Fit log|α_resid| vs log(A) by least squares (3 points, 1 free slope).

**Pre-committed verdict map:**

| Slope | R² | Verdict |
|-------|----|---------| 
| ∈ [1.7, 2.3] | > 0.95 | H1 (back-reaction) |
| ∈ [0.7, 1.3] | > 0.95 | H2 (linear / kinetic-mode) |
| ∈ [1.3, 1.7] | any | H3 (mixed) |
| any | < 0.95 | H3 (no clear scaling) |
| sign flip | — | H4 (VOID) |

## Commitments

1. **A-list committed PRE-RUN**: {0.025, 0.050, 0.100}. No widening
   post-hoc.
2. **Ring cache must be the same as k-scan** (`ring_L28_R4_P1_300_P2_1000_*.npz`).
   No reformation.
3. **DT = 0.025, T_track = 250 lu** locked. Same as k-scan.
4. **Slope verdict bands committed pre-run**. No relaxation.
5. **k = 3π/4, b = 6 fixed**. No additional configurations in this prereg.
6. If `α_scalar_th` differs by > 1% across the three runs (it should
   be A-independent), VOID and report numerical instability.

## Artifacts

- Script: `tests/gpu/qng_v8_bending_a_scan_probe.py` (to be written)
- Audit: `07_validation/audits/qng-v8-bending-a-scan-v1/`
  - `report.json` — α_meas, α_scalar_th, α_resid for each A
  - `run.log` — console output
  - `interpretation.md` — slope fit, verdict, implications

## Runtime estimate

- 7 evolutions × 195 s = ~23 min on GPU (with ring-bg reuse)
- 9 evolutions × 195 s = ~30 min (without reuse)

## Decision rules (single-pass)

| Outcome | Implication for DER-QNG-046 |
|---------|------------------------------|
| H1 | Promotion sub-item 2a closed — non-linear correction; EOM correct to linear |
| H2 | EOM **incomplete**; kinetic-mode extension required (DER-QNG-047 candidate) |
| H3 | 2a remains open; need wider A-scan or different geometry |
| H4 | VOID; redesign |

## References

### Upstream
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` (DER-QNG-046,
  §11 candidate mechanisms, §13 k-scan postscript, promotion item 2a)
- `04_qng_pure/qng-v8-canonical-extension-v1.md` (DER-QNG-042, V_couple form)

### Predecessor audits
- `07_validation/audits/qng-v8-bending-k-scan-v1/` (k-scan: eikonal
  in-core PASS, b > R sign residual identified)
- `07_validation/audits/qng-torus-bending-analytic-v1/` (CPU-078 baseline)

### Downstream
- If H1: append to DER-QNG-046 §13 postscript as resolved
- If H2: open DER-QNG-047 candidate (kinetic-mode bending channel)
- If H3 or H4: park; widen scan in follow-up prereg
