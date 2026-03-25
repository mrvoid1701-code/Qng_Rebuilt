# QNG QM Semigroup Closure Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-017`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test whether the rebuilt QM propagator sector satisfies an approximate semigroup
closure property under three-step composition.

## Inputs

- [qng-qm-propagator-composition-proxy-v1.md](qng-qm-propagator-composition-proxy-v1.md)
- [qng-qm-generator-assembly-v1.md](qng-qm-generator-assembly-v1.md)
- [qng-qm-operator-assembly-v1.md](qng-qm-operator-assembly-v1.md)

## Scope

This file defines only a three-step semigroup closure proxy.

It does not claim:

- an exact semigroup theorem
- exact unitarity under multi-step composition
- a continuum time evolution group
- or a final Chapman-Kolmogorov relation

## Motivation

The rebuilt QM lane passed two-step composition (QNG-CPU-027):

- diagonal two-step: exact reconstruction
- dressed two-step: overlap = 0.999449, bounded, nontrivial

The two-step result is necessary but not sufficient for semigroup structure.

A semigroup demands that composition works for *any* number of steps, not just two.

The minimum defensible test of semigroup-like behaviour is:

- does three-step composition remain bounded
- does three-step composition still align with the direct three-step target
- does the per-step overlap decay stay controlled across the additional step
- does phase sensitivity and dressing nontriviality survive the extra step

## Semigroup property definition (proxy level)

Let `P(a, b)` denote the one-step dressed propagator from step `a` to step `b`.

The exact semigroup property would require:

`P(a, c) = P(b, c) P(a, b)` for all `a < b < c`

This workspace does not claim this holds exactly.

The proxy closure question is:

- does `P_mix(t, t+3) ≈ P_mix(t+2, t+3) P_mix(t+1, t+2) P_mix(t, t+1)`
- where `P_mix(t, t+3)` is the independently chained three-step dressed composition
- and the approximation quality is measured by overlap with the direct target state

## Three-step diagonal composition

Let:

- `P_diag(t, t+1)`, `P_diag(t+1, t+2)`, `P_diag(t+2, t+3)` be the exact
  local-generator diagonal propagators at three consecutive steps.

Then define:

`P_diag^(3) = P_diag(t+2, t+3) P_diag(t+1, t+2) P_diag(t, t+1)`

This should reconstruct `psi_(t+3)` exactly when applied to `psi_t`.

## Three-step dressed composition

Let:

- `P_mix(t, t+1)`, `P_mix(t+1, t+2)`, `P_mix(t+2, t+3)` be the transport-dressed
  one-step propagators.

Then define:

`P_mix^(3) = P_mix(t+2, t+3) P_mix(t+1, t+2) P_mix(t, t+1)`

This is the first three-step closure test.

## Per-step decay measure

Define:

- `ov_2 = overlap(P_mix^(2) psi_t, psi_(t+2))`
- `ov_3 = overlap(P_mix^(3) psi_t, psi_(t+3))`

The per-step decay ratio is:

`rho = ov_3 / ov_2`

A value of `rho` close to 1.0 means the aligned quality degrades slowly.
A value of `rho` near 0 means the composition is blowing up or diverging.

The proxy closure is useful if `rho > 0.93`.

## Minimal success condition

The first semigroup closure proxy is useful if:

1. diagonal three-step composition reconstructs the three-step target exactly
2. dressed three-step composition remains bounded (`max_row_sum < 3.0`)
3. dressed three-step composition aligns with the three-step target (`overlap > 0.95`)
4. dressed three-step is nontrivially different from diagonal (`l1 > 0.25`)
5. per-step decay ratio is stable (`ov_3 / ov_2 > 0.93`)
6. three-step composition retains phase sensitivity

## What remains open

This still does not answer:

- whether the dressed composition satisfies an exact semigroup identity at any step count
- whether the overlap decay stabilises or continues to fall beyond three steps
- whether the continuum limit of the chained composition recovers a well-defined evolution group
- whether associativity holds for the dressed sector

So this is a semigroup closure proxy, not a semigroup theorem.
