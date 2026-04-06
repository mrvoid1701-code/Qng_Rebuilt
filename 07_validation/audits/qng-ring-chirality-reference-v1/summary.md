# QNG-CPU-049: Ring Force Chirality Comparison
- decision: `pass`
- epsilon=0.005, Phase2=3000 steps

## Results
| Metric | Value |
|--------|-------|
| Separation (eps=0) final | 7 |
| Separation (same W+W+) final | 12 |
| Separation (opposite W+W-) final | 8 |
| Chirality diff | 4 |
| Chirality finding | SENSITIVE |
| Trend (same) | REPULSION |
| Trend (opposite) | ATTRACTION |

## Checks
- Check 1 (rings detectable): PASS
- Check 2 (chirality): diff=4 → SENSITIVE
- Check 3 (Channel E active): diff=5 PASS
- Check 4 [info] same=REPULSION, opp=ATTRACTION
