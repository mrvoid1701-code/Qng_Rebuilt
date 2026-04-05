# QNG-CPU-036

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Step N7 — Alpha-screening: λ_screen ∝ 1/√α across five α values

## Purpose

Verify the scaling prediction from `DER-QNG-018` and `DER-QNG-020`:
```
λ_screen = √(β / (z · α))   ⟹   λ_screen ∝ α^(−1/2)
```

This tests that the cosmological identification α ↔ Λ is numerically grounded: the
substrate self-relaxation parameter α controls the screening length in the predicted
power-law manner. Confirmed here with β=0.35 fixed; α varied over two decades.

The companion identity N6.1 (QNG-CPU-035) already confirmed G_QNG = α·λ² at fixed α.
This test independently confirms the α-dependence of λ.

## Inputs

- [qng-poisson-assembly-v1.md](../../04_qng_pure/qng-poisson-assembly-v1.md)
- [qng-alpha-cosmological-v1.md](../../04_qng_pure/qng-alpha-cosmological-v1.md)
- [qng_alpha_screening_reference.py](../../tests/cpu/qng_alpha_screening_reference.py)

## Experimental design

Fixed: β=0.35, z=2, δ=0.20, N=128 ring, 5000 equilibration steps, σ_source=0.05.

For each α ∈ {0.001, 0.002, 0.005, 0.010, 0.020}:
1. Run quasi-static v3 equilibration with source clamped at node 0.
2. Measure equilibrium sigma profile δ_C(r) at each ring distance r.
3. Fit exponential decay: |δ_C(r)| ~ A·exp(−r/λ_fit) over r ∈ [3, 50].
4. Compute:
   - λ_pred = √(β/(z·α))
   - invariant_fit = λ_fit · √α
   - invariant_pred = √(β/z) = √(0.35/2) ≈ 0.4183

Prediction: invariant_fit ≈ invariant_pred for all five α values.

## Checks

**Check 1 — Invariant λ·√α is approximately constant:**
```
max(λ_fit · √α) / min(λ_fit · √α) < 1.20
```
If λ ∝ α^(−1/2), this ratio must be 1.0; tolerance 20% for finite-size/fit noise.

**Check 2 — Log-log slope of λ vs α is −0.5:**
```
|slope_loglog + 0.5| < 0.08
```
Slope from least-squares fit of log(λ_fit) on log(α) across all five points.

**Check 3 — Each λ_fit within 15% of λ_pred:**
```
|λ_fit(α) / λ_pred(α) − 1| < 0.15  for all α
```

**Check 4 — λ decreases monotonically as α increases:**
```
λ_fit(0.001) > λ_fit(0.002) > λ_fit(0.005) > λ_fit(0.010) > λ_fit(0.020)
```

**Check 5 — Fit quality R² > 0.99 for all five simulations:**
```
R²(α) > 0.99  for all α ∈ {0.001, 0.002, 0.005, 0.010, 0.020}
```

## Decision rule

**Overall PASS** if all five checks pass.

**Interpretation of PASS:**
The screening length follows λ ∝ α^(−1/2) numerically. This confirms that the
cosmological identification α_phys ≈ Λ·ℓ²_Planck (DER-QNG-020) is internally
consistent: reducing α toward its physical value increases λ toward R_Hubble,
recovering long-range Newtonian gravity. Gap 5 of the Newtonian limit program is
numerically grounded.

**Interpretation of FAIL:**
- Check 1 fails: λ·√α not constant — wrong power law or strong finite-size effects.
  Increase N and fit range, or check that λ_pred << N/2 for all α.
- Check 2 fails: slope significantly different from −0.5. Re-examine whether screened
  Poisson equation is the correct model at this parameter regime.
- Check 3 fails individually: specific α value has poor fit. Check ring size vs λ_pred.
- Check 4 fails: non-monotone λ suggests fit instability (likely small-α regime where
  λ_pred ~ N/2 causes boundary effects).
- Check 5 fails: poor exponential fit — verify equilibration is complete and source
  perturbation is small relative to σ_ref.

## Artifact paths

- `07_validation/audits/qng-alpha-screening-reference-v1/report.json`
- `07_validation/audits/qng-alpha-screening-reference-v1/summary.md`
