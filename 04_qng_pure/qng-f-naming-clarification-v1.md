# QNG Conversion Factor f — Naming Clarification v1

Type: `note`
ID: `NOTE-QNG-015`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Resolve the apparent 4.4× inconsistency in the conversion factor f between
DER-QNG-029 and CLAUDE.md. The Newton audit (2026-04-06) flagged this as a
potential internal inconsistency in the unit triad (a, τ, m_u).

---

## The Apparent Inconsistency

**DER-QNG-029 §7 defines:**
```
ΔV²(r) = f × C_K(r, λ)   where  f ≡ ρ₀ × A_VORTEX
f_empirical (from OBS-002) ≈ 9700 (km/s)²/lu
ρ₀_empirical = f / A_VORTEX = 9700 / 0.225 ≈ 43000 (km/s)²/lu
```

**CLAUDE.md (project-level memory) states:**
```
"Empirical f≈43000 (km/s)²/lu from OBS-002"
```

**Ratio:** 43000 / 9700 ≈ 4.43 ≈ 1 / A_VORTEX = 1 / 0.225 = 4.44

---

## Diagnosis: Naming Conflict, Not Physical Inconsistency

The two documents use the symbol "f" for two different quantities:

| Document | Symbol "f" | Physical quantity |
|----------|-----------|-----------------|
| DER-QNG-029 | f = ρ₀ × A_VORTEX | direct chi-field → velocity² conversion |
| CLAUDE.md | f = ρ₀ | substrate energy density in velocity² units |

The ratio 4.44× = 1/A_VORTEX = 1/0.225 is exactly the sigma deficit amplitude
of the vortex ring from QNG-CPU-043.

**There is no physical inconsistency.** The two derivation paths agree:
- DER-QNG-029: f = ρ₀ × A_VORTEX → f = 9700 (km/s)²/lu; ρ₀ = 43000 (km/s)²/lu
- CLAUDE.md: called ρ₀ = 43000 (km/s)²/lu "f" (conflating f with ρ₀)

The unit triad (a, τ, m_u) has only ONE empirical constraint from OBS-002, not two.
The 4.4× ratio is not a constraint conflict — it is the definition of A_VORTEX.

---

## Canonical Notation (adopted from this note)

To prevent future confusion, adopt the following convention throughout all QNG documents:

```
ρ₀          [substrate energy density, (km/s)²/lu empirically]
A_VORTEX    [sigma deficit amplitude = 0.225, from QNG-CPU-043]
f ≡ ρ₀ × A_VORTEX   [direct OBS conversion factor]

Numerical values (empirical, not derived):
  ρ₀ ≈ 43000 (km/s)²/lu    (from OBS-002, using f/A_VORTEX)
  f  ≈ 9700  (km/s)²/lu    (direct from OBS-002 residuals)
```

**CLAUDE.md should be updated** to replace "f≈43000" with "ρ₀≈43000".

---

## What Remains Genuinely Open

The Newton audit correctly identified that the unit system has ONE empirical constraint
from OBS-002 but THREE unknowns (a, τ, m_u). The situation:

| Constraint | Source | Status |
|-----------|--------|--------|
| C1: G matching | DER-QNG-019 | ✓ gives m_u × τ² = 8.74×10⁻¹¹ × a³ |
| C2: lattice scale | C2b (Hubble) or C2c (OBS-002) | open — two candidate choices |
| C3: speed of light | v6 Channel G (not yet measured) | open |

Until C2 and C3 are closed from theory (not observation), ρ₀ remains empirical.
The 4.4× was NOT a sign of hidden conflict — there is only one independent OBS-002
measurement, just mislabeled in different documents.

---

## Action

1. Update CLAUDE.md: replace "f≈43000 (km/s)²/lu" with "ρ₀≈43000 (km/s)²/lu"
2. Update DER-QNG-029: add a cross-reference to this note in §7
3. No physical derivations need revision — the underlying numbers are consistent

---

## Cross-references

- DER-QNG-029: physical scale derivation (defines f correctly as ρ₀ × A_VORTEX)
- QNG-OBS-002: source of empirical f measurement
- QNG-CPU-043: source of A_VORTEX = 0.225
