# QNG Quasi-Static 3D Light Reference v1

- decision: `pass`

## Geometry
- 6×6×6 cubic lattice (PBC), N=216 nodes, z=6

## Screening length
- λ_pred_3D = sqrt(β/(z·α)) = `3.4157` node spacings
- λ_pred_1D = sqrt(β/(2·α)) = `5.9161` node spacings
- λ_obs_3D  =               `3.1105`
- ratio obs/pred: `0.9107`  (error: 0.0893, threshold < 0.30)  PASS
- R² fit: `0.8752`  threshold > 0.75  PASS

## G_QNG scaling with z (key formula prediction)
- G_QNG_3D = β/z_3D = `0.058333`
- G_QNG_1D = β/z_1D = `0.175000`
- ratio obs: `0.333333`  pred: `0.333333`  error: `0.000000`  PASS

## Check 1: sigma decays from source
  PASS  (monotone=True, source_depleted=True)

## Check 5: generation order in 3D
- corr(σ_deficit, χ): `0.9443`  threshold > 0.60  PASS

## Check 6: Poisson residual (bulk nodes r≥2)
- mean |β·(σ̄-σ) - α·(σ-σ_ref)|: `0.000000`  threshold < 0.01  PASS

## Radial profile sample
  r=r0.000: σ=0.0500  χ=37.4828  δσ=-0.4500  n=1
  r=r1.000: σ=0.3283  χ=6.6941  δσ=-0.1717  n=6
  r=r1.414: σ=0.3779  χ=4.7618  δσ=-0.1221  n=12
  r=r1.732: σ=0.3956  χ=4.0715  δσ=-0.1044  n=8
  r=r2.000: σ=0.3938  χ=4.1417  δσ=-0.1062  n=6
  r=r2.236: σ=0.4045  χ=3.7241  δσ=-0.0955  n=24
  r=r2.450: σ=0.4103  χ=3.4974  δσ=-0.0897  n=24
  r=r2.828: σ=0.4144  χ=3.3363  δσ=-0.0856  n=12
  r=r3.000: σ=0.4160  χ=3.2733  δσ=-0.0839  n=27
  r=r3.162: σ=0.4121  χ=3.4289  δσ=-0.0879  n=12
  r=r3.317: σ=0.4153  χ=3.3036  δσ=-0.0847  n=12
  r=r3.464: σ=0.4211  χ=3.0771  δσ=-0.0789  n=8
