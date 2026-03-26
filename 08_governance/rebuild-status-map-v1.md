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
- mismatch-gradient current J_mis=C_i·C_j·(mis_j-mis_i): `proxy-supported` (informative negative) — scale_ratio 6-12x (vs phi's 100x); topology-selective: seed 42 mis wins (0.354), seed 137 phi wins (0.572), seed 1729 mem wins (0.101); multi-channel structure identified
- multi-channel current (phi+mismatch+mem joint regression): `proxy-supported` — PASS 4/4; R²_combined > best_single on 5/5 seeds; mean R²=0.405 (vs 0.256 best single); max R²=0.602 (seed 137); effective QNG continuity: ∂_t(C_eff²) + α_phi·J_phi + α_mis·J_mis + α_mem·J_mem ≈ 0 (mismatch-memory dominated)
- multi-channel large-N probe (N=8,16,32): `proxy-supported` (partial 2/4) — multi-channel beats single universally (15/15); R² decreases with N (sparse-graph law); phi absent at N=32; large-N limit: mismatch+mem only
- degree-normalized current: `proxy-supported` (FAIL 1/4) — normalization makes R² negative; N-weakening is structural not degree-dilution; multi-channel law confirmed as sparse-graph/UV law
- GR multi-channel QM source injection: `proxy-supported` — PASS 3/4; div_J_mis + div_J_mem improve E_xx −8.4%, E_tt −17.1%, ratio_split 0.316→0.275; first QM→GR cross-sector coupling confirmed; 6-channel bridge established
- QM→GR coupling covariance (multi-seed): `proxy-supported` — PASS 3/4; **Tier-1**; 5/5 seeds improve (universal); e_mis dominant on 4/5 seeds; sign(e_mis)=−1 on 4/5 seeds; ⟨e_mis⟩=−0.175; coupling ~3–10% of geometry; seed 2718 sign-flip anomaly identified
- QM→GR coupling large-N probe: `proxy-supported` — **PASS 4/4; Tier-1-large-N**; sparse-graph law in GR sector: |e_mis| 1.037→0.259→0.159 (N=8→16→32); 5/5 improve at N=32; sign normalizes at N=32; unified sparse-graph law confirmed (same attenuation in QM+GR)
- QM→GR coupling continuum limit (N=64): `proxy-supported` — **PASS 4/4; SATURATION CLASS**; |e_mis| 0.159→0.134 (N=32→64, decay ×0.84/doubling); seed 2718 fully normalized; non-monotone Δratio (−0.018→−0.030); best estimate |e_mis(∞)| ≈ 0.08–0.12 (non-zero)
- QM↔GR back-reaction loop: `proxy-supported` — **PASS 4/4; Tier-1; LOOP CLOSES**; GR→QM: E_tt→∂_t(ρ) with γ_tt>0 on 5/5 seeds; mean R²: 0.405→0.461; full equation: ∂_t(ρ)≈-(α_phi·dJ_phi+α_mis·dJ_mis+α_mem·dJ_mem)+γ_tt·E_tt; self-regulating damping loop confirmed
- GR→QM back-reaction large-N: `proxy-supported` — **PASS 3/4; Tier-1.5**; γ_tt persists at N=32 5/5; sparse-graph law confirmed; loop_strength≈0.00119 SATURATES at N≥16; subcritical gain (loop<1); finite continuum loop constant established
- back-reaction fixed-point iteration: `proxy-supported` — **PARTIAL 2/4**; rollout IS the QM attractor (Δρ_0≈0.0001); GR+QM converges 5/5 (ratio 0.9534); FP shift ~0.001 correlated with γ_tt; two-level attractor hierarchy confirmed
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
