# QNG-GPU-016

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-18`
test_class: `mass_identification`
hardware: `GPU`

## Title

e_B sigma-gradient energy extended L-scan with fit-competition — testing
soliton rest-energy (Bogomolny-analog) hypothesis for QNG vortex ring mass.

## Purpose

QNG-GPU-015 (Hamiltonian energy L-convergence) decisively falsified both
`E_ring_global` and `E_ring_windowed` as mass observables (FAIL on G1, G2, G3).

However Gate 4 (per-component informational) revealed that ONE sub-component of
the Hamiltonian — e_B, the sigma-gradient energy `(beta/4) sum_nb (sigma_m_j -
sigma_m_i)^2` — has a monotonically decreasing R=5/R=4 ratio that approaches SM
Delta/N = 1.313:

| L     | 20    | 30    | 40    | 60    | 80    |
|-------|-------|-------|-------|-------|-------|
| e_B ratio | 4.33 | 2.65 | 2.03 | 1.53 | 1.319 |

At L=80 the ratio is 1.319 — within 0.5% of SM 1.313. But the last-3-L spread
(2.03 - 1.32 = 0.71) is far above any sensible convergence threshold, so the
apparent SM-approach cannot yet be distinguished from coincidental passage on
the way to a lower asymptote (e.g. the geometric 5/4 = 1.25 that M_ring
asymptotes to).

### Theoretical motivation (NOT post-hoc)

A critical review of the Hamiltonian-energy result (savant physics reviewer,
2026-04-18) ruled out an ADM-analog surface-flux observable on three rigorous
grounds: (1) sigma_m in v7 has no Noether conservation law (dissipative
gradient flow); (2) the ADM integrand `h·grad(h)` is the wrong formula — Gauss
integrand is `grad(h)` alone; (3) sigma_m far field is Yukawa, not 1/r — no
asymptotically flat region exists.

The review redirected to a different theoretical framing: e_B is plausibly
analogous to **soliton rest-energy / Bogomolny bound / MIT bag model gradient
energy** — the ring's mass carried by the sigma-gradient localized at the
topological core, bounded from below by topology rather than by a conservation
law. The mass = integrated (grad sigma_m)^2 in the core region, as in the
't Hooft-Polyakov monopole or the MIT bag model of hadrons. This does NOT
require a Noether current.

## Hypothesis

### H1 (PASS — soliton rest-energy confirmed):
e_B is an L-convergent observable whose ratio at large L matches SM=1.313.
Convergence occurs because the sigma-gradient is localized at ring tube
(~lattice-unit scale), independent of the Goldstone halo. Mathematically:
e_B_ratio(L) = a + b/L with a ~ 1.31 and no log-L term.

### H2 (FAIL — geometric drift):
e_B exhibits the same eventual geometric convergence as M_ring. At L=80 the
ratio happens to pass through SM on its way toward 5/4 or another geometric
limit. Mathematically: e_B_ratio(L) continues to decrease at L > 80, best
fit is a + b·log(L) or an asymptote a ≤ 1.26.

### H3 (AMBIGUOUS):
e_B declines more slowly at L > 80 but the plateau (if any) cannot be
identified within the tested L-range. Fit competition inconclusive.

## Upstream

- QNG-GPU-015 FAIL (`07_validation/audits/qng-hamiltonian-l-convergence-v1/`)
- `04_qng_pure/qng-particle-mass-identification-v1.md` §1.1 (Hamiltonian
  rescue falsified; e_B structural hint retained)
- `04_qng_pure/qng-vortex-ring-catalog-v1.md` Q1 (CRITICA)
- DER-QNG-036 §2.2: e_B definition `(beta/4) sum_nb (sigma_m_j - sigma_m_i)^2`
- Savant review (2026-04-18): Bogomolny/bag-model redirect. Conservation-law
  claim for sigma_m rejected.

## Protocol

Identical dynamics to QNG-GPU-015 and GPU-011: v5 + Channel H active in BOTH
Phase 1 and Phase 2, K_GM = 0. No new parameters are introduced.

### Parameters (identical to GPU-015)
```
ALPHA = 0.005, BETA = 0.35, DELTA_CHI = 0.20
CHI_DECAY = 0.020, CHI_REL = 0.35, GAMMA_PHI = 0.10
BETA_PHI_MIN = 0.0005, BETA_PHI_RING = 0.06
K_GM = 0.0
PHASE1 = 300, PHASE2 = 1500
```

### L-scan (extends GPU-015 upward)
```
L ∈ {20, 40, 60, 80, 100, 120}
R ∈ {4, 5}
```

GPU budget check: L=120 has N = 1.728M sites. Per-field memory float64 =
13.8 MB, six fields (sm, chi, phi, nbstep buffers) plus derived arrays ~ 200 MB.
Well within 12 GB free observed in GPU-015. L=160 would be ~320 MB — feasible
but slow; omitted to keep wall-clock under 20 min total.

### Observables (per L, R)

Three versions of e_B, all using the same physics definition
`e_B(i) = (beta/4) sum_nb (sigma_m_j - sigma_m_i)^2`:

```
e_B_global    = sum_i e_B(i)                               [all sites]
e_B_windowed  = sum_{i: |r_i - center| <= R + 3} e_B(i)    [sphere]
e_B_core      = sum_{i: dist_to_ring_curve(i) <= 3} e_B(i) [tube]
```

The tube-core mask uses the ring's toroidal curve at radius R in the z=center
plane; a site is in the core if its minimum distance to that curve is ≤ 3 lu.

Cross-check observables (informational, not gated):
- e_chi_rel (second-best Gate 4 candidate from GPU-015)
- Full Hamiltonian E_ring_global (cross-check that GPU-015 pathology persists)

### Vacuum subtraction

Same as GPU-015. e_B_vac = 0 exactly (sigma_m = SIGMA_REF everywhere gives
zero gradient). Therefore e_B is already vacuum-excess; no subtraction needed.
(Cross-check: compute vacuum value explicitly, assert ≈ 0.)

## Gates

All gates pre-registered. Numerical thresholds fixed before execution.

**Gate 1 — L-convergence of e_B (global):**
```
last-3-L spread of e_B_ratio_global (across L=80,100,120) < 0.05
```
*(GPU-015 had 0.71 spread; this test requires >14x improvement)*

**Gate 2 — L-convergence of e_B (windowed):**
```
last-3-L spread of e_B_ratio_windowed < 0.05
```

**Gate 3 — SM ratio match at L=120:**
```
|e_B_ratio_global(L=120)  - 1.3130| / 1.3130 < 0.03
|e_B_ratio_windowed(L=120) - 1.3130| / 1.3130 < 0.03
```

**Gate 4 — Fit competition (distinguishes H1 from H2):**

Fit the L-dependence of e_B_ratio_global using least-squares to two models:

- Model A (converging): `ratio(L) = a + b / L`
- Model B (logarithmic drift): `ratio(L) = a + b · log(L)`

Decision: Model A passes if both
- AIC(A) + 4 < AIC(B)   [Model A clearly preferred, Delta-AIC > 4]
- Model A asymptote `a` > 1.28  [bounded away from 5/4 = 1.25 geometric limit]

**Gate 5 — Geometric rejection:**
```
e_B_ratio_global(L=120) > 1.28
```
If the ratio at largest L is already below 1.28, geometric drift is confirmed
regardless of fit outcome.

## Decision rule

- **PASS_STRONG**: Gate 1 AND Gate 2 AND Gate 3 AND Gate 4 AND Gate 5.
  Interpretation: e_B is an L-convergent mass observable matching SM. DER-QNG-038
  is rehabilitated via the Bogomolny/bag-model route. The full Hamiltonian is
  contaminated by the Goldstone halo; e_B isolates the core mass.

- **PASS_WEAK**: Gate 4 AND Gate 5 pass (convergence confirmed, geometric limit
  rejected) but Gate 3 fails (asymptote `a` does not match SM).
  Interpretation: e_B is a legitimate L-convergent observable but the baryon
  ladder R=4→N, R=5→Δ needs reinterpretation. Document the new ratio.

- **FAIL_GEOMETRIC**: Gate 5 fails (ratio at L=120 already ≤ 1.28), OR Gate 4
  picks Model B (logarithmic drift).
  Interpretation: e_B exhibits the same geometric pathology as M_ring, only
  slower. Soliton rest-energy hypothesis is falsified.

- **AMBIGUOUS**: Gate 1 fails (still not converged at L=120) but Gate 5 passes
  (ratio still above 1.28) and fit competition does not decide.
  Interpretation: test inconclusive; would require L=160+ to resolve.
  Results reported; status of DER-QNG-038 unchanged (STRUCTURAL HINT).

## Artifact paths

- `tests/gpu/qng_e_b_l_scan_gpu.py`
- `07_validation/audits/qng-e-b-l-scan-v1/report.json`
- `07_validation/audits/qng-e-b-l-scan-v1/summary.md`
- `07_validation/audits/qng-e-b-l-scan-v1/interpretation.md`

## Pre-registration commitment

All five gates, their numerical thresholds, the two fit models, the fit
competition criterion (Delta-AIC > 4), and the decision rule are fixed before
execution. No post-hoc gate adjustment is permitted. The asymptote threshold
1.28 is chosen to be midway between 5/4 = 1.25 (geometric) and SM = 1.313.

### Risk disclosure

The reference GPU-015 data at L=80 shows e_B_ratio = 1.319, already 0.4% above
SM. Two outcomes are a priori equally plausible:
- The ratio plateaus near 1.319 and stays there (PASS_STRONG very plausible).
- The ratio continues declining toward ~1.25 (FAIL_GEOMETRIC equally plausible).

The L=100 and L=120 points are decisive. If ratio(L=100) ~ 1.30 and ratio(L=120)
~ 1.29, we are in drift regime (FAIL). If both are in [1.305, 1.320], we have
strong evidence for convergence near SM (PASS_STRONG).

Numerical convergence at 0.05 spread across three L values is a 5% precision
statement — not a 0.4% claim. The soliton identification, if it passes, would
be reported as "within ~3% of SM baryon ratio", not as 0.24% (which was always
the finite-size coincidence at L=20).
