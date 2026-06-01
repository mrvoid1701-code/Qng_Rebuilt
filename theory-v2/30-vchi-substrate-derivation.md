---
title: 30. Substrate Derivation of V(χ) — From Identification to Derivation
status: ATTEMPT — analytical sketch, partial result
date: 2026-04-25
author: C.D Gabriel
---

# 30. V(χ) from QNG Substrate

After validating numerical VEV+fluctuations DE+DM unification (theory-v2/27)
and Lyman-α-compatible mass window (theory-v2/29), the biggest remaining
weakness is that:

- V_0 (DE) is a free parameter
- m_χ (DM mass) is a free parameter
- χ_0 (VEV) is a free parameter

Three "cosmological identifications" all small in Planck units, but
not derived from substrate principles.

This document attempts to **derive** V(χ) from QNG substrate Lagrangian
by integrating out the other fields (σ_g, σ_m, φ) to obtain effective
χ-only potential.

---

## §1 — QNG substrate action (v8 baseline)

### 1.1 Full Lagrangian

```
L_QNG = L_kinetic + L_couplings + L_potentials + L_dissipation
```

Specific form (homogeneous fields, time-only):
```
L = (1/(2μ_g))(σ_g')² + (1/(2μ_m))(σ_m')² + (1/(2μ_φ))(φ')²
  - (1/2)·CHI_REL·χ·∇²σ_g  [in homogeneous limit: 0, since ∇²=0]
  - DELTA_χg · σ_g · χ
  - V_couple(σ_m, φ)
  - (CHI_DECAY/2)·χ²
  + ...
```

For homogeneous + cosmological context, ∇² terms vanish. Action becomes:
```
L_homo = (1/(2μ_g))(σ_g')² + (1/(2μ_m))(σ_m')² + (1/(2μ_φ))(φ')²
       - DELTA_χg · σ_g · χ
       - V_couple(σ_m, φ)
       - (CHI_DECAY/2)·χ²
```

### 1.2 Channel structure relevant for χ

In v7/v8 (per CLAUDE.md), χ appears in:
- **Channel D**: CHI_REL·∇²σ_g + DELTA·σ_g (drives χ from σ_g coupling)
- **Decay term**: -(CHI_DECAY/2)·χ²

In homogeneous limit, only DELTA·σ_g·χ and CHI_DECAY·χ² matter.

---

## §2 — Integrating out σ_g

### 2.1 σ_g equation of motion (homogeneous)

```
δL/δσ_g = 0 →  (1/μ_g)σ_g'' + α(σ_g - σ_ref) + DELTA_χg·χ = -k_gm·ρ_m
```

In quasi-static (slow time evolution) approximation:
```
α(σ_g - σ_ref) = -k_gm·ρ_m - DELTA_χg·χ
σ_g_eq = σ_ref - (k_gm/α)·ρ_m - (DELTA_χg/α)·χ
```

### 2.2 Substituting back into action

The σ_g sector contributes to L:
```
L_σ_g = (1/(2μ_g))(σ_g_eq')² - (α/2)(σ_g_eq - σ_ref)² + (other source terms)
```

For static σ_g_eq:
```
σ_g_eq - σ_ref = -(k_gm/α)·ρ_m - (DELTA_χg/α)·χ
```

So `(σ_g - σ_ref)² = (k_gm·ρ_m + DELTA_χg·χ)²/α²`.

The potential contribution to χ from this:
```
L_eff(χ from σ_g) ⊇ -(α/2) · (DELTA_χg·χ/α)² = -(DELTA_χg²/(2α))·χ²
```

### 2.3 Effective χ mass from this mechanism

```
m_χ²_from_σg = -DELTA_χg²/α
```

Wait — this is **NEGATIVE** mass squared. That's a wrong-sign mass term
(tachyonic).

This makes sense: integrating out a HEAVY field with positive coupling
typically gives NEGATIVE contribution to the lighter field's mass.

To prevent tachyonic instability, we need:
```
m_χ²_total = m_χ²_bare - DELTA_χg²/α > 0
m_χ²_bare > DELTA_χg²/α
```

So the bare CHI_DECAY term must dominate over the σ_g-induced negative
contribution.

### 2.4 Constraint on cosmological identification

For α (cosmological, ~10⁻¹²⁴ Planck²) and DELTA_χg (substrate, O(1)):
```
DELTA_χg²/α ~ 10¹²⁴ Planck²
```

For m_χ²_total > 0:
```
m_χ²_bare > 10¹²⁴ Planck² (super-Planckian!)
```

But Lyman-α requires m_χ ~ 10⁻¹⁰⁵ Planck² (much smaller).

**CONTRADICTION**: integrating out σ_g with cosmological α gives huge
negative mass, requiring even huger positive bare mass to compensate.

### 2.5 Resolution

This means:
1. Either the integration scheme is wrong (use full dynamics, not static)
2. Or the cosmological identification of α requires DELTA_χg also small
3. Or χ doesn't directly feel α (different effective potential)

---

## §3 — Alternative: integrate out σ_m + φ

### 3.1 V_couple sector

QNG has V_couple = (g/2)(σ_ref_m - σ_m)²(1 - cos φ). This couples σ_m
and φ but doesn't directly involve χ.

If χ couples to σ_m via some channel (not in default v8 but possible in
extension), it would inherit:
```
L_eff(χ from σ_m, φ) ⊇ ?
```

But without explicit χ-σ_m coupling, this gives no contribution.

### 3.2 χ_0 = 0 in default v8?

In default v8, the Lagrangian has:
```
L_χ = (1/2 μ_χ)(χ')² - (CHI_DECAY/2)χ² - DELTA_χg · σ_g · χ
```

The minimum of -(CHI_DECAY/2)χ² is at χ=0. So **VEV is naturally zero**
unless extra structure is added.

For χ_0 ≠ 0, need either:
- Higher-order terms: V(χ) with double-well structure
- Coupling to background field that breaks χ → -χ symmetry

---

## §4 — What QNG would need for VEV+fluct to be derivable

### 4.1 Required substrate extension

To naturally have:
```
V(χ) = V_0 + (1/2)m_χ²(χ-χ_0)²
```

with non-zero V_0 and χ_0, we'd need:
```
V_QNG(χ) = a·χ⁴ + b·χ² + c·χ + d
```

with specific signs:
- a > 0 (stable at large χ)
- b can be either sign
- c ≠ 0 (breaks symmetry, gives non-zero χ_0)
- d gives V_0

Specifically: V_QNG(χ) = (λ/4)(χ² - χ_0²)² + (additional shift V_0)

### 4.2 Where would this come from?

In v8, no such quartic χ⁴ term exists. To get it, would need:
- v8 → v9-VEV extension with explicit χ⁴ self-interaction

The COEFFICIENTS of this potential would then determine V_0, m_χ, χ_0.

Specifically, if:
```
V_QNG = (λ/4)(χ² - χ_0²)² + V_0
```

Then:
- V at minimum (χ=±χ_0): V(χ_0) = V_0
- m² at minimum: V''(χ_0) = 2λ·χ_0²

For this to give cosmological values:
- V_0 = Ω_DE × ρ_critical ~ 10⁻¹²² Planck⁴
- m_χ² = 2λ·χ_0² ~ 10⁻¹⁰⁵ Planck² (Lyman-α compatible)

### 4.3 Three parameters → three observables

Three unknowns (λ, χ_0, V_0) → three observations (Ω_DE, m_χ, ?).

The third observation is more subtle — could be:
- Measured χ_0 (via direct dark sector observation, not yet possible)
- Or constraint from Stability Principle (E_vac = 0 implies relation)

If Stability Principle constrains V_0 = 0 strictly, then we lose the DE
mechanism via VEV. So Stability Principle must allow V_0 > 0 in some
sense.

---

## §5 — Honest assessment

### 5.1 What this analysis achieved

- Identified that integrating out σ_g gives WRONG-sign χ mass (tachyonic)
- Confirmed χ_0 = 0 in default v8 (no VEV)
- Identified what extension is needed: explicit V_QNG(χ) with χ⁴ term
- Showed that V_0, m_χ², χ_0 → 3 parameters of V_QNG potential

### 5.2 What this analysis did NOT achieve

- Did NOT derive specific values of V_0, m_χ, χ_0 from substrate
- Did NOT determine why these have small Planck-suppressed values
- Did NOT close the "cosmological identification" gap

The fundamental issue remains: there's no first-principles substrate
derivation of why these small numbers take their specific values.

### 5.3 Comparison with α (Λ identification)

This is the SAME issue as α-Λ in DER-QNG-020:
- α has formal definition in substrate
- Cosmological matching gives α ~ 10⁻¹²⁴ Planck²
- Why this specific value? — open

For χ-DM, exactly analogous:
- m_χ has formal definition in extended substrate
- Cosmological matching gives m_χ² ~ 10⁻¹⁰⁵ Planck²
- Why this specific value? — open

Both reflect the unsolved cosmological hierarchy problem.

---

## §6 — Path forward

### 6.1 To genuinely derive V(χ)

Need to either:

**Option A**: Show that V_QNG(χ) emerges from substrate quantum loops
(Sakharov-induced effective potential). Requires multi-week QFT-on-lattice
calculation.

**Option B**: Postulate the v9-VEV extension with explicit potential
form and three parameters λ, χ_0, V_0. Match to observation, accept
identification.

**Option C**: Find a Stability Principle generalization that fixes the
parameters of V_QNG to specific cosmological values.

### 6.2 Why this is HARD

The cosmological hierarchy problem (why is Λ ~ 10⁻¹²² M_Pl⁴?) is the
deepest unsolved problem in physics. NO theory has solved it from
first principles. QNG inherits this.

What QNG offers UNIQUELY:
- Clear identification of what would need to be derived
- Mathematical framework where derivation could in principle be attempted
- Stability Principle as starting point (already gives Λ_substrate = 0 exact)

The remaining "small numbers" are environmentally identified, not
derived. This is honest scope.

---

## §7 — Status

### 7.1 What this document establishes

✓ V(χ) form needed: V_0 + (1/2)m²(χ-χ_0)² requires χ⁴ extension
✓ Default v8 has no VEV mechanism (χ_0 = 0 naturally)
✓ Integrating out σ_g gives wrong-sign mass (need bare mass)
✓ Three identifications (V_0, m_χ, χ_0) parallel to ΛCDM 3 parameters
✓ Same cosmological hierarchy problem as α↔Λ

### 7.2 What's not derived

✗ Specific values of V_0, m_χ, χ_0 from substrate
✗ Mechanism for why these are small
✗ First-principles V_QNG potential shape

### 7.3 Honest verdict

**V(χ) derivation FAILED in this attempt.**

Default v8 substrate doesn't naturally give:
- Non-zero VEV χ_0
- Constant V_0 contribution
- Cosmological-scale m_χ²

To make VEV+fluctuations a derivation (not identification), need v9-VEV
extension with three new parameters whose values are matched to
observation — same number as ΛCDM Λ + DM mass.

**Net gain over ΛCDM**: framework parsimony (1 sector vs 2). Identifications
remain identifications.

### 7.4 Strategic implication

QNG provides the most parsimonious DE+DM framework, but does NOT solve
the cosmological hierarchy problem. This is consistent with:
- Stability Principle gives Λ_substrate = 0 (locked)
- Observed Λ_eff ≠ 0 requires identification mechanism (open)
- Same pattern for DM mass
- Same pattern for α

**These are environmental parameters at present**.

The deep theoretical advance would be: a Stability-Principle-like
mechanism that selects specific small values for these parameters.
That's a multi-year research program, not a session task.

---

## §8 — Connection to overall theory

After today's findings, QNG cosmology has:

**Locked structural content**:
- Stability Principle → Λ_substrate = 0
- VEV+fluctuations → DE+DM single-field framework
- σ_g sector → intrinsic Λ candidate (file 24)
- χ-fuzzy-DM viable in [2e-21, 1e-19] eV (file 29)
- 1/(16πG) → z/(16π β_g) (file 28)

**Open identifications** (the "small numbers"):
- V_0 ~ 10⁻¹²² Planck⁴ (DE scale)
- m_χ² ~ 10⁻¹⁰⁵ Planck² (DM scale)
- α ~ 10⁻¹²⁴ Planck² (Yukawa screening)

These are **environmental at present, derivation is multi-year program**.

---

## §9 — Status

**Document type**: derivation attempt (negative result)
**Date**: 2026-04-25
**Status**: V(χ) NOT DERIVED — requires v9-VEV extension with 3 input parameters

**Implication**: VEV+fluctuations remains the most parsimonious DE+DM
framework, but the values of V_0, m_χ, χ_0 are observational
identifications, not first-principle derivations.

**Honesty**: this document explicitly identifies the limitation.
QNG inherits cosmological hierarchy problem like all other theories.
What QNG adds: clear framework + structural Λ_substrate = 0.

**Path forward**: postulate v9-VEV extension with 3 free parameters,
accept as input until deeper theory derived. Match to observation.
Treat identical to ΛCDM treatment of Λ + DM mass.
