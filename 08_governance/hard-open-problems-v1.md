# Hard Open Problems v1

Type: `note`
ID: `NOTE-GOV-003`
Status: `draft`
Author: `C.D Gabriel`

## Objective

State the hard remaining problems of the rebuilt theory in a direct way, without mixing them with already supported proxy results.

## Problem 1: final native state choice

We still do not know the final minimal ontic state of QNG.

Open question:

- are `sigma`, `chi`, and `phi` all primitive
- or are one or more of them only reference-level coordinates of a deeper node state

This matters because everything downstream depends on whether the current native split is fundamental or only provisional.

Current rebuild update (QNG-CPU-040):

- `phi` is identified as a near-perfectly synchronized phase field (sync_order > 0.94 universally)
- Without history: phi achieves near-perfect global sync (sync ≈ 0.999)
- With history: history.phase feedback breaks perfect sync → anti-ordering (structured local diversity)
- phi-L_eff coupling: weak and sign-unstable (Tier-2, |corr| < 0.46)
- phi→C_eff coupling: indirect and topology-dependent (Tier-2, |corr| < 0.5 on 3/5 seeds)
- phi is NOT a coherence proxy or load proxy — it is the native phase/oscillation mode
- phi is primitive at proxy level: its role (U(1) phase oscillator with memory-driven desync)
  is not reducible to C_eff or L_eff
- Open: topological structure of phi (winding numbers?), phi→ψ=r*exp(i*phi) U(1) amplitude

## Problem 2: status of `Sigma`

The rebuild has improved the old project by replacing the overloaded scalar with `(C_eff, L_eff)`.

But the final status of `Sigma` is still open:

- derived compression
- estimator choice
- or unnecessary legacy carryover

This is one of the most important unresolved structural questions.

Current rebuild update (QNG-CPU-039):

- `sigma = C_eff` is FALSIFIED: corr < 1.0 on all seeds; C_eff has independent inputs
  (mismatch, phase) beyond sigma
- `sigma ∝ C_eff` is SUPPORTED: corr(sigma, C_eff) ∈ [0.707, 0.954] universally
- `sigma` also couples to `L_eff`: corr(sigma, L_eff) ∈ [0.438, 0.821] on all seeds
- C_eff-vs-L_eff primacy is topology-dependent (Tier-2): C_eff wins on 3/5 seeds,
  L_eff wins on 2/5 seeds
- R²(sigma ~ C_eff + L_eff) > 0.71 universally — sigma substantially recoverable
  from the full effective layer
- Physical role: sigma is a self-regularizing coherence primitive coupled to the
  FULL effective layer (not C_eff alone); it is NOT redundant
- Open: dynamical law for sigma in terms of effective fields, large-N limit,
  whether sigma is primitive or derivable from a deeper internal node variable

## Problem 3: exact GR recovery

The current rebuild has only proxy-level GR support.

Open question:

- can the rebuilt geometry sector recover a controlled Einstein-like regime beyond weak-field proxies

Until that is answered, the bridge to GR remains promising but incomplete.

Current rebuild update:

- a staged exact-GR recovery program now exists
- the first linearized assembly step is now testable
- the first linearized assembly step is now proxy-supported
- the first linearized curvature step is now proxy-supported
- the first effective scalar source-matching step is now proxy-supported
- the first tensorial assembly step is now proxy-supported (E_tt, E_xx with opposite-sign source alignment)
- the first tensorial source matching step is now proxy-supported (geometry channel sign separation: a_xx - a_tt = 11.2)

## Problem 4: exact QM recovery

The current rebuild has only correlator-like and transport-like QM proxies.

Open question:

- can the rebuilt dynamics recover operator-level or generator-level QM structure in a controlled way

Without that, the QM bridge remains suggestive rather than final.

Current rebuild update:

- a staged exact-QM recovery program now exists
- the first continuity-style assembly step is now testable
- a density-source balance law is now proxy-supported
- the first local generator assembly step is now proxy-supported
- the first operator-level candidate family is now proxy-supported
- the first operator-algebra proxy is now proxy-supported
- the first propagator proxy family is now proxy-supported
- the first propagator composition proxy is now proxy-supported
- the first semigroup closure proxy is now proxy-supported (3-step overlap 0.9988, per-step decay ratio 0.9994)
- the first mode/spectrum step is now proxy-supported
- the continuity-style balance remains weak
- the first complex amplitude proxy is now proxy-supported (QNG-CPU-041):
  ψ = C_eff * exp(i*phi); current direction correct on 4/5 seeds (corr>0);
  strong signal on seed 137 (corr=0.756); history amplifies |J| by 3–8x universally;
  scale balance weak: |J|>>|Δρ| by 100x — full continuity open
- the first calibrated continuity balance is now proxy-supported (QNG-CPU-042):
  α* > 0 on 4/5 seeds (correct sign: outflow→density decrease);
  R²_calib = 0.572 on seed 137; mean|α*| ≈ 10⁻³ (effective coupling constant);
  cv(|α*|) = 0.76 (moderate stability, Tier-2 topology-dependent)
- Madelung amplitude ψ_M = sqrt(C_eff)·exp(i·phi) is proxy-supported (QNG-CPU-043):
  marginal improvement over standard (mean R² 0.203 vs 0.200);
  amplitude choice NOT the bottleneck — bottleneck is phase gradient structure
- history-phase current proxy ψ_hp = C_eff·exp(i·h.phase) tested (QNG-CPU-044):
  FAIL (1/4 predictions); corr(phi,h.phase)=0.84–0.97 — they are not independent;
  phase variable choice NOT the bottleneck; three diagnoses ruled out:
  amplitude form, scale calibration, phase variable choice;
  root bottleneck identified as: current functional form J=C_i·C_j·sin(Δφ)
  is structurally wrong for QNG density flow
- mismatch-gradient current J_mis=C_i·C_j·(mis_j-mis_i) tested (QNG-CPU-045):
  FAIL (0/4 predictions); scale_ratio 6-12x (vs phi 100x) — scale problem SOLVED;
  topology-selective channels: seed 42→mismatch (0.354), seed 137→phi (0.572),
  seed 1729→mem (0.101); no universal single-channel winner;
  key finding: QNG probability current is MULTI-CHANNEL (topology-dependent mix
  of phi, mismatch, mem); joint multi-variable regression needed (QNG-CPU-046)
- multi-channel current joint regression tested (QNG-CPU-046):
  PASS (4/4 predictions); R²_combined > best_single on 5/5 seeds universally;
  mean R²=0.405 (from 0.256 best single), max R²=0.602 (seed 137);
  dominant channels: mismatch + mem (|α| ~10-20x > α_phi);
  phi contribution: weak, sign-unstable (Tier-2);
  established effective continuity law:
  ∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0
  physical interpretation: mismatch-driven diffusion + chi-memory correction
  open: dynamical law for couplings, non-linear extensions
  QM→GR cross-sector bridge tested (QNG-CPU-049): PASS (3/4);
  div_J_mis + div_J_mem couple directly to GR tensor: E_tt −17%, E_xx −8%;
  6-channel bridge: E_μν ≈ a·κ+b·q_src+c·src+d·m_eff+e·div_J_mis+f·div_J_mem;
  first direct cross-sector coupling confirmed; mismatch is QM→GR mediator
- multi-channel large-N probe (QNG-CPU-047):
  PARTIAL (2/4); multi-channel beats single at ALL N and ALL seeds (15/15 Tier-1);
  R² decreases with N: 0.586→0.405→0.269 (N=8→16→32);
  cause: denser graph (mean_deg 3.2→4.3→6.9) → more divergence cancellation;
  phi channel absent at N=32 (|α_phi|<0.0004 universally — large-N Tier-1 result);
  large-N limit: ∂_t(C_eff²) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0 (phi absent);
  sparse-graph law: strongest at N=8 (R²=0.909 on seed 42)
- degree-normalized current tested (QNG-CPU-048): FAIL (1/4);
  normalization makes R² negative — OLS ill-conditioned after rescaling;
  N-weakening is structural (not degree-dilution): CLOSED;
  multi-channel continuity law is a sparse-graph/UV law;
  large-N exact form requires mean-field or non-linear replacement (open)
- QM→GR coupling covariance tested (QNG-CPU-050): PASS (3/4) — **Tier-1**;
  6-channel improvement universal on 5/5 seeds (P1 PASS);
  |e_mis| > |f_mem| on 4/5 seeds (mismatch dominance — P2 PASS);
  sign(e_mis_ett) = −1 on 4/5 seeds (coupling direction universal — P3 PASS);
  P4 FAIL: sig_ratio < 0.1 on all seeds (max=0.096); 10% threshold too strict;
  QM coupling is ~3–10% of geometry channel across all topologies;
  mean e_mis = −0.175 is the universal QM→GR coupling constant at N=16;
  seed 2718 anomaly: e_mis and f_mem both flip sign (roles exchange); merits dedicated probe;
  **Tier-1 bridge established**: div_J_mis is the universal QM→GR mediator
- QM→GR coupling large-N probe (QNG-CPU-051): **PASS (4/4) — Tier-1-large-N**;
  sparse-graph law in GR sector: |e_mis(N=8)|=1.037 → |e_mis(N=16)|=0.259 → |e_mis(N=32)|=0.159;
  coupling weakens 6.5x from N=8→32; 5/5 seeds improve at N=32 (coupling never collapses);
  sign normalizes at N=32 (seed 2718 anomaly = sparse-topology effect);
  mean Δratio: −0.147 (N=8) → −0.043 (N=16) → −0.018 (N=32);
  **unified sparse-graph law**: same N-attenuation in QM continuity (CPU-047) and GR coupling;
  open: continuum limit — does |e_mis|→0 or →constant as N→∞?
- QM→GR coupling continuum limit probe (QNG-CPU-052): **PASS (4/4) — SATURATION CLASS**;
  N=64: mean|e_mis|=0.134 > sat threshold 0.120; decay ×0.84 per doubling (near-flat);
  seed 2718 fully normalized at N=64 (all 5 signs = −1); anomaly was sparse-topology effect;
  non-monotone Δratio: −0.147→−0.043→−0.018→−0.030 (improves at N=64 = new regime);
  power-law fit: |e_mis| ≈ 5.43×N^(−0.956) but dominated by sparse regime;
  local large-N exponent ~−0.25 → saturation more likely than vanishing;
  **best estimate: |e_mis(N→∞)| ≈ 0.08–0.12 (non-zero, physically meaningful)**;
  two regimes: sparse (N<32, steep decay) and dense (N≥32, saturation);
  open: N=128 probe to confirm; renormalization of e_mis; back-reaction with saturated coupling

## Problem 5: back-reaction closure

The rebuild still lacks a closed law that says how the GR-facing and QM-facing sectors source or constrain one another.

Open question:

- what is the first explicit back-reaction object of rebuilt QNG

This is probably the single most important next theoretical problem.

Current rebuild update:

- a first proxy closure object now exists
- but exact closure remains open
- the first source-response consistency step is now proxy-supported
- an upgraded two-channel closure v2 is now proxy-supported
- an upgraded two-channel source-response step is now proxy-supported
- a first GR-side scalar source composite now improves curvature fitting
- a first three-channel tensorial closure v3 is now proxy-supported (P_delta coeff: e_xx=-1.48, e_tt=+0.88, separation=2.36; E_xx fit improved 0.432→0.314)
- a first self-consistency fixed-point proxy is now supported: gamma=0.0025 (single-iteration contraction), tensor signs preserved under perturbation
- **QM↔GR back-reaction loop closed (QNG-CPU-053): PASS (4/4) — Tier-1**;
  GR→QM direction confirmed: E_tt_i → ∂_t(C_eff²)_i with γ_tt > 0 on ALL 5/5 seeds;
  complete back-reaction equation: ∂_t(ρ) ≈ -(α_phi·dJ_phi + α_mis·dJ_mis + α_mem·dJ_mem) + γ_tt·E_tt;
  γ_tt ≈ +0.003–0.008 (universal positive); mean R²_3ch=0.405 → R²_5ch=0.461 (+5.5%);
  seed 1729: strongest GR→QM coupling (+12.4% R² improvement);
  **self-regulating mechanism**: div_J_mis→↓E_tt→↓∂_t(ρ) (damping loop);
  **Problem 5 partially resolved at proxy level**;
  open: fixed-point equation; N-scaling of γ_tt; second-order GR correction
- **GR→QM back-reaction large-N probe (QNG-CPU-054): PASS (3/4) — Tier-1.5**;
  γ_tt persists at N=32 on 5/5 seeds (P1 PASS); γ_tt(32)<γ_tt(8) on 4/5 (sparse-graph law);
  P3 FAIL: sign unstable at N=8 (2 seeds negative); dense regime (N≥16) fully positive;
  **loop_strength = mean|γ_tt|×mean|e_mis| ≈ 0.00119 for N≥16 (saturates!)**;
  loop is subcritical (gain < 1) → self-stabilizing; finite loop constant confirmed;
  non-monotone γ_tt: 0.00784→0.00455→0.00747 (N=8→16→32), same pattern as CPU-052;
  open: fixed-point equation; continuum loop constant
- **Back-reaction fixed-point iteration (QNG-CPU-055): PARTIAL (2/4)**;
  P1 FAIL: QM-only does NOT need to converge — rollout already IS the fixed-point iteration (Δρ_0=0.0001);
  P2 PASS (5/5): QM+GR converges on all seeds (ratio 0.9534); GR refines beyond QM attractor;
  P3 PASS (3/5): FP shift > 0.001 on seeds 42,137,2718; correlated with γ_tt amplitude;
  P4 FAIL: both already at equilibrium — speed comparison undefined;
  **key finding: 24-step rollout IS the QM attractor; two-level hierarchy: QM + GR correction**;
  GR shift ~0.001 in ρ-space; seed 1729 a_mis sign inversion (topology-dependent);
  open: attractor geometry; FP shift vs observed ρ*; full self-consistent iteration
- **Attractor geometry (QNG-CPU-056): PASS (3/4) — Tier-1.5 — GR GEOMETRIC IMPRINT CONFIRMED**;
  P1 FAIL (2/5): Pearson(ρ*(QM), degree) not consistent at N=12 (mean +0.169); QM attractor driven
  by mismatch/memory fields, not raw degree;
  P2 PASS (5/5): |Pearson(δρ, E_tt)| > 0.99 on ALL seeds — GR correction IS E_tt spatially;
  P3 PASS (5/5): sign(Pearson(δρ,E_tt))=sign(γ_tt) on all seeds; gravitational sign law holds;
  P4 PASS (5/5): std_ratio ≈ 1.3–1.5 — GR correction strongly spatially oscillating (not uniform shift);
  **key finding: δρ ≈ K·η·γ_tt·E_tt — GR gravitational field DIRECTLY imprints onto matter density profile**;
  interpretation: QNG analogue of gravitational potential well filling — matter accumulates where E_tt large;
  open: degree-density law at large N; self-consistent iteration with updating E_tt; real-data unit mapping
- **Self-consistent back-reaction (QNG-CPU-057): PASS (3/4) — Tier-1.5 — LINEAR APPROX VALIDATED; EIGENMODE LOCKING**;
  P1 FAIL (3/5, negative-γ_tt seeds non-monotone but not diverging);
  P2 PASS (5/5): attractor_dist ≈ 0.000037 — linear and self-consistent attractors essentially identical;
  P3 PASS (5/5): |Pearson(δρ_sc, E_tt_final)| > 0.99 — geometric imprint survives nonlinearity;
  P4 PASS (5/5): E_tt_drift = 6.7%–19.6% (mean 13.4%) — E_tt changes substantially but direction preserved;
  **key finding: eigenmode locking — E_tt is approximate eigenvector of its own dynamics under back-reaction**;
  **back-reaction sector CLOSED**: linear approx exact, self-consistent loop confirmedopen: degree-density law at large N; real-data unit mapping; exact GR/QM recovery

## Problem 6: Lorentzian signature recovery

The current geometry estimator is intentionally Euclideanized.

Open question:

- how and where a Lorentzian signature emerges

Without this, any spacetime claim remains incomplete.

Current rebuild update:

- a first signature proxy now existed (QNG-CPU-014) but was limited to sign-pattern
- a first discriminant-based Lorentzian proxy is now proxy-supported (QNG-CPU-033):
  corr(h_tt, h_xx) = -0.972, h_xx > 0 on 100% of nodes, memory amplifies signature 331x
- h_tt < 0 predominantly, h_xx > 0 universally — linearized (-,+) signature confirmed
- exact strong-field Lorentzian recovery remains open
- light cone proxy is now proxy-supported (QNG-CPU-034):
  c_eff in [0.991, 1.002], std_hist/std_nohist = 9.7x, mean shift = 0.0021
- **Back-reaction metric signature correction (QNG-CPU-058): PARTIAL (2/4) — NULL RESULT**;
  P1/P2 PASS vacuously (mean E_tt = 0 identically by construction); P3/P4 FAIL;
  **key finding: Lorentzian signature is phi-driven, not ρ-driven**;
  GR back-reaction modifies matter density (ρ) but NOT metric signature (phi is held fixed);
  Δcorr signal: sign(Δcorr) ≈ sign(γ_tt) — positive γ_tt slightly REDUCES anti-correlation;
  matter sector and geometry sector quasi-independent at FP iteration timescale;
  open: phi dynamics under rollout; signature buildup over time steps; phi-metric coupling
- **Lorentzian signature buildup (QNG-CPU-059): PASS 1/4 — ANTI-HYPOTHESIS CONFIRMED**;
  P1 FAIL 0/5: |corr| STARTS at 0.999 at step 1 and DECAYS — NOT built up dynamically;
  P2 PASS 5/5: history consistently maintains stronger anti-correlation than no-history;
  P3 FAIL 0/5: Pearson(kuramoto,|corr|) = −0.73 — phi sync DESTROYS signature (inverse!);
  **key finding: signature is INITIAL-CONDITION IMPRINT, not emergent; phi disorder → high |corr|;
  phi sync → |corr| decay; history = signature PRESERVER (prevents sync collapse, not generator)**;
  CPU-033's 331× amplification = history prevents 331× decay, not builds up 331×;
  open: why |corr|≈1 at t=1 (statistical property of init_state?); N-dependence; anti-ordering quantification
- **Initial signature N-scaling (QNG-CPU-060): PASS 4/4 — Tier-1 — UNIVERSAL; Δ ~ N^(−0.87)**;
  P1 PASS all N: |corr_1| ≈ 0.9995 at N=8,16,32,64 — universal structural property of metric assembly;
  P2 PASS all N: signature always starts maximal, decays; P3 PASS: decay halves per N-doubling;
  P4 PASS: 5/5 seeds |corr_24| > 0.90 at N=64;
  **key finding: decay Δ ~ N^(−0.87) → 0 as N→∞; continuum limit has PERFECTLY STABLE Lorentzian signature**;
  mechanism: random phi → maximum phi disorder → maximal E_tt/E_xx anticorrelation (structural);
  decay = finite-N phi-sync effect; history slows sync → slows decay;
  **Problem 6 RESOLVED at mechanism level**: (1) structural initial signature, (2) N^(−0.87) decay, (3) history preservation
- **History signature preservation N-scaling (QNG-CPU-061): PASS 3/4 — Tier-1.5**;
  P1 PASS all N: decay_nohist > decay_hist universally; P2 PASS all N: |c|₂₄_hist > |c|₂₄_nohist;
  P3 FAIL: Δ_nohist NON-MONOTONE (peaks at N=32: 0.371 vs 0.225 at N=8); R²=0.398; P4 PASS (5/5 at N=32);
  **key findings: Δ_hist ~ N^(−0.889) confirmed (R²=0.991); no-history collapse peaks at N=32 (same sparse/dense transition as GR coupling);
  history benefit peaks at N=32 (most protective where most needed); continuum stability guaranteed only with history**;
  N=32 transition cross-sector: appears in GR coupling (CPU-051/052), signature decay (this test)
- **N=32 transition mechanism (QNG-CPU-062): PASS 3/4 — Tier-1.5 — MECHANISM PARTIALLY IDENTIFIED**;
  P1 FAIL (1/5 seeds peak at N=32): phi sync velocity does NOT peak at N=32 — increases monotonically
  (mean v_sync: 0.047→0.054→0.068→0.076); simple sync-speed-peak hypothesis FALSIFIED;
  P2 PASS: k̄ increases monotonically (3.20→4.33→6.92→13.03 — ER calibration confirmed);
  P3 PASS: clustering non-monotone: 0.3225→0.2538→0.2030→0.2051 (minimum at N=32, uptick at N=64);
  P4 PASS: Pearson(v_sync, Δ_nohist) = 0.662 — sync speed correlates with decay but doesn't explain non-monotone peak;
  **key finding: N=32 transition is multi-cause; clustering minimum at N=32 (most locally sparse topology)
  co-occurs with sync-speed crossing into "fast" regime; single mechanism insufficient;
  open: why clustering minimum + degree-transition → non-monotone no-history decay; N=32 protective failure mechanism**

## Problem 7: matter sector identification

We do not yet know what in the rebuilt substrate should count as matter content rather than geometry or memory bookkeeping.

Open question:

- what are the first matter-like degrees of freedom in QNG

This also blocks a serious stress-energy interpretation.

Current rebuild update:

- a first matter-like proxy object now exists
- Einstein equations proxy now proxy-supported (QNG-CPU-035):
  corr(E_tt,E_xx)=-0.975, w_eff=-0.69 (history) vs -1.03 (nohist), Δw=+0.34
- effective equation of state is in dark energy range (w ≈ -1)
- history sector introduces quantum correction to cosmological constant: Δw ≈ +0.34
- exact matter sector identification and covariant T_μν remain open

## Problem 8: `chi = m/c`

The rebuild correctly downgraded this from backbone to open issue.

Open question:

- does any defensible mass-scaling relation survive at all

This is still one of the most fragile inheritances from the old project.

Current rebuild update (QNG-CPU-037):

- `chi = m/c` is FALSIFIED at proxy level:
  corr(chi, m/c) = 0.19 on default seed; std across 5 seeds = 0.21;
  sign changes on seeds 1729 and 2718
- `chi ∝ L_eff` is SUPPORTED:
  corr(chi, L_eff) ∈ [0.551, 0.822] on all 5 seeds, always > 0.5
- Physical reidentification: chi is a coherence-memory field, not a mass proxy
- The proportionality chi ∝ L_eff has no derived dynamical law yet — open

## Problem 9: `tau`

The rebuild now separates:

- native memory
- effective lag
- phenomenological delay parameters

Open question:

- can any robust and nontrivial relation between these layers be derived

Until then, `tau` should remain layer-tagged and provisional.

Current rebuild update (QNG-CPU-038):

- universal scalar `tau` is FALSIFIED at proxy level:
  config timescales tau_p=2.857, tau_m=3.333, tau_d=4.000, cv=0.169 (not equal)
  per-node cv=11–17% — tau is NOT constant across nodes
- per-node `tau_eff = L_eff / C_eff` is SUPPORTED:
  history amplifies mean(tau) by 2.6x–4.6x on all 5 seeds
  corr(tau_eff, mem) ∈ [0.68, 0.83] on all 5 seeds
  mean(tau_hist) stable across seeds: range [0.099, 0.117], cv ≈ 7.3%
- Physical reidentification: tau is a per-node history-driven relaxation timescale
- Dynamical law for tau_eff, large-N limit behavior, and phenomenological delay
  connection remain open

## Problem 10: proxy-to-data step

The rebuilt workspace now has multiple phenomenology proxies.

Open question:

- which of them can survive first contact with real data without silently reintroducing old hidden assumptions

This is where the rebuild will either become substantially stronger than the old repo or fall back into the same traps.

## Covariance status (QNG-CPU-036)

Tested across K=5 seeds (42, 137, 1729, 2718, 31415):

Tier 1 — universal signals (topology-independent):
- corr(E_tt, E_xx) in [-0.998, -0.856] — always < -0.5
- w_eff in [-0.743, -0.623], mean=-0.669, std/mean=7.2% — stable
- tensor separation |e_xx - e_tt| in [0.86, 2.98] — always > 0.5
- history amplifies c_eff variation on all seeds

Tier 2 — topology-dependent:
- sign of individual P_delta coefficients (e_xx, e_tt) flips between topologies
- history amplification magnitude varies (2.8x to 23.4x)

## Current strongest zone

The strongest rebuilt zone right now is:

- native memory-sensitive dynamics
- split effective layer
- proxy bridge into GR and QM
- GR weak-field to scalar-source recovery path
- universal physical signals confirmed across K=5 graph topologies

## Current weakest zone

The weakest rebuilt zone right now is:

- exact recovery theorems
- back-reaction closure
- final matter interpretation
- any claim that depends on a universal `tau`
- `chi = m/c` has been falsified — remove from downstream claims
