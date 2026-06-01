# QNG-GPU-100

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel` (autonomous execution 2026-04-22)
Date: `2026-04-22`
test_class: `v9a_phase_space_probe`
hardware: `GPU`
upstream_derivation: `NOTE-QNG-019 (v9 charter, V9-A option)`
prerequisites: `GPU-031f orbital attractor (R=4, T=5000 lu)`

## Title

V9-A phase-space probe — full (sigma_m, pi_m, phi, pi_phi) trajectory
capture across R in {3,4,5} orbital attractors for downstream
computation of candidate geometric-phase / action-quantum integrals.

## Background

GPU-031f confirmed R=4 orbital attractor with <M_ring>_t = 309.45,
period 185.2 lu, duty 38.5%. Existing artifact `m_series.npz` at
`07_validation/audits/qng-v8-r1-long-time-v1/` saves only the scalar
M_ring(t) time series; it is insufficient for the V9-A minimal test
proposed in `08_governance/v9-charter-v1.md`: compute closed-loop
integrals on phase-space trajectories. GPU-100 re-runs R in {3,4,5}
with full-state checkpointing.

## Hypothesis (V9-A)

If the ring orbital attractor supports a structurally protected action
quantum, closed loops in projected phase space should have line
integrals clustering at integer multiples of some theta_0 that is
independent of R.

## Design

Per R (same protocol as GPU-031f):
- Phase 1: T_P1 = 300 lu, v_couple=False (phi vortex formation)
- Phase 2: T_P2 = 5000 lu, v_couple=True (orbital run)

Loop: R in {3, 4, 5}.

Fixed parameters:
- L = 20, DT = 0.025
- CHI_DECAY_V7 = 0.020, K_BACK = 0.10
- BETA_PHI = 0.06, MU_PHI = 0.857, MU_M = 10.0, G_V_COUPLE = 0.22
- exact_a = 'r1'

Sampling in Phase 2:
- Reduced observables every 1 lu: M_ring, P_M (= -sum pi_m / N),
  COM_x/y/z of sigma_m deficit, R_eff, H components
- Full-field snapshots every 10 lu (500 snapshots per R):
  sigma_m, pi_m, phi, pi_phi

## Inputs / outputs

Script: `tests/gpu/qng_v9a_phase_space_probe.py`

Output: `07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/`
- `final_state.npz`
- `reduced_series.npz` (t, M_ring, P_M, COM, R_eff, H per 1 lu)
- `snapshots.npz` (t_snap, sm_stack, pim_stack, phi_stack, piphi_stack per 10 lu)
- `report.json` (orbital stats + raw integral candidates)

## Structural gates (GPU-100 only — V9-A verdict delegated to CPU-098)

- G1: all three R runs complete without NaN; |Delta H|/H < 2% per 1000 lu
- G2: orbital attractor confirmed at each R (duty > 5%, convergence_rel < 10%)
- G3: snapshots written, openable, field shapes consistent

GPU-100 PASS = G1 AND G2 AND G3.

## Abort conditions

- min(sigma_g) < 0.025 (v8 effective-theory boundary)
- |Delta H|/H > 10% per 1000 lu
- disk write failure

## Estimated runtime

~1-2 h per R on RTX 4080; ~3-6 h total.

## Downstream

QNG-CPU-098 consumes GPU-100 artifacts and computes candidate loop
integrals. The V9-A scientific verdict is CPU-098's responsibility.
