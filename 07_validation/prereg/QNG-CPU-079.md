# QNG-CPU-079

Type: `prereg`
Status: `diagnostic_fail`
Author: `C.D Gabriel`
Date: `2026-04-20`
test_class: `derivation_verification`

## Title

Numerical verification of DER-QNG-046 cos(φ_bg) cancellation mechanism
on cached v8 L=28 R=4 ring.

## Purpose

DER-QNG-046 predicts pulse mass m_eff²(x) = (g/(2μ_φ)) · Δ²(x) ·
cos(φ_bg(x)). For a thin vortex ring with 2π winding, the bending
integral in the ring plane vanishes by u→−u antisymmetry of cos(φ_bg).
This would explain (a) why scalar predictions fail, (b) why the
measured P/T anisotropy is 4.00, and (c) why measured α is 10⁻² rad
vs scalar 10¹ rad.

This test loads the cached ring and evaluates the decomposition
α_scalar + α_winding from DER-QNG-046 §5.

## Upstream

- DER-QNG-046 (this document's theoretical framework)
- DER-QNG-042 (v8 canonical substrate)
- DER-QNG-044 Test 3f (measured α(b))
- CPU-078 (scalar channels FAILED — motivated tensorial derivation)

## Experimental design

Load cached `ring_L28_R4_P1_300_P2_1000_*.npz`. For each b ∈ {3,4,6,8}:

1. Sample Δ(x,y_c+b,z_c) along pulse path
2. Sample φ_bg(x,y_c+b,z_c) along pulse path
3. Compute ∂_y Δ and ∂_y φ_bg at path
4. Evaluate integrals:
   - I_naive = ∫ Δ · ∂_y Δ dx (scalar-only, no cos)
   - I_scalar = ∫ Δ · ∂_y Δ · cos(φ_bg) dx
   - I_winding = ∫ Δ² · sin(φ_bg) · ∂_y φ_bg dx
5. Compute cancellation factor |I_naive| / |I_scalar|

Also compute:
- axis-path integral ∫ Δ² · cos(φ_bg) dz at (x=14, y=14)
- transverse integral ∫ Δ² · cos(φ_bg) dx at (y=14, z=14)
- ratio axis/trans (predicts P/T)

## Gates (diagnostic)

| ID | Criterion |
|----|-----------|
| G1 | Cancellation factor > 10 at 2+ of b ∈ {3,4,6,8} |
| G2 | \|α_tensorial\| < 1 rad at all b (≤ order of measured 10⁻²) |
| G3 | axis/trans ratio with cos > 2 (explains P/T = 4) |

## Result

All FAILED. Cancellation factor 1.01–1.07 (not > 10). α_tensorial
still 2–6 rad. axis/trans = 0.72.

Root cause identified: cached φ does NOT have 2π winding — it is a
quadrupolar pattern with |φ| < 1.1 and min = −1.07 at center. The
DER-QNG-046 §5 cancellation mechanism assumes vortex winding that
is not present.

## Verdict

**DIAGNOSTIC_FAIL** (assumption violation, mechanism untested).

## Interpretation

- DER-QNG-046 §1–§4 (Lagrangian → EOM) remains theoretically rigorous.
- §5 cancellation mechanism untested — requires true 2π-winding ring
  (CPU-080 candidate).
- The 100× gap between scalar prediction and measurement is NOT
  due to cos(φ_bg) cancellation.
- Three alternative mechanisms now on the table: eikonal breakdown,
  amplitude modulation, O(A²) back-reaction.

## Next steps

1. CPU-080: initialize true 2π-winding vortex ring, verify persists
   through Phase 1+2, then re-run CPU-079 with proper winding.
2. Short-wavelength bending probe: k_pkt >> 1/R to enter geometric
   optics regime.
3. DER-QNG-046 downgrade to `candidate-partial` (done).

## Artifact paths

- `07_validation/audits/qng-tensorial-cancellation-v1/report.json`
- `07_validation/audits/qng-tensorial-cancellation-v1/summary.md`
