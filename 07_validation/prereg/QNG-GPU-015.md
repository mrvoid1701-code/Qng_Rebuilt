# QNG-GPU-015

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-18`
test_class: `mass_identification`
hardware: `GPU`

## Title

Hamiltonian energy L-convergence and ratio — replacing depletion integral as the mass observable

## Purpose

DER-QNG-038 (N/Δ identification at 0.24%) was downgraded to STRUCTURAL HINT by
GPU-009..014: the observable `M_ring = N·SIGMA_REF − sum(sigma_m)` diverges as
~L^1.6 and asymptotes to the geometric ratio 5/4 = 1.25 (ring perimeter), not
to SM 1.313. The 0.24% agreement at L=20 is a finite-size coincidence.

The particle-mass-identification document explicitly identifies the next step
(§1.1 caveat, 2026-04-15):

> "What would make this a real prediction: a definition of M_ring that is
>  proportional to baryon mass rather than ring perimeter. Candidate:
>  Hamiltonian energy H_v7 = T_g + E_v7 (energy, not depletion integral).
>  This has not been tested."

The vortex ring catalog Q1 (CRITICA) repeats this as the top-priority open
question.

GPU-015 is the decisive test: does the Hamiltonian energy functional evaluated
on the final ring state produce an L-convergent observable, and does its
R=5/R=4 ratio match SM?

## Hypothesis

If phi-gradient energy is confined by Channel H and the short-range
sigma-gradient + chi-coupling energy is inherently localized, then E_ring
(global) = sum of bounded energy densities → converges with L. Distinct
outcomes are possible:

- **H1 (PASS):** E_ring converges AND ratio matches SM to <5%. Mass identification
  is rescued via the energy observable. DER-QNG-038 can be rehabilitated.
- **H2 (PASS_WEAK):** E_ring converges but ratio differs from SM. A legitimate
  mass observable exists but its numerical value does not match N/Δ. The
  baryon ladder needs reinterpretation.
- **H3 (FAIL):** E_ring also diverges with L. Energy is not localized because
  phi halo contributes gradient energy that grows with L. Channel H insufficient.

## Upstream

- DER-QNG-038 §1.1 caveat (2026-04-15): "Hamiltonian energy not tested"
- NOTE-QNG-015 Q1: "Care este masa locala reala a inelului?"
- DER-QNG-036: v7 Hamiltonian H_v7 = T_g[chi] + E_v7[sm, chi, phi]
- DER-QNG-039: Channel H (v8 phi confinement)
- QNG-GPU-011 FAIL: even Channel H from Phase 1 does not make M_ring converge
- CPU-057 (qng_ring_hamiltonian_snapshot_reference.py): the CPU-level energy
  functional definition, to be ported to GPU and L-scan

## Protocol

Same simulation protocol as GPU-011 (v5 + Channel H active in BOTH Phase 1 and
Phase 2, k_gm = 0). The only addition is a post-simulation measurement of the
Hamiltonian energy functional on the final state.

### Parameters (identical to GPU-011)
```
ALPHA = 0.005, BETA = 0.35, DELTA_CHI = 0.20
CHI_DECAY = 0.020, CHI_REL = 0.35, GAMMA_PHI = 0.10
BETA_PHI_MIN = 0.0005, BETA_PHI_RING = 0.06
K_GM = 0.0
PHASE1 = 300, PHASE2 = 1500
```

### L-scan
```
L ∈ {20, 30, 40, 60, 80}
R ∈ {4, 5}
```

### Energy functional (matches CPU-057 with Channel H bp_eff)

For each site i:
```
e_A(i)       = (ALPHA / 2) · (sm_i − SIGMA_REF)²
e_B(i)       = (BETA / 4) · Σ_{j∈nb(i)} (sm_j − sm_i)²      [gradient, per-site]
e_chi_dec(i) = (CHI_DECAY / 2) · chi_i²
e_chi_rel(i) = (CHI_REL / 2)   · chi_i · (sm_nb_mean − sm_i)
e_delta(i)   = DELTA_CHI       · chi_i · (sm_i − SIGMA_REF)
e_phi(i)     = −(bp_eff_i / 6) · Σ_{j∈nb(i)} sm_i · sm_j · cos(phi_i − phi_j)
e_dis(i)     = (GAMMA_PHI / 2) · disorder_i · sm_i²
```

Total: `E_total = Σ_i (e_A + e_B + e_chi_dec + e_chi_rel + e_delta + e_phi + e_dis)(i)`

**Vacuum reference** (phi=0, sm=SIGMA_REF, chi=0):
```
E_vac = Σ_i e_phi_vac(i) = −(bp_eff_vac / 6) · 6 · SIGMA_REF²  per site
      = −bp_eff(SIGMA_REF) · SIGMA_REF² · N
      (all other terms vanish at vacuum)
```

**Ring energy (subtracted):**
```
E_ring = E_total(ring) − E_vac(same L)
```

This subtracts the trivial background so only the ring's excess energy remains.
Like M_ring, E_ring is additive in the box. Windowed version below.

### Windowed energy

Concentric sphere window around box center (where ring sits): r ≤ R + 5.
```
E_inner = Σ_{i: |r_i − center| ≤ R+5} e_total(i)
N_inner = number of sites in that sphere
E_bg_den = (E_total − E_inner) / (N − N_inner)   [outer-shell energy density]
E_ring_windowed = E_inner − E_bg_den × N_inner
```

## Outputs

Per (L, R):
- `E_total`, `E_vac`, `E_ring_global`
- `E_ring_windowed`
- Per-component breakdowns: `E_A_ring`, `E_B_ring`, `E_phi_ring`, `E_dis_ring`, …
  (each = component sum on ring state − same on vacuum)
- For cross-check: `M_ring_global` (the old observable)

## Gates

**Gate 1 — L-convergence of E_ring (global, subtracted):**
```
last-3-L spread of E_ring_global(R=5) / E_ring_global(R=4)   <   0.03
```
*(tighter than GPU-011's 0.02 gate on M_ring which it failed with 0.098)*

**Gate 2 — L-convergence of windowed energy:**
```
last-3-L spread of E_ring_windowed(R=5) / E_ring_windowed(R=4)  <  0.03
```

**Gate 3 — SM ratio match (both global and windowed):**
```
|E_ring(R=5) / E_ring(R=4)  −  1.3130| / 1.3130  <  0.05   at L=80
```
Both global and windowed required to match within 5%.

**Gate 4 — Component identification:**
```
Report which individual component (E_A, E_B, E_phi, E_disorder) passes L-convergence.
If any single component is L-convergent and matches SM, that component is the
legitimate mass carrier. This is informational, not a pass/fail gate.
```

## Decision rule

- **PASS:** Gate 1 AND Gate 2 AND Gate 3. Interpretation: Hamiltonian energy
  (global or windowed) is a legitimate L-convergent mass observable matching SM.
  DER-QNG-038 is rehabilitated.
- **PASS_WEAK:** Gate 1 AND Gate 2, but Gate 3 fails. Energy is L-safe but
  numerical ratio differs from SM. New mass observable exists but baryon ladder
  is wrong. Document implications; do not claim SM identification.
- **FAIL:** Gate 1 OR Gate 2 fails. Energy also diverges; Channel H confinement
  insufficient for energy localization. Report which component dominates
  divergence (via Gate 4). Mass identification remains structural hint only.

## Artifact paths

- `tests/gpu/qng_hamiltonian_l_convergence_gpu.py`
- `07_validation/audits/qng-hamiltonian-l-convergence-v1/report.json`
- `07_validation/audits/qng-hamiltonian-l-convergence-v1/summary.md`

## Pre-registration commitment

The four gates, their numerical thresholds, and the decision rule are fixed
before execution. Gate 4 is informational-only to remain scientifically useful
regardless of pass/fail of Gates 1–3. No post-hoc gate adjustment is permitted.
