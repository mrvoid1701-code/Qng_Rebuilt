---
id: DER-QNG-052
type: derivation
title: v9-C Weyl / path-integral lift of H_v8 — external hbar as quantization postulate
version: v1
date: 2026-04-22
status: draft (V9-C analytic branch; complementary to V9-A empirical branch)
upstream:
  - DER-QNG-042 (H_v8 canonical Hamiltonian)
  - DER-QNG-049 (Channel F canonical)
  - DER-QNG-050 (DER-QNG-050 exact F_A)
  - DER-QNG-051 (Option R1 pure-XY E_phi)
  - NOTE-QNG-018 (edge-stochastic program closure)
  - DEC-QNG-006 (edge-stochastic decision, v9 charter opened)
  - NOTE-QNG-019 (v9 charter)
  - NOTE-QNG-020 (4-agent consultation; savant advocates V9-C directly)
---

# V9-C: Weyl / path-integral lift of H_v8

## Status

This is the "honest minimum" branch of v9: accept that H_v8 is a classical
Hamiltonian field theory and lift it to a quantum theory via standard
canonical quantization, with an EXTERNAL hbar that is a constant of nature
rather than an emergent quantity. It does not replace V9-A (topological
protection), but runs in parallel: if V9-A fails (CPU-098 verdict
V9A-FAIL or V9A-QUANTIZED_CONTINUOUS), V9-C provides the clean close.

## 1. The classical substrate

Per DER-QNG-042 (with amendments A1 Option E^2 and DER-QNG-049, 050, 051),
the classical phase space is

  {q_a, p_a} = {(sigma_m_i, pi_m_i), (phi_i, pi_phi_i) : i = 1..N}
  (sigma_g_i, chi_i : gradient-flow non-canonical; see §5)

with Hamiltonian (pure-XY R1 form)

  H_v8 = T_m + T_phi + E_v7[sigma_g, chi, sigma_m] + E_phi_R1[phi] + V_couple

  T_m      = sum_i (pi_m_i)^2 / (2 mu_m)
  T_phi    = sum_i (pi_phi_i)^2 / (2 mu_phi)
  E_phi_R1 = -(beta_R1/z) sum_{<ij>} cos(phi_i - phi_j),  beta_R1 = BETA_PHI/2
  V_couple = (g/2) sum_i (sigma_m_ref - sigma_m_i)^2 (1 - cos phi_i)

  E_v7 contains the sigma_m quadratic neighbor potential (DER-QNG-042-prereqs),
  the Channel F potential E_F = (GAMMA_PHI/2) sum_i dis_i sigma_m_i^2
  (DER-QNG-049), and the chi/sigma_g gradient-flow terms.

The canonical Poisson brackets are

  {sigma_m_i, pi_m_j} = delta_{ij},   {phi_i, pi_phi_j} = delta_{ij}.

## 2. Weyl quantization

Replace Poisson brackets with commutators divided by i*hbar:

  [sigma_m_i, pi_m_j] = i hbar delta_{ij},   [phi_i, pi_phi_j] = i hbar delta_{ij}.

hbar is an EXTERNAL constant (not derived from H_v8). Operators on each site:

  sigma_m_i   acts as multiplication by sigma_m_i on L^2(R)_i
  pi_m_i      acts as -i hbar d/dsigma_m_i
  phi_i       acts as multiplication (periodic variable, phi in [-pi,pi])
  pi_phi_i    acts as -i hbar d/dphi_i on L^2(S^1)_i

Hilbert space (per site): H_i = L^2(R, dsigma) ⊗ L^2(S^1, dphi).
Full Hilbert space: H = tensor_i H_i.

The quantum Hamiltonian H_hat is obtained by Weyl symmetrization of H_v8.
Kinetic terms are already Weyl-ordered; V_couple is function only of
commuting operators (sigma_m_i, phi_i), so no ordering ambiguity.
Neighbor-cos terms in E_phi_R1 and E_v7 involve only commuting operators
at distinct sites.

Result: H_hat is a well-defined self-adjoint operator on H.

## 3. Path-integral partition function

Equivalent formulation via the Feynman-Kac path integral:

  Z(beta, V) = integral D[phi] D[pi_phi] D[sigma_m] D[pi_m]
                exp( (i / hbar) integral_0^T dt [sum pi_m sigmaDot_m + sum pi_phi phiDot - H_v8] )

For thermodynamics, Wick-rotate t -> -i*tau:

  Z_E(beta_T) = integral D[phi] D[sigma_m] exp( -(1/hbar) integral_0^{hbar*beta_T} dtau L_E )

with Euclidean Lagrangian L_E = sum (mu_m/2) sigmaDotSq_m + (mu_phi/2) phiDotSq + V_eff
and V_eff = E_v7 + E_phi_R1 + V_couple after integrating out the momenta.

## 4. Wallstrom compatibility

Wallstrom 1994 forbids recovering Schrodinger from Madelung hydrodynamics
+ classical noise on the modulus/phase pair (rho, S) because phase
quantization oint dS = 2*pi*n*hbar is not enforced by classical noise.

V9-C does NOT touch Madelung. The phi Z-winding sector is quantized
via integer winding sector decomposition of H^1(T^3, Z): the path
integral decomposes into topological sectors

  Z = sum_{n in Z} Z_n,      Z_n = restriction to winding n.

In each sector, phi is a single-valued classical variable after choosing
a branch. Weyl quantization within a sector is standard. The restriction
that oint dphi = 2*pi*n is structural (topological), not added by hand.

Therefore V9-C is NOT Madelung + noise; Wallstrom 1994 does not apply.

## 5. Gradient-flow sector (sigma_g, chi)

These are NOT canonical in v7/v8. They evolve via gradient flow driven by
chi's relaxation and sigma_g's diffusion+back-reaction. Two options for v9-C:

**Option V9-C-I**: leave (sigma_g, chi) as classical environmental background
fields that parametrize the quantum H_hat. This is an "open system"
quantization: the quantum (sigma_m, phi) sector evolves on a classical
gravitational background.

**Option V9-C-II**: promote (sigma_g, chi) to canonical pairs too, adding
conjugate momenta pi_g, pi_chi with kinetic terms and replacing the
gradient-flow dissipation with Langevin noise. Quantization then yields
a full quantum theory of the four-field substrate. This is a STRUCTURAL
EXTENSION of v8 (not just a lift), and would need its own prereg.

The minimum v9-C commits to Option I only. Option II is a future extension.

## 6. Tree-level spectrum (flat vacuum)

Expand phi = 0 + delta_phi, sigma_m = sigma_m_ref + delta_sm around flat
vacuum. Quadratic action:

  S^{(2)} = integral dt [ sum_i mu_phi/2 (pi_phi_i)^2/mu_phi^2 - beta_R1/(2z) sum_{<ij>} (phi_i - phi_j)^2 + ... ]

The phi mode dispersion at flat vacuum (GPU-020 Stage A, PASS):

  omega^2(k) = (beta_R1 / (2 mu_phi z)) * 4 sum_{mu} sin^2(k_mu / 2)

In the Brillouin zone, maximum omega at k = (pi, pi, pi) with
omega_max = sqrt(2 * beta_R1 / mu_phi). Speed of phonon: c_phi =
sqrt(beta_R1 / (z * mu_phi)) = c_m = c_g (DER-QNG-042-prereqs §3.3).

Quantization: phonons are harmonic oscillators with energy E_n = n*hbar*omega(k).

## 7. One-loop structure

On the ring background (non-flat), the phi mass is m_phi^2 = (g/mu_phi) *
(sigma_m_ref - sigma_m)^2 locally (Jackiw-Rebbi, DER-QNG-046, GPU-035).
Phi modes trapped in the vicinity of the ring experience a position-dependent
effective potential; treat within a local-density approximation (LDA) or
WKB.

One-loop corrections:
- sigma_m self-energy from virtual phi loops: Sigma_{sm}(k) ~ g^2 * hbar
  * integral d^3k' ... (beta_R1/z k'^2 + m_phi^2)^{-1}. This renormalizes
  sigma_m's effective potential.
- phi self-energy from sigma_m loops and V_couple vertex: similar hbar
  corrections, logarithmically divergent in flat limit, regulated by
  lattice.
- Ghost/BRST not needed (no gauge symmetry — Tesla U(1) falsified,
  DER-QNG-044; only global Z winding remains).

## 8. Correspondence with lattice scalar + sine-Gordon

The (phi, pi_phi, sigma_m, pi_m) sector in flat background reduces to:
- phi sector alone: lattice XY model with kinetic term = standard
  canonical lattice scalar field (Minkowski or Euclidean).
- With V_couple: each site has a sine-Gordon potential V_SG(phi) =
  g/2 * (sigma_m_ref - sigma_m)^2 * (1 - cos phi). In the flat sigma_m
  limit this is 2D sine-Gordon mapped onto a 3+1D lattice; its exact
  scalings are known (Coleman 1975, Dashen-Hasslacher-Neveu 1975).
- Full (phi, sigma_m) coupled: a version of the Peierls-Frohlich or
  the Thirring-sine-Gordon duality with dynamical matter field sigma_m.

## 9. Constraint against naive Madelung reduction

The wave function Psi[sigma_m, phi] is NOT Madelung-decomposable in
general. Attempting Psi = sqrt(rho) exp(i*S/hbar) on the joint manifold
forces S to be single-valued on the phi cylinder, which is incompatible
with the Z-winding sector decomposition of §4. Wallstrom blocks the
naive decomposition; V9-C bypasses it via topological sector sum.

## 10. Predictions / falsifiers

Under V9-C, hbar is EXTERNAL. Matching to SM values:

- hbar ~ 1.055e-34 J*s is NOT derived.
- Planck length sqrt(hbar G / c^3) — G enters via QNG Newtonian limit
  (DER-QNG-019: G = beta/z in substrate units); ratio is testable only
  after fixing substrate-to-SI translation.

Falsifiers of V9-C (as a minimal option):
- (A) If V9-A (CPU-098) returns V9A-PASS with theta_0 that renders
  hbar emergent from the topology of ring orbits, V9-C becomes
  redundant.
- (B) If the one-loop correction to phi self-energy is UV-unrenormalizable
  on the QNG lattice (i.e. no continuum limit survives), V9-C loses its
  theoretical foundation and the program must be reformulated.
- (C) If the Weyl-quantized spectrum of H_hat on flat vacuum fails to
  match the classical GPU-020 Stage A phi dispersion (relative error
  > 1% at any k), the quantization prescription is inconsistent.

## 11. Status and next steps

- This document is a draft; it needs rigorous derivation of:
  - The canonical commutators in the presence of the phi periodicity (§2).
  - The ring-background one-loop integrals (§7).
  - The explicit matching of tree-level spectrum to GPU-020 data (§10-C).

- Option V9-C-I (env background) is sufficient for a "quantization of
  matter on QNG gravity" program. Option V9-C-II (full four-field
  quantum substrate) is ambitious and out of scope for this v1.

- Gabriel review required before v9-C becomes load-bearing: the central
  philosophical claim is that QNG becomes "classical substrate
  underlying quantum mechanics" rather than "fundamental theory from
  which hbar emerges". This is smaller than the aspirational claim but
  honest given the 13-program negative record (DEC-QNG-006).

## 12. Relation to V9-A (running in parallel)

V9-A (QNG-GPU-100 + QNG-CPU-098) tests whether the ring orbital
attractor carries an action quantum that V9-C would take as input.
Independent of V9-A's outcome, the Weyl lift described here is a
well-defined quantization of H_v8. V9-A-PASS upgrades V9-C from
"external hbar" to "hbar fixed by topology"; V9-A-FAIL leaves V9-C
as the honest residual path.
