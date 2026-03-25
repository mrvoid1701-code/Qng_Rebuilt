# Recovery Comparison v1

Type: `note`
ID: `NOTE-GOV-004`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Compare the current rebuilt GR-recovery path and QM-recovery path so the project can prioritize the right hard problems.

## Why this file is needed

The rebuild now has:

- a staged GR recovery program
- a staged QM recovery program

But they are not equally mature.

This matters because the next theoretical effort should go where the gap is largest, not where the wording is most ambitious.

## GR recovery status

The GR side currently has:

- weak-field proxy sector
- Lorentzian signature proxy
- back-reaction proxy available as supporting bridge structure
- linearized assembly step marked `proxy-supported`
- linearized curvature step marked `proxy-supported`
- effective source matching step marked `proxy-supported`

The strongest GR-side result so far is:

- the assembled weak-field Lorentzian metric candidate is internally consistent with the back-reacted acceleration proxy
- and already supports a bounded linearized-curvature proxy coherent with the geometry sector
- and now admits a better scalar source fit when the bridge-density and matter channels are added explicitly

This means the GR side has already crossed the line from:

- isolated proxy objects

to:

- coherent weak-field assembly
- coherent weak-field assembly with a first effective scalar source composite

## QM recovery status

The QM side currently has:

- correlator-like proxy sector
- local transport proxy
- density source balance step marked `proxy-supported`
- local generator assembly step marked `proxy-supported`
- local operator assembly step marked `proxy-supported`
- local operator-algebra proxy step marked `proxy-supported`
- propagator proxy step marked `proxy-supported`
- propagator composition proxy step marked `proxy-supported`
- local mode/spectrum step marked `proxy-supported`

The bridge itself currently also has:

- a source-response consistency step marked `proxy-supported`
- an upgraded two-channel closure v2 marked `proxy-supported`
- an upgraded two-channel source-response v2 step marked `proxy-supported`

But it does not yet have:

- a convincing continuity-style balance
- a closed operator algebra
- a stronger field-theoretic balance law

The most important negative result so far is:

- source-free continuity is weak
- source-augmented continuity is still weak

The most important positive correction is:

- density evolution is strongly captured by the local amplitude source induced by the rebuilt generator

This means the QM side has crossed the line from:

- isolated correlator proxy

to:

- local generator-plus-operator picture
- local generator-plus-operator-algebra picture
- local generator-plus-density-source-plus-operator-algebra picture
- local generator-plus-density-source-plus-operator-algebra-plus-propagator picture
- local generator-plus-density-source-plus-operator-algebra-plus-propagator-plus-composition picture

but not yet to:

- coherent field-theoretic balance law

The bridge side has also crossed a new line:

- it no longer relies only on one coherence/transport source
- it now supports a two-channel response structure with a density-source channel added explicitly

## Direct comparison

At the current rebuild stage:

- GR recovery is ahead of QM recovery

More precisely:

- GR has a better assembled weak-field story
- GR now also has a first scalar source-matching story beyond geometry-only fitting
- QM now has a better local update/generator/density-source/operator/algebra/propagator story than a conservation story
- bridge closure is now stronger than the original one-channel source-response picture

## What this implies

The rebuilt theory currently looks less like:

- "GR and QM are recovered in parallel at the same depth"

and more like:

- "GR is currently strongest at metric assembly"
- "QM is currently strongest at local complex update and operator structure"
- "QM already has a nontrivial commutator sector, but not a closed canonical algebra"
- "QM density evolution is presently source-dominated rather than continuity-dominated"
- "QM now also admits a one-step propagator reading, but not yet an exact continuum propagator theorem"
- "QM now also admits a bounded two-step propagator-composition reading, but not yet a semigroup theorem"
- "bridge closure now improves when the QM density-source channel is added explicitly"

This is an important asymmetry.

## Best interpretation

The asymmetry is not necessarily bad.

It may mean that the rebuilt QNG substrate is naturally closer to:

- geometric weak-field assembly on the GR side
- generator-style local evolution on the QM side

than to:

- exact field-equation closure on the GR side
- exact continuity or operator algebra on the QM side

## Current strongest recovery path

The strongest recovery path is:

- native update
- effective split
- geometry proxy
- Lorentzian signature proxy
- GR linearized assembly
- GR linearized curvature
- GR effective source matching
- GR tensorial assembly (E_tt, E_xx with opposite-sign source alignment)
- GR tensorial source matching (geometry channel drives components in opposite directions)
- back-reaction closure v3: propagator dressing channel closes QM→GR loop tensorially (e_xx=-1.48, e_tt=+0.88)
- back-reaction self-consistency: gamma=0.0025, tensor signs preserved — fixed point proxy supported
- Lorentzian signature: corr(h_tt,h_xx)=-0.972, h_xx>0 universal, memory amplifies 331x — linearized (-,+) signature proxy supported
- light cone: c_eff in [0.991,1.002] per node, std_hist/std_nohist=9.7x — first effective speed of light from substrate
- Einstein equations: w_eff=-0.69 (hist) vs -1.03 (nohist), corr(E_tt,E_xx)=-0.975 — vacuum energy / Λ proxy, Δw=+0.34 quantum correction
- covariance: w_eff stable at -0.669 ± 7.2% across K=5 topologies; corr always < -0.85; tier-1 signals universal, tier-2 topology-dependent
- chi identification: chi=m/c FALSIFIED (corr 0.19, sign-unstable); chi∝L_eff SUPPORTED (corr 0.55–0.82, universally positive)
- tau identification: universal scalar tau FALSIFIED (config cv=0.169, per-node cv=11–17%); tau_eff=L_eff/C_eff SUPPORTED (history amplifies 2.6–4.6x, corr(tau,mem)=0.68–0.83 universally)
- sigma identification: sigma=C_eff FALSIFIED; sigma∝C_eff SUPPORTED (corr 0.707–0.954 universally); sigma couples to BOTH C_eff and L_eff; C_eff-vs-L_eff primacy topology-dependent (tier-2); R²(C_eff+L_eff)>0.71 universally
- phi identification: phi is a near-perfectly synchronized phase field (sync>0.94 universally); history introduces phase diversity (anti-ordering); phi-L_eff weak and sign-unstable (tier-2); phi→C_eff indirect and topology-dependent (tier-2); phi is the native U(1) phase/oscillation mode
- complex amplitude proxy: ψ=C_eff*exp(i*phi) SUPPORTED; current direction corr>0 on 4/5 seeds; strong signal on seed 137 (corr=0.756); history amplifies |J| by 3–8x; scale balance weak (|J|>>|Δρ| by 100x — full continuity open)

## Current weakest recovery path

The weakest recovery path is:

- correlator proxy
- current proxy
- continuity-style closure

That is the main place where the rebuilt theory still resists a standard QM reading.

## Practical consequence

If the next goal is maximum theory strengthening, the best order is:

1. strengthen QM recovery beyond local generator assembly
2. return to tensorial or covariance-aware GR recovery beyond scalar source matching
3. only after that attempt deeper bridge closure upgrades
