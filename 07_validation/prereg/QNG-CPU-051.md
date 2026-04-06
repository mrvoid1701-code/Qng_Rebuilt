# QNG-CPU-051

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Ring sigma-depletion integral — numerical measurement of M_ring for rho_0 constraint

## Purpose

DER-QNG-029 shows that rho_0 = m_particle / (a_M × M_ring_integral) where
M_ring_integral = ∫Δσ dV is the total sigma deficit integrated over the ring.

This quantity determines how much "mass" a single vortex ring represents in
substrate units. It is the geometric factor in the rho_0 constraint and must
be measured numerically, not estimated analytically.

Additionally: we test whether M_ring_integral is stable over time (T=500..2000
Phase-2 steps) and whether it scales predictably with ring radius R.

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-rho0-physical-scale-v1.md](../../04_qng_pure/qng-rho0-physical-scale-v1.md) — DER-QNG-029
- [qng_vortex_ring_3d_reference.py](../../tests/cpu/qng_vortex_ring_3d_reference.py) — QNG-CPU-043

## Experimental design

**Lattice:** L=24

**Ring radii tested:** R=2, R=4 (same as CPU-043), R=6

**Protocol per ring:**
1. Phase 1: 300 steps (phi equilibration, Channel F off)
2. Phase 2: 2000 steps (Channel F on)
3. Measure at T=500, 1000, 1500, 2000: sigma profile, M_ring_integral, ring radius

**M_ring_integral definition:**
```
M_ring = sum over all nodes i of max(0, sigma_ref - sigma_i)
```
This is the total sigma deficit — the "missing" coherence relative to vacuum.

**Shell-only variant:**
```
M_ring_shell = sum over nodes i with |rho_i - R| < 4 of max(0, sigma_ref - sigma_i)
```
Restricted to the torus shell around ring radius, excluding background fluctuations.

**Rho_0 constraint evaluation:**
For each particle mass hypothesis, compute:
```
rho_0 = m_particle / (a_M × M_ring_integral)
f = rho_0 × A_VORTEX   where A_VORTEX = 0.225 (from CPU-043)
```
Hypotheses:
- m_proton   = 1.673×10⁻²⁷ kg
- m_electron = 9.109×10⁻³¹ kg
- m_Planck   = 2.176×10⁻⁸  kg
- a_M = 1.0 (normalized, since a_M is unknown)

The goal is to report M_ring_integral numerically so that future derivations
can substitute any (m_particle, a_M) pair.

## Checks

**Check 1 — M_ring_integral stable over Phase 2:**
```
std(M_ring at T=500,1000,1500,2000) / mean < 0.10
```

**Check 2 — M_ring_integral positive and well-defined:**
```
M_ring > 0 for all R tested
```

**Check 3 — M_ring scales with ring geometry:**
```
M_ring(R=4) / M_ring(R=2) > 1.5  (larger ring = more depleted volume)
```

**Check 4 — Constraint table reproduced:**
```
Report rho_0_table with columns: [R, M_ring, rho_0/m_particle, f/m_particle]
This is the key output for DER-QNG-029.
```

## Decision rule

**Overall PASS** if Checks 1, 2, 3 pass.

The primary output is the M_ring_integral value for R=4 (the standard ring),
which enters directly into the rho_0 formula.

## Artifact paths

- `07_validation/audits/qng-ring-sigma-integral-v1/report.json`
- `07_validation/audits/qng-ring-sigma-integral-v1/summary.md`
