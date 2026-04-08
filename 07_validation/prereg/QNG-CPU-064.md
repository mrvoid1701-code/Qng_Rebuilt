# QNG-CPU-064

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-08`
test_class: `two_field_substrate`

## Title

Two-field v7 k_gm scan (corrected sign + Gap 8 fix) — Yukawa profile verification

## Purpose

Re-run k_gm scan with two corrections from mathematical analysis (2026-04-08):
1. K_GM sign fix: sigma_g -= k_gm*(sigma_m_ref - sigma_m) [was +=, gave repulsive potential]
2. CHI_DECAY = 0.020 (Fix B from DER-QNG-034): stabilizes k=0 Jeans mode
   Stability criterion: K_BACK*DELTA = 0.020 < ALPHA + CHI_DECAY*(1-ALPHA) = 0.025 ✓

Goals:
1. Verify dsg at ring is now POSITIVE (attractive gravitational potential)
2. Verify spatial decay of sigma_g profile (genuine Yukawa, not global collapse)
3. Measure effective screening length lambda_g from radial profile
4. Verify ring stability is maintained (sigma_m unaffected by sigma_g sector)

## Upstream derivations

- DER-QNG-033: v7 two-field substrate (K_GM sign corrected 2026-04-08)
- DER-QNG-034: Gap 8 stability analysis — Fix B (CHI_DECAY=0.020)
- DER-QNG-035: double-Yukawa Green's function — lambda_g = sqrt(BETA/(z*ALPHA)) expected

## Experimental design

Parameters:
- L=20, R=5.0 (ring radius)
- ALPHA=0.005, BETA=0.35, BETA_PHI=0.02
- DELTA=0.20, CHI_DECAY=0.020 [changed from 0.005 — Gap 8 fix]
- CHI_REL=0.35, K_BACK=0.10, GAMMA_PHI=0.10
- K_GM scan: [0.0, 0.001, 0.005, 0.01, 0.05, 0.10]
- Phase1=300 steps (no Channel F, no Channel G), Phase2=1500 steps (all channels)
- Snapshot at T=1000 and T=1500

Per k_gm value, record:
- M_ring (ring mass via sigma_m depletion)
- dsg_ring = mean(SIGMA_REF - sigma_g) at ring nodes (should be positive after sign fix)
- Radial sigma_g profile: dsg(r) for r = 1..10 from center
- chi_rms across lattice

## Checks

**Check 1 — Ring survives (sigma_m unaffected):**
M_ring(T=1000) > 50 for all k_gm in scan.
Gate: M > 50.

**Check 2 — Attractive potential (sign fix verified):**
dsg_ring(T=1000) > 0 for all k_gm > 0.
Gate: dsg_ring > 0 for k_gm in [0.001, 0.005, 0.01, 0.05, 0.10].

**Check 3 — Yukawa spatial decay:**
At k_gm = 0.01, the radial profile dsg(r) must be strictly decreasing:
dsg(r=6) > dsg(r=8) > dsg(r=10).
Gate: dsg(r=6) > dsg(r=10) by at least 10%.

**Check 4 — Gap 8 stability (chi not runaway):**
chi_rms(T=1500) < 0.05 for k_gm <= 0.01.
Gate: chi_rms < 0.05.

**Check 5 — Screening length estimate:**
Fit lambda_g from radial profile at k_gm=0.01.
Expected: lambda_g ≈ sqrt(BETA/(z*ALPHA)) = sqrt(0.35/0.03) = 3.4 lattice units.
Gate: 2.0 < lambda_g_fit < 8.0 (broad tolerance, first measurement).

## Decision rule

PASS if Checks 1, 2, 3, 4 all pass. Check 5 is informational.

## Artifact paths

- `07_validation/audits/qng-two-field-kgm-scan-v2/report.json`
- `07_validation/audits/qng-two-field-kgm-scan-v2/summary.md`
