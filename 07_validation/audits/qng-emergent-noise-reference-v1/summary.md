# QNG Emergent Noise Reference v1

- decision: `pass`

## Ring FDT formula
- eta_ring = sqrt(2 * 0.005 * sqrt(0.005 * (0.005 + 2*0.35)))
- eta_ring = 0.024366
- Var_pred = alpha = 0.005
- Ring FDT identity: eta^2 / (2*sqrt(alpha*(alpha+2*beta))) = 0.00500000

## Measured variances

| run | eta | Var_meas | ratio vs expected | check |
|-----|-----|----------|-------------------|-------|
| eta=0         | 0.000000 | 0.00e+00 | < 5e-6 gate | PASS |
| eta=eta_ring  | 0.024366 | 0.004797 | 0.9595 vs 1.0 (alpha=0.005) | PASS |
| eta=2*eta_ring| 0.048733 | 0.020458 | 1.0229 vs 1.0 (4*alpha=0.0200) | PASS |

## Summary checks
- Check 1 (det Var < 5e-6): 0.00e+00  PASS
- Check 2 (ring FDT within 30%): ratio=0.9595  PASS
- Check 3 (eta^2 scaling within 30%): ratio=1.0229  PASS
- Check 4 (algebraic identity): lhs=0.00500000  PASS

## Interpretation
PASS: equilibrium sigma variance on 1D ring matches ring FDT prediction. eta = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta))) is the derived noise amplitude. Noise is emergent from relaxation and relational coupling — not a free parameter.
