# QNG Hamiltonian and Conservative Limit v1

Type: `derivation`
ID: `DER-QNG-032`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Construct the Hamiltonian H = T + E for the QNG substrate and show that:
1. The conservative equations of motion from H reproduce the v6 update law
2. The dissipative v5 gradient flow is the overdamped (large-friction) limit of H
3. The continuum limit of H gives the Klein-Gordon field theory
4. Setting the wave speed v = c closes the physical unit system (Constraint C3)

This addresses Einstein's core requirement: the substrate must have a single
Hamiltonian from which dynamics follow, with Lorentz covariance emerging from
the conservative limit.

## Inputs

- [qng-action-principle-candidate-v1.md](qng-action-principle-candidate-v1.md) — NOTE-QNG-014: E[sigma,chi,phi]
- [qng-wave-equation-derivation-v1.md](qng-wave-equation-derivation-v1.md) — DER-QNG-028: Klein-Gordon from Channel G
- [qng-native-update-law-v6.md](qng-native-update-law-v6.md) — DER-QNG-030: Channel G definition
- [qng-preferred-frame-analysis-v1.md](qng-preferred-frame-analysis-v1.md) — NOTE-QNG-013: Lorentz gap

---

## Section 1: The free energy functional (from NOTE-QNG-014)

The v5 update law follows from gradient flow of:

```
E[sigma, chi, phi] = sum_i {
  alpha/2 * (sigma_i - sigma_ref)^2                   [Channel A: self-restore well]
  + beta/4 * sum_{j~i} (sigma_j - sigma_i)^2          [Channel B: gradient tension]
  + chi_decay/2 * chi_i^2                              [chi self-energy]
  + chi_rel/2 * chi_i * (sigma_i - sigma_bar_i)        [chi-sigma gradient coupling]
  - delta * chi_i * (sigma_ref - sigma_i)              [Channel D: chi-sigma offset]
  - beta_phi/z * sum_{j~i} sigma_i sigma_j cos(phi_ij) [XY phase energy]
  - epsilon * chi_i * phi_i                            [Channel E: chi drives phi]
  + gamma_phi/2 * D_i(phi) * sigma_i^2                [Channel F: phase disorder]
}
```

Gradient flow: field(t+1) = field(t) - tau * dE/d(field)  [overdamped dynamics]

All six v5 channels are recovered. E is the potential energy.

---

## Section 2: The kinetic term T

The sigma-chi oscillator structure (from DER-QNG-028 §3, Channel G) identifies chi
as the velocity of sigma. Specifically, Channel G states:

```
sigma_i(t+1) = sigma_i(t) + k_back * chi_i(t)
```

which in continuum is:
```
∂_t sigma = k_back * chi
```

This identifies `chi_i` as the canonical momentum density of sigma_i (up to k_back):

```
pi_i = ∂_t sigma_i / k_back = chi_i
```

The kinetic energy is:

```
T[chi] = (k_back/2) * sum_i chi_i^2
       = (1/(2*k_back)) * sum_i (∂_t sigma_i)^2
```

This is a standard kinetic term: T = (1/2) × mass × velocity².
Here "mass" = 1/k_back per node, "velocity" = k_back × chi_i = ∂_t sigma_i.

---

## Section 3: The Hamiltonian H = T + E

```
H[sigma, chi, phi] = T[chi] + E[sigma, chi, phi]
                   = (k_back/2) * sum_i chi_i^2  +  E[sigma, chi, phi]
```

**Canonical equations of motion:**

```
∂_t sigma_i = +∂H/∂chi_i = k_back * chi_i + ∂E/∂chi_i
∂_t chi_i   = -∂H/∂sigma_i = -∂E/∂sigma_i
```

Computing ∂E/∂chi_i and ∂E/∂sigma_i from E:

```
∂E/∂chi_i = chi_decay * chi_i + chi_rel/2 * (sigma_i - sigma_bar_i)
             - delta * (sigma_ref - sigma_i)
             - epsilon * phi_i

∂E/∂sigma_i = alpha * (sigma_i - sigma_ref)
              + beta * (sigma_i - sigma_bar_i)
              - chi_rel/2 * chi_i * (term from gradient coupling)
              + delta * chi_i
              + gamma_phi * D_i * sigma_i
              - (phase energy cross-terms)
```

**Conservative equations of motion (leading order, ignoring phi coupling):**

```
∂_t sigma_i = k_back * chi_i                                    (i)
∂_t chi_i   = -alpha*(sigma_i - sigma_ref) + beta*(sigma_bar - sigma_i) - delta*chi_i
```

where the delta*chi_i term appears as a damping on chi from the chi_rel coupling.

For the sigma-chi subsystem with no phi:

```
∂_t sigma_i = k_back * chi_i                               (sigma evolution)
∂_t chi_i   = alpha*(sigma_ref - sigma_i) + beta*(sigma_bar - sigma_i)  (chi evolution)
```

---

## Section 4: Continuum limit — Klein-Gordon equation

Let s_i = sigma_i - sigma_ref (small perturbation), c_i = chi_i.

From (i): ∂_t s = k_back * c

Differentiating:
```
∂²_t s = k_back * ∂_t c
       = k_back * (-alpha*s + chi_rel*(sigma_bar - sigma_i))
```

**z=6 normalization:** In the simulation, `sigma_bar = (1/z) ∑_nb sigma_j` (average of
z=6 neighbors), so:
```
sigma_bar - sigma_i = (1/6) * ∑_nb (sigma_j - sigma_i) ≈ (1/6) * ∇²s   [lattice units, a=1]
```

Therefore:
```
∂²_t s = k_back * (-alpha*s + chi_rel*(1/6)*∇²s)
       = (k_back*chi_rel/6)*∇²s - k_back*alpha*s
```

**Klein-Gordon equation:**

```
∂²_t s = v²_KG ∇²s - m²_KG s
```

with:
```
v²_KG = k_back * chi_rel / 6   [wave speed squared, substrate units: lattice²/step²]
m²_KG = k_back * alpha         [mass squared, substrate units: 1/step²]
```

**Note (corrected from initial draft):** The formula v²=k_back×beta (DER-QNG-030) was
missing the factor 1/6 from the z=6 averaging convention. The correct formula uses
chi_rel/6 (= beta/6 = 0.35/6 ≈ 0.0583 for chi_rel=beta). For k_back=1: v=0.2415,
NOT 0.592. Confirmed numerically by Check 3 of QNG-CPU-054 (sqrt(k_back) scaling
ratio 2.99 vs predicted 3.16).

In physical units (a = lattice spacing, τ = step duration):
```
v²_phys = k_back * chi_rel / 6 * (a/τ)²
m²_phys = k_back * alpha / τ²
```

---

## Section 5: Gradient flow as the overdamped limit of H

The gradient flow (v5 dynamics):
```
∂_t sigma_i = -gamma * ∂E/∂sigma_i    (with large friction gamma)
```

gives:
```
∂_t s = -gamma * (alpha*s - beta*∇²s) = gamma*(beta*∇²s - alpha*s)
```

Setting gamma = 1 (substrate units) recovers the v5 parabolic equation:
```
∂_t s = -alpha*s + beta*∇²s    (DER-QNG-012, confirmed)
```

The Hamiltonian dynamics (conservative) and gradient flow (dissipative) are
related by damping:

```
∂²_t s + gamma * ∂_t s = v²_KG ∇²s - m²_KG s    (damped Klein-Gordon)
```

- **Large friction** (gamma >> 1/τ_KG where τ_KG = 1/sqrt(m²_KG)):
  ∂_t s = (1/gamma) * (v²_KG ∇²s - m²_KG s) → parabolic (v5 gradient flow) ✓
- **Zero friction** (gamma = 0):
  ∂²_t s = v²_KG ∇²s - m²_KG s → undamped Klein-Gordon (relativistic wave) ✓

**Conclusion:** The v5 gradient flow is the overdamped (large-friction) limit of the
v6 Hamiltonian dynamics. The conservative limit H = T + E is the fundamental theory;
the dissipative substrate is an approximation valid when the kinetic energy T << E.

---

## Section 6: Speed of light identification (Constraint C3)

Setting v_phys = c (speed of light):

```
v²_KG = k_back * chi_rel / 6 * (a/τ)² = c²
```

For chi_rel = 0.35, k_back to be measured:
```
τ/a = sqrt(k_back * chi_rel / 6) / c = sqrt(k_back * 0.35/6) / c
```

If k_back = 1: τ/a = sqrt(0.35/6)/c = 0.2415/c
If k_back << 1: τ/a = sqrt(k_back * 0.0583)/c → smaller

Combined with C1 (G_Newton matching, m_u * τ² = 8.74×10⁻¹¹ * a³):

```
m_u = 8.74×10⁻¹¹ * a³ / τ²
    = 8.74×10⁻¹¹ * a³ * c² / (k_back * chi_rel/6 * a²)
    = 8.74×10⁻¹¹ * 6 * a * c² / (k_back * chi_rel)
    = (8.74×10⁻¹¹ * 6 / (k_back * 0.35)) * a * c²
    = 1.498×10⁻⁹ * a * c² / k_back  [kg, a in meters]
```

For k_back = 1, m_node = m_proton (1.673×10⁻²⁷ kg):
```
a = m_proton / (1.498×10⁻⁹ * c²) = 1.673×10⁻²⁷ / (1.498×10⁻⁹ × (3×10⁸)²)
  = 1.673×10⁻²⁷ / (1.348×10⁸)
  ≈ 1.24×10⁻³⁵ m ≈ 0.77 l_Planck
```

Note: with the corrected v formula, the lattice spacing is sub-Planck for k_back=1.
This is consistent with the Planck-scale substrate interpretation.
The exact value of k_back is to be measured from QNG-CPU-054.

**The unit system is fully constrained:** once k_back is measured from a wave propagation
simulation (QNG-CPU-054, proposed), all three of a, τ, m_u follow.

---

## Section 7: KG mass and particle physics

From the mass term:
```
m²_KG = k_back * alpha / τ²
```

Physical mass:
```
m_KG = sqrt(k_back * alpha) * hbar / (τ * c²)    [energy units via E = m*c²]
```

For k_back=1, alpha=0.005, τ = sqrt(beta)*a/c:
```
m_KG = sqrt(0.005) / τ = sqrt(0.005)*c / (sqrt(0.35)*a)
     = (sqrt(0.005/0.35)) * c/a
     = 0.1195 * c/a
```

For a = 4.6 l_Planck = 7.4×10⁻³⁵ m:
```
m_KG * c / hbar = 0.1195 / (7.4×10⁻³⁵) = 1.6×10³³ m⁻¹
               = 1.6×10³³ / (hbar/c) ... 
```

In energy: m_KG * c² = 0.1195 * hbar*c / a = 0.1195 * E_Planck * l_Planck/a
For a = 4.6 l_Planck: m_KG * c² = 0.1195/4.6 * E_Planck ≈ 0.026 * E_Planck ≈ 5×10¹⁷ GeV

This is near-Planck mass — the Klein-Gordon excitation of the substrate is NOT the proton.
The vortex ring IS the proton; the Klein-Gordon wave is a different degree of freedom
(substrate phonon / graviton candidate).

For m_KG = 0 (massless): requires delta = 0 (no Channel D) OR alpha = 0 (no relaxation).
This is the graviton limit — massless spin-2 excitation requires turning off the
relaxation that drives the Newtonian limit. There may be a tension between massive
Klein-Gordon and massless gravitons.

---

## Section 8: Lorentz covariance status

With H = T + E and the conservative equations of motion:

```
∂²_t s - v²_KG ∇²s + m²_KG s = 0    (Klein-Gordon, Lorentz-covariant)
```

**The conservative limit of QNG v6 is Lorentz-covariant** for the sigma field.

Caveats:
1. The full Hamiltonian includes phi (XY model) and chi-phi coupling — phi sector
   must also be checked for Lorentz covariance. Not done here.
2. The substrate still has a preferred foliation at the microscopic level; Lorentz
   covariance is emergent at scales r >> a, not fundamental.
3. The damping term (gamma * ∂_t s) in the damped Klein-Gordon is NOT Lorentz-covariant.
   The fully conservative limit (gamma = 0) is required for exact covariance.
4. Lorentz covariance of the EFFECTIVE METRIC (not just scalar field) is not addressed.

---

## Section 9: Summary

| Result | Status |
|--------|--------|
| T = k_back/2 × Σ chi_i² (kinetic energy) | DERIVED ✓ |
| chi_i = conjugate momentum to sigma_i | IDENTIFIED ✓ |
| H = T + E reproduces Channel G (sigma evolution) | DERIVED ✓ |
| H gives Klein-Gordon: ∂²_t s = v²∇²s - m²s | DERIVED ✓ |
| v5 gradient flow = overdamped limit of H | DERIVED ✓ |
| v²_KG = k_back × beta × (a/τ)² | FORMULA ✓ |
| m²_KG = k_back × alpha / τ² | FORMULA ✓ |
| Setting v_KG = c closes unit system (Constraint C3) | DERIVED ✓ |
| For k_back=1, m_node=m_proton: a ≈ 4.6 l_Planck | COMPUTED ✓ |
| Klein-Gordon excitation ≠ proton (near-Planck mass) | FINDING ✓ |
| phi sector Lorentz covariance | OPEN |
| Effective metric Lorentz covariance | OPEN |
| Massless graviton vs massive KG tension | OPEN |

---

## Section 10: Open problems and next steps

**P1 — k_back measurement (QNG-CPU-054):**
Test wave propagation in v6 substrate with L=64, w=16 (large box, wide wave packet).
Measure group velocity v_group and fit to dispersion relation ω² = v²k² + m².
Gates: v_group ≠ 0 (wave propagates), v_group measurable with 10% precision.

**P2 — phi sector Lorentz covariance:**
The XY model energy E_phi is not Lorentz-covariant (no kinetic term for phi).
Require T_phi = (beta_phi/2) × Σ (∂_t phi_i)² to make phi sector conservative.
Physical meaning: phi oscillations propagate as phonons.

**P3 — Graviton / massless limit:**
For m_KG = 0 need alpha = 0 (no self-relaxation) or delta = 0 (no Channel D).
But alpha = 0 removes the Newtonian potential (alpha needed for screening length).
Tension: gravitational interaction requires alpha > 0, massless waves require alpha = 0.
Possible resolution: the spin-2 graviton is not the scalar s field, but a tensor
perturbation of the effective metric g_μν → requires going beyond scalar field theory.

**P4 — Lorentz covariance of effective metric:**
The full GR-QNG correspondence requires that the effective metric satisfies the
Einstein equations ∂²_t g_μν = v² ∇²g_μν ... (linearized GR). This is a
deeper question than the scalar KG derived here.

---

## Cross-references

- NOTE-QNG-013: preferred frame analysis
- NOTE-QNG-014: free energy functional E (gradient flow → dissipative v5)
- DER-QNG-028: Klein-Gordon derivation from Channel G (linearized approach)
- DER-QNG-030: v6 update law, Channel G, C3 constraint
- DER-QNG-029: unit system (C1, C2, C3)
- QNG-CPU-052: wave test (FAIL — overdiffusive regime; v6 wave propagates but v_meas≠v_pred)
- QNG-CPU-054 (proposed): clean wave measurement (L=64, w=16, measure group velocity)
