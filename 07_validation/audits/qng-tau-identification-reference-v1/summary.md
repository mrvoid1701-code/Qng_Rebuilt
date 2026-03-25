# QNG Tau Identification

- decision: `pass`
- verdict: `universal tau FALSIFIED; per-node history-driven tau SUPPORTED`

## Config timescales
  tau_p=2.857  tau_m=3.333  tau_d=4.000
  cv = `0.1690` (> 0.1 required)

## Per-node tau (default seed)
  cv_tau_node = `0.1688` (> 0.1 required)

## History amplification
  seed 20260325: hist/nohist = `3.05x`  corr(tau,mem) = `0.8328`
  seed 42: hist/nohist = `2.64x`  corr(tau,mem) = `0.6819`
  seed 137: hist/nohist = `4.24x`  corr(tau,mem) = `0.8304`
  seed 1729: hist/nohist = `4.62x`  corr(tau,mem) = `0.7151`
  seed 2718: hist/nohist = `3.90x`  corr(tau,mem) = `0.7667`

## Mean tau stability across seeds
  values: [0.107, 0.1172, 0.099, 0.0993, 0.1016]
  cv = `0.0729` (< 0.10 required)
