# QNG-CPU-101

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel` (autonomous execution 2026-04-22)
Date: `2026-04-22`
test_class: `v9_dirac_constraint_audit`
hardware: `CPU`
upstream_derivation: `DER-QNG-042 (v8 canonical Hamiltonian)`
prerequisites: `DER-QNG-036, DER-QNG-042, DER-QNG-050`

## Title

Dirac constraint analysis on H_v8 — audit whether the v8 phase space
harbors primary or secondary first-class constraints whose reduction
could fix an action scale.

## Background

Dirac's constraint analysis identifies when a Lagrangian is singular
(det(Hessian_{q-dot q-dot}) = 0) and reduces the phase space via
primary + consistency-chain constraints. If the reduced phase space
inherits a natural symplectic structure whose fundamental 2-form
has period 2π·hbar, that would be a structural origin of hbar.

For v8 the claim to test is: the Hessian of L_v8 with respect to
(sigma_g_dot, sigma_m_dot, phi_dot, chi_dot) has full rank on all of
phase space, so there are NO primary constraints, NO secondary
constraints, and therefore NO Dirac reduction. If correct, this
closes the Dirac category as an hbar mechanism.

## Design

### Analytical part (primary)

Write Lagrangian corresponding to H_v8:
  L_v8 = T_g[chi] + T_m + T_phi - V_full

where:
  T_g[chi] = (k_back/2) sum_i chi_i^2       (chi = conjugate of sigma_g)
  T_m = (1/(2 mu_m)) sum_i pi_m_i^2
  T_phi = (1/(2 mu_phi)) sum_i pi_phi_i^2
  V_full = E_v7 + V_couple

Convert to velocity form via Legendre transform:
  chi_i ≡ d(sigma_g_i)/dt / k_back
  pi_m_i ≡ mu_m * d(sigma_m_i)/dt
  pi_phi_i ≡ mu_phi * d(phi_i)/dt

Compute Hessian matrix W_{ab} = del^2 L / (del q_dot^a del q_dot^b).
This is block-diagonal across sites (local kinetic terms) with
diagonal blocks per site:
  diag(1/k_back, mu_m, mu_phi)

For k_back > 0, mu_m > 0, mu_phi > 0 (all physically positive),
det(W) = (1/k_back * mu_m * mu_phi)^N > 0.

Therefore L_v8 is REGULAR (not singular); Legendre transform is
invertible globally; no primary constraints arise.

### Numerical verification

Write `tests/cpu/qng_cpu101_dirac_hessian.py`:

1. Load cached ring + random ring configurations from
   `07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/snapshots.npz`
2. Construct the site-local Hessian W = diag(1/k_back, mu_m, mu_phi)
3. Compute smallest and largest singular values across all sites and
   all snapshots
4. Gate: sigma_min(W) / sigma_max(W) > 1e-10 at all sites and all
   snapshots.

If gate passes, Hessian is uniformly non-degenerate → no primary
constraint anywhere on phase space → no Dirac reduction.

### Continuous symmetries audit

Enumerate candidate continuous symmetries of L_v8:

- **Time translation**: yes → energy conservation (already assumed)
- **Lattice translation (periodic BC)**: yes → 3 conserved linear momenta P_x, P_y, P_z
- **Global U(1) phi → phi + c**: BROKEN by V_couple = (g/2)(delta)^2(1-cos phi).
  Residual symmetry is Z_{2pi}: phi → phi + 2 pi. This is discrete.
- **Global U(1) sigma**: BROKEN by E_v7 (quadratic).
- **Sigma_g → sigma_g + c**: BROKEN by coupling to sigma_m_ref.
- **Higher-order rotations**: none.

Total continuous symmetries: 4 (time + 3 translations).
Noether generators per Hamilton equations: H, P_x, P_y, P_z.
These generators are all dimensionally compatible with (energy, momentum).
None is action-dimensional or periodic; none can quantize anything.

## Gates

- **DIRAC-NO-CONSTRAINT**: Hessian non-degenerate everywhere (sigma_min/sigma_max > 1e-10);
  no primary constraints; no secondary constraints; continuous
  symmetries = 4 (time + 3 spatial). **Dirac category closed as hbar mechanism.**
- **DIRAC-HIDDEN-CONSTRAINT**: any numerical site has sigma_min/sigma_max < 1e-10 →
  investigate further (treat as alarm).

## Artifacts

- Analytical doc: `04_qng_pure/qng-dirac-constraint-analysis-v1.md`
- Numerical script: `tests/cpu/qng_cpu101_dirac_hessian.py`
- Output: `07_validation/audits/qng-cpu101-dirac-v1/`
  - `hessian_check.json`
  - `REPORT.md`

## Downstream

- If DIRAC-NO-CONSTRAINT: 16th hbar program closed; Wallstrom+
  Liouville+Noether+discrete-topology+thermodynamic+Dirac blockade
  fully confirmed. V9-C becomes obligatory (not optional).
- If DIRAC-HIDDEN-CONSTRAINT: investigate the specific degeneracy
  and test whether it produces rigid action scale.
