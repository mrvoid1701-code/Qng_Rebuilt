# Phi Xi Scan vs GAMMA_PHI (QNG-GPU-013)

L=60, R=5, lambda_screen=8.37

| gamma_phi | xi (lu) | xi_pred (1/sqrt) | alpha | R2_exp | R2_pow | better |
|-----------|---------|-----------------|-------|--------|--------|--------|
| 0.03 | 5.998 | 10.97 | 2.365 | 0.9855 | 0.999 | ambiguous |
| 0.05 | 6.003 | 8.50 | 2.367 | 0.9857 | 0.9991 | ambiguous |
| 0.1 | 6.007 | 6.01 | 2.371 | 0.9861 | 0.9993 | ambiguous |
| 0.2 | 5.999 | 4.25 | 2.379 | 0.9863 | 0.9994 | ambiguous |

## Verdict: MASSLESS_PHI

xi approximately constant (slope=0.00) -> phi gapless, L=20 is coincidence
