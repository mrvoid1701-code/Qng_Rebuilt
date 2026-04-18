# Windowed Mass Measurement (QNG-GPU-009)

SM ratio Delta/N = 1.3130

## Method
M_windowed = (dep_inner - dep_outer) * N_inner
dep_inner = mean(sigma_ref - sigma_m | r < R+4)
dep_outer = mean(sigma_ref - sigma_m | r > L/2-6)

## Results

| L | M_win(R4) | M_win(R5) | ratio_win | vs SM% | M_global(R4) |
|---|-----------|-----------|-----------|--------|-------------|
| 20 | 170.11 | 374.76 | 2.2031 | +67.79% | 509.7 |
| 30 | 69.39 | 140.32 | 2.0222 | +54.01% | 967.6 |
| 40 | 92.33 | 184.13 | 1.9943 | +51.89% | 1503.4 |
| 50 | 104.17 | 206.42 | 1.9815 | +50.92% | 2129.3 |
| 60 | 110.71 | 218.37 | 1.9724 | +50.22% | 2851.4 |
| 80 | 117.65 | 230.45 | 1.9588 | +49.19% | 4593.3 |

## Convergence: NO
Last-3 spread: 0.0227
Verdict: NOT_CONVERGED
