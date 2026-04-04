# QNG Phi Dephasing v1

Type: `derivation`
ID: `DER-QNG-017`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Derive the phi coherence decay function `C(t)` induced by Channel E (`ε·χ_i` in the
phi channel, v4 law) acting on a spatially non-uniform chi background. Extract the
dephasing time `T₂*` as a function of the chi distribution. This gives the first
quantitative constraint on `ε`: matching `T₂*` to an observed decoherence time.

## Inputs

- [qng-native-update-law-v4.md](qng-native-update-law-v4.md)
- [qng-chi-ontology-v1.md](qng-chi-ontology-v1.md)
- [qng-generation-order-v1.md](qng-generation-order-v1.md)

---

## Section 1: Setup

Consider N nodes on a graph with frozen chi background `{χ_i}` (no sigma/chi updates).
Initialize all phi values to zero: `φ_i(0) = 0` (perfect phase coherence).

Run Channel E only (set `φ_rel = 0` to isolate the dephasing mechanism from smoothing):

```
φ_i(t+1) = wrap(φ_i(t) + ε·χ_i)
```

Since `φ_rel = 0`, there is no inter-node coupling. Each node evolves independently:

```
φ_i(t) = wrap(ε·χ_i·t)
```

For small `|ε·χ_i·t|` (before wrap activates):

```
φ_i(t) ≈ ε·χ_i·t
```

---

## Section 2: Phase coherence function

Define the global phase coherence (order parameter):

```
C(t) = |(1/N) · Σ_i exp(i·φ_i(t))|
     = |(1/N) · Σ_i exp(i·ε·χ_i·t)|
```

This is the absolute value of the **empirical characteristic function** of the chi
distribution evaluated at argument `s = ε·t`.

### Exact form

```
C(t) = |⟨exp(i·ε·χ·t)⟩|
```

where the average is over the empirical chi distribution of N nodes.

This is model-free: it requires no assumption on the chi distribution. Given the
numerical chi profile `{χ_i}`, `C(t)` can be computed exactly for any `t`.

---

## Section 3: Gaussian approximation

When the chi profile is approximately Gaussian with mean `μ_χ = ⟨χ⟩` and variance
`σ_χ² = Var(χ)`, the characteristic function has a closed form:

```
⟨exp(i·s·χ)⟩ = exp(i·s·μ_χ - s²·σ_χ²/2)
```

Substituting `s = ε·t`:

```
C(t) = |exp(i·ε·μ_χ·t - ε²·σ_χ²·t²/2)|
     = exp(−ε²·σ_χ²·t²/2)
```

The imaginary exponential has modulus 1 and contributes only to the phase of C(t),
not its magnitude. The magnitude decays as a Gaussian in t.

**Dephasing time T₂*:**

Define T₂* as the time at which C(t) = C(0)/e = 1/e:

```
exp(−ε²·σ_χ²·(T₂*)²/2) = 1/e
ε²·σ_χ²·(T₂*)²/2 = 1
T₂* = √2 / (ε·σ_χ)
```

**Constraint formula for ε:**

```
ε = √2 / (T₂* · σ_χ)
```

Given an observed dephasing time `T₂*` and the substrate chi spread `σ_χ`, `ε` is
determined uniquely.

---

## Section 4: Regime of validity

The Gaussian approximation holds when the chi profile is approximately symmetric and
unimodal. The quasi-static source profile (QNG-CPU-030, 031) is exponential — skewed
toward zero. For the exponential profile, the Gaussian approximation underestimates
the tail contribution.

**Correction for exponential profile:**

For `χ_i ~ Exponential(λ)` with mean `μ = 1/λ` and variance `σ² = 1/λ²`:

```
⟨exp(i·s·χ)⟩ = 1/(1 - i·s/λ) = 1/(1 - i·s·μ)
|⟨exp(i·s·χ)⟩| = 1/√(1 + s²·μ²)
```

This gives a Lorentzian decay rather than Gaussian. The 1/e time for Lorentzian:

```
T₂*_Lorentz = 1/(ε·μ_χ)
```

In practice the chi profile (from v3 equilibration) is a mixture: large bulk
population at χ ≈ 0 (most nodes) plus a non-zero elevated region near the source.
The exact C(t) must be computed numerically from the actual chi values — the Gaussian
or Lorentzian formulae serve as limiting cases for calibration.

---

## Section 5: Effect of phi_rel smoothing

When `φ_rel > 0`, the phi channel also has the relational term:

```
φ_i(t+1) = wrap(φ_i(t) + φ_rel·angle_diff(φ̄_i, φ_i) + ε·χ_i)
```

The relational term tends to synchronize phi across neighbors, counteracting the
dephasing from the chi term. The net effect depends on which dominates:

- **Dephasing rate**: `ε²·σ_χ²` (from Channel E)
- **Synchronization rate**: `φ_rel · (1 - cos(2π/N))` for the slowest mode on a ring

When dephasing rate > synchronization rate, coherence decays. When the reverse holds,
phi synchronizes before dephasing can accumulate.

For the test (Section 6 below), `φ_rel = 0` is used to isolate Channel E. The full
v4 dynamics (φ_rel > 0) have longer effective T₂* due to synchronization competition.

---

## Section 6: Testable prediction (QNG-CPU-034)

**Setup:**
- v3 equilibration with δ=0.20 → chi background with σ_χ measured from `{χ_i}`
- Initialize φ_i = 0 (perfect coherence, C(0) = 1)
- Run phi evolution with Channel E only (φ_rel = 0), 500 steps

**Prediction:**
```
C(t) decays from 1 toward 0.
T₂*_meas / T₂*_pred ∈ [0.5, 2.0]
where T₂*_pred = √2 / (ε·σ_χ)
```

**Physical interpretation:** The chi profile imprinted by the gravitational sector
(sigma deficit) directly sets the decoherence timescale in the quantum-phase sector.
The coupling constant ε converts gravitational load into decoherence rate:

```
Γ_deph = 1/T₂* = ε·σ_χ / √2
```

This is the QNG prediction for the dephasing rate in terms of substrate variables.
Matching to observed T₂* in atomic or molecular systems gives ε in substrate units.

---

## Section 7: Constraint formula — summary

```
ε = √2 / (T₂* · σ_χ)
```

where:
- `T₂*` is the measured dephasing time (in substrate steps)
- `σ_χ = √Var(χ)` is the chi spread across the relevant spatial region

Once ε is fixed from one measurement, all other chi-tension effects (frequency shift,
mode broadening) are predictions with no remaining free parameters in Channel E.

---

## Cross-references

- v4 update law: `DER-QNG-016` (`qng-native-update-law-v4.md`)
- P1 confirmation: `QNG-CPU-033`
- Chi ontology: `NOTE-QNG-009` (`qng-chi-ontology-v1.md`)
- Test: `QNG-CPU-034` (`07_validation/prereg/QNG-CPU-034.md`)
