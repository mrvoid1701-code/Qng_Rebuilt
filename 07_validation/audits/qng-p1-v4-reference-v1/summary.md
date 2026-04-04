# QNG P1 v4 Reference

- decision: `pass`

## Conditions
- Condition A: delta=0.0, epsilon=0.02  (Channel D off, Channel E on)
- Condition B: delta=0.2, epsilon=0.02  (Channel D on, Channel E on)

## Chi backgrounds (from v3 equilibration)
- ⟨χ⟩_A = -0.0000
- ⟨χ⟩_B = 3.3395
- Predicted omega_B = epsilon * ⟨χ⟩_B = 0.02 * 3.3395 = 0.0668 rad/step

## Check 1: Drift detected in Condition B
- omega_B = 0.066849 rad/step
- threshold > 0.5 * predicted = 0.033395
- PASS

## Check 2: Null drift in Condition A
- omega_A = 0.000118 rad/step
- threshold |omega_A| < 0.01
- PASS

## Check 3: Linear scaling confirmed
- drift_ratio = omega_B / predicted_omega_B = 1.0009
- threshold in [0.5, 2.0]
- PASS

## Check 4: Sigma spatial power unchanged (null)
- P_sigma_A = 0.3826  P_sigma_B = 0.3826
- |ratio-1| = 0.0000  threshold < 0.01
- PASS

## Interpretation
P1 confirmed in v4. Chi tension drives phase accumulation at rate epsilon*<chi> = 0.02*3.3395 = 0.0668 rad/step. Channel E is the QM-facing coupling linking the gravitational sector (sigma/chi) to the quantum-phase sector (phi).
