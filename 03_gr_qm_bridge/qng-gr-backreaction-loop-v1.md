# DER-BRIDGE-035 — QM↔GR Back-Reaction Loop Closure

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-028 (CPU-046, QM continuity), DER-BRIDGE-031 (CPU-049, QM→GR)

---

## Motivation

The CPU-049–052 chain established the QM→GR direction:

    div_J_mis_i → E_tt_i  (with e_mis ≈ −0.10 to −0.52 across seeds/N)

This is half of a back-reaction loop. The other half (GR→QM) is:

    E_tt_i → ∂_t(ρ_i)  (curvature feeds back into QM density evolution)

In general relativity, matter sources curvature (QM→GR) AND curvature affects
matter motion (GR→QM). The equivalence principle requires both directions.

If E_tt feeds back into ∂_t(C_eff²) with a non-zero coefficient γ, the loop
closes and we have the first explicit back-reaction object of rebuilt QNG.

---

## The back-reaction equation

Starting from CPU-046's multi-channel continuity:

    ∂_t(C_eff²)_i ≈ -(α_phi·div(J_phi)_i + α_mis·div(J_mis)_i + α_mem·div(J_mem)_i)

We extend with a GR feedback term:

    ∂_t(C_eff²)_i ≈ -(α_phi·div(J_phi)_i + α_mis·div(J_mis)_i + α_mem·div(J_mem)_i)
                    + γ_tt·E_tt_i + γ_xx·E_xx_i

where E_tt_i = Lap(h_xx)_i, E_xx_i = Lap(h_tt)_i are the GR tensor components
at time t (same state from which the QM channels are computed).

If γ_tt ≠ 0 with consistent sign across seeds → GR curvature drives QM evolution.
This closes the QM↔GR back-reaction loop.

---

## Mathematical structure

Using `rollout_two_steps` (same as CPU-046):
- Run to step t (steps-1 iterations)
- Compute at step t: drho, QM channels, GR tensor
- Run one more step to get drho = C_eff²(t+1) - C_eff²(t)

Fit comparison:
- 3-channel baseline: drho ≈ -(α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem)
- 5-channel extended: drho ≈ -(α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem) + γ_tt·E_tt + γ_xx·E_xx

GR tensor at time t:
    asm = assemble_linearized_metric(c_t, phi_t)
    ten = tensorial_proxy(asm)
    E_tt = ten["e_tt"]  (vector of length n_nodes)
    E_xx = ten["e_xx"]

---

## Predictions (pre-registered)

**P1 — GR→QM signal exists**:
    R²(3ch + E_tt) > R²(3ch) on ≥ 4/5 seeds
    (E_tt has predictive power for ∂_t(C_eff²))

**P2 — GR feedback sign is coherent**:
    sign(γ_tt) consistent across ≥ 4/5 seeds
    (coupling direction is structural)

**P3 — E_tt stronger than E_xx as feedback**:
    R²(3ch + E_tt) > R²(3ch + E_xx) on ≥ 3/5 seeds
    (consistent with E_tt being the primary QM↔GR channel)

**P4 — Non-trivial improvement**:
    mean(R²_5ch - R²_3ch) > 0.010
    (GR feedback is more than numerical noise)

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Tier classification

- P1 + P2 pass → Tier-1 (universal back-reaction)
- P1 pass, P2 fail → Tier-2 (topology-dependent)
- P1 fail → no back-reaction signal

---

## Physical interpretation

If the test passes:
- The QM↔GR loop closes: div_J_mis → E_tt → ∂_t(C_eff²) → div_J_mis (cycle)
- γ_tt is the first back-reaction constant of rebuilt QNG
- The complete back-reaction equation is established as a proxy law
- This is the first step toward Problem 5 (back-reaction closure)

The physical picture: local GR curvature E_tt (which QM density flows sourced) feeds back
and drives density redistribution. Positive E_tt (curvature from density outflow) damps
further outflow — a self-stabilizing feedback mechanism.
