# QNG-CPU-060

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Two-field substrate (v7): stable ring in sigma_m + Channel G active in sigma_g

## Purpose

Gap 7 (NOTE-QNG-017): single-sigma substrate cannot simultaneously support
KG waves (Channel G) and stable rings (Channel F incompatible with Channel G).

DER-QNG-033 proposes Path D: two sigma fields.
  sigma_g — gravitational sector, supports Channel G (KG wave)
  sigma_m — matter sector, supports Channel F (ring stability)
  Coupling: sigma_g += k_gm × (sigma_m_ref - sigma_m)

If Path D works: a vortex ring survives in sigma_m even when Channel G is active
in sigma_g. This resolves Gap 7 and is the first QNG substrate supporting both
stable matter AND propagating waves simultaneously.

## Inputs

- DER-QNG-033: two-field substrate v7 definition
- NOTE-QNG-017: Gap 7 — resolution paths
- CPU-044: v5 ring stable (baseline, single sigma_m analog)
- CPU-056: Channel G kills single-sigma ring (motivates two-field)

## Experimental design

**Parameters (same as CPU-044 for matter sector, new k_gm for coupling):**
- ALPHA=0.005, BETA=0.35, DELTA=0.20, CHI_DECAY=0.005, CHI_REL=0.35
- GAMMA_PHI=0.10, BETA_PHI=0.02
- K_BACK=0.10 (active in sigma_g only)
- K_GM=0.001 (matter-gravity coupling, weak)
- L=20, R=5, Phase1=300, Phase2=1500

**Fields per node:** (sigma_g, sigma_m, chi, phi)
- sigma_g initialized flat at sigma_g_ref=0.5
- sigma_m initialized with phi ring structure (same as CPU-044)
- chi initialized to 0
- phi initialized with ring winding

**Measurements every 200 Phase-2 steps:**
```
M_ring(t)      = Σ max(0, sigma_m_ref - sigma_m_i)   [ring depletion in sigma_m]
delta_sg_core  = mean(sigma_g_ref - sigma_g_i) over ring_nodes  [gravity signal at ring]
chi_rms(t)     = sqrt(Σchi²/N)                        [wave field amplitude]
H_snapshot(t)  = k_back/2 × Σchi² + E_total - E_vac  [Hamiltonian energy]
```

## Checks

**Check 1 — Ring survives in sigma_m with Channel G active in sigma_g:**
```
M_ring(T=1000) > 50
```
This is the PRIMARY test of Path D. In CPU-056, M_ring(T=1000) = 0 for k_back=0.10.
If Check 1 passes: Path D resolves Gap 7.

**Check 2 — Gravity signal: ring sources sigma_g perturbation:**
```
delta_sg_core(T=1000) > 0.001   [ring creates measurable sigma_g depletion]
```

**Check 3 — chi field active (wave sector running):**
```
chi_rms(T=1000) > 0.01   [chi field non-trivial, wave dynamics present]
```

## Decision rule

**Overall PASS** if Checks 1 and 3 pass.
- PASS: Path D works — two-field substrate supports both stable rings and waves
- FAIL Check 1: ring still killed by some indirect coupling; need k_gm=0 test
- FAIL Check 3: chi field dies off; wave sector not active with two-field

## Artifact paths

- `07_validation/audits/qng-two-field-ring-v1/report.json`
- `07_validation/audits/qng-two-field-ring-v1/summary.md`
