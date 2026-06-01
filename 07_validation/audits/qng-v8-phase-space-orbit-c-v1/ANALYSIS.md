# GPU-031c Analysis: Exact DER-QNG-050 F_A on Cached Ring

Date: 2026-04-21
Run: cached L=28 R=4 ring (formed under approx F_A), then exact_a=True for T>0,
DT=0.025, k_gm=0, chi_decay=0, T target 1000 lu — ABORTED at ~50 lu.

## Outcome: catastrophic divergence

With `exact_a=True` applied at t=0 to a ring that was equilibrated under
`exact_a=False`:

| t (lu) | H        | dH/H0     | M_ring    | sm_min |
|-------:|---------:|----------:|----------:|-------:|
| 0      | -627.57  | 0         | +176.85   | 0.229  |
| 20     | +14250   | +23.7x    | -10900    | 0.996  |
| 40     | +76630   | +123x     | -10812    | 0.992  |

Aborted. The cached ring is **NOT an equilibrium of the exact canonical
Channel A force**.

## Why — diagnosed from force magnitudes

At t=0 on the cached ring state:

| quantity             | approx F_A | exact F_A | delta |
|---------------------:|-----------:|----------:|------:|
| max \|F_sm\|         | 0.051      | 0.152     | 0.163 |
| max \|F_phi\|        | 0.160      | 0.055     | 0.121 |
| mean(ΔF_sm) at 10 lowest-sm core nodes | -    | -   | +0.066 |

The **new sm back-reaction** `F_sm_XY_k = +(2*beta_DER/z) * R_k * cos(phi_k - Theta_k)`
is **positive in the ring core** (since phi_k is closely aligned with its
sigma_m-weighted neighbor mean Theta_k, giving cos ≈ +1). Effect: it
drives sigma_m UP from the core dip (0.23) toward the clipping boundary
(1.0) within ~10 lu. The ring dissolves.

## Interpretation

This is **not** a bug in DER-QNG-050 (finite-diff verified <1e-7 rel err
on both F_A and F_sm_XY). It is a **physical statement**: the sigma_m
ring dip is stabilized in the approx theory by the limited-magnitude
F_A, but under the exact canonical action the same ring state has huge
restoring forces that inflate the core.

## Implications for DER-QNG-038 baryon ladder

The canonical M_ring values (R=3:474, R=4:729, R=5:955) were measured
under the approx F_A. They are **not valid under DER-QNG-050 exact F_A**
applied to those states.

## Required follow-up (GPU-031d)

Form a ring **from scratch** under `exact_a=True`. Three possible
outcomes:
- H_CANONICAL_PRESERVED: ring forms with similar M_ring (< 20% shift)
- H_RING_UNSTABLE: ring forms but drifts substantially
- H_NO_RING: ring does not form at all - matter-as-soliton was an
  artifact of the approximation

This is decisive for whether Scenario A can be tested at all under
the exact canonical theory.

## Einstein-timeline update

We thought we'd test Scenario A at Kaluza 1921 (framework PRESENT,
breathing mode OBSERVED). What we actually learned:
the previous ring state was the equivalent of a hydrodynamic vortex
stabilized by a BAD approximation of the stress tensor. We have to
reconstruct the equilibrium under the proper action first. Still 1921.
