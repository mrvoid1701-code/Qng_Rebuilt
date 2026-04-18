# QNG-GPU-002

Type: `test`
ID: `QNG-GPU-002`
Status: `pre-registered`
Author: `C.D Gabriel`
Date: `2026-04-14`
test_class: `ring_transition`

## Objective

Test whether an R=5 ring (Delta(1232)) undergoes a ring-to-ring transition
to an R=4 ring (N(938)) as it dissolves — the QNG analog of Delta -> N + pi.

Physical motivation: dissolution rate != decay width Gamma. A physical decay
requires a final state. In QNG, Delta -> N + pi corresponds to:
  R=5 ring -> R=4 ring + phi-wave packet

This test checks whether phi winding can migrate from R=5 topology to R=4
topology in a shared substrate.

## Category

`ring_transition`

## Hardware

`GPU`

## Inputs

- v8 update law (DER-QNG-039): Channel H + v7 back-reaction
- L=60 cubic box (periodic), Phase-2 = 60000 steps
- R=5 ring at position A = (15, 30, 30): no Channel H (metastable)
- R=4 ring at position B = (45, 30, 30): with Channel H (stable)
- k_gm = 0.01, alpha=0.005, gamma=0.005
- Spatial windows: W_5 = sphere of radius 12 around A; W_4 = sphere of radius 10 around B

## Outputs

- M_5(t): ring mass in W_5 window
- M_4(t): ring mass in W_4 window
- Q_5(t): phi winding proxy in W_5 (disorder magnitude in ring cross-section)
- Q_4(t): phi winding proxy in W_4
- final_status: {M_5_final, M_4_final, transition_seen}

## Gates

- TRANSITION: M_4 remains stable (late_rate < 0.001) after M_5 has decreased by > 50%
- NO_TRANSITION: M_4 dissolves at same rate as M_5 (no selectivity)
- INDEPENDENT: rings evolve independently (no mass/phi exchange)

## Tolerances

- M measured to nearest 0.01 substrate units
- Rate measured as dM/dt over 1000-step windows

## Artifact paths

- `tests/gpu/qng_ring_transition_gpu.py`
- `07_validation/audits/qng-ring-transition-v1/report.json`
- `07_validation/audits/qng-ring-transition-v1/summary.md`
- `07_validation/audits/qng-ring-transition-v1/run.log`

## Physical interpretation

TRANSITION result: phi winding is mobile; R=5 can convert to R=4 + emission.
This is the zero-parameter prediction of decay width ordering (not magnitude).

NO_TRANSITION result: decay width requires multi-ring interaction; single-box
test is insufficient. Need R=5 ring in presence of target (separate experiment).

INDEPENDENT result: rings do not interact via shared substrate at this k_gm.
Increase k_gm or reduce separation.

## Upstream

- DER-QNG-039 (qng-native-update-law-v8.md) — v8 update law
- DER-QNG-038 — baryon resonance ladder (R=4=N, R=5=Delta)
- QNG-GPU-001 — GPU environment confirmed
