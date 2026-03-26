# QNG Sigma Identification

- test_id: `QNG-CPU-039`
- decision: `pass`
- verdict: `sigma = C_eff FALSIFIED; sigma ∝ C_eff SUPPORTED (universal); sigma couples to BOTH C_eff and L_eff; C_eff-vs-L_eff primacy is topology-dependent (tier-2); R²(C_eff+L_eff) > 0.71 universally`

## corr(sigma, C_eff) per seed
  seed 20260325: `0.9537`
  seed 42: `0.8700`
  seed 137: `0.9047`
  seed 1729: `0.7067`
  seed 2718: `0.9440`
  min: `0.7067` (> 0.5 required)

## corr(sigma, L_eff) per seed
  seed 20260325: `0.4379`
  seed 42: `0.6455`
  seed 137: `0.8214`
  seed 1729: `0.7308`
  seed 2718: `0.4814`
  max: `0.8214`

## R² sigma ~ C_eff only per seed
  seed 20260325: `0.9096`
  seed 42: `0.7568`
  seed 137: `0.8184`
  seed 1729: `0.4995`
  seed 2718: `0.8912`

## R² sigma ~ C_eff + L_eff per seed
  seed 20260325: `0.9865`
  seed 42: `0.8562`
  seed 137: `0.9284`
  seed 1729: `0.7134`
  seed 2718: `0.9452`

## C_eff primary over L_eff?
  seed 20260325: `True`  (corr_C=0.9537, corr_L=0.4379)
  seed 42: `True`  (corr_C=0.8700, corr_L=0.6455)
  seed 137: `True`  (corr_C=0.9047, corr_L=0.8214)
  seed 1729: `False`  (corr_C=0.7067, corr_L=0.7308)
  seed 2718: `True`  (corr_C=0.9440, corr_L=0.4814)
