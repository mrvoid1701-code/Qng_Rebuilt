# QNG Covariance Stability

- decision: `pass`
- seeds tested: [42, 137, 1729, 2718, 31415]
- w_eff values: [-0.6866, -0.6547, -0.7429, -0.6352, -0.6232]
- w_eff mean: `-0.6685`
- w_eff std/mean: `0.0718` (< 0.20 required)
- corr(E_tt,E_xx) per seed: [-0.998, -0.962, -0.856, -0.999, -0.994]
- tensor separation per seed: [1.769, 1.747, 0.914, 2.981, 0.862]

## Tier 1 — Universal (topology-independent)
- corr(E_tt, E_xx) strongly negative on all seeds
- w_eff stable near -0.69 across all seeds
- tensor components always respond differently to P_delta

## Tier 2 — Topology-dependent
- sign of individual P_delta coefficients (e_xx, e_tt) flips between topologies
- magnitude of history amplification varies
