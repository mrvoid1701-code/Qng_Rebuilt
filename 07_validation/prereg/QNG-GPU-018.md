# QNG-GPU-018

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-18`
test_class: `sigma_m_potential_mass_scale`
hardware: `GPU`

## Title

V(sigma_m) = (lambda/4)*(sigma_m^2 - sigma_ref^2)^2 added to E_v7 — test
whether the derived saturation value lambda = 0.19 cures the IR halo
(Gate A), gives R-independent core width (Gate B), and converges the
mass ratio to the SM ladder (Gate C).

## Purpose

After four falsifications of v5+Channel H ring mass observables
(GPU-009..017), NOTE-QNG-016 forces Option B: add a potential V(sigma_m)
to break the σ-shift symmetry and supply sigma_m with a dynamically
generated length scale ξ.

DER-QNG-040 derives lambda from a marginal-stability extension of
DER-QNG-034 (extended from the sigma_g sector to the sigma_m sector):

```
lambda = (gamma_phi - alpha_m) / (2 * sigma_ref^2) = 0.19
xi     = sqrt(beta_m / (2*lambda*sigma_ref^2)) = 1.92 lu
```

Both Einstein-mind (derivation file) and Savant-physics-reviewer
(critique file) agree on the structural form and on the fact that
saturation (as opposed to strict inequality) is a convention. The
convention is upgraded to a falsifiable prediction by the three
gates below.

This pre-reg COMMITS lambda = 0.19 before execution. Post-hoc tuning
is not permitted.

## Hypothesis

### H1 (PASS — DER-QNG-040 saturation confirmed):
At L=80, R=5, lambda=0.19:
- Halo exponent alpha > 3.5 (halo suppressed from Goldstone alpha≈2.37)
- Core FWHM converges to 1.92 lu ± 30%, R-independent across R∈{4,5,6,7}
- Mass ratio M(R=5)/M(R=4) converges (ΔL spread < 5%) to value in [1.25, 1.40]
=> Option B derivation accepted; DER-QNG-040 promoted to `locked`;
   baryon ladder program restored.

### H2 (FAIL_LAMBDA — structural form right, value wrong):
Gate A PASS but Gate B or Gate C FAIL.
=> V(sigma_m) cures the IR halo (structural claim confirmed) but
   saturation lambda=0.19 is wrong. Re-open as Gap 9 (Yukawa-analog).
   Secondary test GPU-018B with lambda as EFT parameter, committed pre-run.

### H3 (FAIL_STRUCTURAL — potential does not help):
Gate A FAIL (alpha stays ~ 2.4 as in the massless case).
=> V(sigma_m) does not cure the halo. Adding a simple mass term is
   insufficient. The baryon-from-ring program requires a more radical
   substrate modification, not identified at this date. Mass
   identification program is halted.

### H4 (AMBIGUOUS):
Any other partial-PASS/partial-FAIL combination. Requires secondary test.

## Upstream

- GPU-009..014 FAIL (M_ring 5/4) — `qng-m-ring-l-convergence-v1`
- GPU-015 FAIL (H_v7 total Hamiltonian)
- GPU-016 FAIL_GEOMETRIC (e_B windowed 4.5) — `qng-e-b-l-scan-v1`
- GPU-017 FAIL (Hopfion α=1.89) — `qng-hopfion-disorder-l-scan-v1`
- NOTE-QNG-016 — mass-observable exhaustion (forces Option B)
- DER-QNG-040 — `qng-sigma-m-potential-v1.md` (theoretical basis)
- DER-QNG-034 — marginal-stability template (extended here)
- DER-QNG-036 — H_v7 Hamiltonian structure (E_v7 augmented)
- einstein-mind/derivation-v-sigma-m-lambda.md
- savant-physics-reviewer/critique-v-sigma-m-routes.md

## Protocol

### 1. Dynamics (v7 + Channel H + V(sigma_m))

Identical to GPU-016 (v5 + Channel H) for the sigma_g, chi, phi sectors.
The sigma_m sector is augmented with the V(sigma_m) gradient:

```
sigma_m_i(t+1) = sigma_m_i(t)
               + alpha_m*(sigma_m_ref - sigma_m_i)
               + beta_m*(sigma_m_bar - sigma_m_i)
               - gamma_phi*(1-|Z_i|)*sigma_m_i
               - lambda * sigma_m_i * (sigma_m_i^2 - sigma_ref^2)
```

Parameters (FROZEN):
```
alpha_m     = 0.005
beta_m      = 0.35
gamma_phi   = 0.10
sigma_ref   = 0.5
lambda      = 0.19              ← COMMITTED (DER-QNG-040 saturation)
DELTA_CHI   = 0.20
CHI_DECAY   = 0.020
CHI_REL     = 0.35
GAMMA_PHI   = 0.10              (same Channel F)
BETA_PHI_MIN  = 0.0005
BETA_PHI_RING = 0.06
K_GM        = 0.0               (gravity off for mass identification)
PHASE1 = 300, PHASE2 = 1500
```

Gate cross-checks compute predicted ξ = sqrt(beta_m/(2*lambda*sigma_ref^2))
= sqrt(0.35 / (2*0.19*0.25)) = 1.92 lu.

### 2. Runs

**Stage A (IR halo + core FWHM):**
- L ∈ {40, 60, 80, 100}
- R = 5 fixed
- Measure: dis(r) = |∇phi|²·sigma_m shell profile, fit alpha;
  and FWHM of sigma_m radial core profile in the ring cross-section.

**Stage B (R-independence of core):**
- L = 80 fixed
- R ∈ {4, 5, 6, 7}
- Measure: core FWHM per R.

**Stage C (mass ratio L-convergence):**
- L ∈ {60, 80, 100, 120}
- R ∈ {4, 5} per L
- Measure: M_ring(R, L) = N * sigma_m_ref - sum(sigma_m);
  ratio M(R=5)/M(R=4) per L; spread across L.

All runs use identical dynamics and numeric protocol; Phase 1 = 300 steps,
Phase 2 = 1500 steps. T_P2 = 1500 snapshot is the canonical measurement.

### 3. Observables

For each (L, R):
- `alpha(L)`: power-law exponent of dis(r) in r ∈ [R+5, L/2-3]
- `FWHM(L, R)`: full-width-half-max of sigma_m core profile in the
  ring's toroidal cross-section (at phi = 0 plane, dr vs axis)
- `M_ring(L, R) = N*sigma_m_ref - sum(sigma_m)`

Diagnostics:
- R² of power-law fit for alpha
- L-independence of FWHM (spread across L at fixed R, R=5)
- R-independence of FWHM (spread across R at fixed L=80)
- L-convergence of M(R=5)/M(R=4) (spread across L)

## Gates (all committed; no post-hoc adjustment)

### Gate A — IR halo suppression (primary structural test)

```
alpha(L=80, R=5)  >= 3.5     [PASS]
alpha(L=80, R=5)  <  3.0     [FAIL]
3.0 <= alpha < 3.5           [AMBIGUOUS]
```

Also require L-independence: |alpha(L=100) - alpha(L=60)| < 0.25.

Rationale: the Goldstone halo has alpha ~ 2.37 (GPU-012). With mass
m_V = sqrt(2*lambda*sigma_ref^2) = sqrt(0.095) ~ 0.31, the expected
Yukawa-suppressed tail has alpha effectively infinite — but we use 3.5
as the threshold because measurement is dominated by the finite fit
range r ∈ [R+5, L/2-3], which saturates the apparent alpha well before
infinity.

### Gate B — R-independent core width (uniqueness of lambda)

At L=80, R ∈ {4, 5, 6, 7}:
```
(max FWHM - min FWHM) / mean FWHM  <  0.30          [PASS]
```

AND the mean value matches prediction:
```
| mean(FWHM) - 2.355 * xi | / (2.355 * xi)  <  0.30   [PASS]
```

where 2.355 = 2·sqrt(2·ln 2) is the Gaussian FWHM factor, xi = 1.92 lu,
so 2.355·xi = 4.52 lu predicted FWHM.

Rationale: if the core width scales with R (FWHM/R = const), V(sigma_m)
is not controlling the core; geometry is. If FWHM is R-independent
but disagrees with 4.52 lu by more than 30%, lambda is wrong.

### Gate C — L-converged, physically reasonable mass ratio

```
spread_L = max(ratio(L)) - min(ratio(L))  over L ∈ {60,80,100,120}
spread_L < 0.08                                     [PASS convergence]
mean(ratio(L)) ∈ [1.25, 1.40]                       [PASS physical range]
```

Rationale: v5+Channel H gave ratio → 1.25 (geometric limit) as L grew.
The DER-QNG-040 prediction with kappa ∈ [3,5] gives ratio ∈ [1.30, 1.35].
The lower bound 1.25 is the v5 failure; upper bound 1.40 allows some
kappa flexibility while excluding the log-dominated regime (kappa=0 →
1.63).

The SM target N(1232)/N(938) = 1.313 lies inside this gate window
but is not used as a binary criterion — convergence + window is the
gate. An exact SM match is a nice-to-have, not a requirement.

### Gate D — consistency self-check

The DER-QNG-040 marginal-stability relation should manifest directly.
Separately measure (in a linearized probe, L=40, no Channel F):
```
d_t sigma_m_global at small perturbation s0 = 0.01
=> effective damping rate r_eff = -d ln|s(t)|/dt
predict r_eff = alpha_m + 2*lambda*sigma_ref^2 = 0.005 + 0.095 = 0.100
gate:  |r_eff - 0.100| / 0.100  <  0.20
```

Rationale: this is the direct test of Eq. 1 linearization. If Gate D
fails, the Hamiltonian structure assumption of DER-QNG-040 is
inconsistent with the simulation (e.g., gradient-flow implementation
differs from the analytic derivation).

## Decision rule

```
Gate A PASS + Gate B PASS + Gate C PASS + Gate D PASS
  => H1 confirmed; DER-QNG-040 → `locked`; baryon ladder restored.

Gate A PASS + Gate D PASS + (Gate B FAIL or Gate C FAIL)
  => H2 (FAIL_LAMBDA): structural form right, value wrong.
     Re-open as Gap 9 (Yukawa). Schedule GPU-018B with lambda as
     committed EFT parameter.

Gate A FAIL
  => H3 (FAIL_STRUCTURAL): potential does not cure the halo.
     Mass identification program halted pending new theoretical input.

Gate D FAIL
  => VOID: simulation inconsistent with linearized analytics.
     Debug implementation before drawing physics conclusions.

Otherwise => H4 (AMBIGUOUS).
```

## Artifact paths

- `tests/gpu/qng_sigma_m_potential_gpu.py`
- `07_validation/audits/qng-sigma-m-potential-v1/report.json`
- `07_validation/audits/qng-sigma-m-potential-v1/summary.md`
- `07_validation/audits/qng-sigma-m-potential-v1/interpretation.md`
- `07_validation/audits/qng-sigma-m-potential-v1/run.log`

## Pre-registration commitment

All four gates (A, B, C, D), numeric thresholds, fit domains, and the
decision rule are fixed before execution. lambda = 0.19 is committed;
no post-hoc tuning, not even to match the SM value 1.313.

### What makes this non-riggable (Savant-physics-reviewer argument)

- Gate A (halo decay) measures the IR tail: an input choice that helps
  the mass ratio (Gate C) would not automatically help Gate A; they
  probe different physics (IR screening vs core profile).
- Gate B (R-independence of FWHM) measures whether V is controlling the
  core or whether geometry is. A tuned lambda that fits the R=4 core
  would NOT automatically give R-independent FWHM across R=4,5,6,7.
- Gate C (L-convergence of ratio) measures whether IR modes contaminate
  the ring mass. This is independent of what value the ratio settles
  to.
- Gate D (damping rate) is a direct linearization check of Eq. 1 and
  is immune to ring-dynamics tuning.

A lambda fit to any one of these four observables cannot automatically
satisfy the other three. Passing all four is a non-trivial confirmation.

### Risk disclosure

- sigma_m clip to [0,1] interacts with V's negative branch at
  sigma_m = -0.5. The clip strips the negative branch, leaving a single
  physical minimum (see DER-QNG-040 §1). Numerical integration errors
  near sigma_m ≈ 0 in the core may produce clip artifacts; the
  effective mass term analysis assumes linearization valid where
  clip is inactive. If the core depletion exceeds sigma_ref (i.e.,
  sigma_m drops below 0 before clip), the derivation breaks down.
  Observable: monitor min(sigma_m) in the core; flag if < 0.01.
- If the mass term is so strong that the ring fails to form (sigma_m
  pinned near sigma_ref even at vortex core), Phase-2 would produce
  a "no-ring" state. Gate E check: sigma_m_core at T_P2 end must be
  < 0.4 (i.e., depletion still occurs). If Gate E fails, V is too
  strong and the ring cannot exist — but this would be a PRINCIPLED
  failure (quantitative prediction of lambda max from ring existence).
  Record but do not use to adjust lambda post-hoc.
