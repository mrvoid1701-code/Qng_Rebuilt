# QNG-CPU-046: Multi-Ring Interaction Reference
- decision: `pass`
- Two rings R=4.0 at z=6 and z=18, separation=12
- Yukawa overlap: 0.0296

## Results
| Metric | Value |
|--------|-------|
| Chi between rings | 10.33849 |
| Chi outside rings | 9.72061 |
| Max chi profile diff (two vs single) | 9.80673 |
| Sigma core ring1 (two rings) | 0.34452 |
| Sigma core ring1 (single) | 0.34829 |

## Checks
- Check 1 (rings survived): PASS
- Check 2 (chi between > outside): PASS
- Check 3 (profile diff > 0.001): PASS
- Check 4 [info] (sigma stable): PASS
