---
id: QNG-CPU-095
type: test
category: cpu
hardware: cpu
title: Edge-stochastic temporal correlation probe (OU process)
date: 2026-04-22
status: executed
---

# QNG-CPU-095: OU temporal correlation probe

## Motivation

CPU-092/093/094 closed scalar i.i.d. edge noise: seven distributions
all give Debye-Waller law, no universal scale. NOTE-QNG-018 §8
identifies option (b') — CORRELATED (non-i.i.d.) edge noise — as a
residual structural move. This test probes temporal correlation via
Ornstein-Uhlenbeck.

## Hypothesis

If temporal correlation introduces a new scale, the shift
|Delta <L>|/<L>_0 should plateau or saturate at a universal value
INDEPENDENT of tau_c in some window. Classical motional-narrowing
theory predicts a smooth function of tau_c with no plateau.

## Inputs

- L = 8, z = 6, BETA_PHI = 0.06, MU_PHI = 0.857
- Fixed rms = 0.2 (Debye-Waller regime from CPU-094)
- Scan tau_c in {0.1, 0.5, 1, 2, 5, 10, 50, 1000} lu
- OU: xi(t+dt) = exp(-dt/tau_c) * xi(t) + sqrt(1 - e^(-2dt/tau_c)) * rms * eta
- Yoshida4, dt = 0.05, T_SIM = 150 lu, 2 seeds

## Outputs

- <L> = 2<T> - <H> (time-averaged Lagrangian)
- Var(xi) effective
- <xi(t) * xi(0)> autocorrelation residual at final time
- H_drift %

## Gates

- **G1**: shift/<L>_0 as function of tau_c. Smooth monotone -> classical.
- **G2**: plateau at universal value across tau_c decade -> hbar candidate.
- **G3**: H_drift < 20% for integrator validity.

## Verdict

**OPTION_B_TEMPORAL_FALSIFIED** (2026-04-22):
- shift/L0 varies smoothly from -0.013 (quenched) to -0.023 (peak at tau_c=2)
- Peak at tau_c=2 matches natural phi relaxation ~sqrt(mu_phi/beta_phi) = 3.8 lu
  -> classical stochastic resonance, not ℏ
- No plateau, no universal scale
- H_drift 20% at tau_c=5 (pumping), but below 2% at quenched limit

## Artifact

`07_validation/audits/qng-edge-stochastic-ou-v1/report.json`
