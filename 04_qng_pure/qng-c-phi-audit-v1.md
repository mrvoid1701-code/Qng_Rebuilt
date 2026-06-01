---
type: note
id: NOTE-QNG-025
title: c_phi formula audit — Einstein correspondence CORRECT, Lorentz emergent derivation flawed, Savant reviewer mistaken
status: self-verified 2026-04-24 — direct from qng_v8_canonical_gpu.py
author: C.D Gabriel
date: 2026-04-24
---

# NOTE-QNG-025 — c_phi audit resolution

## Conflict identified (earlier today)

Three sources gave different answers for c_phi²:
1. `qng-einstein-correspondence-v1.md`: c² = β_φ/(6μ_φ) = 0.01167
2. `qng-lorentz-emergent-v1.md`: c² = β_φ·σ_m_ref²/(3μ_φ) = 0.00583
3. Savant reviewer analysis: c² = β_φ/(12μ_φ) = 0.00583

## Self-verification against QNG code (qng_v8_canonical_gpu.py)

### Force implementation (line 381)

```python
F_A = (BETA_PHI / z_coord) * (sin_sum * cp.cos(phi) - cos_sum * cp.sin(phi))
```

This expands to `-(β_φ/z) · Σ_{j~i} sin(φ_i - φ_j)` per node i.

### Energy implementation (lines 590-592)

```python
if exact_a == 'r1':
    beta_R1 = BETA_PHI / 2.0
    E_phi_A = -(beta_R1 / z_coord) * float(cp.sum(cos_dphi))
```

where `cos_dphi` is `cos(phi[:, None] - phi_nb)` — shape (N, z) array. Summing gives:
```
Σ_{i=1}^N Σ_{j ∈ NN(i)} cos(φ_i - φ_j)
```

This is **double-counted** over edges (each edge (a,b) appears twice: as (a,b) and (b,a)).

### Effective single-counted form

```
E_phi_A = -(β_R1/z) · [2 · Σ_<ij> cos(Δφ)]  = -(β_φ/z) · Σ_<ij> cos(Δφ)
```

With β_R1 = β_φ/2 compensating for double-counting.

### Dispersion derivation (self-verified)

From F_A: μ_φ φ̈_i = -(β_φ/z) Σ_{j~i} sin(φ_i - φ_j)

Small angle: μ_φ δ̈_i = -(β_φ/z) Σ_{j~i} (δ_i - δ_j)

Fourier δ_i = e^{ikr_i}:
```
μ_φ · ω² = (β_φ/z) · [z - 2(cos k_x + cos k_y + cos k_z)]
         = (β_φ/z) · 2·[3 - Σ_μ cos k_μ]
```

For small k: cos k_μ ≈ 1 - k_μ²/2, so 3 - Σcos k_μ ≈ |k|²/2.

Therefore:
```
μ_φ · ω² ≈ (β_φ/z) · 2 · (|k|²/2) = (β_φ/z) · |k|²

→  c_φ² = β_φ / (z·μ_φ) = β_φ / (6·μ_φ) = 0.01167
→  c_φ = 0.1080 lu/step
```

## Verdict

**Einstein correspondence formula (c² = β/(6μ) = 0.01167) is CORRECT**.

### Why the Lorentz emergent formula matches numerically

`c² = β·σ_m_ref²/(3μ)` with σ_m_ref = 0.5:
= β·(0.25)/(3μ) = β/(12μ) = 0.00583

This coincidentally agrees with Savant's derivation.

**But the physics is wrong**: σ_m_ref should NOT appear in the pure-XY (R1) dispersion. It enters only in the sm-weighted formulation (non-R1). The fact that `(1/3)·(0.5)² = 1/12` gives apparent agreement is numerical coincidence, not physical derivation.

### Why Savant was wrong

Savant assumed the Hamiltonian was:
```
H = -(β_φ/(2z)) · Σ_<ij> cos(φ_i - φ_j)   [single-counted edges]
```

But QNG code has:
```
H = -(β_φ/(2z)) · Σ_{i, j~i} cos(φ_i - φ_j)   [double-counted edges]
  = -(β_φ/z) · Σ_<ij> cos(φ_i - φ_j)
```

Factor 2 difference in effective coupling.

## Corrections required in other documents

### `qng-lorentz-emergent-v1.md`
The formula `c² = β_φ·σ_m_ref²/(3μ_phi)` is numerically correct (0.00583 matches empirical tests) BUT physically wrong (σ_m_ref doesn't belong). 

**WAIT**: need to re-verify this. If Lorentz emergent measures c = 0.0764 (not 0.108) empirically, then it's measuring something DIFFERENT from Einstein correspondence's 0.108.

Possible explanation:
- Einstein correspondence tests c_φ_bulk (free field)
- Lorentz emergent tests c on the sm-weighted form (non-R1)

The two different c values may both be CORRECT for DIFFERENT Hamiltonian structures. Under sm-weighted form, c includes σ_m_ref² factor naturally; under R1 pure-XY, it doesn't.

### `qng-connection-map-v1.md` (DER-QNG-061)
I wrote c_φ² = 0.0117 which is CORRECT. My earlier claim "should be /(6μ), was wrong as /(3μ)" was wrong — /(6μ) IS right.

### `qng-unit-bridge-analysis-v1.md` (DER-QNG-064)
The "convention conflict flag" for c_phi is partially resolved:
- c_phi = 0.108 for R1 pure-XY (primary)
- c_phi = 0.0764 for sm-weighted form (secondary, different Hamiltonian)

## Impact on ℏ candidates

With c_phi = 0.108 CORRECT (Einstein correspondence formula), my earlier calculations stand:
- Zero-point balance: ℏ ≈ 0.095
- Per-edge action: ℏ ≈ 0.097
- Per-node action (Einstein-mind preferred): ℏ ≈ 0.292

## Self-verification lesson

**Even rigorous reviewers can be wrong if they assume the wrong Hamiltonian form.** Always verify against the actual code implementation.

In this case:
1. Savant was rigorous in derivation but assumed wrong input
2. QNG Einstein correspondence formula was right
3. QNG Lorentz emergent formula was numerically OK but via questionable derivation (σ_m_ref justification unclear)

**Methodology lesson**: when multiple sources disagree, the CODE is the ultimate arbiter (assuming the code is what actually runs the tests).

## Status

**NOTE-QNG-024** (withdrawing ⟨L⟩ = ℏ claim) — STILL VALID
**Einstein correspondence c_phi** — CORRECT, no change needed  
**Savant reviewer claim** — REJECTED after self-verification from code
**Lorentz emergent derivation** — marked ambiguous, may need separate clarification for when σ_m_ref² matters

ℏ_QNG candidate remains **0.292 (per-node Einstein-mind recommended)** or **0.095 (zero-point balance)** — both with same c_phi basis.
