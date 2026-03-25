# QNG Lensing Proxy v1

Type: `derivation`
ID: `DER-LENS-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first lensing-facing proxy that descends from the rebuilt weak-field QNG sector.

## Inputs

- [qng-gr-weakfield-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-gr-weakfield-proxy-v1.md)
- [qng-geometry-estimator-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-geometry-estimator-v1.md)
- [README.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/05_phenomenology/lensing/README.md)

## Scope

This file defines only a toy-chart lensing proxy.

It does not yet define:

- a physical sky-angle prediction
- a cluster fit
- or a final magnification law

## Starting point

The rebuilt weak-field sector already provides:

- `h_00(i)`
- `h_11(i)`

These are the natural ingredients for a lensing-like potential proxy.

## Lensing potential proxy

Define:

`Phi_lens(i) = (h_00(i) + h_11(i)) / 2`

and the signed deflection proxy:

`alpha_lens(i) = - grad(Phi_lens)(i)`

## Secondary response proxy

Define the unsigned deflection strength:

`D_lens = sum_i |alpha_lens(i)|`

and the edgewise deflection profile:

`alpha_edge(i) = (alpha_lens(i) + alpha_lens(i+1)) / 2`

## Why this is the right first lensing object

This proxy is:

- downstream of geometry
- weak-field compatible
- independent of legacy fit parameters
- and simple enough to test immediately

## Immediate test criteria

The first CPU test should check:

1. weak-field boundedness
2. nontrivial deflection structure
3. history imprint
4. sensitivity to gradients of the geometric sector
