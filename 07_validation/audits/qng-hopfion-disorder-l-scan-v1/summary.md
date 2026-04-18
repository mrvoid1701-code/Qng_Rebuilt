# Hopfion Q=1 vs Ring Q=0 disorder profile L-scan (QNG-GPU-017)

v5 + Channel H, K_GM=0.0, R=5
LAMBDA_SCREEN = sqrt(BETA/ALPHA) = 8.37 lu

## Power-law exponent alpha vs L

| L | alpha(ring, q=0) | alpha(Hopfion, q=1) | R2_pow(q=1) | R2_exp(q=1) | xi(q=1) |
|---|-----------------|---------------------|-------------|-------------|--------|
| 40 | 2.5300 | 1.7742 | 0.984 | 0.971 | 6.95 |
| 60 | 2.4609 | 1.8829 | 0.996 | 0.978 | 7.89 |
| 80 | 2.3945 | 1.8896 | 0.997 | 0.973 | 8.59 |
| 100 | 2.3446 | 1.8863 | 0.997 | 0.969 | 8.95 |

## Gates

- **G1 control** |alpha(ring, L=80) - 2.37| < 0.20 : 0.0245  -> PASS
- **G2 Hopfion exponent** alpha(Hopf,L=80) = 1.8896  -> FAIL
- **G3 L-independence** spread over [60, 80, 100] = 0.0068  -> PASS
- **G4 power-law vs exponential** delta_R2 = -0.0247  -> power-law OK

## Verdict: **FAIL**

Hopfion alpha(L=80)=1.890 < 2.5, similar to ring. IR halo is universal; topology does not cure it. Option C falsified at structural level; Option B (add V(sigma_m)) is forced.
