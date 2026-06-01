# QNG-CPU-079 audit summary — DER-QNG-046 tensorial cancellation

Type: `evidence`
Status: `diagnostic_fail` (assumption violation discovered)
Author: `C.D Gabriel`
Date: `2026-04-20`
Upstream: `DER-QNG-046`, `DER-QNG-044` Test 3f

## Purpose

Verify the DER-QNG-046 prediction that m_eff²(x) = (g/(2μ_φ)) · Δ²(x) ·
cos(φ_bg(x)) produces a large cos(φ_bg)-induced cancellation of the
bending integral, explaining why measured α(b) is 100× smaller than
scalar prediction.

## Gates

All three FAILED:

| Gate | Criterion | Result |
|------|-----------|--------|
| G1 cancellation | \|integ w/o cos\| / \|integ w/ cos\| > 10 for 2+ b | 1.01–1.07 (FAIL) |
| G2 tensorial α | α_tensorial < 1 rad at all b | 2–6 rad (FAIL) |
| G3 anisotropy | axis/trans with cos > 2 | 0.72 (FAIL) |

## Root cause

Inspection of φ[:,:, z=14] on cached ring reveals a **quadrupolar
phase pattern with min = −1.07 at ring center**, amplitude |φ| < 1.1,
**not a vortex with 2π winding**. The DER-QNG-046 §5 assumption
φ_bg(x,y) ≈ arctan((y−y_c)/(x−x_c)) is violated for this
configuration.

The v8 ring formation protocol (Phase-1: 300 lu φ vortex, Phase-2: 1500
lu σ_m ring) evidently does not preserve a pure 2π winding — the φ
field relaxes to a diffuse quadrupolar pattern coupled to σ_m.

## Surviving vs falsified

| Item | Status |
|------|--------|
| EOM derivation §1–§4 (Lagrangian → m_eff²) | surviving (correct) |
| Prediction §5.1 (thin-ring in-plane cancellation) | NOT TESTABLE (assumption violated) |
| Prediction §5.3 (anisotropy from cos(φ_bg)) | FAIL (not the dominant mechanism) |
| Prediction §5.4 (scalar 100× excess = cos cancellation) | FAIL |

## Revised interpretation

Given cached ring has cos(φ_bg) ≈ 0.88 (flat along path), the scalar
V_couple prediction of α ~ 10 rad stands. Measured α ~ 10⁻² rad.
The 100× gap is NOT explained by cos(φ_bg) cancellation.

Candidate alternative mechanisms:

1. **Eikonal breakdown**: wavelength ≈ 8 lu vs ring radius 4. Pulse is
   in diffraction regime, not geometric optics.
2. **Amplitude modulation**: measured "bending" Δy includes pulse
   amplitude growth (0.035 → 0.040) not pure deflection.
3. **Back-reaction O(A²) = 2.5×10⁻³**: matches measured order.

## Required follow-up

1. CPU-080 candidate: enforce 2π winding in initial phi and verify it
   persists; then re-test DER-QNG-046 prediction.
2. New GPU test: shorter-wavelength pulse (k_pkt > 1.5) to enter
   geometric-optics regime where true gravitational deflection can be
   cleanly measured.
3. DER-QNG-046 downgraded to `candidate-partial` — EOM structural,
   mechanism needs verification on proper winding.

## Files

- `tests/cpu/qng_tensorial_cancellation_reference.py`
- `07_validation/audits/qng-tensorial-cancellation-v1/report.json`
- `04_qng_pure/qng-pulse-ring-tensorial-coupling-v1.md` §11 postscript
