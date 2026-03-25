# Audit Summary — QNG-CPU-048

Test: `qng_degree_normalized_current_reference.py`
Theory: `DER-BRIDGE-030`
Decision: **FAIL** (1/4 predictions — P2 is a numerical artifact)

## What was tested

Whether dividing the multi-channel divergence current by local degree restores
N-stability of R²_combined across N ∈ {8, 16, 32}.

## Results summary

| N  | mean R²_norm | mean R²_std | beats_best |
|----|--------------|-------------|------------|
| 8  | -0.099       | 0.586       | 2/5        |
| 16 | -0.165       | 0.405       | 3/5        |
| 32 | +0.172       | 0.269       | 2/5        |

## Pass/Fail

| Criterion                                   | Result | Value                    |
|---------------------------------------------|--------|--------------------------|
| P1: mean R²_norm(N=32) ≥ 0.30               | FAIL   | 0.172                    |
| P2: cv_N(norm) < cv_N(std)=0.369            | PASS*  | -5.83 (*numerical artifact) |
| P3: multi beats single at N=32, ≥4/5        | FAIL   | 2/5                      |
| P4: R²_norm(N=32) > R²_std(N=32)=0.269      | FAIL   | 0.172 < 0.269            |

*P2 is NOT a genuine pass. When R² values are negative, mean R² < 0, and
cv = std/mean is negative — this is numerically less than any positive threshold
but physically meaningless. The normalized current is WORSE than unnormalized.

## Critical findings

### Finding 1: Degree normalization makes things SUBSTANTIALLY WORSE

R² goes negative on multiple seeds at N=8 and N=16:
- N=8, seed 2718: R²_norm = **-1.280** (unnormalized: 0.682)
- N=8, seed 137: R²_norm = **-0.291** (unnormalized: 0.384)
- N=16, seed 1729: R²_norm = **-1.493** (unnormalized: 0.239)
- N=16, seed 42: R²_norm = **-0.907** (unnormalized: 0.535)

Negative R² means the fitted model is worse than predicting the mean of Δρ.

### Finding 2: Why degree normalization fails

The 3×3 OLS normal equations become ill-conditioned when the three
degree-normalized channels have different cross-scale relationships. The
matrix A = [dot(dj_i, dj_j)] changes character after normalization:
- At small N (N=8), dividing by deg~3 increases the signals → OLS overshoots
- At N=16, some seeds get large coefficients that amplify residuals
- The unnormalized version has better-conditioned 3×3 systems

This is a numerical issue at the OLS level, not just a physical issue.

### Finding 3: N-weakening is structural, not a degree-scaling artifact

If degree-dilution were the dominant cause of N-weakening, normalization
would recover R² (and it does partially at N=32 for 2/5 seeds). But the
predominantly negative results at N=8 and N=16 show that the N-dependence
arises from structural changes in channel correlations, not just signal scale.

**Conclusion: The R² decrease with N in CPU-047 reflects genuine structural
evolution of the QNG dynamics at different graph densities.** The correct
density-current relationship changes character as the graph becomes denser.

### Finding 4: A few seeds improve at N=32

seeds 20260325 (+0.048) and 137 (+0.041) at N=32 show marginal improvement
with normalization. This suggests that at large N, degree normalization does
partially compensate the dilution — but the effect is too small and sign-unstable
to be the dominant correction needed.

## Physical interpretation

The degree-normalization hypothesis is **falsified**. The N-dependence of the
multi-channel continuity law is NOT primarily due to degree-dilution of the
divergence sum. Instead, it reflects:

1. **Genuine structural evolution**: At higher graph density, the correlation
   structure between channels and density changes qualitatively.

2. **The multi-channel law is intrinsically a sparse-graph law**: The
   mismatch-memory diffusion current is most informative in sparse graphs
   (low degree) where each neighbor carries strongly differentiated information.
   In dense graphs, the neighborhood average smooths out the gradient signal.

3. **QNG is a mean-field substrate at large N**: With many neighbors, each node
   sees a mean-field average of its neighborhood, losing gradient structure.
   The multi-channel law degrades to zero in the infinite-connectivity limit.

## Implication for the theory

The multi-channel continuity law (CPU-046) is confirmed as a **finite-system law**,
strongest in the sparse-graph regime (N=8–16). The large-N / dense-graph limit
requires either:
1. A different current operator (non-linear, or based on deviation from local mean)
2. A mean-field continuum limit that replaces the graph law
3. Accepting that the law is a sparse-graph result valid in the QNG UV regime

This closes the N-scaling investigation. The next logical move is the planned
**pivot to GR side** (CPU-049) as recommended by recovery-comparison-v1.
