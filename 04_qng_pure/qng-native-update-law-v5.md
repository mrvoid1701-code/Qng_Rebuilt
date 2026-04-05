# QNG Native Update Law v5

Type: `derivation`
ID: `DER-QNG-026`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Extend the v4 update law (`DER-QNG-016`) with Channel F: phase-coherence feedback
into the sigma channel. The new term suppresses sigma_i when the local phi field is
disordered — specifically when neighboring node phases do not align coherently. This
produces sigma depletion at phi vortex cores, where the phase winds by 2π around a
single plaquette and the neighborhood order parameter |Z_i| drops toward zero.

This is the minimal coupling that makes (sigma, phi) a coherent pair — analogous to
the Gross-Pitaevskii equation where the condensate density goes to zero where the
phase is undefined.

**Motivated by QNG-CPU-041 (PASS):** phi vortices are topologically stable in v3/v4,
but sigma is NOT depleted at the vortex core (sigma channel is autonomous). The matter
stability program (DER-QNG-025) requires sigma depletion at the core for the phi vortex
to constitute a matter particle. Channel F provides this coupling.

## Inputs

- [qng-native-update-law-v4.md](qng-native-update-law-v4.md)
- [qng-matter-stability-v1.md](qng-matter-stability-v1.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)

---

## The v5 update law

### Complete explicit form

```
N_i(t+1) = Proj[  N_i(t)
                 - alpha * ( N_i(t) - N_ref )
                 + beta  * ( bar_N_i(t) - N_i(t) )
                 + gamma * M_i(t) * (1 - D_i(t)) * ( bar_N_i(t) - N_i^hist(t) )
                 + (0,  delta * (sigma_ref - sigma_i(t)),  0)
                 + (0,  0,  epsilon * chi_i(t))
                 - (gamma_phi * (1 - |Z_i(t)|) * sigma_i(t),  0,  0)
                 + eta * zeta_i(t)
                ]
```

The only change from v4 is the sixth line (Channel F, negative sign in sigma component).

### Channel F: phase-coherence feedback into sigma

```
Delta_phi_sigma(i,t) = (-gamma_phi * phase_disorder_i(t) * sigma_i(t),  0,  0)
```

where:

```
Z_i(t) = (1/z) * sum_{j in N(i)} exp( i * phi_j(t) )    [complex mean of z neighbors]
|Z_i(t)| in [0, 1]                                       [phase order parameter]
phase_disorder_i(t) = max(0, 1 - |Z_i(t)|) in [0, 1]    [phase disorder = 1 - order]
```

- `Z_i` is the normalized complex sum of neighbor phase phasors
- `|Z_i| = 1`: all neighbors have the same phase (perfect order) — Channel F has zero effect
- `|Z_i| = 0`: neighbor phases maximally disordered — Channel F drives sigma to zero
- `gamma_phi >= 0` is the phase-coherence coupling strength (new free parameter)
- Only the sigma component is non-zero; chi and phi channels are unchanged from v4

**Physical motivation:**

In QNG, sigma_i is the coherence amplitude of node i. A node cannot maintain high
coherence if its neighborhood is in a state of phase disorder. The coupling:
```
sigma_i(t+1) -= gamma_phi * (1 - |Z_i|) * sigma_i(t)
```
is the minimal linear term that:
1. Has no effect in the ordered phase (|Z_i| = 1): sigma dynamics unchanged from v4
2. Drives sigma → 0 at full disorder (|Z_i| = 0): sigma depleted at vortex core
3. Is proportional to sigma_i: cannot drive sigma below zero (Proj clamps at 0)
4. Is proportional to disorder (1 - |Z_i|): smooth interpolation

This is the discrete analog of the quantum pressure term in the Gross-Pitaevskii
equation: Ψ = √ρ * exp(iφ), where the condensate density ρ → 0 at a vortex core
because the phase φ is undefined there, creating infinite kinetic energy in the
continuum limit. In QNG, the equivalent is: sigma is penalized by the local
phase incoherence of its neighborhood.

**Structural analogy:**

| GP equation                           | QNG v5                                      |
|---------------------------------------|---------------------------------------------|
| ρ = |Ψ|²  (condensate density)       | sigma_i (coherence amplitude)               |
| φ = arg(Ψ)  (condensate phase)        | phi_i ∈ S¹ (node phase)                    |
| ρ = 0 at vortex core (undefined φ)   | sigma_eq → 0 at vortex core (|Z_i| → 0)    |
| Quantum pressure ~ ∇²√ρ / √ρ         | gamma_phi * (1 - |Z_i|) (discrete analog)   |
| Winding number W ∈ ℤ (quantized)     | Winding number W ∈ ℤ (quantized)           |

---

## Equilibrium analysis

At equilibrium (sigma_eq), the sigma update balances:
```
alpha * (sigma_ref - sigma_eq) = gamma_phi * D * sigma_eq
```
where D = phase_disorder = 1 - |Z_i| (constant at equilibrium).

Solving:
```
sigma_eq = sigma_ref * alpha / (alpha + gamma_phi * D)
```

**Bulk (D ≈ 0):** sigma_eq ≈ sigma_ref (unchanged from v4)

**Vortex core (D ≈ D_core):**
```
sigma_eq = sigma_ref * alpha / (alpha + gamma_phi * D_core)
```

With parameters alpha=0.005, sigma_ref=0.5, gamma_phi=0.05, D_core ≈ 0.8:
```
sigma_eq ≈ 0.5 * 0.005 / (0.005 + 0.04) ≈ 0.056
```
Deep depletion from sigma_ref=0.5 to sigma_eq≈0.056 — a factor of ~9 reduction.

**Depletion width:** The depletion is confined to the region where |Z_i| < 1, i.e.,
where neighbors have incoherent phases. This region has radius r_core ~ 1-2 lattice
spacings (the vortex plaquette and its immediate neighborhood). The sigma profile
outside r_core returns to sigma_ref with a Yukawa-screened tail.

---

## Sigma profile around the vortex

For the v5 equilibrium, the sigma profile is:
```
sigma(r) ≈ sigma_eq_core    for r < r_core   [depleted core]
sigma(r) ≈ sigma_ref        for r >> r_core  [returns to reference]
```

The transition region has a screened profile determined by the balance between:
- alpha (relaxation toward sigma_ref)
- beta (diffusion, smoothing the step)
- gamma_phi * D(r) (depletion, only where D > 0)

Since D(r) decreases away from the core (phases become ordered), the depletion
is self-confining. The core size r_core is set by the vortex structure.

---

## Impact on the matter stability program

With Channel F active:
1. Phi vortex creates a zone of phase disorder (vortex core, plaquette region)
2. Phase disorder drives sigma depletion: sigma_core << sigma_ref
3. The sigma deficit is PERMANENT (topologically protected by phi winding)
4. The sigma profile is Yukawa-screened outside the core

This completes the mechanism in DER-QNG-025 Section 3:
```
stable matter = topologically protected sigma deficit at phi vortex core
```

The a_M fixing condition (DER-QNG-025 §4) now applies:
```
a_M * kappa * A_vortex * C_K0 = m_particle / rho_0
```
where A_vortex = (sigma_ref - sigma_core) and C_K0 is the integral of K_0 over the
exterior. Both A_vortex and C_K0 can be extracted from the v5 simulation.

---

## Free parameter table

| Symbol       | Domain          | Physical meaning                                                  |
|--------------|-----------------|-------------------------------------------------------------------|
| `alpha`      | (0, 1)          | Self-relaxation rate toward reference state                       |
| `beta`       | (0, 1)          | Relational coupling strength to neighborhood mean                 |
| `gamma`      | (0, 1)          | History-channel coupling strength                                 |
| `delta`      | [0, 1)          | Cross-coupling: sigma deficit → chi tension (Channel D)           |
| `epsilon`    | ℝ               | Cross-coupling: chi tension → phase accumulation (Channel E)      |
| `gamma_phi`  | [0, ∞)          | Phase-coherence feedback: phase disorder → sigma depletion (new)  |
| `eta`        | [0, ∞)          | Fluctuation amplitude                                             |
| `sigma_ref`  | (0, 1)          | Native reference coherence amplitude                              |
| `alpha_M`    | (0, 1)          | Memory amplitude update rate                                      |
| `alpha_D`    | (0, 1)          | Mismatch accumulator update rate                                  |
| `alpha_P`    | (0, 1)          | Phase coherence update rate                                       |

**Total free parameters: 11.** One more than v4.

---

## Limiting cases

### Case 1: gamma_phi = 0 (v4 recovery)
```
Delta_phi_sigma = 0
```
Identical to v4. sigma_i is autonomous from phi.

### Case 2: gamma_phi > 0, no vortex (uniform phi)
|Z_i| = 1 everywhere → phase_disorder = 0 → Channel F has zero effect.
sigma dynamics identical to v4. Adding v5 to a vortex-free substrate changes nothing.

### Case 3: gamma_phi >> alpha (strong coupling)
sigma_eq_core → 0: complete suppression of coherence at vortex core.
The vortex core becomes a true "hole" in sigma.
This recovers the deep-depletion limit analogous to hard-core vortices in BEC.

### Case 4: gamma_phi → 0+ (weak coupling)
sigma_eq_core → sigma_ref * alpha / (alpha + gamma_phi * D_core) → sigma_ref (1 - gamma_phi * D_core / alpha)
Perturbative depletion: small but nonzero. Linear in gamma_phi.

---

## What remains open

1. The value of gamma_phi is not constrained by the coupling argument alone.
   It requires either: (a) matching to observed vortex core size, or (b) a
   variational derivation from the substrate free energy.

2. The sigma-phi coupling breaks the exact sigma-chi factorization used in the
   Newtonian limit derivation (DER-QNG-012 through DER-QNG-018). The Newtonian
   limit must be re-examined to confirm G_QNG is unchanged in the v5 bulk (far from
   vortices). Expected result: bulk dynamics unchanged (Channel F = 0 away from vortices).

3. The chi field now sees a sigma with spatial structure (vortex core depletion).
   Chi builds up near the vortex core where sigma_i < sigma_ref. This feeds back
   through Channel D (sigma deficit → chi tension) → consistent with DER-QNG-025.

4. The 2D test (QNG-CPU-042) verifies sigma depletion in 2D. The 3D case (QNG-CPU-043)
   is needed for vortex rings (pi_2(S^1) = 0 prevents point defects in 3D).

---

## Cross-references

- v4 law: `DER-QNG-016` (`qng-native-update-law-v4.md`)
- Matter stability: `DER-QNG-025` (`qng-matter-stability-v1.md`)
- Phi vortex topology test: `QNG-CPU-041`
- Sigma depletion at vortex core: `QNG-CPU-042` (proposed)
- 3D vortex ring: `QNG-CPU-043` (future)
