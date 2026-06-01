# QNG-GPU-035

Type: `prereg`
Status: `pending`
Author: `C.D Gabriel`
Date: `2026-04-21`
test_class: `correspondence`
hardware: `GPU`
upstream: `DER-QNG-042` (v8 canonical extension, V_couple = (g/2)·(σ_ref - σ_m)²·(1 - cos φ));
          `DER-QNG-041` (Yukawa phi-mass via V_couple);
          `DER-QNG-051` (v8 vacuum instability, R1 pure-XY cure)

## Title

Einstein Jackiw-Rebbi dispersion test — verify m_φ²(x) = (g/μ_φ)·(σ_ref - σ_m)²
as position-dependent phi mass from V_couple.

## Purpose

The Einstein agent's strongest pivot proposal: matter in v8 is not the ring
itself but the **phi field**, with position-dependent mass induced by the
sine-Gordon V_couple. Expanded to leading order at small phi:

  V_couple ≈ (g/2) · (σ_ref - σ_m)² · φ²/2

so φ behaves like a Klein-Gordon field with mass

  m_φ²(x) = (g/μ_φ) · (σ_ref - σ_m(x))²

This is the canonical **Jackiw-Rebbi** structure: a scalar field acquires
a position-dependent mass via coupling to a background scalar (here σ_m).
Rings become sigma_m wells that trap phi bound states — the "matter" is
not the ring topology but the phi modes in its well.

Before committing to this ontology, we must verify the dispersion relation
in the simplest setting: **uniform σ_m** (no ring). Then phi has uniform
mass m_φ² = (g/μ_φ)·Δ², and small-amplitude phi oscillates at a pure
frequency ω = m_φ at k=0.

## Prediction

With canonical v8 params (g = 0.22, μ_φ = 0.857):

| Δ (deficit) | m² = (g/μ_φ)Δ² | T = 2π/m |
|---|---|---|
| 0.0 | 0 | ∞ (no oscillation — massless) |
| 0.1 | 0.002568 | 123.9 lu |
| 0.2 | 0.01027 | 62.0 lu |

Ratio T(0.1)/T(0.2) = 2.0 exactly (m ∝ Δ).

## Configuration

- Integrator: Yoshida4, DT=0.025, exact_a='r1'
- Lattice: L=24 (periodic cubic, z=6)
- Initial state: σ_g = σ_g_ref (flat), σ_m = σ_m_ref - Δ (flat, per run),
  χ = 0, pi_m = pi_phi = 0, φ = A · cos(k·x)
- phi amplitude A = 0.05 (small enough for linear KG)
- k_mode = 0 (global bump, pure mass mode)
- T_run = 300 lu per deficit

## Gates

- **G1** (Δ = 0.0): k=0 phi does NOT oscillate (no zero-crossings detected
  or T_measured > 10·T_run). Confirms massless vacuum — no accidental mass
  from integrator or Channel F.
- **G2** (Δ = 0.1): |T_meas / 123.9 - 1| < 0.15. Quantitative mass-gap test.
- **G3** (Δ = 0.2): |T_meas / 62.0 - 1| < 0.15. Validates Δ² scaling.
- **G4**: |T(0.1) / T(0.2) - 2.0| < 0.10. Independent check of linear m ∝ Δ
  (doesn't depend on absolute g/μ_φ calibration).

## Interpretation

- **JACKIW_REBBI_PASS** (all four gates): m_φ = √(g/μ_φ)·|σ_ref - σ_m|
  confirmed quantitatively. Phi is the matter field; rings are just the
  σ_m wells that trap it. Next test (GPU-037, future): measure φ bound
  states in a ring σ_m profile and compute bound-state mass spectrum.
- **G2/G3 or G4 FAIL**: V_couple either has additional terms beyond
  quadratic (large-amplitude corrections bleeding in at A=0.05) or the
  derived μ_φ = 0.857 is wrong. Revisit DER-QNG-042 prereqs §3.3.
- **G1 FAIL**: spurious mass in the "vacuum" — integrator artifact or
  exact_a='r1' bug. Must be resolved before any mass claim in v8.

## Expected wall time

~30 minutes (L=24, 3 runs × 300 lu × 12000 steps each, Yoshida4).

## Artifacts

- Script: `tests/gpu/qng_v8_jackiw_rebbi.py`
- Audit: `07_validation/audits/qng-v8-jackiw-rebbi-v1/`
  - `report.json`
  - `phi_traces.npz` (times + phi_mean per deficit)
- Memory hook: `project_gpu035_jackiw_rebbi.md` (write only after completion).
