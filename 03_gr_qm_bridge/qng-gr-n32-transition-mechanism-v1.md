# DER-BRIDGE-044 — N=32 Topological Transition Mechanism

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-043 (CPU-061), DER-BRIDGE-033 (CPU-051)
**Cross-sector**: GR coupling anomaly (CPU-051/052) + signature decay anomaly (CPU-061)

---

## Motivation

Three independent sectors show anomalous behavior at N=32:

1. **GR coupling** (CPU-051): sign(e_mis) first normalizes to −1 universally at N=32
2. **GR continuum** (CPU-052): non-monotone Δratio; dense regime onset at N=32
3. **Signature decay** (CPU-061): no-history |corr| collapse peaks at N=32 (0.629)

All three anomalies occur at N=32, then partially recover at N=64. This suggests
a structural transition in the QNG graph at N≈32 that affects multiple sectors.

**Proposed mechanism**: phi synchronization velocity — the rate at which the
Kuramoto order parameter r(t) increases per rollout step — peaks at N=32 without
history. Fast sync → fast phi-disorder collapse → maximum signature damage at N=32.

At N=64, sync slows again (larger graph → smaller per-step phi change per node)
because each edge contributes 1/(degree) to the phi update, and degree grows with N.

---

## Graph topology analysis

For an Erdős-Rényi graph G(N, p) with fixed p:
- Mean degree k̄ = (N−1)·p grows linearly with N
- Algebraic connectivity λ_2 ~ p·N grows with N (faster sync at large N)
- BUT: Kuramoto dynamics compete with graph size N
  - Each node has ~p·N neighbors
  - Each step changes phi by ~J·sin(Δφ) summed over neighbors
  - Net sync speed ∝ p (independent of N for large N)
  - This gives the observed N^(−0.87) decay law with history

Without history: the phi update includes memory/mismatch corrections that may
produce non-monotone sync rates. Specifically:
- At small N: few neighbors → slow consensus → slow sync
- At N=32: optimal combination of connectivity and update magnitude → fastest sync
- At N=64: more neighbors but each contributes less → slower per-step change

---

## Protocol

For each N in {8, 16, 32, 64} and seed in {20260325, 42, 137, 1729, 2718}:

### Graph metrics (from adj):
- mean_degree: k̄ = mean(|adj[i]|)
- degree_cv: std(k) / mean(k)  (coefficient of variation)
- clustering: C = mean_i [edges among neighbors of i / (k_i·(k_i−1)/2)]
- mean_path_length: L = mean BFS path length (Floyd-style or BFS)

### Phi sync velocity:
- Run rollout WITHOUT history for steps 1..24
- Compute kuramoto order r(t) at each step
- Fit linear slope over steps 1..12 → early sync rate v_sync
- Peak at N=32 → N=32 transition confirmed

Pass criteria:

- P1: v_sync (no-history) peaks at N=32 on ≥ 4/5 seeds
- P2: mean_degree k̄ increases with N (confirms ER structure, calibration)
- P3: clustering C decreases or is non-monotone with N (topology changes character)
- P4: Pearson(mean v_sync(N), Δ_nohist(N)) > 0.5 across N values

---

## Theoretical significance

**If P1 passes**: phi sync velocity peaks at N=32, directly explaining the
no-history signature collapse. The N=32 transition is a sync-rate transition.

**If P4 passes**: sync velocity quantitatively predicts signature decay — a
causal mechanism, not just correlation.

**If P3 passes**: graph clustering coefficient changes at N=32 — the structural
transition has a topological origin (clustering affects the mismatch/memory
field coupling which drives phi updates).

The combined evidence would establish N=32 as a **universal QNG scale**:
- Below N=32: sparse-regime dynamics (topology-dominated)
- At N=32: critical transition (maximal anomalies)
- Above N=32: dense-regime dynamics (mean-field-like)
