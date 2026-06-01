# Session Report — COSMO Audit, 2026-04-25

**Author**: C.D Gabriel (with Claude Opus 4.7, autonomous block)
**Started**: 2026-04-25, autonomous block while user at work
**Goal**: Do QNG cosmology CORRECTLY, with multiple verifications, before
moving to Gap 13.

---

## Executive summary

QNG-Yukawa cannot replace Lambda in cosmology. This is a **structural
result** confirmed across multiple independent observational tests with
robustness verification.

Paper 4 main claim retracted. Cosmology adopts honest open scope.

The locked content of QNG (c, G, ℏ derivation; Stability Principle;
static gravity) is unaffected.

---

## What was tested

### 1. Comprehensive BAO diagnostic
**File**: `tests/cpu/qng_cosmology_v2_diagnostic.py`

Six cosmological hypotheses against eBOSS DR16 BAO (5 measurements at
z = 0.7, 0.85, 1.48):

| Model | χ²/dof | Verdict |
|---|---|---|
| LCDM (Ω_m=0.315, Ω_Λ=0.685) | **0.975** | EXCELLENT |
| Pure matter (Ω_m=1, Λ=0) | 103 | CATASTROPHIC |
| Yukawa-modified Friedmann | **161** | STRUCTURAL FAIL |
| LCDM with proper b/cdm split | 0.973 | EXCELLENT |
| CPL best-fit (w0=-1, wa=0.2) | **0.884** | better than LCDM |

### 2. CMB acoustic-peak cross-check
**File**: `tests/cpu/qng_cosmology_cmb_peak_check.py`

Independent test via D_M(z*=1090) for first peak position:

| Model | D_M(z*) Mpc | l_peak | Match observed 220? |
|---|---|---|---|
| LCDM | 13933 | 208 | YES |
| Pure matter | 8627 | 129 | NO |
| Yukawa-mod | 7574 | 113 | NO (off by factor ~2) |
| CPL (w0=-1,wa=0.2) | 13862 | 207 | YES |

### 3. Robustness verification
**File**: `tests/cpu/qng_cosmology_robustness_check.py`

Triple-verified Yukawa failure across:
- H_0 ∈ {67.0, 67.4, 70.0, 73.0} → χ²/dof always > 145
- r_d ∈ {140, 145, 147, 150, 155} → χ²/dof always > 130
- Three BAO datasets (eBOSS, +6dFGS, +SDSS DR12)
- Two Yukawa forms: exp(-x)(1+x) vs exp(-x)
- Full R/λ scan from 0.05 to 2.0

**Best-case Yukawa**: χ²/dof = 103 (when R/λ → 0, screening vanishes,
reducing to pure matter — i.e., Yukawa contributes nothing).

LCDM remains χ²/dof < 1 across all variations. Failure is robust.

---

## Why Yukawa-Friedmann fails (structural diagnosis)

Yukawa screening operates at scale `r ~ λ_screen`. With `λ_screen ~ R_Hubble_today`:

| Scale | R_H/λ | Yukawa relevance |
|---|---|---|
| z = 0 (today) | ~1 | significant |
| z = 0.7 (BAO LRG) | ~0.5 | reduced |
| z = 1.5 (BAO QSO) | ~0.4 | minimal |
| z = 1090 (CMB) | ~0.001 | irrelevant |

So at all observationally relevant redshifts, Yukawa is irrelevant or
weak. `H_QNG(z)` tracks pure matter, which is too fast by factor 1.5-2.

This is fundamentally different from how Λ acts: Λ contributes at all z,
with relative importance changing with z. Yukawa contribution PEAKS at
z=0 and vanishes at z>>1 — wrong sign of redshift dependence.

---

## What we updated

1. **`papers/paper4_yukawa_cosmological_alpha.md`**: title and abstract
   rewritten to reflect retraction; main claim withdrawn; honest scope
   documented.

2. **`04_qng_pure/qng-cosmology-diagnosis-v1.md`** (DER-QNG-090, NEW):
   formal locked-finding document.

3. **`THEORY_STATE.md`**: COSMO section added at top with summary.

4. **Memory file**: `project_cosmology_no_de_2026_04_25.md` saved for
   future sessions.

5. **Test scripts** (NEW):
   - `tests/cpu/qng_cosmology_v2_diagnostic.py`
   - `tests/cpu/qng_cosmology_cmb_peak_check.py`
   - `tests/cpu/qng_cosmology_robustness_check.py`

---

## What stands (locked positive content)

- **Λ = 0 structural prediction** from Stability Principle (Paper 2).
- **Yukawa kernel form for static sources** (DER-QNG-018).
- **Newtonian gravity at all sub-cosmological scales** (full Solar
  System, galactic, cluster scales operate in pure-Poisson regime).
- **All 6/6 Einstein static-source phenomenology tests** (DER-QNG-044
  in v10).
- **Derived c, G, ℏ** matched to SI at machine precision (Paper 1).

---

## What is now in honest open scope

Three problems QNG cannot currently address:

1. **Dark Energy / Λ_obs ≠ 0 phenomenology**
   - QNG-Yukawa cannot replace Λ (this audit)
   - Sakharov-induced Λ ≤ 10% of observed (theory-v2 file 18)
   - No quintessence-like substrate scalar derived
   - **Path forward**: derive substrate scalar dynamics in cosmological
     context, test against DESI 2024 evolving-DE hints (multi-month
     research program)

2. **Dark Matter** (DM Phase 1-4 exhausted)
   - All four candidate mechanisms falsified
   - Hopfion charged ±e under v12
   - **Path forward**: v13+ extension with new field

3. **Particle masses** (Gap 13)
   - Substrate-to-MeV scale separation 22 orders unexplained
   - Classical α-running L-independent (CPU-141)
   - **Path forward**: quantum one-loop calculation (5-8 weeks)

---

## What we learned (methodology)

- **Negative results matter**: structural falsification clarifies what
  QNG actually predicts vs claims.
- **Robustness verification was crucial**: showed failure isn't a
  parameter-tuning issue but a structural obstruction.
- **Independent tests confirm**: BAO + CMB peak position give the same
  diagnosis from completely independent observational windows.
- **Honest scope strengthens, not weakens**: a theory that knows what
  it doesn't solve is more credible than one that overclaims.

---

## Recommendation for next session

User said "easier first (cosmology), then Gap 13". Cosmology is now
done — negative result locked. **Next**: Gap 13 attack.

Gap 13 is HARD. Three honest options:

**Option A**: Quantum one-loop calculation (5-8 weeks of math + numerics)
**Option B**: Try a different Gap 13 mechanism (substrate topology,
new ontology layer)
**Option C**: Accept particle mass identification as input parameters
(like SM Yukawa couplings)

User decides on return.

---

## Verification checklist (per user request "verify multiple times")

- [x] BAO chi² computed via scipy.integrate.quad
- [x] BAO chi² re-computed via trapezoid integrator → identical
- [x] H(0) = H_0 verified for all models
- [x] D_M(z) monotonic verified
- [x] r_d sensitivity scan
- [x] Iteration convergence verified for self-consistent Yukawa
- [x] Independent test via CMB acoustic-peak position
- [x] Robustness across H_0, r_d, datasets, Yukawa forms, R/λ scan
- [x] Log-grid integration cross-check for D_C(z*)
- [x] Documentation reviewed and self-consistent

All verifications PASS. Result is robust.

---

**Status**: COSMO audit COMPLETE. Paper 4 retracted. DER-QNG-090 locked.
Ready for Gap 13 work on user return.
