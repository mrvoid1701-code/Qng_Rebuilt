# QNG GR Tensorial Source Matching Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-019`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test whether fitting the individual linearized Einstein-tensor components
`E_tt` and `E_xx` separately with channel-matched sources produces a lower
combined residual than fitting the scalar `R_lin = E_xx - E_tt` alone.

This is the first place the rebuilt GR lane can claim that tensor structure
carries information that the scalar projection discards.

## Inputs

- [qng-gr-tensorial-assembly-proxy-v1.md](qng-gr-tensorial-assembly-proxy-v1.md)
- [qng-gr-effective-source-matching-v1.md](qng-gr-effective-source-matching-v1.md)

## Scope

This file defines only a first tensorial source-matching comparison.

It does not define:

- a covariant stress-energy tensor
- a unique channel assignment rule
- or an exact Einstein equation

## Motivation

The tensorial assembly proxy (DER-BRIDGE-018) established that:

- `E_tt` anti-correlates with transport and matter sources
- `E_xx` correlates positively with transport and matter sources
- the two components carry opposite source signatures

This means the scalar model `R_lin ~ a K_C + b Q + c S + d M` is averaging
out a signal that the individual components carry in opposite directions.

A tensorial model that fits `E_tt` and `E_xx` separately should recover more
of that signal: the coefficient for `Q_src` should be positive for `E_xx`
and negative for `E_tt`, reflecting the actual opposite-sign structure.

## Tensorial fit model

Fit each component independently with the same four-channel source composite:

`E_xx(i) ~ a_xx K_C(i) + b_xx Q_src(i) + c_xx S_src(i) + d_xx M_eff(i)`

`E_tt(i) ~ a_tt K_C(i) + b_tt Q_src(i) + c_tt S_src(i) + d_tt M_eff(i)`

and separately fit the scalar:

`R_lin(i) ~ a_rl K_C(i) + b_rl Q_src(i) + c_rl S_src(i) + d_rl M_eff(i)`

## Tensorial improvement condition

Define the split residual mean as:

`ratio_split = (ratio_exx + ratio_ett) / 2`

where each ratio is `residual_l2 / raw_l2`.

The tensorial fit is an improvement if:

`ratio_split < ratio_rlin`

This says: the average per-component fit quality beats the scalar fit quality
when the tensor is resolved into its two components.

## Sign separation condition

The tensor is carrying real differential source information if the
transport coefficient (`b`) has opposite sign in the two fits:

- `b_xx > 0` (E_xx aligned with transport source)
- `b_tt < 0` (E_tt anti-aligned with transport source)

And the sign separation is:

`b_xx - b_tt > threshold`

## Minimal success condition

The first tensorial source matching proxy is useful if:

1. `E_xx` fits well with sources (`ratio_exx < 0.90`)
2. `b_xx > 0` (E_xx transport coefficient is positive)
3. `b_tt < 0` (E_tt transport coefficient is negative — confirmed opposition)
4. sign separation is clear: `b_xx - b_tt > 0.10`
5. split model improves over scalar: `ratio_split < ratio_rlin`
6. history imprint is retained on both component fits

## What remains open

This still does not answer:

- whether the channel assignment is unique or representation-dependent
- whether the tensor can be covariantized beyond 1+1D
- whether the four sources are the minimal sufficient set
- whether the split improvement survives beyond the toy chart

So this is a tensorial source matching proxy, not a covariant source theorem.
