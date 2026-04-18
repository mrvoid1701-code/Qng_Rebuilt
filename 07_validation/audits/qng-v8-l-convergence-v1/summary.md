# v8 L-Convergence Test (QNG-GPU-011)

Channel H active in Phase 1 AND Phase 2. k_gm=0.
bp_min=0.0005  bp_ring=0.06
SM ratio Delta/N = 1.3130

## Results

| L | M(R4) | M(R5) | ratio | vs SM% | dis_bulk_P2 |
|---|-------|-------|-------|--------|-------------|
| 20 | 605.67 | 846.61 | 1.3978 | +6.46% | 0.008564 |
| 30 | 1249.57 | 1542.21 | 1.2342 | -6.00% | 0.005218 |
| 40 | 1978.64 | 2300.28 | 1.1626 | -11.46% | 0.003459 |
| 60 | 3810.84 | 4173.95 | 1.0953 | -16.58% | 0.001964 |
| 80 | 6195.34 | 6594.22 | 1.0644 | -18.94% | 0.001347 |

## Verdict: FAIL
Last-3 spread: 0.0982  (gate 0.02)
Detail: M_ring ratio does not converge (spread=0.0982)
