---
type: test
test_id: QNG-GPU-046
category: gpu_scale
hardware: GPU
status: preregistered
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-056 (v9-probabilistic graph substrate, draft)
  - QNG-GPU-043 (deterministic FDT FAILED)
  - QNG-GPU-044 (constant-σ vacuum FDT FAILED)
  - QNG-GPU-045 (Lyapunov — if CHAOTIC, this test is primary path)
---

# QNG-GPU-046 — v9-P multiplicative-noise Langevin probe

## Purpose

Test whether state-dependent multiplicative noise (DER-QNG-056 v9-P) closes
Einstein-Nyquist FDT where constant-amplitude noise (GPU-044) failed:

```
dχ_i = [deterministic v8 drive] − γ·χ_i·dt + σ(σ_m_i)·sqrt(dt)·randn
```

with state-dependent amplitude `σ²(σ_m) = σ²_0 · (σ_m / σ_m_ref)^n`.

**Prediction** (DER-QNG-056 §Analytical derivation):
```
ℏ_local(x) = σ²(σ_m_x)·dt / ω_orb     (γ-INVARIANT by construction)
<χ_i²>_eq   = σ²(σ_m_i) / (2γ)         (1/γ scaling, unlike GPU-044)
```

If BOTH hold → v9-P mechanism validated; ℏ becomes state-local.

## Inputs

- v8 canonical substrate (`tests/gpu/qng_v8_canonical_gpu.py`)
- v8 ring formation (fresh, R1 protocol, k_gm=0.01)
- Fixed parameters:
  - `L=20, R=4, T_P1=300, T_P2=1000, T_spinup=200, T_meas=1000 lu`
  - `DT=0.025, exact_a='r1', K_GM=0.01`
  - Reference baseline: σ²_0 = 1.6e-03, n=1 (linear state-dependence)

## Protocol

### Part A — γ-scan (primary test)

Three runs at R=4, σ²_0 = 1.6e-03, n=1:
- γ ∈ {0.010, 0.020, 0.040}

After each Yoshida4 step, inject multiplicative noise:
```python
sigma_local = SIGMA_0 * (state['sm'] / SIGMA_M_REF)**(N_EXPONENT / 2)
state['chi'] += sigma_local * sqrt(DT) * randn(N_total)
```

Compute:
- `⟨χ²⟩_local` = spatial variance of χ at each node, averaged over time
- `⟨χ²⟩_ring_core` = average over |z-z_ring|<R+2 region
- `⟨χ²⟩_vacuum` = average over |z-z_ring|>R+4 region
- `ℏ_cand_core = 2γ·⟨χ²⟩_core / ω_orb`
- `ℏ_cand_vacuum = 2γ·⟨χ²⟩_vacuum / ω_orb`

### Part B — n-scan (functional form test)

At R=4, γ=0.020, σ²_0 fixed:
- n ∈ {0.5, 1.0, 2.0}  (three functional forms for σ²(σ_m))

Verify predicted scaling holds for each n.

### Part C — Control: constant σ (GPU-044 replication)

At R=4, γ=0.020, n=0 (constant σ=σ_0):
- Should reproduce GPU-044 γ-DEPENDENT result (sanity check)

## Outputs

- `07_validation/audits/qng-gpu046-v9p-langevin-v1/`
  - `hbar_local_core.csv` — ℏ_cand at ring core across γ
  - `hbar_local_vacuum.csv` — ℏ_cand at vacuum across γ
  - `chi_squared_traces.npz` — full time traces
  - `REPORT.md` — verdict

## Gates

### `V9P_PASS` (primary)
- ℏ_cand_core CV across γ ∈ {0.010, 0.020, 0.040} < 2%
- ℏ_cand_vacuum CV < 2%
- ⟨χ²⟩ scales as 1/γ at both locations (verify FDT prediction)
→ v9-P multiplicative-noise mechanism validated. DER-QNG-056 upgraded
  from draft to confirmed. Proceed with analytical derivation of σ²_0.

### `V9P_LOCAL_OK` (partial)
- ℏ_cand_local γ-invariant at each LOCATION (<2% CV)
- But ℏ_cand_core ≠ ℏ_cand_vacuum (spatial variation confirmed)
→ Confirms "ℏ is local" prediction. v9-P structurally correct.
  NOT a derivation of ℏ_SI, but demonstrates mechanism.

### `V9P_FAIL`
- ℏ_cand_local CV > 10% even with state-dependent noise
- Or: Channel D rigidity still dominates
→ v9-P falsified; only v9-G or V9-C remain.

## Tolerances

- Attractor stability: M_ring must stay bounded during measurement
  (⟨M⟩ in [100, 800], std/⟨M⟩ < 1.0)
- H drift: |ΔH/H| < 1% over T_meas
- Noise injection: verify σ_local matches analytical prediction
  within 5% at each site

## Numerical stability

- If multiplicative noise destabilizes integrator (χ diverges exponentially):
  reduce σ²_0 to 1.0e-04 and retry.
- If ring dissolves early: extend T_spinup by 200 lu.

## Runtime estimate

- 3 γ-values (Part A): 3 × 20 min = 60 min
- 3 n-values (Part B): 3 × 20 min = 60 min
- 1 control (Part C): 20 min
- **Total: ~2.5 hours on GPU** (serial, per feedback_gpu_serialization)

## Deliverables

1. Executable: `tests/gpu/qng_gpu046_v9p_langevin.py`
2. Audit: `07_validation/audits/qng-gpu046-v9p-langevin-v1/`
3. THEORY_STATE update with v9-P verdict
4. If V9P_PASS → update DER-QNG-056 status from draft to confirmed
5. If V9P_LOCAL_OK → update DER-QNG-056 with "local ℏ" revision
6. If V9P_FAIL → document as third failure in probabilistic family

## Prereg enforcement

Test is preregistered. Post-hoc parameter tuning of σ²_0 or n to match a
desired ℏ value is FORBIDDEN. If V9P_FAIL, report verbatim — don't
re-run with new parameters without updating preregistration.

## Conditional launch

This test should run ONLY IF:
- GPU-045 shows λ_max > 10⁻³ (chaotic — Hypothesis B viable), OR
- GPU-045 shows λ_max ≈ 0 (quasi-periodic) AND we explicitly want to
  test whether EXTERNAL multiplicative noise (without Ruelle-Bowen) can
  close FDT on KAM substrate

If GPU-045 quasi-periodic AND V9P also FAIL → v9-G becomes only path forward.
