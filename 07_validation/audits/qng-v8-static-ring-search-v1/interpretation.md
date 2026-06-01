# GPU-024d v1 interpretation — cached ring is not a v8 gradient-flow fixed point

**Date**: 2026-04-20
**Script**: `tests/gpu/qng_v8_static_ring_search.py`
**Run log**: `run.log`
**Verdict**: `H_INCONCLUSIVE` (extended in v2)

## Initial force residuals on the cached ring

| channel_f | ||F_sm||_RMS | max|F_sm| | ||F_phi||_RMS | max|F_phi| |
|---|---|---|---|---|
| True | 8.67e-03 | 5.11e-02 | 5.29e-03 | 1.52e-01 |
| False | 8.38e-03 | 4.83e-02 | 5.29e-03 | 1.52e-01 |

A true stationary point would have F ≈ 0. The cached ring therefore is
**not** a v8 steady state — by about three orders of magnitude over
numerical noise.

Notice that turning Channel F off barely changes the residual, because
the ring's phi texture has already been partially washed out during
caching (CPU-080 winding destroyed).

## Relaxation trajectory (channel_f=False, dt_relax=0.05, N=5000)

| iter | M_ring | ||F_sm|| | ||F_phi|| | shape drift |
|---|---|---|---|---|
| 0 | 176.85 | 8.38e-03 | 5.29e-03 | 0 |
| 200 | 206.53 (peak) | 2.02e-03 | 3.63e-03 | 7.7% |
| 1000 | 155.34 | 3.49e-04 | 1.53e-03 | 12.9% |
| 3000 | 53.96 | 5.09e-05 | 6.40e-04 | 14.7% |
| 5000 | 19.09 | 1.33e-05 | 4.28e-04 | 14.9% |

`||F_sm||` drops 630x; `||F_phi||` drops only 12x. M_ring monotonically
decays after the early transient (iter ≤ 200). The trajectory is heading
toward the vacuum but hadn't fully dissolved at N=5000. Extended in v2
to N=30000.

## Mechanism (preliminary, confirmed in v2)

- V_couple = (g/2)(σ_m_ref - σ_m)²(1 - cos φ) has gradient zero iff
  σ_m = σ_m_ref (deficit vanishes) OR φ = 0 (mod 2π). The second root
  is pulled down because V_couple is quadratic in deficit: deep
  deficit regions feel a strong restoring force on φ.
- The residual 1e-4 on ||F_phi|| comes from the φ texture slowly
  relaxing to the Z vacuum. Because the ring has residual deficit,
  φ still feels pressure; as the deficit shrinks, the pressure shrinks
  (the process self-terminates in the trivial vacuum).

## Why it's not v7's equilibrium

v7 Channel F has form `F_phi contribution = 0` (only sigma channel); the
phi texture in v7 is a pure Goldstone mode of a U(1) coset, metastable
under diffusion alone. v8 V_couple introduces explicit U(1)→Z
breaking, giving phi a potential whose gradient drives it to 0.

## What v1 decided and what remained open

**Decided by v1**:
- Cached ring is not a v8 fixed point (force residuals ~1e-2).
- Gradient flow takes M_ring monotonically down; no plateau by iter 5000.

**Open after v1** (resolved in v2):
- Does M_ring reach 0 (full vacuum) or stop at some nontrivial
  residual? Answered: full vacuum (M→0.05 at iter 18000 with V_couple,
  M→0.10 at iter 30000 without V_couple).
- Is V_couple specifically the culprit? Answered: no. V_couple-free
  variant ALSO dissolves to vacuum.

## Contextual note

The hadron identification in DER-QNG-038 (R=4 → N(938) etc.) was
derived from Phase-3 conservative dynamics on this cached ring, where
V_couple was not active (CPU-074/075 used v7 conservative, not v8
symplectic). Those mass numbers remain valid as statements about v7
ring properties. They do not transfer automatically to v8: under v8,
the same cached state is a basin flank, not a rest-frame soliton, and
its "mass" is a Noether charge of a dynamic pattern — not a
rest-energy via E=m c².
