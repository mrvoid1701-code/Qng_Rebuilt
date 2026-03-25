# Rebuild Status Map v1

Type: `note`
ID: `NOTE-GOV-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Provide one compact status map for the rebuilt workspace so supported layers, candidate layers, and open layers stay explicit.

## Status vocabulary used here

- `proxy-supported`
- `candidate`
- `open`

## Core layers

- GR pure backbone: `candidate`
- QM pure backbone: `candidate`
- QNG ontic backbone: `candidate`
- native update reference: `proxy-supported`
- CPU/GPU agreement on native update: `proxy-supported`
- split effective layer `(C_eff, L_eff)`: `proxy-supported`
- matter-sector proxy: `proxy-supported`
- geometry proxy estimator: `proxy-supported`
- Lorentzian signature proxy: `proxy-supported`

## Bridge layers

- GR weak-field proxy sector: `proxy-supported`
- GR recovery program: `candidate`
- GR linearized assembly step: `proxy-supported`
- GR linearized curvature step: `proxy-supported`
- GR effective source matching step: `proxy-supported`
- GR tensorial assembly step: `proxy-supported`
- GR tensorial source matching step: `proxy-supported`
- QM coherence proxy sector: `proxy-supported`
- QM recovery program: `candidate`
- QM density source balance step: `proxy-supported`
- QM generator assembly step: `proxy-supported`
- QM operator assembly step: `proxy-supported`
- QM operator-algebra proxy step: `proxy-supported`
- QM propagator proxy step: `proxy-supported`
- QM propagator composition proxy step: `proxy-supported`
- QM semigroup closure proxy step: `proxy-supported`
- QM mode/spectrum step: `proxy-supported`
- back-reaction proxy closure: `proxy-supported`
- back-reaction proxy closure v2: `proxy-supported`
- back-reaction proxy closure v3 (three-channel tensorial): `proxy-supported`
- back-reaction self-consistency fixed point (single-iteration contraction): `proxy-supported`
- Lorentzian signature proxy (memory-driven h_tt/h_xx anti-correlation): `proxy-supported`
- light cone proxy (per-node c_eff from null condition): `proxy-supported`
- Einstein equations proxy (equation of state w_eff ≈ -0.69, Δw from memory): `proxy-supported`
- covariance stability (K=5 seeds, tier-1 signals universal, tier-2 topology-dependent): `proxy-supported`
- source-response consistency step: `proxy-supported`
- source-response consistency v2 step: `proxy-supported`
- unified split-bridge architecture: `candidate`
- bridge consistency registry: `proxy-supported`
- back-reaction closure: `open`
- exact GR recovery: `open`
- exact QM recovery: `open`

## Phenomenology layers

- trajectory lag proxy: `proxy-supported`
- lensing proxy: `proxy-supported`
- rotation support proxy: `proxy-supported`
- timing proxy: `proxy-supported`
- cosmology proxy: `proxy-supported`

## Fragile or deliberately unlocked items

- `Sigma` as final effective scalar: `open`
- `chi = m/c`: `open`
- universal `tau`: `open`
- Lorentzian signature recovery: `open`
- matter sector identification: `open`

## Working interpretation

The rebuilt workspace now supports the following statement:

- a native memory-sensitive QNG substrate can feed a split effective layer, then a GR-facing proxy sector, a QM-facing proxy sector, and multiple downstream phenomenology proxies

This is stronger and cleaner than the old workspace, but it is still not a final derivation program.
