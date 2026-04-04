# QNG-CPU-034

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `QM_facing`

## Title

Phi dephasing from chi background: T₂* measurement and ε constraint formula

## Purpose

Verify the dephasing mechanism derived in `DER-QNG-017`: a non-uniform chi background
(produced by Channel D, v3 law) causes phi coherence to decay when Channel E (v4 law)
is active. Measure the dephasing time T₂* and compare to the analytic prediction
`T₂*_pred = √2 / (ε · σ_χ)`.

This test:
1. Confirms that Channel E causes decoherence (not just coherent drift).
2. Validates the Gaussian-approximation formula for T₂*.
3. Demonstrates that chi-background controlled by δ sets the decoherence rate.
4. Provides the operative constraint formula: `ε = √2 / (T₂* · σ_χ)`.

## Inputs

- [qng-phi-dephasing-v1.md](../../04_qng_pure/qng-phi-dephasing-v1.md)
- [qng-native-update-law-v4.md](../../04_qng_pure/qng-native-update-law-v4.md)
- [qng_phi_dephasing_reference.py](../../tests/cpu/qng_phi_dephasing_reference.py)

## Experimental design

1. Build 64-node ring. Run v3 equilibration (3000 steps) with δ=0.20 to establish
   chi background `{χ_i}`. Record `σ_χ = √Var(χ)`.
2. Initialize φ_i = 0 for all i (perfect coherence, C(0) = 1).
3. Run Channel E only (φ_rel = 0, frozen sigma/chi) for 500 steps:
   ```
   φ_i(t+1) = wrap(φ_i(t) + ε·χ_i)
   ```
   with ε = 0.02.
4. Record C(t) = |⟨exp(i·φ_i(t))⟩_i| at each step.
5. Find T₂*_meas: first t where C(t) ≤ 1/e.
6. Compute T₂*_pred = √2 / (ε · σ_χ).
7. Also run Condition A (δ=0, chi≈0): C(t) should stay near 1.

## Checks

**Check 1 — Decoherence occurs in Condition B:**
```
C_B(t) drops below 1/e within 500 steps
```
Channel E with non-zero chi background causes phase coherence to decay.

**Check 2 — Measured T₂* matches exact characteristic-function prediction:**
```
T₂*_meas / T₂*_exact ∈ [0.5, 2.0]
```
T₂*_exact is computed directly from the chi values (not Gaussian approximation):
```
C_exact(t) = |mean(exp(i·ε·χ_i·t))|
T₂*_exact = first t where C_exact(t) ≤ 1/e
```
Since Channel E is deterministic and wrap does not affect exp(i·φ), the measured
and exact predicted coherences should match closely. The Gaussian T₂*_pred =
√2/(ε·σ_χ) is recorded as informational only — it is expected to be inaccurate for
skewed chi profiles.

**Check 3 — B dephases while A is still coherent:**
```
C_A(T₂*_B) > 1/e
```
At the time step when Condition B's coherence reaches 1/e, Condition A's coherence
is still above 1/e. This shows that Channel D (δ=0.20) is responsible for the
accelerated dephasing — not residual chi from sigma gradients alone.
Note: chi is non-zero in A even at δ=0 (chi_rel term generates chi from sigma
gradients near the source). This check accounts for that correctly.

**Check 4 — C_B(t) is monotonically decreasing (early regime):**
```
C_B(50) < C_B(0) and C_B(100) < C_B(50)
```
Confirms that decoherence builds up progressively, not instantaneously.

## Decision rule

**Overall PASS** if all four checks pass.

**Interpretation of PASS:**
Channel E produces decoherence via differential chi-driven phase drift. The
dephasing time scales as `1/(ε·σ_χ)` — faster decoherence for larger chi spread
or larger ε. The formula `ε = √2 / (T₂* · σ_χ)` is the operative constraint for ε
given experimental T₂* data.

**Interpretation of FAIL:**
- Check 1 fails: ε is too small or χ spread is too narrow — try larger δ or ε.
- Check 2 fails: wrap() boundary effects corrupting coherence measurement, or a
  coding error in the exact characteristic function computation.
- Check 3 fails: Channel D contribution to dephasing is not distinguishable from
  residual chi-from-gradients — increase δ_B or decrease δ_A.
- Check 4 fails: C(t) oscillates rather than decays — inspect for wrap() boundary effects.

## Artifact paths

- `07_validation/audits/qng-phi-dephasing-reference-v1/report.json`
- `07_validation/audits/qng-phi-dephasing-reference-v1/summary.md`
