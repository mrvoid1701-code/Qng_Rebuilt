# QNG a_M Fixing Program v1

Type: `derivation`
ID: `DER-QNG-027`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Fix the coefficient a_M (matter coupling amplitude) from the vortex ring simulation
results (QNG-CPU-043) and the substrate parameter G_QNG. Once fixed, a_M enables
parameter-free predictions of rotation curves, lensing, and other observables.

This derivation completes DER-QNG-025 §4: the a_M fixing condition.

## Inputs

- [qng-matter-stability-v1.md](qng-matter-stability-v1.md) — DER-QNG-025, §4
- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026, Channel F
- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md) — G_QNG = β/z
- QNG-CPU-043 result: A_vortex_ring = sigma_ref - sigma_core = 0.5 - 0.275 = 0.225

---

## Step 1: What A_vortex_ring measures

From QNG-CPU-043, the vortex ring creates a sigma deficit:
```
A_vortex_ring = sigma_ref - sigma_core = 0.225
```
at the ring core (rho ≈ R, |z - z_ring| ≤ 1).

This is the amplitude of the coherence deficit localized at the ring core. In the
matter stability program (DER-QNG-025), this deficit IS the "matter particle" — the
ring is the particle, A_vortex_ring is its internal amplitude.

---

## Step 2: The a_M fixing condition (from DER-QNG-025 §4)

The a_M fixing condition derived in DER-QNG-025 §4 states:

```
a_M × kappa × A_vortex × C_K = m_particle / rho_0
```

where:
- `a_M` — the matter coupling amplitude (free parameter to fix)
- `kappa` — a geometric factor from the vortex ring spatial profile
- `A_vortex` — the sigma deficit amplitude (= A_vortex_ring from simulation)
- `C_K` — the integral of the Yukawa kernel over the ring exterior
- `m_particle` — the physical mass of the particle (electron, proton, etc.)
- `rho_0` — the substrate energy density

---

## Step 3: Computing kappa and C_K from simulation

**kappa (geometric factor):**
kappa is the ratio of the integral of the sigma deficit profile over the ring volume
to A_vortex_ring × V_core, where V_core is the core volume.

From QNG-CPU-043:
```
n_ring_shape = 920 (sigma-depleted nodes with rho in [R-3, R+3])
V_core ≈ n_ring_shape × (lattice spacing)^3
kappa ≈ 1  (by construction, if A_vortex = mean deficit in core region)
```

**C_K (Yukawa kernel integral):**
The screened Poisson kernel in 3D is K_3D(r) = exp(-r/lambda) / r.

The integral of K_3D over the exterior of a vortex ring of radius R in 3D:
```
C_K = integral_{exterior} exp(-|r - r_ring|/lambda) / |r - r_ring|  d^3r
```

For lambda >> R (Yukawa screening length >> ring radius — galaxy scales):
```
C_K ≈ 4pi * lambda^2  (dominant term; the ring source acts like a point at scales >> R)
```

For the substrate: lambda = sqrt(beta / (alpha * z)) where z=6 (cubic lattice).
With alpha=0.005, beta=0.35, z=6:
```
lambda = sqrt(0.35 / (0.005 * 6)) = sqrt(0.35 / 0.03) = sqrt(11.67) ≈ 3.41 lattice units
```

So in the substrate: C_K_substrate ≈ 4pi × (3.41)^2 ≈ 4pi × 11.63 ≈ 146 (lattice units)^2

---

## Step 4: Connecting substrate units to physical units

The substrate screening length in physical units:
```
lambda_physical = lambda_substrate × a_lattice
```
where a_lattice is the physical lattice spacing (unknown a priori — set by matching G_QNG to G_Newton).

From the Newtonian limit (DER-QNG-019, GRAV-C2):
```
G_QNG = beta / z = 0.35 / 6 ≈ 0.0583  [substrate units]
G_Newton = 6.674e-11 m^3 kg^-1 s^-2
```

The physical lattice spacing a_lattice and time step tau are set by:
```
G_QNG (substrate) = G_Newton (physical)
```
This gives the conversion factor but leaves a_lattice as a free parameter until
rho_0 (substrate energy density) is fixed.

---

## Step 5: The a_M fixing equation — dimensionless form

Working in substrate units (lattice spacing = 1, time step = 1):

```
a_M × A_vortex_ring × C_K_substrate = (m_particle / rho_0) × (1 / G_QNG)
```

Rearranging:
```
a_M = (m_particle / rho_0) / (A_vortex_ring × C_K_substrate × G_QNG)
```

Substituting known values:
- A_vortex_ring = 0.225 (QNG-CPU-043)
- C_K_substrate ≈ 146 (Step 3)
- G_QNG = 0.0583 (substrate)

```
a_M = (m_particle / rho_0) / (0.225 × 146 × 0.0583)
a_M = (m_particle / rho_0) / 1.916
a_M ≈ 0.52 × (m_particle / rho_0)
```

This is the a_M fixing equation. Once rho_0 is specified (via the baryon density
constraint from DER-QNG-021), a_M is fully determined.

---

## Step 6: The rho_0 constraint (from DER-QNG-021)

From DER-QNG-021, rho_0 satisfies:
```
rho_0 = m_particle / integral M_eff dV
```

where M_eff = a_M × delta_sigma × f(sigma, chi, phi) is the effective matter
source field. This is implicit in a_M (circular). The self-consistent solution:

Define the dimensionless ratio:
```
xi = a_M × integral M_eff dV / (lattice volume)
```

Then: rho_0 = m_particle / (xi × lattice_volume).

From the simulation, the integral of sigma deficit over the ring:
```
integral (sigma_ref - sigma) dV ≈ A_vortex_ring × n_ring_shape
                                 ≈ 0.225 × 920 = 207  [lattice units]^3
```

This gives:
```
rho_0 × 207 = m_particle × (1 / a_M factor)
```

The circular dependence is broken by fixing rho_0 externally: rho_0 is set to the
mean baryon energy density of the observable universe in substrate units.

---

## Step 7: The rotation curve prediction

Once a_M is fixed, the QNG prediction for the rotation velocity excess is:

```
V^2_QNG(r) = V^2_baryon(r) + a_M × G_QNG × M_vortex × C_K(r)
```

where C_K(r) = (1 + r/lambda) × exp(-r/lambda) is the Yukawa potential factor
and M_vortex is the number of vortex ring "particles" (matter content) within
the galaxy.

For galaxy scales r << lambda_physical:
```
V^2_QNG(r) ≈ V^2_baryon(r) + a_M × G_QNG × M_galaxy / lambda^2
```

This is a FLAT correction (independent of r for r << lambda), exactly what is
observed in galaxy rotation curves.

**The QNG prediction for flat rotation excess:**
```
Delta_V^2 = a_M × G_QNG × M_baryon / lambda^2
           = a_M × (beta/z) × M_baryon / (beta/(alpha*z))
           = a_M × alpha × M_baryon
```

So `Delta_V^2 ∝ alpha × M_baryon` — the rotation excess is proportional to the
relaxation rate alpha times the baryonic mass. This is the key testable prediction.

---

## Step 8: Ring self-velocity — Phase-1 drift finding (QNG-CPU-045)

QNG-CPU-045 measured ring positions for R = 3, 4, 5, 6, 7 and found ALL radii
give identical drift velocity ≈ 0.022 units/step (L=24, Phase2=500 steps).

Investigation shows: the ring drifts during PHASE 1 (phi diffusion, BETA_PHI=0.02,
300 steps) before Channel F activates. All radii reach z=23 from z=12 during Phase 1.
The 1/R Biot-Savart scaling is MASKED by this R-independent phi-diffusion drift.

**Consequence:** The "ring self-velocity dz=9" reported in QNG-CPU-043 was Phase-1
drift (not Phase-2 Biot-Savart propulsion). In Phase 2, the ring DOES NOT MOVE
significantly — z_ring=19 at both Phase-2 T=500 and T=1000 confirms this.

**For the a_M fixing program:**
- k_v (Biot-Savart substrate constant) is NOT measurable with the current two-phase protocol
- The ring's kinematic velocity is dominated by phi diffusion, not Biot-Savart
- This is a GENUINE SUBSTRATE FINDING: BETA_PHI=0.02 puts the substrate in the
  "viscous ring" regime where phi diffusion >> self-propulsion
- k_v fixing requires a different measurement protocol (e.g., phi winding center tracking)
  or a smaller BETA_PHI value (approaching the inviscid limit)

**Updated a_M fixing chain:**
The k_v term in the matter kinematic sector remains open. The a_M amplitude fixing
from Step 5 (using A_vortex_ring and G_QNG) is unaffected by this finding.

---

## Summary: a_M fixing chain

```
QNG-CPU-043: A_vortex_ring = 0.225
QNG-CPU-044: T_lifetime = 2400 Phase-2 steps → T_lifetime × alpha = 12 >> 1 (stable)
QNG-CPU-045: k_v = v_QNG / v_theory  (substrate kinematic factor, pending)
DER-QNG-019: G_QNG = beta/z = 0.0583
DER-QNG-021: rho_0 = m_baryon / integral M_eff dV  (baryon density constraint)

→ a_M = 0.52 × (m_particle / rho_0)   [substrate units]
→ Delta_V^2 = a_M × alpha × M_baryon   [rotation curve prediction]
→ QNG-OBS-001: test against 175 rotation curves (rotation_ds006_rotmod.csv)
```

---

## What remains open

1. **rho_0 physical value**: mapping m_baryon to substrate units requires the
   lattice spacing a_lattice, which requires a second physical constraint beyond G.
   Candidate: match Lambda_QCD (proton scale) to the vortex ring core size.

2. **k_v measurement**: QNG-CPU-045 will provide k_v. This enters the ring mass
   estimate and should be consistent with a_M from Step 5.

3. **Multi-particle consistency**: a single vortex ring represents one particle.
   A galaxy contains ~10^67 particles. The total chi field from 10^67 vortex rings
   must reproduce the observed rotation curves. This requires the additivity of
   chi fields (screened Poisson → linear superposition).

4. **Parameter-free prediction**: once rho_0 is fixed, Delta_V^2 = a_M × alpha × M_baryon
   is a zero-free-parameter prediction for each galaxy. Test: QNG-OBS-001.

---

## Cross-references

- DER-QNG-025: matter stability, a_M fixing condition
- DER-QNG-026: v5 Channel F, sigma depletion at vortex core
- DER-QNG-019: G_QNG = beta/z (Newtonian limit)
- DER-QNG-021: rho_0 formal constraint
- QNG-CPU-043: A_vortex_ring = 0.225 (simulation result)
- QNG-CPU-044: T_lifetime (ring stability window)
- QNG-CPU-045: k_v (substrate kinematic factor)
- QNG-OBS-001: rotation curve parameter-free test (planned)
