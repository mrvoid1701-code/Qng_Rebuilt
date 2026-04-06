# QNG-CPU-048: Ring Force Linear Reference
- decision: `pass`
- epsilon=0.005 (linear regime), Phase2=3000 steps

## Results
| Metric | Value |
|--------|-------|
| Separation (eps=0) final | 7 |
| Separation (eps=0.005) final | 12 |
| Separation diff | 5 |
| Trend | REPULSION |

## Checks
- Check 1 (ring detectable): PASS
- Check 2 (sep diff > 1): PASS (5)
- Check 3 [info] trend: REPULSION
