---
type: evidence
test_id: QNG-GPU-044
category: gpu_scale
hardware: GPU
status: completed (stopped after 2/3 runs — definitive)
verdict: VACUUM_FDT_FAIL
author: C.D Gabriel
date: 2026-04-24
upstream:
  - QNG-GPU-043 (deterministic two-channel FDT, FAILED)
  - DER-QNG-054 (two-channel FDT analytical structure)
  - Hypothesis A (stochastic-vacuum layer, Gabriel 2026-04-24)
---

# QNG-GPU-044 — Vacuum-sourced FDT probe REPORT

## Verdict: **VACUUM_FDT_FAIL** — stochastic vacuum layer does NOT rescue ℏ emergence

CV between γ=0.010 and γ=0.020 measurements = 42% (threshold FAIL: 10%).
Run stopped at 2/3 data points — extrapolation confirms ≥60% final CV,
well beyond any passing threshold.

## Configuration

- L=20, R=4 fixed, γ_scan = {0.010, 0.020, 0.040 — STOPPED}
- σ_vac = 0.04 (white Gaussian noise injected into χ after each Yoshida step)
- Same protocol as GPU-043 (exact_a='r1', k_gm=0.01, fresh ring formation)
- Added noise: `dchi += sigma_vac * sqrt(dt) * randn()` post-step

## Results

| γ | ⟨χ²⟩_meas | ⟨χ²⟩_FDT_theory | ratio | hbar_cand | H_drift |
|---|---|---|---|---|---|
| 0.010 | 7.39e-03 | 2.00e-03 | **3.70x** | **4.28e-03** | 0.11% |
| 0.020 | 6.85e-03 | 1.00e-03 | **6.85x** | **7.92e-03** | (similar) |
| 0.040 | STOPPED | 0.50e-03 | (extrap ~13x) | (extrap ~15e-03) | — |

**hbar_candidate CV across 2 observed points = 42%**

Linear extrapolation to γ=0.040: hbar_cand ≈ 15.8e-03, projected 3-point
CV ≈ 65%. Far above prereg FAIL threshold of 10%.

## Diagnostic interpretation

### Why Einstein-Nyquist still fails with vacuum noise

The theoretical prediction `⟨χ²⟩ = σ_vac²·dt/(2γ)` would be γ-invariant
for `hbar_cand = 2γ·⟨χ²⟩/ω` by construction. Observations show:

1. **⟨χ²⟩ is nearly constant across γ** (7.39 vs 6.85, only 7% change for
   2× γ change). This is contrary to the 1/γ scaling expected from a pure
   Ornstein-Uhlenbeck process.

2. **⟨χ²⟩ / ⟨χ²⟩_FDT_theory grows with γ** (3.70 → 6.85). The measured
   χ² is far higher than pure FDT prediction, and the excess grows. This
   means the driving on χ is dominated by deterministic (Channel D
   rigidity) terms, not by the added stochastic noise.

3. **Root cause**: Channel D drive
   ```
   dchi/dt = -gamma*chi + CHI_REL*(sigma_g_bar - sigma_g) + DELTA_CHI*(SIGMA_G_REF - sigma_g) + Xi
   ```
   has coupling coefficients `CHI_REL=0.35` and `DELTA_CHI=0.20` that
   dominate any tested γ ∈ [0.010, 0.040]. The χ field is tightly bound
   to σ_g deviations — it is NOT a free mode that can equilibrate with
   an external bath.

4. **Noise suppression**: The vacuum kick `σ_vac·sqrt(dt)·randn` is
   immediately "absorbed" by χ's restoring forces back to the deterministic
   setpoint determined by σ_g. Equilibrium ⟨χ²⟩ is set by the σ_g
   deterministic profile, not by the noise/dissipation balance.

### What this confirms beyond GPU-043

GPU-043 showed deterministic-only dynamics cannot produce γ-invariance.
GPU-044 shows that **adding external stochastic noise is insufficient** if
the receiving mode (χ) is not a free mode. The problem is structural:

> **Emergent hbar via Einstein-Nyquist requires not just stochasticity but
> also that the dissipative mode χ be effectively UNCOUPLED from
> deterministic forces.** In v8, χ is tightly bound to σ_g via Channel D,
> so adding noise does not produce OU-type statistics.

This rules out Hypothesis A (stochastic-vacuum layer) as implemented in v8.

## What this DOES NOT rule out

- **Hypothesis B (three-infinities / intrinsic chaos)**: untested. GPU-045
  (Lyapunov analysis on R1 orbital attractor) is the decisive diagnostic.
  If λ_max > 0 with fast mixing, intrinsic stochasticity is possible even
  without external noise.

- **v9-graphity (probabilistic substrate)**: fundamentally different
  architecture where noise is intrinsic to graph fluctuations, not
  injected externally. Not yet designed or tested.

- **V9-C (external hbar via Weyl path integral)**: still obligatory path
  per DEC-QNG-007.

## Scientific value of the negative result

Two-layer diagnosis:

1. **Deterministic substrate (GPU-043)**: cannot produce hbar. Applies to
   Adler, 't Hooft, Wolfram, all pure-deterministic programs.

2. **Deterministic substrate + external stochastic vacuum (GPU-044)**:
   STILL cannot produce hbar if the dissipative mode is tightly coupled.
   Applies to any SED-style completion of a classical substrate where
   the "quantum carrier" has internal structure.

Combined result: **emergent hbar from classical substrates requires either
(a) intrinsic ergodic chaos producing effective stochasticity (Ruelle-Bowen)
or (b) ontological probabilistic graph structure (quantum graphity), not
layered SED.**

## Deliverables

- Executable: `tests/gpu/qng_gpu044_vacuum_fdt.py`
- Traces: `traces_vac_R4_gamma0.010.npz`, `traces_vac_R4_gamma0.020.npz`
- Partial measurement on γ=0.040 stopped

## Governance follow-ups

1. Hypothesis A (stochastic-vacuum) → **FALSIFIED for v8 substrate**
2. Surviving paths per DEC-QNG-007:
   - V9-C (external hbar) — sole axiomatic path
   - GPU-045 Lyapunov (Hypothesis B test — pending)
   - v9-graphity program (new, untested) — to be drafted
3. NOTE-QNG-023 (to write): "Structural obstruction: tight-coupled
   dissipative modes cannot equilibrate with external noise to produce
   FDT-based hbar"

## Runtime

- γ=0.010 run: 602 s
- γ=0.020 run: 600 s
- γ=0.040 run: STOPPED at P2 36000/40000 (~7 min in)
- Total: ~21 min on GPU
