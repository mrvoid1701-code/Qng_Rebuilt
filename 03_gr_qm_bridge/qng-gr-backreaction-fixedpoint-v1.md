# DER-BRIDGE-037 — Back-Reaction Fixed-Point Iteration

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-035 (CPU-053), DER-BRIDGE-036 (CPU-054)

---

## Motivation

CPU-053/054 established the back-reaction equation:

    ∂_t(ρ_i) ≈ -(α_mis·dJ_mis_i + α_mem·dJ_mem_i) + γ_tt·E_tt_i

with loop_strength ≈ 0.00119 (finite, subcritical).

The fixed point of this equation is:

    0 = -(α_mis·dJ_mis* + α_mem·dJ_mem*) + γ_tt·E_tt*

where starred quantities are evaluated at the fixed-point density ρ*.

**Open question**: Does this equation have a non-trivial attractor?
Starting from the rollout final state, does iterating the back-reaction
equation converge to a fixed point ρ*? And does adding GR back-reaction
(γ_tt·E_tt) shift the attractor compared to QM-only?

---

## Iteration scheme

Starting from final rollout state (C_eff_0, phi, mismatch_0, mem_0):

**QM-only iteration** (baseline):
    ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis_k + α_mem·dJ_mem_k))

**QM+GR iteration** (with back-reaction):
    ρ_{k+1} = ρ_k + η·(-(α_mis·dJ_mis_k + α_mem·dJ_mem_k) + γ_tt·E_tt_k)

where:
- η = 0.05 (step size; small enough to avoid divergence)
- E_tt_k = tensorial_proxy(assemble_linearized_metric(c_k, phi))["e_tt"]
  (phi held fixed; only ρ updated)
- C_eff_k = sqrt(clip(ρ_k, 0, 1)) after each step
- Convergence metric: ||Δρ_k||₂ = ||ρ_{k+1} - ρ_k||₂
- Run for K=30 iterations

α_mis, α_mem, γ_tt are estimated from the same seed's rollout data
(same as CPU-046/053 protocol).

---

## Predictions (pre-registered)

**P1 — QM-only iteration converges**:
    ||Δρ_k|| decreases from k=0 to k=29 on ≥ 4/5 seeds
    (QM continuity has an attractor)

**P2 — QM+GR iteration converges**:
    ||Δρ_k|| decreases with GR back-reaction on ≥ 4/5 seeds
    (back-reaction preserves convergence)

**P3 — GR back-reaction shifts the fixed point**:
    ||ρ*_QM+GR - ρ*_QM||₂ > 0.001 on ≥ 3/5 seeds
    (GR feedback changes the attractor location)

**P4 — GR back-reaction speeds convergence**:
    ||Δρ_29||_QM+GR < ||Δρ_29||_QM on ≥ 3/5 seeds
    (GR helps stabilize faster)

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Expected results

- P1: PASS — QM channels form a contractive map near the attractor
- P2: PASS — loop_strength < 1 guarantees subcritical gain; GR is a perturbation
- P3: PASS — γ_tt·E_tt is nonzero, must shift equilibrium
- P4: uncertain — GR could help or hinder depending on phase alignment

---

## Physical interpretation if passes

The QNG back-reaction equation has a non-trivial attractor:
- QM current divergences converge to a fixed pattern
- GR curvature response shifts this pattern by a calculable amount
- The fixed point ρ* is the first "ground state" prediction of rebuilt QNG
