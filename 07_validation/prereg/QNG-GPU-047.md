---
type: test
test_id: QNG-GPU-047
category: gpu_scale
hardware: GPU
status: preregistered
author: C.D Gabriel
date: 2026-04-24
upstream:
  - QNG-GPU-043 (deterministic FDT, T_meas=1000 lu, FAIL)
  - QNG-GPU-045 (Lyapunov, λ_max=+0.00150/lu, H_CHAOTIC marginal)
  - QNG-GPU-046-LONG (single γ=0.020 at T_meas=10000 lu — prerequisite)
---

# QNG-GPU-047 — Long-time deterministic FDT γ-scan (Ruelle-Bowen test)

## Purpose

Test whether pure v8 deterministic dynamics produces γ-invariant emergent
ℏ at T_meas ≫ 1/λ_max (long-time Ruelle-Bowen regime).

Following GPU-045 verdict H_CHAOTIC (λ_max=+0.00150/lu, 1/λ_max≈667 lu),
we now test the γ-scan at T_meas ≥ 15 mixing times, which is roughly
10× the window used in GPU-043/044.

**Prediction if Ruelle-Bowen mechanism active**:
```
At T_meas >> 1/lambda_max:
  <chi²>(gamma) -> D_eff/gamma (equilibrium)
  hbar_cand = 2*gamma*<chi²>/omega -> 2*D_eff/omega (gamma-INVARIANT)
```

Contrast with GPU-043 result (T_meas=1000 lu, ~1.5 mixing times):
  hbar_cand scaled LINEARLY with gamma (CV 59%).

## Launch condition

**ONLY launch if GPU-046-LONG verdict is H_STILL_GROWING or
⟨χ²⟩ at T_meas=10000 lu differs substantially (>30%) from GPU-043
baseline of 1.63e-04.**

If GPU-046-LONG shows ⟨χ²⟩ plateau at source-limited value → FDT
never activates even at long times → GPU-047 would waste GPU cycles.
In that case, proceed to v9-P (GPU-046 stochastic) or V9-C path.

## Inputs

- v8 canonical substrate (same as GPU-043)
- L=20, R=4, T_P1=300, T_P2=1000, T_spinup=200, DT=0.025
- exact_a='r1', K_GM=0.01
- γ-scan: {0.010, 0.020, 0.040}
- **T_meas = 20000 lu** (30 mixing times — vs 1.5 in GPU-043)

## Protocol

For each γ ∈ {0.010, 0.020, 0.040}:
1. Fresh ring formation (P1+P2+spinup)
2. Measurement T_meas = 20000 lu
3. Sample χ², M_ring every 1 lu
4. Compute ⟨χ²⟩_avg over multiple time windows:
   - Early: first 2000 lu (comparable to GPU-043)
   - Middle: 5000-15000 lu
   - Late: last 5000 lu
5. Compute hbar_cand for each window

## Gates

### `RB_FDT_PASS` (emergent ℏ from pure determinism!)
- hbar_cand(γ) CV across {0.010, 0.020, 0.040} < 2% at LATE window
- AND ⟨χ²⟩(γ) scales as 1/γ at LATE window (verify within 10%)
- AND late window consistent across γ (time-reversal symmetry check)
→ **Emergent ℏ from purely deterministic v8 substrate CONFIRMED**
  First numerical demonstration. DER-QNG-056 downgraded to "unnecessary
  extension". Proceed with paper: "Ruelle-Bowen emergent hbar in a
  weakly-chaotic discrete substrate".

### `RB_FDT_MARGINAL` (partial)
- CV in [2%, 10%] → FDT approximately closes, improvement over GPU-043
  (CV 59%) but not decisive. Try L=24 or T_meas=50000 lu.

### `RB_FDT_FAIL` (Ruelle-Bowen insufficient)
- CV > 10% even at 30 mixing times
→ Weak chaos (λ_max/ω_orb ≈ 0.04) not sufficient for FDT closure.
  v9-P/v9-G become obligatory.

## Tolerances

- Stability check: M_ring bounded throughout all 60000 lu of evolution
  (per run). If ring dissolves at long T, reduce to T_meas=15000 lu.
- H_drift: accumulated over full run; < 1% acceptable.
- Windowing: first/middle/late averages must be computed separately
  (avoid averaging transient with steady state).

## Runtime estimate

Per γ-run: formation 12 min + T_meas=20000 lu × 40 steps/lu / 80 steps/s
= 12 min + 167 min ≈ 180 min = 3 hours.

Total for 3 γ values: ~9 hours on GPU (serial).

Option to reduce: do γ ∈ {0.010, 0.040} only (skip middle) — 6 hours,
still decisive for CV.

## Falsifiability

If RB_FDT_FAIL → definitive closure of "emergent ℏ from deterministic
v8". V9-C becomes obligatory path; v9-P/v9-G remain alternatives.

If RB_FDT_PASS → falsifies both my prediction (H_QUASIPERIODIC)
and Einstein-mind's (hbar axiomatic). Would reopen the entire emergent
ℏ program on firmer ground.

## Dependencies

Upstream:
- DER-QNG-054 (two-channel FDT analytical structure)
- DER-QNG-042 (v8 canonical extension)
- GPU-045 REPORT (establishes λ_max baseline)

Downstream (if PASS):
- DER-QNG-057 (to write): "Ruelle-Bowen derivation of ℏ in QNG v8"
- CLAIM-QNG-### (new): "ℏ emergent from deterministic chaos in v8"
- DEC-QNG-008 rewrite: v8 self-contained; V9-C deferred
