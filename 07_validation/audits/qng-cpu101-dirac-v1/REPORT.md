---
id: AUDIT-QNG-CPU-101
type: audit
title: CPU-101 Dirac-constraint audit — DIRAC-NO-CONSTRAINT (16th hbar category closed)
version: v1
date: 2026-04-22
status: locked
scope: H_v8 kinetic-Hessian rank + Noether-continuous-symmetry enumeration
---

# CPU-101 Dirac-Constraint Audit — Verdict

## Summary: DIRAC-NO-CONSTRAINT

The v8 Lagrangian is REGULAR: its kinetic Hessian is state-independent
and positive-definite (eigvals {0.857, 10.0, 10.0}, condition number
0.0857 >> 1e-10). No primary constraints; no secondary constraints;
no Dirac reduction possible. Continuous symmetries = 4 (time + 3
spatial translations). None produces a rigid action scale.

**16th hbar program closed.**

## Analytical result (DER-QNG-053)

Site-local kinetic Hessian:
  W_site = diag(1/k_back, mu_m, mu_phi) = diag(10.0, 10.0, 0.857)

Full lattice Hessian = block-diagonal, 3N x 3N, rank 3N.
No sites have degenerate block (W is state-independent, not a
function of (sigma_g, sigma_m, phi)).

## Numerical verification

Per-R snapshot kinetic energies (non-negative, finite, everywhere):

| R | T_m range | T_phi range |
|---|---|---|
| 3 | [1.33, 3.66] | [3.59, 7.29] |
| 4 | [1.55, 3.98] | [3.69, 7.19] |
| 5 | [1.84, 4.08] | [4.23, 7.18] |

All finite, all positive, R-agreed within factor ~2. Confirms that
Legendre map p = mu * q_dot is invertible at every phase-space point
sampled by GPU-100.

## Continuous symmetry audit

| Symmetry | Status | Noether charge |
|---|---|---|
| Time translation | YES | H_v8 (energy) |
| Translation x | YES | P_x |
| Translation y | YES | P_y |
| Translation z | YES | P_z |
| Global phi U(1) | BROKEN by V_couple | discrete Z_{2pi} only |
| Global sigma_g shift | BROKEN by E_v7 | — |
| Global sigma_m shift | BROKEN by E_v7 + V_couple | — |

Total continuous: 4. All generators are (energy) or (momentum).
None compact. No natural period in phase space.

## Consequence for hbar program

Combined verdicts:

| Probe | Category | Verdict |
|---|---|---|
| CPU-098 | Dynamical (Berry) | V9A-MARGINAL (universal but non-integer) |
| CPU-099 | Topological (H_1) | V9-TOP-LOCAL_DEFECTS_ONLY (trivial sector) |
| CPU-100 | Thermodynamic (Verlinde) | VERLINDE-PARTIAL (universal but non-integer) |
| CPU-101 | Constraint (Dirac) | DIRAC-NO-CONSTRAINT (Hessian regular) |

All four remaining mathematically well-defined categories closed.
The Savant-physics-reviewer theorem-level argument (Liouville +
Noether + no compact symmetry => classical H cannot produce rigid
action scale) is now empirically AND analytically confirmed.

**V9-C (DER-QNG-052 Weyl path integral with external hbar) is the
obligatory residual path.** Z-winding sector decomposition handles
quantization of ∮ dphi via topology, not dynamics.

## Decision flow

DEC-QNG-007 (v8 classical lock + V9-C promotion) is fully supported
by this probe cluster. Pending only Gabriel sign-off.

## Artifacts

- Analytical: `04_qng_pure/qng-dirac-constraint-analysis-v1.md` (DER-QNG-053)
- Numerical: `tests/cpu/qng_cpu101_dirac_hessian.py`
- Output: `07_validation/audits/qng-cpu101-dirac-v1/hessian_check.json`

Signed: autonomous assistant (main context)
Locked: 2026-04-22
