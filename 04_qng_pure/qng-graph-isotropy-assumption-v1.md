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

All CPU reference scripts use a **1D ring** (N nodes, z = 2, periodic boundary). On
a ring, the Laplacian is trivially isotropic in 1D by symmetry. The 1D results
confirm the functional form of the screened Poisson equation but do not probe the
3D isotropy of D2.

No 3D simulation has been run in the current rebuild. The 3D case requires:
- A 3D graph with N^3 nodes (minimum N ~ 32 for meaningful Laplacian fitting)
- z = 6 (cubic) or z = 12 (FCC) coordination
- Source at center, profile measured as function of 3D distance r
- Isotropy test: compare profile along (1,0,0), (1,1,0), (1,1,1) directions

---

## What D2 implies for Gap 1

Gap 1 of `DER-QNG-011` reads: "The 3D graph topology is not specified. The
coarse-graining from the discrete update law to a 3D PDE requires a graph with
sufficient symmetry to produce an isotropic Laplacian."

D2 is Gap 1's resolution condition. D2 is currently **assumed**, not derived.

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

## Current standing

D2 is an **open assumption** (Gap 1 status: open). All Newtonian limit results
(DER-QNG-012 through DER-QNG-020) are conditional on D2. Results are labeled
"valid under D2" throughout.

The functional form of the screened Poisson equation, the identity G_QNG = alpha *
lambda^2, and the alpha-Lambda identification are all independent of the specific
graph topology and hold whenever D2 holds. The quantitative prefactor in G_QNG
(specifically the GRAV-C2 convention a * a_sigma = 2pi) depends on the coordination
number z, and z is set by the graph topology assumed under D2.

---

## Cross-references

- Gap 1 program: `DER-QNG-011` (`qng-newtonian-limit-program-v1.md`)
- First use of D2: `DER-QNG-012` §2.4 (`qng-ceff-field-equation-v1.md`)
- G_QNG formula (depends on z from D2): `DER-QNG-018` (`qng-poisson-assembly-v1.md`)
- Lorentzian signature recovery: `qng-lorentzian-signature-proxy-v1.md`
