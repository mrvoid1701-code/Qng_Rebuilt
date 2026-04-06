# QNG-OBS-002: Global Fixed a_M Reference
- decision: `fail`
- a_M fixed = 0.225 (from QNG-CPU-043, zero free parameters)

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof QNG global  | 38.867 |
| Improvement ratio           | 1.000x |
| Fraction improved           | 0.725 |
| Median residual bias        | 0.152 |

## Checks
- Check 1 (QNG < baryon): PASS
- Check 2 (ratio >= 1.5x): FAIL (1.000x)
- Check 3 (frac > 0.50): PASS (0.725)
- Check 4 [info] (bias < 0.30): PASS (0.152)
