# 07. Predictions: Structural Invariants

These are **algebraic invariants** that follow directly from QNG's
substrate-parameter derivations. They are UNIQUE to QNG — Standard
Model + GR cannot make these predictions because they treat c, G, ℏ
as independent inputs.

## The three invariants

### Invariant 1: ℏ·c independent of (μ_φ, z)

```
ℏ·c = β_φ / C_cubic
```

**Derivation**:
```
ℏ·c = √(β_φ·μ_φ·z)/C × √(β_φ/(z·μ_φ))
    = √(β_φ²)/C
    = β_φ / C_cubic
```

**Physical content**: The product `ℏ·c` depends ONLY on β_φ and lattice
geometry. Independent of μ_φ (phase inertia) and z (coordination).

**Verification numerical** (CPU-144):
- ℏ_QNG · c_QNG = 0.2326 × 0.108 = 0.02512
- β_φ / C_cubic = 0.06 / 2.388 = 0.02513
- Match: 0.04% (rounding)

### Invariant 2: ℏ/c independent of β_φ

```
ℏ/c = z · μ_φ / C_cubic
```

**Derivation**:
```
ℏ/c = √(β·μ·z)/C / √(β/(z·μ)) = √(z²·μ²)/C = z·μ_φ/C_cubic
```

**Physical content**: The ratio `ℏ/c` depends ONLY on z, μ_φ, and lattice
geometry. Independent of β_φ (coupling strength).

**Numerical**:
- ℏ_QNG / c_QNG = 0.2326 / 0.108 = 2.153
- z · μ_φ / C_cubic = 6 × 0.857 / 2.388 = 2.153 ✓

### Invariant 3: G/c² independent of z

```
G/c² = β_g · μ_φ / β_φ
```

**Derivation**:
```
G/c² = (β_g/z) / (β_φ/(z·μ_φ)) = β_g·μ_φ/β_φ
```

**Physical content**: Schwarzschild radius `r_s = 2GM/c²` is invariant
under z-changes (connectivity variations).

**Numerical**:
- G_QNG / c_QNG² = 0.0583 / 0.01167 = 5.0
- β_g · μ_φ / β_φ = 0.35 × 0.857 / 0.06 = 5.0 ✓

## Predictions from these invariants

### Prediction 1: ℏ·c invariant under thermal substrate variations

Hypothesis: in early universe (T → T_Planck), substrate inertia μ_φ
might be temperature-dependent: `μ_φ_eff(T) = μ_φ · f(T/T_P)`.

Under this:
```
c_eff(T) = c_0 · 1/√f(T/T_P)
ℏ_eff(T) = ℏ_0 · √f(T/T_P)
ℏ·c stays CONSTANT
```

**Observable signature**: any future detection of ℏ-variation should
show counter-correlated c-variation such that the product stays constant.

In standard physics: c and ℏ are independent — no such correlation
predicted.

### Prediction 2: ℏ/c invariant under coupling variations

If β_φ effectively varied (e.g., near horizons where coupling strength
might run), c and ℏ would both change — but in such a way that ℏ/c
stays constant.

```
β_eff > β_0  →  c_eff > c_0,  ℏ_eff > ℏ_0,  ℏ/c stays
```

### Prediction 3: G/c² invariant under z (connectivity)

If effective dimension of substrate varied (4D → 3D phase transitions
speculated in some approaches), z would change but G/c² would stay.

**Schwarzschild radius prediction**: r_s = 2GM/c² remains invariant
under such transitions. Observable in BH dynamics if such phenomena exist.

## Why these are unique

Standard Model + General Relativity:
- c, G, ℏ are independent constants
- No structural relations between them
- Each has independent error bars in measurements

QNG:
- c, G, ℏ all from same 4 substrate parameters
- 3 specific algebraic invariants follow
- Predicts CORRELATIONS between observed values

These invariants are algebraic identities, not test results — they hold
exactly by construction. The PREDICTION is that **if any of c, G, ℏ
ever varies in any regime, the others co-vary in specifically these
ways**.

## Tests in principle

| Variation source | What changes | What stays |
|---|---|---|
| μ_φ (T-dependent inertia) | c, ℏ | ℏ·c, G |
| β_φ (coupling running) | c, ℏ | ℏ/c, G |
| z (connectivity change) | c, G | G/c² |
| β_g | G | c, ℏ, ℏ·c, ℏ/c |

## Observational status

- Variations of c, ℏ, G have been searched: current bounds
  `|Δα/α| < 10⁻⁵` over cosmic time (most stringent on combinations).
- All bounds CONSISTENT with QNG invariants — no observed variations
  yet.
- If ANY variation is observed, QNG predicts the SPECIFIC pattern
  (Predictions 1-3).

## Summary

QNG predicts three **algebraic invariants** between c, G, ℏ:

1. ℏ·c = β_φ / C_cubic
2. ℏ/c = z·μ_φ / C_cubic
3. G/c² = β_g·μ_φ / β_φ

These follow from substrate-derivation. They constrain how c, G, ℏ can
co-vary if substrate parameters effectively change. **No other framework
makes these predictions.**

## References

- DER-QNG-083 (predictions from ℏ derivation)
- CPU-144 (numerical extraction of invariants)
- Original: `QNG-Theory Release-01/04_qng_pure/qng-predictions-from-hbar-v1.md`
