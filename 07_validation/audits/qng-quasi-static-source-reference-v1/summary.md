# QNG Quasi-Static Point Source Reference v1

- decision: `pass`

## Parameters
- alpha=0.005, beta=0.35, delta=0.2, n_nodes=64, steps=3000
- lambda_pred = sqrt(beta/(z*alpha)) = `5.9161` node spacings

## Check 1: sigma decays from source
- sigma(r=0)=0.0500, sigma(r=5)=0.3065, sigma(r=15)=0.4641
  PASS

## Check 2: exponential fit quality
- R² of log|δ_sigma| vs r (fit on r=[2,15]): `1.0000`  threshold > 0.80  PASS

## Check 3: screening length
- lambda_pred: `5.9161`
- lambda_obs:  `5.9302`
- ratio:       `1.0024`  (|ratio-1| = 0.0024, threshold < 0.30)  PASS

## Check 4: chi elevated near source
- mean |chi| r≤3:  `15.203544`
- mean |chi| r≥10: `0.910830`  PASS

## Check 5: generation order spatial correlation
- corr(sigma_deficit, chi): `0.9914`  threshold > 0.60  PASS

## Check 6: G_QNG formula
- G_QNG (substrate units) = `0.175000`  PASS
