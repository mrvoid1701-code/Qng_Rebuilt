# QNG v7 Hopfion Rotation Reference (Codex)
- author: `Codex`
- decision: `pass`
- hopfion isotropic weight: 0.839

## Results
| Metric | Value |
|--------|-------|
| Median chi2/dof baryon-only | 38.870 |
| Median chi2/dof v7 hopfion proxy | 36.696 |
| v7 hopfion improvement ratio | 1.059x |
| OBS-001 ratio (reference) | 2.264x |
| OBS-005 ratio (reference) | 1.058x |
| MOND ratio (reference) | 1.702x |
| Best lam_ring | 50000.0000 kpc |
| Best lam_hopf | 0.1000 kpc |
| Best lam_grav | 50000.0000 kpc |
| Best A | 2577.8306 (km/s)^2 |
| Fraction galaxies improved | 0.702 |

## Checks
- hopfion < baryon: PASS
- hopfion > MOND: FAIL
- hopfion > OBS-001: FAIL
- hopfion > OBS-005: PASS
- lam_grav > 0: PASS
- A > 0: PASS
- fraction improved > 0.60: PASS
