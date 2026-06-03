# QNG Hopfion Candidate — Topological Analysis

Type: `derivation`
ID: `DER-QNG-036`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-08`

---

## Inputs

- [qng-two-field-substrate-v1.md](qng-two-field-substrate-v1.md) — DER-QNG-033 (v7 two-field substrate)
- [qng-gap8-stability-analysis-v1.md](qng-gap8-stability-analysis-v1.md) — DER-QNG-034 (Gap 8 stability)

---

## Motivation

CPU-065 showed that the ring (vortex circle) cannot simultaneously satisfy:
- Gap 8 stability (CHI_DECAY large → chi small → E~R^1 only)
- Kinetic mass recovery (chi large → H~R² spectrum)

An alternative particle candidate was proposed: the **Hopfion** — a 3D topological soliton
with bipolar field structure (field lines enter south pole, exit north pole of a torus).
Key property: stable under CONSERVATIVE dynamics — does not need dissipation to survive.

This derivation asks: can the existing QNG v7 substrate support Hopfion topology WITHOUT
adding new fields?

---

## Topological review

**Current ring:** phi is S¹-valued. The vortex ring carries topological charge from:
  pi_1(S¹) = Z   (winding number around the ring core)

**Hopfion:** requires charge from:
  pi_3(S²) = Z   (Hopf invariant — how field lines link in 3D)

At first glance these seem different. But consider the PAIR (sigma_m, phi) in v7:

  sigma_m ∈ [0,1]   (real, bounded)
  phi ∈ S¹ = [-π, π]   (phase)

Together, define the complex field: Psi = sigma_m * exp(i*phi)

This maps each node to a point in the UNIT DISK D² ⊂ C.
In QNG, sigma_m → 0 at the vortex core (ring depletes sigma_m).

**Key observation:** If sigma_m = 0 everywhere at infinity (outside any finite region),
then all boundary points map to the same point (0 ∈ D²). This compactifies R³ to S³,
and D² with boundary collapsed to a point is homeomorphic to S².

Therefore: Psi: S³ → S² is well-defined IF sigma_m → 0 at boundary.

This is exactly the setting for the Hopf invariant Q ∈ pi_3(S²) = Z.

**Conclusion: the (sigma_m, phi) pair in v7 ALREADY supports Hopf topology.**
No new fields are needed. The Hopf charge counts how many times the map Psi: S³ → S²
wraps around S².

---

## Hopfion initial condition

The simplest Q=1 Hopfion is a toroidal configuration with TWO winding numbers:
  p = poloidal winding (around the tube cross-section) = 1  [same as current ring]
  q = toroidal winding (around the ring circumference) = 1  [NEW — not in current ring]

For the current vortex ring: p=1, q=0 → Hopf charge Q = p*q = 0 (trivial)
For the simplest Hopfion:   p=1, q=1 → Hopf charge Q = 1 (non-trivial)

**Initial condition for phi (Hopfion Q=1):**

  phi(x,y,z) = p * atan2(z, rho - R)     [poloidal angle around ring tube]
             + q * atan2(y, x)            [toroidal angle around ring axis]

  where rho = sqrt(x² + y²), R = ring radius.

For current ring: phi = 1 * atan2(z, rho-R) + 0 * atan2(y,x)
For Q=1 Hopfion: phi = 1 * atan2(z, rho-R) + 1 * atan2(y,x)

The toroidal term adds a TWIST to the phase as you travel around the ring.
This twist makes adjacent field lines wind around each other → Hopf linking.

---

## Physical picture

The Hopfion field lines (level sets of phi) form closed circles. Due to the toroidal
winding, each circle is LINKED with every other circle (Hopf fibration property).

Viewed along the z-axis (ring axis):
- South region (z < 0): phi lines converge from below
- North region (z > 0): phi lines diverge upward
- This is the BIPOLAR JET structure identified by the theory author

The sigma_m depletion forms a torus at radius R from center. The chi field,
responding to sigma_m depletion, forms a jet along the z-axis — exactly like a
neutron star / magnetar's bipolar electromagnetic jets.

---

## Why Hopfion might be stable where ring is not

The current ring dissolves in conservative dynamics because:
- Energy E(sigma_m) has no barrier preventing the ring from expanding/contracting
- Derrick's theorem: in 3D, field theory with only quadratic terms has no stable solitons
- The ring's topological charge (winding number) can be reduced by "escaping to infinity"

The Hopfion is protected differently:
- Hopf charge Q is a GLOBAL invariant — you cannot unlink the field lines locally
- To dissolve Q=1 Hopfion, you need a global rearrangement of field lines
- This requires crossing an energy barrier (unlike the ring which can shrink continuously)
- In the Skyrme-Faddeev model, Hopfions are provably stable solitons

In QNG terms: the additional toroidal winding (q=1) adds a topological barrier that
prevents the sigma_m depletion from simply expanding away. The field lines must
maintain their linking, which constrains the geometry.

---

## Energy scaling prediction

For Hopfions in the Skyrme-Faddeev model:
  E(Q) ~ Q^(3/4)   [Vakulenko-Kapitanski bound]

For Q=1: E ~ 1
For Q=2: E ~ 2^(3/4) = 1.68
For Q=4: E ~ 4^(3/4) = 2.83

Compare to:
- Current ring: E ~ R^1 (string tension)
- v5 ring: H ~ R^2 (kinetic)
- Hopfion: E ~ Q^(3/4) (sub-linear in charge)

The Q^(3/4) scaling is DISTINCT from both R^1 and R^2. If confirmed numerically,
it would be a genuine new prediction of QNG with Hopfion particles.

---

## Testable prediction (CPU-066)

Initialize phi with q=1 twist (Hopfion Q=1) vs q=0 (standard ring), same R.
Run v7 Phase 1 + Phase 2. Check:
1. Does the Hopfion survive longer than the ring in conservative dynamics?
2. Does sigma_m show bipolar chi jet structure?
3. Is the energy higher than the ring (Hopfion has more topological content)?

If the Hopfion survives in conservative dynamics where the ring does not → major finding.
If it dissolves → topology alone is insufficient without Skyrme-type stabilization term.

---

## Required Skyrme stabilization (if needed)

If Hopfion dissolves, a Skyrme-type term is needed in the energy:
  E_Skyrme = e² * sum_{i<j} (F_ij)²
  where F_ij = (nabla_i phi) × (nabla_j phi) [field strength tensor]

This term is quartic in derivatives and stabilizes against collapse.
In QNG, this could be implemented as a phi-update correction:
  phi_i += skyrme_coeff * [some 4th-order gradient term]

This is a potential CPU-067 if CPU-066 shows dissolution.

---

## Cross-references

- CPU-059: ring dissolves in 50 conservative steps
- DER-QNG-033: v7 two-field substrate
- DER-QNG-034: Gap 8 stability
- CPU-065: DELTA_m cannot recover kinetic mass
- Skyrme-Faddeev model: Hopfions as baryons (external reference)
- Vakulenko-Kapitanski 1979: Q^(3/4) energy bound for Hopfions
