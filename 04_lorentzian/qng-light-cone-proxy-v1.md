# QNG Light Cone Proxy v1

Type: `derivation`
ID: `DER-SIG-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define and test the first effective light cone proxy in the rebuilt QNG
substrate, using the Lorentzian signature established in DER-SIG-001.

## Inputs

- [qng-lorentzian-signature-proxy-v1.md](qng-lorentzian-signature-proxy-v1.md)

## Scope

This file defines only a linearized, per-node light cone proxy.

It does not define:

- a full null geodesic structure
- a causal diamond or causal horizon
- a covariant light cone in curved spacetime
- an exact causal structure

## The null condition

In the linearized metric with `g_tt < 0` and `g_xx > 0`, the null
condition for a light ray is:

`g_tt(i) dt² + g_xx(i) dx² = 0`

Solving for the effective speed of light per node:

`c_eff(i) = |dx/dt| = sqrt(-g_tt(i) / g_xx(i))`

Since `g_tt(i) < 0` the numerator `-g_tt(i) > 0`, and the
denominator `g_xx(i) > 0`, so `c_eff(i)` is real and positive
at every node.

## Flat-space normalization

In flat spacetime `h_tt = h_xx = 0`:
- `g_tt = -1`, `g_xx = 1`
- `c_eff = sqrt(1/1) = 1` (normalized units)

At weak field:
`c_eff(i) ≈ 1 - h_tt(i)/2 - h_xx(i)/2`

Since `mean(h_tt) < 0` and `mean(h_xx) > 0`, the two corrections
partially cancel. The mean effective speed is close to but not
exactly 1, with node-to-node spatial variation.

## Spatial variation of c_eff

The per-node variation of `c_eff` is the first proxy for a
spatially varying speed of light in the QNG substrate.

In standard GR, the effective speed of light is uniform in vacuum.
Spatial variation of `c_eff` signals either matter content or quantum
corrections to the metric.

The history/memory sector is expected to increase this variation, since
it differentiates nodes more strongly.

## Minimal success condition

The light cone proxy is supported if:

1. `c_eff(i) > 0` on all nodes (null cone well-defined everywhere)
2. `mean(c_eff)` in `(0.9, 1.1)` (near speed-of-light normalization)
3. `std(c_eff) > 1e-3` (nontrivial spatial variation)
4. history shifts mean: `|mean(c_eff_hist) - mean(c_eff_nohist)| > 1e-3`
5. history amplifies variation: `std(c_eff_hist) > std(c_eff_nohist)`

## What remains open

Even if this proxy is supported:

- the null geodesic structure is not computed
- the causal diamond and causal horizon are not defined
- the variation of `c_eff` is not yet identified as matter or quantum correction
- the covariant generalization is not defined

So this is a per-node linearized null-speed proxy, not a full causal
structure.
