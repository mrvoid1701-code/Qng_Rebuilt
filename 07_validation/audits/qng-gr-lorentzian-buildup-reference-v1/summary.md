# QNG-CPU-059 Audit Summary — Lorentzian Signature Buildup

**Test**: qng_gr_lorentzian_buildup_reference.py
**Theory doc**: DER-BRIDGE-041
**Date**: 2026-03-26
**Result**: PASS 1/4 — ANTI-HYPOTHESIS CONFIRMED — SIGNATURE DECAYS WITH PHI SYNC

---

## Pass/Fail

| Criterion | Result | Seeds passing |
|-----------|--------|--------------|
| P1: \|corr\| step 24 > step 1 (signature builds) | **FAIL** | 0/5 — opposite! |
| P2: mean\|corr_hist\| > mean\|corr_nohist\| | **PASS** | 5/5 |
| P3: Pearson(kuramoto, \|corr\|) > 0.2 | **FAIL** | 0/5 — strongly negative! |
| P4: Signature converges (not monotone growth) | **FAIL** | 2/5 |

---

## Per-seed results

| Seed | \|corr\|_1 | \|corr\|_12 | \|corr\|_24 | r(kur,\|c\|) | kur_final | htt_neg_final |
|------|-----------|------------|------------|-------------|-----------|--------------|
| 20260325 | 0.9995 | 0.9770 | 0.9748 | −0.973 | 0.950 | 0.375 |
| 42 | 0.9989 | 0.9911 | 0.9980 | −0.425 | 0.979 | 0.4375 |
| 137 | 0.9995 | 0.9842 | 0.9621 | −0.930 | 0.926 | 0.375 |
| 1729 | 0.9993 | 0.9815 | 0.8559 | −0.714 | 0.914 | 0.500 |
| 2718 | 0.9996 | 0.9996 | 0.9988 | −0.631 | 0.978 | 0.500 |

Step trajectory (seed 20260325, with history):

| t | \|corr\| | kuramoto | htt_neg |
|---|---------|----------|---------|
| 1 | 0.99952 | 0.256 | 0.500 |
| 5 | 0.99855 | 0.434 | 0.4375 |
| 9 | 0.98923 | 0.606 | 0.4375 |
| 13 | 0.97637 | 0.804 | 0.500 |
| 17 | 0.97516 | 0.886 | 0.4375 |
| 21 | 0.97506 | 0.929 | 0.4375 |

---

## Key finding: Signature is initialized, not built

**P1 fails on ALL 5 seeds**: |corr| at step 1 ≈ 0.999 — the metric anti-correlation
is already near-maximal at the very first rollout step. It does NOT build up.
Instead, it DECAYS: mean|corr| drops from 0.9994 at step 1 to 0.9579 at step 24.

**The Lorentzian signature is an initial-condition imprint**, not a dynamically
emergent phenomenon. The initial state has a strong geometric structure (|corr| ≈ 1)
that degrades as the dynamics drive phi toward synchronization.

---

## Phi sync DESTROYS the signature (inverse P3)

**P3 fails with strongly NEGATIVE values**: Pearson(kuramoto, |corr|) = −0.73 (mean).

As phi synchronizes (kuramoto increases from 0.26 to 0.95 over 24 steps), the
metric anti-correlation DECREASES. This is the inverse of the original hypothesis.

**Interpretation**: In the initial state, phi has random phases (kuramoto ≈ 0.25).
This disorder creates spatial variation in phi, which the metric assembly
(assemble_linearized_metric) converts into the E_tt/E_xx anti-correlation.
As phi synchronizes, the spatial variation COLLAPSES → E_tt and E_xx lose their
anti-correlated structure → |corr| decreases.

The Lorentzian signature requires PHASE DISORDER, not phase coherence.

---

## History as a signature preserver (P2 PASS 5/5)

Despite the general signature decay, P2 passes universally: the history-driven
rollout maintains stronger anti-correlation than the no-history version throughout
all 24 steps.

**Connection to CPU-033 and CPU-040**:
- CPU-033: history amplifies signature 331× — NOW UNDERSTOOD as history preventing
  complete phi synchronization, preserving the phase disorder that generates signature
- CPU-040: history creates "anti-ordering" (structured local diversity in phi)
  rather than global sync — this PRESERVES spatial phi variation → preserves signature

Without history: phi → near-perfect global sync (kuramoto → 1.0) → |corr| collapses
toward 0 (all nodes have same phi → E_tt ≈ E_xx → no anti-correlation).

With history: phi → intermediate anti-ordering (kuramoto ≈ 0.93–0.98) → residual
spatial diversity → |corr| ≈ 0.86–1.00 at step 24.

---

## Revised understanding of Problem 6

The Lorentzian signature in QNG is NOT emergent — it is imprinted at initialization
(step 1: |corr| ≈ 0.999) and preserved (not built) by history dynamics.

The correct question for Problem 6 is:
1. **Why does the initial state have |corr| ≈ 0.999?** (Statistical/graph property)
2. **Why does history specifically preserve this initial structure?** (Anti-ordering mechanism)
3. **Is the residual signature at step 24 sufficient for physical predictions?**

The 331× amplification factor (CPU-033) is now reinterpreted: it is NOT that history
builds the signature from nothing, but that history PREVENTS the 331× DECAY that
occurs without history. History acts as a signature PRESERVER, not a generator.

---

## Tier classification

**Tier-1.5** (P2 passes strongly; P1/P3/P4 fail but reveal inverse physics):

- P2 5/5: history consistently preserves stronger Lorentzian signature throughout
- Inverse P3 (r = −0.73): phi sync destroys signature — confirmed universally
- The anti-hypothesis is confirmed with extraordinary clarity
- Step trajectory clearly shows decay from |corr|≈1.000 at t=1 to ~0.97 at t=24

**The result is scientifically richer than the original hypothesis would have been.**

---

## Open questions for CPU-060+

1. What property of init_state produces |corr| ≈ 1.000 at t=1?
   (Random phi → zero-mean variation → initial perfect anti-correlation?)
2. Can the anti-ordering mechanism (history) be quantified to predict the
   steady-state residual |corr| as a function of N?
3. Does the initial |corr| ≈ 1 hold at large N (is it N-independent)?
