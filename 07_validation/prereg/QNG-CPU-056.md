# QNG-CPU-056

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Vortex ring physical mass from Hamiltonian H = T + E in v6 substrate

## Purpose

CPU-055 showed that E_ring (free energy, v5) is NEGATIVE relative to the phi=0
vacuum. In v5, T=0 so H=E<0 → negative "mass" — unphysical.

DER-QNG-032 shows that the correct physical energy is the HAMILTONIAN H = T + E
where T = k_back/2 × Σ chi_i² is the kinetic energy of the chi field.

The chi field in the ring is large (chi_core ≈ 10-12 per node, driven by DELTA
coupling σ→χ). For k_back > k_min ≈ 0.05, T_ring > |E_ring - E_vac|, giving:

  ΔH = H[ring] - H[vacuum] > 0   (positive physical mass)

This is the matter source identification mass:
  m_ring = ΔH × (m_u / (ℏ/τ))   [in physical units via C3+C4]

## Physical picture

In v5: ring is a purely dissipative bound state (E < 0, no kinetic energy).
In v6: Channel G (sigma += k_back × chi) gives chi an inertial role. The chi
field carries kinetic energy T. The ring's chi content makes it massive.

Analogy: in QED, the electron mass comes from the interaction energy of the
Dirac field, not from the "potential well" alone. Here, chi is the momentum
field and T is the rest-mass energy.

## Inputs

- DER-QNG-032 (qng-hamiltonian-conservative-limit-v1.md): H = T + E formula
- NOTE-QNG-016 (qng-c4-quantum-action-candidate-v1.md): C4 constraint
- QNG-CPU-055: E_ring = -569 at T=400, chi_core ≈ 11.6, ring_nodes=868
- QNG-CPU-043/044: ring stable for 2400 Phase-2 steps with v5

## Experimental design

**Parameters:** Same as CPU-055 (v5 ring params) PLUS k_back scan.
Ring initialized identically (Phase 1 = 300 steps, Phase 2 = 1500 steps).

k_back values: [0.0, 0.02, 0.05, 0.10, 0.20]

Note: k_back > 0 activates Channel G in sigma update:
  sigma_i += k_back × chi_i   (in addition to Channels A,B,D,F)
For small k_back (< 0.10), ring structure should remain stable.

**Measurements every 300 Phase-2 steps:**
```
T_ring(t) = k_back/2 × Σ_i chi_i²               [kinetic energy, all nodes]
E_ring(t) = E[sigma,chi,phi] - E_vacuum           [potential energy above phi=0 vacuum]
H_ring(t) = T_ring(t) + E_ring(t)                [total Hamiltonian energy]
chi_rms(t) = sqrt(Σ chi_i² / N)                  [RMS chi field amplitude]
```

Also ring survival check (M_ring > 50) at each checkpoint.

## Checks

**Check 1 — Ring survives at k_back=0 (v5 baseline):**
```
M_ring(T=1000, k_back=0) > 50
```

**Check 2 — H_ring crosses zero (mass becomes positive) at k_min:**
```
H_ring(T=600, k_back=0.05) > H_ring(T=600, k_back=0.0)
```
Equivalently: there exists k_back in [0, 0.20] where H_ring > 0.

**Check 3 — Ring survives at k_back=0.10 (v6 ring stability):**
```
M_ring(T=1000, k_back=0.10) > 50
```
If Channel G is too strong, the ring collapses. This check confirms v6 ring is stable.

**Check 4 — H_ring scales with k_back (informational):**
Report H_ring vs k_back at T=600. If monotone increasing: kinetic energy dominates.

## Decision rule

**Overall PASS** if Checks 1, 2, and 3 pass.
- PASS: ring has positive physical mass for k_back >= k_min; mass identification possible
- FAIL Check 2: chi content insufficient for positive mass; need larger k_back or different ring
- FAIL Check 3: Channel G destabilizes ring; need k_back < 0.05 range

## Artifact paths

- `07_validation/audits/qng-ring-hamiltonian-v1/report.json`
- `07_validation/audits/qng-ring-hamiltonian-v1/summary.md`
