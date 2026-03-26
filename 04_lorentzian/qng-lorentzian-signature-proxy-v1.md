# QNG Lorentzian Signature Proxy v1

Type: `derivation`
ID: `DER-SIG-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define and test the first proxy for Lorentzian signature emergence in the
rebuilt QNG substrate.

## Inputs

- [qng-gr-linearized-assembly-proxy-v1.md](../02_gr_sector/qng-gr-linearized-assembly-proxy-v1.md)
- [qng-gr-backreaction-selfconsistency-v1.md](../03_gr_qm_bridge/qng-gr-backreaction-selfconsistency-v1.md)

## Scope

This file defines only a first weak-field Lorentzian signature proxy.

It does not define:

- a full Lorentzian recovery program
- a Wick rotation or analytic continuation
- a proof of Lorentzian signature at strong coupling
- an exact causal structure

## Motivation

In general relativity, the metric has signature (-,+,+,+).

At weak field:
- `g_tt = 1 + h_tt` where `h_tt < 0` on average → `g_tt < 1` (timelike component reduced)
- `g_xx = 1 + h_xx` where `h_xx > 0` on average → `g_xx > 1` (spacelike component enhanced)

If the linearized perturbations `h_tt` and `h_xx` carry this opposite-sign structure, the
substrate supports a Lorentzian signature proxy.

## Signature discriminant

Define the per-node signature discriminant:

`D_sig(i) = h_tt(i) * h_xx(i)`

In a **Euclidean** substrate: both `h_tt` and `h_xx` are positive fluctuations on average
→ `mean(D_sig) > 0`

In a **Lorentzian** substrate: `h_tt` tends negative and `h_xx` tends positive
→ `mean(D_sig) < 0`

## Anti-correlation signature

The Lorentzian structure is also encoded in the across-node anti-correlation:

`corr(h_tt, h_xx) < 0`

At strong Lorentzian signature, every node where h_tt is depressed should have
h_xx elevated, and vice versa — this is the linearized expression of the sign
flip between time and space metric components.

## Memory sector drives Lorentzian structure

The history sector carries temporal correlations that break the symmetry between
h_tt and h_xx.

Expected behaviour:
- `mean(D_sig)_history` is much more negative than `mean(D_sig)_nohist`
- `|corr(h_tt, h_xx)|_history > |corr(h_tt, h_xx)|_nohist`

This means that the causal structure (Lorentzian signature) is driven by
the memory sector of the substrate — the information-theoretic history of
the system is what generates the time/space asymmetry.

## Spacelike robustness

A distinctive proxy signal: `h_xx > 0` on every single node, while `h_tt < 0`
on a majority of nodes.

This asymmetry — spacelike perturbation always positive, timelike perturbation
predominantly negative — is the linearized Lorentzian signature condition.

## Minimal success condition

The Lorentzian signature proxy is supported if:

1. `mean(D_sig) < 0` (discriminant negative with history)
2. `corr(h_tt, h_xx) < -0.5` (anti-correlation with history)
3. `fraction of nodes with h_xx > 0 > 0.90` (spacelike robustness)
4. history amplifies discriminant: `|mean(D_sig)_hist| > 10 * |mean(D_sig)_nohist|`
5. history sharpens anti-correlation: `|corr_hist| > |corr_nohist|`

## What remains open

Even if this proxy is supported:

- weak-field only: strong-field Lorentzian signature is not addressed
- the full `(-,+,+,+)` signature requires off-diagonal and higher components
- no analytic continuation or Wick rotation is defined
- no causal horizon, light cone, or causal diamond structure is defined

So this is a linearized metric signature proxy, not a full Lorentzian recovery.
