# QNG G_QNG Consistency Reference v1

- decision: `pass`

## Identity N6.1: G_QNG = alpha * lambda^2_screen

| beta | G_QNG=beta/z | lambda_pred | lambda_fit | R^2  | alpha*lam^2/G | check |
|------|-------------|-------------|------------|------|---------------|-------|
| 0.20 | 0.1000 | 4.47 | 4.48 | 1.0000 | 1.0044 | PASS |
| 0.35 | 0.1750 | 5.92 | 5.93 | 1.0000 | 1.0048 | PASS |
| 0.50 | 0.2500 | 7.07 | 7.10 | 1.0000 | 1.0092 | PASS |

## Check 4: G_QNG linear in beta
- G(0.50)/G(0.20) = 2.5000  expected 2.5000  PASS

## Check 5: lambda^2 linear in beta
- lambda_fit(0.50)^2 / lambda_fit(0.20)^2 = 2.5120  expected 2.5000  PASS

## Interpretation
Identity N6.1 confirmed: G_QNG = alpha * lambda^2 holds across all beta values. G_QNG formula and screening length formula are jointly consistent.
