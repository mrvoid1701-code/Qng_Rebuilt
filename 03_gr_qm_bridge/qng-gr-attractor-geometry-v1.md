# DER-BRIDGE-038 — Attractor Geometry: Degree-Density Law and GR Correction Profile

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-037 (CPU-055), DER-BRIDGE-036 (CPU-054)

---

## Motivation

CPU-055 established that:

1. The 24-step QNG rollout converges to a QM fixed-point ρ*(QM) with Δρ_0 ≈ 0.0001
2. Adding GR back-reaction (γ_tt·E_tt) shifts the attractor: ρ*(QM+GR) ≠ ρ*(QM)
3. The shift magnitude ≈ 0.001 in ρ-space, correlated with γ_tt amplitude

**Open question**: What is the spatial structure of ρ*(QM) and of the GR correction
δρ = ρ*(QM+GR) − ρ*(QM)?

If QNG has genuine geometric content, the attractor should not be uniform:

- ρ*(QM) should be higher at high-degree nodes (stronger coupling = more density)
- δρ should correlate with E_tt (the GR tensor component that drives GR→QM feedback)
- The correlation sign should be consistent: positive γ_tt → positive δρ in the
  direction of E_tt

This test characterizes the spatial geometry of the QNG attractor.

---

## Attractor geometry claims

### Claim A — Degree-density law

In the QM attractor ρ*(QM), the density at node i correlates positively with
its graph degree k_i:

    Pearson(ρ*_i, k_i) > 0.2   on majority of seeds

High-degree nodes act as hubs: more neighbors means stronger total current
flow into the node, pushing ρ_i higher.

### Claim B — GR correction correlates with E_tt

The GR correction profile δρ_i = ρ*_GR_i − ρ*_QM_i satisfies:

    |Pearson(δρ_i, E_tt_i)| > 0.05   on majority of seeds

This is a direct test that the GR back-reaction is geometrically structured,
not noise.

### Claim C — GR correction sign consistent with γ_tt

Since γ_tt > 0 on all seeds (CPU-053/054), the update γ_tt·E_tt_i is positive
where E_tt_i > 0. The attractor shift should inherit this:

    sign(Pearson(δρ, E_tt)) = sign(γ_tt)   on majority of seeds

### Claim D — Non-trivial GR profile

The GR correction is spatially structured (not uniform):

    std(δρ) / mean(|δρ|) > 0.1   on majority of seeds

A uniform shift would have ratio ≈ 0, while a structured spatial pattern has
ratio > 0.1.

---

## Protocol

For each seed in {20260325, 42, 137, 1729, 2718}:

1. Run 24-step rollout, capture final state (c_t, phi_t, mismatch_t, mem_t, adj)
2. Estimate coefficients (a_mis, a_mem, g_tt) from two-step rollout
3. Run QM-only FP iteration (K=30, η=0.05) → ρ*(QM)
4. Run QM+GR FP iteration (K=30, η=0.05) → ρ*(QM+GR)
5. Compute δρ = ρ*(QM+GR) − ρ*(QM)
6. Compute node degrees k_i = |adj[i]|
7. Compute E_tt from the rollout final state
8. Compute Pearson(ρ*(QM), k), Pearson(δρ, E_tt), std(δρ)/mean(|δρ|)

Pass criteria:

- P1: Pearson(ρ*, k) > 0.2 on ≥ 4/5 seeds
- P2: |Pearson(δρ, E_tt)| > 0.05 on ≥ 4/5 seeds
- P3: sign(Pearson(δρ, E_tt)) = sign(γ_tt) on ≥ 4/5 seeds
- P4: std(δρ)/mean(|δρ|) > 0.1 on ≥ 4/5 seeds

---

## Theoretical significance

If all four pass:

- The QNG attractor has **topological structure**: high-degree nodes concentrate density
- The GR correction has **gravitational imprint**: E_tt sculpts the density profile
- Together they describe a **geometry-matter coupling at equilibrium**: the density
  profile encodes both the graph topology (QM sector) and the linearized metric (GR sector)

This is the first characterization of the QNG equilibrium state geometry.

---

## Falsifiability

The test is falsifiable:

- P1 fails if the rollout attractor is degree-uniform (no topological structure)
- P2/P3 fail if δρ is noise-dominated (GR correction structureless)
- P4 fails if δρ is a uniform scalar shift (all nodes move together)

A partial pass (P1+P4, not P2/P3) would mean topological structure is real
but GR geometric imprint is absent — ruling out geometric back-reaction.
