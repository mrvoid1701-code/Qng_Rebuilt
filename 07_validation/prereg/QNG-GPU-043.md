---
type: test
test_id: QNG-GPU-043
category: gpu_scale
hardware: GPU
status: preregistered
author: C.D Gabriel
date: 2026-04-22
upstream:
  - DER-QNG-054 (two-channel FDT structure, analytical)
  - DER-QNG-015 (Channel D)
  - DER-QNG-030 (Channel G)
  - DER-QNG-034 (Gap 8 stability)
  - GPU-031f (orbital attractor R=4)
  - GPU-031g (orbital attractor R=3,5)
  - NOTE-QNG-017 (<L>=660 classical invariant)
---

# QNG-GPU-043 — Two-channel FDT test for emergent ℏ candidate

## Purpose

Test the DER-QNG-054 analytical prediction that
`ℏ_candidate = 2·CHI_DECAY·⟨χ²⟩/ω_orbit`
is:
1. CHI_DECAY-independent (Einstein-Nyquist cancellation), and
2. R-universal across ring radii R ∈ {3, 4, 5, 6}.

If BOTH hold → first proof-of-concept for intrinsic ℏ emergence from
v8 two-channel structure. If either fails → 17th failed ℏ program,
V9-C (external-ℏ) remains obligatory.

## Inputs

- v8 canonical substrate (`tests/gpu/qng_v8_canonical_gpu.py`,
  yoshida4_step + full Channel D/F/G).
- Ring cache infrastructure (`tests/gpu/qng_v8_ring_cache.py`) for
  R ∈ {3, 4, 5, 6} at L=28, T_P1=300, T_P2=1500.
- Fixed parameters:
  - `BETA = 0.35`, `ALPHA = 0.005`, `BETA_PHI = 0.06`, `MU_PHI = 0.857`
  - `G_V_COUPLE = 0.22`, `K_BACK = 0.10`, `K_GM = 0.01`
  - `DELTA = 0.20`, `CHI_REL = 0.01`
  - `CHI_DECAY = 0.020` (baseline); γ-scan values {0.010, 0.020, 0.040}
- No external noise, no Ξ(t) term.

## Protocol

### Part A — R-scan (baseline CHI_DECAY=0.020)

For each R ∈ {3, 4, 5, 6}:

1. Load/form ring from cache.
2. Evolve under Yoshida4 + all v8 channels active for T_spinup = 2000 lu.
3. Confirm orbital attractor: M_ring autocorrelation shows period
   T_cycle finite and ⟨M_ring⟩ bounded (no dissolve, no divergence).
4. Measurement window: T_measure = 5000 lu. Record every step:
   - `sum_chi_sq[t] = sum_i χ_i²`
   - `sum_sigma_sq[t] = sum_i σ_m_i²` (restricted to ring-core region
     |z - z_ring| ≤ R+2)
   - `M_ring[t] = N·σ_m_ref − sum_i σ_m_i`
5. Compute:
   - `⟨χ²⟩ = mean(sum_chi_sq) / N`
   - `⟨σ²⟩_core = mean(sum_sigma_sq) / N_core`
   - `ω_orbit = 2π / T_cycle`, where T_cycle = peak of M_ring
     autocorrelation
   - `ℏ_candidate(R) = 2 · CHI_DECAY · ⟨χ²⟩ / ω_orbit`

### Part B — γ-invariance check at R=4

Repeat steps 1–5 for R=4 with CHI_DECAY ∈ {0.010, 0.020, 0.040}.

Nyquist prediction: `ℏ_candidate(R=4, γ)` should be constant to ≤ 2%
across the 4× CHI_DECAY range.

### Part C — Control (S sector alone)

Run R=4 with Channel D disabled (χ ≡ 0). Confirm σ-sector dynamics
unchanged (classical symplectic attractor) and ℏ_candidate ≡ 0 by
construction.

## Outputs

- `07_validation/audits/qng-cpu102-two-channel-fdt-v1/`
  - `hbar_candidate_R_scan.csv` — R, ⟨χ²⟩, ⟨σ²⟩, ω_orbit, ℏ_candidate
  - `hbar_candidate_gamma_scan.csv` — γ, ⟨χ²⟩, ω_orbit, ℏ_candidate
  - `M_ring_autocorrelations.png` — attractor period verification
  - `REPORT.md` — verdict + tables + CV computations

## Gates

### `TWO_CHANNEL_PASS`
- CV(ℏ_candidate) across R={3,4,5,6} < 2%
- AND γ-invariance: max|ℏ_candidate(γ_i)/ℏ_candidate(γ_baseline) − 1| < 2%
- AND ℏ_candidate(R=4) in control case ≡ 0 (sanity)
→ **Open two-channel ℏ program**. Draft DER-QNG-055 elevating
  ℏ_candidate to ontology. Update DEC-QNG-007 to leave V9-C as
  dual path rather than sole path.

### `TWO_CHANNEL_R_DEPENDENT`
- CV(ℏ_candidate) across R ∈ [2%, 10%]
- OR γ-invariance violated ∈ [2%, 5%]
→ **Classical invariant of two-channel coupling**, not ℏ. Document
  as extension of NOTE-QNG-017 family (⟨L⟩=660, ⟨H⟩~−225,
  |H|·T≈40000, and now ℏ_candidate as 4th classical R-signature).
  V9-C remains sole path to ℏ.

### `TWO_CHANNEL_FAIL`
- CV(ℏ_candidate) > 10% OR γ-invariance > 5%
→ **17th failed ℏ program**. Two-channel FDT structure does not
  produce a rigid emergent action quantum. Document as NOTE-QNG-022.
  V9-C (DER-QNG-052) confirmed as obligatory external-ℏ path.

## Tolerances

- Attractor period measurement: T_cycle within ±3 lu (from FFT
  bin resolution on T_measure=5000 lu data).
- ⟨χ²⟩, ⟨σ²⟩ convergence: second half of T_measure window should
  differ from first half by < 5% (otherwise attractor not yet
  settled; extend T_spinup).

## Numerical stability

- Monitor H_v8 drift over T_measure; if |ΔH/H| > 5% → Yoshida4
  integrator breakdown, reduce dt from 0.5 to 0.25 and rerun.
- If orbital attractor dissolves before T_measure completes
  (M_ring → 0 or → ±∞) → extend T_spinup and retry; if persists,
  record as STRUCTURAL_ATTRACTOR_FAIL_R.

## Runtime estimate

- Ring formation (Phase 1+2): 2–3 min per R from scratch, <1 min
  from cache.
- T_spinup + T_measure = 7000 lu per run on L=28: ~3–5 min each
  on GPU (serial; no parallel v8 probes per feedback_gpu_serialization).
- Total: 4 R-scan runs + 2 additional γ-scan runs + 1 control =
  7 runs × 4 min ≈ 25–35 min on GPU.

## Deliverables

1. Executable: `tests/gpu/qng_gpu043_two_channel_fdt.py`
2. Audit: `07_validation/audits/qng-gpu043-two-channel-fdt-v1/`
3. THEORY_STATE.md update with verdict.
4. MEMORY.md + `memory/project_gpu043_*.md` entry.
5. If PASS or R_DEPENDENT → update DEC-QNG-007 draft.
6. If PASS → draft DER-QNG-055 (two-channel ℏ ontology promotion).

## Open questions deferred

- If PASS: what is the UV regulator? (v9-C Weyl PI still needed.)
- If PASS: how does χ-noise-like behavior emerge from deterministic
  Channel D? (Answer: σ-attractor acts as "chaotic reservoir" for χ,
  FDT-analog of fluctuating boundary in QED Casimir. Full analysis
  deferred to DER-QNG-055.)
- If R_DEPENDENT: does the R-dependence trace to ω_orbit(R) alone?
  Decompose `ℏ_candidate(R) / (⟨σ²⟩(R)/ω_orbit(R)³)` = constant
  check.
