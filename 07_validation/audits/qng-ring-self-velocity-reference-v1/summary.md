# QNG Ring Self-Velocity Reference v1
- decision: `fail`

## Results
| R | v_QNG | v_theory | k_v | dz |
|---|-------|----------|-----|----|
| 3 | 0.02200 | 0.15534 | 0.142 | 11.0 |
| 4 | 0.02200 | 0.12795 | 0.172 | 11.0 |
| 5 | 0.02200 | 0.10946 | 0.201 | 11.0 |
| 6 | 0.02200 | 0.09606 | 0.229 | 11.0 |
| 7 | 0.02200 | 0.08584 | 0.256 | 11.0 |

- Ratio v(R=3)/v(R=7): 1.000  (theory: 1.810)

## Checks
- Check 1 (dz >= 1): PASS
- Check 2 (v decreases): FAIL
- Check 3 (ratio > 1.3): FAIL
- Check 4 (v(R=5) range): PASS
- Check 5 (monotone): PASS
