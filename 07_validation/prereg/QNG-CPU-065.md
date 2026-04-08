# QNG-CPU-065

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `two_field_substrate`

## Title

Two-field v7 with DELTA_m coupling — kinetic mass recovery scan

## Purpose

CPU-063 showed that v7 (chi coupled to sigma_g only) gives E~R^1 spectrum (string tension).
The v5 spectrum was H~R^2 (kinetic: chi_rms ~ R). The difference: in v5, chi built up at
the ring (DELTA*(sigma_ref - sigma) with sigma depleted at ring). In v7, chi couples to
sigma_g (which is nearly flat near ring) → no chi buildup → no kinetic mass.

Fix: add DELTA_m coupling to chi update:
  chi_i += DELTA_m * (sigma_m_ref - sigma_m_i)

This gives chi a response to sigma_m depletion at the ring core, recovering kinetic mass
while preserving:
- Channel G in sigma_g only (Gap 7 remains resolved)
- sigma_m decoupled from Channel G (ring stability preserved)
- Stability fix: CHI_DECAY=0.020 (Gap 8 resolved by DER-QNG-034)

## Upstream derivations

- DER-QNG-033: v7 two-field substrate
- DER-QNG-034: Gap 8 stability analysis (stability criterion unchanged by DELTA_m)
- DER-QNG-035: double-Yukawa Green's function
- QNG-CPU-063: v7 spectrum at DELTA_m=0 (string tension baseline)
- QNG-CPU-064: Gap 8 resolved at CHI_DECAY=0.020

## Stability note (DER-QNG-034 §Fix D)

The stability criterion K_BACK*DELTA < ALPHA + CHI_DECAY*(1-ALPHA) involves only the
sigma_g ↔ chi feedback loop. DELTA_m drives chi from sigma_m (fixed source, not feedback),
so it does NOT change the stability criterion. The system remains stable at CHI_DECAY=0.020.

However, DELTA_m creates large chi at the ring core:
  chi_ss ~ DELTA_m * m_dep / CHI_DECAY (quasi-static estimate)
For DELTA_m=0.20, m_dep~0.3: chi_ss ~ 0.20*0.3/0.020 = 3.0

This large chi feeds into Channel G (sigma_g += K_BACK*chi) producing gravitational signal.
The total H = E_ring + K_BACK/2 * sum_chi² should grow significantly.

## Experimental design

Parameters (v7 baseline from CPU-064):
- L=20, R=5.0, Phase1=300, Phase2=1500, snap at T=1000
- ALPHA=0.005, BETA=0.35, BETA_PHI=0.02
- DELTA=0.20, CHI_DECAY=0.020, CHI_REL=0.35
- GAMMA_PHI=0.10, K_BACK=0.10, K_GM=0.001

DELTA_m scan: [0.0, 0.02, 0.05, 0.10, 0.20]
  (0.0 = baseline v7, 0.20 = full symmetry chi couples equally to both sigma fields)

Per DELTA_m value, run R=2,3,4,5 rings (for spectrum) and report:
- E_ring = compute_E - E_vac (potential energy)
- T_ring = K_BACK/2 * sum_chi² (kinetic energy from chi)
- H_ring = E_ring + T_ring (Hamiltonian)
- chi_rms at ring core
- H(R)/H(R=5) ratio for spectrum
- Best-match hadron ratio

## Checks

**Check 1 — All rings survive:**
M_ring(T=1000) > 10 for all R in [2,3,4,5] and all DELTA_m in scan.
Gate: M > 10.

**Check 2 — Kinetic mass grows with DELTA_m:**
T_ring(DELTA_m=0.20) / T_ring(DELTA_m=0.0) > 100 for R=5.
(T_ring ≈ 0 at DELTA_m=0; should be large at DELTA_m=0.20)
Gate: ratio > 100.

**Check 3 — chi stable at T=1000:**
chi_rms(T=1000) < 1.0 for all DELTA_m in scan, all R.
(chi_ss ~ DELTA_m*0.3/0.020 = 3*DELTA_m; for DELTA_m=0.20 expect chi~0.6)
Gate: chi_rms < 1.0.

**Check 4 — Spectrum R^n scaling:**
For DELTA_m=0.20: log(H(R=5)/H(R=2)) / log(5/2) gives power n.
Report n and compare to n=1 (string tension) and n=2 (kinetic).
Gate: informational only.

## Decision rule

PASS if Checks 1, 2, 3 all pass.

## Artifact paths

- `07_validation/audits/qng-two-field-delta-m-v1/report.json`
- `07_validation/audits/qng-two-field-delta-m-v1/summary.md`
