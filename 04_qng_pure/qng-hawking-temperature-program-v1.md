---
type: note
id: NOTE-QNG-032
title: Path 3 — research program to derive Hawking temperature T_H from QNG substrate
status: PROGRAM CHARTER — multi-stage research program, 6-11 weeks estimated
author: C.D Gabriel
date: 2026-05-06
upstream:
  - DER-QNG-066 (Stability Principle)
  - DER-QNG-067 (ℏ derivation)
  - DER-QNG-072 (v11 tensor extension)
  - NOTE-QNG-031 (block-spin RG + Padmanabhan = factor 0.67 of Λ_obs)
downstream: closure of Λ derivation, possibly NOTE-QNG-033 onwards
---

# NOTE-QNG-032 — Path 3 research program: Hawking T from QNG

## Goal

Derive `T_H = κ/(2π)` (Hawking temperature on cosmological horizon) and
`S = A/(4 ℓ_P²)` (Bekenstein-Hawking entropy) directly from QNG substrate
dynamics, without invoking standard QFT-in-curved-spacetime.

If successful: closes the partial derivation in NOTE-QNG-031, giving Λ
fully derived from QNG (currently within factor 0.67 using standard physics
for these two pieces).

## Status: NOT STARTED

Today (2026-05-06) we identified that this is the missing piece. Below is
the structured 4-stage program. Estimated total duration: 6-11 weeks of
focused work.

## Stage 1: Emergent metric from v11 (1-2 weeks)

**Goal:** Show that v11 substrate produces a propagating spin-2 tensor field
that responds to matter sources as in linearized GR.

**Tasks:**
1. Derive the linearized equation of motion for `h_ij` from v11 Lagrangian
   (already present in DER-QNG-072)
2. Compute the source term: how does `σ_m` (matter ring/soliton) couple to
   `h_ij`?
3. Solve in static limit: does `h_ij(r)` decay as `1/r` outside source
   (Newtonian gravity)?
4. Verify dispersion `ω² = c²·k²` numerically on lattice with `h_ij` initialized

**Success criterion:** A point source in `σ_m` produces `h_ij(r) ~ G_QNG·M/r`
with `G_QNG = β_g/z` (already known from DER-QNG-067).

**If fails:** v11 doesn't actually have emergent geometry — Path 3 blocked,
need different approach (maybe v12 EM or v13 non-Abelian).

## Stage 2: de Sitter solution in QNG (2-3 weeks)

**Goal:** Find a static solution of QNG equations that mimics de Sitter
spacetime — exponential expansion with horizon at R = R_H.

**Tasks:**
1. Search for solutions with `σ_g(r,t)` and `h_ij(r,t)` profiles consistent
   with FLRW metric `ds² = -dt² + a²(t) dx²` with `a(t) = exp(H₀t)`
2. Verify these solutions are stable under v11 dynamics on long timescales
3. Identify the "de Sitter horizon" as the location where local clock rate
   (effective frequency of `h_ij` modes) → 0
4. Verify horizon location matches `R_H = c/H₀`

**Success criterion:** A self-consistent QNG state on lattice that exhibits
exponential expansion + horizon at correct distance.

**If fails:** QNG substrate may not support de Sitter geometry — Λ_obs
remains observational input even with full v11 framework.

**Critical computational requirement:** Long-time simulation (T = 10⁴ - 10⁵
lattice units) on L = 64-128 lattice. Estimated 2-3 days GPU compute.

## Stage 3: Surface gravity κ at horizon (1-2 weeks)

**Goal:** Compute the QNG analog of surface gravity κ — rate of effective
clock-rate change near the horizon.

**Tasks:**
1. From Stage 2 de Sitter solution, extract the effective metric `g_tt(r)`
2. Compute `κ = (1/2) ∂_r g_tt|_horizon` (standard GR formula)
3. Verify `κ = 1/R_H = H₀` (de Sitter prediction)
4. Cross-check via "redshift integral" — propagate a wave from inside to
   horizon and measure frequency loss

**Success criterion:** κ extracted matches `H₀` within numerical precision.

**If fails:** Either Stage 2 solution is wrong, or QNG has different surface
gravity definition. Both require revisiting.

## Stage 4: Hawking T from substrate (2-4 weeks)

**Goal:** Derive `T_H = κ/(2π)` from substrate dynamics, plus
`S = A/(4 ℓ_P²)` from substrate counting.

**Three independent methods (cross-check):**

### Method 4A: Wick rotation / periodicity
- Set up QNG in Euclidean signature (imaginary time)
- Find periodicity in imaginary time = `2π/κ` (no conical singularity at
  horizon)
- Identify temperature as `T = 1/period = κ/(2π)`

### Method 4B: Bogoliubov coefficients
- Compute particle creation rate at horizon: amplitude for vacuum mode at
  past horizon to be observed as thermal mode at future horizon
- Extract temperature from spectrum: thermal Bose distribution at `T = κ/(2π)`

### Method 4C: Tunneling (Parikh-Wilczek)
- Compute imaginary part of the action for a wavepacket tunneling across
  horizon
- Probability `~ exp(-Im(S)/ℏ)` interpreted as thermal at `T_H`

**Success criterion:** All three methods give consistent `T_H = 1/(2π·R_H)`.

**Deliverable:** Λ × ℓ_P² = 3/N_H² fully derived from QNG, no standard
physics inputs needed.

## Resource estimates

| Stage | Duration | GPU time | Theoretical work | Risk |
|---|---|---|---|---|
| 1 | 1-2 weeks | 1-2 days | 60% | low |
| 2 | 2-3 weeks | 3-5 days | 50% | medium |
| 3 | 1-2 weeks | 1 day | 70% | low (if Stage 2 OK) |
| 4 | 2-4 weeks | 2-3 days | 80% | medium |
| **Total** | **6-11 weeks** | **7-11 days** | mixed | medium |

**Parallel work:** Some tasks can be done in parallel (e.g., Stage 1
analytical work can begin while planning Stage 2 simulations).

## Why this is worth pursuing

If Path 3 succeeds:
1. **First derivation of Λ from microscopic substrate** in any framework
2. **First QNG derivation of Bekenstein-Hawking entropy** (currently
   imported from standard physics)
3. **Closes Gap 5 fully**, eliminating it from the open-problems list
4. **Multi-paper publication potential**:
   - Paper 1: Block-spin RG result (NOTE-QNG-031)
   - Paper 2: v11 emergent metric
   - Paper 3: de Sitter solution in QNG
   - Paper 4: Hawking T from substrate (Path 3 closure)
5. **Strong evidence for QNG framework**: providing microscopic origin for
   black hole thermodynamics is what string theory aimed for and partially
   achieved (BPS BHs only)

## Why this is risky

1. **Stage 2 may fail**: QNG might not support de Sitter geometry stably.
   This has been a generic problem (Yukawa cosmology failed in DER-QNG-090).
2. **Stage 4 may give different T**: substrate quantization could give
   `T_H = α·κ/(2π)` for some α ≠ 1, leaving cosmology unmatched.
3. **Computational requirements** could escalate if larger lattices needed.

## Alternative if Path 3 fails

If after 6-11 weeks Path 3 doesn't close, accept:
- Λ remains "within factor 0.67 of observed using QNG block-spin + standard
  Bekenstein-Padmanabhan"
- This is still the best microscopic derivation in any framework
- Publish as "QNG provides substrate origin for Bekenstein-Hawking scaling
  via block-spin RG"

## First concrete step (today, 1-2 hours)

Run Stage 1.1: derive linearized equation of motion for `h_ij` from
v11 Lagrangian, verify it matches linearized Einstein equation in vacuum.

This is analytical work, no simulation needed. Can be done in this session.
Result will be saved in companion document or appended here.

## Cross-references

- DER-QNG-072 (v11 tensor extension — has `h_ij` Lagrangian)
- NOTE-QNG-031 (block-spin RG + Padmanabhan partial derivation)
- DER-QNG-090 (cosmology diagnosis, why Yukawa failed for Λ)
- Standard references:
  - Bekenstein-Hawking 1973-1975 entropy/temperature
  - Padmanabhan 2005 thermodynamic gravity
  - Parikh-Wilczek 2000 tunneling derivation
