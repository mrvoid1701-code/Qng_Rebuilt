# QNG-CPU-078

Type: `prereg`
Status: `diagnostic_fail`
Author: `C.D Gabriel`
Date: `2026-04-20`
test_class: `derivation_verification`

## Title

Numerical verification of DER-QNG-045 scalar bending-angle formula
against measured α(b) on v8 canonical L=28 R=4 ring.

## Purpose

DER-QNG-045 derives α(b) for a vortex-ring gravitational source
treated as a thin σ_m deficit coupled via Channel G to σ_g. In
the far-field limit it predicts Einstein 1911's α ∝ 1/b; in the
near-field it introduces a geometric form factor F(b/R) encoding
the torus double-attractor structure.

This test evaluates the double-integral formula numerically at
b ∈ {3, 4, 6, 8} — the four impact parameters measured in
DER-QNG-044 Test 3f — and tests whether the analytical prediction
reproduces magnitude, sign, and far-field scaling of the
measurement.

A secondary diagnostic channel is also tested: the V_couple
m²(x) = g·(σ_m,ref − σ_m(x))² quadratic coupling, integrated along
the pulse path using the actual cached ring σ_m profile.

## Upstream

- DER-QNG-045 (torus bending formula)
- DER-QNG-044 Test 3f (measured α(b) for b = 3, 4, 6, 8)
- DER-QNG-042 (v8 canonical substrate)
- QNG-CPU-074 (canonical M_ring = 176.85 at L=28 R=4)

## Experimental design

### Part A — scalar σ_g Poisson analytic prediction

Evaluate the double integral from DER-QNG-045 §2.3:

```
α(b) = (k_gm · D) / (8π² c_φ²) · ∫_{u_min}^{u_max} du ∫_0^{2π} dθ
         (b − R sinθ) / ρ(u, θ, b, R)³
```

with R = 4, D = M_ring(R=4) = 176.85, k_gm = 0.10, c_φ² = 0.01167,
pulse path u ∈ [−10, +10] (matching L=28 ring at center x=14,
pulse from x=4 to x=24). Use trapezoidal quadrature with 2001 × 2001
grid.

Also evaluate the far-field monopole limit α_far(b) = −k_gm·D /
(2π·b·c_φ²) at b ∈ {10, 20, 40, 80} for the 1/b saturation check.

### Part B — lattice-direct comparison

Load the cached L=28 R=4 ring state
(`07_validation/audits/qng-v8-stability-probe-v1/ring_cache/`).
For each b ∈ {3, 4, 6, 8}, evaluate:

1. α_sg(direct) = −(1/c_φ²) ∫ ∂_y σ_g(x, y_c+b, z_c) dx — tests
   whether the scalar σ_g Poisson picture survives when the
   analytical thin-ring approximation is replaced by the actual
   lattice σ_g field.

2. α_m2(direct) = −(1/2ω²) ∫ ∂_y m²(x, y_c+b, z_c) dx with
   m²(x) = g · (σ_m,ref − σ_m(x))² — tests the V_couple direct
   mass-modulation channel.

## Checks (diagnostic gates)

| ID | Gate | Pass criterion |
|----|------|----------------|
| D1 | Ratio \|α_pred / α_meas\| within factor 3 at all b outside ring | 0.33 < \|α_full/α_meas\| < 3 for b ∈ {6, 8} |
| D2 | Sign of α_pred matches α_meas at all b ≥ R | sign(α_full) = sign(α_meas) for b ∈ {6, 8} |
| D3 | Form factor F(b/R) = α_full/α_far lies in [0.001, 0.5] for b ∈ {6, 8} | F quantifies ring-topology suppression |
| D4 | Far-field 1/b saturation: std/mean of b·α_far at b ∈ {10, 20, 40, 80} | < 0.20 |

## Result

**All four diagnostic gates FAIL:**

- D1: ratios are {0.0004, 1.6×10⁻⁶, 7.7×10⁻⁴, 1.5×10⁻³} — predicted
  α is 10² to 10⁶× LARGER than measured.
- D2: sign at b=3 is wrong (predicted +8.11, measured −3.4×10⁻³);
  singular at b=4 (on-rim); correct at b=6, 8.
- D3: F values {−0.11, 134, 1.39, 1.19} — singular at b=R, outside
  gate range.
- D4: std/mean = 0.58 — far-field 1/b not saturated on L=20 path.

**Lattice-direct (Part B):**

- α_sg(direct) = 0 at all b — because cached ring has σ_g = 0.5
  everywhere (ring_cache runs with default k_gm=0; Channel G never
  engages during ring formation).
- α_m2(direct) gives O(1) values with sign flips at b=4, 6 — the
  V_couple m² coupling is also too strong by ~10² and not
  consistently signed.

## Verdict

**DIAGNOSTIC_FAIL**: scalar Poisson (σ_g) and scalar V_couple (m²)
channels **both fail** to reproduce the measured α(b) in magnitude
and sign at finite path L=20.

## Interpretation

Consistent with DER-QNG-044 Test 3e anisotropy result (measured
P/T = 4.00 vs scalar-theory 1.31, excess 3.06×). **v8 bending is
not a scalar-gravitational phenomenon** — the mediating coupling is
tensorial or involves the pulse-background kinetic cross-term
`2 ∇φ_bg · ∇φ_pulse`.

This falsifies the "scalar-Poisson → 1911 Einstein analog" framing of
DER-QNG-045 §3.1–§3.2 as a quantitative prediction. The qualitative
observation (double-attractor, F(b/R) peaking near b ~ 1.5R) survives
as a structural feature but requires a tensorial derivation for its
absolute scale.

## Artifact paths

- `07_validation/audits/qng-torus-bending-analytic-v1/report.json`
- `07_validation/audits/qng-torus-bending-analytic-v1/summary.md`
- `tests/cpu/qng_torus_bending_analytic_reference.py`
