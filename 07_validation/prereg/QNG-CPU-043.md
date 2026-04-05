# QNG-CPU-043

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

3D vortex ring stability — dynamic persistence of phi vortex ring in v5 substrate

## Purpose

Test whether a phi vortex ring (a closed vortex line in 3D space) is DYNAMICALLY
stable in the v5 QNG substrate over T=1000 steps. In 3D, phi ∈ S¹ has π₂(S¹) = 0:
there are NO topologically protected point defects. Vortex RINGS (closed vortex lines)
are characterized by π₁(S¹) = ℤ applied to loops in 3D space, but they are NOT
topologically protected — they can shrink and annihilate.

Dynamic stability means: the ring does not immediately collapse. The QNG substrate's
beta diffusion acts like viscosity; this test measures whether the ring survives
with detectable sigma depletion at T=1000 despite not being topologically forced to.

**Why the two-phase protocol is necessary:**
The sigma diffusion (beta=0.35) and phi diffusion both use the same BETA parameter
in v3/v4. Applying beta=0.35 to the phi channel causes ring collapse (π₂(S¹)=0:
no topological protection) before Channel F can build sigma depletion. The fix is
a separate BETA_PHI=0.02 for the phi update, and a two-phase protocol:
- Phase 1 (T=0..300): phi equilibrates with slow diffusion (BETA_PHI=0.02),
  Channel F off (GAMMA_PHI=0). Sigma stays at sigma_ref (autonomous).
- Phase 2 (T=300..1000, 700 steps): Channel F active (GAMMA_PHI=0.10).
  Sigma depletes at ring core; ring already has equilibrated phi structure.

A PASS means: with BETA_PHI=0.02 and the two-phase protocol, the v5 substrate
supports dynamically stable vortex rings. This motivates the a_M fixing program
for 3D matter (a vortex ring as a 3D "particle").

A FAIL means: even with slow phi diffusion, the ring collapses or sigma depletion
cannot be maintained. 3D matter in QNG requires additional stabilization.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng_vortex_ring_3d_reference.py](../../tests/cpu/qng_vortex_ring_3d_reference.py)

## Experimental design

**Lattice:** 3D cubic grid, L=20, N=20³=8000 nodes, periodic (torus) boundary conditions.

**Vortex ring initialization:**
Ring in the xy-plane, centered at (x0, y0, z0) = (10, 10, 10), radius R=5.

For each node at (x, y, z) using minimum image convention:
```
dx = x - x0  (min-image)
dy = y - y0  (min-image)
dz = z - z0  (min-image)
rho = sqrt(dx^2 + dy^2)   [distance from z-axis]
phi_i = atan2(dz, rho - R)  [winding in meridional plane]
```

This gives a phase field that winds by 2π around the ring core circle
(rho=R, z=z0), the correct initialization for a vortex ring.

sigma = 0.5 uniform, chi = 0.0 uniform.

**Parameters:** alpha=0.005, beta=0.35 (sigma/chi), beta_phi=0.02 (phi channel),
delta=0.20, epsilon=0.0, chi_decay=0.005, chi_rel=0.35, sigma_ref=0.5, gamma_phi=0.10.

Note: BETA_PHI=0.02 (not 0.35) for the phi update prevents ring collapse under
phi diffusion. The sigma channel always uses BETA=0.35 for sigma_bar diffusion.

**6-neighbor update (3D):** sigma_bar = mean of 6 neighbors (±x, ±y, ±z).
Phase disorder: D_i = 1 - |mean(exp(i*phi_j)) for 6 neighbors|.
The 3D Channel F is identical to 2D but uses 6 neighbors.

**Two-phase protocol:**
1. **Phase 1 (steps 1–300):** Initialize phi with vortex ring, sigma=0.5, chi=0.0.
   Run 300 steps with BETA_PHI=0.02, GAMMA_PHI=0 (Channel F off).
   Sigma is autonomous; phi equilibrates slowly without ring collapse.
2. **Phase 2 (steps 301–1000, 700 steps):** Switch on Channel F (GAMMA_PHI=0.10).
   Sigma depletes at ring core; ring has already equilibrated its phi structure.
3. Record snapshots at T=500 (Phase 2 step 200) and T=1000 (Phase 2 step 700).
4. At T=1000: locate the ring by finding the z-plane of minimum mean sigma
   in the cylindrical shell rho ∈ [R-3, R+3].
5. Measure ring radius R_t = mean rho of sigma-depleted nodes (sigma < 0.35)
   near the detected ring plane.
6. Count non-zero winding plaquettes (all 3 types: xy, xz, yz) at T=1000.

**Note on ring self-velocity:** A vortex ring in 3D self-propels along its symmetry
axis (z-axis here) due to its own circulation. The ring will drift in z during Phase 2;
the ring-detection algorithm searches all z-planes to find it.

## Checks

**Check 1 — Sigma depletion at ring core at T=1000:**
```
mean(sigma at nodes with rho in [R-2, R+2] and |z - z_ring|_min-image <= 1) < 0.40
```
where z_ring is the z-position of minimum sigma (ring may have moved in z due to
self-induced velocity). Gate 0.40 is conservative — actual depletion depends on
beta competition: beta=0.35 sigma diffusion refills the core from the bulk.

**Check 2 — Sigma in bulk unaffected:**
```
mean(sigma at nodes with rho > R + 5 AND |z - z_ring|_min-image > 5) > 0.40
```
Channel F has zero effect far from the ring. Gate 0.40 (not 0.45) accounts for
slight global sigma redistribution under the two-phase protocol (Phase 2 acts on
all nodes, slight bulk depletion from nodes with non-zero D away from core).

**Check 3 — Ring radius not collapsed:**
```
R_t > R / 2 = 2.5 at T=1000
```
The ring may shrink (not topologically protected) but must not collapse completely.
R_t measured as mean rho of sigma-depleted nodes (sigma < 0.35) near z_ring.

**Check 4 — Non-zero winding plaquettes present at T=1000:**
```
total count of plaquettes with |W| = 1 >= 4 at T=1000
```
across all 3 types of plaquettes (xy, xz, yz). A ring of radius R should create
approximately 4R ≈ 20 non-zero plaquettes. Gate 4 is conservative.

**Check 5 — Ring depletion is ring-shaped (not spherical collapse):**
```
count(sigma < 0.35 nodes with rho in [R-3, R+3] and |z - z_ring| <= 3) >= 10
```
The sigma-depleted nodes must form a distributed ring structure (at least 10 nodes),
not a single collapsed point.

**Check 6 — Sigma depletion persists from T=500 to T=1000 (not transient):**
```
mean sigma at ring region at T=500 < 0.45
mean sigma at ring region at T=1000 < 0.45
```
The ring depletion must already be established at T=500 (Phase 2 step 200) and
persist to T=1000 (Phase 2 step 700). Both gates must pass.

## Decision rule

**Overall PASS** if all six checks pass.

**Interpretation of PASS:**
The vortex ring is dynamically stable in the v5 QNG substrate over 700 steps of
Channel F (1000 total including Phase 1). With BETA_PHI=0.02, the ring does not
collapse before sigma depletion builds. Despite π₂(S¹) = 0 (no topological
protection), the ring maintains its sigma depletion and ring radius > R/2. This
confirms that matter in 3D QNG can take the form of a dynamically stable vortex
ring, not requiring a topological guarantee.

The stability mechanism: the sigma depletion at the core is maintained by Channel F
as long as the phi phase circulation persists. The two-phase design separates phi
equilibration from the sigma depletion measurement.

This motivates:
- a_M fixing for 3D: measure A_vortex_ring = (sigma_ref - sigma_core) from this simulation
- QNG-CPU-044: ring lifetime measurement (at what T does the ring collapse with BETA_PHI=0.02?)
- QNG-CPU-045: ring self-velocity measurement (quantitative z-drift as function of R)

**Interpretation of FAIL:**
- Check 1 fails: no sigma depletion — phi ring smoothed out before Channel F acts, or
  D_ring too low. Increase gamma_phi or reduce beta_phi further.
- Check 2 fails: bulk sigma depleted below 0.40 — global Channel F effect. Either
  |Z_i| is not close enough to 1 in the bulk, or n_dep is underestimated.
- Check 3 fails: ring collapsed below R/2 — even BETA_PHI=0.02 too strong, ring shrinks
  too fast. Try larger R or smaller beta_phi.
- Check 4 fails: no winding plaquettes — phi has completely smoothed out by T=1000.
- Check 5 fails: depletion not ring-shaped — ring collapsed to a point.
- Check 6 fails: transient depletion — ring decays between T=500 and T=1000.

## Artifact paths

- `07_validation/audits/qng-vortex-ring-3d-reference-v1/report.json`
- `07_validation/audits/qng-vortex-ring-3d-reference-v1/summary.md`
