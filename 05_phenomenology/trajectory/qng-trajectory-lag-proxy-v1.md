# QNG Trajectory Lag Proxy v1

Type: `derivation`
ID: `DER-TRJ-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first trajectory-facing proxy that descends from the rebuilt QNG layers without importing legacy fit parameters.

## Inputs

- [trajectory-reduction-chain-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/05_phenomenology/trajectory/trajectory-reduction-chain-v1.md)
- [qng-emergent-field-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-emergent-field-v1.md)
- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)

## Scope

This file defines only a trajectory proxy.

It does not yet define:

- a mission fit
- a universal `tau`
- or a physical anomaly claim

## Motivation

The rebuilt theory now distinguishes:

- `L_eff` as memory-load content
- weak-field acceleration proxies from the geometry sector

The cleanest first trajectory observable should therefore depend on both:

- memory-load
- direction-sensitive weak-field response

## Edge response proxy

On the ordered toy chart, define the edge memory load:

`L_edge(i) = (L_eff(i) + L_eff(i+1)) / 2`

and the edge acceleration:

`a_edge(i) = (a_QNG(i) + a_QNG(i+1)) / 2`

Define the signed edge lag response:

`R_edge(i) = L_edge(i) a_edge(i)`

## Global trajectory proxies

Define the net directional lag proxy:

`A_trj = sum_i R_edge(i)`

Define the unsigned lag strength:

`S_trj = sum_i |R_edge(i)|`

## Interpretation

`A_trj` measures directional bias.

`S_trj` measures total lag-like activity independent of sign.

This is the first point where the rebuilt theory speaks in trajectory language.

## Why this is cleaner than the legacy path

The old project often moved too quickly from memory language to fitted lag parameters.

The rebuild inserts an explicit reduction layer:

- native memory
- effective memory-load
- weak-field acceleration proxy
- trajectory lag proxy

## Immediate test criteria

The first CPU test should check:

1. nontrivial lag strength
2. history imprint
3. directional sign reversal under acceleration reversal
4. boundedness of the proxy inputs
