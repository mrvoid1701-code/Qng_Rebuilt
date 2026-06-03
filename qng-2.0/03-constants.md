# QNG 2.0 / 03 — the CONSTANTS

Type: `derivation`
Track: `qng-2.0`
Author: C.D Gabriel
Date: 2026-06-03

## Inputs

- [02-primitives.md](02-primitives.md) — PRIM-1…4 (causal order, field, density ρ, action S)
- `theory-test-1` rung 4 — Λ ≈ 1/√V from Poisson counting

## The economy: 2 inputs, not 4

QNG 2.0 reduces the fundamental constants to **two inputs**, with the rest structural or
predicted:

- **c — structural (not a free input).** The causal order `≺` IS the light-cone structure;
  the maximum signal speed is intrinsic to it. In natural units `c = 1`; dimensionfully it
  is the conversion between the order's timelike and spacelike reach, which for an isotropic
  (Lorentz-invariant) Poisson order is fixed. So `c` is the order's null structure, not a
  dial. [STRUCTURAL]
- **ħ — input #1 (the action quantum).** In `Z = Σ_C ∫Dψ e^{iS/ħ}`, `ħ` is the unit that
  converts the (dimensionless, counting-based) action `S` to physical action. One input. [INPUT]
- **ℓ_P — input #2 (the discreteness length).** PRIM-3: one event per `V_0 = ℓ_P⁴`. The
  single length scale. [INPUT]
- **G — DERIVED.** From `ℓ_P = √(ħG/c³)` (the Planck length is the discreteness scale):
  `G = ℓ_P² c³ / ħ`. Given the two inputs (ℓ_P, ħ) and structural c, **G is not
  independent**. [DERIVED from the two inputs]
- **Λ — DERIVED / PREDICTED.** `Λ ≈ ±1/√V` (Planck units) from the Poisson number–volume
  fluctuation (tt1 rung 4) → `Λ ~ 10⁻¹²²`, matching observation. NOT an input. [PREDICTED]

## Net

Standard physics takes `{c, G, ħ}` as three independent dimensionful constants and `Λ` as
a fourth (fine-tuned) input. **QNG 2.0 takes only `{ℓ_P, ħ}`** — `c` is the order's
structure, `G = ℓ_P²c³/ħ` follows, and `Λ ~ 1/√V` is predicted. Four constants → two
inputs + one prediction.

## Honest status

- The PARAMETER ECONOMY (3 dimensionful constants collapse to 2 inputs via `G=ℓ_P²c³/ħ`)
  is real but partly DEFINITIONAL: `ℓ_P ≡ √(ħG/c³)` is the definition of the Planck
  length, so this says "QNG 2.0's one length scale IS the Planck length" — a structural
  identification, not an independent prediction of G's numerical value. Labelled [STRUCTURAL].
- The genuinely PREDICTED constant is **Λ** (≈1/√V), which QNG 1.0 could not give
  (it forced Λ=0 + a separate holographic V_0, Gap 5). This is QNG 2.0's constants win.
- Still OPEN: deriving the dimensionless couplings (α_fine, mass ratios, the field mass m
  in PRIM-4) — same open status as in QNG 1.0 and the Standard Model. Not claimed.

See `tests/qng2_constants_economy.py` for the closure check + parameter count.
