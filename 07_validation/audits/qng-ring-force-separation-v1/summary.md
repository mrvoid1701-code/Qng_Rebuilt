# QNG-CPU-050: Ring Force vs Separation
- decision: `fail`
- chirality: opposite (W+W-), epsilon=0.005

## Attraction Score by Separation
| d | score | early_mean | late_mean |
|---|-------|------------|-----------|
| 4 | -4.514 | 1.2 | 5.714 |
| 6 | -0.838 | 6.4 | 7.238 |
| 8 | 1.257 | 8.4 | 7.143 |
| 10 | 6.267 | 9.6 | 3.333 |
| 12 | 4.933 | 11.6 | 6.667 |

## Yukawa Fit
- lambda_fit: inf
- lambda_theory: 3.41
- A_fit: 0.111

## Checks
- Check 1 (rings detectable): PASS
- Check 2 (monotonic): violations=3 FAIL
- Check 3 (lambda fit): FAIL (fit=inf)
- Check 4 (reproducibility): PASS
