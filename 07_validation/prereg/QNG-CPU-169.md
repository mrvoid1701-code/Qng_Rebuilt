---
test_id: QNG-CPU-169
title: Stress test — Phase 3 robustness of all 8 identifications
category: structural / phenomenological / robustness
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-091, 093, 094 (all baryon + a0 identifications)
  - CPU-159, 164, 165, 167, 168 (mass measurements)
---

# QNG-CPU-169 — STRESS TEST of all identifications

## Purpose

Test if QNG-SM identifications are ROBUST under longer Phase 3
evolution (6000 lu vs original 3000 lu). If masses shift significantly,
the original 3000-lu values may be NON-EQUILIBRIUM snapshots and
the identifications need reinterpretation.

## Inputs

L=20, v12 enhanced (e=3.0, mu_A=1.0, BETA_A=0.05).
**Phase 3 extended to 6000 lu** (2× original 3000 lu).

8 configurations:
1. trefoil (proton)
2. anti-trefoil (anti-proton)
3. Hopfion Q1 (Δ+)
4. anti-Hopfion Q1 (Δ-)
5. W+W+ composite (Δ++)
6. W-W- composite (Δ--)
7. W+W- composite at D=10 (neutron)
8. WpWmWp layered composite (a0(980)+)

## Gates

**G_robust**: |M(t=6000) − M(t=3000)| / M(t=3000) < 2% for at least
6 of 8 configurations.

If G_robust fails: identifications are non-equilibrium artefacts.

## Result (2026-05-30)

| QNG configuration | M(3000) | M(6000) | Shift | SM err (stressed) |
|---|---|---|---|---|
| trefoil_proton | 1902.16 | 1444.31 | **−24.07%** | 0.00% (ref) |
| anti_trefoil_pbar | 1902.16 | 1444.31 | **−24.07%** | 0.00% (chirality) |
| Hopfion_Q1_Delta+ | 2456.50 | 1150.07 | −53.18% | **−39.36%** |
| anti_Hopfion_Q1_Delta- | 2456.50 | 1150.07 | −53.18% | −39.36% |
| W+W+_Delta++ | 2515.27 | 1454.40 | −42.18% | −23.31% |
| W-W-_Delta-- | 2505.33 | 2108.05 | −15.86% | +11.16% |
| W+W-_D10_neutron | 1900.73 | 314.95 | **−83.43%** | **−78.22%** |
| WpWmWp_layered_a0 | 1991.46 | 1308.36 | −34.30% | −13.27% |

**Robustness verdict**:
- STABLE (shift < 2%): **0 of 8** (NONE)
- SLIGHT shift (2-5%): 0 of 8
- SIGNIFICANT shift (> 5%): **8 of 8**

**Decision: FAIL — G_robust FAILS UNIVERSALLY**.

## Critical interpretation

The original 3000-lu Phase 3 values used for ALL CPU-159/164/165/167/168
identifications were **NOT equilibrium masses**. They were snapshots of
ongoing relaxation/oscillation dynamics.

Under extended evolution to 6000 lu:
- All configurations exhibit further mass changes (≥10%)
- Some show dramatic shifts (Hopfion family −53%, W+W- −83%)
- W-W- has the smallest absolute shift (−16%), explaining why it was
  the "best" identification at 3000 lu (0.30%) — it was closest to
  equilibrium by accident

**Identifications that SURVIVE stress test**:
1. **proton ↔ trefoil**: 0% by reference construction (always)
2. **anti-proton ↔ anti-trefoil**: 0% by chirality symmetry (always)

Both are RATIO-INVARIANT — they hold regardless of whether masses are
at equilibrium because the comparison is to the same reference.

**Identifications that DO NOT SURVIVE stress test (6 of 8)**:
- All Δ family (Δ+, Δ−, Δ++, Δ−−): shifts 11-39%, no longer clean
- neutron (W+W- D=10): catastrophic 78% error
- a0(980): 13% error, no longer the clean 0.24%

## Diagnosis

The QNG v12 enhanced dynamics has long oscillations and slow
equilibration. At 3000 lu, masses are at one phase of oscillation;
at 6000 lu, they're at another. True equilibrium may require:
- 30000+ lu Phase 3 (10× longer)
- More careful averaging over multiple oscillation periods
- Different protocol (e.g., conservative Phase 3 instead of dissipative)

Until true equilibrium values are established, all mass-ratio
identifications beyond the chirality-protected (proton, anti-proton)
are TENTATIVE.

## Implications for DER-QNG-093/094 and Paper 7

**DER-QNG-093**: 5 of 6 identifications need re-examination. Only
proton-trefoil holds.
**DER-QNG-094**: All 4 Δ identifications need confirmation with longer
Phase 3.
**Paper 7 §4.2'' through §4.2''''**: claims of "5 baryons identified",
"6 baryons identified" need to be downgraded to "2 robust + 6 tentative
pending equilibration".

## Honest verdict

The QNG-SM baryon identification framework, as applied with 3000-lu
Phase 3, produced an over-confident result. **The true number of QNG
identifications with current method = 2 (proton, anti-proton)**.

The remaining 6 candidates require:
- Either longer Phase 3 (10000+ lu) to confirm masses
- Or different dynamics (conservative, symplectic) to find true equilibrium
- Or acceptance that finite-precision identifications need wider error
  bars

This is a CRITICAL finding that improves the framework's honesty.

## Artifacts

- Report: `07_validation/audits/qng-particle-stress-test-v1/report.json`
- Test runner: `tests/cpu/qng_particle_stress_test_reference.py`

## Follow-up urgent

- **CPU-170**: ultra-long Phase 3 (20000+ lu) on key identifications
  (trefoil, Hopfion Q1, W+W+) to find true asymptotic mass
- **CPU-171**: conservative Phase 3 (no Channel F, no chi_decay) to
  test if equilibrium without dissipation is reached
- **Updated DER-QNG-094**: reflect tentative status of all baryon
  identifications pending equilibrium confirmation
