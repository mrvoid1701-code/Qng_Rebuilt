# QNG-CPU-098

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel` (autonomous execution 2026-04-22)
Date: `2026-04-22`
test_class: `v9a_berry_analysis`
hardware: `CPU`
upstream_derivation: `NOTE-QNG-019 (v9 charter, V9-A option)`
prerequisites: `QNG-GPU-100 artifacts`

## Title

V9-A Berry-integral analysis — compute candidate closed-loop integrals
on GPU-100 phase-space trajectories at R in {3,4,5} and test for
R-invariant action quantum.

## Background

The v9 charter option V9-A proposes that S_Berry = integral over one
orbit of pi_m d sigma_m may, on the closed orbital attractor, reduce
to a topologically protected action quantum. GPU-100 provides the
phase-space data; CPU-098 is the analysis that converts data into a
verdict.

Savant-physics-reviewer (2026-04-22 consultation, NOTE-QNG-020) argues
on theorem-level grounds that this integral is continuous real-valued
phase-space area and cannot be an action quantum without external
quantization. CPU-098 tests that claim empirically.

## Design

Load `reduced_series.npz` and `snapshots.npz` from
`qng-v9a-phase-space-v1/R{3,4,5}/`.

Detect orbital cycles in M_ring(t) via zero-crossings of (M_ring - <M_ring>).

For each cycle k at each R, compute four candidate loop integrals:

### Candidate 1: zero-mode action

S1_k = oint_cycle_k P_M dM_ring

where P_M = -(1/N) sum_i pi_m_i is the canonical momentum conjugate
to the zero-mode sum_i sigma_m_i.

### Candidate 2: full-field action

S2_k = integral_cycle_k sum_i pi_m_i * (d sigma_m_i / dt) dt
     = -2 integral_cycle_k T_m dt

This is the total kinetic-action contribution from the sigma_m sector
over one cycle.

### Candidate 3: phi winding-weighted action

S3_k = integral_cycle_k sum_i pi_phi_i * (d phi_i / dt) dt
     * n_winding_i

where n_winding_i is the local phi Z-winding around the ring core.
Tests whether topological sectors modulate the action.

### Candidate 4: reduced COM action

S4_k = oint_cycle_k P_COM . dR_COM

where R_COM is the center-of-mass of the sigma_m deficit, P_COM its
conjugate.

## Gates (V9-A verdict)

For each candidate S_j in {S1, S2, S3, S4}:

- **V9A-PASS**: across R in {3,4,5}, the per-cycle mean <S_j>_cycles is
  consistent with integer multiples of a single theta_0:
  |<S_j>(R) / theta_0 - round(<S_j>(R)/theta_0)| < 0.05 for all R
  AND within-R cycle-to-cycle CV < 10%.
- **V9A-QUANTIZED_CONTINUOUS**: per-cycle means are R-dependent but
  cycle-to-cycle CV < 10% at each R (a classical adiabatic invariant,
  not a quantum).
- **V9A-FAIL**: cycle-to-cycle CV > 20% at any R (no conserved
  adiabatic action exists for the loop).

Report all four candidates independently. V9A passes overall if AT
LEAST ONE candidate reaches V9A-PASS.

## Auxiliary diagnostics

- Per-cycle energy <H> variation as adiabatic-invariant consistency check
- Orbit reconstruction quality (integral of dM_ring closes to zero per cycle)
- Snapshot time-spacing (10 lu) adequacy for integration accuracy
  (compare trapezoid vs Simpson on 1-lu reduced series)

## Artifacts

- Script: `tests/cpu/qng_v9a_berry_analysis.py`
- Output: `07_validation/audits/qng-v9a-berry-analysis-v1/`
  - `cycles_R{3,4,5}.json` (per-cycle integrals + stats)
  - `report.json` (verdict per candidate + overall V9A status)
  - `fig_phase_space.png` (M_ring vs P_M loop, one per R)

## Downstream

- If V9A-PASS: promote V9-A to candidate derivation DER-QNG-052
  (topological action quantum) and open a full Hamiltonian modification
  program.
- If V9A-FAIL or V9A-QUANTIZED_CONTINUOUS: close V9-A as 14th failed
  hbar program; default to V9-C (path integral with external hbar).
  savant-physics-reviewer 2026-04-22 argument upheld.
