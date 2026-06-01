---
id: QNG-CPU-096
type: test
category: cpu
hardware: cpu
title: Edge-stochastic spatial correlation probe
date: 2026-04-22
status: executed
---

# QNG-CPU-096: Spatial correlation probe

## Motivation

Extension of CPU-095 (temporal OU) to SPATIAL correlation. Tests
option (b') of NOTE-QNG-018 §8 closure statement.

## Hypothesis

Spatially correlated edge noise may produce universal prefactor
A(l_corr) that plateaus at some length — a hbar candidate scale.
Alternative: A grows monotonically with l (classical amplification).

## Inputs

- L = 8, z = 6
- rms in {0.05, 0.1, 0.2, 0.3}
- l_corr in {0, 1, 2, 4} lu
- Field generated via FFT kernel smoothing of white Gaussian, renormalized to unit per-site variance
- Projected onto edges by direction
- Quenched + dynamic (noise_resample every 20 steps)

## Outputs

- |shift|/<L>_0 per (rms, l_corr, mode)
- Power-law fit A, p in |shift|/<L>_0 = A * rms^p
- H_drift

## Gates

- **G1**: p ≈ 2 across all l -> Debye-Waller universal form (not hbar)
- **G2**: A(l) monotonic / saturated at physical universal value -> hbar candidate
- **G3**: H_drift < 20% for integrator validity

## Verdict

**OPTION_B_SPATIAL_FALSIFIED** (2026-04-22):
- l=0, 1: A ≈ 0.34-0.57, p ≈ 2.04 -> standard Debye-Waller
- l=2 quenched: A = 0.431 (27% amplification vs i.i.d.)
- l=2 dynamic: A = 1.408, H_drift 45% at rms=0.3 -> destabilization
- l=4 dynamic: p = -0.012 (flat!) but H_drift 236% at rms=0.05 -> integrator break, not physical plateau
- l=4 quenched: p = 0.160 (near-flat) BUT variance saturates at xi ≈ constant field = twisted boundary condition, not hbar

No universal scale. Amplification is classical (Debye-Waller prefactor
depends on correlation volume); saturation at large l is integrator
breakdown / twisted-BC artifact.

## Artifact

`07_validation/audits/qng-edge-stochastic-spatial-v1/report.json`
