# QNG-CPU-057

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Vortex ring physical mass — snapshot Hamiltonian H(k_back) on pre-formed v5 ring

## Purpose

CPU-056 showed that Channel G (sigma += k_back × chi) destroys the v5 ring
during Phase 2 at any k_back >= 0.02. The root cause: chi_core ~ 10–12 gives
T > 0 (positive mass), but the same chi through Channel G restores sigma
(destroys ring). Stability threshold k_back < 0.0015, but k_min for H > 0 ~ 0.02.

This test decouples the measurement from the dynamics:
1. Run the ring fully in v5 (no Channel G) until steady state
2. At each checkpoint, evaluate H(k_back) = k_back/2 × Σchi² + E_ring
   as a FUNCTIONAL EVALUATION on the v5 state — no v6 time evolution

This gives the physical mass the v5 ring WOULD HAVE if embedded in a v6 substrate.

## Physical picture

H(k_back) = T(k_back) + E_ring
           = k_back/2 × Σ chi_i²  +  (E[sigma,chi,phi] - E_vac)

Since E_ring is fixed (v5 state, no Channel G evolution):
  H > 0  when  k_back > k_min = 2|E_ring| / Σ chi_i²

From CPU-055 at T=400 (near peak M): E_ring ~ -569, chi_rms ~ 5.2, N=8000
  Σ chi_i² ~ 5.2² × 8000 = 216320
  k_min ~ 2 × 569 / 216320 ~ 0.0053

Expected: k_min ~ 0.005–0.01 (well within physical range).

## Inputs

- DER-QNG-032: H = T + E formula
- NOTE-QNG-016: C4 constraint (m_u ~ Planck mass)
- QNG-CPU-055: E_ring(t) and chi_rms(t) measurements (v5)
- QNG-CPU-056: Channel G incompatibility diagnosis

## Experimental design

**Parameters:** Identical to CPU-055 (L=20, R=5, v5, same as CPU-044):
- ALPHA=0.005, BETA=0.35, DELTA=0.20, CHI_DECAY=0.005, CHI_REL=0.35
- GAMMA_PHI=0.10, BETA_PHI=0.02, EPSILON=0.0
- Phase 1: 300 steps, Phase 2: 2500 steps (v5 only — no Channel G)

**Snapshot k_back values:** [0.0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00]

**Measurements every 200 Phase-2 steps:**
```
For each checkpoint t and each k_back:
  sum_chi2(t) = Σ_i chi_i²                       [chi squared sum]
  T(k_back, t) = k_back/2 × sum_chi2(t)          [kinetic energy]
  E_ring(t) = E[sigma,chi,phi] - E_vac            [potential energy, same for all k_back]
  H(k_back, t) = T(k_back, t) + E_ring(t)        [total Hamiltonian]
  M_ring(t) = Σ max(0, sigma_ref - sigma_i)       [sigma depletion integral]
  k_min(t) = 2*|E_ring(t)| / sum_chi2(t)         [threshold for H > 0]
```

## Checks

**Check 1 — Ring survives Phase 2:**
```
M_ring(T=1000) > 50
```

**Check 2 — H > 0 at k_back=0.05, T=1000:**
```
H(k_back=0.05, T=1000) > 0
```
Expected from CPU-055 data: k_min ~ 0.005–0.01, so k_back=0.05 should give H > 0.

**Check 3 — k_min is physically small (< 0.10):**
```
k_min(T=1000) < 0.10
```
If k_min > 0.10: chi field too small relative to potential energy depth;
ring is too strongly bound for k_back in the tested range to overcome.

**Check 4 — Physical mass estimate (informational):**
Report m_ring(k_back=1.0, T=1000) in kg and GeV via C3+C4 unit conversion.

## Decision rule

**Overall PASS** if Checks 1, 2, and 3 pass.
- PASS: positive physical mass confirmed; snapshot mass estimate valid
- FAIL Check 2: k_min > 0.05 (need larger k_back or different ring)
- FAIL Check 3: ring too tightly bound; H positive only at very large k_back

## Artifact paths

- `07_validation/audits/qng-ring-hamiltonian-snapshot-v1/report.json`
- `07_validation/audits/qng-ring-hamiltonian-snapshot-v1/summary.md`
