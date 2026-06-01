---
test_id: QNG-CPU-092
title: Edge-stochastic hbar probe (Gabriel intuition)
category: theory-probe
hardware: cpu
status: prereg
date: 2026-04-22
upstream:
  - NOTE-QNG-018 (qng-edge-stochastic-program-v1.md)
  - DER-QNG-051 (R1 XY cure)
  - project_lagrangian_invariant_derived.md
---

# QNG-CPU-092: Edge-stochastic hbar probe

## Inputs
- Pure XY vacuum on z=6 cubic, L in {8, 10}
- beta_phi = 0.06
- Edge phase offset xi_ij added to XY cosine:
  cos(phi_i - phi_j + xi_ij)
- Two modes:
  - QUENCHED: xi_ij frozen at t=0, xi_ij ~ N(0, eps)
  - DYNAMIC: xi_ij resampled every dt_noise step, tau_c via OU process
- eps in {0.0, 0.01, 0.05, 0.10, 0.30, 1.00}
- T_sim = 200 lu (dt = 0.05 -> 4000 steps)
- Yoshida4 symplectic integrator (v8 canonical)

## Outputs
- <L> = 2<T> - <H> per (mode, eps)
- Var(phi_i) over bulk nodes
- edge-averaged <cos(phi_i - phi_j + xi_ij)>
- action autocorrelation, energy drift

## Gates
- **X1 (quenched null)**: <L> / <L>_eps=0 deviates at most eps^2 (quenched disorder preserves H up to eps^2 corrections).
- **X2 (dynamic response)**: measure slope d<L>/d eps at small eps. Linear = no hbar; plateau or step = candidate.
- **X3 (coarse-graining)**: compare L=8 and L=10; if X2 signature is intensive (per-volume-independent) -> hbar candidate.

## Tolerances
- H drift < 1% over T=200 lu (symplectic lane baseline)
- Monte Carlo disorder average over 3 seeds per eps (quenched)

## Artifact paths
- `07_validation/audits/qng-edge-stochastic-v1/report.json`
- `tests/cpu/qng_edge_stochastic_probe.py`

## Verdict table template
- X1 PASS/FAIL
- X2 slope value, behavior classification (linear/plateau/step)
- X3 intensive ratio L=10/L=8
