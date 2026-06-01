# E4 RESULT — mass is the volume charge, not a 1/R resonance

Type: `evidence`
Status: `RUN COMPLETE 2026-06-01 — verdict MASS_IS_VOLUME_CHARGE`
Author: `C.D Gabriel`
Probe: `demo-theory/tests/e4_mass_resonance_probe.py`
Artifact: `07_validation/audits/demo-e4-mass-resonance-v1/report.json`
Gates: the page-05 conjecture `m = ℏω₀/c²` (mass as a cavity resonance)

---

## What E4 asked

Page `05` conjectured mass is a **trapped frequency**: `m = ℏω₀/c²` with the
toroidal cavity fundamental `ω₁ = c_φ/R`. The decisive test: for rings
`R = 3,4,5`, does the baryon ladder `N(938), Δ(1232)` track the **volume charge**
`Σσ_m`, the **frequency** `ω₁`, or their **product**?

## What E4 found (canonical M_ring + cavity ω∼1/R)

Using the established canonical charges (CPU-074: `M_ring` = 474.15, 728.92,
954.88) and the cavity conjecture `ω₁ = c_φ/R`:

| Hypothesis | R5/R4 ratio | PDG target Δ/N | match? |
|---|---|---|---|
| **H_volume** `m ∝ Σσ_m` | **1.310** | 1.313 | **YES (0.2%)** |
| H_freq `m ∝ ω₁ ∝ 1/R` | 0.800 | 1.313 | no (falling) |
| H_product `m ∝ Σσ_m·ω₁` | 1.048 | 1.313 | no |

## Verdict: **MASS_IS_VOLUME_CHARGE**

> The baryon ladder is reproduced by the **conserved volume / topological charge
> `Σσ_m` alone** (0.2% on Δ/N). Multiplying by a `1/R` cavity frequency **breaks**
> the match. The page-05 "mass = `1/R` resonance" conjecture is **DISFAVORED**.
>
> **Division of labor (the whole thread's spine) holds:** frequency lives on the
> **edges** and sets **light** (E5/E7); the node **volume charge** sets **mass**.

## Honest caveats (important)

This result rests on the **canonical** M_ring values, not on this probe's
self-contained ring simulation, which was **too crude to trust**:

- Its Channel-F carving depleted `σ_m` globally (deficit ≈ 2300–2700), **not**
  reproducing the canonical core charge (≈ 474–955).
- Its measured `ω₁ = 0.134` was **R-independent** — a global `φ` mode, not the
  toroidal cavity mode. The poloidal-ring + crude carve is not a faithful v8
  ring.

So the *quantitative* conclusion is carried by canonical data + the cavity
`ω∼1/R` assumption, **not** by a direct `ω₁(R)` measurement.

**The one loophole, stated honestly:** the `1/R` form is what is excluded. If a
faithful measurement found `ω₁` to be **R-independent** (a fixed core-scale
frequency, not the ring-circumference mode), then `product ≡ volume` and the
ladder match would survive — i.e. "resonance" would be *compatible* as a
constant dressing, just not as a `1/R` cavity. Settling this needs the real v8
ring infrastructure (GPU ring cache), flagged as follow-up **E4-faithful**.

## Caveats inherited from the main theory

- `M_ring` is **lattice-dependent** (Gap 14): matches at `L=20`, drifts ~7% at
  `L=28`. So even "mass = volume charge" is not yet a clean rest mass.
- v8 rings are **dynamic patterns, not static solitons** (`DER-QNG-047`).
- The MeV scale itself is **Gap 13** (Planck→MeV is 22 orders, unexplained).

E4 therefore confirms the *scaling* picture (mass ∝ volume charge, not 1/R
frequency) without claiming an absolute mass.

## Status updates

- `05-mass-as-resonance.md`: conjecture status → **DISFAVORED (1/R form
  excluded by E4)**; mass tracks the volume charge.
- Net thread picture: **frequency = light (edges); volume charge = mass
  (nodes).** Clean separation, consistent with E5/E7/E8.
