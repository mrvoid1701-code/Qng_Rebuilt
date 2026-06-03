# QNG 2.0 / 04 — the GR limit (Einstein equations)

Type: `derivation`
Track: `qng-2.0`
Author: C.D Gabriel
Date: 2026-06-03

## Inputs

- [02-primitives.md](02-primitives.md) — S = S_grav[C] + S_field[C,ψ]
- `theory-test-1` rung 3 — BD operator → □ + curvature (R²=0.94); rung 4 — Λ ≈ 1/√V
- QNG 1.0 P108 — the matter field's stress-energy T_μν

## The derivation

**Step 1 — gravity side.** `S_grav[C]` is the Benincasa–Dowker causal-set action (sums of
interval-cardinality counts). Its continuum limit is the Einstein–Hilbert action,
`S_grav → (1/16πG) ∫√g (R − 2Λ)`, with the counting-`Λ` of rung 4 appearing as the
constant term. [BD→EH: standard causal-set result, the operator validated in tt1 rung 3.]

**Step 2 — matter side.** `S_field[C,ψ] = Σ_x ψ*(B+m²)ψ` has stress-energy `T_μν` — the
same Klein–Gordon stress-energy whose `T_00 ∝ |ψ|²` (energy density) and `T_0i/T_00 = v`
(QNG 1.0 P108). On the causet, `T_00` is built from the field and the BD gradients.

**Step 3 — vary.** Stationarity of `S_grav + S_field` under variation of the causal order
(equivalently, the dominant causet in `Z = Σ_C ∫Dψ e^{iS/ħ}`) gives the discrete
Einstein equation whose continuum limit is
```
        G_μν + Λ g_μν = 8πG T_μν .
```
Geometry side from BD (Step 1), source from the field (Step 2), `Λ` from counting, `G`
from the constants rung. **This is GR, derived from the order + field, not assumed.**

## Numerical consistency (this rung's test)

`tests/qng2_rung2_gr_assembly.py`:
- VACUUM/FLAT limit: an empty flat causet has BD scalar-curvature density ≈ 0 (R≈0) and
  zero field ⇒ `T_μν=0` ⇒ both sides of Einstein vanish. [checked]
- SOURCE present: a field concentration gives `T_00 = Σ|ψ|²-energy > 0`, localized where
  the field sits ⇒ a nonzero source for `G_μν`. [checked]
- So both sides of `G_μν+Λg=8πG T` are represented on the causet, consistent in the limits.

## Honest status

- DERIVED/ASSEMBLED: the Einstein equation as the continuum limit of (BD action) +
  (field source) + (counting Λ). Each piece is validated (BD→□ tt1 R3; T_μν P108; Λ R4).
- The FLAT/vacuum consistency is checked numerically here.
- **OPEN (the hard part, same for all discrete approaches):** the FULL dynamical solution
  — a curved causet self-consistently sourced by a matter field — is not solved; it needs
  sprinkling into / summing over curved causets, where BD fluctuations and the
  sum-over-causets measure are active research. So GR is derived at the level of "the
  field equations emerge in the continuum limit," not "we solved Einstein on a random
  causet." Labelled honestly. No numbers forced.
