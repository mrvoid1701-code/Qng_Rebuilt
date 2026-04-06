# QNG-OBS-005: Ring Yukawa Disk Convolution Reference
- decision: `fail`
- best-fit lambda = 50000.00 kpc
- best-fit A = 2539.26 (km/s)^2

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof ring model | 36.728 |
| Ring improvement ratio | 1.058x |
| MOND improvement ratio (OBS-003) | 1.702x |
| Fraction galaxies improved | 0.696 |
| Pearson r(A_gal, M_proxy) | 0.435 |
| Best-fit lambda | 50000.00 kpc |
| Best-fit A | 2539.26 (km/s)^2 |

## Checks
- Check 1 (ring < baryon): PASS
- Check 2 (ratio > MOND): FAIL (1.058x vs 1.702x)
- Check 3 (lambda in range): FAIL (50000.00 kpc)
- Check 4 (A_opt > 0): PASS (2539.26)
- Check 6 [info] Pearson r: PASS (0.435)
