# QNG-GPU-042

Type: `prereg`
Status: `pending`
Author: `C.D Gabriel`
Date: `2026-04-22`
test_class: `derivation_verification`
hardware: `GPU`
upstream: `QNG-GPU-031f` (orbital attractor <L>=660 at L=28 R=4 beta_phi=0.06);
          `NOTE-QNG-017` (universal <L>=N*beta_phi/2 invariant);
          `DER-QNG-051` (Option R1 pure-XY E_phi)

## Title

beta_phi-scan of v8 R1 orbital attractor Lagrangian invariant - Gate B
falsifier of linear scaling in beta_phi.

## Purpose

NOTE-QNG-017 conjectures <L>/N = beta_phi/2 exactly, derived from the
R1 pure-XY ground-state energy on cubic lattice z=6:

    E_phi_A_ground = -beta_phi * N / 2

Gate A (L-scan, QNG-CPU-089) tests the N-scaling.
Gate B (this prereg) tests the beta_phi-scaling: does <L> scale LINEARLY
in beta_phi with slope N/2?

## Prediction

For fixed L=28, R=4, varying beta_phi in {0.03, 0.06, 0.12}:

| beta_phi | predicted E_char (beta_phi * N / 2) | ratio target |
|----------|-------------------------------------|-------------:|
| 0.03     | 329.28                              | 1.000        |
| 0.06     | 658.56                              | 1.000        |
| 0.12     | 1317.12                             | 1.000        |

Measured at beta_phi=0.06: E_char = 660.00 (ratio 1.002).

If any ratio deviates from 1 by more than 2%, the linear-in-beta_phi
conjecture is falsified. If all three match to <2%, Gate B passes.

Note: Changing beta_phi also changes c_phi = sqrt(beta_phi/(3*mu_phi)):
- beta_phi=0.03 -> c_phi = 0.108 (matches lighter effective inertia)
- beta_phi=0.06 -> c_phi = 0.153 (nominal)
- beta_phi=0.12 -> c_phi = 0.216

mu_phi is held fixed to isolate beta_phi scaling. DER-QNG-042-prereqs
matching condition c_g=c_m=c_phi is thus broken (intentional for this
diagnostic).

## Configuration

- Integrator: Yoshida4, DT=0.025
- exact_a='r1' (DER-QNG-051 Option R1 pure-XY)
- Phase 1 (no V_couple): T_P1=300 lu
- Phase 2 (full v8): T_P2=1000 lu
- Tracking: T_run=2000 lu, burn-in 500 lu
- L=28 R=4 (matches existing reference)
- beta_phi override: qng.BETA_PHI = <value>
- Ring cache keyed by beta_phi tag (fresh formation per value)

## Gates

- **LINEAR_PASS**: |ratio(beta_phi)/1 - 1| < 0.02 for ALL three values
  -> NOTE-QNG-017 linear conjecture confirmed; <L> = N*beta_phi/2 is
  parameter-robust; XY-ground-state derivation verified.
- **SUB_LINEAR**: ratio monotonically decreases with beta_phi
  -> corrections O(beta_phi^2) present; derivation is a leading-order
  approximation but not exact.
- **SUPER_LINEAR**: ratio monotonically increases with beta_phi
  -> unexpected anharmonic contributions dominate; requires new theory.
- **NON_MONOTONIC / SATURATION**: ratio non-monotonic or plateaus
  -> new regime structure; possibly a phase transition in beta_phi.

## Expected wall time

- Per beta_phi value: ~22 min (T_P1+T_P2+T_run = 3300 lu at L=28)
- Total for 3 values (sequential): ~66 min on single GPU

## Artifacts

- Script: tests/gpu/qng_v8_beta_phi_scan.py
- Audit: 07_validation/audits/qng-v8-beta-phi-scan-{beta}-v1/
- Analysis: extend qng_L_scan_E_char_analysis.py with beta-phi branch
  OR inline report.json parse.
- Memory hook: project_lagrangian_invariant_derived.md (update with
  Gate B outcome).

## Falsifier direction

Structurally falsifying - no free parameter. Derivation predicts
E_char = N * beta_phi / 2 EXACTLY (modulo small positive corrections
from ring winding and kinetic excitations, bounded below 1% from
L=28 R=4 reference). A clear power-law deviation or saturation
immediately refutes the XY-ground-state interpretation.
