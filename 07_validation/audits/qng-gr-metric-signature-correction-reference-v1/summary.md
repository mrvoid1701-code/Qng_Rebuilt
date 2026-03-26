# QNG-CPU-058 Audit Summary — Metric Signature Correction

**Test**: qng_gr_metric_signature_correction_reference.py
**Theory doc**: DER-BRIDGE-040
**Date**: 2026-03-26
**Result**: PARTIAL 2/4 — NULL RESULT — METRIC SIGNATURE IS PHI-DRIVEN NOT ρ-DRIVEN

---

## Pass/Fail

| Criterion | Result | Note |
|-----------|--------|------|
| P1: sign(ΔE_tt) consistent | **PASS** (5/5) | **VACUOUS**: mean E_tt = 0 identically |
| P2: sign(ΔE_xx) consistent | **PASS** (4/5) | **VACUOUS**: mean E_xx = 0 identically |
| P3: sign(ΔE_tt) ≠ sign(ΔE_xx) | **FAIL** (0/5) | Both exactly zero |
| P4: \|ΔE_tt\| > 1e-5 | **FAIL** (0/5) | Shifts are < 1e-10 (machine precision) |

---

## Key finding: zero-mean metric proxy

E_tt and E_xx are zero-mean fields by construction. The tensorial_proxy returns
deviations from a reference, such that Σ_i E_tt_i = 0 for any amplitude profile c.
Therefore:

    mean(E_tt(c_GR)) − mean(E_tt(c_QM)) = 0 − 0 = 0 **exactly**

P1/P2 pass vacuously: the "consistent sign" is the sign of machine-precision noise
(effectively testing sign(0) = sign(0)). P1/P2 carry no information.

P4 fails for the same reason: |ΔE_tt| = |0 − 0| = 0 < 1e-5.

This is a test design issue, not a theory failure. The test was pre-registered
with the hypothesis that mean metric shifts would be detectable — they are not,
because E_tt has exactly zero mean.

---

## Informative signal: Pearson correlation shift

The only non-trivial metric diagnostic is Δcorr = corr(E_tt,E_xx)_GR − corr(E_tt,E_xx)_QM:

| Seed | γ_tt | qm_corr | gr_corr | Δcorr |
|------|------|---------|---------|-------|
| 20260325 | −0.00030 | ? | ? | −0.000330 |
| 42 | +0.00032 | ? | ? | +0.000020 |
| 137 | −0.00043 | ? | ? | −0.000620 |
| 1729 | +0.00835 | −0.853 | −0.824 | +0.029953 |
| 2718 | +0.00234 | ? | ? | +0.000160 |

**Pattern**: sign(Δcorr) ≈ sign(γ_tt)

- γ_tt < 0 → Δcorr < 0 (MORE Lorentzian: anti-correlation strengthens)
- γ_tt > 0 → Δcorr > 0 (LESS Lorentzian: anti-correlation weakens)

This is the opposite of what DER-BRIDGE-040 hypothesized. The GR back-reaction
with γ_tt > 0 (typical, from CPU-053) makes the metric SLIGHTLY LESS Lorentzian
at the attractor. But the effect is tiny (|Δcorr| < 0.001 for 4/5 seeds;
seed 1729 alone shows |Δcorr| = 0.030 due to larger γ_tt = 0.00835).

---

## Structural finding

**Metric signature is phi-driven, not ρ-driven.**

The Lorentzian signature of E_tt (timelike nodes: negative E_tt) and E_xx
(spacelike nodes: positive E_xx) is determined by the phase field phi.
The anti-correlation between E_tt and E_xx (corr ≈ −0.85 to −0.97 from CPU-033)
is a geometric property of the phi configuration.

The GR back-reaction modifies ρ (via γ_tt·E_tt iteration), but phi is held
fixed in the FP iteration. Therefore:

1. The nodal MEANS of E_tt and E_xx do not change (both are zero-mean)
2. The PATTERN of E_tt and E_xx barely changes (phi is unchanged)
3. Only the CORRELATION changes slightly (because new c changes coupling weights
   in the metric assembly)

The matter sector (ρ) and geometry sector (phi-driven metric signature) are
**quasi-independent** in QNG at the FP iteration timescale.

---

## Implications for Problem 6 (Lorentzian signature recovery)

The Lorentzian signature does NOT emerge or strengthen through the back-reaction
loop on ρ. To test signature emergence, one would need to track phi evolution
under some driven dynamics — the back-reaction does not affect phi in the
current iteration scheme.

Possible CPU-059 directions:
1. Test phi dynamics under time-step rollout (does phi evolve toward more Lorentzian?)
2. Test corr(E_tt, E_xx) as a function of rollout step count (signature builds up?)
3. Explicitly test whether the phi synchronization (CPU-040) correlates with
   the anti-correlation signature

---

## Design note for future tests

Any test of metric signature correction should use:
- **Nodewise norm** of ΔE_tt: norm(E_tt_GR − E_tt_QM) ≠ mean difference
- **Δcorr**: change in Pearson anti-correlation between E_tt and E_xx
- **Δfrac_htt_neg**: change in fraction of timelike nodes

Not mean(ΔE_tt) which is identically zero by construction.
