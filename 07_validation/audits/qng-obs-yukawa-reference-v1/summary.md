# QNG-OBS-004: Yukawa Radial Profile Reference
- decision: `fail`
- best-fit lambda = 10000.00 kpc
- best-fit A = 376.98 (km/s)^2

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof Yukawa | 38.164 |
| Yukawa improvement ratio | 1.018x |
| MOND improvement ratio (OBS-003) | 1.702x |
| Fraction galaxies improved | 0.637 |
| Best-fit lambda | 10000.00 kpc |
| Best-fit A | 376.98 (km/s)^2 |

## Checks
- Check 1 (Yukawa < baryon): PASS
- Check 2 (ratio > MOND): FAIL (1.018x vs 1.702x)
- Check 3 (lambda in galactic range): FAIL (10000.00 kpc)
- Check 4 (A_opt > 0): PASS (376.98)
- Check 5 [info] AIC: FAIL
