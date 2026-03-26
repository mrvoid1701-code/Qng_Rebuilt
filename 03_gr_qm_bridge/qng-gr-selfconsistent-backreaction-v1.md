# DER-BRIDGE-039 — Self-Consistent Back-Reaction: Nonlinear Fixed-Point

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-038 (CPU-056), DER-BRIDGE-037 (CPU-055)

---

## Motivation

CPU-056 found |Pearson(δρ, E_tt)| > 0.99 on all 5 seeds and concluded:

    δρ ≈ K · η · γ_tt · E_tt

But this relied on a **linear approximation**: E_tt was computed once from the
rollout final state and held fixed across all K iterations. The self-consistent
equation requires re-evaluating E_tt at each step as c (and hence ρ) evolves:

    ρ_{k+1} = ρ_k + η · [a_mis·dJ_mis(ρ_k) + a_mem·dJ_mem(ρ_k) + γ_tt·E_tt(ρ_k)]

where E_tt(ρ_k) = tensorial_proxy(assemble_linearized_metric(c_k, phi))["e_tt"]
is re-computed from the current density c_k = sqrt(ρ_k) at each k.

**Questions**:

1. Does the self-consistent iteration still converge?
2. Is the self-consistent attractor ρ*_sc close to the linear attractor ρ*_lin?
   (i.e., is the linear approximation quantitatively valid?)
3. Does Pearson(δρ_sc, E_tt_final) remain high?
   (i.e., does the geometric imprint survive nonlinear feedback?)
4. How much does E_tt change across the K iterations?
   (i.e., is the linearization a good approximation at all?)

---

## Self-consistent iteration scheme

Two iterations run per seed per comparison:

**Linear (CPU-056 variant)**:

    E_tt^(0) = tensorial_proxy(asm(c_0, phi))["e_tt"]   # computed once
    ρ_{k+1} = ρ_k + η·[a_mis·dJ_mis(ρ_k) + a_mem·dJ_mem(ρ_k) + γ_tt·E_tt^(0)]

**Self-consistent (this test)**:

    E_tt^(k) = tensorial_proxy(asm(c_k, phi))["e_tt"]   # re-computed each step
    ρ_{k+1} = ρ_k + η·[a_mis·dJ_mis(ρ_k) + a_mem·dJ_mem(ρ_k) + γ_tt·E_tt^(k)]

Both: K=30, η=0.05, same initial ρ_0 = rollout final state.

---

## Theoretical predictions

**Convergence (P1)**: The self-consistent iteration should still converge.
Since γ_tt is small (|γ_tt| ≈ 0.001–0.008), the GR feedback is a small
perturbation on the QM dynamics. The QM attractor is already stable
(CPU-055); adding a small nonlinear perturbation should not destroy convergence.

**Attractor shift (P2)**: ρ*_sc ≈ ρ*_lin because E_tt(ρ_k) ≈ E_tt(ρ_0) for
small η. The density barely changes from ρ_0 across 30 iterations (CPU-055:
fp_shift ≈ 0.001), so E_tt changes by O(fp_shift) which is small.

**Geometric imprint (P3)**: Pearson(δρ_sc, E_tt_final) should remain high.
Even if E_tt evolves, the dominant direction of evolution is still E_tt — the
feedback loop reinforces the spatial structure.

**E_tt dynamics (P4)**: E_tt does change across iterations, but by a small
relative amount (scaling as η · γ_tt · ||∂E_tt/∂ρ||). This tests whether
the linear approximation is self-consistent.

---

## Protocol

For each seed in {20260325, 42, 137, 1729, 2718}:

1. Run rollout_final → (c_0, phi, mismatch, mem, adj)
2. Estimate (a_mis, a_mem, g_tt) from two-step rollout
3. Run linear GR iteration (K=30) → ρ*_lin, record E_tt_0
4. Run self-consistent GR iteration (K=30) → ρ*_sc, record E_tt_final
5. Compute:
   - sc_converges: δ_norms decreasing in self-consistent run
   - attractor_close: ||ρ*_sc - ρ*_lin||_2
   - Pearson(δρ_sc, E_tt_final) where δρ_sc = ρ*_sc - ρ*_QM_only
   - E_tt_drift: ||E_tt_final - E_tt_0||_2 / ||E_tt_0||_2

Pass criteria:

- P1: sc_converges on ≥ 4/5 seeds (δ_norms decreasing)
- P2: attractor_close < 0.005 on ≥ 4/5 seeds (linear approx valid)
- P3: |Pearson(δρ_sc, E_tt_final)| > 0.5 on ≥ 4/5 seeds (imprint persists)
- P4: E_tt_drift > 0.001 on ≥ 3/5 seeds (non-trivial E_tt evolution)

---

## Theoretical significance

**If P1+P2+P3 all pass**: The linear approximation is valid; the self-consistent
attractor is essentially the linearized one; the geometric imprint is robust.
The CPU-056 result is not an artifact.

**If P3 fails but P1+P2 pass**: The geometric imprint breaks down nonlinearly
even though the attractors are close — suggests cancellations in the self-consistent
E_tt that wash out the spatial correlation.

**If P1 fails**: The self-consistent iteration diverges — nonlinear GR feedback
can destabilize the QM attractor for some seeds. Would revise stability assessment.

**If P4 fails**: E_tt barely changes (ratio < 0.001) — linear approximation is
exact to high precision. The nonlinear test is trivially consistent with linearized.

---

## Falsifiability

- P1 fails → self-consistent destabilization: γ_tt too large for some seeds
- P2 fails → nonlinear attractor significantly displaced from linear one
- P3 fails → spatial structure is linear-approximation artifact
- P4 fails → E_tt essentially frozen (linear approx perfect)
