# QNG Physical Scale Derivation v1

Type: `derivation`
ID: `DER-QNG-029`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Derive the physical scale factor ρ₀ that converts the dimensionless QNG substrate
to physical mass-energy density. ρ₀ is the central open quantity blocking
zero-free-parameter rotation curve tests (OBS-002, OBS-004).

## Inputs

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026
- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md) — DER-QNG-019 (G_QNG = β/z)
- [qng-matter-source-identification-v1.md](qng-matter-source-identification-v1.md) — rho0-C1
- [qng-vortex-ring-3d-reference.py](../../tests/cpu/qng_vortex_ring_3d_reference.py) — CPU-043 (ring sigma profile)

---

## Step 1: The unit system

The QNG substrate has three primitive units:
- **a** — lattice spacing (meters)
- **τ** — update step duration (seconds)
- **m_u** — mass represented by one unit of σ-field depletion (kg/lattice-cell)

All physical quantities must be expressed in terms of {a, τ, m_u}.

We have three unknowns and need three independent physical constraints.

---

## Step 2: Constraint C1 — G_Newton matching (N2, already established)

From DER-QNG-019: in substrate units, the gravitational constant is:
```
G_QNG = β / z = 0.35 / 6 ≈ 0.05833  (substrate units)
```

In physical units, Newton's constant G_N has dimensions m³ kg⁻¹ s⁻²:
```
G_N = G_QNG × (a³) / (m_u × τ²)
```

This gives **Constraint C1**:
```
m_u × τ² = G_QNG × a³ / G_N
          = 0.05833 × a³ / (6.674×10⁻¹¹)
          = 8.740×10⁻¹¹ × a³  [kg·s², a in meters]
```

One equation, three unknowns. Two more constraints needed.

---

## Step 3: Constraint C2 candidates

To fix the unit system, one of the following additional physical inputs must be chosen:

**C2a — Planck lattice:** a = l_Planck = 1.616×10⁻³⁵ m
- Physically motivated: discrete substrate at Planck scale
- But: Yukawa screening λ=3.41 lattice units → λ_phys = 5.5×10⁻³⁵ m (sub-Planck)
- Problem: galactic gravity requires λ_phys ~ R_Hubble; Planck scale is ~10⁶¹ times too small
- **Status: inconsistent with galactic phenomenology**

**C2b — Hubble lattice:** λ_phys = R_Hubble → a = R_H / 3.41 ≈ 3.8×10²⁵ m
- Motivated by N4 (α ↔ Λ): α sets the Yukawa screen = Hubble scale
- Gives: one lattice cell ≈ 4 Hubble radii — macroscopic lattice
- **Status: consistent with cosmological claim but λ ↔ Λ still not derived**

**C2c — Observational fit:** f ≡ ρ₀ × A_VORTEX ≈ 9700 (km/s)²/lattice-unit (from OBS-002)
- Empirical determination of ρ₀ from rotation curve residuals
- Not predictive — just re-expresses the OBS-002 fit parameter
- **Status: valid empirical constraint, not a derivation**

---

## Step 4: Constraint C3 — Speed of light (tentative)

The substrate has no wave equation in v5 (DER-QNG-028), so c cannot be matched
to substrate signal speed directly. In v6 (Channel G), the Klein-Gordon speed is:
```
v² = k_back × chi_rel  (substrate units, dimensionless)
```

Setting v_physical = c:
```
c = v × (a / τ)  →  τ = v × a / c
```

This provides C3 once v is known from a Channel-G simulation. **Open until v6 is tested.**

---

## Step 5: Evaluating ρ₀ under C2b (Hubble lattice)

With a = R_H / 3.41:
- R_H = 1.3×10²⁶ m  (Hubble radius)
- a = 3.81×10²⁵ m

From C1: m_u × τ² = 8.740×10⁻¹¹ × (3.81×10²⁵)³
                   = 8.740×10⁻¹¹ × 5.53×10⁷⁶
                   = 4.83×10⁶⁶ kg·s²

Without C3 (τ unknown), m_u is undetermined. Cannot evaluate ρ₀ numerically.

---

## Step 6: ρ₀ from particle mass matching (working formula)

From rho0-C1 (DER-QNG-021):
```
ρ₀ = m_particle / ∫M_eff dV
```

where:
- m_particle = physical mass of the particle the ring represents
- ∫M_eff dV = integral of the dimensionless M_eff field over ring volume (lattice units³)

From CPU-043 ring: sigma_core ≈ 0.27, sigma_bulk ≈ 0.47
M_eff at core: M_eff = a_M × D + a_D × D + a_P × P ≈ a_M (dominant term, a_D,a_P unknown)
Effective Δσ = sigma_bulk - sigma_core ≈ 0.20 per lattice cell at core

Ring volume: torus with R=4, core radius r_core ≈ 2 lattice units (from sigma profile)
V_ring = 2π²Rr_core² ≈ 2 × 9.87 × 4 × 4 = 315 lattice cells (approximate)

Sigma deficit integral:
```
∫Δσ dV ≈ 0.20 × 315 = 63  lattice-cells (dimensionless)
```

(Measured numerically in CPU-051 — see below.)

Working formula:
```
ρ₀ = m_particle / (a_M × ∫Δσ dV)
   = m_particle / (a_M × 63)
```

Since a_M is free, ρ₀ is undetermined. The OBS-001 finding (a_M uncorrelated with
baryonic mass) means a_M cannot be set from rotation curves directly.

---

## Step 7: Conversion factor f

The observable in rotation curves is:
```
ΔV²(r) = f × C_K(r, λ)   where f = ρ₀ × A_VORTEX
```

From OBS-002 residuals: f_empirical ≈ 9700 (km/s)² / lattice-unit
From CPU-043: A_VORTEX = 0.225

Therefore:
```
ρ₀_empirical = f_empirical / A_VORTEX = 9700 / 0.225 ≈ 43000 (km/s)²/lattice-unit
```

This is an observational determination of ρ₀, not a derivation from first principles.

Connecting to particle mass:
```
m_particle = ρ₀_empirical × a_M × ∫Δσ dV
           = 43000 × a_M × 63  (km/s)² / lattice-unit
           = 2.71×10⁶ × a_M  (km/s)²/lattice-unit
```

The physical unit conversion still requires a (lattice spacing in physical units).

---

## Summary of open constraints

| Symbol | Status | Constraint |
|--------|--------|-----------|
| a (lattice spacing) | **open** | C2b plausible but not derived |
| τ (time step) | **open** | requires v6 + c matching |
| m_u (node mass) | **open** | follows from a, τ via C1 |
| a_M (M_eff coefficient) | **open** | OBS-001 Check 3 FAIL |
| ρ₀ | **open** | = m_particle / (a_M × ∫Δσ dV) |
| f = ρ₀ × A_VORTEX | empirically ~43000 (km/s)²/lu | from OBS-002 residuals |

**Minimum inputs needed to fully determine ρ₀:**
1. Physical identification of one particle mass (proton? electron? Planck mass?)
2. Value of a_M (requires particle-level M_eff calculation)
3. Lattice spacing a (requires C2 + C3, i.e., both v6 wave speed and cosmological α)

Until at least one of these is fixed from theory (not observation), ρ₀ remains open.

---

## Immediate next step

CPU-051: Measure ∫Δσ dV numerically from a stable ring simulation.
This gives the geometric factor; ρ₀ is then expressed as:
```
ρ₀ = m_particle / (a_M × M_ring_integral)
```
leaving only (m_particle, a_M) as free inputs — the minimal open set.

---

## Notation note (added 2026-04-06)

The symbol "f" in §7 means f ≡ ρ₀ × A_VORTEX (the direct OBS-002 conversion factor).
CLAUDE.md previously used "f" for ρ₀. Canonical convention per NOTE-QNG-015:
- ρ₀ ≈ 43000 (km/s)²/lu  (substrate energy density, from OBS-002 via ρ₀ = f / A_VORTEX)
- f  ≈  9700 (km/s)²/lu  (direct OBS-002 residual; f = ρ₀ × A_VORTEX)
See `qng-f-naming-clarification-v1.md` (NOTE-QNG-015).
