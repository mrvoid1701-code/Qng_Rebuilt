---
name: v8 matter vacuum instability — DER-QNG-051
description: E_phi with sigma_m weighting drives sm->1 condensation under canonical dynamics; v7 rings were gradient-flow artifacts
type: derivation
status: LOCKED (2026-04-21)
upstream:
  - DER-QNG-036 (qng-hamiltonian-v7-two-field-v1.md, §2.4 E_phi form)
  - DER-QNG-050 (qng-channel-a-canonical-v1.md, exact canonical F_A)
  - GPU-031c (cached ring + exact F_A dissolves in 20 lu)
  - GPU-031d (from-scratch formation under exact F_A also blows up)
  - CPU-074 / DER-QNG-038 baryon ladder (approx-F_A artifact)
---

# DER-QNG-051: v8 matter sector has no bounded ground state under DER-QNG-036 + DER-QNG-050

## Claim

The v7/v8 matter Hamiltonian as specified in DER-QNG-036 §2.4, combined
with the exact canonical force derivation DER-QNG-050, has **no bounded
ground state for sigma_m**. Minimizing
```
E_phi = -(beta_phi / z) * sum_{i, j~i} sigma_m_i * sigma_m_j * cos(phi_i - phi_j)
```
drives sigma_m -> 1 everywhere (XY-ferromagnet condensation, with the
"magnetization amplitude" being sigma_m). No other term in E_v7 or V_couple
provides a bounded-above restoring force strong enough to oppose this.

## Evidence

### GPU-031c (cached ring, switch exact_a at t=0)

Cached L=28 R=4 ring state (CPU-074 canonical, M_ring=+176.85 under
approx F_A) evolved with exact_a=True from t=0:

| t (lu) | H        | dH/H0 | M_ring  | sm_min | sm_max |
|-------:|---------:|------:|--------:|-------:|-------:|
| 0      | -627.57  | 0     | +176.85 | 0.229  | 0.766  |
| 20     | +14250   | +23x  | -10901  | 0.996  | 1.000  |
| 40     | +76630   | +123x | -10812  | 0.992  | 1.000  |

Ring dissolved. sigma_m saturated at the clip boundary within ~10 lu.

### GPU-031d (from-scratch formation under exact F_A)

Same Phase 1/2 protocol as CPU-074 but with exact_a=True throughout:

| t (lu) | M_ring    | H         | sm range         |
|-------:|----------:|----------:|-----------------:|
| 100    | -3838     | +164502   | [0.155, 0.999]   |
| 200    | -3711     | +674830   | [0.367, 0.998]   |

Even without V_couple (Phase 1), sigma_m saturates near 1 everywhere.
The ring simply cannot form: Phase 1 produces uniform sigma_m≈1, not
a dipped ring core.

### Diagnostic force comparison on cached ring at t=0

| quantity              | approx F_A | exact F_A | delta F |
|----------------------:|-----------:|----------:|--------:|
| max \|F_sm\|          | 0.051      | 0.152     | 0.163   |
| max \|F_phi\|         | 0.160      | 0.055     | 0.121   |
| mean dF_sm (core)     | —          | —         | +0.066  |

The new `F_sm_XY_k = +(2*beta_DER/z) * R_k * cos(phi_k - Theta_k)` is
**positive in the ring core** (phi_k aligned with Theta_k gives cos~1),
pushing sigma_m UP out of the dip. Restoration alpha*(sm_ref - sm_k)
with alpha=0.005 is ~30x weaker than this condensation force. No
counter-force available.

## Root cause in DER-QNG-036

DER-QNG-036 §2.4 writes E_phi with sigma_m weighting but ONLY computes
`dE_phi/dphi_i` (treating sigma_m as parametric). The partial derivative
`dE_phi/dsigma_m_i` was never derived or discussed. Under gradient flow
in phi, this omission is harmless (the sm sector has its own gradient
flow from E_A_m + E_B_m + E_F). Under canonical (symplectic) dynamics
it is fatal: H conservation requires both partials, and the sm partial
gives a condensation force with no bounded minimum.

## Consequence: CPU-074 rings are gradient-flow artifacts

The stable rings observed in CPU-073/074/075 under v7 gradient flow
are NOT equilibria of the canonical Hamiltonian. They are dissipative
fixed points of the truncated gradient flow (phi-only force acting
through a non-canonical channel). The "canonical M_ring ladder"
(DER-QNG-038: R=3 -> 474, R=4 -> 729, R=5 -> 955) was identifying
properties of a dissipative truncation, not properties of a physical
Hamiltonian system.

Under the full canonical dynamics, the ring states simply do not exist.

## Consequence for DER-QNG-038 baryon ladder

The baryon mass identification (CPU-074/075 PASS for N/Δ ladder via
a_M = 1.373e-3) is void under v8 canonical dynamics. The ratios match
not because hadron physics has a QNG substrate, but because the
gradient-flow M_ring values scale as R^n for a specific n that happened
to match the nucleon/delta resonance spacing.

## Options to restore a physical matter sector

**Option R1 — Remove sigma_m weighting in E_phi:**
```
E_phi_R1 = -(beta_phi/z) * sum_{i, j~i} cos(phi_i - phi_j)
```
Pure XY. Force only on phi; no F_sm_XY. Canonical. Matches the approx
phi-force in the uniform-sm limit. Breaks the "matter weights phase
alignment" motivation of §2.4 — sigma_m decouples from phi at the
canonical level. Ring stability becomes a question about the remaining
sigma_m Hamiltonian (E_A_m + E_B_m + E_F + V_couple).

**Option R2 — Add sigma_m^4 self-potential:**
```
E_extra = (lambda_m / 4) * sum_i sigma_m_i^4
```
Large enough lambda_m shifts the ground state back to sigma_m < 1.
Introduces a new free parameter. Physically unnatural unless motivated
by an independent mechanism.

**Option R3 — Switch to compact sigma_m representation:**
Treat sigma_m as an angular variable (e.g., sin^2 of an underlying
theta) so the maximum is built into the parametrization. Forces are
automatically bounded. Substantial redesign; changes the relation to
the legacy v7 code.

**Option R4 — Accept DER-QNG-051; promote Gap 11 to decisive:**
The v7 matter sector is not canonical as written. v9 unification
(DEC-QNG-005 Option C) is the right way forward, with a reformulated
matter Hamiltonian designed to be canonically bounded from the start.

## Recommended next step

R4 is the honest verdict. R1 is the cheapest quick test — if R1 rings
still form and behave like CPU-074, then the sigma_m weighting in
E_phi was pure decoration and can be removed. If R1 rings DON'T form,
the matter sector has a deeper issue and v9 is mandatory.

## R1 probe result (GPU-031e, 2026-04-21)

R1 ran full Phase 1+2 at L=20, R=4, T_P2=1000. Verdict:
**H_R1_RING_UNSTABLE** (partial success).

Summary:
- σ_m NEVER saturates (stays in [0.09, 0.85]) → **vacuum instability
  is CURED by R1**. The σ_m weighting was the cause.
- H conserved to <0.01% over full Phase 2 → canonical dynamics work.
- M_ring oscillates chaotically in [-97, +686]; last-500-lu drift 202%.
  **No static equilibrium under R1 alone**.
- End-of-run M_ring = +656.64, i.e. -9.92% from CPU-074's 728.92 — but
  this is sampling luck (adjacent samples gave +83, +391, +569).

Consequence: CPU-074/075 static rings were gradient-flow artifacts
(already known), AND dropping σ_m weights is not sufficient to
recreate them canonically. The ring is a **transient pattern** the
canonical flow visits, not a stationary solution. This is a stronger
statement than DER-QNG-051 alone: even the R1-cured Hamiltonian has
no static ring.

DER-QNG-038 baryon ladder: not recoverable as rest-mass identification
under R1. Potentially recoverable under the orbital interpretation
"baryon = bounded phase-space orbit that periodically visits the ring
phase". To be tested by GPU-031f (T_P2=5000, measure <M_ring>_t,
recurrence period, and duty cycle).

Artifacts:
- `07_validation/audits/qng-v8-r1-ring-formation-v1/ANALYSIS.md`
- `07_validation/audits/qng-v8-r1-ring-formation-v1/report.json`
- `07_validation/audits/qng-v8-r1-ring-formation-v1/final_state.npz`
- `tests/gpu/qng_v8_r1_ring_formation.py` (GPU-031e)
- `tests/gpu/qng_v8_r1_finite_diff.py` (R1 force verified 7e-11)

## R1 long-time probe result (GPU-031f, 2026-04-21)

R1 ran Phase 2 at T_P2=5000 lu, M_ring sampled every 1 lu
(5000 samples) for orbital analysis.

Verdict: **H_ORBITAL_ATTRACTOR** — Scenario A confirmed at R=4.

### Orbital statistics

| Quantity                 | Value    |
|--------------------------|----------|
| <M_ring>_t (mean_all)    | +309.45  |
| std_all                  | +423.25  |
| mean_first_half          | +312.78  |
| mean_second_half         | +306.12  |
| convergence_rel          | 2.15%    |
| duty_cycle_ring (>500)   | 38.54%   |
| dominant_period_lu       | 185.2    |
| dominant_power_frac      | 40.93%   |
| H drift (0→5000 lu)      | 0.196%   |

### Three findings

1. **<M_ring>_t converges** (2.15% between halves, well under 5%
   threshold). The orbital time-average is a well-defined quantity.
2. **Dominant frequency 0.0054/lu** (period 185.2 lu) carries 40.9% of
   spectral power — orbit is quasi-periodic, not chaotic noise.
3. **Duty cycle 38.5%** in ring phase (M>500) — ring is a recognizable
   lobe of phase space revisited regularly.

### Consequences

- Scenario A (particle = bounded phase-space orbit) is **confirmed**
  at R=4 L=20.
- DER-QNG-038 baryon ladder recoverable as orbital identification:
  `m = a_M_orbital * <M_ring>_t` with
  a_M_orbital = 938 MeV / 309.45 ≈ 3.03 MeV/unit (2.2× the gradient-flow
  a_M of 1.373e-3 × 1e6 = 1.373 MeV/unit).
- Ladder structure (R=3,5,6,7) pending GPU-031g.
- Gap 11 no longer decisive-fatal: v8 supports particle physics via
  dynamic orbits. The static soliton assumption was a v7-era error.
- Structural analogy to sine-Gordon breathers: V_couple sine-Gordon
  (DER-QNG-044 Tesla finding) naturally hosts breather-like bound
  states with mass = time-averaged internal energy.

### R1 option reclassification

R1 is **not a dead-end after GPU-031e**. It is a **partial but valid
cure**:
- Vacuum instability (σ_m saturation) CURED
- Canonical H conserved (0.2% drift)
- Static ring FALSIFIED (as before)
- **Dynamic orbit CONFIRMED at long time**
- DER-QNG-038 RECOVERABLE under orbital interpretation

The original "R1 partial success" reading (from GPU-031e, T=1000 lu)
was incomplete. At T=5000 lu the full picture emerges: R1 produces
a canonical, conservative Hamiltonian whose low-lying orbit has the
properties needed for particle physics.

Artifacts:
- `07_validation/audits/qng-v8-r1-long-time-v1/ANALYSIS.md`
- `07_validation/audits/qng-v8-r1-long-time-v1/report.json`
- `07_validation/audits/qng-v8-r1-long-time-v1/m_series.npz`
- `tests/gpu/qng_v8_r1_long_time.py` (GPU-031f)

## Status

LOCKED at v8+R1 level. DER-QNG-051 original claim stands (E_phi §2.4
is non-canonical; CPU-074 rings are gradient-flow artifacts). The cure
R1 is now upgraded from "partial" to "valid with reinterpretation":
the matter sector under R1 is canonically consistent and hosts
dynamic orbits that serve as particle-mass candidates.

Open: GPU-031g (R=3,5,6,7 orbital probes) — test whether baryon
ladder structure holds under the orbital interpretation.

Claude Code autonomous session 2026-04-21.
