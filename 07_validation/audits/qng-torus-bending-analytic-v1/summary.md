# QNG-CPU-078 audit summary — DER-QNG-045 bending formula diagnostic

Type: `evidence`
Status: `diagnostic_fail` (scalar channels ruled out)
Author: `C.D Gabriel`
Date: `2026-04-20`
Upstream: `DER-QNG-045`, `DER-QNG-044` Test 3f

---

## Purpose

Numerically evaluate the scalar-Poisson bending-angle prediction from
`DER-QNG-045 §2.3` at the four impact parameters where `DER-QNG-044`
Test 3f measured α(b) on a v8 canonical L=28 R=4 ring. Compare
magnitudes, signs, and the far-field 1/b limit.

## Result summary

| b | α_full (analytic) | α_far (monopole) | α_measured | α_full / α_meas |
|---|---|---|---|---|
| 3 | +8.11 | −77.0 | −3.4×10⁻³ | wrong sign |
| 4 | −7515 (singular) | −56.0 | −1.2×10⁻² | 6.4×10⁵ over |
| 6 | −48 | −34.5 | −3.7×10⁻² | 1.3×10³ over |
| 8 | −28 | −23.5 | −4.2×10⁻² | 660× over |

Far-field 1/b check:
`b · α_far` at b ∈ {10, 20, 40, 80} gives {-170, -108, -58, -30} — a
factor-2 drop across the grid (std/mean = 0.58), indicating the 20-node
finite path has NOT reached the asymptotic 1/b regime.

## Lattice-direct check against cached L=28 R=4 ring

Loaded the cached ring state and integrated transverse gradients
directly along the pulse path:

| b | α_direct(σ_g) | α_direct(m²=g·δ²) | α_measured |
|---|---|---|---|
| 3 | 0.00 | −2.66 | −3.4×10⁻³ |
| 4 | 0.00 | +4.13 | −1.2×10⁻² (wrong sign) |
| 6 | 0.00 | +10.3 | −3.7×10⁻² (wrong sign) |
| 8 | 0.00 | −9.26 | −4.2×10⁻² |

Key finding 1 (σ_g channel is inert in the cached ring):
The σ_g field is literally 0.5 everywhere (`<σ_g> = 0.5`, `min = 0.5`).
Root cause: `qng_v8_ring_cache.py` calls `yoshida4_step` without passing
`k_gm` — the default `k_gm = 0.0` turns off Channel G during ring
formation. The cached ring therefore has **no gravitational σ_g
profile** at all. The measured α(b) ≠ 0 cannot be sourced by σ_g.

Key finding 2 (V_couple m² channel magnitudes too large, signs unstable):
The quadratic V_couple coupling m²(x) = g · (σ_m,ref − σ_m(x))² was
tested as the alternative scalar channel. It yields α values of
order 1–10 rad, which is still 100× larger than measured and flips
sign at b=4, 6.

## Interpretation

Both scalar coupling channels available in v8 fail to reproduce the
measured bending in magnitude and sign:

1. Scalar σ_g Poisson (DER-QNG-045 as written): wrong by ~10³× and
   is physically inert in the current ring_cache configuration.
2. Scalar V_couple m²(x): wrong by ~10² and sign-inconsistent at some b.

This is **consistent with the anisotropy finding** from DER-QNG-044
Test 3e: scalar theory predicts P/T = 1.31, measured 4.00, excess
factor 3.06× beyond scalar — already flagged as tensorial /
kinetic-mode coupling. The bending measurement confirms the same
diagnosis on a different observable.

**Net conclusion**: v8 bending is **not** mediated by a scalar
gravitational potential. The coupling carrying the measured deflection
is direction-dependent (tensorial) or involves the pulse-background
kinetic cross-term `2 ∇φ_bg · ∇φ_pulse`.

## Required next steps

1. **DER-QNG-045 revision** (postscript added): note that the scalar
   Poisson section §2–§3 gives order-of-magnitude disagreement at
   finite path; the formula recovers the correct qualitative
   sign pattern only outside the ring domain (b > R), not inside.

2. **DER-QNG-046 (new)**: derive the tensorial / kinetic-cross-term
   coupling. Start from the full v8 action and expand V_couple
   and the φ kinetic term around a background phi-vortex to
   extract the non-scalar contribution `2·∂_μ φ_bg · ∂^μ φ_p`.
   Predict α(b) from this channel and compare to CPU-078 numerics.

3. **Re-run ring cache with k_gm ≠ 0**: the current cached ring has
   no σ_g gradient because `yoshida4_step` was called with default
   `k_gm=0`. A corrected cache should reveal whether a true σ_g
   profile modifies the bending result.

## Files

- `tests/cpu/qng_torus_bending_analytic_reference.py` (this test)
- `07_validation/audits/qng-torus-bending-analytic-v1/report.json`
- `04_qng_pure/qng-torus-gravity-v1.md` (DER-QNG-045, postscript added)
