# DER-BRIDGE-036 — GR→QM Back-Reaction Coupling Large-N Probe

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-035 (CPU-053), DER-BRIDGE-034 (CPU-052)

---

## Motivation

CPU-053 established the GR→QM back-reaction:
    E_tt_i → ∂_t(C_eff²)_i   with γ_tt ≈ +0.003–0.008 (5/5 seeds, Tier-1)

CPU-052 showed the QM→GR coupling e_mis saturates at large N:
    |e_mis(N=64)| = 0.134 (×0.84 per doubling, saturation regime)

**Open question**: Does γ_tt follow the same sparse-graph law as e_mis?

Two scenarios:
(a) γ_tt also saturates at large N → both coupling constants finite in continuum
(b) γ_tt vanishes faster than e_mis → GR→QM direction is UV-only

The product γ_tt · |e_mis| has physical meaning: it is the strength of the
full back-reaction loop. If both saturate, the loop closes in the continuum.

---

## Theoretical claim

By symmetry of the back-reaction mechanism, γ_tt should follow the same
sparse-graph law as e_mis: both are driven by local divergence signals
that weaken with graph density. Therefore:

    γ_tt(N) ~ f(N)   with f decreasing (same qualitative trend as e_mis)

But γ_tt could saturate faster (γ_tt is an indirect effect: GR field feeds
back into QM, two steps removed from the raw mismatch signal).

---

## Predictions (pre-registered)

**P1 — GR→QM signal persists at N=32**:
    R²(3ch + E_tt) > R²(3ch) on ≥ 4/5 seeds at N=32

**P2 — γ_tt decreases with N (sparse-graph law)**:
    mean γ_tt(N=32) < mean γ_tt(N=8) on majority of seeds (≥ 3/5)

**P3 — Sign stable across N**:
    sign(γ_tt) consistent across N ∈ {8, 16, 32} on ≥ 4/5 seeds

**P4 — γ_tt non-zero at N=32**:
    mean γ_tt(N=32) > 0.001  (non-vanishing)

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Loop strength metric

Define: loop_strength(N) = mean|γ_tt(N)| × mean|e_mis(N)|

If both saturate, loop_strength(∞) > 0 → the back-reaction loop closes in the continuum.
If γ_tt vanishes faster, loop_strength(∞) → 0 → loop is UV-only.

---

## N values tested

N ∈ {8, 16, 32} × 5 seeds = 15 runs
(N=64 excluded for speed; consistent with CPU-046/047 which used N={8,16,32})
