# QNG-CPU-035

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Step N6 — G_QNG consistency identity: G_QNG = α·λ²_screen across multiple β values

## Purpose

Verify Identity N6.1 from `DER-QNG-018`:
```
G_QNG = α · λ²_screen
```

This identity states that Newton's constant and the gravitational screening length
are not independent — they are both determined by the same substrate parameters
(β, z, α) and must satisfy this exact relation. It cross-validates the G_QNG formula
`G_QNG = β/z` and the screening length formula `λ_screen = √(β/(z·α))` simultaneously.

Running three simulations at β = 0.20, 0.35, 0.50 (fixed z=2, α=0.005) provides
three independent checks of the identity.

## Inputs

- [qng-poisson-assembly-v1.md](../../04_qng_pure/qng-poisson-assembly-v1.md)
- [qng-ceff-field-equation-v1.md](../../04_qng_pure/qng-ceff-field-equation-v1.md)
- [qng_g_qng_consistency_reference.py](../../tests/cpu/qng_g_qng_consistency_reference.py)

## Experimental design

For each β ∈ {0.20, 0.35, 0.50}:
1. Run quasi-static v3 equilibration on 64-node ring (z=2, α=0.005, δ=0.20, 3000 steps)
   with source clamped at node 0 (σ₀ = 0.05).
2. Measure equilibrium sigma profile δ_C(r) = σ(r) - σ_ref.
3. Fit exponential decay: |δ_C(r)| ~ A·exp(-r/λ_fit) over r ∈ [2, 15].
4. Compute:
   - G_QNG_formula = β/z
   - λ_pred = √(β/(z·α))
   - ratio = α·λ_fit² / G_QNG_formula

## Checks

**Check 1 — Identity holds at β=0.20:**
```
|α·λ_fit(0.20)² / G_QNG(0.20) - 1| < 0.10
```

**Check 2 — Identity holds at β=0.35:**
```
|α·λ_fit(0.35)² / G_QNG(0.35) - 1| < 0.10
```

**Check 3 — Identity holds at β=0.50:**
```
|α·λ_fit(0.50)² / G_QNG(0.50) - 1| < 0.10
```

**Check 4 — G_QNG scales linearly with β:**
```
|G_QNG(0.50)/G_QNG(0.20) - (0.50/0.20)| < 0.01
```
Algebraic identity — should pass exactly.

**Check 5 — λ² scales linearly with β:**
```
|λ_fit(0.50)²/λ_fit(0.20)² - (0.50/0.20)| < 0.15
```
From λ_pred = √(β/(z·α)): λ_pred² ∝ β. Fit values should track this within 15%.

## Decision rule

**Overall PASS** if all five checks pass.

**Interpretation of PASS:**
Identity N6.1 (`G_QNG = α·λ²_screen`) holds numerically across multiple β values.
The G_QNG formula and the screening length formula are jointly consistent with the
same substrate parameters. Step N6 of the Newtonian limit program is confirmed.

**Interpretation of FAIL:**
- Checks 1-3 fail: the exponential fit quality is poor (short ring, boundary effects)
  or the screened Poisson equation is not the correct model. Increase N or check fit range.
- Check 4 fails: coding error in G_QNG formula (should be exact).
- Check 5 fails: the sigma profile does not follow a clean Yukawa decay at this β
  (non-linear effects, or λ is comparable to ring size). Check that λ_pred << N/2.

## Artifact paths

- `07_validation/audits/qng-g-qng-consistency-reference-v1/report.json`
- `07_validation/audits/qng-g-qng-consistency-reference-v1/summary.md`
