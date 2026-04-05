# QNG Alpha Screening Reference v1

- decision: `pass`

## Scaling: lambda_screen ∝ alpha^(−1/2)

- Predicted invariant sqrt(beta/z) = 0.4183
- Log-log slope: -0.5037  (expected -0.5)

| alpha | lambda_pred | lambda_fit | ratio | inv=lam*sqrt(a) | R^2    | C3   | C5   |
|-------|-------------|------------|-------|-----------------|--------|------|------|
| 0.001 |     13.2288 |    13.4535 | 1.0170 |          0.4254 | 0.9998 | PASS | PASS |
| 0.002 |      9.3541 |     9.4056 | 1.0055 |          0.4206 | 1.0000 | PASS | PASS |
| 0.005 |      5.9161 |     5.9256 | 1.0016 |          0.4190 | 1.0000 | PASS | PASS |
| 0.010 |      4.1833 |     4.1934 | 1.0024 |          0.4193 | 1.0000 | PASS | PASS |
| 0.020 |      2.9580 |     2.9720 | 1.0047 |          0.4203 | 1.0000 | PASS | PASS |

## Summary checks
- Check 1 (invariant constant): max/min = 1.0154 < 1.20  PASS
- Check 2 (log-log slope = -0.5): slope = -0.5037  PASS
- Check 3 (each lambda within 15%): PASS
- Check 4 (lambda monotone in alpha): PASS
- Check 5 (R^2 > 0.99 all): PASS

## Interpretation
Confirmed: lambda_screen ∝ alpha^(-1/2). The cosmological identification alpha_phys ~ Lambda * l_Planck^2 is numerically grounded. Gap 5 of the Newtonian limit program is confirmed.
