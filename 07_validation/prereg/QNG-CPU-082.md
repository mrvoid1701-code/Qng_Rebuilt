---
id: QNG-CPU-082
type: test
status: pre-registered
category: reference
hardware: cpu
created: 2026-04-22
depends_on:
  - qng-emergent-noise-v1       # DER-QNG-023 (η derived from ring FDT)
  - qng-quantization-program-v1 # NOTE-QNG-016 (program alpha)
executable: tests/cpu/qng_eta_fluctuation_reference.py
---

# QNG-CPU-082 — eta fluctuation invariant (program alpha probe)

## Purpose

First numerical probe of NOTE-QNG-016 program alpha (η ↔ ℏ).

Test whether the classical v8 substrate exhibits a zero-point-like
fluctuation invariant

```
Q = <(Δπ_m)²><(Δσ_m)²>
```

that is independent of perturbation amplitude ε. If yes, Q is a candidate
for η² — the substrate action quantum that plays the role of ℏ.

## Motivation

After GPU-038 (2026-04-22) showed that the orbital attractor is a global
mode (R_eff = L/2) with no spin and no topological winding, the
interpretation of v8 matter has shifted from "localized particle" to
"classical field mode awaiting quantization". Program alpha proposes
this quantization emerges from substrate-intrinsic noise η rather than
requiring an external ℏ postulate.

This test is the minimal numerical check before committing to program
alpha or pivoting to program beta (external canonical quantization).

## Protocol

- **Reduction**: 1D lattice (L=100, periodic) of (σ_m, π_m) — captures the
  canonical sector of v8 responsible for M_ring fluctuations
- **Background**: σ_m = SIGMA_M_REF uniform (no ring; pure substrate test)
- **Perturbation**: σ_m += ε·randn(L); π_m += ε·randn(L)
- **Dynamics**: Yoshida4 symplectic with EOM
  - dot(σ_m) = π_m / μ_m
  - dot(π_m) = β_m · Δσ_m − k_eff · (σ_m − σ_ref)
- **Parameters**: match v8 canonical — β_m=0.40, μ_m=10.0, k_eff=0.04,
  σ_ref=0.5, DT=0.025
- **Evolution**: T_RUN=200 lu with T_BURN=50 lu burn-in
- **Sampling**: every 5 lu, compute spatial Var(σ_m) and Var(π_m) about
  their current spatial means
- **Statistics**: time-average post-burn; report Q = <Var(σ)>·<Var(π)>
- **Amplitude sweep**: ε ∈ {0.005, 0.010, 0.020}, 3 random seeds each

## Inputs

None (self-contained reference test)

## Outputs

- `07_validation/audits/qng-eta-fluctuation-v1/report.json`:
  - 9 per-run results (eps × seed)
  - per-eps aggregated products
  - empirical scaling exponent ζ where Q ~ ε^ζ
  - verdict

## Gates

- **ETA_UNIVERSAL_CANDIDATE** (ζ in [−0.3, +0.3]):
  Q is ε-independent → substrate has intrinsic zero-point fluctuations.
  Program alpha VIABLE. Proceed to DER-QNG-048 identification η ↔ ℏ.

- **ETA_LINEAR_RESPONSE** (ζ in [1.7, 2.3]):
  Q scales as ε² → each variance ~ ε → classical linear response
  without substrate-intrinsic scale. Program alpha needs stronger
  setup (e.g., 3D substrate with dispersive noise).

- **ETA_TRIVIAL** (ζ in [3.7, 4.3]):
  Q scales as ε⁴ → trivial product of two linear responses. Program
  alpha DEAD in this reduction; advance program beta.

- **ETA_AMBIGUOUS** (ζ otherwise):
  Intermediate scaling. Widen amplitude range or move to 3D full v8
  (requires GPU).

## Tolerances

- H drift per run: ≤ 10⁻³ (symplectic conservation sanity check)
- Scaling exponent uncertainty: ±0.15 over 3 seeds per eps

## Artifacts

- Script: `tests/cpu/qng_eta_fluctuation_reference.py`
- Audit dir: `07_validation/audits/qng-eta-fluctuation-v1/`

## Expected runtime

<30 s wall (L=100, T=200 lu, 9 runs, all CPU numpy)

## Theoretical prediction

DER-QNG-023 gives η_ring = √(2α·√(α(α+2β))) for ring-FDT in dissipative
regime. In the non-dissipative 1D substrate probed here, a similar
FDT-like scale may emerge from the effective temperature of the
initial-condition perturbation. The specific numerical match between
measured Q and η² is deferred to a follow-up test only if this test
passes ETA_UNIVERSAL_CANDIDATE.

## Consequences

**If PASS (ETA_UNIVERSAL_CANDIDATE)**:
- Commit to program alpha
- Open DER-QNG-048 (η ↔ ℏ identification)
- Design CPU-083: measure η numeric value vs substrate parameters
- Connect to Gap 5 (cosmological α)

**If FAIL (ETA_LINEAR_RESPONSE or ETA_TRIVIAL)**:
- Program alpha not viable in minimal reduction
- Pivot to program beta (canonical quantization of orbital action J)
- Compute ∮p·dq from GPU-038 traces as first step
