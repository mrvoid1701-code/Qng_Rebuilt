# QNG Cosmology Structural Diagnosis v1

Type: `derivation`
ID: `DER-QNG-090`
Status: `LOCKED — structural finding`
Date: 2026-04-25
Author: C.D Gabriel
Test: `tests/cpu/qng_cosmology_v2_diagnostic.py`

---

## Inputs

- [qng-poisson-assembly-v1.md](qng-poisson-assembly-v1.md) — DER-QNG-018 (screened Poisson)
- [qng-alpha-cosmological-v1.md](qng-alpha-cosmological-v1.md) — DER-QNG-020 (alpha <-> Lambda)

---

## Statement

The QNG-Yukawa kernel (`DER-QNG-018`), rigorous for static sources, **does
not extend** to a working modified Friedmann equation that matches eBOSS DR16
BAO data. Paper 4's claim that "Yukawa screening replaces Λ" is structurally
unsupported.

This document provides the rigorous diagnosis.

---

## 1. The structural obstruction

### 1.1 Yukawa screening for static sources (correct, locked)

For a point source in QNG, the substrate equation gives:
```
(α + ν∇²) δσ_g = -k_gm ρ_m
```

In Fourier space, this yields the Yukawa form:
```
Φ(r) = -G M e^(-r/λ_screen) / r
```

with `λ_screen = √(β_g/(z α))`. Identifying `λ_screen ~ R_Hubble` requires
`α_phys ~ 7.9×10⁻¹²⁴` — matches observed `Λ·ℓ_P²` to factor 7.

This part is correct and locked (DER-QNG-018, DER-QNG-020).

### 1.2 The cosmological extension (BROKEN)

The naive extension to FLRW:
```
H²(z) = (8πG/3) ρ_m × Y(R_H/λ)
```

where `Y(R_H/λ) = exp(-R_H/λ)(1 + R_H/λ)` is the Yukawa enhancement of force
on a Newton-sphere of radius `R_H`, fails because:

1. At high z (z ≳ 1), `R_H(z) << λ`, so `Y → 1` (no screening).
2. Therefore `H_QNG(z >> 1) → H_0 √(Ω_m_total (1+z)³)` — pure matter.
3. ΛCDM at high z has only matter, with `Ω_m = 0.315`. QNG-Yukawa requires
   `Ω_m_total ≈ 1.36` (to achieve `H(0) = H_0` after horizon-scale screening).
4. Hence `H_QNG(z) / H_LCDM(z) → 2.0` at z = 2-3.

This factor-2 deviation gives **χ²/dof = 161** against eBOSS DR16 BAO —
WORSE than pure matter (χ²/dof = 103).

### 1.3 Numerical evidence (CPU-COSMO-V2)

| Model | χ²/dof | Verdict |
|---|---|---|
| LCDM (Ω_m=0.315, Ω_Λ=0.685) | **0.975** | EXCELLENT |
| Pure matter (Ω_m=1, Λ=0) | 103.2 | CATASTROPHIC |
| Yukawa-mod. Friedmann (any R/λ) | **161-309** | STRUCTURAL FAIL |
| CPL best-fit (w0=-1, wa=0.2) | 0.884 | comparable to LCDM |

H(z) comparison at BAO redshifts:

| z | H_LCDM | H_Yukawa | H_pure_matter | Yuk/LCDM |
|---|---|---|---|---|
| 0.7 | 100.7 | 168.7 | 149.4 | 1.68 |
| 1.0 | 120.7 | 217.9 | 190.6 | 1.81 |
| 1.5 | 159.6 | 307.4 | 266.4 | 1.93 |
| 2.0 | 204.3 | 405.8 | 350.2 | 1.99 |
| 3.0 | 307.7 | 626.9 | 539.2 | 2.04 |

All units km/s/Mpc.

### 1.4 Why Yukawa cannot work

**Fundamental issue**: Yukawa screening operates at scales `r ~ λ_screen`.
For `λ_screen = c/H_0` (fixed today), this is the Hubble radius today.

In FLRW, the relevant cosmic scale at redshift z is `R_H(z) = c/H(z)`. As z
increases, H(z) increases, so R_H(z) DECREASES. At BAO redshifts (z ~ 1):

```
R_H(z=1) / λ_screen ≈ H_0 / H(1) ≈ 0.5    (less than 1)
R_H(z=1.5) / λ_screen ≈ 0.4    (less than 1)
```

So at BAO redshifts, the universe is well INSIDE the screening length —
Yukawa is irrelevant. Gravity behaves Newtonian. This means matter
gravitates fully. No DE-like effect.

ΛCDM works at BAO because Λ contributes constantly at all z (including high z
where it dominates the late-time evolution). Yukawa contribution PEAKS at z=0
and vanishes at z>>1. Wrong sign of redshift dependence to mimic Λ.

### 1.5 Newton-sphere argument has its own problem

For a HOMOGENEOUS density distribution, the Yukawa potential is constant
(independent of position), giving zero force. Friedmann derivation requires
either:
- A finite sphere of radius R bounded by something (causal horizon, comoving
  observer scale, etc.)
- Or a covariant derivation from Einstein-like field equations

QNG has neither at the cosmological level. The sphere argument used in
H3 above is heuristic — not a rigorous derivation.

A truly rigorous QNG cosmology would require:
1. Coupling QNG substrate to FLRW metric (or equivalent emergent geometry)
2. Deriving modified field equations
3. Reducing to modified Friedmann

This program is **not yet executed** in QNG.

---

## 2. What QNG actually has at cosmological scale

| Item | Status |
|---|---|
| Λ = 0 structural | LOCKED (Stability Principle) |
| Yukawa form for static sources | LOCKED (DER-QNG-018) |
| α ↔ Λ identification at scale-match | factor-7 across 125 orders (LOCKED as identification) |
| Modified Friedmann from substrate | **NOT DONE** |
| FLRW emergent geometry | NOT DERIVED |
| Sakharov-induced effective Λ | <10% of observed (DER-QNG-018 file 18) |
| Quintessence-like substrate scalar | NOT DERIVED |

---

## 3. Three honest paths forward

### Path A: New mechanism within QNG

Identify a substrate-derived process that gives effective DE consistent with
BAO. Candidates:

1. **Substrate scalar as quintessence**: σ_g or χ field acting as slow-rolling
   scalar. Requires deriving its potential V(φ) from substrate dynamics
   (currently absent).

2. **Modified geometry from substrate topology**: non-trivial topology of the
   substrate graph could give effective DE. Speculative.

3. **Backreaction from inhomogeneities**: in QNG, the substrate is fundamentally
   discrete; statistical averaging might give residual energy density. Would
   require detailed coarse-graining analysis.

**Status**: all speculative. None derived. Each is a multi-month research
program.

### Path B: Accept QNG cannot explain DE

Honest scope:
- QNG explains: c, G, ℏ derivation; static gravity; Newtonian limit; particle
  ontology; Λ = 0 structural prediction.
- QNG does NOT explain: observed cosmic acceleration; dark energy.

Treat dark energy as **beyond QNG** phenomenology, like dark matter (also
unsolved in QNG — exhausted in DM Phase 1-4 retrospective).

This is **honest scope**, not failure. Many physical theories don't address
all phenomena (e.g., GR doesn't derive matter; QED doesn't address gravity).

### Path C: Reinterpret observations

DESI 2024 hints at evolving DE (`w(z) ≠ -1` constant). If actual cosmology
has time-varying DE, ΛCDM is the wrong fit. QNG might predict a SPECIFIC
form of evolving DE that matches.

Best CPL fit to eBOSS BAO alone: w0=-1, wa=0.2, χ²/dof = 0.884.
DESI 2024 reports: w0=-0.55±0.21, wa=-0.83±0.65 (different).

QNG would need to derive a specific w(z) from substrate dynamics. **Not yet
done.** This is a high-risk, high-reward path.

---

## 4. Recommended action

### 4.1 Immediate

**Update Paper 4 to honest scope**:
- Retract the "Yukawa replaces Λ" claim explicitly.
- Keep: Yukawa form for static sources, Λ=0 structural prediction.
- Add: clear statement that QNG currently lacks a DE mechanism.

### 4.2 Medium-term

**Pursue Path C (evolving DE) as research program**:
- Derive substrate dynamics in cosmological context.
- Compute w(z) prediction.
- Compare with DESI 2024 + future surveys (Euclid, LSST).

### 4.3 Long-term

**Build covariant QNG cosmology**:
- Extend substrate to dynamic emergent metric (beyond static + linear).
- Derive Einstein-like equations from QNG action.
- Compute Friedmann equation from first principles.

This is the proper path to a complete QNG cosmology. Multi-year program.

---

## 5. Verification status

This diagnosis is verified by:
1. `tests/cpu/qng_cosmology_v2_diagnostic.py` — 6 cosmological hypotheses
   tested against eBOSS DR16 BAO.
2. Independent integrators (scipy.quad and trapezoid) give identical χ².
3. H(0) = H_0 by construction for all models.
4. Iteration convergence verified for H3 Yukawa (10 vs 50 iterations: agree
   to 6 decimal places).
5. r_d sensitivity scan confirms LCDM result robust around 147 Mpc.

The structural failure of H3 (Yukawa) is robust to all parameter choices and
implementation variations.

---

## 6. Connection to other QNG findings

This diagnosis is consistent with and reinforces:
- DM Phase 4 conclusion: QNG cannot solve dark matter without v13 extension.
- Gap 13 (scale separation): substrate-to-particle scale not bridged.
- Gap 5 (cosmological α): α as identification, not derivation.

QNG has multiple **honest open problems** in cosmology + particle masses.
None of these diminish the LOCKED achievements (c, G, ℏ derivation; Stability
Principle; static gravity; Λ=0 structure).

This is **mature theory development** — distinguishing what's solved from
what's open.

---

## Cross-references

- `DER-QNG-018` Yukawa kernel (locked)
- `DER-QNG-020` α-Λ identification (locked at scale-match level)
- `papers/paper4_yukawa_cosmological_alpha.md` (must be revised)
- `tests/cpu/qng_cpu131_eboss_bao_test.py` (toy test, superseded)
- `tests/cpu/qng_cosmology_v2_diagnostic.py` (this diagnosis)
- `theory-v2/18-sakharov-rigorous.md` (Sakharov gives <10% of G)

---

## Status

**Locked finding**: QNG-Yukawa cannot replace Λ in cosmology at BAO precision.
Paper 4 main claim retracted. Honest scope adopted.
