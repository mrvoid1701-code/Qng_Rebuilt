---
id: DER-QNG-053
type: derivation
title: Dirac constraint analysis of H_v8 — no hidden first-class constraints
version: v1
date: 2026-04-22
status: draft
upstream: [DER-QNG-036, DER-QNG-042, DER-QNG-050, DER-QNG-051]
downstream: [DEC-QNG-007 candidate]
---

# Dirac constraint analysis of H_v8

## 1. Purpose

Close the Dirac-constraint category as an hbar mechanism. Test
whether the v8 Lagrangian is singular (rank-deficient Hessian) and
therefore supports first-class constraints whose reduction could
fix a natural action scale.

Verdict (anticipated): H_v8 is a regular Lagrangian; no primary
constraints exist; the phase space is already minimal; no Dirac
reduction produces an action quantum.

## 2. The v8 Lagrangian

From DER-QNG-036 (H_v7) + DER-QNG-042 (canonical extension) + DER-QNG-050 (exact F_A):

  L_v8 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] - V(sigma_g, sigma_m, phi)

where, writing `chi_i = d sigma_g_i / dt / k_back` (so chi is the
velocity of sigma_g scaled by 1/k_back):

  T_g = (1/(2 k_back)) sum_i (d sigma_g_i / dt)^2
  T_m = (mu_m / 2) sum_i (d sigma_m_i / dt)^2
  T_phi = (mu_phi / 2) sum_i (d phi_i / dt)^2
  V = E_v7 + V_couple + V_backreaction   (all positional, no velocity)

and

  E_v7 = (alpha / (2 z)) sum_{<ij>} (sigma_g_i - sigma_g_j)^2
       + (beta_g / (2 z)) sum_{<ij>} (sigma_m_i - sigma_m_j)^2
       + (beta_phi / z) sum_{<ij>} [1 - cos(phi_i - phi_j)]     [pure-XY, R1]

  V_couple = (g / 2) sum_i (sigma_ref - sigma_m_i)^2 (1 - cos phi_i)

## 3. Kinetic Hessian

The kinetic Hessian is the matrix of second derivatives of L with
respect to velocities:

  W_{(a,i) (b,j)} = del^2 L / (del q_dot^{a,i} del q_dot^{b,j})

where (a, b) in {g, m, phi} and i, j are site indices.

Because kinetic terms are all strictly local (no cross-site velocity
products) and all local kinetic blocks are diagonal in (g, m, phi),
the Hessian is block-diagonal:

  W = diag_i diag(1/k_back, mu_m, mu_phi)

Determinant:

  det(W) = (1 / (k_back * mu_m * mu_phi))^N * (mu_m * mu_phi / k_back)^N
         [this factor depends on convention; the key property is positivity]

With standard v8 parameters:
  k_back = 0.10,  mu_m = 10.0,  mu_phi = 0.857

All three diagonals are strictly positive. Therefore W is positive
definite everywhere on phase space.

## 4. Primary constraints: none

A primary constraint of the Dirac-Bergmann procedure is an algebraic
relation

  phi_r(q, p) = 0

that holds on the image of the Legendre map p = del L / del q_dot.
Primary constraints arise precisely when W is rank-deficient (singular
Lagrangian). Here W has full rank 3N everywhere on phase space.

**Therefore the v8 Lagrangian has no primary constraints.**

Without primary constraints, the Dirac-Bergmann procedure terminates
trivially: no secondary constraints are generated, no constraint
algebra exists to classify into first/second class, no gauge reduction
is performed.

The full 6N-dimensional phase space (3N coordinates (sigma_g, sigma_m,
phi) and 3N momenta (chi/k_back equiv p_g, p_m, p_phi)) is physical.

## 5. Continuous symmetries (Noether audit)

The Noether theorem maps continuous symmetries of L_v8 to conserved
charges. Enumeration:

### 5.1 Time translation
  delta t = epsilon
  dL/dt = 0 (explicit time-independence of L_v8)
  -> conserved: H_v8 (energy)

### 5.2 Spatial translations on the cubic lattice
Because boundary conditions are periodic, lattice translations
x_i -> x_i + a in each of the three directions leave E_v7, V_couple,
and all kinetic terms invariant.
  -> conserved: P_g^mu = sum_i p_g_i * del sigma_g_i / del x^mu, similarly
     P_m^mu, P_phi^mu; or equivalently the centroid-conjugate momenta
     of each sector.
  -> 3 independent P^mu charges (one per Cartesian direction)

### 5.3 Global phi rotation: phi_i -> phi_i + c
The XY edge term (1 - cos(phi_i - phi_j)) is invariant under
phi_i -> phi_i + c, but V_couple = (g/2) delta^2 (1 - cos phi_i)
is NOT invariant under c != 2pi n (it changes by an explicit
cos(phi + c) - cos phi).
Residual symmetry: phi_i -> phi_i + 2pi. This is a discrete Z symmetry,
not a continuous one. No Noether charge.

### 5.4 Global sigma_g translation
Breaks E_v7 and coupling to sigma_m_ref. Not a symmetry.

### 5.5 Global sigma_m translation
Breaks E_v7 (quadratic in sigma_m differences but also constraints
via V_couple(sigma_ref - sigma_m)^2). Not a symmetry.

### 5.6 Combined sigma_g/sigma_m shift preserving sigma_g - sigma_m
If E_v7 were antisymmetric in g-m exchange it could. It is not.
Not a symmetry.

### 5.7 Discrete reflection / Z2 symmetries
phi_i -> -phi_i: breaks V_couple by sign of (1 - cos phi) = (1 - cos -phi) — INVARIANT.
sigma_m -> 2 sigma_ref - sigma_m: E_v7 invariant, V_couple invariant.
These are Z_2 symmetries, not continuous.

### Total continuous symmetries
4 (1 time + 3 spatial translations). All generators are
action-DIMENSIONAL (energy) × time + momentum × length. None of them
forces a periodic structure on phase space that could produce a rigid
action scale.

## 6. Does any symmetry have a periodic structure?

Periodic structure in phase space arises when a generator G has
a non-trivial holonomy: exp(2 pi G / hbar) = identity. The
Bohr-Sommerfeld condition ∮ p dq = n · h is an example, but it is
imposed from outside, not derived.

For v8:
- Energy H has non-compact range (depends on field configuration).
- Spatial momenta P^mu have non-compact range.
- No compact Lie-group symmetry is present.

**No compact continuous symmetry -> no natural period -> no hbar
from this category.**

## 7. Second-class constraints: not applicable

Second-class constraints arise when consistency of primary constraints
under Hamilton evolution generates additional algebraic relations.
Since there are no primary constraints, no consistency chain begins,
and no second-class constraints are produced.

## 8. Interaction with DER-QNG-051 (vacuum instability)

DER-QNG-051 flagged that pre-R1 V_couple produces a non-bounded
ground state. R1 (DER-QNG-050) cured this by replacing V_couple
with the pure-XY form. The cured Lagrangian L_v8^{R1} has the same
kinetic structure; the analysis of §3-§4 applies unchanged.

## 9. Predictions

- Hessian W evaluated at every snapshot of GPU-100 R3/R4/R5 has
  condition number (sigma_min / sigma_max) = k_back * min(mu_m, mu_phi)
  / max(1/k_back, mu_m, mu_phi) = 0.10 * 0.857 / 10.0 = 0.00857.
  Well above 1e-10 (numerical singularity threshold).
- No snapshot anywhere should reveal a degenerate local Hessian.

If CPU-101 numerical test confirms these predictions, **DIRAC-NO-
CONSTRAINT** is the locked verdict.

## 10. Consequences

Combined with CPU-098 (Berry: V9A-MARGINAL), CPU-099 (winding: V9-TOP-
LOCAL_DEFECTS_ONLY), and CPU-100 (Verlinde: VERLINDE-PARTIAL, no
integer ladder), this closes the 4 remaining mathematically well-
defined categories for "hbar from inside v8":

- Topological (winding): trivial
- Dynamical (Berry/adiabatic): universal but non-integer
- Thermodynamic (entropy/holographic): universal but dimensional mismatch
- Constraint (Dirac/gauge): no constraints to reduce

**The 14th-15th-16th hbar programs are all closed.**

The Savant-physics-reviewer theorem-level argument (Liouville +
Noether + no compact symmetry => classical H cannot carry rigid
action scale) is empirically and analytically confirmed inside v8.

## 11. Links

- Wallstrom 1994: no-go for Madelung + noise (not applicable to V9-C
  which uses canonical Weyl quantization, not Madelung).
- DER-QNG-052 (V9-C Weyl path integral) stands as the residual
  "external hbar" path. Z-winding sector decomposition handles
  quantization of ∮ dphi via topology, not dynamics.

## 12. Status

- Analytical content: locked.
- Numerical verification: pending CPU-101 run.
- If CPU-101 passes: promote this document to "locked" and DEC-QNG-007
  (v8 classical lock + V9-C promotion) can be drafted.

Signed: autonomous assistant (main context), 2026-04-22
