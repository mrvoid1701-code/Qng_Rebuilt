# QNG QM Complex Amplitude Proxy v1

Type: `derivation`
ID: `DER-BRIDGE-023`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-GOV-005` (phi identification), `DER-GOV-004` (sigma identification)

## Objective

Construct the first complex amplitude from native QNG fields and test whether
it admits a continuity-like current balance at proxy level.

## Motivation

QNG-CPU-040 established that:
- `phi` is a near-perfect U(1) synchronization field
- `C_eff` is the coherence amplitude estimator

These two fields are the natural ingredients of a complex amplitude. If we can
write `ψ_i = C_eff_i * exp(i * phi_i)`, then:
- `ρ_i = |ψ_i|² = C_eff_i²` is a positive-definite density
- `J_{i→j} = Im(ψ_i* · ψ_j) = C_eff_i * C_eff_j * sin(phi_j - phi_i)`
  is a current on each graph edge

The question is whether ∂_t ρ + div(J) ≈ 0 holds at proxy level.

## Construction

### Complex amplitude

```
ψ_i = C_eff_i * (cos(phi_i) + i * sin(phi_i))
```

where `C_eff_i` comes from `field_extract(state, history)` and `phi_i = state.phi[i]`.

### Density

```
ρ_i = |ψ_i|² = C_eff_i²
```

### Graph edge current

For each neighbor pair (i, j):

```
J_{i→j} = Im(ψ_i* · ψ_j)
         = C_eff_i * C_eff_j * sin(phi_j - phi_i)
```

### Divergence of current

```
div(J)_i = sum_{j ∈ neighbors(i)} J_{i→j}
          = C_eff_i * sum_{j ∈ neighbors(i)} C_eff_j * sin(phi_j - phi_i)
```

### Continuity balance

The continuity equation would require:

```
∂_t ρ_i + div(J)_i = 0   (source-free)
```

or

```
∂_t ρ_i + div(J)_i = S_i  (source-augmented)
```

At proxy level, we test the correlational form:

```
corr(Δρ, -div(J)) > 0
```

which asks whether the current points in the direction of density decrease.

## Claims

### Claim A: ψ is well-defined

Prediction: SUPPORTED (trivially)

`C_eff_i ∈ [0, 1]` always; `phi_i ∈ [-π, π]` always. So ψ is a valid complex
number on every node at every step.

### Claim B: ρ is a density-like object

Prediction: SUPPORTED

`ρ_i = C_eff_i² ≥ 0` with `sum_i ρ_i > 0`. The density is positive definite
and normalizable.

### Claim C: corr(Δρ, -div(J)) > 0 (current has correct direction)

Prediction: OPEN — to be resolved by QNG-CPU-041

Argument: If phi is synchronized (sin(phi_j - phi_i) ≈ 0 everywhere), the
current vanishes and the correlation is undefined. But history introduces local
phase gradients (anti-ordering effect from QNG-CPU-040), so div(J) is nonzero.
Whether its sign matches -Δρ is an open question.

### Claim D: history improves the continuity balance

Prediction: OPEN

Argument: History increases phase diversity (anti-ordering), which increases
|div(J)|. Whether this improves the corr(Δρ, -div(J)) balance or worsens it
depends on the phase gradient structure.

## Physical interpretation

If Claim C is supported, this would be the first proxy-level evidence that:

- The native QNG substrate supports a density-current pair (ρ, J) derived from
  the complex amplitude ψ = C_eff * exp(i*phi)
- The quantum current J is not zero (phi is not perfectly uniform)
- The current's direction is statistically aligned with density change

This does NOT imply full continuity closure (the residual may be large), but it
would place the complex amplitude on the same footing as the other proxy results:
a structured, testable QM-like object emerging from the native fields.

## Validation

Test: `QNG-CPU-041` — `qng_complex_amplitude_proxy_reference.py`
Decision: PASS

Pass criteria:
- P1: ψ well-defined on all nodes — PASS (trivial)
- P2: corr(Δρ, -div(J)) > 0 on ≥3/5 seeds — PASS (4/5 seeds positive)
- P3: at least one strong signal corr > 0.5 — PASS (seed 137: corr = 0.756)
- P4: history amplifies |J| on ≥3/5 seeds — PASS (5/5, ratio 3–8x)

Key documented finding:
- Scale mismatch: |J| >> |Δρ| by ~100x on all seeds
- Full continuity balance is WEAK (as expected from prior work)
- Directional continuity is SUPPORTED: current points in correct direction
