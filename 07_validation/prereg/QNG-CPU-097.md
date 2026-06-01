---
id: QNG-CPU-097
type: test
category: cpu
hardware: cpu
title: Compact U(1) lattice-gauge edge probe (Program 9-gauge)
date: 2026-04-22
status: executed
---

# QNG-CPU-097: Compact U(1) lattice-gauge probe

## Motivation

Option (a) of NOTE-QNG-018 §8: promote edges from passive geometry to
dynamical U(1) gauge field with conjugate momentum. Test whether
CLASSICAL coupled (phi, A_ij, E_ij) system produces a universal action
scale emergence.

Agent audit 2026-04-22 (3/4 consensus): classical LGT requires
[A_ij, E_ij] = i hbar to quantize Wilson loops; without this
commutator imposed, continuous classical dynamics is expected.
This test empirically checks that prediction inside QNG.

## Hypothesis

If classical gauge coupling alone produces universal scale, <L>/N
should plateau at beta_phi/2 + delta_gauge independent of mu_E, mu_B
across decades of variation. If it tracks (mu_E, mu_B) smoothly,
classical LGT confirms agent prediction.

## Inputs

- L = 6, N = 216, edges = 648, plaquettes = 648
- BETA_PHI = 0.06, MU_PHI = 0.857
- Scan mu_E in {0.1, 1.0, 10.0}, mu_B in {0.1, 1.0, 10.0}
- Yoshida4, dt = 0.05, T_SIM = 100 lu
- Full Hamiltonian:
    H = T_phi + T_E - (beta_phi/z) cos(phi_i - phi_j - A_ij)
        + mu_B [1 - cos(W_plaq)]

## Outputs

- <L>/N, <H>/N per (mu_E, mu_B)
- <cos W>, Var(W): plaquette winding statistics
- H_drift

## Gates

- **G1**: CV of <L>/N across (mu_E, mu_B) < 1% -> UNIVERSAL (hbar candidate)
- **G2**: CV > 10% -> classical, no hbar
- **G3**: H_drift < 20% at stiff point (mu_E=10, mu_B=10)
- **G4**: <cos W> shows clustering near integer multiples -> discrete flux quanta

## Verdict

**OPTION_A_LATTICE_GAUGE_FALSIFIED** (2026-04-22):
- CV(<L>/N) = **199.85%** across (mu_E, mu_B)
- Range: [0.029 (recovers XY pure at stiff gauge), 1.45 (soft gauge dominates)]
- <cos W> ≈ 0.98-0.99 everywhere — small-angle Gaussian fluctuations
- Var(W) ≈ 0.02-0.04 — no integer-flux clustering
- H_drift 0.29% at (mu_E=10, mu_B=10); grows to 177% at mu_E=1, mu_B=0.1
- At stiff-gauge limit (mu_E,mu_B) -> (inf, inf), <L>/N -> beta_phi/2 = 0.030
  exactly — recovers ungauged XY. Confirms gauge dynamics are continuous
  classical oscillations, not quantum.

**Agent audit CONFIRMED**: classical compact U(1) LGT coupled to phi
produces continuous <L>/N tracking coupling constants. No universal
scale. Quantization requires [A, E] = i hbar imposed externally.

## Implication for NOTE-QNG-018

Options (a) lattice gauge, (b') spatial correlation, (b') temporal
correlation (CPU-095/096/097) all FALSIFIED. Only option (c) remains:
accept H_v8 is classical, impose canonical quantization via path
integral or Weyl correspondence.

## Artifact

`07_validation/audits/qng-edge-gauge-v1/report.json`
