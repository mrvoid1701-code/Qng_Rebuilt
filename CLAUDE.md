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

Multi-ring / force lane (QNG-CPU-046 to QNG-CPU-051):
`qng_multi_ring_reference` (QNG-CPU-046), `qng_ring_force_reference` (QNG-CPU-047), `qng_ring_force_linear_reference` (QNG-CPU-048), `qng_ring_chirality_reference` (QNG-CPU-049), `qng_ring_force_separation_reference` (QNG-CPU-050), `qng_ring_sigma_integral_reference` (QNG-CPU-051)

Wave equation + v7 two-field substrate (QNG-CPU-052 to QNG-CPU-065):
`qng_wave_kg_reference` (CPU-052/054), `qng_ring_hamiltonian_reference` (CPU-056), `qng_ring_hamiltonian_snapshot_reference` (CPU-057), `qng_ring_mass_spectrum_reference` (CPU-058), `qng_ring_conservative_reference` (CPU-059), `qng_two_field_ring_reference` (CPU-060), `qng_two_field_extended_reference` (CPU-061), `qng_two_field_kgm_scan_reference` (CPU-062), `qng_two_field_spectrum_reference` (CPU-063), `qng_two_field_kgm_scan_v2_reference` (CPU-064), `qng_two_field_delta_m_reference` (CPU-065)

Observational lane (QNG-OBS-001 through QNG-OBS-005):
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

Pre-registrations live in `07_validation/prereg/` (71 registered: GR-CPU-001, QM-CPU-001, QNG-CPU-001 through QNG-CPU-065, QNG-CPUGPU-001/002, QNG-GPU-001, QNG-OBS-001 through QNG-OBS-005).

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
- **v6** (`DER-QNG-030`) — adds Channel G: sigma_i += k_back × chi_i (chi back-reaction on sigma). Required for Klein-Gordon wave equation: ∂²_t s = v²∇²s - m²s with v²=k_back×chi_rel/6, m²=k_back×delta. Confirmed by QNG-CPU-054 (PASS). **Critical**: Channel G incompatible with stable vortex rings in single-sigma substrate (Gap 7 — k_back stability threshold < 0.0015 vs k_back needed for waves ≥ 0.01). See `DER-QNG-028/030`.
- **v7** (`DER-QNG-033`) — **two-field substrate** resolving Gap 7: `(sigma_g, sigma_m, chi, phi)` per node. sigma_g hosts Channel G (KG waves); sigma_m hosts Channel F (vortex rings), NO Channel G. Coupling: `sigma_g -= k_gm*(sigma_m_ref - sigma_m)` (MINUS sign — matter depletion sources attractive potential). chi couples to sigma_g only (or also sigma_m via DELTA_m, see CPU-065). **Stability constraint**: `K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA)` (DER-QNG-034) — requires CHI_DECAY ≥ 0.020 at current parameters (was 0.005 — causes Jeans instability). See `qng-gap8-stability-analysis-v1.md`.

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
  - **Phi vortex program** (DER-QNG-025/026): sigma dissipative (040 PASS); phi vortex stable 2D (041 PASS); v5 Channel F sigma depletion at core confirmed (042 PASS, core/bulk ratio 2.2×, D_core=0.55); **3D vortex ring dynamically stable** (043 PASS — two-phase protocol, BETA_PHI=0.02, core=0.27, R_t=4.84); **ring lifetime T_lifetime=2400 Phase-2 steps** (044 PASS — gradual linear decay, T_lifetime×alpha=12>>1); **ring self-velocity: 1/R Biot-Savart NOT confirmed** (045 FAIL — phi diffusion drift dominates Phase-1, all R give same velocity; genuine substrate finding: BETA_PHI=0.02 is viscous regime); a_M fixing: A_vortex_ring=0.225, Delta_V²=a_M×alpha×M_baryon (DER-QNG-027); k_v open; **QNG-CPU-046: PASS** — two rings (R=4, z=6 and z=18, separation=12) in same lattice; chi field AMPLIFIED 4× at midpoint (z=12-13: chi=13.2 two-rings vs 3.4 single-ring); explanation: geometric (effective Yukawa distance = sqrt(R²+(d/2)²) = sqrt(16+36) = 7.2 lattice units, NOT 12; Yukawa at 7.2 ≈ 12% per ring); both rings stable (Checks 1,2,3 PASS); **QNG-CPU-047: PASS (but qualitative finding)** — epsilon=0.1 enables chi→phi Channel E; ring positions differ between eps=0 and eps=0.1 (Check 2: diff=3 PASS, Check 3: ring2 effect=2 PASS); however eps=0.1 is VIOLENT — phi perturbation per step = 0.1×chi~13 = 1.3 rad >> linear regime → trajectories chaotic; rings scrambled not cleanly displaced; genuine substrate finding: linear regime requires eps << 1/chi_max; **QNG-CPU-048: PASS** — epsilon=0.005 (phi perturbation=0.065 rad, linear regime); zone-restricted detection; S(t) separation tracking 3000 steps; sep_diff=5 (gate >1, PASS); trend REPULSION (early mean sep=3.2, late=4.9); BUT: single ring wanders z=7→2→11→4→1→11 under eps=0.005 — chi-induced phi drift is large; repulsion signal sits on noisy drift; **QNG-CPU-049: PASS — CHIRALITY SENSITIVE** — same chirality (W+W+) → REPULSION (early=3.2, late=4.9); opposite chirality (W+W-) → ATTRACTION (early=11.6, late=6.7); chirality_diff=4 (gate >2); **phi winding number acts as topological charge: like charges repel, opposite charges attract**; attraction signal cleaner than repulsion (Δ=4.9 vs Δ=1.7); signal at T<3000 only — at T=3000-6000 rings separate again (oscillatory); **QNG-CPU-053: FAIL** — 3 "independent" trials identical (simulation fully deterministic, no Xi(t) in v5); at 6000 steps d=10 score=-2.358 (repulsion in second half), single-ring drift=4.471 >> force signal; **conclusion: inter-ring force at eps=0.005 too weak/mixed with drift to cleanly separate; CPU-049 attraction signal was T<3000 fluctuation not stable trend; deterministic substrate needs stochastic Xi(t) for independent trials**; **QNG-CPU-050: FAIL on Yukawa monotonicity, but key finding** — force profile vs separation is NON-MONOTONIC (not simple Yukawa): d=4 score=-4.5 (repulsive, rings destabilize), d=6 score=-0.8, d=8 score=+1.3, d=10 score=+6.3 (maximum attraction), d=12 score=+4.9; suggests Lennard-Jones-like potential with equilibrium near d≈10 (≈3λ); at d<6 phi fields of opposite-chirality rings interfere destructively; simple Yukawa decay NOT confirmed; force structure is richer than chi-field profile alone predicts; **QNG-OBS-001: FAIL** — flat-ether per-galaxy model improves chi²/dof 2.26× (38.87→17.17) and fits 100% of galaxies better (Checks 1,2,4 PASS), but Pearson r(a_M, M_proxy)=-0.03 (Check 3 FAIL — gate > 0.40); a_M uncorrelated with baryonic mass; **QNG-OBS-002: FAIL** — A_vortex=0.225 fixed (zero free params) gives 1.000× improvement; units mismatch: substrate value is dimensionless, data is (km/s)²; median residual 2185 (km/s)² vs A_VORTEX=0.225 — conversion factor f≈9700 (km/s)²/lattice-unit required, set by rho_0 (open); **QNG-OBS-003: FAIL** — MOND (a_0=1.2e-10 m/s², zero free params) improves 1.70× (38.87→22.84), 57.3% galaxies improved; QNG-OBS-001 per-galaxy beats MOND (2.26× vs 1.70×) but uses 171 free params vs 0; **key finding: QNG flat profile is wrong — MOND radial profile does real work; chi-field must have radial dependence (Yukawa C_K(r), not flat limit) to compete with MOND at zero free params**; **QNG-OBS-004: FAIL** — Yukawa profile C_K(r,λ) with 2 global free params (λ, A): best-fit λ→∞ (flat limit), ratio 1.02×; MOND (0 params, 1.70×) beats Yukawa (2 params, 1.02×); finding: no universal Yukawa profile — each galaxy needs its own amplitude; flat profile insufficient, Yukawa profile also insufficient at global level; **OBS program conclusion: chi-field rotation curve prediction requires per-galaxy amplitude that is uncorrelated with baryonic mass (OBS-001 Check 3) — matter source identification (rho_0, a_M) must be solved before any zero-free-param rotation curve test is meaningful**; **QNG-OBS-005: FAIL** — ring Yukawa disk convolution (DER-QNG-031): best-fit λ→∞ again, ratio 1.058× (< MOND 1.702×); BUT **Check 6 PASS: Pearson r(A_gal, M_proxy)=0.435 > 0.40** — disk convolution RESTORES mass correlation (OBS-001 had r=-0.03); physical interpretation: (a) disk convolution gives baryonic-shaped chi-field profile in Coulomb limit (same radial structure as V²_baryon → barely improves over baryon-only); (b) the amplitude per galaxy now correlates with mass because disk convolution weights inner mass correctly; **key finding: the PROFILE (λ→∞ flat/Coulomb) is wrong, but the AMPLITUDE geometry (disk convolution) is physically correct; QNG needs λ finite AND comparable to galaxy scale to produce a halo-like chi-field profile different from the baryonic disk; the Coulomb-limit disk convolution IS essentially Newtonian gravity — no dark matter equivalent unless λ is cosmological AND the chi-field halos fill spherically**; **updated OBS conclusion: (1) disk convolution is the correct source model (not point source); (2) λ must be constrained from theory (N4 gap); (3) a_M–mass correlation is now restored by correct geometry — OBS-001 failure was a geometry artifact not a fundamental problem**

- **v7 two-field substrate program** (2026-04-07/08): Gap 7 resolved (CPU-060). Gap 8 resolved (DER-QNG-034, CPU-064). **v7 mass spectrum** (CPU-063): E_ring~R^1 (string tension, geometric) vs v5 H~R^2 (kinetic, chi). Pion match lost; R=3/R=5=0.520 ≈ K meson (1.4%) — likely coincidental (Einstein review). **DELTA_m coupling** (CPU-065 in progress): chi += DELTA_m*(sigma_m_ref - sigma_m) recovers kinetic mass at ring while preserving two-field separation. Spectrum shifts from E~R^1 toward H~R^2 as DELTA_m increases.

- **Native derivation program** — `qng-native-derivation-program-v1.md` — six phases; A–D complete, E (QM embedding) weak, F (phenomenological reduction) structural only

**Gap status summary:**
- Gap 1 (isotropy): **closed** — SMC condition (DER-QNG-024); confirmed cubic (CPU-037) and perturbed graph (CPU-039)
- Gap 3 (Newtonian potential): **closed** via GRAV-C1 (δ_C not ∇²C_eff)
- Gap 4 (ρ₀): **substantially advanced** — DER-QNG-029: 3-unknown unit system (a, τ, m_u); M_ring(R=4, T=1000)=158.4 lu (CPU-051); M_ring NOT conserved (decays); ρ₀ = m_particle/(a_M × 158.4); minimum open set: (m_particle, a_M, a) require external input
- Gap 5 (cosmological α): **open** — α ↔ Λ is identification, not derivation
- **Gap 7 (wave-matter compatibility)**: **RESOLVED** (2026-04-07) via v7 two-field substrate (DER-QNG-033, CPU-060). sigma_m ring survives with K_BACK=0.10 in sigma_g. Single-sigma substrate destroys ring at k_back ≥ 0.02. CPU-059 confirmed: v5 ring is NOT a soliton of H (50-step half-life in conservative dynamics).
- **Gap 8 (chi global instability)**: **RESOLVED** (2026-04-08) via CHI_DECAY=0.020 (DER-QNG-034 Fix B). K_GM coupling at CHI_DECAY=0.005 drove Jeans-like k=0 mode instability (growth rate 0.03/step >> chi_decay=0.005/step; Jeans length L_J≈16 lattice units). With CHI_DECAY=0.020: K_BACK×DELTA=0.020 < threshold=0.025 ✓. **Also**: K_GM sign bug fixed (2026-04-08): must be `-=` not `+=` (depletion → attractive potential).

**Structural gaps (from 2026-04-06/08 Einstein/Newton reviews):**
- **Lorentz covariance** (`NOTE-QNG-013`): synchronous update = preferred foliation; parabolic dynamics, not hyperbolic. Conservative limit H = T + E is the candidate. **Most important open structural gap.**
- **Action principle** (`NOTE-QNG-014`): all 6 channels derive from gradient flow of E[sigma,chi,phi]; but gradient flow is dissipative. Lorentz-covariant action requires conservative limit.
- **Wave equation** (`DER-QNG-028/030`): KG confirmed at L=50 (CPU-054 PASS, v²=k_back×chi_rel/6 corrected from ×beta). CPU-052 FAIL at L=20 (overdiffusive — sigma diffusion τ≈2 steps << chi buildup 1/chi_decay=200 steps). v7 gravitational potential is **double-Yukawa** (DER-QNG-035): Phi(r) = convolution of two Yukawa kernels (sigma_m → sigma_g cascade). For equal screening lengths: modified exp profile. New G_eff formula: G_eff ∝ k_gm/(z×alpha).
- **Conservative Hamiltonian for v7**: open — H = T_g[chi] + T_m[pi_m] + E[sigma_g,sigma_m,phi] not yet constructed. sigma_m needs its own conjugate momentum pi_m if it is a fundamental field (Einstein review, 2026-04-07).

## Visualization Scripts (`scripts/`)

```bash
# Static 3-panel view (sigma / chi / phi)
py scripts/qng_visualize_ether_3d.py --mode ring        # single vortex ring
py scripts/qng_visualize_ether_3d.py --mode two_rings   # W+W- two rings + chi field
py scripts/qng_visualize_ether_3d.py --mode phi_slice   # phi winding slices
py scripts/qng_visualize_ether_3d.py --mode ring --save out.png

# Animated GIF (XZ slice: sigma + chi + phi over time)
py scripts/qng_animate_ether.py --mode two_rings --save scripts/out.gif
py scripts/qng_animate_ether.py --mode single    --phase2 2000 --every 50
py scripts/qng_animate_ether.py --mode birth               # ring forming from Phase 1
```

Generated assets already in `scripts/`: `ether_ring_preview.png`, `ether_two_rings_v2.png`, `ether_two_rings_animation.gif`.

## Key Simulation Notes

- **Fully deterministic**: v5/v7 has no stochastic Xi(t) term — identical initial conditions give identical results every run. "Independent trials" require either different ring positions or adding noise.
- **Buffered output**: run with `py -u script.py` to see progress in real time on Windows.
- **Runtime estimates**: L=20, 1500 Phase-2 steps ≈ 3-5 min per scenario on CPU; 4 radii × 5 DELTA_m values ≈ 30-40 min.
- **v7 stability requirement**: use CHI_DECAY=0.020 (not 0.005). Criterion: `K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA)`. With K_BACK=0.10, DELTA=0.20, ALPHA=0.005: needs CHI_DECAY ≥ 0.016 for stability; use 0.020 for margin. CHI_DECAY=0.005 causes Jeans-like k=0 instability (sigma_g global collapse by T=2000).
- **v7 K_GM sign**: `sigma_g -= k_gm*(sigma_m_ref - sigma_m)` — MINUS sign. Positive sign gives repulsive potential (bug present in CPU-062/063 results; corrected 2026-04-08). All scripts from CPU-064 onward use correct sign.
- **Two-phase protocol**: Phase 1 (no Channel F, no Channel G) lets phi vortex form cleanly. Phase 2 activates all channels. Standard: PHASE1=300, PHASE2=1500 for L=20.

Avoid red flags documented in `04_qng_pure/qng-red-flags-v1.md` (legacy mistakes to not repeat).
