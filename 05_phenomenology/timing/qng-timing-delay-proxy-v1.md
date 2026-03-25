# QNG Timing Delay Proxy v1

Type: `derivation`
ID: `DER-TIME-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first timing-facing proxy that descends from rebuilt QNG quantities without importing legacy delay-fit parameters.

## Inputs

- [README.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/05_phenomenology/timing/README.md)
- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)

## Scope

This file defines only a toy-chart propagation-delay proxy.

It does not yet define:

- a waveform model
- an exact travel-time law
- or a data-facing timing fit

## Motivation

The rebuilt theory already separates:

- `L_eff` as retained memory-load
- `Psi_QNG` as a weak-field potential proxy

The first timing object should therefore measure how memory-load modulates propagation through the weak-field sector.

## Edge delay proxy

On the ordered toy chart define:

`L_edge(i) = (L_eff(i) + L_eff(i+1)) / 2`

`Psi_edge(i) = (|Psi_QNG(i)| + |Psi_QNG(i+1)|) / 2`

and the local delay load:

`T_edge(i) = L_edge(i) Psi_edge(i)`

## Global timing proxies

Define:

`D_time = sum_i T_edge(i)`

as the total unsigned timing delay proxy.

Define:

`W_time = sum_i |T_edge(i+1) - T_edge(i)|`

as the timing-distortion or echo-structure proxy.

## Interpretation

`D_time` measures total propagation delay burden.

`W_time` measures how unevenly that burden is distributed along the chart.

## Why this is cleaner than the legacy path

The old workspace often moved directly from lag intuition to fitted timing parameters.

The rebuild inserts:

- memory-load
- weak-field potential proxy
- local delay load
- global timing proxies

## Immediate test criteria

The first CPU test should check:

1. boundedness
2. nontrivial delay burden
3. memory-switch sensitivity
4. history imprint
5. nontrivial distortion structure
