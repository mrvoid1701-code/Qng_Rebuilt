# QNG-CPU-055

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Vortex ring energy vs sigma integral — E_ring vs M_ring decay comparison

## Purpose

All ring simulations to date (CPU-041 to CPU-051) measured M_ring = Σ(sigma_ref - sigma_i)
(sigma depletion integral). This is a **charge-like quantity** — how much sigma is missing.

DER-QNG-032 (NOTE-QNG-016 companion) defines the substrate free energy:
```
E[sigma, chi, phi] = Σ_i {
  alpha/2 * (sigma_i - sigma_ref)²
  + beta/4 * Σ_{j~i} (sigma_j - sigma_i)²
  + chi_decay/2 * chi_i²
  + chi_rel/2 * chi_i * (sigma_bar_i - sigma_i)
  + delta * chi_i * (sigma_i - sigma_ref)
  - beta_phi/6 * Σ_{j~i} sigma_i*sigma_j*cos(phi_i - phi_j)
  + gamma_phi/2 * D_i(phi) * sigma_i²
}
```

E_ring is the **energy-like quantity** — the free energy stored in the ring state above vacuum.
For the matter source identification program, the physical mass of the ring depends on
WHICH quantity maps to mass, and how they relate.

**Key question:** Do E_ring and M_ring decay at the same rate, or differently?
- Same rate → mass ∝ charge (simple linear identification)
- Different rates → E and M are independent; need to identify which is "mass"
- Ratio E/M is a dimensionless substrate property of the ring

## Inputs

- [qng-hamiltonian-conservative-limit-v1.md](../../04_qng_pure/qng-hamiltonian-conservative-limit-v1.md) — DER-QNG-032: E functional
- [qng-c4-quantum-action-candidate-v1.md](../../04_qng_pure/qng-c4-quantum-action-candidate-v1.md) — NOTE-QNG-016: C4 constraint
- [qng-matter-source-identification-v1.md](../../04_qng_pure/qng-matter-source-identification-v1.md) — DER-QNG-013
- QNG-CPU-044 (ring lifetime, M_ring decay confirmed)
- QNG-CPU-051 (M_ring = 158.4 at T=1000)

## Experimental design

**Parameters:** Identical to CPU-044 (L=20, R=5, BETA_PHI=0.02, two-phase protocol):
- ALPHA=0.005, BETA=0.35, DELTA=0.20, CHI_DECAY=0.005, CHI_REL=0.35
- GAMMA_PHI=0.10, BETA_PHI=0.02, EPSILON=0.0
- Phase 1: 300 steps (form ring), Phase 2: 2500 steps

**Measurements every 200 Phase-2 steps:**
```
M_ring(t) = Σ_i max(0, sigma_ref - sigma_i)   [sigma depletion integral]
E_ring(t) = E[sigma(t), chi(t), phi(t)] - E_vacuum   [free energy above vacuum]
E_vacuum  = E evaluated at sigma=sigma_ref, chi=0, phi=0 everywhere
ratio(t)  = E_ring(t) / M_ring(t)   [energy per unit depletion]
```

Also compute the **ring-localized** versions (only nodes within 3 lattice units of the ring tube):
```
M_ring_local(t) = Σ_{ring nodes} max(0, sigma_ref - sigma_i)
E_ring_local(t) = E[sigma, chi, phi] summed over ring nodes only
```

## Checks

**Check 1 — Ring survives Phase 2 (structural):**
```
M_ring(T=1000) > 50   [ring still present at T=1000]
```

**Check 2 — Both E and M are measurable:**
```
E_ring(T=200) > 0  AND  M_ring(T=200) > 0
```

**Check 3 — Decay rate comparison (key finding):**
Fit M_ring(t) = M_0 * exp(-t/τ_M) and E_ring(t) = E_0 * exp(-t/τ_E).
Report τ_M and τ_E. If |τ_E/τ_M - 1| < 0.10: same decay (mass ∝ charge).
If |τ_E/τ_M - 1| > 0.50: independent quantities.
This check is **informational** (no PASS/FAIL gate) — any result is a finding.

**Check 4 — E/M ratio stability:**
Report stddev(ratio) / mean(ratio) over all checkpoints.
If < 0.20: ratio is stable (E ∝ M throughout decay).
If > 0.20: ratio evolves (E and M decouple during decay).

## Decision rule

**Overall PASS** if Checks 1 and 2 pass (ring exists, quantities measurable).
Checks 3 and 4 are findings regardless of value — all outcomes are informative.

## Artifact paths

- `07_validation/audits/qng-ring-energy-v1/report.json`
- `07_validation/audits/qng-ring-energy-v1/summary.md`
