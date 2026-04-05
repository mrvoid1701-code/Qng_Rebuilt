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

Observational lane (QNG-OBS-001):
`qng_obs_rotation_reference` (QNG-OBS-001) — data in `data/rotation/rotation_ds006_rotmod.csv`

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

Pre-registrations live in `07_validation/prereg/` (49 registered: GR-CPU-001, QM-CPU-001, QNG-CPU-001 through QNG-CPU-045, QNG-CPUGPU-001/002, QNG-GPU-001, QNG-OBS-001).

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
  - **Phi vortex program** (DER-QNG-025/026): sigma dissipative (040 PASS); phi vortex stable 2D (041 PASS); v5 Channel F sigma depletion at core confirmed (042 PASS, core/bulk ratio 2.2×, D_core=0.55); **3D vortex ring dynamically stable** (043 PASS — two-phase protocol, BETA_PHI=0.02, core=0.27, R_t=4.84); **ring lifetime T_lifetime=2400 Phase-2 steps** (044 PASS — gradual linear decay, T_lifetime×alpha=12>>1); **ring self-velocity: 1/R Biot-Savart NOT confirmed** (045 FAIL — phi diffusion drift dominates Phase-1, all R give same velocity; genuine substrate finding: BETA_PHI=0.02 is viscous regime); a_M fixing: A_vortex_ring=0.225, Delta_V²=a_M×alpha×M_baryon (DER-QNG-027); k_v open; **QNG-OBS-001: FAIL** — flat-ether per-galaxy model improves chi²/dof 2.26× (38.87→17.17) and fits 100% of galaxies better (Checks 1,2,4 PASS), but Pearson r(a_M, M_proxy)=-0.03 (Check 3 FAIL — gate > 0.40); a_M uncorrelated with baryonic mass; next: QNG-OBS-002 (global a_M) or QNG-OBS-003 (vs MOND)

- **Native derivation program** — `qng-native-derivation-program-v1.md` — six phases; A–D complete, E (QM embedding) weak, F (phenomenological reduction) structural only

**Gap status summary:**
- Gap 1 (isotropy): **closed for all statistically isotropic graphs** — second-moment condition (SMC) identified as necessary and sufficient (DER-QNG-024); confirmed numerically for cubic (QNG-CPU-037) AND perturbed irregular graph (QNG-CPU-039); open only for graphs with systematic anisotropy (excluded by experiment)
- Gap 3 (Newtonian potential): closed via GRAV-C1 (δ_C not ∇²C_eff)
- Gap 4 (ρ₀): partially constrained — formal constraint derived, order-of-magnitude estimate schematic, particle-level M_eff open
- Gap 5 (cosmological α): **reframed** — α ↔ Λ is an identification, not a derivation; status changed to open

Avoid red flags documented in `04_qng_pure/qng-red-flags-v1.md` (legacy mistakes to not repeat).
