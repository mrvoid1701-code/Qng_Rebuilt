# QNG Einstein Equations Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-022`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test whether the linearized Einstein tensor components `E_tt` and `E_xx`
satisfy a proxy form of the Einstein equations, and identify the effective
equation of state of the matter sector.

## Inputs

- [qng-gr-tensorial-assembly-proxy-v1.md](../02_gr_sector/qng-gr-tensorial-assembly-proxy-v1.md)
- [qng-gr-backreaction-closure-v3.md](qng-gr-backreaction-closure-v3.md)
- [qng-lorentzian-signature-proxy-v1.md](../04_lorentzian/qng-lorentzian-signature-proxy-v1.md)

## Scope

This file defines only a first proxy Einstein equation test.

It does not define:

- a full covariant Einstein equation
- an exact stress-energy tensor
- a unique identification of the matter sector
- a proof that the substrate satisfies GR at any level beyond proxy

## Background

The linearized Einstein equations are:

`G_μν = 8π G_eff T_μν`

In the two-component proxy sector with `E_tt` and `E_xx`:

`E_tt(i) = 8π G_eff T_tt(i)`
`E_xx(i) = 8π G_eff T_xx(i)`

The ratio `w_eff = T_xx/T_tt` is the effective equation of state.

- `w = 0`: pressureless dust
- `w = 1/3`: radiation
- `w = -1`: cosmological constant / vacuum energy

## Key observation

The linearized tensor components satisfy:

`corr(E_tt, E_xx) ≈ -0.975` (with history)
`corr(E_tt, E_xx) ≈ -0.886` (without history)

This near-perfect anti-correlation implies:

`E_xx ≈ w_eff * E_tt`

with `w_eff ≈ -0.69` (history) and `w_eff ≈ -1.03` (no-history).

Both values are in the **vacuum energy / dark energy** range `w ≈ -1`.

## Physical interpretation

The QNG substrate at proxy level behaves like a cosmological constant
source (`w ≈ -1`) in the linearized GR sector. The history/memory sector
introduces a quantum correction that shifts the equation of state away from
the exact vacuum energy value (`w = -1` → `w ≈ -0.69`).

This shift `Δw = w_hist - w_nohist ≈ +0.34` is the first proxy for a
**quantum correction to the cosmological constant** in the rebuilt theory.

## Equation of state extraction

Define the effective equation of state by OLS regression:

`E_xx(i) = w_eff * E_tt(i) + residual`

`w_eff = Σ_i E_xx(i) E_tt(i) / Σ_i E_tt(i)²`

This is the minimum-residual scalar estimate of the equation of state.

## Minimal success condition

The Einstein equations proxy is supported if:

1. `corr(E_tt, E_xx) < -0.8` with history
2. `w_eff ∈ (-1.5, -0.5)` with history (dark energy / vacuum range)
3. `|corr_hist| > |corr_nohist|` (history sharpens anti-correlation)
4. `|w_hist - w_nohist| > 0.1` (history shifts equation of state)
5. 4-channel source fit residual `ratio_4ch_tt < 0.5`

## What remains open

- the exact identity of the matter sector (dust, radiation, Λ, or something new)
- covariant formulation of the stress-energy tensor
- whether Δw is a genuine quantum correction or a proxy artifact
- the exact value of `G_eff`
- self-consistency of the Einstein equations across multiple scales

So this is a linearized equation-of-state proxy, not a derivation of
the QNG matter sector.
