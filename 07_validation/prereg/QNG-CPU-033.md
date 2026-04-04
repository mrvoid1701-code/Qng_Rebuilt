# QNG-CPU-033

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `QM_facing`

## Title

P1 confirmation: chi-to-phi coupling in v4 — frequency shift proportional to ⟨χ⟩

## Purpose

Test Prediction P1 from `qng-chi-ontology-v1.md` (NOTE-QNG-009) using the v4 update
law (`DER-QNG-016`), which adds Channel E: `ε·χ_i` in the phi channel.

QNG-CPU-032 established that v3 is a null result for P1 by construction (no chi→phi
term). v4 introduces Channel E and this test verifies that:

1. With Channel E active (`ε > 0`, `δ > 0`): phi accumulates angular drift at rate
   proportional to `ε·⟨χ⟩_B`.
2. With Channel E active but chi background zero (`ε > 0`, `δ = 0`): no drift.
3. The drift ratio `ω_B / (ε·⟨χ⟩_B)` lies within 50% of 1.0 (linear scaling confirmed).
4. Sigma equilibrium is unchanged (Channel E adds no chi→sigma coupling).

## Inputs

- [qng-native-update-law-v4.md](../../04_qng_pure/qng-native-update-law-v4.md)
- [qng-chi-ontology-v1.md](../../04_qng_pure/qng-chi-ontology-v1.md)
- [qng_p1_v4_reference.py](../../tests/cpu/qng_p1_v4_reference.py)

## Experimental design

1. Build a 64-node ring (z=2), same parameters as QNG-CPU-030/032.
2. Run v3 equilibration (3000 steps) under two delta conditions to establish chi backgrounds:
   - **Condition A**: δ=0.00 → ⟨χ⟩_A ≈ 0
   - **Condition B**: δ=0.20 → ⟨χ⟩_B ≈ 3.34
3. Freeze sigma and chi backgrounds from equilibration.
4. Reset phi to a common random perturbation (same seed for both conditions).
5. Run phi relaxation for 500 steps using the **v4 phi step** with `ε = 0.02`:
   ```
   phi_new = wrap(phi_i + phi_rel * angle_diff(phi_bar_i, phi_i) + epsilon * chi_i)
   ```
   Sigma and chi are held frozen (not updated).
6. Measure mean angular drift rate per step from total phase accumulation.

## Checks

**Check 1 — Drift detected in Condition B:**
```
omega_B > 0.5 * epsilon * chi_mean_B
```
Phi drifts at least half the predicted rate. Upper tolerance: `omega_B < 2.0 * epsilon * chi_mean_B`.

**Check 2 — Null drift in Condition A:**
```
|omega_A| < 0.01
```
No detectable drift when chi background is zero.

**Check 3 — Drift ratio confirms linear scaling:**
```
omega_B / (epsilon * chi_mean_B) in [0.5, 2.0]
```
The measured drift is within a factor of 2 of the linear P1.1 prediction.

**Check 4 — Sigma spatial power unchanged (null):**
```
|P_sigma_B / P_sigma_A - 1| < 0.01
```
Channel E adds nothing to sigma. Identical to Check 3 of QNG-CPU-032.

## Decision rule

**Overall PASS** if all four checks pass.

**Interpretation of PASS:**
P1 is confirmed in v4. Chi tension drives phase accumulation at rate ε·⟨χ⟩ as predicted.
Channel E is the QM-facing coupling that connects the gravitational (sigma/chi) sector
to the quantum-phase (phi) sector.

**Interpretation of FAIL:**
- Check 1 fails: Channel E is not propagating — inspect phi step implementation.
- Check 2 fails: Spurious drift in A — inspect chi initialization (should be zero).
- Check 3 fails: Drift is non-linear in chi — the linear approximation breaks down at
  delta=0.20. Try smaller epsilon or smaller delta.
- Check 4 fails: Unexpected chi→sigma path — inspect v4 law (should be impossible by construction).

## Artifact paths

- `07_validation/audits/qng-p1-v4-reference-v1/report.json`
- `07_validation/audits/qng-p1-v4-reference-v1/summary.md`
