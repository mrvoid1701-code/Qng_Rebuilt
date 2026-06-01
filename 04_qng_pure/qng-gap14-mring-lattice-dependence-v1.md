---
type: derivation
id: DER-QNG-075
title: Gap 14 — M_ring ratios depend on lattice size; DER-QNG-038 baryon match was finite-size coincidence
status: STRUCTURAL FINDING; effectively retracts DER-QNG-038 baryon identification
author: C.D Gabriel
date: 2026-04-25
upstream:
  - DER-QNG-038 (baryon ladder, L=20-based)
  - DER-QNG-074 (Gap 13 scale tension)
  - CPU-074/075 (L=20 M_ring data)
  - CPU-125 (L=28 M_ring extension)
  - CPU-126 (L-dependence ratio audit)
---

# DER-QNG-075 — Gap 14: M_ring ratios are L-dependent

## Statement

The M_ring(R)/M_ring(R=4) ratios that DER-QNG-038 used to identify
the baryon ladder are **lattice-size-dependent**. At L=20 the match
with observed hadron ratios is <1%; at L=28 the deviations grow to
7-9%. The match at L=20 was therefore a **finite-size lattice
coincidence**, not a structural prediction of QNG.

## Numerical evidence (CPU-126)

| R | particle | m_PDG / m_N | L=20: M(R)/M(R=4) | %off | L=28: M(R)/M(R=4) | %off |
|---|---|---|---|---|---|---|
| 4 | N(938) | 1.0000 | 1.0000 | 0.0% | 1.0000 | 0.0% |
| 5 | Δ(1232) | 1.3131 | 1.3100 | -0.2% | 1.2327 | **-6.1%** |
| 6 | N*(1520) | 1.6200 | 1.6080 | -0.7% | 1.4773 | **-8.8%** |
| 7 | Δ(1700) | 1.8118 | 1.8220 | +0.6% | 1.6841 | **-7.1%** |

**Mean |deviation| at L=20**: 0.51% (matches DER-QNG-038's <2% claim)
**Mean |deviation| at L=28**: 7.33% (14× worse)

The L=28 R=8/9/10 measurements (also CPU-125) show deviations of
6.0%, +1.0%, +2.9% respectively — variable, not converging.

## Mechanism (why L matters)

`M_ring = sum_n max(0, sigma_ref - sigma_m(n))` is the integrated
**deficit** of sigma_m, summed over **the entire lattice volume**, not
just the ring's neighborhood.

A sigma_m vortex ring of radius R depletes sigma_m primarily in a
toroidal tube around the ring. But the precise depletion profile, and
the depletion in the surrounding background, depends on:
- Distance to lattice edge (periodic BC + finite L)
- Background equilibration of phase phi(x) over the bulk
- Disorder term `gamma_phi * disorder(phi) * sm` in Phase 2 acts on
  the ENTIRE volume, depleting sm wherever phi is disordered

For larger L, more bulk volume → larger absolute M (consistent with
L=28 giving 1.5× the L=20 values). And the *ratio* between rings of
different R changes too because the bulk contribution scales
differently from the ring contribution.

**M_ring is NOT a topological invariant in any rigorous sense.** It
is an integrated quantity with mixed ring + bulk contributions.

## Consequences

### DER-QNG-038 baryon ladder

**Effectively retracted.** The identification

```
R=4 ↔ N(938 MeV)
R=5 ↔ Δ(1232 MeV)
R=6 ↔ N*(1520 MeV)
R=7 ↔ Δ(1700 MeV)
```

with single calibration `a_M = 1.373×10⁻³` was based on the L=20
specific ratio match. At L=28 the same ladder predicts:

```
R=5 ↔ Δ?(1156 MeV)   [-6% off Δ(1232)]
R=6 ↔ N*?(1386 MeV)  [-9% off N*(1520)]
R=7 ↔ Δ?(1580 MeV)   [-7% off Δ(1700)]
```

7-9% deviations are not within typical hadronic theoretical precision.
The "match" was lattice-specific.

### Combined impact with Gap 13 (DER-QNG-074)

**Gap 13** showed the absolute calibration `a_M_phenom` was 22 orders
of magnitude off the substrate-derived `a_M_bridge`. **Gap 14** shows
even the relative ratios were L-specific.

Together: DER-QNG-038's baryon ladder is **wrong on both axes**:
- Absolute scale (Gap 13): 10²² off Planck scale
- Relative ratios (Gap 14): L-dependent, no L-independent match

### What remains valid

1. **Geometric pattern M(R) ≈ linear in R** is real (CPU-125 fit
   slope ≈ 230 at L=28). This reflects torus geometry: ring of radius
   R in a tube of fixed cross-section depletes volume ∝ R.
2. **Stable vortex rings exist** in QNG v7 and form via the canonical
   3-phase protocol (Phase 1 + Phase 2). This is a genuine soliton
   sector.
3. **CPU-074 conservation** of M_ring under Phase-3 (no Channel A or F)
   is exact (Laplacian sums to zero). But this is conservation under
   pure diffusion, NOT a topological theorem.

### Phase C particle program

**Cannot proceed via M_ring identification.** Need entirely different
approach for QNG → particle physics correspondence.

Possible alternative approaches:
- **Energy spectrum E_R(L)**: compute ⟨H⟩_ring under v10 and check if
  L→∞ extrapolated values are well-defined and L-independent.
- **Spectral analysis**: look for discrete bound-state energies in
  ring spectrum at large L (Jackiw-Rebbi modes already CONFIRMED at
  GPU-035 — these may be the actual particle states, not the rings
  themselves).
- **Topological charges that ARE L-independent**: phi-winding number,
  Hopf invariant, etc. — but GPU-038 / CPU-080 showed v8 sine-Gordon
  vacuum destroys 2π winding.

### Honest reassessment of QNG status

After Gap 13 + Gap 14, the QNG status is:

**Solid (substrate-level, L-independent)**:
- c_QNG² = β/(z·μ) — derived from dispersion (DER-QNG-067)
- G_QNG = β/z — derived from Newtonian limit (DER-QNG-019)
- ℏ_QNG = 0.2326 — derived via Stability Principle (DER-QNG-066)
- Λ = 0 structural prediction (DER-QNG-066)
- Unit-bridge SI consistency (CPU-114)
- v11 spin-2 graviton extension (DER-QNG-072)
- Hawking T_H = ℏc³/(8πGM·k_B) trivially reproduced (CPU-120)

**Retracted or downgraded**:
- DER-QNG-038 baryon ladder absolute identification (Gap 13 + 14)
- CPU-115 "E=mc² match nucleon 938 MeV" claim (Gap 13)
- DER-QNG-068 Test 1 result (E=mc²) — m_inertial is well-defined,
  but does not equal nucleon mass under substrate-derived calibration

**Open programs**:
- Gap 5 (cosmological α ↔ Λ) — open
- Gap 12 (tensor graviton ontology) — closed at linear level via v11
  axiomatic addition (savant: actually a definitional dissolution,
  not a derivation)
- Gap 13 (scale separation) — open, needs RG flow or scale-bridging
- Gap 14 (M_ring lattice dependence) — observational, requires new
  particle-identification approach
- Particle physics correspondence — wide open, no clean path

## Why this wasn't caught earlier

- DER-QNG-038 was tested at L=20 only (CPU-074/075 ran at L=20).
- The L=120 mass ratio test mentioned in qng-mass-observable-exhaustion-v1.md
  found "M_ring(R=5)/M_ring(R=4) ≈ 1.04" but was interpreted as
  evidence for a different problem (size scaling), not as
  retraction of the L=20 match.
- No systematic L-scan of M_ring ratios was performed before locking
  DER-QNG-038.
- The 4-point ratio match at L=20 was so impressive (<1% across 3
  independent ratios) that it appeared structural.

## Recommendations

1. **Update DER-QNG-038**: explicit retraction of absolute hadron
   identification; preserve as "geometric pattern observation at
   L=20 with no clear physical interpretation".
2. **Update DER-QNG-068**: Test 1 (E=mc²) re-graded to PASS structural
   only; nucleon-mass match retracted.
3. **Update THEORY_STATE Section 4** (DER-QNG-044 status table) to
   reflect E=mc² re-grade.
4. **Add Gap 14 to Section 3** of THEORY_STATE.
5. **Phase C programme**: new approach needed. Working hypothesis:
   real "particles" in QNG might be the **Jackiw-Rebbi bound modes**
   (φ in σ_m wells, GPU-035 confirmed at 0.02%), not the rings
   themselves. The rings would then be **classical solitons** or
   **monopoles/cores**, and the physical particles are **quantized
   excitations bound to them** — analogous to electrons bound to
   nuclei in atomic physics.
6. **Don't continue C2 (leptons) or C3 (mesons) until C1 has a clean
   correspondence**.

## Verification log

- CPU-125: M_ring(R=8,9,10) at L=28 with same protocol as CPU-074/075
- CPU-126: explicit L=20 vs L=28 ratio comparison; deviation jumped
  14× from 0.5% to 7.3%
- Cross-check: linear fit M(R) at L=28 has slope 236 with non-trivial
  residuals (-87 to +57); pattern is approximate, not precise.
- Geometric expectation: torus volume ∝ R, M_ring ∝ R approximately
  confirmed.
