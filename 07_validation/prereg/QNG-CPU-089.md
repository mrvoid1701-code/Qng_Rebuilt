# QNG-CPU-089

Type: `prereg`
Status: `pending`
Author: `C.D Gabriel`
Date: `2026-04-22`
test_class: `derivation_verification`
hardware: `CPU`
upstream: `QNG-GPU-031f` (orbital attractor <L>~660 at L=28 R=4);
          `QNG-GPU-040` (R=2 and R=6 particle probes);
          `NOTE-QNG-017` (universal <L>=N*beta_phi/2 invariant);
          `DER-QNG-051` (Option R1 pure-XY E_phi)

## Title

L-scan of v8 R1 orbital attractor Lagrangian invariant E_char - falsify
XY-ground-state derivation.

## Purpose

NOTE-QNG-017 observed that `<L> = 2<T_kin> - <H>` on the orbital attractor
equals N*beta_phi/2 within 0.22% at L=28 R=4, across R in {2,3,4,5}.
The conjecture `<L> = N*beta_phi/2` is now derived analytically
(NOTE-QNG-017 section 2.2):

    E_phi_A (R1) = -(beta_phi/(2z)) * Sum_i Sum_{j in N(i)} cos(phi_i - phi_j)

At ferromagnetic ground state on z=6 cubic lattice:
    E_phi_A_ground = -beta_phi * N / 2

Since <T> << |<V>| on the attractor, <L> approx -<V> approx beta_phi*N/2.

## Prediction

If the derivation is correct, E_char scales as:
    E_char(L) = A * L^alpha   with   alpha = 3.00   (extensive in N=L^3)

Specifically:
    L=20 (N=8000)  -> predicted E_char = 240.00
    L=24 (N=13824) -> predicted E_char = 414.72
    L=28 (N=21952) -> predicted E_char = 658.56  (measured 660.00 at R=4)

If measured alpha deviates from 3 by more than 0.1, the XY-ground-state
derivation is falsified and <L> is not substrate-intrinsic but
geometry-specific.

## Configuration

- Input traces: 07_validation/audits/qng-v8-L-scan-R4-L{20,24}-v1/traces.npz
  (produced by tests/gpu/qng_v8_L_scan_probe.py --L 20 / --L 24)
- Reference: 07_validation/audits/qng-v8-particle-probe-v1/traces.npz
  (existing L=28 R=4 at T_run=5000 from GPU-031f)
- Analyzer: tests/cpu/qng_L_scan_E_char_analysis.py
- Burn-in: 500 lu (standard warm-state cutoff)
- E_char formula: `E_char = 2*T_kin.mean() - H.mean()` where
  `T_kin = T_g + T_m + T_phi`

## Gates

- **EXTENSIVE_PASS**: |alpha_fit - 3.0| < 0.10 AND
  RMS residual of power-law fit < 1% of E_char.
  -> XY-ground-state derivation confirmed; Gate A passed.
- **INTENSIVE_PASS**: |alpha_fit| < 0.10 AND E_char(L=20) approx 660.
  -> substrate-intrinsic rest-energy scale (NOT XY-ground-state);
  requires new derivation and is much more surprising.
- **GEOMETRIC_PASS**: alpha_fit in [0.5, 2.5]
  -> ring geometry dominates; E_char depends on ring perimeter/surface;
  inconsistent with both XY-ground-state and intensive interpretations.
- **ANOMALOUS**: alpha_fit not in [-0.2, 0.2] or [2.8, 3.2] and RMS > 5%
  -> any other result invalidates all three simple interpretations.

## Expected wall time

- CPU analysis: <1 second (reads three npz files and does polyfit).
- Upstream data generation (blocking): ~1 hour per L value on current
  GPU (contention with other probes).

## Artifacts

- Analysis script: tests/cpu/qng_L_scan_E_char_analysis.py
- Report: 07_validation/audits/qng-L-scan-E-char-v1/report.json
- Memory hook: project_lagrangian_invariant_derived.md (update on
  completion with gate outcome).

## Falsifier direction

This test is structurally falsifying. The XY-ground-state derivation
makes a SHARP numerical prediction (alpha = 3 exactly; coefficient
= beta_phi/2 exactly) that either survives or is ruled out. There is
no free parameter to absorb a moderate deviation.
