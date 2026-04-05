# QNG Graph Isotropy Assumption v1

Type: `axiom`
ID: `AX-QNG-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State Assumption D2 explicitly: the QNG graph ensemble produces an isotropic
continuum Laplacian in the coarse-graining limit. This assumption underlies every
PDE in the Newtonian limit derivation chain (DER-QNG-012 through DER-QNG-020) and
is the subject of Gap 1 in `DER-QNG-011`.

This document makes D2 precise, states the conditions under which it holds, records
what is known, and declares what must be done to promote it from axiom to derivation.

---

## Statement of Assumption D2

Let `G = (V, E)` be the QNG graph ensemble with node count `N`, coordination number
`z`, and uniform edge weight `w = 1/z`. Define the graph Laplacian:

```
(L_graph f)(i) = sum_{j in N(i)} w * (f(j) - f(i))
               = (1/z) * sum_{j in N(i)} f(j) - f(i)
```

**Assumption D2:** In the limit `Delta_u -> 0`, `N -> infinity` with `N * Delta_u^3`
fixed (constant coarse-graining volume), the coarse-grained graph Laplacian converges
to the isotropic 3D continuum Laplacian:

```
(1/Delta_u^2) * L_graph C_eff(x)  ->  nabla^2 C_eff(x)
```

where `nabla^2` is the standard Euclidean Laplacian in R^3, **isotropic** (no
preferred direction, no anisotropic coefficients).

---

## Where D2 is used

D2 is invoked in:
- `DER-QNG-012` §2.4: passage from discrete update to reaction-diffusion PDE
- `DER-QNG-012` §5: quasi-static Poisson equation (requires 3D isotropic Laplacian)
- `DER-QNG-013` §3: matter source identification in continuum limit
- `DER-QNG-018` §3: Poisson assembly and G_QNG formula

Every formula that contains `nabla^2` in the Newtonian limit chain assumes D2.
If D2 fails (anisotropic Laplacian), the effective Newton's constant `G_QNG` becomes
direction-dependent — ruled out by experiment to better than 1 part in 10^14
(lunar laser ranging, torsion balance tests).

---

## When D2 holds: sufficient conditions

D2 is known to hold exactly for the following graph geometries:

**Case 1 — Regular cubic lattice (z = 6):**
The 3D cubic lattice has discrete Laplacian:
```
(L f)(i,j,k) = f(i+1,j,k) + f(i-1,j,k) + f(i,j+1,k) + f(i,j-1,k)
             + f(i,j,k+1) + f(i,j,k-1) - 6 f(i,j,k)
```
In the continuum limit `Delta_u -> 0`, this converges to `nabla^2 f` exactly, with
no anisotropic corrections at leading order (anisotropic terms appear at order
`Delta_u^2`, suppressed by the lattice spacing squared).

**Case 2 — Face-centered cubic (FCC, z = 12):**
Also produces an isotropic continuum Laplacian. The FCC lattice is the densest
packing of equal spheres and has full cubic symmetry group (O_h).

**Case 3 — Random graph with isotropic degree distribution:**
If edge directions are drawn uniformly from the sphere S^2 and the coordination
number is homogeneous (each node has exactly z neighbors), the expected Laplacian
is isotropic by symmetry of the direction distribution.

**General sufficient condition:**
The coarse-grained Laplacian is isotropic if and only if the graph has the full
rotation symmetry group of R^3 (or a discrete subgroup that is a representation of
SO(3) dense enough to resolve the relevant wavelengths). For a lattice, this requires
at minimum cubic symmetry (O_h group).

---

## Current status in QNG numerics

**QNG-CPU-037 (PASS):** A 3D cubic lattice simulation (N=20, 8000 nodes, z=6) has been
run with a clamped source at center. Results:

- Spherically averaged Yukawa fit: lambda_sphere = 3.746, lambda_pred = 3.416, ratio = 1.097 (within 10%)
- R^2 = 0.9957 — clean exponential Yukawa profile in 3D
- Directional lambdas: (1,0,0) = 3.590, (1,1,0) = 3.770, (1,1,1) = 3.867
- Isotropy ratio max/min = 1.077 — isotropic to within 8%

D2 is numerically supported for the z=6 cubic lattice. The 7.7% anisotropy between
(100) and (111) directions is expected at leading order: for a cubic lattice the
discrete Laplacian has anisotropic corrections at order (Delta_u/lambda)^2. With
lambda ~= 3.4 lattice spacings, these corrections are of order 1/3.4^2 ~= 9%, consistent
with the observed 7.7%.

**Earlier simulations** used a 1D ring (z=2) which is trivially isotropic in 1D.
The 3D result is the first non-trivial check of D2.

---

## What D2 implies for Gap 1

Gap 1 of `DER-QNG-011` reads: "The 3D graph topology is not specified. The
coarse-graining from the discrete update law to a 3D PDE requires a graph with
sufficient symmetry to produce an isotropic Laplacian."

D2 is Gap 1's resolution condition. D2 is **numerically supported** for z=6 cubic lattice (QNG-CPU-037 PASS) and **assumed
for general graph topologies** — not derived from substrate dynamics.

**To promote D2 from axiom to derivation requires one of:**

1. **Spectral argument:** Show that the QNG dynamics selects a graph topology (e.g.,
   via an entropy maximization or stability argument) that has isotropic Laplacian.
   This would require a variational principle for the substrate graph.

2. **Numerical confirmation:** Run a 3D cubic QNG simulation (z=6, N=32^3) and
   verify that the sigma profile from a point source is spherically symmetric to
   within simulation noise. This is the minimal numerical evidence for D2 in 3D.

3. **Symmetry postulate promoted to axiom:** Declare that the QNG substrate is a
   3D regular lattice with z=6 (or another fully symmetric graph), and that this
   choice is part of the theory's ontology, not derived from dynamics. This closes
   Gap 1 by ontological declaration rather than derivation — acceptable if made
   explicit.

---

## Precise characterization of D2 (DER-QNG-024)

`DER-QNG-024` (`qng-graph-isotropy-formal-v1.md`) derives the necessary and sufficient
condition on a graph for D2 to hold at leading order:

**Second-moment condition (SMC):**
```
Σ_j (ê_ij ⊗ ê_ij) = (z/3) · I    for all nodes i
```

where ê_ij is the unit vector from node i to neighbor j.

**Consequences:**
- SMC holds **exactly** for any lattice with octahedral symmetry (O_h): cubic (z=6),
  FCC (z=12), BCC (z=8). D2 is exact at leading order for these.
- SMC holds **approximately** for perturbed or random isotropic graphs, with per-node
  deviation ~ ε_max (perturbation amplitude). The coarse-grained anisotropy at
  physical scales is suppressed by 1/√N_cell → negligible.
- SMC **fails** for graphs with systematic anisotropy (fibers, sheets). These produce
  direction-dependent G_QNG, ruled out experimentally. Excluded from QNG's scope.

## Current standing

D2 is **formally characterized** (Gap 1 status: partially closed). The condition
for D2 is identified (SMC), proven for standard lattices, and shown to hold
approximately for perturbed/random isotropic graphs with quantitative anisotropy
bounds. All Newtonian limit results remain conditional on D2.

**Numerically confirmed:**
- QNG-CPU-037: cubic lattice (z=6, 20³), directional isotropy ratio 1.077 — D2 exact case
- QNG-CPU-039: perturbed cubic (perturbation 0.3, 20³), SMC off-diag < 0.007, octant iso_ratio 1.356 — D2 approximate case
  Results: λ_sphere=3.232 (ratio 0.946 vs pred), SMC diagonal (2.006, 2.005, 1.989) vs target 2.000, off-diag < 0.007

**Remaining open:** D2 for dynamic graphs (edge formation/breaking); Gap 1 is
closed for all static graphs satisfying SMC exactly or approximately.

---

## Cross-references

- Gap 1 program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- SMC derivation: `DER-QNG-024` (`qng-graph-isotropy-formal-v1.md`)
- First use of D2: `DER-QNG-012` §2.4 (`qng-ceff-field-equation-v1.md`)
- G_QNG formula (depends on z from D2): `DER-QNG-018` (`qng-poisson-assembly-v1.md`)
- Cubic lattice test: `QNG-CPU-037`
- Perturbed lattice test: `QNG-CPU-039`
