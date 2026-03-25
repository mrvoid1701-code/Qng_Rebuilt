# QNG QM Madelung Amplitude v1

Type: `derivation`
ID: `DER-BRIDGE-025`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-024` (calibrated continuity)

## Objective

Test whether the Madelung representation of the QNG amplitude —
`ψ_M = sqrt(C_eff) · exp(i·phi)` with density `ρ_M = C_eff` — gives a
better-calibrated continuity balance than the standard form
`ψ = C_eff · exp(i·phi)` with `ρ = C_eff²`.

## Background

QNG-CPU-042 found:
- Standard amplitude ψ = C_eff·exp(i·phi): α*≈10⁻³, R²_max=0.572
- Scale mismatch persists: |J_std| >> |Δ(C_eff²)| by ~100x

The scale mismatch has two components:
1. `ρ = C_eff²` changes slowly because C_eff is near-constant
2. `J_std = C_eff_i · C_eff_j · sin(phi_j - phi_i)` is large

In the Madelung representation:
- `ρ_M = C_eff` — direct density (changes faster than C_eff²)
- `J_M_{i→j} = sqrt(C_eff_i · C_eff_j) · sin(phi_j - phi_i)` — geometric mean amplitude

Key comparison:
- `Δρ_M = ΔC_eff ≈ 2·C_eff·Δ(C_eff)` — roughly 2/C_eff times larger than Δ(C_eff²)
  (since C_eff ≈ 0.87, factor ≈ 2.3x larger)
- `J_M = sqrt(C_eff_i·C_eff_j)·sin(...)` ≈ sqrt(0.87)·sin(...) ≈ 0.93·J_std/C_eff ≈ J_std
  (roughly same magnitude as J_std)

Net effect: scale mismatch reduces from ~100x to ~40x. The question is whether
this also improves the directional R²_calib.

## Construction

### Madelung amplitude

```
ψ_M_i = sqrt(C_eff_i) · exp(i · phi_i)
```

### Madelung density

```
ρ_M_i = |ψ_M_i|² = C_eff_i
```

### Madelung edge current

```
J_M_{i→j} = Im(ψ_M_i* · ψ_M_j)
           = sqrt(C_eff_i) · sqrt(C_eff_j) · sin(phi_j - phi_i)
           = sqrt(C_eff_i · C_eff_j) · sin(phi_j - phi_i)
```

### Madelung div current

```
div(J_M)_i = sqrt(C_eff_i) · Σ_{j∈neighbors(i)} sqrt(C_eff_j) · sin(phi_j - phi_i)
```

### Calibrated coupling

```
α*_M = -Σ(ΔC_eff · div(J_M)) / Σ(div(J_M)²)
R²_M = 1 - Var(ΔC_eff + α*_M · div(J_M)) / Var(ΔC_eff)
```

## Claims

### Claim A: R²_M > R²_std on majority of seeds

Prediction: OPEN

Argument: The Madelung form uses a better-matched amplitude but the same
phase structure. Whether the geometric-mean current better predicts the
density change is not analytically determined.

### Claim B: α*_M > α*_std (coupling larger)

Prediction: SUPPORTED (expected)

Argument: Since ρ_M = C_eff ≈ 2x larger than ρ_std changes and J_M ≈ J_std,
α*_M ≈ |Δρ_M| / |J_M| ≈ 2x · α*_std ≈ 2x · 10⁻³.

### Claim C: cv(α*_M) < cv(α*_std) (more universal coupling)

Prediction: OPEN — Madelung form may be more natural to the substrate

### Claim D: max R²_M > 0.5 on ≥1 seed

Prediction: SUPPORTED (seed 137 had R²_std=0.572; Madelung may match or improve)

## Physical interpretation

If R²_M > R²_std universally, the natural QNG amplitude is the Madelung form:
ψ_M = sqrt(C_eff) · exp(i·phi), where C_eff plays the role of the probability
density directly (not its square). This would identify C_eff as the quantum
probability density of the native substrate — a strong QM identification.

## Validation

Test: `QNG-CPU-043` — `qng_madelung_amplitude_reference.py`
Decision: PASS

Results:
- P1: α*_M > 0 on 4/5 seeds — PASS
- P2: max R²_M = 0.580 (seed 137) > 0.5 — PASS
- P3: mean R²_M = 0.203 > mean R²_std = 0.200 — PASS (marginal +0.3%)
- P4: cv(|α*_M|) = 0.77 ≤ 0.76 — FAIL (barely, cv essentially unchanged)

Key finding: Madelung beats standard on 3/5 seeds, but the improvement is
marginal (mean +0.3%). The scale mismatch is WORSE for Madelung (200–240x)
than for standard (100x) because ΔC_eff < Δ(C_eff²) when C_eff ≈ 0.87.

Critical conclusion: The bottleneck for R²_calib is NOT the amplitude
definition (C_eff vs sqrt(C_eff)). Both forms give R²≈0.20 on average.
The bottleneck is the PHASE GRADIENT structure: how well sin(phi_j-phi_i)
correlates with density change. To improve beyond R²≈0.57, a different
approach to the phase coupling is needed.
