# QNG Alpha Papers Series

Date: 2026-04-25
Author: C.D Gabriel
Status: ALPHA DRAFTS — internal release for skill-driven editing/refinement

---

## Series structure

Four complementary papers covering the SOLID portions of the QNG
framework after the Gap 13 + Gap 14 audit (which retracted the
DER-QNG-038 baryon-ladder claim).

### Paper 1: `paper1_hbar_emergent_alpha.md`
**Title**: Emergent Planck Constant from Discrete Graph Substrate Under a Stability Principle
**Target**: Physical Review Letters (primary), Foundations of Physics (extended)
**~10 pages** | **Focused contribution** | **Most defensible single result**

Derives `ℏ_QNG = √(β_φ μ_φ z) / C_cubic ≈ 0.233` from substrate
parameters + Stability Principle. Numerical, falsifiable, and
independent of particle-physics claims.

---

### Paper 2: `paper2_lambda_zero_stability_alpha.md`
**Title**: A Stability Principle Resolves the Cosmological Constant Problem: Λ = 0 as a Structural Necessity
**Target**: Foundations of Physics, Phys Rev D
**~12 pages** | **Foundational contribution**

Formal axiomatization of the Stability Principle. Explicit comparison
with anthropic / multiverse approaches. Predicts `Λ = 0` exactly
(structural). Companion to Paper 1.

---

### Paper 4: `paper4_yukawa_cosmological_alpha.md`
**Title**: Modified Gravity at Cosmological Scales from a Yukawa Kernel: A Falsifiable Prediction of the QNG Substrate
**Target**: Phys Rev D, JCAP
**~12 pages** | **Predictive contribution** | **Genuine new physics**

Predicts Yukawa-screened gravity at scales `r ≳ R_Hubble`. Provides
testable signatures: `w(z=0.5) ≈ -0.95 ± 0.02`, suppressed LSS at
`k < 0.01 h/Mpc`, enhanced late-ISW. **THE main QNG-unique
prediction** distinguishable from ΛCDM.

---

### Paper 3: `paper3_qng_framework_alpha.md`
**Title**: QNG: A Discrete Graph Substrate as an Effective Framework for c, G, ℏ and Linearized Gravity
**Target**: Foundations of Physics, Annals of Physics
**~30+ pages** | **Comprehensive review/framework**

Consolidates substrate definition, derived constants, Stability
Principle, static-source GR correspondence, v11 spin-2 graviton
extension, and **explicit catalog of open programs and retractions**
(including Gap 13, 14 → DER-QNG-038 retraction).

Honest scope: QNG as **EFT framework**, NOT complete QG. Particle
physics retracted. Non-linear gravity open. UV physics open.

---

## Reading order

For peer review:
1. **Paper 3** (comprehensive) — provides full context.
2. **Paper 1** (ℏ) — most concrete derivation.
3. **Paper 2** (Stability Principle / Λ=0) — foundational rationale.
4. **Paper 4** (Yukawa cosmological) — falsifiable new prediction.

For impact/announcement:
1. **Paper 1** alone is the strongest standalone result.
2. **Paper 4** is the most novel testable prediction.
3. **Paper 2** is the most foundational claim.

---

## Submission strategy

- **Tier A (highest impact)**: Paper 1 to Phys Rev Lett.
- **Tier B (foundational)**: Paper 2 to Foundations of Physics.
- **Tier C (predictive)**: Paper 4 to Phys Rev D / JCAP.
- **Tier D (review)**: Paper 3 to Annals of Physics or Foundations
  extended issue.

These are independent enough to submit in parallel; cross-referenced
as companion papers.

---

## What is NOT in these papers

The papers explicitly DO NOT claim:

- ❌ DER-QNG-038 baryon ladder identification (retracted via Gap 13/14)
- ❌ QNG predicts hadron masses (M_ring is L-dependent finite-size artifact)
- ❌ Full quantum gravity theory (QNG is EFT)
- ❌ Non-linear GR derivation (open program)
- ❌ Particle-physics correspondence (open, no current path)
- ❌ Dark matter explanation
- ❌ UV completion below Planck scale

These are honest exclusions, documented in Paper 3 §6.

---

## Repository pointers

Supporting code and derivations:
- `04_qng_pure/qng-hbar-derivation-paper-draft-v1.md` (DER-QNG-067, expanded ℏ)
- `04_qng_pure/qng-stability-principle-v1.md` (DER-QNG-066)
- `04_qng_pure/qng-v10-foundational-v1.md` (DER-QNG-062)
- `04_qng_pure/qng-v11-tensor-extension-v1.md` (DER-QNG-072)
- `04_qng_pure/qng-gap12-no-go-proof-v1.md` (DER-QNG-071)
- `04_qng_pure/qng-gap12-correction-v1.md` (NOTE-QNG-028, savant retraction)
- `04_qng_pure/qng-gap13-scale-tension-v1.md` (DER-QNG-074)
- `04_qng_pure/qng-gap14-mring-lattice-dependence-v1.md` (DER-QNG-075)
- `tests/cpu/qng_cpu107_hbar_unique_check.py` — primary ℏ derivation
- `tests/cpu/qng_cpu108_hbar_L_scan.py` — L→∞ convergence
- `tests/cpu/qng_cpu113_robustness_scan.py` — β/μ scans
- `tests/cpu/qng_cpu114_SI_robust.py` — SI bridge
- `tests/cpu/qng_cpu120_hawking_flrw.py` — Hawking + cosmology consistency
- `tests/cpu/qng_cpu124_scale_tension_audit.py` — Gap 13 audit
- `tests/cpu/qng_cpu126_mring_ratios_L_dependence.py` — Gap 14 audit
