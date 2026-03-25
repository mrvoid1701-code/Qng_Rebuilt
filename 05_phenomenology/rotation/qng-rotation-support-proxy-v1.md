# QNG Rotation Support Proxy v1

Type: `derivation`
ID: `DER-ROT-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first rotation-facing proxy that descends from the rebuilt weak-field and memory-load sectors without importing legacy fit laws.

## Inputs

- [README.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/05_phenomenology/rotation/README.md)
- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)

## Scope

This file defines only a toy-chart radial-support proxy.

It does not yet define:

- a galaxy fit
- a baryonic model
- or a final rotation law

## Motivation

The rebuilt theory already distinguishes:

- geometry-driven weak-field acceleration
- memory-load content through `L_eff`

So the clean first rotation question is:

- does memory-load generate a structured support excess over the geometry-only baseline

## Toy radial chart

Choose a chart center `i_*` and define:

`r(i) = 1 + min(|i - i_*|, N - |i - i_*|)`

This is only a probe coordinate for the current ordered toy chart.

## Baseline support proxy

From the weak-field acceleration proxy, define:

`V_base^2(i) = r(i) |a_QNG(i)|`

## Memory-enhanced support proxy

Define the rebuilt QNG support proxy:

`V_qng^2(i) = r(i) |a_QNG(i)| (1 + eta L_eff(i))`

with fixed positive `eta`.

## Excess proxy

Define:

`Delta_rot(i) = V_qng^2(i) - V_base^2(i)`

and the global excess strength:

`S_rot = sum_i Delta_rot(i)`

## Interpretation

`Delta_rot(i)` measures local support added by memory-load beyond the geometry-only baseline.

`S_rot` measures the total memory-linked support excess on the chart.

## Why this is cleaner than the legacy path

The old workspace moved rapidly from lag intuition to domain-specific fits.

The rebuild inserts an explicit reduction:

- weak-field baseline
- memory-load correction
- support excess proxy

## Immediate test criteria

The first CPU test should check:

1. positivity of the excess
2. boundedness of the support proxy
3. memory sensitivity
4. history imprint
