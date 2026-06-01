# QNG Gap Inventory — Status as of 2026-04-25

This document is the **single source of truth** for the gap status of
QNG theory. Updated after every major closure, retraction, or new
identification.

## Theory layer stack (current)

| Layer | Definition | Status |
|---|---|---|
| **v7** | (σ_g, σ_m, φ, χ) gradient-flow scalars | LOCKED |
| **v8** | v7 + (π_m, π_φ) canonical momenta, symplectic | LOCKED |
| **v10** | v8 + canonical quantization [Ψ̂, Π̂†] = iℏ | LOCKED |
| **v11** | v10 + h_ij rank-2 tensor (spin-2 graviton) | DRAFT axiom |
| **v12** | v11 + A_{ij} edge gauge field (spin-1 photon) | DRAFT axiom |

Each extension is **axiomatic**, not derived from the substrate. v11
parallels Standard Model adding Higgs; v12 parallels lattice gauge
theory introduction of A_μ.

## Constants STATUS (locked)

| Constant | Formula | Value | Status |
|---|---|---|---|
| c² | β_φ/(z·μ_φ) | 0.01167 | DERIVED |
| G | β_g/z | 0.0583 | DERIVED |
| ℏ | √(β_φ·μ_φ·z)/C_cubic | 0.2326 | DERIVED via Stability Principle |
| Λ | (Stability Principle) | exact 0 | DERIVED |
| a_L (lattice spacing) | unit-bridge | 0.305 ℓ_Planck | DERIVED |
| a_M (mass per node) | unit-bridge | 1.524 m_Planck | DERIVED |
| a_T (time step) | unit-bridge | 0.033 t_Planck | DERIVED |

## Gap inventory (17 gaps tracked)

| # | Topic | Status | Notes |
|---|---|---|---|
| 1 | Graph isotropy | **CLOSED** | SMC condition (DER-QNG-024); CPU-037, CPU-039 |
| 3 | Newtonian potential | **CLOSED** | GRAV-C1: Φ ∝ δ_C |
| 4 | ρ₀ / mass identification | **OPEN** (regressed) | DER-QNG-038 retracted via Gap 13+14 |
| 5 | Cosmological α | **OPEN** | α ↔ Λ identification only; factor-7 match across 125 orders, but Paper 4 BAO test FAILED at 33×LCDM (CPU-131) |
| 7 | Wave-matter compatibility | **CLOSED** | v7 two-field substrate |
| 8 | χ global instability | **CLOSED** | CHI_DECAY=0.020 fix |
| 9 | EFT g coupling | **OPEN** | g = 0.22 phenomenological |
| 10 | Dimension selection | **OPEN** | Substrate dim-agnostic at linear level (GPU-026) |
| 11 | χ canonicalization | **CLOSED** | R1 orbital attractor (GPU-031f) |
| 12 | Tensor graviton ontology | **CLOSED structurally** via v11 (axiomatic); savant: "axiomatic GR import" caveat | DER-QNG-072 |
| 13 | **Scale separation** | **OPEN HIGH** | 22-order tension between substrate (Planck) and observed (MeV/GeV); blocks particle ID, mass predictions. **2026-04-25 update**: classical α power-law ansatz (DER-QNG-079) FALSIFIED via CPU-141 — λ_eff is L-INDEPENDENT (CV<1%). Only quantum one-loop running (5-8 weeks of work) could revive (DER-QNG-081 sketch) |
| 14 | M_ring lattice dependence | **OPEN** | Ratios L-dependent (CPU-126); DER-QNG-038 retracted |
| 15 | Electromagnetism | **CLOSED structurally** via v12 (axiomatic) | DER-QNG-076; CPU-135/136 |
| 16 | Charge quantization | **FORMALLY SOLVED** via v12 winding-charge correspondence | CPU-137 |
| 17 | Fine structure constant α_fine | **OPEN NEW** | e is INPUT to v12, not derived |
| **DM** | Dark matter mechanism | **STRUCTURALLY IMPOSSIBLE in v10/v11/v12** (2026-04-25) | DER-QNG-082: all 4 phases exhausted. Phase 1 (chi-Yukawa) FALSIFIED CPU-132; Phase 2a (vortex rings) charged under v12; Phase 2b (σ_g defects) RULED OUT structurally CPU-142; Phase 2c (hopfion) charged under v12 CPU-143; Phase 3 (modified gravity) NOT predicted CPU-134. Topological stability ↔ EM charge LINKED in v12. Requires v13 extension or honest scope acceptance. |
| **Non-linear gravity** | Full Einstein equations | **OPEN** | v11 linear only; no path to Riemann tensor self-coupling |

## Phenomenological tests STATUS

### v10 quantum reformulation (DER-QNG-068)

6/6 PASS for static-source phenomena:
- KG dispersion ✅
- Shapiro delay ✅
- Tensorial coupling (eikonal) ✅
- E=mc² ⚠️ (PASS structurally, nucleon match retracted via Gap 13)
- Far-field Yukawa ⚠️ (PASS-conditional via Gap 5)
- WEP + Pound-Rebka ✅

### Empirical tests against real data (Phase D, 2026-04-25)

| Test | CPU | Result | Implication |
|---|---|---|---|
| Galaxy rotation (DS-006, 176 galaxies) | CPU-127 | QNG correction 10⁻¹⁰ vs 51% DM disc | Confirmed: QNG ≠ DM at galactic scale |
| Cluster lensing (Bullet, PSZ2) | CPU-130 | QNG 10⁻¹² vs 200kpc Bullet offset | Confirmed: QNG ≠ Bullet DM |
| Pioneer + flyby anomaly | CPU-128 | QNG 10⁻³³ vs 8.7e-10 (24 orders short, wrong sign) | Confirmed: QNG ≠ Pioneer |
| Planck TT acoustic peaks | CPU-129 | Peak positions match LCDM | PASS (consistent) |
| Planck TT low-ℓ ISW | CPU-129 | ℓ=2 deficit, Paper 4 §5.3 predicts excess | YELLOW FLAG |
| **eBOSS BAO (5 measurements)** | **CPU-131** | **LCDM χ²/dof=0.98, QNG-Yukawa-toy χ²/dof=33** | **MAJOR FLAG: Paper 4 §5.2 fails** |

### Particle physics tests

| Test | CPU | Result | Implication |
|---|---|---|---|
| Standard ring winding | CPU-138 | N=1 verified | v12 charge q=±e for vortex rings |
| Coulomb force re-interpretation | CPU-138 + CPU-049 | W+W+ repels, W+W- attracts | Consistent with EM Coulomb (v12 retro-validation) |
| Electron mass match | CPU-138 | Off by 10²⁵ (Planck-scale ring) | Gap 13 blocks quantitative ID |

## Solid claims (after all retractions)

These survived all audits and can be defended in publication:

1. **c, G, ℏ derived** from substrate parameters + Stability Principle
2. **Λ = 0 structural** (Stability Principle)
3. **SI unit-bridge** at Planck scale, machine precision
4. **DER-QNG-068** GR static-source 6/6 PASS in v10 (with caveats on Test 1 nucleon)
5. **v11** spin-2 graviton sector (axiomatic, but consistent)
6. **v12** spin-1 photon sector (axiomatic, but consistent)
7. **Empirical scope confirmed** by negative tests (B1, B2, B3 — QNG honestly cannot replace DM/Pioneer)

## Retracted / abandoned claims

- **DER-QNG-038** baryon ladder (Gap 13 + 14)
- **CPU-115** "m_ring = 938 MeV nucleon match" (Gap 13)
- **Tesla U(1) gauge** identification of χ (DER-QNG-044)
- **OBS-001** "chi-as-DM"  per-galaxy fit improvement was parameter-fitting trivial (CPU-132)
- **Trajectory lag** legacy proxy (DER-TRJ-001) under v10 (CPU-128)

## Pending revisions

- **Paper 4 §5.2** (Yukawa BAO prediction): MAJOR REVISION required
  after CPU-131 failure
- **Paper 4 §5.3** (low-ℓ ISW): yellow flag from CPU-129
- **THEORY_STATE.md**: needs Gap 13/14/15/16/17 added to Section 3

## Next-step priorities

### Immediate (high impact, moderate effort)

1. **Gap 13 attack**: scale separation — blocks ALL quantitative particle physics
   - Investigate renormalization-group flow in QNG
   - OR explore if effective constants run between scales
2. **σ_g topological defects** as DM (untested option)
3. **Hopfion long-time stability** test (extend CPU-068 to T=10⁵ lu)

### Medium term

4. **Paper 4 revision** with honest empirical caveats
5. **Non-linear gravity completion** (Gap 12 partial → full)
6. **SU(2) electroweak extension** (v13?) for full Standard Model embedding

### Long term

7. **Modified Friedmann derivation** from QNG substrate (saves Paper 4)
8. **QNG cosmology with v12** for primordial baryogenesis-like mechanisms

## Honest summary

QNG provides a **substrate-derived microscopic origin for c, G, ℏ, Λ** at
Planck scale, with structural extensions for matter (v10), gravity tensor
(v11), and electromagnetism (v12). The substrate-level claims are SOLID.

**However**, scale separation (Gap 13) prevents quantitative match to
particle physics phenomenology, dark matter remains unsolved at the
mechanism level, and full non-linear GR is not yet derived from substrate.

The theory is at a **mature substrate framework + open phenomenology**
stage. Paper 1 (ℏ) and Paper 2 (Λ=0) are publishable; Paper 3 (framework)
is honest comprehensive review; Paper 4 (Yukawa) needs major revision after
BAO failure.

## Files of record

- Theory layers: `04_qng_pure/qng-vN-foundational-v1.md` for N=10/11/12
- Constants derivation: `04_qng_pure/qng-hbar-derivation-paper-draft-v1.md` (DER-QNG-067)
- Stability Principle: `04_qng_pure/qng-stability-principle-v1.md` (DER-QNG-066)
- Gap docs: `04_qng_pure/qng-gapNN-*-v1.md` for each gap
- Tests: `tests/cpu/qng_cpuNNN_*.py` for each numerical verification
- Audits: `07_validation/audits/<topic>/REPORT.md` for major test reports
- Papers: `papers/paper{1,2,3,4}_*_alpha.md` for publication drafts
- This inventory: `GAP_INVENTORY.md` (single source of truth)
