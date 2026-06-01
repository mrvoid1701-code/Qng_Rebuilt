# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Relearning QNG** is a clean-room reconstruction of Quantum Node Gravity (QNG) theory by C.D Gabriel. The goal is to rebuild the theory with strict separation of concerns, full dependency tracing, and pre-registered validation — stricter than the legacy workspace. Legacy results may be consulted but their structure is not binding.

> **Start here: `THEORY_STATE.md`** — single-page living snapshot of what's locked, what's open, gap status, Einstein-correspondence verdicts, next-test queue, and latest audits. Read this before touching any theory file.

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

Hopfion lane (QNG-CPU-066 to QNG-CPU-072):
`qng_hopfion_reference` (CPU-066), `qng_hopfion_long_reference` (CPU-067), `qng_hopfion_ultralong_reference` (CPU-068), `qng_hopfion_100k_reference` (CPU-069), `qng_hopfion_shape_reference` (CPU-070), `qng_hopfion_gravity_reference` (CPU-071), `qng_hopfion_kgm_scan_reference` (CPU-072)

v7 back-reaction + mass identification (QNG-CPU-073 to QNG-CPU-076):
`qng_back_reaction_reference` (CPU-073), `qng_conservative_mring_reference` (CPU-074), `qng_extended_mring_reference` (CPU-075), plus CPU-076 proton mass calibration scan.

v8 canonical + Einstein correspondence (GPU lane, `tests/gpu/qng_v8_*`):
`qng_v8_canonical_gpu` (shared integrator/module), `qng_v8_ring_cache` (cached ring formation), plus probe scripts — `qng_v8_kg_dispersion_probe`, `qng_v8_shapiro_probe`, `qng_v8_shapiro_far_field_probe`, `qng_v8_shapiro_R_scan_probe`, `qng_v8_bending_probe`, `qng_v8_anisotropy_probe`, `qng_v8_tesla_gauge_probe`, `qng_v8_redshift_probe`, `qng_v8_wep_probe`. CPU-side theory counterparts in `tests/cpu/qng_v8_shapiro_theory_prediction.py` and `qng_v8_anisotropy_theory_analysis.py`.

Observational lane (QNG-OBS-001 through QNG-OBS-005):
`qng_obs_rotation_reference` (OBS-001), `qng_obs_rotation_global_reference` (OBS-002), `qng_obs_mond_reference` (OBS-003), `qng_obs_yukawa_reference` (OBS-004), `qng_obs_ring_reference` (OBS-005) — data in `data/rotation/rotation_ds006_rotmod.csv`

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

Pre-registrations live in `07_validation/prereg/` (91 registered: GR-CPU-001, QM-CPU-001, QNG-CPU-001 through QNG-CPU-076, QNG-CPUGPU-001/002, QNG-GPU-001/002/003/011/015/016/017/018/019/020, QNG-OBS-001 through QNG-OBS-005).

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
- **v7-symmetric** — v7 plus back-reaction term: `sigma_m_i += k_gm*(sigma_g_i - sigma_g_ref)`. Required for rings to fall into gravitational wells (confirmed CPU-073 PASS). Not yet promoted to official DER-QNG-033 revision; currently only in `qng_back_reaction_reference.py`.
- **v8** (`DER-QNG-042`) — **canonical extension** adding conjugate momenta: `(sigma_m, pi_m)` and `(phi, pi_phi)` get kinetic terms T_m + T_phi. Full Hamiltonian: `H_v8 = T_g + T_m + T_phi + E_v8`. Resolves `NOTE-QNG-013` (Lorentz), `NOTE-QNG-014` (action principle), and Gap 8 simultaneously. **Canonical V_couple**: `(g/2)·(SIGMA_M_REF - sigma_m)²·(1 - cos phi)` — Yukawa phi-mass via `DER-QNG-041` (g labeled Gap 9 EFT). **Effective inertias**: `mu_m=10.0`, `mu_phi=0.857` — derived from `c_g = c_m = c_phi` matching condition (`DER-QNG-042-prereqs §3.3`). **Consequence**: rings become dynamic patterns, not static solitons — the conserved `M_ring` from CPU-074 is a topological charge, not a rest mass. Einstein correspondence suite: `DER-QNG-044`.

**Key conventions (established in Newtonian limit program):**
- **GRAV-C1**: Newtonian potential Φ ∝ δ_C (deviation of C_eff from reference), NOT ∝ ∇²C_eff. Biharmonic identification is wrong. See `qng-geometry-estimator-v1.md` correction section.
- **GRAV-C2**: Normalization a·a_sigma = 2π is a convention; k cancels exactly from Poisson equation. G_QNG = β/z in substrate units (most natural choice). See `qng-poisson-assembly-v1.md` §1a.
- **η (noise amplitude)** is derived, not free: for 1D ring geometry, η_ring = sqrt(2·α·sqrt(α·(α+2β))). See `DER-QNG-023` (`qng-emergent-noise-v1.md`). Formula is geometry-dependent — mean-field and 3D cases differ.
- **Two G formulas reconciled** (DER-QNG-037): F1: G_QNG=β/z (single-sigma); F2: G_eff=k_gm/(z×α_g) (v7 cascade). Consistency condition CC: k_gm = β_g × α_g makes them equal. k_gm fine-tuning = α fine-tuning (both = Gap 5).

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
  - **Still open**: physical value of α unexplained (Gap 5); rotation curve prediction blocked until a_M–mass correlation resolved

- **Matter source identification** — `qng-matter-source-identification-v1.md`:
  - ρ₀ formal constraint derived: ρ₀ = m/∫M_eff dV (DER-QNG-021)
  - Sigmoid form physically motivated via 5 necessary constraints (DER-QNG-022)
  - **v5 Channel F CONFIRMED** — gamma_phi=0.10: sigma_core=0.21, sigma_bulk=0.47 (ratio 2.2×), D_core=0.55 (QNG-CPU-042, PASS)
  - **3D vortex ring dynamically stable** (QNG-CPU-043, PASS — BETA_PHI=0.02, core=0.27, R_t=4.84)
  - **Ring self-velocity: 1/R Biot-Savart NOT confirmed** (QNG-CPU-045, FAIL — phi diffusion drift dominates; BETA_PHI=0.02 is viscous regime)
  - **Inter-ring force: chirality-sensitive** (QNG-CPU-049, PASS — W+W+ repels, W+W- attracts; QNG-CPU-050 FAIL: non-monotonic Lennard-Jones-like potential with equilibrium near d≈3λ)
  - **OBS program conclusion**: chi-field rotation curve prediction requires per-galaxy amplitude uncorrelated with baryonic mass (OBS-001 Check 3 FAIL). Disk convolution (OBS-005) restores mass correlation (r=0.435) but profile λ→∞ in all fits. a_M–mass identification must be solved before zero-free-param rotation test is meaningful.

- **v7 two-field substrate program** (2026-04-07 onward):
  - Gap 7 RESOLVED (CPU-060): sigma_m ring survives K_BACK=0.10 in sigma_g
  - Gap 8 RESOLVED (DER-QNG-034, CPU-064): CHI_DECAY=0.020 stabilizes k=0 mode
  - **Hamiltonian constructed** (DER-QNG-036): H_v7 = T_g[chi] + E_v7; all channels = gradient flow of E_v7; KG for sigma_g confirmed (CPU-054)
  - **Back-reaction confirmed** (CPU-073, PASS): v7-symmetric extra_drift = 1.01 lu; sigma_m is overdamped (terminal velocity, not free-fall)
  - **G formulas reconciled** (DER-QNG-037): CC condition k_gm = β_g × α_g; k_gm fine-tuning = Gap 5
  - **Hopfion program** (CPU-066..072): Hopfion Q=1 topology tested vs vortex ring Q=0 in v7 substrate; gravitational sigma_g profile measured; K_GM scan for gravitational signal strength
  - **DER-QNG-044 Einstein correspondence** (2026-04-20): six probes consolidated against Einstein-era gravitational physics. Results: KG dispersion PASS (ω² = c_φ²k² + m² verified <2% across k∈{0,π/2}); Shapiro 1919-analog PASS (+26 lu delay through ring core, +39% vs vacuum); anisotropy 120% measured (scalar prediction 1.31 → 3.06× excess → genuine tensorial/kinetic-mode coupling); far-field 1/b falloff RULED OUT (ratio 0.96 vs 2.0); E=mc² FAIL (rings are dynamic patterns, not static solitons); WEP + Pound-Rebka INCONCLUSIVE. **Tesla U(1) gauge FALSIFIED**: v8 has only Z winding symmetry; V_couple is sine-Gordon (explicit U(1)→Z breaking); chi is NOT a gauge connection.
  - **Mass identification COMPLETE** (DER-QNG-038, CPU-074/075 PASS):
    - Canonical M_ring at T_P2=1000 (CPU-074): R=3:474.15, R=4:728.92, R=5:954.88
    - **M_ring is exactly conserved under Phase-3 diffusion** (ratio 1.000x — pure conservation law)
    - CPU-051 value of 158.4 (R=4, dissipative) is DEPRECATED for mass identification
    - a_M = 1.373×10^-3 (m_u = m_proton, k_back=1 convention); a ≈ 0.77 l_Planck
    - Baryon resonance ladder: R=4→N(938), R=5→Δ(1232), R=6→N*(1520), R=7→Δ(1700) — all within <1% using single a_M
    - Pattern: even R → I=1/2 (nucleon family), odd R → I=3/2 (delta family)
    - Roper N*(1440) ABSENT — QNG selects orbital excitations (L=1), not radial (n=2)
    - R=3 particle unidentified (predicted 611 MeV, no SM match)

- **Native derivation program** — `qng-native-derivation-program-v1.md` — six phases; A–D complete, E (QM embedding) weak, F (phenomenological reduction) structural only

**Gap status summary:**
- Gap 1 (isotropy): **closed** — SMC condition (DER-QNG-024); confirmed cubic (CPU-037) and perturbed graph (CPU-039)
- Gap 3 (Newtonian potential): **closed** via GRAV-C1 (δ_C not ∇²C_eff)
- Gap 4 (ρ₀): **substantially advanced** — canonical M_ring values established (CPU-074/075); baryon resonance ladder identified (DER-QNG-038); a_M=1.373×10^-3 fixed; minimum open: R=3 identification and QNG derivation of JP/I from ring radius
- Gap 5 (cosmological α): **open** — α ↔ Λ is identification, not derivation; k_gm fine-tuning reduces to same gap
- **Gap 7 (wave-matter compatibility)**: **RESOLVED** (2026-04-07) via v7 two-field substrate (DER-QNG-033, CPU-060)
- **Gap 8 (chi global instability)**: **RESOLVED** (2026-04-08) via CHI_DECAY=0.020 (DER-QNG-034 Fix B). K_GM sign bug also fixed: must be `-=` not `+=`.

**Structural gaps:**
- **Lorentz covariance** (`NOTE-QNG-013`): **substantially resolved** (2026-04-19) via `DER-QNG-043` + `QNG-GPU-012 v3`. v7+v8 makes all three sectors hyperbolic; μ_m=10.0, μ_phi=0.857 derived from c_g=c_m=c_phi (DER-QNG-042-prereqs §3.3); GPU-012 v3 symplectic run PASSED G1/G2/G3 on L=32³ (spread 0.41% σ_g/σ_m, 1.64% φ; cross-sector 0.82%; amplitude spread 0.00% across 25×). Items (ii) dispersion isotropy and (iii) non-linear corrections **numerically closed**. Only item (i) ring-interior c_φ (Unruh acoustic-metric analogue) remains — scope phenomenology (CPU-077), not theory-gap.
- **Action principle** (`NOTE-QNG-014`): **resolved for v8** via `DER-QNG-042`: H_v8 = T_g + T_m + T_phi + E_v8 is fully conservative with three kinetic terms; gradient-flow dissipation replaced by symplectic evolution (Yoshida4). H_v7 = T_g + E_v7 (DER-QNG-036) remains the gradient-flow predecessor.
- **Spin from ring radius**: the baryon resonance identification (DER-QNG-038) shows R encodes JP and I, but the QNG derivation of these quantum numbers from ring geometry is open.

**Falsified / retracted candidates:**
- **DER-QNG-040** V(sigma_m) as rest-mass source — **FALSIFIED** (GPU-018 FAIL_H3_STRUCTURAL): Goldstone theorem forbids a sigma_m-only cure; phi Goldstone mode remains massless regardless of V(sigma_m) shape.
- **DER-QNG-041** Yukawa phi-mass via `sigma_g·(1-cos phi)` — **falsified as sole cure** (GPU-019 halted at g=0.08 with 3/5 FAIL); retained in v8 as part of V_couple via DER-QNG-042.
- **Tesla U(1) gauge interpretation** — **FALSIFIED** (DER-QNG-044 Tesla probe): v8 has only Z winding symmetry; V_couple is sine-Gordon (explicit U(1)→Z breaking); chi is not a gauge connection.
- **Einstein 1911 1/b Shapiro falloff** — **RULED OUT** (DER-QNG-044 far-field probe): ratio 0.96 vs predicted 2.0 for 1/b. Consistent with GR log(b) or saturation.

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

# Hopfion visualization
py scripts/qng_render_hopfion_ether.py
```

Generated assets already in `scripts/`: `ether_ring_preview.png`, `ether_two_rings_v2.png`, `ether_two_rings_animation.gif`, `ether_hopfion_v7.png`.

## Key Simulation Notes

- **Fully deterministic**: v5/v7 has no stochastic Xi(t) term — identical initial conditions give identical results every run. "Independent trials" require either different ring positions or adding noise.
- **Buffered output**: run with `py -u script.py` to see progress in real time on Windows.
- **Runtime estimates**: L=20, 1500 Phase-2 steps ≈ 3-5 min per scenario on CPU; 4 radii × 5 DELTA_m values ≈ 30-40 min.
- **v7 stability requirement**: use CHI_DECAY=0.020 (not 0.005). Criterion: `K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA)`. With K_BACK=0.10, DELTA=0.20, ALPHA=0.005: needs CHI_DECAY ≥ 0.016 for stability; use 0.020 for margin. CHI_DECAY=0.005 causes Jeans-like k=0 instability (sigma_g global collapse by T=2000).
- **v7 K_GM sign**: `sigma_g -= k_gm*(sigma_m_ref - sigma_m)` — MINUS sign. Positive sign gives repulsive potential (bug present in CPU-062/063 results; corrected 2026-04-08). All scripts from CPU-064 onward use correct sign.
- **Three-phase protocol** (CPU-073/074/075): Phase 1 (300 steps, no Channel F/G) → phi vortex forms. Phase 2 (1500 steps, Channel F active, CHI_DECAY=0.020) → ring forms. Phase 3 (optional 1000 conservative steps: no A, no F, no chi_decay) → mass measurement. **Canonical M_ring is the T_P2=1000 snapshot** (not Phase-3 end, which is identical due to exact conservation).
- **M_ring conservation**: Under Phase-3 dynamics (pure diffusion, no Channel A or F), sum(sigma_m) is exactly conserved on the periodic lattice (Laplacian sums to zero). M_ring = N×sigma_m_ref - sum(sigma_m) is therefore constant. Phase-3 adds no new information beyond the T_P2 snapshot.
- **sigma_m overdamped**: In v7, sigma_m has no kinetic term T_m — it is in gradient-flow (overdamped) regime. Ring drift in a gravitational well is TERMINAL VELOCITY (drift rate constant), not free-fall (accelerating). True F=ma requires v8 with conjugate momentum pi_m.
- **v8 symplectic integrator**: use `yoshida4_step` (4th-order symplectic) from `tests/gpu/qng_v8_canonical_gpu.py`. Unlike v7 gradient flow, v8 is time-reversal symmetric and conserves H_v8 to <10⁻³ over T=250 lu. Typical v8 parameters: `BETA_PHI=0.06`, `MU_PHI=0.857`, `G_V_COUPLE=0.22`, `CHI_DECAY_V7=0.020`, `K_BACK=0.10`.
- **v8 vs v7 equilibria**: rings that were static under v7 gradient flow are dynamic oscillating patterns under v8 symplectic evolution. The topological charge `M_ring = N·sigma_m_ref - sum(sigma_m)` is still conserved, but it is NOT a rest mass (there is no `E = M_ring · c²` for these solitons).
- **Ring cache**: `form_ring_cached(L, R, T_P1, T_P2)` in `tests/gpu/qng_v8_ring_cache.py` memoizes Phase 1+2 rings by parameter hash under `07_validation/audits/qng-v8-stability-probe-v1/ring_cache/`. Reuse across Shapiro / bending / anisotropy probes to save ~10 min per test.
- **Windows console encoding**: avoid Unicode symbols (Δ, ↔, ×, σ, φ, α, ω, etc.) in print() statements — use ASCII equivalents (D, <->, x, sigma, phi, alpha, omega) to prevent cp1252 codec errors on Windows terminals.

Avoid red flags documented in `04_qng_pure/qng-red-flags-v1.md` (legacy mistakes to not repeat).
