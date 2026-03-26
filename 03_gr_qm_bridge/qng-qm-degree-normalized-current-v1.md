# QNG QM Degree-Normalized Multi-Channel Current v1

Type: `derivation`
ID: `DER-BRIDGE-030`
Status: `proxy-supported` (FAIL — normalization hypothesis falsified; N-weakening is structural)
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-029` (large-N probe — sparse-graph law, N-weakening identified)

## Objective

Test whether normalizing the divergence current by local node degree restores
N-stability of the multi-channel continuity law.

## Background

QNG-CPU-047 identified the cause of R² degradation with N:

- `build_graph` creates ring + Erdos-Renyi (p=0.18) → mean_degree scales with N
  - N=8: mean_degree=3.2
  - N=16: mean_degree=4.3
  - N=32: mean_degree=6.9
- Larger degree → more neighbor terms in the divergence sum → increased cancellation
  of opposite-direction gradients → weaker signal → lower R²
- mean R²: 0.586 (N=8) → 0.405 (N=16) → 0.269 (N=32)

This is a **degree-dilution effect**: the divergence signal is diluted by the
number of neighbors. The fix is to normalize by local degree.

## Construction

### Standard (unnormalized) divergence

```
div(J_X)_i = C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · Δf_{ij}
```

where `Δf_{ij} = f_j - f_i` (for mismatch, mem) or `sin(phi_j - phi_i)` (for phi).

### Degree-normalized divergence

```
divN(J_X)_i = (1 / deg_i) · C_eff_i · Σ_{j∈neighbors(i)} C_eff_j · Δf_{ij}
```

where `deg_i = |neighbors(i)|` is the local degree of node i.

Physical meaning: divN is the **per-neighbor average** divergence, not the
total divergence. This removes the degree-scaling artifact and gives a
signal that measures the average gradient, not the sum.

### Multi-channel calibrated continuity (same OLS form)

```
Δρ + α_phi·divN(J_phi) + α_mis·divN(J_mis) + α_mem·divN(J_mem) ≈ 0
```

Solve by 3×3 normal equations (same as CPU-046).

### N-stability criterion

For the current to be N-stable, we need R²_combined to remain roughly constant
(within ±0.05 of the N=16 reference) across N=8, 16, 32.

## Why degree normalization might restore N-stability

In a d-regular graph (all nodes have same degree d), the divergence scales as d·J̄
where J̄ is the mean edge current. Normalizing by d gives J̄ — independent of d.

In the QNG random graph, degrees are heterogeneous but the mean degree scales with N.
Dividing by deg_i accounts for the heterogeneous degree and removes the bulk
dilution effect.

Prediction: After normalization, the per-neighbor gradient signal |divN(J_X)/deg|
should be roughly degree-independent → R² more stable across N.

## Claims

### Claim A: mean R²_combined(N=32) ≥ 0.30 with degree normalization

Prediction: OPEN

Argument: At N=32 without normalization, mean R²=0.269. The degree-dilution
effect accounts for a factor ~(4.3/6.9)=0.62 in signal strength (comparing
N=16 to N=32 mean degree ratio). Normalization should recover at least part
of the lost R².

### Claim B: R² is more N-stable with normalization than without

Metric: cv_N(R²_combined) = std(R² across N=8,16,32) / mean(R² across N=8,16,32)
Prediction: cv_N(R²_normalized) < cv_N(R²_standard)

Argument: Normalization removes the degree-scaling component of the signal.
If degree-dilution is the dominant N-dependence, cv should decrease.

### Claim C: multi-channel beats single-channel universally (15/15)

Prediction: OPEN but expected PASS

Argument: Degree normalization changes the scale but not the relative structure
of the channels. The topology-selective preference observed in CPU-045 should
persist — so combination should still beat single-channel.

### Claim D: improvement over unnormalized at N=32 (mean R²_norm > mean R²_std=0.269)

Prediction: OPEN

Argument: Normalization directly compensates the degree-dilution effect.
R² at N=32 should improve toward the N=16 reference of 0.405.

## Physical interpretation

If degree normalization restores N-stability (R² ~0.40 at all N):
- The correct current is the **per-neighbor average gradient**, not the total sum
- The QNG continuity equation uses a mean-field form of the divergence
- This is consistent with the QNG update rule itself, which uses neighbor means
  (neigh_mean, circular_mean) rather than neighbor sums

If degree normalization does NOT restore N-stability:
- The N-dependence is not purely due to degree-dilution
- There is additional structural change in the correlations at large N
- The law requires a fundamentally different large-N treatment

## Validation

Test: `QNG-CPU-048` — `qng_degree_normalized_current_reference.py`
Decision: FAIL (1/4 — P2 is numerical artifact with negative R²)

Results:
- P1: mean R²_norm(N=32) ≥ 0.30 — FAIL (0.172)
- P2: cv_N(norm) < cv_N(std) — PASS (numerical artifact: mean R²<0)
- P3: multi beats single at N=32, ≥4/5 — FAIL (2/5)
- P4: R²_norm(N=32) > 0.269 — FAIL (0.172 < 0.269)

Key finding: Degree normalization makes R² go NEGATIVE on many seeds (e.g.,
N=8 seed 2718: R²=-1.280). The 3×3 OLS system becomes ill-conditioned after
normalization. The hypothesis is FALSIFIED: N-weakening is NOT due to degree
dilution alone — it is a structural feature of the QNG channel correlations.
Multi-channel law is confirmed as a sparse-graph law (valid in QNG UV regime).
GR pivot (CPU-049) is the next step per recovery-comparison-v1.
