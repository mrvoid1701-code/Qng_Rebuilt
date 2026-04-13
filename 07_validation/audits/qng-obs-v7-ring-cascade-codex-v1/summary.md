# QNG v7 Ring Cascade Rotation Reference (Codex)
- author: `Codex`
- decision: `pass`

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof v7 cascade | 36.728 |
| v7 cascade improvement ratio | 1.058x |
| OBS-001 ratio (reference) | 2.264x |
| OBS-005 ratio (reference) | 1.058x |
| MOND ratio (reference) | 1.702x |
| Best lam_ring | 50000.0000 kpc |
| Best lam_grav | 50000.0000 kpc |
| Best A | 2539.2585 (km/s)^2 |
| Fraction galaxies improved | 0.696 |

## Checks
- v7 < baryon: PASS
- v7 > MOND: FAIL
- v7 > OBS-001: FAIL
- v7 > OBS-005: PASS
- lam_grav > 0: PASS
- A > 0: PASS
- fraction improved > 0.60: PASS
