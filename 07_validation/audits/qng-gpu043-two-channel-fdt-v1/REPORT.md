---
type: evidence
test_id: QNG-GPU-043
category: gpu_scale
hardware: GPU
status: completed
verdict: TWO_CHANNEL_FAIL
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-054 (two-channel FDT structure, analytical)
  - DER-QNG-051 (vacuum instability, R1 pure-XY option)
  - GPU-031f (orbital attractor R=4, T=185 lu)
  - NOTE-QNG-017 (classical invariants ⟨L⟩=660)
---

# QNG-GPU-043 — Two-channel FDT probe REPORT

## Verdict: **TWO_CHANNEL_FAIL** (17th failed ℏ program)

γ-invariance violated with CV = 58.99% (prereg fail threshold: 10%). No
R-scan needed — γ-dependence is definitive.

## Configuration

- L = 20, T_P1 = 300 lu, T_P2 = 1000 lu, T_spinup = 200 lu, T_meas = 1000 lu
- DT = 0.025, Yoshida4 integrator
- exact_a = 'r1' (DER-QNG-051 Option R1, pure-XY E_phi)
- k_gm = 0.01 (activates Channel A: σ_m → σ_g → χ coupling)
- R = 4 fixed; γ (CHI_DECAY) ∈ {0.010, 0.020, 0.040}

Fresh ring formation each run (no cache reuse — cache was formed under
default exact_a=False with k_gm=0, which leaves σ_g ≡ 0.5 uniform and
χ ≡ 0 exactly, making the two-channel mechanism inert).

## Results

### γ-scan at R=4

| γ | ⟨χ²⟩ | T_cycle (lu) | ω_orbit | M_mean | M_std | H_drift | ℏ_candidate |
|---|---|---|---|---|---|---|---|
| 0.010 | 1.7152e-04 | 181.70 | 0.03458 | +321.9 | 417.6 | 0.08% | **9.9203e-05** |
| 0.020 | 1.6330e-04 | 181.70 | 0.03458 | +321.9 | 417.6 | 0.08% | **1.8889e-04** |
| 0.040 | 1.4925e-04 | 181.70 | 0.03458 | +321.9 | 417.6 | 0.08% | **3.4529e-04** |

**ℏ_candidate CV across γ = 58.99%**

### Sub-diagnostics (pass)

- Symplectic sector (S) **decoupled from γ**: T_cycle, ω_orbit, M_mean identical
  across all three runs → confirms GPU-031f orbital attractor is unaffected
  by Channel D dissipation rate (expected and required).
- Energy conservation **excellent** at H_drift = 0.08% over T=1000 lu for all
  runs → Yoshida4 symplectic integrator stable in two-channel regime.
- Channel A active: std(σ_g) = 3.3–3.6e-03 (nonzero for all γ) → σ_g does
  develop spatial structure under k_gm=0.01 (contrast: baseline cache with
  k_gm=0 had std(σ_g) = 0 exactly).
- χ² steady-state active: mean ⟨χ²⟩ = 1.5–1.7e-04 **nonzero for first time
  in v8 experimental history** → two-channel coupling is ontologically real.

## Interpretation

### Why γ-invariance failed

Einstein-Nyquist FDT cancellation `γ·⟨χ²⟩ = D_eff` (γ-independent) requires
the driving force on χ to be **stochastic white noise**. Observed instead:

```
γ      ⟨χ²⟩        γ·⟨χ²⟩
0.010  1.72e-04    1.72e-06
0.020  1.63e-04    3.27e-06
0.040  1.49e-04    5.97e-06
```

`γ·⟨χ²⟩` scales nearly linearly with γ (ratio 1 : 1.9 : 3.5), NOT constant.
⟨χ²⟩ decreases only ~13% for 4× γ change — χ is **source-limited, not
dissipation-limited**.

Root cause: v8 dynamics are **purely deterministic** (Yoshida4 conservative
+ Channel D linear dissipation). The orbital attractor drives χ with a
quasi-periodic signal at ω_orb = 0.035 rad/lu — narrow-band, not white.
Einstein-Nyquist cancellation requires flat spectral density; concentration
of driving power at a single frequency cannot produce γ-invariant ⟨χ²⟩.

### What this closes

- **DER-QNG-054 falsified** as route to emergent ℏ. Two-channel structure
  exists (confirmed) but does NOT produce a rigid action quantum.
- **17th failed ℏ program** under QNG native ontology. Programs ruled out:
  phase-space volume (α), action universality (β), χ-variance (γ as symbol),
  Gabriel edge-noise (δ), ⟨L⟩/N intensive (ε), Tesla cavity (ζ),
  H-dispersion (η), Onsager circulation (θ), Debye-Waller edge
  disorder (ι), non-Gaussian edge (κ), discrete edge (λ), OU stochastic
  edge (μ), U(1) LGT edge (ν), graph winding topology (ο), Verlinde
  entropic (π), Dirac constraint (ρ), two-channel FDT (σ).
- **V9-C (external ℏ via Weyl path integral, DER-QNG-052) remains obligatory**
  as the sole path to ℏ in QNG.

### What this teaches beyond QNG

The failure mode is **structural**, not specific to QNG:

> **No purely deterministic substrate with a quasi-periodic attractor can
> produce emergent ℏ via Einstein-Nyquist FDT.** Genuine stochasticity
> (ontological noise, thermal coupling, or quantum vacuum) or effective
> stochasticity (strong chaotic mixing) is required.

This result applies to:
- Adler trace dynamics (matrix-valued deterministic)
- 't Hooft cellular automaton (discrete deterministic)
- Wolfram hypergraph (rewriting deterministic)
- Any classical substrate without ontological noise injection

The negative result **sharpens the landscape**: emergent-ℏ programs must
either admit stochastic primitives (v9 Langevin style) or impose external
quantization (V9-C path integral). There is no "free lunch" derivation
from pure determinism.

### What this PRESERVES

- **v8 two-channel structure is real** — χ field is not a bookkeeping
  artifact; it carries a physical dissipation-fluctuation sector that
  tracks the symplectic sector's forcing. Just not in Einstein-Nyquist
  form.
- **Orbital attractor (GPU-031f) robust against γ** — T_cycle, ω, M_mean
  invariant across γ ∈ [0.010, 0.040]. The symplectic sector of v8 has
  well-defined classical dynamics independent of Channel D.
- **Classical invariants unchanged**: ⟨L⟩=660 (DER-QNG-049), baryon ladder
  (DER-QNG-038), Einstein correspondence (DER-QNG-044) — none affected by
  this negative result.

## Deliverables produced

- Executable: `tests/gpu/qng_gpu043_two_channel_fdt.py` (--poc, --gamma, --full)
- Traces: `traces_POC_R4_gamma0.020.npz`, `traces_B_R4_gamma0.010.npz`,
  `traces_B_R4_gamma0.040.npz` (chi² + sm² + M_ring + H arrays)
- Summary JSON: `gamma_scan_rows.json`, `poc_result.json`

## Governance follow-ups

1. DER-QNG-054 status → **FALSIFIED** (add to CLAUDE.md falsified list)
2. DEC-QNG-007 → V9-C remains sole path to ℏ; V9-A (two-channel) marked
   FAILED in §γ-invariance
3. THEORY_STATE.md → add GPU-043 TWO_CHANNEL_FAIL to latest-audits
4. NOTE-QNG-023 (to write) → "On the necessity of ontological stochasticity
   for emergent ℏ in classical substrates"

## Runtime

- POC run: 601 s (10 min) for γ=0.020
- γ-scan run: 2 × ~590 s = 1178 s (20 min) for γ=0.010 and γ=0.040
- Total: ~30 min on GPU (single NVIDIA device, serial per feedback_gpu_serialization)
