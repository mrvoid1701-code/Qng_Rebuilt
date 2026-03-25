# QNG QM Mode Spectrum Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-008`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit mode/spectrum proxy of the rebuilt QNG QM sector.

## Inputs

- [qng-qm-recovery-program-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-recovery-program-v1.md)
- [qng-qm-generator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-generator-assembly-v1.md)

## Scope

This file defines only a first discrete mode/spectrum proxy.

It does not yet define:

- an exact Hamiltonian spectrum
- a continuum mode basis
- a full normal-mode theorem
- or exact occupation numbers

## Motivation

The rebuilt QM sector now has:

- a complex state candidate `psi`
- a local generator proxy `K_loc`

The next natural question is:

- do these objects admit a stable and interpretable mode decomposition on the ordered probe chart

## State spectrum proxy

On the ordered toy chart, define the discrete mode coefficients:

`hat psi(k) = N^(-1/2) sum_i psi(i) exp(-2 pi i k i / N)`

and the state mode power:

`P_psi(k) = |hat psi(k)|^2`

## Generator spectrum proxy

Define the complex generator field:

`K_loc(i) = A_loc(i) + i Omega_loc(i)`

and its mode coefficients:

`hat K(k) = N^(-1/2) sum_i K_loc(i) exp(-2 pi i k i / N)`

with generator mode power:

`P_K(k) = |hat K(k)|^2`

## Why this matters

This is the first point where the rebuilt QM sector can speak in:

- mode language
- spectral concentration language
- state/generator spectral comparison

instead of only local proxy language.

## Minimal success condition

The first spectrum proxy is useful if:

1. the mode powers are bounded and Parseval-consistent
2. the generator spectrum is nontrivial
3. the spectrum is phase-sensitive
4. the spectrum retains history imprint

## What remains open

This proxy still does not answer:

- whether the spectrum comes from a Hermitian generator
- whether the modes are physical normal modes
- whether occupation and energy can be recovered

So this is a spectrum proxy, not an exact QM spectral theorem.
