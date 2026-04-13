# QNG v7 Newton Constant Reconciliation

Type: `derivation`
ID: `DER-QNG-037`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-13`

## Objective

Two formulas for Newton's constant appear in the QNG literature:

```
(F1)  G_QNG = beta_g / z                    [single-sigma, DER-QNG-018]
(F2)  G_eff = k_gm / (z × alpha_g)         [v7 two-field cascade, DER-QNG-035]
```

Both are derived from first principles within QNG. They cannot both be independently
true unless there is a constraint between k_gm, beta_g, and alpha_g. This derivation:

1. Identifies the physical regime in which each formula applies.
2. Derives the consistency condition that makes them equal.
3. Determines the physical value of k_gm implied by G_Newton matching.
4. Revises the C1 unit constraint for the v7 two-field substrate.

## Inputs

- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md) — DER-QNG-018: G_QNG = beta/z
- [qng-double-yukawa-derivation-v1.md](qng-double-yukawa-derivation-v1.md) — DER-QNG-035: G_eff = k_gm/(z×alpha_g)
- [qng-hamiltonian-v7-two-field-v1.md](qng-hamiltonian-v7-two-field-v1.md) — DER-QNG-036: v7 Hamiltonian, unit system
- [qng-codata-constraint-v1.md](qng-codata-constraint-v1.md) — DER-QNG-019: CODATA matching

---

## Section 1: Derivation of each formula — regime conditions

### 1.1 Formula F1: G_QNG = beta_g / z

**Derivation (DER-QNG-018):** From the screened Poisson equation for delta_sigma_g:

```
(-alpha_g + beta_g × ∇²) delta_sigma_g = S_src
```

In the quasi-static, r << lambda_screen limit, the Yukawa Green's function gives:

```
Phi(r) ∝ -(pi×z/beta_g) × delta_sigma_g(r)
       ∝ G_QNG × M / r   where   G_QNG = beta_g / z
```

**Regime conditions for F1:**
- sigma_m IS sigma_g (single-sigma, or matter = gravity field directly)
- OR: sigma_g is sourced directly at the matter location (no K_GM cascade)
- K_GM = 0 (no two-field coupling)
- Quasi-static: K_BACK × chi << alpha_g × delta_sigma_g (chi term negligible)

**F1 is the "bare" gravitational coupling** — Newton's constant of the sigma_g field
with itself when it IS the matter source.

### 1.2 Formula F2: G_eff = k_gm / (z × alpha_g)

**Derivation (DER-QNG-035):** In v7, matter (sigma_m) sources gravity (sigma_g)
through the cascade:

```
(-alpha_m + beta_m × ∇²) delta_sigma_m = source_m(r)        [matter equation]
(-alpha_g + beta_g × ∇²) delta_sigma_g = K_GM × delta_sigma_m [gravity equation]
```

The second equation is sourced by the solution to the first. This gives a double-Yukawa
convolution. For equal screening lengths (alpha_g = alpha_m, lambda_g = lambda_m = lambda):

```
Phi(r) ∝ K_GM / BETA² × (Y * Y)(r) × source_m_total
```

where Y(r) = exp(-r/lambda)/(4×pi×r) and (Y * Y)(r) is the self-convolution.

The effective G in the point-source limit (r >> lambda):
```
G_eff = K_GM × lambda² / BETA = K_GM × (BETA/(z×ALPHA)) / BETA = K_GM / (z × ALPHA_g)
```

**Regime conditions for F2:**
- sigma_m and sigma_g are distinct fields (v7 two-field substrate)
- K_GM > 0 (two-field coupling active)
- Quasi-static: chi quasi-static (K_BACK × DELTA << ALPHA_g × CHI_DECAY, from DER-QNG-035)
- r >> lambda_g AND r >> lambda_m (far field, both Yukawa screenings resolved)

**F2 is the "cascade" gravitational coupling** — Newton's constant as seen by a
test particle sourcing sigma_m, which then sources sigma_g at a distance.

---

## Section 2: Consistency condition

For QNG to have a unique Newton's constant in both regimes:

```
G_QNG = G_eff
beta_g / z = k_gm / (z × alpha_g)
```

Solving:
```
k_gm_phys = beta_g × alpha_g             [CONSISTENCY CONDITION — CC]
```

**Physical interpretation:** The two-field coupling K_GM must equal the product of the
gravitational diffusion rate (beta_g) and the self-relaxation rate (alpha_g).

Numerically (beta_g = 0.35, alpha_g = alpha_test = 0.005):
```
k_gm_consistent = 0.35 × 0.005 = 0.00175   [substrate units, test parameters]
```

For the physical alpha:
```
k_gm_phys = beta_g × alpha_phys = 0.35 × 7.9×10^{-124} ≈ 2.8×10^{-124}
```

This is an astronomically small coupling — consistent with the extreme weakness of
gravity relative to other forces.

**Ratio of test k_gm to consistent value:**
In current simulations we use k_gm = 0.001 to 0.050. The consistent value at test
alpha is k_gm = 0.00175. Simulations with k_gm >> 0.00175 amplify G_eff beyond
G_QNG by a factor k_gm/(beta_g×alpha_g).

| k_gm (test) | G_eff/G_QNG | Physical meaning |
|-------------|-------------|-----------------|
| 0.00175 | 1.000× | Consistent, physical G |
| 0.001   | 0.571× | Sub-G (gravity weakened) |
| 0.005   | 2.857× | 2.9× enhanced G |
| 0.010   | 5.714× | 5.7× enhanced G |
| 0.050   | 28.57× | 28.6× enhanced G (CPU-073) |

---

## Section 3: Revised C1 unit constraint for v7

The CODATA matching in DER-QNG-019/032 used F1 (G_QNG = beta_g/z):
```
G_Newton_SI = G_QNG × a^3 / (m_u × tau^2)
            = (beta_g/z) × a^3 / (m_u × tau^2)
```

In v7 with the two-field cascade, the relevant G is G_eff (not G_QNG).
Under the consistency condition CC (k_gm = beta_g × alpha_g):
```
G_eff = k_gm / (z × alpha_g) = beta_g × alpha_g / (z × alpha_g) = beta_g / z = G_QNG ✓
```

So **when CC holds, F1 and F2 agree and the C1 constraint is unchanged:**
```
m_u × tau^2 = (beta_g/z) / G_Newton_SI × a^3 = 8.74×10^8 × a^3   [substrate units]
```

When CC is NOT enforced (k_gm ≠ beta_g × alpha_g), the C1 constraint becomes:
```
m_u × tau^2 = (k_gm/(z×alpha_g)) / G_Newton_SI × a^3
```

This CHANGES the lattice spacing `a` for a given `m_u`. For k_gm = 0.050 (CPU-073):
```
G_eff/G_QNG = 28.6×
a = a_F1 / sqrt(28.6) ≈ a_F1 / 5.35
```

The lattice spacing is 5.35× smaller when k_gm = 0.050. This is the price of
amplifying gravity in test simulations — the effective lattice is more sub-Planckian.

---

## Section 4: Physical prediction — k_gm from G_Newton

Setting G_eff = G_Newton in physical units and using CC:

```
k_gm_phys = beta_g × alpha_phys

alpha_phys ≈ 7.9×10^{-124}   [from DER-QNG-020: alpha_phys ~ Lambda × l_Planck^2]
beta_g     = 0.35             [fixed by G_QNG = beta_g/z and CODATA]

k_gm_phys ≈ 0.35 × 7.9×10^{-124} ≈ 2.8×10^{-124}
```

This is the v7 analog of the cosmological constant fine-tuning: k_gm_phys is tiny
because alpha_phys is tiny (lambda_screen = R_Hubble). It is NOT an additional
fine-tuning — it follows from CC once alpha_phys is fixed.

**The k_gm fine-tuning problem reduces to the alpha fine-tuning problem.**
Both are manifestations of the cosmological constant problem (Gap 5).

---

## Section 5: Formula applicability table

| Quantity | Formula F1 (single-sigma) | Formula F2 (v7 cascade) | Which to use |
|----------|--------------------------|------------------------|-------------|
| Newton's constant | beta_g/z | k_gm/(z×alpha_g) | Both equal when CC holds |
| Gravitational source | sigma_g directly | sigma_m → sigma_g via K_GM | F2 for physical rings |
| Potential profile | Yukawa exp(-r/lambda)/r | Double-Yukawa (DER-QNG-035) | F2 for v7 |
| C1 constraint (m_u) | unchanged (beta_g/z) | unchanged IF CC holds | CC must be imposed |
| Screening length | sqrt(beta_g/(z×alpha_g)) | two lengths: lambda_g, lambda_m | F2 if lambda_g≠lambda_m |
| Valid regime | K_GM=0 or single sigma | K_GM > 0, far field | F2 for all v7 physics |

---

## Section 6: Implications for the mass identification program (Pas 4)

The canonical mass formula from DER-QNG-036 §6 is:
```
m_particle = a_M × m_u × M_ring(R)
```

where m_u is fixed by C1 + C3. Under CC (k_gm = beta_g × alpha_g):
- G_eff = G_QNG → C1 gives m_u × tau^2 = 8.74×10^8 × a^3 (unchanged)
- C3 gives tau/a = sqrt(k_back × beta_g / 6) / c (unchanged)
- Therefore m_u = 1.498×10^{-9} × a × c^2 / k_back (unchanged from DER-QNG-036)

For the mass identification, the canonical M_ring values (from QNG-CPU-074, T_P2=1000):
```
M_ring(R=3) = 474.2   [substrate units]
M_ring(R=4) = 728.9   [substrate units]
M_ring(R=5) = 954.9   [substrate units, matches CPU-067]
```

The identification m_particle = a_M × m_u × M_ring gives:
```
a_M = m_particle / (m_u × M_ring)
```

For m_particle = m_proton, R=4 (the standard ring), m_u = m_proton (k_back=1 convention):
```
a_M = 1 / M_ring(R=4) = 1 / 728.9 ≈ 1.37×10^{-3}
```

This determines a_M from first principles given a choice of ring radius.
The remaining freedom is which physical particle corresponds to which R.

---

## Section 7: Summary

| Result | Status |
|--------|--------|
| F1 (G_QNG = beta_g/z) derived in single-sigma quasi-static limit | ESTABLISHED ✓ |
| F2 (G_eff = k_gm/(z×alpha_g)) derived in v7 far-field limit | ESTABLISHED ✓ |
| Consistency condition: k_gm = beta_g × alpha_g | DERIVED ✓ |
| k_gm_phys = beta_g × alpha_phys ≈ 2.8×10^{-124} | COMPUTED ✓ |
| k_gm fine-tuning = alpha fine-tuning (Gap 5) | IDENTIFIED ✓ |
| C1 constraint unchanged when CC holds | DERIVED ✓ |
| Canonical M_ring values (CPU-074) for mass identification | ESTABLISHED ✓ |
| Physical particle-to-ring-radius identification | OPEN (Pas 4) |

---

## Cross-references

- DER-QNG-018: G_QNG = beta/z (single-sigma Poisson equation)
- DER-QNG-019: CODATA constraint, unit system
- DER-QNG-020: alpha_phys ~ Lambda × l_Planck^2 (Gap 5)
- DER-QNG-035: double-Yukawa, G_eff = k_gm/(z×alpha_g)
- DER-QNG-036: v7 Hamiltonian, C1+C3 unit system
- QNG-CPU-074: canonical M_ring(R) at T_P2=1000
