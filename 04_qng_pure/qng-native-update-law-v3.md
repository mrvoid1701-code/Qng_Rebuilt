# QNG Native Update Law v3

Type: `derivation`
ID: `DER-QNG-015`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Extend the v2 update law (`DER-QNG-010`) with the generation-order cross-coupling derived in `DER-QNG-014`. The single addition is a term in the chi channel that couples chi to local sigma deviations, implementing the hierarchy `σ → χ`. All v2 structure is preserved; this document records only the delta and its consequences.

## Inputs

- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-generation-order-v1.md](qng-generation-order-v1.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)
- [qng-history-summary-v1.md](qng-history-summary-v1.md)

## Scope

Identical to `DER-QNG-010`. Ontic layer only. The cross-coupling parameter `δ` is a substrate constant — it has no phenomenological origin and is not imported from the effective-field or phenomenological layers. Setting `δ = 0` recovers the v2 law exactly.

---

## Working node state

Unchanged from v2:

```
N_i(t) = ( sigma_i(t), chi_i(t), phi_i(t) )
H_i(t) = ( M_i(t), D_i(t), P_i(t) )
```

Domains, reference state, and history structure are identical to `DER-QNG-010`.

---

## The v3 update law

### Complete explicit form

```
N_i(t+1) = Proj[  N_i(t)
                 - alpha * ( N_i(t) - N_ref )
                 + beta  * ( bar_N_i(t) - N_i(t) )
                 + gamma * M_i(t) * (1 - D_i(t)) * ( bar_N_i(t) - N_i^hist(t) )
                 + (0,  delta * (sigma_ref - sigma_i(t)),  0)
                 + eta * zeta_i(t)
                ]
```

The only change from v2 is the fourth line: `(0, delta * (sigma_ref - sigma_i(t)), 0)`.

### Channel D: generation-order cross-coupling

```
Delta_cross(i,t) = (0,  delta * (sigma_ref - sigma_i(t)),  0)
```

where:

- `delta in [0, 1)` is the cross-coupling strength (new free parameter)
- Only the chi component is non-zero
- The sigma and phi components are unchanged from v2

**Motivation:** `chi_i` is the local load or tension amplitude. Tension accumulates when the substrate element departs from its coherence reference (`sigma_i < sigma_ref`). The minimal local coupling consistent with this interpretation is a direct proportional drive. No neighbor information is needed; the coupling is purely self-referential. Setting `delta = 0` disables the channel.

**Sign:** `sigma_ref - sigma_i > 0` when coherence is depleted (presence of matter or strain). This drives `chi_i` positive, consistent with chi as a signed load variable in `[-1, 1]`.

### History update

Unchanged from `DER-QNG-010`. The history variables `M_i`, `D_i`, `P_i` and their update equations are identical.

---

## Free parameter table

| Symbol      | Domain          | Physical meaning                                                                           |
|-------------|-----------------|-------------------------------------------------------------------------------------------|
| `alpha`     | (0, 1)          | Self-relaxation rate toward reference state                                                |
| `beta`      | (0, 1)          | Relational coupling strength to neighborhood mean                                          |
| `gamma`     | (0, 1)          | History-channel coupling strength                                                          |
| `delta`     | [0, 1)          | Cross-coupling strength: sigma deviation → chi tension (new in v3)                        |
| `eta`       | [0, ∞)          | Fluctuation amplitude (0 = deterministic limit)                                            |
| `sigma_ref` | (0, 1)          | Native reference coherence amplitude                                                       |
| `alpha_M`   | (0, 1)          | Memory amplitude update rate                                                               |
| `alpha_D`   | (0, 1)          | Mismatch accumulator update rate                                                           |
| `alpha_P`   | (0, 1)          | Phase coherence update rate                                                                |

**Total free parameters: 9.** One more than v2. All 9 are defined exclusively in terms of node-level quantities.

---

## Contractiveness condition

The sufficient contractiveness condition from v2 is updated. The chi component before `Proj`:

```
chi_i(t+1)_pre = (1 - alpha - beta) * chi_i(t) + beta * chi_bar_i(t)
               + gamma * M_i * (1-D_i) * [chi_bar_i - chi_i^hist]
               + delta * (sigma_ref - sigma_i(t))
```

The cross-coupling term contributes a bounded additive shift of magnitude at most `delta` (since `|sigma_ref - sigma_i| <= 1`). The updated sufficient contractiveness condition for the chi channel is:

```
alpha + beta + gamma * sup_i( M_i * (1-D_i) ) + delta < 1
```

For the sigma and phi channels the condition is unchanged from v2.

**Practical implication:** For typical v2 parameters (`alpha = 0.08`, `beta = 0.18`, `gamma = 0.12`, `M_i * (1-D_i) <= 1`), the v2 margin is `1 - 0.08 - 0.18 - 0.12 = 0.62`. Any `delta < 0.62` preserves contractiveness at the v2 parameter point.

---

## Limiting cases

### Case 1: δ = 0 (v2 recovery)

```
Delta_cross = 0
```

The v3 law is identical to v2 for all node states. Full backward compatibility.

### Case 2: δ > 0, γ = 0, η = 0 (generation order only, no history, no noise)

```
N_i(t+1) = Proj[ (1-alpha-beta)*N_i(t) + beta*N_bar_i(t) + alpha*N_ref + (0, delta*(sigma_ref - sigma_i), 0) ]
```

At the fixed point, chi satisfies:

```
(alpha + beta) * chi_i* = beta * chi_bar_i* + delta * (sigma_ref - sigma_i*)
```

In the homogeneous background (`chi_bar = 0`, `sigma_i* = sigma_ref`): `chi_i* = 0`. The generation order produces no chi in the vacuum. Near a depleted sigma region: `chi_i* > 0`, proportional to the coherence deficit. This is the mechanism identified in `DER-QNG-014`.

### Case 3: δ → 1 - α - β (saturated cross-coupling)

Chi is driven maximally by sigma deviations. The chi dynamics become dominated by the cross-coupling rather than by relational consensus. This regime is not the Newtonian target but may be relevant for high-density substrate regions.

### Summary table

| Condition                            | Character                                           |
|--------------------------------------|-----------------------------------------------------|
| `delta = 0`                          | Identical to v2; no generation order                |
| `delta > 0`, `gamma = 0`             | Generation order active; no history coupling        |
| `delta > 0`, `gamma > 0`             | Full v3: generation order + memory coupling         |
| `delta > 0`, `sigma_i = sigma_ref`   | Cross-coupling contributes zero; chi relaxes to 0   |
| `delta > 0`, `sigma_i < sigma_ref`   | Chi accumulates; matter sector proxy activates      |

---

## Connection to the effective field layer

From `DER-QNG-014` Section 3, in the static limit and Newtonian regime:

```
L_eff(x) ≈ -(delta/alpha) * delta_C(x)
```

where `delta_C = C_eff - C_ref`. This slaving relation is the key output of the generation order. It reduces the two-field effective system `(C_eff, L_eff)` to an effectively single-field system at leading order, upgrading Assumption M.1 of `DER-QNG-013` from a declared bridge to a derived consequence.

---

## What remains open

Items 1–8 from `DER-QNG-010` carry forward unchanged. New items:

9. The value of `delta` is not constrained by the generation order argument alone. A constraint requires either: (a) matching the observed matter distribution to substrate dynamics, or (b) a QM-facing argument connecting chi tension to quantum number densities.

10. Whether `δ → φ` (analogous cross-coupling from chi to phi) is required for the QM-facing closure is open. `DER-QNG-014` Section 7, Question 2.

11. The history correction to `G_QNG` at order `δ·γ/(α·β)` is not computed. Its sign determines whether the generation order strengthens or weakens effective gravitational coupling at subleading order.

---

## Cross-references

- v2 law: `DER-QNG-010` (`qng-native-update-law-v2.md`)
- Generation order derivation: `DER-QNG-014` (`qng-generation-order-v1.md`)
- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
- Matter source identification: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
