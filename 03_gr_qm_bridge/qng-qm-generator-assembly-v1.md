# QNG QM Generator Assembly v1

Type: `derivation`
ID: `DER-BRIDGE-007`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first explicit local generator-like assembly of the rebuilt QNG QM sector.

## Inputs

- [qng-qm-recovery-program-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-recovery-program-v1.md)
- [qng-qm-coherence-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-coherence-proxy-v1.md)

## Scope

This file defines only a first local generator candidate.

It does not yet define:

- a Hamiltonian
- a global unitary operator
- a commutator algebra
- or an exact Schrödinger equation

## Motivation

The continuity-style test is informative but not yet strong.

A more direct first recovery step is:

- can two successive rebuilt QNG state assemblies define a stable local complex update generator candidate

## Local generator proxy

Given:

- `psi_t(i) = sqrt(C_eff(i,t)) exp(i phi_i(t))`
- `psi_{t+1}(i) = sqrt(C_eff(i,t+1)) exp(i phi_i(t+1))`

define the local multiplicative update:

`U_loc(i,t) = psi_{t+1}(i) / psi_t(i)`

and the local generator proxy:

`K_loc(i,t) = log U_loc(i,t) = A_loc(i,t) + i Omega_loc(i,t)`

where:

- `A_loc` is the amplitude-growth part
- `Omega_loc` is the phase-rotation part

## Why this matters

This is the first point where the rebuilt QM sector begins to speak in generator language rather than only correlator language.

## Minimal success condition

The first generator assembly is useful if:

1. `K_loc` is bounded
2. `K_loc` is nontrivial
3. `K_loc` reconstructs the next-step complex state candidate
4. `K_loc` retains history imprint
5. `Omega_loc` remains phase-sensitive

## What remains open

This proxy still does not answer:

- what the exact Hilbert space is
- what the global generator is
- whether the generator is Hermitian or only effective

So this is a generator proxy, not an exact QM recovery theorem.
