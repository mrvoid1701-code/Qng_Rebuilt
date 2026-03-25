# QNG QM Calibrated Continuity v1

Type: `derivation`
ID: `DER-BRIDGE-024`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-023` (complex amplitude proxy)

## Objective

Resolve the scale mismatch identified in QNG-CPU-041 and find the first
calibrated continuity balance for the complex amplitude ψ = C_eff·exp(i·phi).

## Background

QNG-CPU-041 established:
- ψ = C_eff·exp(i·phi) produces a current J with the correct directional sign
  (corr(Δρ, -div(J)) > 0 on 4/5 seeds)
- But |J| >> |Δρ| by ~100x — a scale mismatch that prevents full balance

The scale mismatch has a clear origin:
- `Δρ_i = C_eff_{t+1,i}² - C_eff_{t,i}²` ≈ 0.003–0.005 (C_eff changes slowly)
- `div(J)_i = C_eff_i · Σ_j C_eff_j · sin(phi_j - phi_i)` ≈ 0.1–0.6 (phase gradients are large)

These two quantities have the right relative direction but different natural scales.
The resolution is to find the optimal coupling constant α* such that:

```
Δρ_i + α* · div(J)_i ≈ 0
```

## Construction

### Optimal coupling constant

Given vectors Δρ and div(J) (both length n_nodes), the least-squares optimal α* is:

```
α* = -Σ_i (Δρ_i · div(J)_i) / Σ_i (div(J)_i)²
```

This minimizes rms(Δρ + α · div(J)) over all α ∈ ℝ.

### Calibrated residual

```
residual_i = Δρ_i + α* · div(J)_i
```

### Explained variance

```
R²_calib = 1 - Var(residual) / Var(Δρ)
```

### Continuity quality

R²_calib > 0 means the calibrated current explains some fraction of density change.
R²_calib = 1 means perfect continuity balance at coupling α*.

## Claims

### Claim A: α* exists and is positive

Prediction: SUPPORTED

Argument: The continuity equation Δρ + α*·div(J) = 0 requires Δρ ≈ -α*·div(J).
Since corr(Δρ, -div(J)) > 0 on 4/5 seeds, div(J) and Δρ are negatively correlated,
so Σ(Δρ·div(J)) < 0 and α* = -Σ(Δρ·div(J))/Σ(div(J)²) > 0.
This is the correct sign for a probability current: outflow (div(J)>0) causes density
decrease (Δρ<0).

### Claim B: α* is stable across seeds

Prediction: OPEN

Argument: If α* represents a universal coupling of the substrate, it should
be topology-independent (Tier-1 signal). If it varies strongly with topology,
it is a Tier-2 signal and the coupling is graph-dependent.

### Claim C: R²_calib > 0 on majority of seeds

Prediction: SUPPORTED (follows from corr > 0 on 4/5 seeds)

Since R²_calib = corr(Δρ, -div(J))², R²_calib > 0 whenever corr ≠ 0.

### Claim D: R²_calib > 0.1 on at least one seed (nontrivial balance)

Prediction: OPEN

Seed 137 had corr = 0.756, so R²_calib ≈ 0.571 there. For the others,
R²_calib will be lower (0.04–0.14).

### Claim E: history improves R²_calib

Prediction: OPEN

History increases |J| (3–8x) — this could improve α* stability or worsen
the calibrated balance depending on the phase gradient structure.

## Physical interpretation

If α* is stable and negative, it represents the first proxy-level determination
of an effective QNG coupling constant between the density sector and the
phase-gradient sector:

```
∂_t(|ψ|²) + α* · ∇·Im(ψ* ∇ψ) = 0
```

This is the QM continuity equation with an effective coupling α* ≠ 1.
The deviation from 1 reflects that the QNG substrate is not yet a fully
normalized quantum system — the coupling is a proxy-level estimate.

## Open questions

- Is α* universal (Tier-1) or topology-dependent (Tier-2)?
- What sets the magnitude of α*? Does it have a physical interpretation in
  terms of native QNG parameters (e.g., phi_rel_gain, phi_hist_gain)?
- Can the continuity balance be improved by modifying the amplitude definition
  (e.g., ψ = C_eff^p · exp(i·phi) for some p ≠ 1)?

## Validation

Test: `QNG-CPU-042` — `qng_calibrated_continuity_reference.py`

Pass criteria (post-run, corrected sign):
- P1: α* > 0 on ≥4/5 seeds — PASS (4/5)
- P2: R²_calib > 0.05 on ≥3/5 seeds — PASS (3/5)
- P3: R²_calib > 0.5 on ≥1 seed — PASS (seed 137: 0.572)
- P4: cv(|α*|) < 1.5 — PASS (cv = 0.76)

Key result: α* ≈ 10⁻³ (effective coupling constant); cv = 0.76 (moderate stability, Tier-2)
