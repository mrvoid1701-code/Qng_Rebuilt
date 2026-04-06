# QNG-CPU-053: Ring Force Clean Measurement
- decision: `fail`
- W+W-, eps=0.005, N_trials=3, Phase2=6000 steps

## Attraction Scores
| d | scores | median |
|---|--------|--------|
| 8 | [0.25, 0.25, 0.25] | 0.246 |
| 10 | [-2.36, -2.36, -2.36] | -2.358 |
| 12 | [-0.53, -0.53, -0.53] | -0.529 |

- Single-ring drift amplitude: 4.471

## Checks
- Check 1 (survive): PASS
- Check 2 (score d=10 > 0.5): FAIL (-2.358)
- Check 3 (force > drift): FAIL
- Check 4 [info] monotonic: False
