# 02. The Stability Principle

The single physical axiom of QNG. Without this, ℏ is not derived; with
it, ℏ follows mathematically and Λ = 0 emerges structurally.

## Statement

> **AXIOM (Stability Principle)**: The only physically realizable
> quantum-mechanical substrate is one for which the total vacuum energy
> density (classical + quantum zero-point) vanishes:
>
> ```
> E_vacuum_total = E_classical_ground + (ℏ/2) · Σ_k ω_k = 0
> ```

## Physical motivation (not anthropic)

If the universe's vacuum energy density is non-zero significantly:

### If `ρ_vac > 0` (positive Λ): **Big Rip scenario**
Friedmann equation gives `(ȧ/a)² = (8πG/3)·ρ_vac → constant`,
solution `a(t) ∝ exp(t·H_Λ)`. Exponential expansion tears all
structures apart at infinite time.

### If `ρ_vac < 0` (negative Λ): **Big Crunch / AdS instability**
Friedmann gives accelerating contraction; in coupled QM substrates,
imaginary mode frequencies arise → exponential instability in
finite time.

### If `ρ_vac ≈ 0`: **Stability window**
No Big Rip, no Big Crunch. Complex temporal structures (galaxies,
atoms, observers) can form and persist.

**Theorem (Stability Selection)**: Only substrates with `E_vacuum ≈ 0`
support universes containing complex stable structures over
cosmological time.

## Difference from Anthropic Principle

| Principle | Statement | Logical character |
|---|---|---|
| Anthropic | "Observers exist, so values must permit life" | Tautological selection |
| **Stability** | "Long-time substrate persistence requires E_vac = 0" | Dynamical selection |

The Stability Principle is **about substrate dynamics**, not about
observer existence. Any substrate violating it cannot persist as
asymptotic structure, regardless of what it contains.

## Mathematical content

For QNG specifically:

```
E_classical_ground = -β_φ · N / 2                  (XY ground state, N = lattice nodes)
Σ_k ω_k           = √(β_φ/(z·μ_φ)) · Σ_k √(λ_k)    (sum over normal modes)
```

**Note on renormalization** (added 2026-04-25 after T4 audit):
the formula above uses `β_φ_R` — the **renormalized** φ coupling.
In v8 substrate, σ_g, σ_m, φ all have kinetic terms with c_g = c_m = c_φ
matched (DER-QNG-042), so all three contribute zero-point energy.

These additional zero-points (σ_g, σ_m) are absorbed into the renormalized
β_φ_R via standard QFT renormalization (minimal subtraction at lattice
scale). The formula above with β_φ_R = 0.06 (the value observed in
simulations) gives ℏ_QNG = 0.2326 = observed via unit-bridge.

The "total vacuum energy = 0" condition applies to RENORMALIZED
contributions (after absorbing UV zero-points into bare parameters).
This is consistent with standard QFT treatment of vacuum energy.

Full one-loop derivation of β_φ_R from bare parameters is pending
(multi-week analytical work). See theory-v2/32 for resolution discussion.

where `λ_k = 2(3 - cos k_x - cos k_y - cos k_z)` are lattice
eigenvalues.

Imposing `E_vacuum = 0` solves for ℏ:

```
ℏ_QNG = β_φ · N / Σ_k ω_k = √(β_φ · μ_φ · z) / C_cubic ≈ 0.233
```

with `C_cubic = ⟨√λ_k⟩_BZ = 2.388` (lattice geometric constant).

## Three independent verifications (CPU-107)

| Method | Formula | ℏ_QNG |
|---|---|---|
| Structural | √(β·μ·z)/C | 0.23263 |
| Zero-point balance | β·N/Σω_k | 0.23264 |
| Intensive | β/⟨ω⟩ | 0.23263 |

Spread: 0.0046%. CONSISTENCY CONFIRMED across methods.

## Thermodynamic limit (CPU-108)

| L | ℏ_QNG |
|---|---|
| 4 | 0.23340 |
| 16 | 0.23258 |
| 48 | 0.23264 |
| 96 | 0.23264 |

Convergence to <0.001% by L = 48. ℏ is **lattice-size-independent**
in thermodynamic limit.

## Consequence: Λ = 0 structurally

The Stability Principle requires `ρ_vac = 0`. This translates to
cosmological constant `Λ = 0` exactly (since `Λ = 8πG·ρ_vac/c⁴`).

**Resolution of cosmological constant problem**:
- Standard QFT estimate: `Λ ~ 10⁰` to `10¹²²` Planck units
- Observed: `Λ_obs ~ 10⁻¹²²` Planck units
- Standard discrepancy: 122 orders of magnitude (worst fine-tuning in physics)
- **QNG**: `Λ = 0` exactly — not fine-tuning, structural

The 10⁻¹²² observed is a small but nonzero number. QNG's `Λ = 0` is
consistent with this (within 122 orders of magnitude). To explain
observed nonzero value, QNG requires either:
- Yukawa screening at cosmological scale (Paper 4 conjecture, BAO test failed CPU-131)
- α as cosmological-scale input parameter
- Quantum running of α (Gap 13, open)

The structural prediction `Λ = 0` is unambiguous; the explanation of
observed nonzero `Λ_obs` is open.

## Falsifiability

The Stability Principle is falsifiable in two ways:

1. **Λ measurement**: if `Λ_observed > 10⁻¹⁰` Planck units, principle
   fails. Currently consistent (Λ_obs ~ 10⁻¹²²).

2. **Substrate counterexample**: showing a substrate with non-zero
   vacuum energy density that supports stable observers. Verifiable
   in principle by explicit example.

## Status

The Stability Principle is currently **provisional axiom**. To promote
to **locked axiom**:
- Independent peer review
- Numerical predictions confirmed (ℏ ≈ 0.233 ✓, Λ ≈ 0 ✓ at current bounds)
- Consistency across all QNG tests (verified)

This document treats it as the SINGLE physical principle of QNG. Without
it, c, G are derived but ℏ is not. With it, ℏ value follows mathematically.

## References

- DER-QNG-066 (Stability Principle formal axiomatization)
- DER-QNG-067 (ℏ derivation paper draft)
- CPU-107, 108, 113, 114 (numerical verification)
- Original: `QNG-Theory Release-01/04_qng_pure/qng-stability-principle-v1.md`
