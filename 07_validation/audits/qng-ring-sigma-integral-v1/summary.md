# QNG-CPU-051: Ring Sigma-Depletion Integral
- decision: `fail`

## M_ring by Radius
| R | M_ring_mean | M_ring_cv | sigma_core | sigma_bulk |
|---|-------------|-----------|------------|------------|
| 2 | 36.739 | 0.3194 | 0.4648 | 0.47 |
| 4 | 132.7784 | 0.3406 | 0.4326 | 0.4453 |
| 6 | 299.821 | 0.0828 | 0.3343 | 0.3755 |

## rho_0 Constraint
- M_ring (R=4, standard): 132.7784
- Formula: `rho_0 = m_particle / (a_M * 132.7784)`
- Empirical rho_0 (from OBS-002): ~191111.0  (km/s)^2/lu

## Checks
- Check 1 (stable): FAIL
- Check 2 (positive): PASS
- Check 3 (scales with R): PASS
