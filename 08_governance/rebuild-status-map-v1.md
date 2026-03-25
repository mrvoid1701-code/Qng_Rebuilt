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
- chi identification: `chi = m/c` FALSIFIED; `chi ∝ L_eff` supported (corr 0.55–0.82 across 5 seeds)
- tau identification: universal scalar `tau` FALSIFIED; per-node `tau_eff = L_eff/C_eff` supported (history amplifies 2.6–4.6x, corr(tau,mem) 0.68–0.83)
- sigma identification: `sigma = C_eff` FALSIFIED; `sigma ∝ C_eff` supported (corr 0.71–0.95 universally); sigma couples to BOTH C_eff and L_eff; R²(C_eff+L_eff) > 0.71 universally; C_eff-vs-L_eff primacy topology-dependent
- phi identification: phi is a near-perfect synchronization field (sync>0.94 universally); history anti-ordering (increases phase diversity); phi-L_eff weak/sign-unstable (tier-2); phi is native U(1) phase mode
- complex amplitude proxy ψ=C_eff*exp(i*phi): `proxy-supported` — current direction correct 4/5 seeds; history amplifies |J| 3–8x; scale balance open
- calibrated continuity balance: `proxy-supported` — α*>0 on 4/5 seeds; R²=0.572 max; mean|α*|≈10⁻³ effective coupling; cv=0.76 (Tier-2)
- Madelung amplitude ψ_M=sqrt(C_eff)·exp(i·phi): `proxy-supported` — marginal improvement (mean R² 0.203 vs 0.200); amplitude form NOT bottleneck
- history-phase current proxy ψ_hp=C_eff·exp(i·h.phase): `proxy-supported` (informative negative) — R²_hp < R²_std on 4/5 seeds; corr(phi,h.phase)=0.84–0.97; phase variable choice NOT bottleneck; current functional form identified as root issue
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
