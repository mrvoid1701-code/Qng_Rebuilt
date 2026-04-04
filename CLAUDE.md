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
`qng_native_update_reference`, `qng_effective_field_reference`, `qng_geometry_estimator_reference`, `qng_lorentzian_signature_proxy_reference`, `qng_gr_weakfield_proxy_reference`, `qng_gr_linearized_curvature_reference`, `qng_gr_linearized_assembly_reference`, `qng_gr_effective_source_matching_reference`, `qng_source_response_consistency_reference`, `qng_backreaction_closure_reference`, `qng_bridge_closure_v2_reference`, `qng_lensing_proxy_reference`, `qng_rotation_support_proxy_reference`, `qng_timing_delay_proxy_reference`, `qng_trajectory_lag_proxy_reference`, `qng_expansion_proxy_reference`, `qng_matter_sector_proxy_reference`, `qng_qm_*_reference` (8 QM-facing scripts).

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

Pre-registrations live in `07_validation/prereg/` (35 registered: GR-CPU-001, QM-CPU-001, QNG-CPU-001 through QNG-CPU-028, QNG-CPUGPU-001/002, QNG-GPU-001).

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

**Unresolved symbols — consult status files before use:**
- **chi (χ)** — three distinct roles: `chi_native` / `chi_effective` / `chi_phenomenological`; status in `04_qng_pure/qng-chi-status-v1.md`. The map `chi = m/c` is **downgraded** — not core ontology.
- **Sigma (Σ)** — three distinct roles: `Sigma_ontic` / `Sigma_effective` / `Sigma_phenomenological`; status in `04_qng_pure/qng-sigma-status-v1.md`. Not yet promoted to primitive.

Any file using unlabeled `chi` or `Sigma` must be flagged as containing unresolved symbol status.

## Open Programs (from `04_qng_pure/`)

- **Newtonian limit** — `qng-newtonian-limit-program-v1.md` — required before phenomenology can produce quantitative predictions
- **Matter source identification** — `qng-matter-source-identification-v1.md` — required to ground `M_eff` to physical mass-energy
- **Native derivation program** — `qng-native-derivation-program-v1.md` — six phases; A–D complete, E (QM embedding) weak, F (phenomenological reduction) structural only

Avoid red flags documented in `04_qng_pure/qng-red-flags-v1.md` (legacy mistakes to not repeat).
