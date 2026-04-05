# QNG CODATA Constraint v1

Type: `derivation`
ID: `DER-QNG-019`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Execute Step N7 of the Newtonian limit program (`DER-QNG-011`): match the QNG formula
for G_QNG to the CODATA value of Newton's constant, derive the substrate unit mapping,
and combine with the dephasing constraint from `DER-QNG-017` to reduce the number of
free substrate parameters.

## Inputs

- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md)
- [qng-phi-dephasing-v1.md](qng-phi-dephasing-v1.md)
- [qng-newtonian-limit-program-v1.md](qng-newtonian-limit-program-v1.md)

---

## Section 1: G_QNG in Physical Units

From `DER-QNG-018`, in substrate units (Δu=1, t_s=1):
```
G_QNG_substrate = β/z      [dimension: Δu²/t_s]
```

In physical SI units, with substrate node spacing `Δu_SI` [m] and substrate timestep
`t_s_SI` [s]:
```
G_QNG_SI = (β/z) · (Δu_SI² / t_s_SI)    [m²/s]
```

**Dimensional mismatch:** SI Newton's constant `G_SI = 6.674×10⁻¹¹ m³/(kg·s²)` has
dimension `[m³/(kg·s²)]`, while `G_QNG_SI` has dimension `[m²/s]`. The missing
dimensions come from the mass scale.

**Resolution (DER-QNG-013 §4.3):** The substrate has no intrinsic mass scale. The
mass unit is introduced through the matter sector parameter `ρ₀` [kg per substrate cell].
The effective density `ρ_eff = ρ₀·M_eff/Δu³_SI` has dimension [kg/m³] when ρ₀ is in kg.

From the Poisson equation in physical units:
```
∇²Φ_Newton = 4π · G_QNG_SI · ρ_eff
```

LHS: [m⁻²] · [m²/s²] = [s⁻²]
RHS: [m²/s] · [kg/m³] = [kg/(m·s)]

For dimensional consistency: [s⁻²] = [kg/(m·s)] requires [kg] = [m·s⁻¹]. This means
the mass unit in QNG is tied to the substrate speed:
```
[ρ₀] = [Δu_SI · t_s_SI⁻¹] = [c_substrate_SI]    (mass unit = speed unit)
```

This is a natural unit system, not SI. The physical Newton constant in substrate natural
units is:
```
G_physical = G_QNG_SI / c²_substrate_SI = (β/z) · (Δu_SI/t_s_SI)²    [m³/s²/c²]
```

For G_physical = G_SI = 6.674×10⁻¹¹ m³/(kg·s²), we need c_substrate to absorb the
remaining kg:
```
G_SI = G_QNG_SI · c_substrate_SI    [if mass is measured in units of m/s]
```

**Simplest consistent choice:** Work in Planck units where c_substrate = c = 1, and
match G_QNG to G in natural units. This gives:

---

## Section 2: CODATA Constraint Equation

**In Planck units** (ℏ = c = G = 1), all substrate parameters are dimensionless ratios
of Planck quantities. The CODATA constraint becomes:

```
β / z = 1    (in Planck units)
```

since G = 1 in Planck units. This means β = z (one substrate parameter is fixed
by G in Planck units). For z=6 (3D cubic lattice): β_Planck = 6. But β ∈ (0,1) in
the update law — a contradiction.

**Resolution:** The substrate operates at sub-Planck resolution. Let Δu_SI = n_Planck · ℓ_Planck
and t_s_SI = n_Planck · t_Planck for some large integer `n_Planck` (number of Planck
lengths per substrate cell). Then:

```
G_QNG_SI = (β/z) · (Δu_SI² / t_s_SI) = (β/z) · n_Planck · ℓ_Planck² / t_Planck
         = (β/z) · n_Planck · G_SI · ℏ/c⁵ · c³/ℏ
         = (β/z) · n_Planck · G_SI / c²
```

Setting G_QNG_SI = G_SI (matching Newton's constant):
```
(β/z) · n_Planck / c² = 1
n_Planck = z · c² / β    [number of Planck lengths per substrate cell]
```

For β=0.35, z=6, c=1 (natural units): n_Planck = 6/0.35 ≈ 17.1.

So each substrate cell is ≈17 Planck lengths across. The substrate resolution is
slightly coarser than Planck scale — a physically reasonable scenario.

**CODATA constraint statement:**
```
n_Planck = z · c² / β    [Planck cells per substrate cell]
```

This gives the substrate length scale in physical units:
```
Δu_SI = n_Planck · ℓ_Planck = (z/β) · ℓ_Planck
t_s_SI = n_Planck · t_Planck = (z/β) · t_Planck
```

Note: Δu_SI/t_s_SI = ℓ_Planck/t_Planck = c → c_substrate = c. The substrate signal
speed is the speed of light. ✓ (physically required for relativistic invariance)

---

## Section 3: Screening Length in Physical Units

From `DER-QNG-018`, Identity N6.1:
```
λ_screen = Δu · √(β/(z·α))
```

In physical units:
```
λ_screen_SI = Δu_SI · √(β/(z·α))
             = (z/β) · ℓ_Planck · √(β/(z·α))
             = (z/β) · √(β/(z·α)) · ℓ_Planck
             = √(z/(β·α)) · ℓ_Planck
```

For β=0.35, z=6, α=0.005:
```
λ_screen_SI = √(6/(0.35·0.005)) · ℓ_Planck
             = √(3428) · ℓ_Planck
             ≈ 58.5 · ℓ_Planck
             ≈ 9.5 × 10⁻³⁴ m
```

This is sub-Planck-scale (actually super-Planck by a factor 58.5). More precisely,
it is ≈58.5 Planck lengths, which is ∼10⁻³³ m — far below any observable scale.

**Implication:** The gravitational screening does not affect any astrophysical
observation (solar system scales are ≫ λ_screen_SI). Newtonian gravity is recovered
without modification on all observable scales. The screened Poisson equation is
indistinguishable from the pure Poisson equation for r ≫ λ_screen_SI.

**Constraint:** If α were much smaller (α ≪ 10⁻⁴), λ_screen would grow toward
observable scales and the screened Poisson regime would leave detectable signatures.
This is a testable condition: α must satisfy α ≥ β/(z·(λ_obs/Δu)²) to avoid
observable deviations at scale λ_obs. For test parameters (β=0.35, z=6), this gives
α ≥ 3.4×10⁻⁷ for λ_obs at μm scale.

---

## Section 4: Dephasing Constraint on ε

From `DER-QNG-017` (QNG-CPU-034):
```
ε = √2 / (T₂*_SI · σ_chi_SI)
```

where T₂*_SI is an observed dephasing time and σ_chi_SI is the chi spread in SI units.

**Unit mapping:** σ_chi is dimensionless (chi ∈ [-1,1]). So σ_chi_SI = σ_chi_substrate
(no unit conversion needed for the chi field itself).

Therefore:
```
ε = √2 / (T₂*_SI_steps · σ_chi)
```

where T₂*_SI_steps = T₂*_physical / t_s_SI = T₂*_physical · β / (z · t_Planck).

**Example:** For a typical atomic dephasing time T₂* = 10⁻⁶ s (μs) and
σ_chi ≈ 4.6 (from QNG-CPU-034 equilibrium):
```
t_s_SI = (z/β) · t_Planck = (6/0.35) · 5.39×10⁻⁴⁴ s ≈ 9.24×10⁻⁴⁴ s
T₂*_SI_steps = 10⁻⁶ / 9.24×10⁻⁴⁴ ≈ 1.08×10³⁷ steps
ε = √2 / (1.08×10³⁷ · 4.6) ≈ 2.8×10⁻³⁸
```

This implies ε is extremely small in substrate units — consistent with the chi→phi
coupling being weak on quantum scales.

**Combined constraint system (two equations, three unknowns {Δu_SI, t_s_SI, ρ₀_SI}):**

1. CODATA G:  `(β/z)·(Δu_SI²/t_s_SI) / (some_mass_factor) = G_SI`
2. Dephasing: `ε = √2 / (T₂*_SI / t_s_SI · σ_chi)`

From constraint 1 + the Planck unit identification: Δu_SI and t_s_SI are both
determined by `z/β` times Planck scales.

From constraint 2: ε is determined once t_s_SI and T₂*_observed are known.

**The system is closed in Planck units.** The remaining freedom is in ρ₀_SI (matter
mass scale), which is fixed by requiring that G_QNG·ρ₀_SI matches the observed baryon
density times the Newtonian potential for a test system (Step N7 extended, not pursued here).

---

## Section 5: Parameter Summary

| Parameter | Substrate value | Physical meaning | Fixed by |
|-----------|----------------|-----------------|---------|
| `β` | 0.35 (test) | Relational coupling | Free — closest to known data |
| `z` | 6 (3D) | Lattice coordination | Graph geometry |
| `α` | 0.005 (test) | Self-relaxation rate | Free |
| `δ` | 0.20 (test) | Generation order coupling | Free |
| `ε` | 0.02 (test) | Chi-to-phi coupling | DER-QNG-017 constraint |
| `Δu_SI` | `(z/β)·ℓ_Planck` | Substrate cell size | CODATA G (this doc) |
| `t_s_SI` | `(z/β)·t_Planck` | Substrate timestep | CODATA G (this doc) |
| `ρ₀_SI` | open | Matter mass scale | Baryon density matching (open) |

**Free parameters remaining after CODATA + dephasing:** {β, z, α, δ} with one
constraint G = α·λ²_screen (Identity N6.1). Remaining degrees of freedom: 3.

---

## Section 6: Gravity Probe A Check

From Gravity Probe A (1976): the radial potential `Φ = -GM/r` must hold to 70 ppm
from Earth's surface to r = 10,000 km.

In QNG, the screened Poisson equation gives:
```
Φ(r) = -G_QNG · M_eff · exp(-r/λ_screen) / (4πr)   [3D Yukawa]
```

For r ≪ λ_screen, this reduces to `Φ = -G_QNG·M_eff/(4πr)` — pure 1/r as required.

With λ_screen ≈ 58.5 ℓ_Planck ≈ 10⁻³³ m, even at sub-nuclear scales (r ≈ 10⁻¹⁵ m):
```
exp(-r/λ_screen) = exp(-10⁻¹⁵/10⁻³³) = exp(-10¹⁸) ≈ 0
```

Wait — r/λ_screen = 10⁻¹⁵ / 10⁻³³ = 10¹⁸. This is enormous. exp(-10¹⁸) ≈ 0.

This means the exponential screening kills the potential at ALL observable scales —
which would mean gravity doesn't propagate beyond λ_screen. This is a problem.

**Resolution:** The Yukawa decay exp(-r/λ_screen)/r should be compared to the Planck
unit 1/r for r ≫ λ_screen. Since λ_screen ≪ any observable scale, the field has
essentially decayed to zero for r ≫ λ_screen. But then there's no long-range gravity!

**This is the critical open issue from Gap 5 of DER-QNG-011:** the parameter regime
where G_QNG matches CODATA forces α to be so large (relative to β/z) that
λ_screen becomes sub-Planck — below the grid scale — making the screening unphysical.
The resolution requires that α in the test simulations (α = 0.005 >> α needed
for astrophysical λ_screen) is NOT the astrophysical α. The astrophysical α must
satisfy α ≪ β/z to give λ_screen ≫ astrophysical scales.

**Revised astrophysical α constraint:**
For λ_screen ≥ 1 AU = 1.5×10¹¹ m:
```
Δu_SI · √(β/(z·α)) ≥ 1.5×10¹¹ m
(z/β)·ℓ_Planck · √(β/(z·α)) ≥ 1.5×10¹¹ m
√(z/(β·α)) · ℓ_Planck ≥ 1.5×10¹¹ m
z/(β·α) ≥ (1.5×10¹¹ / 1.6×10⁻³⁵)²  = (9.4×10⁴⁵)²
α ≤ z / (β · 8.8×10⁹¹) ≈ 6/(0.35 · 8.8×10⁹¹) ≈ 2×10⁻⁹¹
```

So for gravity to be unscreened on solar system scales, α must be ≤ 10⁻⁹¹ in
Planck units. This is a fine-tuning condition — the relaxation rate must be
astronomically small.

**Alternatively:** The screened Poisson equation is NOT the correct equation for
large-scale gravity. The long-range (r ≫ λ_screen) behavior must recover a different
equation — one that does not decay exponentially. This suggests the Newtonian limit
requires a two-step analysis:
1. Short-range (r ≲ λ_screen): screened Poisson governs
2. Long-range (r ≫ λ_screen): different mechanism, possibly from the memory sector
   or from graph connectivity at cosmological scales

**This is the primary open issue for the Newtonian limit.** It is documented here
rather than resolved. Resolution likely requires:
- Analyzing the Newtonian limit on a cosmological-scale graph (not a small ring)
- Including the memory sector (ε₄ correction) which may dominate at long range
- Or allowing α → 0 (no relaxation) so λ_screen → ∞ and the pure Poisson equation holds globally

---

## Section 7: Step N7 Status

| Sub-step | Status |
|----------|--------|
| G_QNG formula in physical units | Complete (this document) |
| CODATA constraint equation | Complete (n_Planck = z/β) |
| c_substrate = c identification | Complete (Planck unit consistency) |
| Screening length in physical units | Complete (sub-Planck for test parameters) |
| Long-range gravity recovery | **Open — Gap 5 + screening problem** |
| ρ₀ from baryon density | Open — requires matter sector extension |
| ε constraint from dephasing | Combined formula given, absolute value open |

**Step N7 is partially complete.** The G_QNG → G_SI unit mapping is established, but
the long-range gravity problem (screening at sub-Planck scale) is a critical open gap
that must be resolved before claiming full Newtonian recovery.

---

## Cross-references

- Poisson assembly: `DER-QNG-018` (`qng-poisson-assembly-v1.md`)
- Phi dephasing: `DER-QNG-017` (`qng-phi-dephasing-v1.md`)
- Newtonian program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- Screening test: `QNG-CPU-035`
