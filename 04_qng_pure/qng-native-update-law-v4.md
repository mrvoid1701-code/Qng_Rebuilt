# QNG Native Update Law v4

Type: `derivation`
ID: `DER-QNG-016`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Extend the v3 update law (`DER-QNG-015`) with Channel E: a direct `χ → φ` coupling
that implements Prediction P1 from `NOTE-QNG-009`. The single addition is a term
`ε·χ_i` in the phi channel, giving chi tension the ability to drive local phase
accumulation. All v3 structure is preserved; setting `ε = 0` recovers v3 exactly.

## Inputs

- [qng-native-update-law-v3.md](qng-native-update-law-v3.md)
- [qng-chi-ontology-v1.md](qng-chi-ontology-v1.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)

## Scope

Identical to `DER-QNG-015`. Ontic layer only. The coupling parameter `ε` is a
substrate constant with no phenomenological origin. Setting `ε = 0` recovers v3.

---

## Working node state

Unchanged from v3:

```
N_i(t) = ( sigma_i(t), chi_i(t), phi_i(t) )
H_i(t) = ( M_i(t), D_i(t), P_i(t) )
```

---

## The v4 update law

### Complete explicit form

```
N_i(t+1) = Proj[  N_i(t)
                 - alpha * ( N_i(t) - N_ref )
                 + beta  * ( bar_N_i(t) - N_i(t) )
                 + gamma * M_i(t) * (1 - D_i(t)) * ( bar_N_i(t) - N_i^hist(t) )
                 + (0,  delta * (sigma_ref - sigma_i(t)),  0)
                 + (0,  0,  epsilon * chi_i(t))
                 + eta * zeta_i(t)
                ]
```

The only change from v3 is the fifth line: `(0, 0, epsilon * chi_i(t))`.

### Channel E: chi-to-phi coupling

```
Delta_chi_phi(i,t) = (0,  0,  epsilon * chi_i(t))
```

where:

- `epsilon ∈ ℝ` is the chi-to-phi coupling strength (new free parameter)
- Only the phi component is non-zero
- The sigma and chi components are unchanged from v3

**Motivation:** If `χ_i` acts as coherence suppression (NOTE-QNG-009, Section 2),
it must leave a signature on the phase variable φ — the candidate quantum-phase
variable. The minimal coupling is a direct additive drive: a node under chi tension
accumulates phase at rate `ε·χ_i` per step. This is analogous to a detuning in a
two-level quantum system, where population imbalance shifts the precession frequency.

**Sign convention:** With `χ_i > 0` (coherence depleted, source region) and `ε > 0`,
phi is driven in the positive direction. The absolute sign is not constrained by
generation order; it is a free orientation.

**Linearity:** The coupling is linear in χ_i. Non-linear extensions (e.g., `ε·χ_i²`
or `ε·sign(χ_i)`) are possible but not introduced here. The linear form is the minimal
non-trivial coupling.

**Boundedness:** Since `chi_i ∈ [-1, 1]` and phi evolves under `wrap()`, the term
`ε·chi_i` contributes at most `|ε|` per step to phi. The phi channel remains bounded.

---

## Free parameter table

| Symbol      | Domain          | Physical meaning                                                                           |
|-------------|-----------------|-------------------------------------------------------------------------------------------|
| `alpha`     | (0, 1)          | Self-relaxation rate toward reference state                                                |
| `beta`      | (0, 1)          | Relational coupling strength to neighborhood mean                                          |
| `gamma`     | (0, 1)          | History-channel coupling strength                                                          |
| `delta`     | [0, 1)          | Cross-coupling: sigma deficit → chi tension (v3, Channel D)                               |
| `epsilon`   | ℝ               | Cross-coupling: chi tension → phase accumulation (new in v4, Channel E)                   |
| `eta`       | [0, ∞)          | Fluctuation amplitude (0 = deterministic limit)                                            |
| `sigma_ref` | (0, 1)          | Native reference coherence amplitude                                                       |
| `alpha_M`   | (0, 1)          | Memory amplitude update rate                                                               |
| `alpha_D`   | (0, 1)          | Mismatch accumulator update rate                                                           |
| `alpha_P`   | (0, 1)          | Phase coherence update rate                                                                |

**Total free parameters: 10.** One more than v3.

---

## Contractiveness

The phi channel update (pre-wrap) for node i:

```
phi_i(t+1)_pre = phi_i + phi_rel * angle_diff(phi_bar_i, phi_i) + epsilon * chi_i
```

The phi channel is intrinsically bounded by the `wrap()` projection. The relational
term is contractive (phi_rel < 1 ensures angle_diff shrinks). The epsilon term is a
bounded additive perturbation (`|epsilon * chi_i| <= |epsilon|`). Contractiveness
of the phi dynamics is not affected in the sense of orbit boundedness, but the epsilon
term introduces a persistent drift when chi is non-zero.

**Drift rate:** In a uniform chi background `chi_i = C` (constant), phi precesses at
rate `ε·C` per step indefinitely. This is a free precession, not dissipation.
Contractiveness toward a fixed point is broken by Channel E when chi ≠ 0; the system
approaches a limit cycle (uniform phase rotation) rather than a fixed point in phi.

---

## Limiting cases

### Case 1: ε = 0 (v3 recovery)

```
Delta_chi_phi = 0
```

Identical to v3 for all states.

### Case 2: ε > 0, δ = 0 (Channel E only, no Channel D)

Chi is zero everywhere (no sigma→chi drive). Channel E contributes nothing.
Phi dynamics are identical to v2. This confirms that Channel E requires Channel D
to have any observable effect.

### Case 3: ε > 0, δ > 0 (full v4 near source)

Chi is elevated near the source (F3 from NOTE-QNG-009). Phi accumulates at rate
`ε·χ_i(x)` per step. The spatial profile of chi imprints on phi: nodes near the
source precess faster than bulk nodes. This spatial differential precession is the
substrate-level mechanism behind P1.

### Case 4: ε > 0, uniform chi background `⟨χ⟩ ≠ 0`

Phi precesses uniformly at rate `ε·⟨χ⟩`. The autocorrelation function
`C_φ(τ) ∝ cos(ε·⟨χ⟩·τ)` develops an oscillatory modulation absent in the ε=0 case.
This is Prediction P1, Check 1.

---

## Prediction P1 — formal statement

With `δ > 0` (Channel D active) establishing a chi background, and `ε > 0` (Channel E
active), in the frozen background approximation:

**P1.1 — Mean frequency shift:**
```
ω_phi = ε · ⟨χ⟩
```
The mean angular drift rate of φ is proportional to mean chi tension and to ε.

**P1.2 — Spatial broadening:**
Nodes with higher local chi accumulate phase faster. The phi spatial power spectrum
acquires structure proportional to the chi spatial profile.

**P1.3 — Null in Condition A:**
With δ=0 → ⟨χ⟩ ≈ 0 → ω_phi ≈ 0. No frequency shift.

---

## What remains open

Items 1–11 from `DER-QNG-015` carry forward. New item:

12. The value of `ε` is not constrained by the chi-phi coupling argument alone.
    A constraint requires a QM-facing argument: either matching the observed
    decoherence rate to substrate dynamics, or a dispersion relation calculation.
    This is the next step in the QM-facing closure program.

13. Channel E breaks phi fixed-point convergence when chi ≠ 0. The quasi-static
    approximation for the phi sector must be revised: phi is no longer quasi-static
    in the presence of chi tension.

---

## Cross-references

- v3 law: `DER-QNG-015` (`qng-native-update-law-v3.md`)
- Chi ontology and P1: `NOTE-QNG-009` (`qng-chi-ontology-v1.md`)
- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
