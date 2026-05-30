---
type: derivation
id: DER-QNG-095
title: Stress test verdict — baryon identifications DOWNGRADED to TENTATIVE
status: ANALYSIS — critical refinement after CPU-169 stress test
author: C.D Gabriel
date: 2026-05-30
upstream:
  - DER-QNG-093 (initial baryon identifications)
  - DER-QNG-094 (Delta family + neutron + chirality)
  - CPU-169 (this work's stress test)
---

# DER-QNG-095 — Stress test verdict and revised identification status

## Critical finding from CPU-169

The CPU-169 stress test extending Phase 3 from 3000 lu to 6000 lu
revealed that **all 8 identified particles shift significantly** in
mass under longer evolution:

| Particle | Original error (3000) | Stressed error (6000) | Status |
|---|---|---|---|
| proton (trefoil) | 0.00% (ref) | 0.00% | ROBUST |
| anti-proton (anti-trefoil) | 0.00% | 0.00% | ROBUST |
| Δ+ (Hopfion Q1) | 1.65% | -39.36% | TENTATIVE |
| Δ- (anti-Hopfion Q1) | 1.65% | -39.36% | TENTATIVE |
| Δ++ (W+W+) | 0.68% | -23.31% | TENTATIVE |
| Δ-- (W-W-) | 0.30% | +11.16% | TENTATIVE |
| neutron (W+W- D=10) | 0.21% | -78.22% | UNSTABLE |
| a0(980)+ (WpWmWp) | 0.24% | -13.27% | TENTATIVE |

**Robust under stress: 2 (proton, anti-proton)**
**Tentative pending equilibrium: 5 (Δ family + a0)**
**Unstable / artefact: 1 (neutron)**

## Diagnosis

The QNG v12 enhanced dissipative dynamics exhibits long-period
oscillations and slow equilibration. The arbitrary Phase 3 = 3000 lu
choice in CPU-159/164/165/167/168 captured a transient snapshot, not
true equilibrium.

The mass-RATIO identifications were artifacts of:
- The reference (trefoil) and the targets shifting at similar rates
  during the transient
- Numerical coincidence of being at the same phase of oscillation

When Phase 3 is doubled to 6000 lu, the relative phases differ and the
ratios change substantially.

## What this means physically

The QNG-SM IDENTIFICATIONS are not falsified — they are TENTATIVE.
The framework still predicts:
- A discrete spectrum of stable topological soliton classes
- Topology-dependent equilibrium masses
- Chirality-symmetric ±particle pairs

But the SPECIFIC mass-ratio values, and therefore the QNG-SM
correspondence at the percent level, depend on reaching true
equilibrium. This requires:
- Much longer Phase 3 (10000-30000 lu)
- Or different protocol (conservative dynamics post-equilibration)
- Or analytical treatment of the oscillation modes

## What identifications survive

**Only the chirality-protected pairs survive:**
- proton (trefoil) ↔ anti-proton (anti-trefoil): mass ratio = 1.000
  by chirality symmetry, independent of dynamic equilibration.

**Reason**: anti-trefoil has phi → -phi. The dynamics is invariant
under this transformation (the v7 + v12 Hamiltonian respects this).
So the masses must be equal at ALL times, not just equilibrium.
Therefore the proton ↔ anti-proton mass equality is a SYMMETRY THEOREM
of QNG, not a numerical identification.

This is the QNG analog of the CPT theorem: particle and anti-particle
have identical masses.

## Updated identification count

**Confirmed identifications** (robust under stress, theorem-level):
1. proton ↔ trefoil (reference)
2. anti-proton ↔ anti-trefoil (chirality theorem)

**Tentative identifications** (need equilibrium verification):
3. Δ+ ↔ Hopfion Q1 (was 1.65%, requires longer P3)
4. Δ- ↔ anti-Hopfion Q1
5. Δ++ ↔ W+W+ composite
6. Δ-- ↔ W-W- composite
7. neutron ↔ W+W- composite at specific D
8. a0(980)+ ↔ WpWmWp layered composite

## Honest verdict for the session

After all CPU-145 through CPU-169 work:

**ROBUST identifications**: 2 (proton family by chirality symmetry)
**TENTATIVE identifications**: 6 (depend on Phase 3 equilibration)

The original "8 particles identified" claim was overconfident. The
correct statement is "8 particle CANDIDATES with mass ratios in
agreement with SM at 3000-lu snapshot, of which 2 are confirmed
robust by chirality symmetry and 6 require equilibrium verification".

## Status of falsifiability conditions (revised)

P_F1-P_F7 from DER-QNG-093/094 remain valid as stated.

**NEW P_F8**: If 30000+ lu Phase 3 evolution shows masses do NOT
converge to values matching SM at the 1-2% level, the QNG-SM mass
identifications beyond proton/anti-proton are FALSIFIED.

## Recommended next steps (urgent)

1. **CPU-170**: ultra-long Phase 3 (20000-30000 lu) for trefoil + Hopfion
   Q1 to find asymptotic mass
2. **CPU-171**: conservative Phase 3 (post-relaxation, no F, no chi_decay)
   to test alternative equilibration
3. **Statistical analysis**: average over multiple oscillation periods
   to extract mean equilibrium mass
4. **Updated Paper 7**: downgrade claims from "8 particles identified"
   to "2 robust + 6 tentative pending equilibrium confirmation"

## Methodological lesson

This stress test illustrates the importance of equilibrium
verification BEFORE claiming numerical identifications. The session
discovered identifications that LOOKED clean at 3000 lu but turn out
to be transient. This is a STANDARD pitfall of dissipative lattice
dynamics and should be expected to recur in future QNG work.

For all future identification claims, equilibrium must be verified
via:
- Long evolution (10× the apparent settling time)
- OR conservative dynamics post-equilibration
- OR multiple time-window averaging
