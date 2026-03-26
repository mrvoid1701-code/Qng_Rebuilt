# DER-BRIDGE-034 — QM→GR Coupling Continuum Limit Probe

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-033 (CPU-051)

---

## Motivation

CPU-051 established the sparse-graph law for the QM→GR coupling:

| N | mean|e_mis| | mean Δratio |
|---|-------------|-------------|
| 8 | 1.037 | −0.147 |
| 16 | 0.259 | −0.043 |
| 32 | 0.159 | −0.018 |

The decay is clearly slowing:
- N=8→16 (×2): amplitude drops ×0.25 (large drop, ~N⁻²)
- N=16→32 (×2): amplitude drops ×0.61 (slower, ~N⁻⁰·⁷)

This suggests either:
(a) **Power-law decay** with flattening exponent → |e_mis| → 0 as N → ∞ (UV law)
(b) **Saturation** → |e_mis| → const > 0 as N → ∞ (physical in continuum)

Testing N=64 adds a critical data point for distinguishing between these scenarios.

---

## Theoretical claim

**Saturation hypothesis**: The N-attenuation of div_J_mis is caused by increasing
divergence cancellation in denser graphs (more neighbors → each ∂C_eff_i is
sourced from more directions, cancellations increase). However, local fluctuations
of mismatch do not vanish as N → ∞ — they become more concentrated on geometrically
unusual nodes. Therefore |e_mis| saturates to a non-zero constant.

**Vanishing hypothesis**: div_J_mis → 0 per node in the dense limit (mean-field
averaging completely cancels local gradient signals). The coupling is purely
a UV / sparse-graph effect.

**Distinguishing test**: If |e_mis(64)| is significantly above the exponential
extrapolation (< 0.065), saturation is favored. If near or below, power-law vanishing
is more consistent.

Extrapolations from N=32:
- Power-law (N⁻²): |e_mis(64)| ≈ 0.040
- Observed decay rate (×0.61 per doubling): |e_mis(64)| ≈ 0.097
- Saturation: |e_mis(64)| ≈ 0.100–0.160

---

## Predictions (pre-registered)

**P1 — Coupling persists at N=64**:
    Δratio_split(N=64,s) < 0 on ≥ 4/5 seeds
    (6-channel still beats 4-channel at N=64)

**P2 — Coupling continues to decrease**:
    mean|e_mis(N=64)| < mean|e_mis(N=32)| = 0.159
    (attenuation hasn't fully stopped)

**P3 — Coupling doesn't vanish**:
    mean|e_mis(N=64)| > 0.050
    (non-trivial coupling persists; above pure noise threshold)

**P4 — Sign stable at N=64**:
    sign(e_mis_ett) consistent across all 4 N values on ≥ 4/5 seeds
    (coupling direction is N-independent)

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Saturation classification (post-test)

Based on |e_mis(N=64)| value:
- > 0.120: **saturation regime** — coupling stabilizing above noise
- 0.050–0.120: **slow decay** — power law exponent < 0.5; continuum limit finite
- < 0.050: **vanishing** — coupling decays to zero, UV law only

---

## Connection to open problems

- **Problem 3 (GR recovery)**: If coupling saturates, it must appear in the
  continuum GR equation; if it vanishes, it's a lattice artifact
- **Problem 4 (QM recovery)**: Same argument for QM continuum limit
- **Problem 5 (back-reaction)**: The back-reaction closure must account for
  the large-N behavior of the QM→GR coupling
