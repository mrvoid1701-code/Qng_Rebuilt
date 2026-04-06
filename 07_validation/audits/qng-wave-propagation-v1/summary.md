# QNG-CPU-052: v6 Wave Propagation Speed
- decision: `fail`
- v_pred = sqrt(beta) = 0.5916

## Speed Results
| k_back | v_measured | v_pred | rel_err | r@T50 |
|--------|------------|--------|---------|-------|
| 0.01 | 0.1688 | 0.5916 | 0.715 | 12.5 |
| 0.05 | 0.1697 | 0.5916 | 0.713 | 12.5 |
| 0.1 | 0.1329 | 0.5916 | 0.775 | 9.5 |

## Physical Units (m_node = m_proton)
- tau/a = 5.660e-10 s/m
- a = 6.133e-55 m = 0.0 l_Planck
- lambda_phys = 0.000e+00 m

## Checks
- Check 1 (propagates): PASS
- Check 2 (speed correct): FAIL
- Check 3 (k_back independent): PASS
