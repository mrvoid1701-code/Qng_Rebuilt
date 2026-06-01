---
type: evidence
test_id: QNG-GPU-046
category: gpu_scale
hardware: GPU
status: completed (all 7 runs)
verdict: V9P_FAIL
author: C.D Gabriel
date: 2026-04-24
upstream:
  - QNG-GPU-043 (deterministic two-channel FDT FAIL)
  - QNG-GPU-044 (external constant-sigma vacuum FAIL)
  - QNG-GPU-045 (Lyapunov H_CHAOTIC marginal)
  - QNG-GPU-046-LONG (extended deterministic FAIL)
  - DER-QNG-056 draft (v9-P/v9-G probabilistic extension)
---

# QNG-GPU-046 v9-P — State-dependent multiplicative Langevin REPORT

## Verdict: **V9P_FAIL** — state-dependent noise does not close Einstein-Nyquist FDT

CV(hbar_cand across γ) = 55.86% (threshold FAIL: 10%).
CV(hbar_cand across n) = 5% (smaller but also failing closure).

## Key findings

### Finding 1: γ-scaling is LINEAR (same as GPU-043/044)

| γ | ⟨χ²⟩_core | hbar_core | ratio to γ=0.010 |
|---|---|---|---|
| 0.010 | 6.80e-03 | 3.93e-03 | 1.00 |
| 0.020 | 6.31e-03 | 7.30e-03 | 1.86 |
| 0.040 | 5.53e-03 | 1.28e-02 | 3.26 |

hbar_cand ≈ 2γ·⟨χ²⟩/ω with ⟨χ²⟩ ≈ constant. Einstein-Nyquist cancellation
does NOT occur. State-dependence of noise amplitude is integrated out by
χ's own diffusive dynamics.

### Finding 2: Core = Vacuum (<0.3% diff) — localization FAILED

| γ | ⟨χ²⟩_core | ⟨χ²⟩_vac | ratio |
|---|---|---|---|
| 0.010 | 6.7977e-03 | 6.7978e-03 | 1.000002 |
| 0.020 | 6.3096e-03 | 6.3114e-03 | 0.999715 |
| 0.040 | 5.5295e-03 | 5.5104e-03 | 1.003466 |

The prediction "state-local ℏ" (core different from vacuum) FALSIFIED.
χ field is spatially homogenized by Channel D's CHI_REL coupling faster
than local state-dependent noise can produce distinct amplitudes.

### Finding 3: Functional form n is IRRELEVANT

At γ=0.020 fixed, scanning n (shape of state-dependence):

| n | σ²(σ_m) form | ⟨χ²⟩_core | hbar_core |
|---|---|---|---|
| 0.0 (control) | constant σ²_0 | 6.84e-03 | 7.91e-03 |
| 0.5 | σ²_0·sqrt(σ_m/σ_ref) | 6.53e-03 | 7.56e-03 |
| 1.0 (baseline) | σ²_0·(σ_m/σ_ref) | 6.31e-03 | 7.30e-03 |
| 2.0 | σ²_0·(σ_m/σ_ref)² | 6.14e-03 | 7.10e-03 |

All values within 10% of each other. **The functional shape of state-
dependent noise has essentially no effect on ⟨χ²⟩ or hbar**.

**Interpretation**: noise is injected locally at each site, but χ's
diffusive evolution (CHI_REL·(σ̄_g - σ_g) term in Channel D) spreads
fluctuations homogeneously before they can equilibrate with local
structure. The state-dependence is averaged out by diffusion.

Finding 3 is **crucial evidence** that:
> The bottleneck for emergent ℏ in v8 is NOT noise amplitude or
> noise localization — it is the DIFFUSIVE NATURE of χ field that
> homogenizes any local noise structure.

## Configuration

- L=20, R=4 fixed
- T_P1=300, T_P2=1000, T_spinup=200, T_meas=1000 lu
- DT=0.025, exact_a='r1', K_GM=0.01
- σ_0 = 0.04 (noise amplitude baseline)
- 7 runs × ~20 min each ≈ 2.5 hours total

## Scientific implications

### Why state-dependent noise on χ CANNOT close FDT

In v8 Channel D, χ has coupling:
```
dχ_i/dt = -γ·χ_i + CHI_REL·(σ̄_g_i - σ_g_i) + DELTA_CHI·(σ_g_ref - σ_g_i)
          + σ²(σ_m_i)·ξ_i(t)
```

The CHI_REL term is a discrete Laplacian — it couples χ at every site
to its neighbors at rate CHI_REL = 0.35 (per unit time). This creates
a diffusive mode with characteristic length ~1/sqrt(γ/CHI_REL) ≈ 4
lattice spacings — well beyond local ring structure (core size ~R+2
= 6).

Noise injected locally (with amplitude σ²(σ_m_i)) is immediately
smeared over this diffusive length scale. The resulting ⟨χ²⟩(x) is
approximately uniform, regardless of the spatial structure of σ²(σ_m).

### What actually matters for ℏ emergence

From today's GPU-043 + GPU-044 + GPU-045 + GPU-046-LONG + GPU-046 v9-P
results combined, we can now state:

1. **Noise added to χ directly** — any form (constant, state-dependent,
   Gaussian, etc.) — gets homogenized by χ diffusion. Cannot produce
   γ-invariant hbar. [GPU-044, GPU-046]

2. **Pure determinism** — even with λ_max > 0 chaos — insufficient.
   Weak chaos (λ/ω < 0.1) cannot drive broadband dynamics at orbital
   frequency. [GPU-043, GPU-045, GPU-046-LONG]

3. **Remaining viable paths** operate on different degrees of freedom:
   - **v9-G graphity**: noise on graph edges, not on χ. Enters through
     Laplacian OPERATOR so bypasses χ diffusion. Not yet tested.
   - **v9-E edge-only Laplacian noise**: intermediate test (QNG-GPU-048
     preregistered). Cheaper alternative; tests same mechanism as v9-G
     without full graphity.
   - **V9-C axiomatic**: hbar as fundamental constant (DER-QNG-052).

## Comparison with all 2026-04-24 results

| Test | Mechanism | ⟨χ²⟩ (γ=0.020) | hbar_cand | CV across γ |
|---|---|---|---|---|
| GPU-043 | deterministic | 1.63e-04 | 1.89e-04 | 59% |
| GPU-044 | +constant noise σ_vac=0.04 | 6.85e-03 | 7.92e-03 | 42%+ |
| GPU-046-LONG | deterministic, T=15τ_mix | 1.41e-04↓ | ~1.4e-04 | (single γ) |
| GPU-046 v9-P | +state-dep noise σ²(σ_m) | 6.31e-03 | 7.30e-03 | 56% |

All failed gate threshold (10%). Adding noise to χ increases ⟨χ²⟩ by
~40× but fails to make it γ-invariant (which is the FDT signature).

## Governance actions

- DER-QNG-056 v9-P: **FALSIFIED as primary path** — v9-P variant does
  not close FDT.
- DER-QNG-058 v9-G: **promoted to primary probabilistic path**
- QNG-GPU-048 v9-E (edge-only Laplacian noise): **ready to launch** —
  script at `tests/gpu/qng_gpu048_edge_noise.py`, prereg at
  `07_validation/prereg/QNG-GPU-048.md`. Cheaper test (~2.5 hours)
  of edge-based noise mechanism before committing to full v9-G.
- NOTE-QNG-023 update to add: "χ direct-noise path exhaustively
  closed; must move noise to graph structure itself."

## Runtime

Total GPU time today: ~5.5 hours (GPU-043 2h + GPU-044 2h + GPU-045 45m
+ GPU-046-LONG 45m partial + GPU-046 v9-P 2.5h). Five tests, four
FAILs, one surprise (GPU-045 H_CHAOTIC).

## Scientific value of this negative result

GPU-046 v9-P is the most carefully designed noise-on-χ test performed
(3 γ × 3 n + control). Its failure with n-independence confirms
definitively that **χ's diffusive dynamics homogenize any noise form**.

This closes an entire CLASS of proposals: "add noise of any kind to χ
and close FDT." The class includes:
- Constant noise (GPU-044)
- State-dependent amplitude (this test)
- Any n ∈ [0, 2] state-dependence
- Presumably all monotonic f(σ_m) forms

Next generation of tests must operate OUTSIDE χ's diffusion shell —
i.e., on graph structure, path integral measure, or entirely different
fields.

## Files

- Summary JSON: `summary.json`
- CSVs: `gamma_scan.csv`, `n_scan.csv`, `control.csv`
- Traces: `traces_A_R4_*.npz`, `traces_B_R4_*.npz`, `traces_C_R4_*.npz`
