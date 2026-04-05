# QNG Ring Lifetime Reference v1
- decision: `pass`
- T_lifetime: 2400 Phase-2 steps
- R_t at Phase-2 T~700 (QNG-CPU-043 ref): 5.090

## Decay curve
| Phase-2 T | z_ring | R_t | core_sigma | collapsed |
|-----------|--------|-----|------------|-----------|
| 200 | 19 | 5.291 | 0.2689 | False |
| 400 | 19 | 5.398 | 0.2624 | False |
| 600 | 19 | 5.090 | 0.2695 | False |
| 800 | 19 | 4.673 | 0.2805 | False |
| 1000 | 19 | 4.332 | 0.2932 | False |
| 1200 | 19 | 3.987 | 0.3075 | False |
| 1400 | 19 | 3.675 | 0.3242 | False |
| 1600 | 19 | 3.251 | 0.3419 | False |
| 1800 | 19 | 2.890 | 0.3611 | False |
| 2000 | 19 | 2.322 | 0.3817 | False |
| 2200 | 19 | 1.358 | 0.4017 | False |
| 2400 | 19 | 0.000 | 0.4173 | True |
| 2600 | 19 | 0.000 | 0.4295 | True |

## Checks
- Check 1 (R_t > 2.5 at T~700): PASS
- Check 2 (T_lifetime measurable): PASS
- Check 3 (T_lifetime > 1000): PASS
- Check 4 (gradual decay): PASS
