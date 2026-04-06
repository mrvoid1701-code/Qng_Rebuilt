# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Relearning QNG** is a clean-room reconstruction of Quantum Node Gravity (QNG) theory by C.D Gabriel. The goal is to rebuild the theory with strict separation of concerns, full dependency tracing, and pre-registered validation — stricter than the legacy workspace. Legacy results may be consulted but their structure is not binding.

## Running Tests and Audits

No build system. All executables are Python scripts; no install step required.

**On Windows use `py` (not `python` or `python3`):**

```bash
# Validate workspace structure compliance
py tests/cpu/dependency_audit.py
py tests/cpu/theory_purity_audit.py

# Run individual reference tests (CPU correctness lane)
py tests/cpu/qng_native_update_reference.py
py tests/cpu/<any_reference>.py

# GPU lane
py tests/gpu/gpu_env_probe.py
py tests/gpu/qng_cpu_gpu_agreement.py
```

Test results are recorded in `07_validation/audits/`.

**All CPU reference scripts** (one per pre-registration):

QNG-CPU-001 to QNG-CPU-018 (original lane):
`qng_native_update_reference`, `qng_effective_field_reference`, `qng_geometry_estimator_reference`, `qng_lorentzian_signature_proxy_reference`, `qng_gr_weakfield_proxy_reference`, `qng_gr_linearized_curvature_reference`, `qng_gr_linearized_assembly_reference`, `qng_gr_effective_source_matching_reference`, `qng_source_response_consistency_reference`, `qng_backreaction_closure_reference`, `qng_bridge_closure_v2_reference`, `qng_lensing_proxy_reference`, `qng_rotation_support_proxy_reference`, `qng_timing_delay_proxy_reference`, `qng_trajectory_lag_proxy_reference`, `qng_expansion_proxy_reference`, `qng_matter_sector_proxy_reference`

QM-facing (QNG-CPU-019 to QNG-CPU-028):
`qng_qm_*_reference` (10 scripts: coherence_proxy, continuity_assembly, density_source_balance, generator_assembly, mode_spectrum, operator_algebra, operator_assembly, propagator_composition, propagator_proxy, semigroup_closure)

Newtonian limit + structural (QNG-CPU-029 to QNG-CPU-038):
`qng_generation_order_reference`, `qng_quasi_static_source_reference`, `qng_quasi_static_3d_light_reference`, `qng_p1_spectrum_reference`, `qng_p1_v4_reference`, `qng_phi_dephasing_reference`, `qng_g_qng_consistency_reference`, `qng_alpha_screening_reference`, `qng_3d_isotropy_reference`, `qng_emergent_noise_reference`

Matter sector (QNG-CPU-039 to QNG-CPU-045):
`qng_perturbed_lattice_isotropy_reference` (QNG-CPU-039), `qng_sigma_stability_reference` (QNG-CPU-040), `qng_phi_vortex_reference` (QNG-CPU-041), `qng_sigma_depletion_vortex_reference` (QNG-CPU-042), `qng_vortex_ring_3d_reference` (QNG-CPU-043), `qng_ring_lifetime_reference` (QNG-CPU-044), `qng_ring_self_velocity_reference` (QNG-CPU-045)

Multi-ring / force lane (QNG-CPU-046 to QNG-CPU-048):
`qng_multi_ring_reference` (QNG-CPU-046), `qng_ring_force_reference` (QNG-CPU-047), `qng_ring_force_linear_reference` (QNG-CPU-048), `qng_ring_chirality_reference` (QNG-CPU-049), `qng_ring_force_separation_reference` (QNG-CPU-050), `qng_ring_sigma_integral_reference` (QNG-CPU-051)

Observational lane (QNG-OBS-001 through QNG-OBS-004):
`qng_obs_rotation_reference` (OBS-001), `qng_obs_rotation_global_reference` (OBS-002), `qng_obs_mond_reference` (OBS-003), `qng_obs_yukawa_reference` (OBS-004) — data in `data/rotation/rotation_ds006_rotmod.csv`

## Architecture: One-Way Build Order

The directory numbers enforce a strict dependency direction — nothing in a lower-numbered tier may depend on a higher-numbered tier:

```
01_gr_pure        → GR foundations only (no graph substrate, no QNG primitives)
02_qm_pure        → QM foundations only (no observational fitting)
03_gr_qm_bridge   → Correspondence layer between GR and QM
04_qng_pure       → Native QNG: nodes, edges, states, update laws, emergent geometry
05_phenomenology  → Observable consequences (cosmology, lensing, rotation, timing, trajectory)
06_claims         → Explicit claim records with upstream dependencies
07_validation     → Pre-registrations, evidence, audits (specs only — executables in tests/)
08_governance     → Policy, decision records, paper drafts
09_templates      → Document templates (axiom/claim/definition/derivation/evidence/test)
10_exports        → Paper figures and renderable assets
data/             → Datasets only
scripts/          → Utilities
tests/cpu/        → CPU reference implementations (correctness lane)
tests/gpu/        → GPU scale/stress tests
```

## Document Types

Every file declares a `type:` field in its header. The allowed types are:

- **axiom** — foundational assumption, no derivation required
- **definition** — introduces a primitive or derived object
- **derivation** — derives a result from upstream inputs; may NOT contain test results
- **note** — informal commentary
- **claim** — explicit claim with status and upstream dependencies; may NOT contain free-form derivation
- **test** — executable test spec declared in `07_validation/`; executables live in `tests/`
- **evidence** — observational/experimental data; may NOT define primitives
- **decision** — governance decision record

## Hard Classification Rules (from `00_meta/classification_rules.md`)

1. `01_gr_pure` — no `Sigma`, `chi`, `tau`, or graph-native terms
2. `04_qng_pure` — no observational fit parameters declared primitive unless required by ontology
3. `05_phenomenology` — must list every upstream QNG object used; may not redefine them
4. `06_claims` — not derivations and not evidence; require full dependency traces
5. `07_validation` — validation may test claims and compare CPU/GPU; may NOT create ontology or silently alter definitions

## Testing Policy (from `00_meta/testing_policy.md`)

Every test must declare: `test_id`, `category`, `hardware`, `inputs`, `outputs`, `gates`, `tolerances`, `artifact paths`.

- **CPU lane** = canonical correctness reference
- **GPU lane** = scale and stress; must match CPU within declared tolerance
- **CPU+GPU lane** = cross-hardware agreement tests

Pre-registrations live in `07_validation/prereg/` (61 registered: GR-CPU-001, QM-CPU-001, QNG-CPU-001 through QNG-CPU-052, QNG-CPUGPU-001/002, QNG-GPU-001, QNG-OBS-001 through QNG-OBS-004).

## Key Theory Objects (from `04_qng_pure/`)

**Substrate primitives:**
- **Node state** — triplet `(sigma_i, chi_i, phi_i)` where `sigma ∈ [0,1]`, `chi ∈ [-1,1]`, `phi ∈ [-π,π]`
- **History summary** — triplet `(M_i, D_i, P_i)` — memory, mismatch accumulator, phase coherence
- **Update operator** — four-channel law: `Delta_self + Delta_rel + Delta_hist + Xi(t)`
- **Adjacency/linkage** — graph connectivity primitive

**Derived/effective (NOT primitives):**
- **C_eff** — coarse-grained coherence field
- **L_eff** — coarse-grained load/charge field
- **Emergent metric, effective curvature, effective propagators**

**Update law versions:**
- **v2** (`DER-QNG-010`) — baseline four-channel law
- **v3** (`DER-QNG-015`, **locked**) — adds δ cross-coupling σ→χ (Channel D); required for generation order and Newtonian limit
- **v4** (`DER-QNG-016`) — adds ε·χ_i in φ channel (Channel E); tested by QNG-CPU-033
- **v5** (`DER-QNG-026`) — adds Channel F: gamma_phi*(1-|Z_i|)*sigma_i depletion term; confirmed by QNG-CPU-042 (2D) and QNG-CPU-043 (3D ring). Note: phi channel in 3D ring test uses separate BETA_PHI=0.02 (not sigma's BETA=0.35) to prevent ring collapse.
- **v6 (proposed)** — adds Channel G: sigma_i += k_back × chi_i (chi back-reaction on sigma). Required for Klein-Gordon wave equation: ∂²_t s = v²∇²s - m²s with v²=k_back×chi_rel, m²=k_back×delta. Without Channel G, linearized v5 vacuum is purely diffusive (parabolic), no wave equation. See `DER-QNG-028` (`qng-wave-equation-derivation-v1.md`).

**Key conventions (established in Newtonian limit program):**
- **GRAV-C1**: Newtonian potential Φ ∝ δ_C (deviation of C_eff from reference), NOT ∝ ∇²C_eff. Biharmonic identification is wrong. See `qng-geometry-estimator-v1.md` correction section.
- **GRAV-C2**: Normalization a·a_sigma = 2π is a convention; k cancels exactly from Poisson equation. G_QNG = β/z in substrate units (most natural choice). See `qng-poisson-assembly-v1.md` §1a.
- **η (noise amplitude)** is derived, not free: for 1D ring geometry, η_ring = sqrt(2·α·sqrt(α·(α+2β))). See `DER-QNG-023` (`qng-emergent-noise-v1.md`). Formula is geometry-dependent — mean-field and 3D cases differ.

**Axiomatic additions:**
- **AX-QNG-004** (`qng-graph-isotropy-assumption-v1.md`): discrete graph Laplacian → isotropic 3D continuum Laplacian (Assumption D2). Sufficient condition: z=6 cubic lattice. Confirmed numerically by QNG-CPU-037 (isotropy ratio 1.077 on 20³ cubic lattice).

**Unresolved symbols — consult status files before use:**
- **chi (χ)** — three distinct roles: `chi_native` / `chi_effective` / `chi_phenomenological`; status in `04_qng_pure/qng-chi-status-v1.md`. The map `chi = m/c` is **downgraded** — not core ontology.
- **Sigma (Σ)** — three distinct roles: `Sigma_ontic` / `Sigma_effective` / `Sigma_phenomenological`; status in `04_qng_pure/qng-sigma-status-v1.md`. Not yet promoted to primitive.

Any file using unlabeled `chi` or `Sigma` must be flagged as containing unresolved symbol status.

## Open Programs (from `04_qng_pure/`)

- **Newtonian limit** — `qng-newtonian-limit-program-v1.md` — N1–N7 substantially complete:
  - N1: screened Poisson equation derived (DER-QNG-012, DER-QNG-018)
  - N2: G_QNG = β/z identified; CODATA matching (DER-QNG-019)
  - N3: identity G_QNG = α·λ²_screen confirmed algebraically and numerically (QNG-CPU-035)
  - N4: α ↔ Λ identification (λ_screen = R_Hubble) — **reframed as open**: the identification is stated but why α takes its physical value is not derived (DER-QNG-020, Gap 5)
  - N5: D2 (isotropy) formally characterized by second-moment condition SMC (DER-QNG-024); confirmed for z=6 cubic (QNG-CPU-037) AND perturbed irregular graph (QNG-CPU-039, perturbation 0.3); Gap 1 closed for any statistically isotropic graph
  - N6: GRAV-C1 (Φ ∝ δ_C) and GRAV-C2 (normalization convention) resolved
  - N7: η derived from ring FDT — not a free parameter (DER-QNG-023, QNG-CPU-038)
  - **Matter stability**: sigma channel is purely dissipative (QNG-CPU-040, PASS); phi vortices topologically stable (QNG-CPU-041, PASS — W=+1 and W=-1 persist 5000 steps, vortex plaq gradient ratio 21.6x); sigma depletion at vortex core requires phi→sigma coupling not yet in v3/v4 (v5 open program); DER-QNG-025 corrected — π₂(S¹)=0 means no topologically stable point defects in 3D, hedgehog monopole claim removed; **v5 Channel F (DER-QNG-026) CONFIRMED** — gamma_phi=0.10 produces sigma_core=0.21 vs sigma_bulk=0.47 (ratio 2.2×) at vortex core, D_core=0.55 (QNG-CPU-042, PASS)
  - **Still open**: λ-screening confirmed (QNG-CPU-036), but physical value of α unexplained; particle-level M_eff requires phi vortex simulation (QNG-CPU-041, proposed)

- **Matter source identification** — `qng-matter-source-identification-v1.md` — required to ground `M_eff` to physical mass-energy:
  - ρ₀ formal constraint derived: ρ₀ = m/∫M_eff dV (DER-QNG-021, Constraint rho0-C1)
  - Sigmoid form physically motivated via 5 necessary constraints and Fermi-Dirac analogy (DER-QNG-022)
  - Coefficients a_M, a_D, a_P remain free; connecting M_eff to Standard Model masses is open
  - **Phi vortex program** (DER-QNG-025/026): sigma dissipative (040 PASS); phi vortex stable 2D (041 PASS); v5 Channel F sigma depletion at core confirmed (042 PASS, core/bulk ratio 2.2×, D_core=0.55); **3D vortex ring dynamically stable** (043 PASS — two-phase protocol, BETA_PHI=0.02, core=0.27, R_t=4.84); **ring lifetime T_lifetime=2400 Phase-2 steps** (044 PASS — gradual linear decay, T_lifetime×alpha=12>>1); **ring self-velocity: 1/R Biot-Savart NOT confirmed** (045 FAIL — phi diffusion drift dominates Phase-1, all R give same velocity; genuine substrate finding: BETA_PHI=0.02 is viscous regime); a_M fixing: A_vortex_ring=0.225, Delta_V²=a_M×alpha×M_baryon (DER-QNG-027); k_v open; **QNG-CPU-046: PASS** — two rings (R=4, z=6 and z=18, separation=12) in same lattice; chi field AMPLIFIED 4× at midpoint (z=12-13: chi=13.2 two-rings vs 3.4 single-ring); explanation: geometric (effective Yukawa distance = sqrt(R²+(d/2)²) = sqrt(16+36) = 7.2 lattice units, NOT 12; Yukawa at 7.2 ≈ 12% per ring); both rings stable (Checks 1,2,3 PASS); **QNG-CPU-047: PASS (but qualitative finding)** — epsilon=0.1 enables chi→phi Channel E; ring positions differ between eps=0 and eps=0.1 (Check 2: diff=3 PASS, Check 3: ring2 effect=2 PASS); however eps=0.1 is VIOLENT — phi perturbation per step = 0.1×chi~13 = 1.3 rad >> linear regime → trajectories chaotic; rings scrambled not cleanly displaced; genuine substrate finding: linear regime requires eps << 1/chi_max; **QNG-CPU-048: PASS** — epsilon=0.005 (phi perturbation=0.065 rad, linear regime); zone-restricted detection; S(t) separation tracking 3000 steps; sep_diff=5 (gate >1, PASS); trend REPULSION (early mean sep=3.2, late=4.9); BUT: single ring wanders z=7→2→11→4→1→11 under eps=0.005 — chi-induced phi drift is large; repulsion signal sits on noisy drift; **QNG-CPU-049: PASS — CHIRALITY SENSITIVE** — same chirality (W+W+) → REPULSION (early=3.2, late=4.9); opposite chirality (W+W-) → ATTRACTION (early=11.6, late=6.7); chirality_diff=4 (gate >2); **phi winding number acts as topological charge: like charges repel, opposite charges attract**; attraction signal cleaner than repulsion (Δ=4.9 vs Δ=1.7); still noisy but direction is consistent across both runs; **QNG-CPU-050: FAIL on Yukawa monotonicity, but key finding** — force profile vs separation is NON-MONOTONIC (not simple Yukawa): d=4 score=-4.5 (repulsive, rings destabilize), d=6 score=-0.8, d=8 score=+1.3, d=10 score=+6.3 (maximum attraction), d=12 score=+4.9; suggests Lennard-Jones-like potential with equilibrium near d≈10 (≈3λ); at d<6 phi fields of opposite-chirality rings interfere destructively; simple Yukawa decay NOT confirmed; force structure is richer than chi-field profile alone predicts; **QNG-OBS-001: FAIL** — flat-ether per-galaxy model improves chi²/dof 2.26× (38.87→17.17) and fits 100% of galaxies better (Checks 1,2,4 PASS), but Pearson r(a_M, M_proxy)=-0.03 (Check 3 FAIL — gate > 0.40); a_M uncorrelated with baryonic mass; **QNG-OBS-002: FAIL** — A_vortex=0.225 fixed (zero free params) gives 1.000× improvement; units mismatch: substrate value is dimensionless, data is (km/s)²; median residual 2185 (km/s)² vs A_VORTEX=0.225 — conversion factor f≈9700 (km/s)²/lattice-unit required, set by rho_0 (open); **QNG-OBS-003: FAIL** — MOND (a_0=1.2e-10 m/s², zero free params) improves 1.70× (38.87→22.84), 57.3% galaxies improved; QNG-OBS-001 per-galaxy beats MOND (2.26× vs 1.70×) but uses 171 free params vs 0; **key finding: QNG flat profile is wrong — MOND radial profile does real work; chi-field must have radial dependence (Yukawa C_K(r), not flat limit) to compete with MOND at zero free params**; **QNG-OBS-004: FAIL** — Yukawa profile C_K(r,λ) with 2 global free params (λ, A): best-fit λ→∞ (flat limit), ratio 1.02×; MOND (0 params, 1.70×) beats Yukawa (2 params, 1.02×); finding: no universal Yukawa profile — each galaxy needs its own amplitude; flat profile insufficient, Yukawa profile also insufficient at global level; **OBS program conclusion: chi-field rotation curve prediction requires per-galaxy amplitude that is uncorrelated with baryonic mass (OBS-001 Check 3) — matter source identification (rho_0, a_M) must be solved before any zero-free-param rotation curve test is meaningful**

- **Native derivation program** — `qng-native-derivation-program-v1.md` — six phases; A–D complete, E (QM embedding) weak, F (phenomenological reduction) structural only

**Gap status summary:**
- Gap 1 (isotropy): **closed for all statistically isotropic graphs** — second-moment condition (SMC) identified as necessary and sufficient (DER-QNG-024); confirmed numerically for cubic (QNG-CPU-037) AND perturbed irregular graph (QNG-CPU-039); open only for graphs with systematic anisotropy (excluded by experiment)
- Gap 3 (Newtonian potential): closed via GRAV-C1 (δ_C not ∇²C_eff)
- Gap 4 (ρ₀): **substantially advanced** — DER-QNG-029 establishes 3-unknown unit system (a, τ, m_u); G matching gives C1; Planck-scale inconsistent with galactic Yukawa (λ_phys sub-Planck); empirical f≈43000 (km/s)²/lu from OBS-002; M_ring(R=4, T=1000)=158.4 lattice-units measured (CPU-051); **key finding: M_ring is NOT conserved — decays monotonically (T=500: 191.6 → T=2000: 74.8); sigma depletion is dynamical, not a static charge**; ρ₀ = m_particle / (a_M × 158.4) at T=1000 reference; minimum open set: (m_particle, a_M, a) — all three still require external physical input
- Gap 5 (cosmological α): **reframed** — α ↔ Λ is an identification, not a derivation; status changed to open

**Structural gaps added 2026-04-06 (Einstein/Newton review):**
- **Lorentz covariance** (`NOTE-QNG-013`, `qng-preferred-frame-analysis-v1.md`): synchronous update = preferred foliation; C_eff equation is parabolic (∂_t C_eff = α(...) + β∇²C_eff), NOT hyperbolic — Lorentz covariance is ASSUMED via Planck-scale argument, not derived; the conservative limit of the substrate (H = T + E) is the candidate for Lorentz-covariant dynamics; **this is the most important open structural gap**
- **Action principle** (`NOTE-QNG-014`, `qng-action-principle-candidate-v1.md`): all 6 update channels derive from a single free-energy functional E[sigma,chi,phi] (gradient flow); substrate is NOT arbitrary phenomenology; but gradient flow is dissipative/irreversible — a Lorentz-covariant action requires the conservative limit H = T + E (open program)
- **Wave equation** (`DER-QNG-028`, `qng-wave-equation-derivation-v1.md`): linearized v5 vacuum (D_i=0) gives ∂_t s = -αs + β∇²s (parabolic — chi slaved, no back-reaction, no wave equation); Channel G (k_back×chi_i term in sigma update) produces Klein-Gordon; v6 defined in DER-QNG-030; **QNG-CPU-052: FAIL** — wave propagates (Check 1 PASS, r=12.5 at T=50) and k_back-dependent propagation confirms KG mass effect (k_back=0.1 gives r=9.5 vs 12.5); but v_meas=0.17 ≠ v_pred=0.59; **finding: overdiffusive regime** — sigma diffusion τ_diff≈2 steps << chi buildup 1/chi_decay=200 steps; KG phase velocity (0.59) vs group velocity at dominant k (0.17) discrepancy; need w>>10, L>>50 for clean wave measurement; C3 constraint requires dedicated long-wavelength test

Avoid red flags documented in `04_qng_pure/qng-red-flags-v1.md` (legacy mistakes to not repeat).
