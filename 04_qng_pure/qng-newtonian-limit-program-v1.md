# QNG Newtonian Limit Derivation Program v1

Type: `derivation`
ID: `DER-QNG-011`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Set up the complete derivation program by which QNG must recover the Newtonian inverse-square law from its native substrate dynamics.

This is a program document. It states the target, defines the approximation ladder, identifies the functional form of Newton's constant G in terms of QNG substrate parameters, records the experimental benchmarks the derivation must reproduce, and states explicitly what remains open.

The Newtonian limit is the single most critical theoretical closure for QNG. A referee at PRD or CQG will ask this question first. This document makes the question precise enough that the answer can be pursued step by step.

## Inputs

- [qng-primitives-v1.md](qng-primitives-v1.md)
- [qng-native-update-law-v1.md](qng-native-update-law-v1.md)
- [qng-native-update-law-v2.md](qng-native-update-law-v2.md)
- [qng-emergent-field-v1.md](qng-emergent-field-v1.md)
- [qng-geometry-estimator-v1.md](qng-geometry-estimator-v1.md)
- [qng-emergent-geometry-v1.md](qng-emergent-geometry-v1.md)
- [qng-lorentzian-signature-proxy-v1.md](qng-lorentzian-signature-proxy-v1.md)
- [qng-lorentzian-4d-resolution-v1.md](qng-lorentzian-4d-resolution-v1.md)

## Scope

This document operates at Regime B (weak-field GR) and Regime C (observational proxy layer). It does not make exact GR claims. It does not import observational data. Every small parameter is defined in terms of substrate quantities.

---

## Section 1: The Target

The Newtonian limit target is:

```
nabla^2 phi(x) = 4 pi G rho(x)
```

where `phi` is the Newtonian gravitational potential, `rho` is the local mass density, `G` is Newton's gravitational constant, and `nabla^2` is the Laplacian on flat three-dimensional space.

In QNG terms, the potential proxy already defined in the GR bridge layer is:

```
Psi_QNG(i) = h_00(i) / 2
```

where `h_00(i) = g_00(i) - 1` is the lapse perturbation from the geometry estimator. The acceleration proxy is:

```
a_QNG(i) = - grad(Psi_QNG)(i)
```

The Newtonian limit is achieved when, in the appropriate limit (Section 2), the equation governing `Psi_QNG` becomes:

```
lap(Psi_QNG)(i)  -->  4 pi G_QNG rho_eff(i)
```

where `lap` is the discrete graph Laplacian converging to the continuum Laplacian, `G_QNG` is Newton's constant expressed in QNG substrate parameters (Section 3), and `rho_eff` is the effective mass-density proxy from the matter sector.

This target is not imposed by hand. It must emerge from the QNG equation stack without additional postulates.

---

## Section 2: The Approximation Ladder

Four successive approximations are required, each controlled by a named small parameter.

### Approximation 1: Large-N Continuum Limit

The discrete graph `G(t)` with `N` nodes admits a continuum approximation when node spacing `Delta_u -> 0` with physical volume fixed.

**Small parameter:** `epsilon_1 = ell_Planck / L_phys`

**Output:** Discrete sums over neighbors become continuum integrals. The effective fields `C_eff(i)` and `L_eff(i)` become smooth functions `C_eff(x)` and `L_eff(x)`. The discrete Laplacian converges to `nabla^2`.

**Open condition:** The graph must be sufficiently regular (locally approximately isotropic in 3D) for the continuum Laplacian to be recovered without large anisotropy corrections. This is Gap 1 (Section 5).

### Approximation 2: Slow Variation (Quasi-Static)

Source distributions evolve slowly compared to the substrate propagation timescale.

**Small parameter:** `epsilon_2 = (v_source / c_substrate)^2`

where `c_substrate` is the effective propagation speed of disturbances in the QNG substrate — not assumed to equal `c` a priori.

**Output:** Time derivatives of `C_eff` and `L_eff` are dropped at leading order. The field equation reduces from hyperbolic to elliptic (Poisson type).

### Approximation 3: Weak Field

The geometry estimator is close to its flat-background value:

**Small parameter:** `epsilon_3 = max_i { |h_00(i)|, |h_11(i)| }`

**Output:** The geometry estimator equation is linearized around the flat background. The linearized equation is Poisson type in the quasi-static limit.

**Connection to existing work:** The weak-field proxy observables `h_00`, `h_11`, `Psi_QNG`, `a_QNG` already live at this approximation level. The Newtonian limit derivation produces a closed equation for `Psi_QNG` rather than merely defining it as a proxy.

### Approximation 4: Low Memory

The history correction channel is treated as a small perturbation to the relational coupling.

**Small parameter:** `epsilon_4 = k_hist / k_rel`

**Output:** The effective field equation retains a leading term controlled by `k_rel` and a subleading memory correction. At leading order the equation is the standard Poisson equation. The memory correction at order `epsilon_4` is the first QNG-specific departure from classical Newtonian gravity.

**Note:** The full QNG theory does not require `epsilon_4 << 1`. The low-memory limit is invoked only to isolate the Newtonian regime. The regime `epsilon_4 ~ 1` or larger may produce observable deviations — this is a separate prediction program.

### Summary

| Step | Name | Small parameter | Effect |
|------|------|-----------------|--------|
| 1 | Large-N continuum | `epsilon_1 = ell_Planck / L_phys` | Discrete → continuum |
| 2 | Slow variation | `epsilon_2 = (v / c_substrate)^2` | Wave eq → Poisson eq |
| 3 | Weak field | `epsilon_3 = max |h_mu nu|` | Nonlinear → linearized |
| 4 | Low memory | `epsilon_4 = k_hist / k_rel` | Full QNG → classical limit |

The Newtonian limit is the simultaneous limit `epsilon_1, epsilon_2, epsilon_3, epsilon_4 -> 0`. Their order of application and mutual consistency must be verified explicitly as part of the derivation.

---

## Section 3: The Functional Form of Newton's Constant

Newton's constant G is not an input to QNG. It must emerge as an output of the substrate dynamics.

### QNG substrate parameters available

From the native update law v2 (`DER-QNG-010`): `alpha`, `beta`, `gamma`, `eta`, `sigma_ref`, `alpha_M`, `alpha_D`, `alpha_P`

From the effective field layer: `a_sigma`, `a_D`, `a_P` (coherence weights), `b_M`, `b_chi` (memory-load weights)

From the geometry estimator: `a`, `b`, `c` (metric coefficients)

From the Lorentzian signature proxy: `lambda`, `nu`

Graph structural parameters: `z` (mean node degree), `Delta_u` (node spacing), `t_substrate` (native update timestep)

### Structural form

At the program level, the functional form of `G_QNG` is:

```
G_QNG = f(beta, gamma, z, ell, Delta_u, t_substrate, a, b, c, a_sigma, a_D, a_P)
```

Dimensional analysis constrains the form. In three spatial dimensions, `[G] = length^3 / (mass * time^2)`. The substrate produces this from:

**Geometric factor:** The continuum Laplacian emerges from the graph topology with a prefactor depending on `z` and `Delta_u`. The discrete second-difference carries a factor `1/Delta_u^2` absorbed into the physical length scale in the continuum limit.

**Coupling factor:** At leading order in the weak-field and low-memory limits:

```
G_QNG ~ (beta / z) * (Delta_u^3 / t_substrate)^2 * F(a, b, c, a_sigma, a_D, a_P)
```

where `F` is a dimensionless function of the geometry estimator and coherence field coefficients encoding how strongly curvature of the coherence field responds to local density.

**History correction:** At order `epsilon_4 = gamma / beta`:

```
G_QNG(full) = G_QNG(0) * ( 1 + alpha_hist * epsilon_4 + O(epsilon_4^2) )
```

where `alpha_hist` is determined by the structure of `U_hist`. Its sign determines whether memory strengthens or weakens the effective gravitational coupling at subleading order.

### Physical meaning

G is not free in QNG. Its numerical value is fixed once `Delta_u`, `t_substrate`, `beta`, `z`, and `a, b, c` are determined. These must be constrained by requiring the output to match the measured value of G — a constraint equation, not a free choice. The exact coefficients in `G_QNG` must be computed by completing the derivation in Section 2.

---

## Section 4: Experimental Benchmarks

The derivation must reproduce or be consistent with the following measurements.

| Measurement | Value | Precision | Physical content |
|-------------|-------|-----------|-----------------|
| CODATA G (2018) | `6.674 × 10⁻¹¹ m³ kg⁻¹ s⁻²` | 22 ppm | Absolute value of gravitational coupling |
| Pound-Rebka (1959) | `Δν/ν = gh/c²` | ~1% | Existence of gravitational redshift |
| Gravity Probe A (1976) | `Δν/ν = (GM/c²)(1/r₁ - 1/r₂)` | 70 ppm | Radial dependence of weak-field potential |

**CODATA G:** The combination of QNG substrate parameters in `G_QNG` must equal this number within 22 ppm when the substrate is identified with physical spacetime.

**Pound-Rebka:** Requires `Psi_QNG(x+h) - Psi_QNG(x) = gh + O((gh/c²)²)` — linear potential profile in the near-field regime of a static spherically symmetric source.

**Gravity Probe A:** Tighter constraint. Requires `Psi_QNG ~ -GM/r` for a point source to 70 ppm across altitudes from Earth's surface to 10,000 km — i.e., the Poisson equation must hold with correct radial profile, not merely correct overall scale.

Meeting Gravity Probe A (not just CODATA) is what establishes that QNG recovers the correct shape of the Newtonian potential, not merely its normalization.

---

## Section 5: Open Gaps

### Gap 1 — Graph isotropy in 3+1 dimensions

**Status: unresolved.**

The current toy implementations use a 1D ordered cycle. The Newtonian limit requires a 3D isotropic Laplacian. A sufficient condition on the graph ensemble for isotropic 3D continuum Laplacian recovery must be stated and verified. Whether QNG graph dynamics preserves this condition dynamically or requires it as an initial condition is open.

**Next step:** State a sufficient condition on `G(t)` under which the discrete Laplacian recovers `nabla^2_3D` isotropically.

### Gap 2 — Effective field equation for C_eff

**Status: unresolved. This is the most urgent gap.**

The geometry estimator `g_ref(i)` is defined from `C_eff` by a geometric formula. But the equation of motion that `C_eff` obeys — the PDE governing its dynamics — is not written down in closed form anywhere in the repository.

The Poisson equation for `Psi_QNG` can only be derived once there is a closed equation for `C_eff`. Without it, the relation between `lap(Psi_QNG)` and `rho_eff` cannot be established.

**Next step:** Derive the leading-order effective field equation for `C_eff(x)` from the coarse-grained native update law in the simultaneous limit `epsilon_1, epsilon_2, epsilon_3 -> 0`. This is Step N2 in Section 6 and the most concrete next derivation in the entire program.

### Gap 3 — Matter sector identification

**Status: closed in Newtonian limit (`DER-QNG-013` + `DER-QNG-014`).**

With the generation order cross-coupling `δ > 0` (v3 law, `DER-QNG-015`), in the simultaneous limit `(ε₁, ε₂, ε₃, ε₄) → 0`, `L_eff ≈ -(δ/α)·δ_C` and `M_eff ≈ -κ_eff·δ_C`. The identification `ρ_eff = ρ₀·M_eff/Δu³` is a derived consequence in this limit, not a declared bridge. Two unknowns remain unconstrained jointly: `(δ, ρ₀)` — one equation from CODATA G (Step N7) constrains their product; a second independent constraint is required to fix them separately.

**Next step:** Step N6 (Poisson assembly) is ready. Step N7 (CODATA constraint) gives one relation on `(δ, ρ₀)`. A second constraint from QM-facing or from a quasi-static source test is needed to resolve the degeneracy.

### Gap 4 — Numerical value of G_QNG

**Status: not computed.**

The structural form `G_QNG = (beta/z) * (Delta_u^3/t_substrate)^2 * F(...)` is stated. The explicit formula with numerical prefactors has not been computed. Computing it requires completing Gap 2 first.

**Next step:** Once Gap 2 is resolved, extract the coefficient in front of `nabla^2 Psi_QNG` and equate to `4 pi G_QNG` to obtain the explicit formula. Use CODATA to constrain the parameter combination.

### Gap 5 — Continuum limit validity range

**Status: not analyzed.**

It has not been established whether the QNG substrate dynamics admits a parameter regime where all four `epsilon_i` are simultaneously small and physically achievable.

**Next step:** Identify the range of `(beta, gamma, z, Delta_u)` for which the four-parameter limit is jointly achievable. If this range is empty, the update law requires revision.

### Gap 6 — Inherited proxy status of the signature sector

**Status: documented (see `qng-lorentzian-4d-resolution-v1.md`).**

The temporal slot entering `h_00` and therefore `Psi_QNG` is currently defined through the 2×2 Lorentzian signature proxy. The full derivation in 3+1D requires a 4×4 metric. This gap is inherited from the signature sector and must be closed jointly with Gaps 1 and 2.

---

## Section 6: Derivation Sequence

Minimal ordered steps from QNG substrate to the Poisson equation:

```
Step N1: Graph isotropy condition
  Input:  QNG graph ensemble G(t), native update law v2
  Output: sufficient condition for isotropic 3D continuum Laplacian recovery
  Closes: Gap 1

Step N2: Effective field equation for C_eff in 3D         ← NEXT STEP
  Input:  native update law v2, coarse-graining rule, epsilon_1 -> 0
  Output: closed PDE for C_eff(x, t) in 3D
  Depends on: Step N1

Step N3: Quasi-static reduction
  Input:  C_eff PDE from N2, epsilon_2 -> 0
  Output: elliptic equation for C_eff(x) in the static limit

Step N4: Weak-field linearization
  Input:  geometry estimator formula, C_eff equation from N3, epsilon_3 -> 0
  Output: linearized equation for Psi_QNG(x)

Step N5: Source identification
  Input:  M_eff, S_src from matter sector
  Output: explicit rho_eff(x) = f_matter(M_eff, S_src)
  Closes: Gap 3

Step N6: Poisson equation assembly
  Input:  Steps N4 and N5
  Output: nabla^2 Psi_QNG = 4 pi G_QNG rho_eff  with explicit G_QNG formula
  This is the primary closure step.

Step N7: Benchmark matching
  Input:  G_QNG formula, CODATA value, Gravity Probe A constraint
  Output: constraint on substrate parameter combination
```

**The next concrete step is N2.** Derive the continuum effective field equation for `C_eff` from the coarse-grained native update law v2 by applying the coarse-graining map from `qng-emergent-field-v1.md` at scale `ell`, then taking `epsilon_1 -> 0`.

---

## Section 7: Current Repository State

| Stage | Description | Status |
|-------|-------------|--------|
| GR-R1 | Linearized metric assembly (`h_00`, `h_11`, `Psi_QNG` defined) | Proxy-level complete |
| GR-R2 | Linearized curvature consistency (`R_lin` defined and tested) | Proxy-level complete |
| GR-R3 | Source-side closure (scalar source matching ansatz) | Proxy-level, partial |
| N1 | Graph isotropy condition | **Open — Gap 1** |
| N2 | C_eff field equation (reaction-diffusion PDE) | **Complete** — `DER-QNG-012` |
| N3 | Quasi-static reduction (screened Poisson) | **Complete** — `DER-QNG-012` §5 |
| N4 | Weak-field linearization + Φ_C convention | **Complete** — `DER-QNG-012` §6 |
| N5 | Source identification | **Closed in Newtonian limit** — `DER-QNG-013` + `DER-QNG-014` |
| N6 | Poisson equation assembly | **Ready to execute** — pending geometry estimator convention |
| N7 | Benchmark matching (CODATA, Gravity Probe A) | Not started — requires N6 + second constraint on (δ, ρ₀) |

The Newtonian limit program begins where GR-R3 ends — converting the proxy-level scalar source matching into a closed field equation and extracting the Poisson equation from it.

---

## What Counts as Success

The program is successfully completed when:

1. A closed elliptic equation for `Psi_QNG(x)` is derived in the limit `(epsilon_1, epsilon_2, epsilon_3, epsilon_4) -> 0`.
2. The right-hand side is proportional to a well-defined effective density `rho_eff(x)`.
3. The proportionality constant is identified as `4 pi G_QNG` with an explicit formula for `G_QNG`.
4. The formula admits a parameter choice consistent with the CODATA value to within the stated precision.
5. The same parameter choice is consistent with the Gravity Probe A radial constraint.

Condition 5 is required in addition to 4. Agreement on overall scale without correct radial profile is not sufficient.

## What Counts as Failure

The program fails if:

- the quasi-static limit does not produce an elliptic equation
- `rho_eff` cannot be expressed in QNG matter-sector variables without new free parameters
- `G_QNG` vanishes or diverges for all substrate parameter values
- the parameter range required to match G is incompatible with `epsilon_3 << 1`

Each failure mode is informative: it identifies the structural feature of the update law or geometry estimator that blocks Newtonian recovery and pinpoints what must be revised.
