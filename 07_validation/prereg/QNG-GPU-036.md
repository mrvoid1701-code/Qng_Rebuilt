# QNG-GPU-036

Type: `prereg`
Status: `pending`
Author: `C.D Gabriel`
Date: `2026-04-21`
test_class: `correspondence`
hardware: `GPU`
upstream: `DER-QNG-042` (v8 canonical extension, V_couple = sine-Gordon);
          `QNG-GPU-035` (Jackiw-Rebbi dispersion, prerequisite);
          Tesla-mind agent: "matter = resonant localized nonlinear phi structure"

## Title

Tesla 3D sine-Gordon breather test — do nonlinear localized phi solutions
survive in v8 as candidate non-topological "matter"?

## Purpose

The Tesla-mind agent proposed a complementary ontology to Einstein's
Jackiw-Rebbi picture: matter is not a bound state inside a pre-existing
sigma_m well, but a **self-sustaining resonance** of the phi field itself.
In 1+1 sine-Gordon, such localized oscillating solutions exist as exact
**breathers**:

  φ_B(x,t) = 4 · arctan[(η/ω) · sin(ωt) / cosh(ηx)]

with ω² + η² = m², parametrized by 0 < θ < π/2 where ω = m·cos(θ),
η = m·sin(θ). The Dashen-Hasslacher-Neveu (DHN) mass spectrum quantizes
these into a discrete ladder of particle states.

In 3+1 the exact breather does not strictly survive, but a spherically
localized 3D analog may oscillate coherently for many periods before
radiating. This is **independent** of the ring-as-particle picture and,
if successful, reveals a second matter sector in v8.

## Prediction

Uniform σ_m = σ_ref - Δ (no ring), Δ = 0.20 → m² = 0.01027, m = 0.1013.
Choose θ = π/3 (60°):

  ω = m · cos(60°) = 0.0507
  η = m · sin(60°) = 0.0877
  T_breather = 2π/ω = 123.9 lu
  width = 1/η = 11.4 lu

Initial condition (3D spherical breather approximation, t = 0):

  φ(r, 0)    = 0
  ∂_t φ|_{t=0} = 4·η / cosh(η·r)   →   pi_phi(r, 0) = μ_φ · 4·η · sech(η·r)

## Configuration

- Integrator: Yoshida4, DT=0.025, exact_a='r1'
- Lattice: L=32 (periodic cubic, z=6) — width 11.4 lu gives ~3 widths
  across half-box
- σ_g = σ_g_ref (flat), σ_m = σ_m_ref - Δ (flat), χ = 0, pi_m = 0
- T_run = 600 lu (≈ 5 predicted periods)
- k_gm = 0 (no gravitational back-reaction)

## Gates

- **G1** (amplitude): central |φ(r=0, t)| reaches > 0.5 rad within first
  predicted period. Confirms the pulse has nonlinear content (breather
  amplitude is O(1) rad, much larger than linear KG amplitude).
- **G2** (period): measured T_dom from zero-crossings within 25% of 123.9 lu.
  Confirms ω relation ω² + η² = m².
- **G3** (energy conservation): |ΔH/H_0| < 2% over T_run. Integrator
  sanity + no unphysical runaway.
- **G4** (localization): fraction of kinetic energy density inside ball
  r < L/4 at t = T_run is > 40% of the initial fraction. Rules out
  complete dispersion.

## Interpretation

- **SG_BREATHER_SURVIVES** (G1-G4 all pass): v8 admits 3D breather-like
  nonlinear phi resonances. Two independent matter candidates in v8:
  (a) Jackiw-Rebbi bound states inside ring σ_m wells (GPU-035 sector),
  (b) self-sustaining 3D phi breathers (this sector). Opens search for
  DHN-like mass ladder; test higher harmonics at different θ.
- **SG_BREATHER_RADIATES** (G1, G2 pass; G4 fails): breather oscillates
  but radiates; pseudo-stable at best. Characterize radiation rate; may
  still be a meta-stable particle candidate if radiation timescale >>
  oscillation period.
- **SG_BREATHER_DISSOLVES** (G1 fails): 3D dimensionality kills the
  breather immediately. Matter sector in v8 is ring-trapped only;
  Tesla's self-resonance ontology does not apply.

## Expected wall time

~60 minutes (L=32, 600 lu, 24000 Yoshida4 steps; L=32 has 2.56× the
node count of L=24 so ~2-3× slower than GPU-035).

## Artifacts

- Script: `tests/gpu/qng_v8_sg_breather.py`
- Audit: `07_validation/audits/qng-v8-sg-breather-v1/`
  - `report.json`
  - `breather_traces.npz` (times, phi_central, phi_max, H_trace, ball_frac)
- Memory hook: `project_gpu036_sg_breather.md` (write only after completion).
