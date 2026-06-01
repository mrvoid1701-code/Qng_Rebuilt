---
type: test
test_id: QNG-GPU-048
category: gpu_scale
hardware: GPU
status: preregistered
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-058 graphity design (v9-G full plan)
  - QNG-GPU-046 v9-P (state-dependent chi noise FAIL)
  - QNG-GPU-044 (external vacuum noise FAIL)
---

# QNG-GPU-048 — v9-E edge-only Laplacian noise (intermediate variant)

## Purpose

Test whether noise injected into the **Laplacian operator weights** (not
χ directly) closes Einstein-Nyquist FDT in v8.

**Hypothesis**: GPU-044 failed because noise on χ was absorbed by
Channel D rigidity. GPU-046 v9-P failed because χ homogenizes spatially.
v9-E adds noise to the OPERATOR (edge weights in discrete Laplacian)
instead. This noise propagates through every use of Laplacian — σ_g,
σ_m, χ, and φ all feel the fluctuating metric.

**Prediction** (DER-QNG-058 §Alternative path):
```
d²σ_g/dt² = β·Δ_noisy σ_g,   where Δ_noisy = Δ_std + σ_edge·η(t)·Δ'
```

Edge-noise bypasses Channel D rigidity by entering through all channels
simultaneously. Can close FDT with smaller σ_edge than GPU-044 needed
on χ alone.

## Algorithm

Replace standard Laplacian `nb_mean(sg, nb_idx)` with:
```python
sg_bar = (1/deg) * sum_j (1 + sigma_edge * eta_ij(t)) * (sg_j - sg_i)
```

where `eta_ij(t)` is i.i.d. white Gaussian noise per edge per step.

This affects ALL channels simultaneously (A, B, D, F, G) that use
the neighbor-mean operator.

## Protocol

γ-scan at R=4, L=20 with edge noise:
- σ_edge ∈ {0.0 (control), 0.05, 0.10, 0.20}
- γ ∈ {0.010, 0.020, 0.040}
- T_meas = 1000 lu (same as GPU-043 for comparison)

## Gates

### `V9E_PASS`
- CV(hbar_cand across γ) < 2% at fixed σ_edge
- AND CV(hbar_cand across σ_edge) at fixed γ monotonic (sanity)
→ Edge-noise mechanism works. Proceed to v9-G full implementation.

### `V9E_MARGINAL`
- CV in [2%, 10%]
→ Partial closure. May need colored edge noise or larger σ_edge.

### `V9E_FAIL`
- CV > 10%
→ Edge-only noise also fails. v9-G full graphity required or V9-C
  obligatory.

## Runtime

4 σ_edge × 3 γ = 12 runs × ~20 min = ~4 hours.

Option: σ_edge={0.0, 0.10} × γ={0.010, 0.020, 0.040} = 6 runs = 2 hours
(primary test only).

## Risk

σ_edge too large may destroy ring attractor. Stability check first at
σ_edge=0.20 with γ=0.020.
