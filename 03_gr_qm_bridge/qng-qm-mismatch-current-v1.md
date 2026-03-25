# QNG QM Mismatch-Gradient Current v1

Type: `derivation`
ID: `DER-BRIDGE-027`
Status: `proxy-supported` (informative negative: multi-channel structure identified)
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-026` (history-phase current — current form ruled out)

## Objective

Test whether replacing the phase-difference current `J_phi = C_i·C_j·sin(Δφ)`
with a mismatch-gradient current `J_mis = C_i·C_j·(mismatch_j - mismatch_i)`
gives a significantly better calibrated continuity balance.

## Background

QNG-CPU-044 identified the root bottleneck for R²_calib:

- phi is near-perfectly synchronized (sync_order > 0.94 universally)
- Therefore sin(phi_j - phi_i) ≈ 0 for most neighbor pairs
- Small current → weak R² regardless of amplitude or phase variable choice
- Three diagnoses ruled out: amplitude form, scale calibration, phase variable
- **Root bottleneck: the current functional form J = C_i·C_j·sin(Δφ)**

Why `mismatch` is a better current candidate:

1. **Direct path into C_eff**: `C_eff = 0.45·sigma + 0.35·(1−mismatch) + 0.20·(1+cos(phase))/2`
   So `ΔC_eff ≈ −0.35·Δmismatch` (mismatch contributes directly and linearly)
   → mismatch gradient directly predicts ΔC_eff without angle approximation

2. **Not synchronized**: `mismatch` = exp. mov. avg. of |sigma_new − sigma_neigh|
   Values live in [0,1], have genuine cross-node variation, NOT near-constant
   → mismatch differences are large → stronger current signal

3. **Physical role**: mismatch measures local sigma disagreement → high-mismatch nodes
   are "excited" relative to neighbors → natural source of probability flux

4. **Comparison with mem**: `mem` = exp. mov. avg. of |chi_new − chi_neigh|
   Also in [0,1], also has genuine cross-node variation
   → test both as phase-space current drivers

## Construction

### Mismatch-gradient current

```
J_mis_{i→j} = C_eff_i · C_eff_j · (mismatch_j − mismatch_i)
```

Anti-symmetric: `J_mis_{i→j} = -J_mis_{j→i}` ✓ (conserved flux)

### Mismatch div current

```
div(J_mis)_i = C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · (mismatch_j − mismatch_i)
```

### Memory-gradient current (comparison)

```
J_mem_{i→j} = C_eff_i · C_eff_j · (mem_j − mem_i)
div(J_mem)_i = C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · (mem_j − mem_i)
```

### Calibrated coupling (same OLS estimator)

```
α*_X = −Σ(Δρ · div(J_X)) / Σ(div(J_X)²)
R²_X = 1 − Var(Δρ + α*_X · div(J_X)) / Var(Δρ)   where ρ = C_eff²
```

### Key scale prediction

Since mismatch ∈ [0,1] and differences are O(0.1−0.3):
- `|J_mis| ~ C_eff² · |Δmismatch| ~ 0.75 · 0.2 ~ 0.15`
- `|Δρ| = |Δ(C_eff²)| ~ 2·C_eff·|ΔC_eff| ~ 2·0.87·0.002 ~ 0.003`
- Predicted scale ratio: 0.15/0.003 ~ 50x (still large but much better than 100x from phi)
- If ΔC_eff is driven by Δmismatch, calibrated α* absorbs the scale → R² improvement

## Claims

### Claim A: R²_mis > R²_std on ≥4/5 seeds

Prediction: OPEN

Argument: Mismatch has a direct linear path into C_eff (−0.35 weight).
If mismatch gradients drive density changes, the current should be much better
correlated with Δρ than the phase current (which is near-zero universally).

### Claim B: max R²_mis > 0.57 (beats seed-137 benchmark)

Prediction: OPEN

Argument: If mismatch gradient is the correct current driver, seed 137
(which had best R²_std=0.572) should improve.

### Claim C: mean R²_mis > 0.40

Prediction: OPEN

Argument: A direct linear path from mismatch to C_eff should give substantially
better than the 0.20 mean from phase-based currents.

### Claim D: cv(|α*_mis|) < cv(|α*_std|)

Prediction: OPEN

Argument: If the mismatch channel is the correct physical driver, coupling
universality should improve (less topology-dependent).

## Physical interpretation

If R²_mis >> R²_std universally:
- The QNG probability current is not a U(1) phase current
- It is a **mismatch-gradient diffusion current**: density flows from high-mismatch
  to low-mismatch regions
- The correct QNG continuity equation is:
  `∂_t(C_eff²) + α* · div(C_eff_i · C_eff_j · Δmismatch_{ij}) = 0`
- This is a non-linear diffusion law on the graph, NOT a Schrödinger-like U(1) flow
- Physical meaning: excitation (sigma mismatch) drives probability flux

If R²_mis ≈ R²_std:
- The bottleneck is not the current variable but something structural
  (e.g., the continuity framework itself, or the need for multi-step gradients)

## Validation

Test: `QNG-CPU-045` — `qng_mismatch_current_reference.py`
Decision: FAIL (0/4 predictions — informative negative: multi-channel structure identified)

Results:
- P1: R²_mis > R²_std on ≥4/5 seeds — FAIL (2/5)
- P2: mean R²_mis > 0.40 — FAIL (mean=0.1197)
- P3: max R²_mis > 0.57 — FAIL (max=0.3538)
- P4: R²_mis > R²_mem on ≥3/5 — FAIL (2/5)

Key findings:
- Scale ratio: mismatch gives 6-12x vs phi's 100-120x — scale problem SOLVED
  but R² still poor because DIRECTION of correlation is topology-dependent
- Topology-selective channels: seed 42 → mismatch (0.354); seed 137 → phi (0.572);
  seed 1729 → mem (0.101) — no universal single-channel winner
- Implication: QNG probability current is MULTI-CHANNEL; each topology activates
  a different dominant driver; joint regression needed
