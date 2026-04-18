# QNG-GPU-003

Type: `test`
ID: `QNG-GPU-003`
Status: `pre-registered`
Author: `C.D Gabriel`
Date: `2026-04-14`
test_class: `ring_decay_emission`

## Objective

Measure what field excitations are emitted when a vortex ring dissolves.
Determines whether ring dissolution is purely dissipative or produces
propagating field perturbations (the QNG analog of meson emission).

Physical question: Delta(1232) -> N(938) + pi requires a "pion" carrier.
In QNG, what IS the pion? Candidate: a sigma_g wave packet (KG field,
confirmed CPU-054), or phi disorder pulse, or purely local sigma_m diffusion.

## Category

`ring_decay_emission`

## Hardware

`GPU`

## Inputs

- v7 update law (DER-QNG-033): full dynamics, NO Channel H
- L=60 cubic box (periodic), single R=5 ring at center (30,30,30)
- Phase1=300 (phi imprint), Phase2_form=1000 (ring formation), Phase3_decay=30000
- Concentric shell masks: r in {0-8, 8-12, 12-16, 16-20, 20-24, 24-28}
- k_gm=0.01, alpha=0.005, gamma_phi=0.005, chi_decay=0.020, k_back=0.10

## Outputs

Per shell, every 500 steps:
- delta_sg(shell, t): mean(sigma_ref - sigma_g) in shell -- gravitational perturbation
- delta_sm(shell, t): mean(sigma_ref - sigma_m) in shell -- matter perturbation
- phi_disorder(shell, t): mean phi disorder in shell -- phase perturbation
- M_ring(t): total ring mass in inner shell (r < 8)
- peak_shell(t): shell with largest delta_sg (wave front position)

## Gates

- WAVE_EMISSION: delta_sg in outer shells (r > 20) exceeds 5e-5 AND
  is > 10% of inner shell signal. Indicates sigma_g wave packet propagates.
- PARTIAL_EMISSION: delta_sg reaches mid shells (r=12-16) only.
- NO_EMISSION: perturbations stay in inner shell (r < 8). Purely local.

## Tolerances

- delta_sg measured to 1e-7 precision (float64)
- Wave speed check: predicted v_s = sqrt(k_back * chi_rel / 6) = 0.0764 lu/step

## Artifact paths

- `tests/gpu/qng_ring_decay_emission_gpu.py`
- `07_validation/audits/qng-ring-decay-emission-v1/report.json`
- `07_validation/audits/qng-ring-decay-emission-v1/summary.md`

## Physical interpretation

WAVE_EMISSION:
  sigma_g is the QNG meson carrier. Ring dissolution emits gravitational
  wave packets. This is the first evidence of a distinct "meson sector"
  in QNG. Propagation speed should match v_s from CPU-054.

NO_EMISSION:
  Dissolution is purely dissipative in current v7. The "pion" requires
  a different mechanism -- possibly: (a) two-ring interaction required
  (virtual meson exchange), (b) v8 Channel H needed for coherent emission,
  or (c) pion is not a sigma_g wave but a phi topological defect.

## Upstream

- DER-QNG-033 (v7 two-field substrate)
- DER-QNG-032 / QNG-CPU-054 (KG wave equation, v_s derivation)
- DER-QNG-038 (baryon resonance ladder, R=5=Delta)
- QNG-GPU-001 (GPU environment confirmed)
