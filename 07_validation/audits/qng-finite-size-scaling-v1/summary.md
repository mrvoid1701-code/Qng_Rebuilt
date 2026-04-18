# Finite-Size Scaling of Ring Mass (QNG-GPU-006)

Screening length lambda = 8.37 lu  (saturation expected at L >> 25 lu)

## Scan Results

| L | M(R=4) | M(R=5) | ratio | M4 vs CPU-074 | ratio vs CPU-074 |
|---|--------|--------|-------|---------------|-----------------|
| 20 | 509.66 | 810.13 | 1.5895 | -30.1% | +21.34% |
| 30 | 967.61 | 1301.10 | 1.3447 | +32.8% | +2.65% |
| 40 | 1503.42 | 1861.34 | 1.2381 | +106.2% | -5.49% |
| 50 | 2129.30 | 2508.68 | 1.1782 | +192.1% | -10.06% |
| 60 | 2851.36 | 3250.66 | 1.1400 | +291.2% | -12.97% |

## Convergence: NOT_CONVERGED

Ratio still drifting: 1.2381 -> 1.1400. Need larger L.

CPU-074 reference ratio: 1.3100 (L=20)
