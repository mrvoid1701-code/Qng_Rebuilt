# DER-BRIDGE-042 — Initial Metric Anticorrelation: Statistical Origin

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-041 (CPU-059)
**Addresses**: Problem 6 (Lorentzian signature recovery)

---

## Motivation

CPU-059 found that |corr(E_tt, E_xx)| ≈ 0.999 at rollout step 1 (random phi).
The Lorentzian signature does not build up — it is imprinted from initialization.

**Open question**: Is this initial near-perfect anticorrelation:

1. A universal statistical property of the metric assembly (independent of N)?
2. Or a finite-size coincidence that disappears at large N?

This matters for Problem 6: if |corr| ≈ 1 at all N for random phi, then the
Lorentzian signature is a structural property of QNG geometry — present whenever
phi has spatial disorder, regardless of system size.

---

## Proposed mechanism

The linearized metric assembly computes tensorial components from (c, phi).
With random phi uniformly distributed in [0, 2π), the spatial variation of phi
creates oscillating contributions to each node's E_tt and E_xx.

If the metric assembly has the structure:

    E_tt_i = f_tt(phi_i, phi_j,...) with Σ_i E_tt_i = 0
    E_xx_i = f_xx(phi_i, phi_j,...) with Σ_i E_xx_i = 0

and if f_tt and f_xx are both driven by the SAME phi-gradient terms (just with
different projection operators), then E_tt and E_xx will be anticorrelated:
the time projection and space projection respond oppositely to the same phi variation.

In this case, |corr(E_tt, E_xx)| → 1 as N → ∞ (law of large numbers averaging
over independent phi contributions).

---

## N-scaling predictions

**Prediction A**: |corr| ≈ 1 at all N for random phi (step 1)

If E_tt and E_xx are linear transformations of the same phi-gradient field, their
correlation approaches 1 (or -1) as N grows. The initial anticorrelation is a
structural, N-independent property.

**Prediction B**: Signature decay (from step 1 to step 24) decreases with N

At large N, the phi field has more degrees of freedom. The rollout dynamics
change phi less per-node (each node is connected to O(k) neighbors, but the
phi update is distributed across more nodes). Therefore the signature decay
should be smaller at large N.

**Prediction C**: Steady-state |corr| (step 24) also increases with N

As N grows, the dynamical phi changes become smaller relative to the initial
phi structure. The signature at step 24 should approach the initial value.

---

## Protocol

For each N in {8, 16, 32, 64} and each seed in {20260325, 42, 137, 1729, 2718}:

1. Run rollout step 1 and step 24 (with history)
2. Capture (c, phi) at each step
3. Compute |corr(E_tt, E_xx)| at step 1 and step 24
4. Compute signature decay Δ = |corr_1| − |corr_24|

Also: for each N, compute the initial |corr| for 100 random phi configurations
at uniform random seeds, to establish the statistical baseline.

Pass criteria:

- P1: mean |corr_1| > 0.95 at each N ∈ {8, 16, 32, 64} (universal initial signature)
- P2: mean |corr_1| > mean |corr_24| at each N (signature always starts higher)
- P3: mean(Δ) decreases from N=8 to N=64 (signature more stable at large N)
- P4: |corr_1| > 0.90 on ≥ 4/5 seeds at N=64 (holds at continuum-ish scale)

---

## Theoretical significance

**If P1 passes at all N**: The Lorentzian signature is an N-independent structural
property of QNG geometry. Any state with spatially disordered phi has near-perfect
metric anticorrelation — the Lorentzian signature is universal, not fine-tuned.

**If P3 passes**: The signature becomes more stable at large N. The continuum
limit has STRONGER Lorentzian signature, supporting the physical prediction.

**If P4 passes**: At N=64 (the continuum-ish scale from CPU-052), the initial
Lorentzian signature is still above 0.90. Combined with history preservation, the
continuum signature is robustly Lorentzian.
