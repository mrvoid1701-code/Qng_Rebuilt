# QNG-CPU-047: Ring Force Reference
- decision: `pass`
- epsilon=0 vs epsilon=0.1, Phase2=2000 steps

## Final Positions
| Scenario | z_ring1 | z_ring2 |
|----------|---------|---------|
| Two rings eps=0   | 6 | 6 |
| Two rings eps=0.1 | 3 | 3 |
| Single ring eps=0.1 | 5 | — |

- Epsilon effect on ring1: 3.0 lattice units
- Ring2 presence effect:   2.0 lattice units
- Direction: REPULSION

## Checks
- Check 1 (rings survived): PASS
- Check 2 (epsilon effect > 1): PASS (3.0)
- Check 3 (ring2 presence > 1): PASS (2.0)
- Check 4 [info] direction: REPULSION
