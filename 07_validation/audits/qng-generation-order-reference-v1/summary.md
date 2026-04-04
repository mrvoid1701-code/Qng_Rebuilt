# QNG Generation Order Cross-Coupling Reference v1

- decision: `pass`

## Check 1: v2 parity (delta=0)
- max_diff_total: `0.000e+00`  threshold < 1e-12  PASS

## Check 2: chi signal stronger with delta>0
- mean |chi| delta=0.00: `0.203036`
- mean |chi| delta=0.20: `0.534691`
- difference: `0.331655`  threshold > 0.001  PASS

## Check 3: generation order direction
- corr(sigma_deficit, chi): `0.7814`  threshold > 0.30  PASS

## Check 4: l_eff increases with delta
- mean l_eff delta=0.00: `0.084370`
- mean l_eff delta=0.20: `0.229594`  PASS

## Check 5: l_eff correlated with sigma deficit
- corr(Δchi, sigma_deficit): `0.7856`  threshold > 0.30  PASS

## Check 6: contractiveness
- alpha + beta + delta: `0.4600`  threshold < 1.0  PASS
