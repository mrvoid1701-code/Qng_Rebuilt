# QNG QM Density Source Balance v1

Type: `derivation`
ID: `DER-BRIDGE-011`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first successful balance law for the rebuilt QNG QM density sector.

## Inputs

- [qng-qm-generator-assembly-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-generator-assembly-v1.md)
- [qng-qm-operator-algebra-proxy-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-operator-algebra-proxy-v1.md)
- [qng-qm-recovery-program-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/03_gr_qm_bridge/qng-qm-recovery-program-v1.md)

## Scope

This file does not claim a final continuity equation.

It defines the first successful density-balance law currently supported by the rebuild.

## Motivation

The earlier continuity-style test remained weak even after source augmentation with external memory-load terms.

That failure suggests that the rebuilt density sector may not be primarily transport-driven at this stage.

The local generator proxy already provides:

`K_loc(i,t) = A_loc(i,t) + i Omega_loc(i,t)`

and the rebuilt state update is:

`psi_{t+1}(i) = exp(K_loc(i,t)) psi_t(i)`

Taking density:

`rho_t(i) = |psi_t(i)|^2`

gives:

`rho_{t+1}(i) = exp(2 A_loc(i,t)) rho_t(i)`

## Density source law

Define the local density source term:

`S_amp(i,t) = rho_t(i) (exp(2 A_loc(i,t)) - 1)`

Then the exact local density balance induced by the rebuilt local generator is:

`rho_{t+1}(i) - rho_t(i) = S_amp(i,t)`

## Transport-corrected balance

A transport-corrected probe balance may still be tested:

`rho_{t+1} - rho_t + kappa div(J_probe) - S_amp = residual`

but the current rebuild suggests that:

- `S_amp` is the dominant density-balance term
- the transport contribution is sub-leading in the present toy chart

## Why this matters

This is a genuine advance over the failed continuity-only reading.

It means the rebuilt QM sector does have a strong density evolution law, but its present best form is:

- source-dominated through amplitude evolution

not:

- transport-dominated through a standard continuity equation

## Minimal success condition

The first density-source balance is useful if:

1. `S_amp` reconstructs `rho_{t+1} - rho_t` with negligible residual
2. `S_amp` is nontrivial
3. transport-corrected fitting leaves only a small current coefficient
4. the source term retains history imprint

## What remains open

This still does not answer:

- how density source balance connects to exact QM continuity
- whether a stronger current definition exists
- whether source-dominated balance survives beyond the toy chart

So this is a density-source balance law, not an exact continuity theorem.
