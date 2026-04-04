# QNG Native Update Law v2

Type: `derivation`
ID: `DER-QNG-010`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Specify `U_local` explicitly: replace every placeholder in the v1 abstract decomposition with a concrete, physically motivated expression. Every functional form and every free parameter must be interpretable entirely within the node ontology defined by `qng-primitives-v1.md`, `qng-history-summary-v1.md`, and `qng-state-space-v1.md`. No parameter may be imported from phenomenology or from outside the substrate.

## Inputs

- [qng-primitives-v1.md](qng-primitives-v1.md)
- [qng-state-space-v1.md](qng-state-space-v1.md)
- [qng-memory-structure-v1.md](qng-memory-structure-v1.md)
- [qng-history-summary-v1.md](qng-history-summary-v1.md)
- [qng-ontology-backbone-v1.md](qng-ontology-backbone-v1.md)
- [qng-native-update-law-v1.md](qng-native-update-law-v1.md)

## Scope

This document lives entirely at the ontic level (levels 1 and 2 in the ontological backbone). It does not use effective fields, does not import fitted parameters, and does not couple to the phenomenological layer. Any connection to `Sigma_effective`, `tau`, or emergent geometry must be derived in a downstream document.

---

## Working node state

Following `qng-primitives-v1.md`, the local node state is treated as a tuple of three scalar components:

```
N_i(t) = ( sigma_i(t), chi_i(t), phi_i(t) )
```

where:

- `sigma_i(t)` is a bounded local compatibility or coherence amplitude; `sigma_i in [0, 1]`
- `chi_i(t)` is a signed local load or tension amplitude; `chi_i in [-1, 1]`
- `phi_i(t)` is a local phase-memory variable; `phi_i in [-pi, pi]`

The primitive/derived status of each component remains open as stated in `qng-primitives-v1.md`. The v2 update law treats them as a working triple. Nothing below changes if a future decision promotes or demotes one component, provided the domain constraints above are preserved.

The local history summary follows `qng-history-summary-v1.md`:

```
H_i(t) = ( M_i(t), D_i(t), P_i(t) )
```

where:

- `M_i(t) in [0, 1]` is the retained local memory amplitude
- `D_i(t) in [0, 1]` is the local mismatch or tension accumulator
- `P_i(t) in [-pi, pi]` is the retained local phase coherence

---

## The v1 abstract form (carried forward)

From `qng-native-update-law-v1.md`:

```
N_i(t+1) = Proj[ N_i(t) + Delta_self(i,t) + Delta_rel(i,t) + Delta_hist(i,t) + Xi_i(t) ]
```

with a companion history update:

```
H_i(t+1) = U_hist( H_i(t), N_i(t+1), mean_{j in Adj(i)} N_j(t+1) )
```

The four channels and `Proj` are now specified below. The history update `U_hist` is specified in its own section.

---

## Notation

Let `k_i = |Adj(i)|` denote the degree of node `i`.

Let the local neighborhood mean at time `t` be:

```
bar_N_i(t) = (1 / k_i) * sum_{j in Adj(i)} N_j(t)
```

with components `bar_sigma_i`, `bar_chi_i`, `bar_phi_i`.

When `k_i = 0` (isolated node), set `bar_N_i(t) = N_i(t)` so that the relational channel contributes zero without special-casing.

---

## Channel A: self-relaxation

### Expression

```
Delta_self(i,t) = -alpha * ( N_i(t) - N_ref )
```

where:

- `alpha in (0, 1)` is the self-relaxation rate (free parameter, see parameter table)
- `N_ref = (sigma_ref, 0, 0)` is the node reference state

### Motivation

Each node relaxes toward a reference configuration in the absence of coupling. The reference state has zero tension (`chi_ref = 0`), no preferred phase (`phi_ref = 0`), and a reference coherence `sigma_ref in (0, 1)` that is a substrate-level constant (see parameter table). The sign is chosen so that if a component is above its reference value, the channel pulls it down, and conversely. The rate `alpha` controls how strongly the node's own history biases it toward baseline. No external field is needed: the reference state is purely a native substrate equilibrium.

### Limiting behavior

When `alpha -> 0`: self-relaxation is disabled; the node retains its current state indefinitely in the absence of other channels.

When `alpha -> 1`: the node forgets its current state completely and collapses to `N_ref` in one step (before `Proj`).

---

## Channel B: relational coupling

### Expression

```
Delta_rel(i,t) = beta * ( bar_N_i(t) - N_i(t) )
```

where:

- `beta in (0, 1)` is the relational coupling strength (free parameter, see parameter table)

### Motivation

Each node moves toward the mean state of its current neighborhood. This is the minimal local relational coupling consistent with the ontological backbone's locality requirement. The form is a discrete-time diffusion or consensus step on the graph. It has no preferred direction imposed externally: the only input is the present-step neighborhood mean. The rate `beta` encodes how strongly adjacency drives local state equalization. Because both `N_i(t)` and `bar_N_i(t)` live in the same domain, the difference is always bounded.

### Limiting behavior

When `beta -> 0`: nodes decouple; the relational channel is off.

When `beta -> 1`: the node fully adopts its neighborhood mean in one step (before `Proj`).

---

## Channel C: history-sensitive correction

### Expression

Define the history-weighted reference state:

```
N_i^hist(t) = ( M_i(t) * sigma_ref + (1 - M_i(t)) * sigma_i(t),
                M_i(t) * 0         + (1 - M_i(t)) * chi_i(t),
                P_i(t) )
```

This interpolates between the current node state and the reference, weighted by retained memory amplitude `M_i`, with phase set by the stored phase coherence `P_i`.

The present-step mismatch between neighborhood and stored history is:

```
mismatch_i(t) = bar_N_i(t) - N_i^hist(t)
```

The history channel is:

```
Delta_hist(i,t) = gamma * M_i(t) * (1 - D_i(t)) * mismatch_i(t)
```

where:

- `gamma in (0, 1)` is the history-coupling strength (free parameter, see parameter table)

### Motivation

The correction fires only when the node has retained memory (`M_i` large) and is not already in high internal tension (`D_i` small). When the present neighborhood departs from what the node remembers, the history channel resists the departure by pulling toward the stored reference. The factor `M_i * (1 - D_i)` acts as a native gate: a node with no memory (`M_i = 0`) or a saturated mismatch accumulator (`D_i = 1`) contributes zero history correction. This is the sense in which memory is structural, not phenomenological: it gates dynamical influence rather than adding a lag term by hand.

### Limiting behavior

When `gamma -> 0` or `M_i -> 0` uniformly: history channel is off; the update reduces to channels A and B only.

When `D_i -> 1` uniformly: the node is in maximum tension; the history channel is also suppressed. The node is then driven only by self-relaxation and relational coupling until tension relaxes.

---

## Fluctuation term

### Expression

```
Xi_i(t) = eta * zeta_i(t)
```

where:

- `eta >= 0` is the fluctuation amplitude (free parameter, see parameter table)
- `zeta_i(t)` is a vector of independent draws from a zero-mean, unit-variance distribution over the same component space as `N_i`

### Status

`Xi_i(t)` is not declared ontologically primitive. It represents unresolved microstructure below the resolution of the node description. Setting `eta = 0` gives a deterministic update law. The parameter `eta` controls whether substrate-level fluctuations are included, and at what amplitude, without committing to their origin.

---

## The Proj operator

### Why not clip01

Clipping has two structural problems:

1. It introduces non-differentiable corners that are artifacts of the projection, not of the physics.
2. It can return states that exactly saturate the boundary, making it impossible to distinguish a physical saturated state from a numerical artifact.

### Chosen form: component-wise sigmoid normalization

Define the smooth bounded map `S` applied component-wise:

```
S(x; x_min, x_max) = x_min + (x_max - x_min) * sigmoid(x)

sigmoid(x) = 1 / (1 + exp(-x))
```

Applied to each component with its natural domain:

```
Proj( N )[sigma] = S( N[sigma]; 0, 1 )
Proj( N )[chi]   = 2 * sigmoid( N[chi] ) - 1
Proj( N )[phi]   = wrap( N[phi]; -pi, pi )
```

where `wrap` is the standard modular wrapping onto `[-pi, pi]`.

### Motivation

The sigmoid map is smooth everywhere, is analytically differentiable, preserves the interior of the domain (values near the boundary are compressed but not pinned), and introduces no free parameters. The only inputs to `Proj` are the domain bounds inherited from the node ontology. The phase component uses wrapping rather than sigmoid because phase variables are periodic, not one-sided. `Proj` is therefore derived entirely from the domain constraint of the node state, not from phenomenological considerations.

---

## Complete explicit update law

Collecting all channels:

```
N_i(t+1) = Proj[  N_i(t)
                 - alpha * ( N_i(t) - N_ref )
                 + beta  * ( bar_N_i(t) - N_i(t) )
                 + gamma * M_i(t) * (1 - D_i(t)) * ( bar_N_i(t) - N_i^hist(t) )
                 + eta   * zeta_i(t)
                ]
```

with:

- `Proj` as specified above
- `bar_N_i(t) = (1/k_i) * sum_{j in Adj(i)} N_j(t)`
- `N_i^hist(t)` as defined in Channel C
- `N_ref = (sigma_ref, 0, 0)`

---

## History update U_hist

The companion update for `H_i(t)`.

### Memory amplitude

```
M_i(t+1) = (1 - alpha_M) * M_i(t)  +  alpha_M * |N_i(t+1) - bar_N_i(t+1)|_norm
```

where the component-averaged absolute deviation is:

```
|v|_norm = (1/3) * ( |v[sigma]| + |v[chi]| + |v[phi]| / pi )
```

and `alpha_M in (0,1)` is the memory-update rate (free parameter, see parameter table).

Interpretation: `M_i` tracks how much the node's updated state diverges from its current neighborhood. Large divergence accumulates memory; small divergence relaxes it toward zero.

### Mismatch accumulator

```
D_i(t+1) = (1 - alpha_D) * D_i(t)  +  alpha_D * |bar_N_i(t) - N_i^hist(t)|_norm
```

where `alpha_D in (0,1)` is the tension-update rate (free parameter, see parameter table).

Interpretation: `D_i` accumulates when the present neighborhood consistently differs from what the node remembers. It relaxes when neighborhood and memory align.

### Phase coherence

```
P_i(t+1) = wrap( (1 - alpha_P) * P_i(t)  +  alpha_P * bar_phi_i(t+1) )
```

where `alpha_P in (0,1)` is the phase-update rate (free parameter, see parameter table), and `bar_phi_i(t+1)` is the neighborhood-mean phase at step `t+1`.

Interpretation: `P_i` blends the node's retained phase memory toward the neighborhood's mean phase at rate `alpha_P`.

---

## Free parameter table

| Symbol      | Domain          | Physical meaning in node ontology                                                          |
|-------------|-----------------|-------------------------------------------------------------------------------------------|
| `alpha`     | (0, 1)          | Rate at which a node relaxes toward its own reference state, absent coupling               |
| `beta`      | (0, 1)          | Strength of local relational coupling to present neighborhood mean                         |
| `gamma`     | (0, 1)          | Strength of history-sensitive correction when memory is retained and tension is low        |
| `eta`       | [0, ∞)          | Amplitude of unresolved fluctuation (0 = deterministic limit)                              |
| `sigma_ref` | (0, 1)          | Native reference coherence amplitude; the substrate baseline for self-relaxation           |
| `alpha_M`   | (0, 1)          | Rate at which memory amplitude `M_i` responds to present-step divergence                  |
| `alpha_D`   | (0, 1)          | Rate at which mismatch accumulator `D_i` responds to present-step neighborhood tension     |
| `alpha_P`   | (0, 1)          | Rate at which phase memory `P_i` adopts the present neighborhood phase                     |

**Total free parameters: 8.** All 8 have a stated physical meaning exclusively in terms of node-level quantities (`N_i`, `H_i`, `Adj(i)`). None reference any effective field, phenomenological observable, or external physical scale.

---

## Limiting cases

### Case 1: history turned off (`gamma = 0` or `M_i -> 0` uniformly)

```
N_i(t+1) = Proj[ (1 - alpha - beta) * N_i(t)  +  beta * bar_N_i(t)  +  alpha * N_ref  +  Xi_i(t) ]
```

Standard linear graph consensus step with self-relaxation toward `N_ref` and optional noise. Markovian — no memory.

### Case 2: relational coupling and history off (`beta = 0`, `gamma = 0`)

```
N_i(t+1) = Proj[ (1 - alpha) * N_i(t)  +  alpha * N_ref  +  Xi_i(t) ]
```

Each node evolves independently, exponentially relaxing toward `N_ref`. Graph structure is irrelevant.

### Case 3: minimal deterministic limit (`beta = 0`, `gamma = 0`, `eta = 0`)

```
N_i(t+1) = Proj[ (1 - alpha) * N_i(t)  +  alpha * N_ref ]
```

Pure geometric relaxation. Every component converges to `N_ref` at rate `alpha`.

### Summary table

| Condition                              | Effective form                     | Character                          |
|----------------------------------------|------------------------------------|------------------------------------|
| `gamma = 0` (history off)              | Linear consensus + self-relax      | Markovian graph diffusion          |
| `beta = 0`, `gamma = 0`                | Independent node decay             | No graph structure                 |
| `beta = 0`, `gamma = 0`, `eta = 0`     | Pure node decay to `N_ref`         | Minimal deterministic limit        |
| `alpha = 0`, `eta = 0`                 | Relational + history only          | Memory-coupled consensus           |
| Full law, `eta = 0`                    | Deterministic native QNG           | Primary working form               |

---

## Domain of validity

### Graph class

Applies to any finite graph `G(t)` that is undirected, locally finite (`k_i < ∞`), and connected (or isolated nodes handled by `bar_N_i = N_i`). Dynamic graph topology permitted provided each step uses adjacency at time `t`.

### Contractiveness condition (sufficient)

```
alpha + beta + gamma * sup_i( M_i * (1 - D_i) ) < 1
```

Under this constraint the pre-`Proj` argument is a convex combination of bounded quantities.

### Timescales

No physical time unit is assigned at this layer. Effective time units emerge only after the effective-field and emergent-geometry layers are defined downstream.

---

## What remains open

1. A nonlinear self-relaxation drive (e.g., double-well potential in `sigma_i`) is a natural generalization, deferred.
2. Finite-depth history windows may be needed once effective-lag structure is studied.
3. Correlated noise structure for `Xi_i(t)` not specified.
4. Node-local sigmoid with state-dependent width is possible but deferred.
5. Derivation of effective lag `tau_eff` from `(M_i, D_i)` under coarse-graining belongs in the effective-field-layer document.
6. Fixed-point structure and stability of the full coupled system under all four channels not yet analyzed — required before numerical implementations are trusted.
7. Whether `sigma_ref` varies by node class remains open; currently treated as uniform.
8. A physically motivated upper bound on `eta` from contractiveness requirements not stated.
