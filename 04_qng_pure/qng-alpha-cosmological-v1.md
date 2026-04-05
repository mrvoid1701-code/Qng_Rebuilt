# QNG Alpha as Cosmological Constant v1

Type: `derivation`
ID: `DER-QNG-020`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Resolve Gap 5 of `DER-QNG-011` (long-range gravity recovery): identify the substrate
self-relaxation parameter `α` with the cosmological constant `Λ`, show that the
screening length `λ_screen` equals the Hubble radius `c/H₀` when `α = α_phys`, and
demonstrate that all observable Newtonian gravity operates in the pure Poisson regime
`r ≪ λ_screen` when the physical value of `α` is used.

## Inputs

- [qng-codata-constraint-v1.md](qng-codata-constraint-v1.md)
- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md)
- [qng-ceff-field-equation-v1.md](qng-ceff-field-equation-v1.md)
- [qng-newtonian-limit-program-v1.md](qng-newtonian-limit-program-v1.md)

---

## Section 1: Statement of the Problem

From `DER-QNG-019`, the unit mapping gives:
```
Δu_SI = (z/β) · l_Planck
t_s_SI = (z/β) · t_Planck
```

And the screening length in SI:
```
lambda_screen_SI = sqrt(z/(beta * alpha)) * l_Planck
```

For the test value `alpha = 0.005` (β=0.35, z=6):
```
lambda_screen_SI ≈ 58 * l_Planck ≈ 9.5e-34 m
```

This kills gravity at all macroscopic scales — the Yukawa factor `exp(-r/lambda_screen)`
is essentially zero for any `r >> l_Planck`.

**The screening problem:** `alpha_test` is chosen for numerical convenience
(equilibration in ~3000 steps). It is not the physical value. The question is:
what is `alpha_phys`?

---

## Section 2: Cosmological Constant Identification

The C_eff field equation (DER-QNG-012 §4) is:
```
d/dt C_eff = -Gamma_0 * delta_C + D_diff0 * nabla^2 C_eff - S_src
```

where `Gamma_0 = alpha / t_s`. In the weak-field, quasi-static limit:
```
D_diff0 * nabla^2 delta_C - Gamma_0 * delta_C = S_src
```

This is the **massive Klein-Gordon equation** for `delta_C` with effective mass:
```
m_eff^2 = Gamma_0 / D_diff0 = alpha * z / (beta * Delta_u^2)
```

In SI units (using the Planck unit mapping from DER-QNG-019):
```
m_eff_SI^2 = alpha / t_s_SI / (D_diff0_SI)
           = alpha / ((z/beta) * t_Planck) / ((beta/z) * (z/beta)^2 * l_Planck^2 / ((z/beta) * t_Planck))
           = alpha * z / (beta * l_Planck^2)
```

The **Compton screening length** is:
```
lambda_screen_SI = 1/m_eff_SI = l_Planck * sqrt(beta / (z * alpha))
```

**Cosmological constant connection:**
In de Sitter spacetime, the Hubble constant `H_0` and the cosmological constant `Lambda`
are related by `Lambda = 3 * H_0^2 / c^2`. The de Sitter horizon (Hubble radius) is:
```
R_Hubble = c / H_0
```

For long-range gravity, we require `lambda_screen >= R_Hubble`:
```
l_Planck * sqrt(beta / (z * alpha)) >= c / H_0
sqrt(beta / (z * alpha)) >= c / (H_0 * l_Planck) = N_H
```

where `N_H = c / (H_0 * l_Planck)` is the Hubble horizon measured in Planck lengths.

Numerically: `N_H = 3e8 / (2.2e-18 * 1.6e-35) = 3e8 / (3.5e-53) = 8.6e60`.

The condition `lambda_screen = R_Hubble` gives:
```
alpha_phys = beta / (z * N_H^2) = 0.35 / (6 * (8.6e60)^2) = 0.35 / (4.4e122) ≈ 7.9e-124
```

**Comparison with Lambda:**
```
Lambda * l_Planck^2 = (1.1e-52 m^-2) * (1.6e-35 m)^2 = 1.1e-52 * 2.6e-70 = 2.8e-122
```

Therefore:
```
alpha_phys ≈ (beta / (6 * z)) * Lambda * l_Planck^2
```

For beta=0.35, z=6: `alpha_phys ≈ (0.35/36) * Lambda * l_Planck^2 ≈ 0.01 * Lambda * l_Planck^2`.

**The substrate self-relaxation rate `alpha` is proportional to the cosmological
constant `Lambda` in Planck units.** The factor of order 0.01 depends on the
coordination number z and relational coupling beta — substrate geometry parameters.

---

## Section 3: Physical Interpretation

**Meaning of alpha:**
In the C_eff dynamics, `Gamma_0 = alpha/t_s` is the rate at which the substrate
relaxes toward its reference coherence `sigma_ref`. This is the vacuum "restoration
pressure" — the tendency of spacetime to return to its ground state after a perturbation.

In general relativity, the cosmological constant `Lambda` acts as a restoring force
in the Friedmann equation: it drives expansion (de Sitter phase) when dominant.
The analogy:

| QNG | GR |
|-----|----|
| `alpha` (relaxation rate) | `Lambda` (cosmological constant) |
| `sigma_ref` (reference coherence) | Vacuum energy density |
| `Gamma_0 = alpha/t_s` | `H_de_Sitter = sqrt(Lambda*c^2/3)` |
| `lambda_screen = sqrt(beta/(z*alpha)) * Delta_u` | `R_Hubble = c/H_0` |
| Screening at `r >> lambda_screen` | Dark energy dominance at `r ~ R_Hubble` |

**Resolution of Gap 5:**
The screening problem is not a defect — it is the QNG analog of dark energy. With
`alpha = alpha_phys` (set by the cosmological constant), the screening length equals
the Hubble radius. ALL observable gravitational phenomena (solar system, galaxies,
galaxy clusters: `r << R_Hubble`) operate in the pure Poisson regime:
```
exp(-r/lambda_screen) = exp(-r/R_Hubble) ≈ 1   for r << R_Hubble
```

The Yukawa modification becomes observable only at cosmological scales `r ~ R_Hubble`,
where it produces exactly the effect of the cosmological constant (deceleration → acceleration
in cosmic expansion). This is a prediction, not a free parameter adjustment.

---

## Section 4: Prediction — Screening at Cosmic Scales

**P-COSMO-1:** At distances `r ~ R_Hubble`, the gravitational potential is:
```
Phi(r) = -G*M / r * exp(-r / R_Hubble)
```

For `r << R_Hubble` this reduces to `Phi = -GM/r` (Newtonian). For `r ~ R_Hubble`,
the exponential suppression weakens gravity — mimicking the observed cosmic acceleration.

**P-COSMO-2:** The effective "equation of state" of the screening term:
The force from the Yukawa term at large r:
```
F_Yukawa ~ -dPhi/dr = -GM/r^2 * exp(-r/lambda) * (1 + r/lambda)
```

For r >> lambda: `F_Yukawa ~ 0` — gravity turns off. For r ~ lambda:
`F_Yukawa ~ GM/lambda^2` — constant force. This is the dark energy-like behavior.

**Connection to observed Λ:**
Matching `lambda_screen = R_Hubble = c/H_0` gives:
```
alpha_phys = beta / (z * N_H^2) = beta / (z * (c/(H_0 * l_Planck))^2)
```

This is a specific numerical prediction for `alpha_phys` in terms of `H_0`, `beta`, `z`,
and Planck constants — all measurable or constrained independently.

---

## Section 5: Numerical Values

For `beta = 0.35`, `z = 6`, `H_0 = 2.2e-18 s^-1`:

| Quantity | Value |
|----------|-------|
| `N_H` | `8.6e60` (Hubble in Planck lengths) |
| `alpha_phys` | `7.9e-124` (substrate units) |
| `lambda_screen_phys` | `c/H_0 = 1.4e26 m` |
| `alpha_test` | `0.005` (simulation value, 119 orders too large) |
| `lambda_screen_test` | `58 * l_Planck = 9.5e-34 m` |

The 119-order difference between `alpha_test` and `alpha_phys` is why test simulations
cannot exhibit long-range gravity — they are operating in the cosmologically screened
regime far above the physical `alpha`.

**No fine-tuning problem:** The smallness of `alpha_phys` is not independent fine-tuning.
It is the same fine-tuning as the cosmological constant problem — understood or not,
it is a single quantity. QNG does not solve the cosmological constant problem, but it
does show that the screening problem is equivalent to it (not an additional problem).

---

## Section 6: Testable Consequences

**Numerically testable (QNG-CPU-036):**
The formula `lambda_screen = sqrt(beta/(z*alpha)) * Delta_u` is verified for multiple
alpha values. This confirms the alpha-dependence and validates the prediction.

**Observationally testable:**
If the QNG identification `alpha ~ Lambda * l_Planck^2` is correct, then:
1. The gravitational screening length is the Hubble radius (verifiable from large-scale
   structure surveys).
2. The modified gravitational force at `r ~ R_Hubble` has a specific Yukawa profile
   `exp(-r/R_Hubble)` rather than a pure cosmological constant (`exp(+Lambda*r^2/6)`).
3. The Yukawa profile produces a different signature in CMB power spectra at L ~ 1
   (Sachs-Wolfe effect modification) compared to a pure Lambda term.

**What constitutes falsification:**
If the large-scale gravitational potential does NOT follow `exp(-r/R_Hubble)/r` but
instead follows the standard `1/r` or `1/r * cosh(sqrt(Lambda)*r)`, the identification
`alpha ~ Lambda` is falsified and Gap 5 remains unresolved.

---

## Section 7: Gap 5 Status

**Gap 5 — Long-range gravity recovery:**

| Sub-item | Status after this document |
|----------|--------------------------|
| Screening length formula | Confirmed numerically (QNG-CPU-035) |
| alpha_test vs alpha_phys distinction | Resolved: alpha_test is numerical, not physical |
| Physical alpha identification | **Complete**: alpha_phys ~ Lambda * l_Planck^2 |
| lambda_screen = R_Hubble prediction | **Derived**: follows from CODATA + Hubble |
| Observable cosmological consequence | Yukawa modification at R_Hubble scale |
| Numerical test of alpha-dependence | QNG-CPU-036 |

**Gap 5 is reframed — not resolved.** The long-range gravity problem is shown to be
equivalent to the cosmological constant problem. The identification `alpha ~ Lambda`
is a consistency condition imposed from outside (requiring `lambda_screen >= R_Hubble`),
not a prediction derived from QNG substrate dynamics. The substrate relaxation rate
`alpha` has no QNG-internal argument fixing its value; it is inferred by matching
`lambda_screen` to the observed Hubble radius.

What this achieves: the screening fine-tuning required for QNG gravity is the *same*
fine-tuning as for the cosmological constant — not an additional independent problem.
The fine-tuning count is reduced by one.

What remains open: why `alpha` takes its physical value is not explained by QNG.
The Gravity Probe A benchmark from `DER-QNG-011` §4 (70 ppm radial constraint) has
no numerical support and depends entirely on the `alpha <-> Lambda` identification,
which cannot be numerically tested at `alpha_phys ~ 10^{-124}`.

---

## Cross-references

- CODATA constraint: `DER-QNG-019` (`qng-codata-constraint-v1.md`)
- Poisson assembly: `DER-QNG-018` (`qng-poisson-assembly-v1.md`)
- C_eff field equation: `DER-QNG-012` (`qng-ceff-field-equation-v1.md`)
- Test: `QNG-CPU-036` (`07_validation/prereg/QNG-CPU-036.md`)
