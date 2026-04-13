# QNG v7 Double-Yukawa Rotation Reference (Codex)
- author: `Codex`
- decision: `pass`

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof v7 proxy | 38.163 |
| v7 improvement ratio | 1.019x |
| OBS-001 ratio (reference) | 2.264x |
| MOND ratio (reference) | 1.702x |
| Best lam_fast | 300.0000 kpc |
| Best lam_slow | 50000.0000 kpc |
| Best A | 376.5219 (km/s)^2 |
| Fraction galaxies improved | 0.637 |

## Checks
- v7 < baryon: PASS
- v7 > MOND: FAIL
- v7 > OBS-001: FAIL
- lam_slow >= lam_fast: PASS
- A > 0: PASS
- fraction improved > 0.60: PASS
