# QNG Candidate Constraint C4: Quantum of Action

Type: `note`
ID: `NOTE-QNG-016`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-07`

## Purpose

C1 (G matching) and C3 (v = c) give two constraints on (a, τ, m_u).
Together they reduce to one free parameter:

```
a = m_u × G_Newton × (v_meas/c)² / G_QNG
  ≈ m_u × 1.113×10⁻²⁷ m/kg        [for k_back=1, v_meas=0.2286]
```

One more equation is needed. This note proposes the **quantum of action** identification
as the natural third constraint.

---

## The proposal: C4

From DER-QNG-032, the kinetic energy of the substrate is:

```
T = (k_back/2) × Σ chi_i²
```

The chi field is identified as the canonical momentum of sigma, with:

```
∂_t sigma_i = k_back × chi_i
→  chi_i = (1/k_back) × ∂_t sigma_i
```

The conjugate pair (sigma_i, chi_i) satisfies a Hamiltonian structure. In a
quantum theory, the canonical commutation relation requires:

```
[sigma_i, pi_j] = iℏ δ_ij    where pi_i = ∂L/∂(∂_t sigma_i) = (1/k_back) × chi_i
```

The natural identification is that **one substrate timestep carries one quantum
of action ℏ**. Dimensionally:

```
[T] = k_back × chi² × (substrate energy)
```

The simplest covariant condition: the action per node per step equals ℏ:

```
C4:  m_u × (a²/τ) × k_back = ℏ
```

Using τ = a × v_meas/c (from C3):

```
m_u × (a²/(a × v_meas/c)) × k_back = ℏ
m_u × a × c / v_meas × k_back = ℏ
m_u × a = ℏ × v_meas / (k_back × c)
```

Substituting a = m_u × 1.113×10⁻²⁷:

```
m_u² = ℏ × v_meas / (k_back × c × 1.113×10⁻²⁷)
     = (1.055×10⁻³⁴ × 0.2286) / (1 × 3×10⁸ × 1.113×10⁻²⁷)
     = 2.41×10⁻³⁵ / 3.34×10⁻¹⁹
     = 7.22×10⁻¹⁷  kg²

m_u ≈ 2.7×10⁻⁸·⁵ kg ≈ 8.5×10⁻⁹ kg  ≈ 0.5 × m_Planck
```

(Planck mass m_Pl = 2.18×10⁻⁸ kg)

**C4 gives m_u ~ Planck mass**, independent of any Standard Model particle mass.

---

## Consequences if C4 holds

With m_u ~ Planck mass and a = m_u × 1.113×10⁻²⁷ ≈ 9.5×10⁻³⁶ m:

```
a ≈ 0.6 × l_Planck   (consistent — substrate at Planck scale)
τ = a × v_meas/c ≈ 7.2×10⁻⁴⁵ s  (≈ 4 × t_Planck)
```

This is **self-consistent** with the Planck-scale substrate interpretation.

---

## The tension with vortex ring proton identification

If m_u ~ Planck mass, and the proton is a vortex ring with M_ring = 158
(sigma integral, QNG-CPU-051), then:

```
m_proton = m_u × a³ × ρ_0 × a_M × M_ring
```

For this to give m_proton = 1.67×10⁻²⁷ kg with m_u ~ 10⁻⁸ kg:
the product (a³ × ρ_0 × a_M) must be ~ 10⁻¹⁹. Alternatively:

**Interpretation A — collective excitation:**
The proton corresponds to ~ m_u/m_proton ~ 10¹⁹ coherent nodes.
A vortex ring of radius R=4 on a 24³ lattice contains ~10³ nodes.
This requires the physical ring to be cosmologically larger — inconsistent
with a particle at sub-fm scales.

**Interpretation B — redefine M_ring:**
M_ring (sigma integral) is not the physical mass. The physical mass is
the energy of the ring: E_ring = (kinetic + potential) in substrate units,
converted via (m_u/τ²) × a³. This is NOT the same as m_u × M_ring.
The energy calculation has not been done yet (open program).

**Interpretation C — m_u ≠ m_proton AND the ring energy is small:**
If E_ring (energy) << m_u (node mass), the proton mass comes from
binding energy or topological self-energy, not from summing node masses.
Analogous to how nuclear binding energy << sum of quark masses.

---

## Status

| Item | Status |
|------|--------|
| C4 equation proposed | CANDIDATE |
| C4 confirmed numerically | OPEN |
| C4 consistent with C1+C3 | YES (algebraically) |
| Planck-scale a consistent with CPU-054 | YES |
| Tension with vortex ring proton | OPEN — requires energy calculation |
| Matter source identification program | REQUIRED before C4 can be tested |

---

## Next steps

1. **Matter source identification** (DER-QNG-027/029 program): derive E_ring
   (energy of vortex ring in substrate units) vs M_ring (sigma integral).
   These differ: M_ring is a charge-like integral; E_ring is the Hamiltonian evaluated
   on the ring state. E_ring may be much smaller than m_u × M_ring.

2. **C4 numerical test**: if E_ring / (m_u × a³) matches m_proton for some
   k_back, C4 is confirmed. This is a pre-registration candidate.

3. **Mass spectrum**: compute E_ring for different R values. If ratios match
   hadron mass ratios, C4 is empirically justified even without analytic derivation.

---

## Cross-references

- DER-QNG-029: unit system (C1, C2 constraints)
- DER-QNG-032 (NOTE-QNG-016 companion): Hamiltonian H=T+E, kinetic term
- QNG-CPU-054: C3 confirmed numerically (v_meas=0.2286, k_back=1)
- QNG-CPU-051: M_ring=158.4 measured (decaying, not conserved)
- `qng-matter-source-identification-v1.md`: open program for ρ_0 and a_M
- `qng-chi-status-v1.md`: chi canonical momentum status (required for C4 derivation)
