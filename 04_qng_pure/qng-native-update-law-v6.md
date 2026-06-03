# QNG Native Update Law v6

Type: `derivation`
ID: `DER-QNG-030`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Inputs

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026 (v5 baseline)
- [qng-wave-equation-derivation-v1.md](qng-wave-equation-derivation-v1.md) — DER-QNG-028 (wave-equation gap)
- [qng-rho0-physical-scale-v1.md](qng-rho0-physical-scale-v1.md) — DER-QNG-029 (rho0 scale)

---

## Objective

Extend v5 with Channel G: chi back-reaction on sigma. DER-QNG-028 showed that
linearized v5 is purely diffusive — no wave equation. Channel G closes this gap
and produces a Klein-Gordon dispersion relation, enabling c-matching and the
τ/a constraint for the physical unit system (DER-QNG-029).

## Upstream

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026
- [qng-wave-equation-derivation-v1.md](qng-wave-equation-derivation-v1.md) — DER-QNG-028
- [qng-rho0-physical-scale-v1.md](qng-rho0-physical-scale-v1.md) — DER-QNG-029

---

## Channel G definition

Add to the sigma update:

```
sigma_i(t+1) = sigma_i(t)
    + alpha  * (sigma_ref - sigma_i)          [Channel A: self-restore]
    + beta   * (sigma_bar_i - sigma_i)        [Channel B: diffusion]
    - delta  * (sigma_ref - sigma_i)          [Channel D: chi cross-coupling, v3]
    - gamma_phi * D_i * sigma_i               [Channel F: phi disorder, v5]
    + k_back * chi_i                          [Channel G: chi back-reaction, v6 NEW]
```

The chi and phi updates are unchanged from v5.

**Parameter:** k_back ∈ (0, 1) — chi-to-sigma coupling strength.

---

## Wave equation derivation (linearized vacuum)

Vacuum: sigma_i = sigma_ref, chi_i = 0, phi_i = uniform → D_i = 0.

Let s_i = sigma_i - sigma_ref (small perturbation).

**Sigma linearized:**
```
s_i(t+1) = s_i(t) - alpha*s_i + beta*(s_bar - s_i) + k_back*c_i
```

Spatial Fourier mode k: s_bar = cos(k)*s_k (for cubic lattice, cos(k) = (1/3)Σcos(k_μ))
Let L_k = beta*(cos(k)-1) - alpha (effective Laplacian + damping)

```
s_k(t+1) = (1 + L_k) * s_k(t) + k_back * c_k(t)     ... (1)
```

**Chi linearized:**
From chi update: c_new = c*(1-chi_decay) + chi_rel*(s_bar-s) + delta*(sigma_ref-sigma)
In vacuum perturbation (sigma_ref-sigma = -s):
```
c_k(t+1) = (1-chi_decay) * c_k(t) - chi_rel*(1-cos(k)) * s_k(t) - delta * s_k(t)
          = (1-chi_decay) * c_k(t) - [chi_rel*(1-cos(k)) + delta] * s_k(t)  ... (2)
```

**Second-order time equation:** Eliminate c_k from (1) and (2).

From (1): c_k(t) = [s_k(t+1) - (1+L_k)*s_k(t)] / k_back

Substituting into (2) (shifted by 1):
```
[s_k(t+2) - (1+L_k)*s_k(t+1)] / k_back
= (1-chi_decay)*[s_k(t+1) - (1+L_k)*s_k(t)] / k_back
  - [chi_rel*(1-cos(k)) + delta] * s_k(t)
```

Multiply through by k_back:
```
s_k(t+2) = (2 + L_k - chi_decay)*s_k(t+1)
           - [(1+L_k)*(1-chi_decay) + k_back*(chi_rel*(1-cos(k))+delta)] * s_k(t)
```

**Continuum limit** (small k, small step size):
- s_k(t+2) - 2*s_k(t+1) + s_k(t) ≈ τ² ∂²_t s
- s_k(t+1) - s_k(t) ≈ τ ∂_t s
- (1 - cos(k)) ≈ k²a²/2 (for small k, a = lattice spacing)
- L_k ≈ -beta*k²a² - alpha

Result:
```
τ² ∂²_t s = -(alpha + chi_decay)*τ ∂_t s
            + beta*k²a²*s - k_back*(chi_rel*k²a²/2 + delta)*s  [leading order]
```

Rearranging (dropping the τ ∂_t s damping for the dispersion relation):
```
∂²_t s = v²_eff ∇²s - m²_eff s
```

where:
```
v²_eff = (beta - k_back*chi_rel/2) * (a/τ)²
m²_eff = k_back * delta / τ²
```

**For k_back << 2*beta/chi_rel (k_back << 2.0 for beta=0.35, chi_rel=0.35):**
```
v²_eff ≈ beta * (a/τ)²     [wave speed dominated by beta diffusion]
m²_eff = k_back*delta/τ²   [mass term from chi-sigma coupling]
```

**Physical identification:**
- Setting v_eff = c: τ/a = sqrt(beta)/c ≈ 0.592/c
- With a = lattice spacing (m), τ = 0.592 * a / c

This provides **Constraint C3** needed in DER-QNG-029 to fully determine τ.

---

## Combined with G_Newton matching (C1):

From C1: m_u × τ² = 8.740×10⁻¹¹ × a³

With C3: τ = sqrt(beta) × a / c = 0.5916 × a / c

```
m_u = 8.740×10⁻¹¹ × a³ / τ²
    = 8.740×10⁻¹¹ × a³ / (0.5916² × a² / c²)
    = 8.740×10⁻¹¹ × a × c² / 0.3500
    = 2.497×10⁻¹⁰ × a × c²  [SI: kg, a in meters, c in m/s]
    = 2.497×10⁻¹⁰ × a × (3×10⁸)²
    = 2.247×10⁷ × a  [kg, a in meters]
```

For m_u = m_proton = 1.673×10⁻²⁷ kg:
```
a = 1.673×10⁻²⁷ / 2.247×10⁷ = 7.4×10⁻³⁵ m  ≈ 4.6 × l_Planck
```

For m_u = m_electron = 9.109×10⁻³¹ kg:
```
a = 9.109×10⁻³¹ / 2.247×10⁷ = 4.1×10⁻³⁸ m  ≈ 2.5×10⁻³ × l_Planck
```

**Key result:** If one lattice node = one proton, a ≈ 4.6 l_Planck.
The lattice is near-Planck scale regardless of which sub-nuclear particle is chosen.

The Yukawa screening then gives:
```
lambda_physical = 3.41 × a ≈ 3.41 × 7.4×10⁻³⁵ m ≈ 2.5×10⁻³⁴ m
```
Still sub-nuclear. The lambda=3.41 screens at particle-physics scale, not galactic scale.

**Open question (Gap 5 restatement):** For galactic-scale gravity, either:
(a) The lattice spacing a >> 4.6 l_Planck — not derivable from particle mass matching
(b) The Yukawa length is set differently at cosmological scales — the cosmological α
    problem remains open

---

## Summary

| Channel | Formula | Version |
|---------|---------|---------|
| A (self-restore) | +alpha*(sigma_ref - sigma_i) | v2 |
| B (diffusion) | +beta*(sigma_bar - sigma_i) | v2 |
| D (chi cross-coupling) | -delta*(sigma_ref - sigma_i) | v3 |
| E (chi drives phi) | +epsilon*chi_i in phi update | v4 |
| F (phi disorder → sigma) | -gamma_phi*D_i*sigma_i | v5 |
| G (chi back-reaction) | +k_back*chi_i | v6 |

v6 gives Klein-Gordon: v²_eff ≈ beta*(a/τ)², m²_eff = k_back*delta/τ²
Setting v_eff = c: τ = sqrt(beta)*a/c, a ≈ 4.6 l_Planck for m_node = m_proton.
