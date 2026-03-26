# DER-BRIDGE-040 — Back-Reaction Metric Signature Correction

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-039 (CPU-057), DER-BRIDGE-038 (CPU-056)
**Connects to**: CPU-033 (Lorentzian signature proxy, QNG-CPU-033)

---

## Motivation

CPU-033 established that the QNG assembled metric has a Lorentzian signature proxy:

    h_tt ≈ −0.009  (negative time-time component — timelike)
    h_xx ≈ +0.014  (positive space-space component — spacelike)
    corr(h_tt, h_xx) ≈ −0.97  (strong anti-correlation)
    history amplification factor ≈ 331×

CPUs 053–057 established the GR back-reaction:

    δρ = ρ*(QM+GR) − ρ*(QM) ≈ K·η·γ_tt·E_tt

where E_tt = h_tt is exactly the time-time metric component.

**Key question**: Does the GR back-reaction shift the assembled metric in the
direction of stronger Lorentzian signature — i.e., does it make h_tt more
negative and h_xx more positive?

Since δρ ∝ γ_tt·h_tt, the GR correction concentrates or depletes density
at nodes with large |h_tt|. This changes c* = sqrt(ρ*), which feeds back
into the assembled metric at the GR attractor. The resulting ΔE_tt and ΔE_xx
test whether back-reaction is a Lorentzian-signature-enhancing mechanism.

---

## Metric signature correction

Define:

    E_tt(c) = mean_i [ tensorial_proxy(asm(c, phi))["e_tt"] ]
    E_xx(c) = mean_i [ tensorial_proxy(asm(c, phi))["e_xx"] ]

Then the metric signature corrections are:

    ΔE_tt = E_tt(c*_GR) − E_tt(c*_QM)
    ΔE_xx = E_xx(c*_GR) − E_xx(c*_QM)

where c*_QM = sqrt(ρ*(QM)) and c*_GR = sqrt(ρ*(QM+GR)) are the QM-only and
GR-corrected attractor amplitudes.

**Lorentzian correction criterion**: sign(ΔE_tt) < 0 AND sign(ΔE_xx) > 0

This means the GR correction makes the time component more negative (more
timelike) and the space component more positive (more spacelike) — enhancing
the Lorentzian signature of the emergent metric.

---

## Theoretical prediction

From δρ ≈ γ_tt·E_tt·(K·η) and E_tt = h_tt < 0 (from CPU-033 baseline):

- If γ_tt > 0 (most seeds, CPU-053): δρ < 0 at timelike nodes → density drops
  at timelike loci → c* decreases where h_tt < 0
- The metric response ∂h_tt/∂c is unknown a priori (requires full assembly analysis)

The test is genuinely predictive: we pre-register the hypothesis that the GR
back-reaction is a Lorentzian-signature-enhancing mechanism, and test whether
sign(ΔE_tt) · sign(ΔE_xx) < 0 (opposite corrections).

---

## Additional metric diagnostics

Beyond the nodal means, also track:

- frac_htt_neg: fraction of nodes with E_tt < 0 (should be > 0.5 for timelike)
- frac_hxx_pos: fraction of nodes with E_xx > 0 (should be 1.0 from CPU-033)
- corr(h_tt, h_xx): anti-correlation at the GR attractor (stronger = more Lorentzian)
- Δcorr: change in anti-correlation from QM to GR attractor

---

## Protocol

For each seed in {20260325, 42, 137, 1729, 2718}:

1. Run rollout_final → (c_0, phi, mismatch, mem, adj)
2. Estimate coefficients (a_mis, a_mem, g_tt)
3. Run QM-only FP iteration → ρ*(QM) → c*_QM = sqrt(ρ*(QM))
4. Run QM+GR FP iteration → ρ*(QM+GR) → c*_GR = sqrt(ρ*(QM+GR))
5. Compute E_tt and E_xx at both attractors using phi (fixed from rollout)
6. Compute ΔE_tt, ΔE_xx, Δcorr, Δfrac_htt_neg

Pass criteria:

- P1: sign(ΔE_tt) consistent on ≥ 4/5 seeds (same sign across seeds)
- P2: sign(ΔE_xx) consistent on ≥ 4/5 seeds (same sign across seeds)
- P3: sign(ΔE_tt) ≠ sign(ΔE_xx) on ≥ 4/5 seeds (Lorentzian direction)
- P4: |ΔE_tt| > 1e-5 on ≥ 4/5 seeds (detectable metric correction)

---

## Theoretical significance

**If P1+P2+P3 all pass**: Back-reaction is a Lorentzian-signature-enhancing mechanism.
The GR coupling not only corrects the density distribution but pushes the emergent
metric toward a more pronounced (−,+,...) signature. This would be a deeply
significant finding: **gravity strengthens the Lorentzian character of spacetime
in QNG**, consistent with the real-universe observation that gravity is the
organizing principle of spacetime geometry.

**If P3 fails (corrections same sign)**: The GR back-reaction is metric-neutral
or metric-isotropic — it shifts h_tt and h_xx in the same direction. This would
mean back-reaction does not selectively strengthen the timelike sector.

**If P1+P2 fail (signs inconsistent)**: The metric correction is seed-dependent,
not universal — each topology induces a different metric response. This would
be informative about the role of graph structure in QNG geometry.

---

## Connection to Problem 6

This test provides the first quantitative link between:
1. The back-reaction loop (closed in CPUs 053–057)
2. The Lorentzian signature recovery (Problem 6, still open)

If P3 passes, it suggests a mechanism for Lorentzian signature emergence:
GR back-reaction iteratively enhances the (−,+,...) signature over dynamical time.
