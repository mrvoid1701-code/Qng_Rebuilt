---
type: derivation
id: DER-QNG-096
title: REAL PROBLEM identified — QNG mass measurement has no well-defined equilibrium
status: CRITICAL FINDING — methodological/structural issue with current framework
author: C.D Gabriel
date: 2026-05-30
upstream:
  - DER-QNG-095 (stress test verdict)
  - CPU-169 (stress test)
  - CPU-170 (ultra-long Phase 3)
  - CPU-171 (conservative Phase 3)
---

# DER-QNG-096 — The real problem: QNG mass has no well-defined equilibrium

## Critical finding (CPU-170 + CPU-171)

After exhaustive investigation, the REAL PROBLEM with the QNG-SM
identification framework is identified:

> **There is no well-defined notion of "QNG equilibrium mass" under
> current dynamics.**

This explains why the stress test (CPU-169) showed massive shifts
between Phase 3 = 3000 lu and Phase 3 = 6000 lu, and why CPU-170
showed continued drift at Phase 3 = 30000 lu.

## Diagnosis

### CPU-170 result (dissipative Phase 3 = 30000 lu)

Even at 10× longer Phase 3, **masses do not converge**:

| Config | Peak M | Min M | "Asymptote" | rel_change |
|---|---|---|---|---|
| trefoil | 2460 | 1405 | 1461 ± 4 | converges? |
| Hopfion Q1 | 2778 | 506 | 777 ± 25 | 34% drift |
| W+W+ | 3025 | 1344 | 1488 ± 8 | converges? |
| W-W- | 3003 | 338 | 432 ± 17 | 34% drift, still GROWING |

W-W- mass was still GROWING monotonically at t=30000 (379 → 391 → ... → 454).
Hopfion Q1 has 34% variation. Even the "converged" configs may shift
at 100000+ lu.

### CPU-171 result (conservative Phase 3)

Under FULLY CONSERVATIVE Phase 3 (Channel A off, Channel F off,
CHI_DECAY off), masses are EXACTLY CONSERVED:

| Config | M_P2_end | M after 5000 conservative lu | Variation |
|---|---|---|---|
| trefoil | 448 | 448 | **0.00%** |
| Hopfion Q1 | 1360 | 1360 | 0.00% |
| W+W+ | 736 | 736 | 0.00% |
| W-W- | 734 | 734 | 0.00% |

This is because σ_m diffusion (Channel B alone) preserves total σ_m
on the periodic lattice. M_ring = N·σ_ref − Σσ_m is therefore exactly
constant.

But the conservative-equilibrium values give DIFFERENT identification
errors than the dissipative ones:

| Config | Conservative M | Ratio vs proton | Predicted (MeV) | vs Δ family |
|---|---|---|---|---|
| Hopfion Q1 | 1360 | 3.04 | 2851 | Δ+ (+131%) ❌ |
| W+W+ | 736 | 1.64 | 1542 | Δ++ (+25%) ❌ |
| W-W- | 734 | 1.64 | 1539 | Δ-- (+25%) ❌ |

So the conservative-mass identifications also FAIL the original
1-2% claims.

## The fundamental problem

The QNG mass `M_ring` measures matter-depletion around phi-vortex.
This depends on:

1. **Phase 1 duration**: how long phi vortex is allowed to form before
   matter starts depleting
2. **Phase 2 duration**: how long Channel F operates depleting matter
3. **Phase 2 termination**: arbitrary stop point
4. **Phase 3 dynamics**: dissipative (Channel A + B) drives M_ring back
   toward zero over very long times; conservative preserves Phase 2 end

**There is no INTRINSIC notion of QNG equilibrium mass**. The measured
value depends on the protocol's arbitrary timings (PHASE1=300, PHASE2=
1500).

If we change Phase 2 from 1500 lu to 15000 lu, the M_P2_end values
will be different. Conservative Phase 3 will preserve different
numbers. Identifications will differ.

## What this means for QNG-SM correspondence

The original claims of "8 baryons identified at 1-2% precision"
should be downgraded to:

> "Under one specific simulation protocol (PHASE1=300, PHASE2=1500,
> Phase 3 dissipative=3000 lu at v12 enhanced e=3.0, L=20), the
> mass-ratio snapshots match SM baryon ratios at the 1-2% level for
> several knot topologies. These ratios are protocol-dependent and
> do not represent true equilibrium values."

The chirality-protected pairs (proton↔anti-proton) remain robust
because they are equal by symmetry at every snapshot.

The other 6 identifications (Δ family + neutron + a0) are **protocol
artefacts**.

## Possible resolutions

### Option 1: Symplectic v8 dynamics
The v8 canonical Hamiltonian (DER-QNG-042) has conjugate momenta and
energy conservation. Solitons in v8 have well-defined equilibrium
masses via Noether charges. This is the CLEANEST path forward.

Cost: need to extend v8 simulation to v12 EM coupling. Substantial
coding (~weeks). Existing v8 code on GPU (qng_v8_canonical_gpu.py).

### Option 2: Analytical linearization
Linearize the v12 EM-coupled v7 equations around the soliton
configuration. Compute eigenvalues; the ground-state eigenvalue is
the mass.

Cost: substantial mathematical work. Likely requires WKB approximation
or numerical eigensolvers.

### Option 3: Long-time averaging
Run dissipative dynamics for very long times (100000+ lu) and average
over the late-time oscillation. The MEAN of the oscillation might
be the meaningful "equilibrium".

Cost: high compute (100x current). Not feasible at L=20 CPU.

### Option 4: Accept protocol-dependent identifications
Define a specific protocol (e.g., "PHASE3=3000 lu dissipative at
e=3.0") as the canonical measurement. All identifications are
relative to this protocol.

Cost: zero — but makes the framework less fundamental.

## Honest verdict on this session's identifications

Under the protocol used (PHASE3=3000 lu), 8 candidate identifications
were claimed:
- 2 robust (proton, anti-proton by chirality)
- 6 protocol-dependent (Δ family + neutron + a0)

Under longer Phase 3, the 6 protocol-dependent identifications all
shift significantly:
- Errors range from 11% to 78% at PHASE3=6000 lu
- Errors don't stabilize at PHASE3=30000 lu either

**Honest current count of QNG-SM identifications**:
- **Robust by symmetry: 2** (proton, anti-proton)
- **Tentative pending equilibrium method: 6** (Δ family, neutron, a0)
- **Total candidates: 8**

The framework is NOT FALSIFIED — it remains consistent with QNG
producing topologically distinct soliton classes. But the NUMERICAL
precision of identifications cannot be established at the percent
level until equilibrium is properly defined.

## The "real problem" identified

QNG framework as currently implemented has:
- Well-defined topology
- Well-defined chirality symmetry
- Well-defined v12 gauge structure

But it LACKS:
- Well-defined equilibrium mass (depends on arbitrary Phase 2/3 timing)

This is the fundamental obstacle. Until resolved (via v8 symplectic,
analytical linearization, or other method), all QNG mass
identifications at percent-precision are tentative.

## Recommendation for theoretical priority

1. **HIGH**: Port v12 EM dynamics to v8 symplectic framework (GPU-based)
   to get energy-conserving dynamics with well-defined eigenvalue masses
2. **MEDIUM**: Analytical linearization for each soliton class
   (proton-trefoil at minimum)
3. **LOW**: Accept current limitations and proceed with chirality-based
   robust identifications only

## Methodological lesson

Future QNG identification work should:
- ALWAYS verify equilibrium before claiming identifications
- Use multiple time-window measurements (1000, 3000, 10000 lu)
- Distinguish "snapshot" from "asymptote"
- Be conservative about precision claims

This stress test was REVELATORY but COSTLY in terms of overclaim
correction. Future work should bake equilibrium verification into
the protocol from the start.
