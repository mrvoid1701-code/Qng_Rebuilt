# QNG-GPU-024 ring stability probe — Interpretation (structural methodology finding)

Type: `note`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-20`
Audit: `qng-v8-ring-stability-v1`
Upstream: `QNG-GPU-022` + `QNG-GPU-023` (σ_m-scan saturation lineage)
Companion: `qng_v8_ring_stability_probe.py`, `report.json`, `run.log`

---

## 1. Pre-registered question

After GPU-023 ruled out candidate #1 (detector window clipping),
candidate #3 (ring self-distortion from post-cache rescaling) was
the leading suspect for GPU-022 high-s saturation. Direct test:
evolve scaled ring alone (no pulse) for T_track=250 lu, monitor
structural drift.

Pre-committed thresholds (for s=1.4 vs s=1.0 contrast):
- H_DISTORTION_CONFIRMED: s=1.4 ≥5% drift AND s=1.0 all <1%
- H_DISTORTION_REJECTED: s=1.4 all <2%
- H_DISTORTION_PARTIAL: s=1.4 in (2%, 5%)

## 2. Configuration

- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (M_ring=176.85)
- v8 Phase-2 dynamics during T_track: v_couple_on=True, CHI_DECAY=0.020
- T_track = 250 lu (matches GPU-022/023 bending measurement)
- s ∈ {0.7, 1.0, 1.4}, sample every 10 lu

## 3. Results

| s | M_ring(0) | M_ring range | rel drift % | max RMS drift (% of SIGMA_M_REF) |
|---|-----------|--------------|-------------|-----------------------------------|
| 0.70 | 123.80 | [124, **1380**] | **+1015%** | 23.2% |
| 1.00 | 176.85 | [177, **1419**] | **+702%** | 28.5% |
| 1.40 | 247.59 | [248, **1547**] | **+525%** | 36.3% |

(r_CM metric is invalid — sigma_m develops regions > SIGMA_M_REF, making
signed delta negative and the naive centroid fall outside the lattice.
Fix: use |delta| weighting. Flag for re-measurement if r_CM is needed;
the M_ring and RMS_drift metrics stand.)

Verdict (pre-committed logic): **H_DISTORTION_MIXED** — neither confirmed
(s=1.0 is NOT all <1%) nor rejected (s=1.4 is NOT all <2%) nor partial
(all s are in the big-drift regime).

## 4. Primary interpretation — candidate #3 as originally framed is RULED OUT

**Candidate #3** posited that post-cache rescaling specifically at s≠1
causes ring distortion. The data shows:

- ALL s values exhibit 500–1000% M_ring drift
- s=1.0 (the "equilibrium" reference, no rescaling applied — identical
  to the cached ring used in ALL probes in this lineage) also destabilizes
- Relative drift order: s=0.7 > s=1.0 > s=1.4, i.e. SMALLER initial
  scaling shows GREATER relative drift — opposite of what candidate #3
  predicted

⇒ candidate #3 as pre-registered is **RULED OUT**: instability is not
s-scaling-specific. All three rings converge to similar chaotic attractors
regardless of initial deficit magnitude.

## 5. Deeper structural finding — the cached ring is NOT at v8 Phase-2 equilibrium

The cached ring was formed via Phase-2 dynamics (v_couple_on=True,
CHI_DECAY=0.020) over T_P2=1000 lu, reaching M_ring=176.85. Continuing
these SAME dynamics past T_P2=1000 reveals the ring is NOT at a stable
fixed point — it immediately begins large oscillations:

- By t=50 lu past cache, M_ring has jumped to ~1400 (8× the cached value)
- Subsequent samples show chaotic-looking oscillations between ~500 and ~1500
- Eigenvalue-like behavior suggests an unstable or limit-cycle attractor

This matches the CLAUDE.md comment that v8 rings are "dynamic patterns,
not static solitons" but goes further — the cached state at T_P2=1000 is
**metastable**, not a true Phase-2 fixed point.

Consistent with the CLAUDE.md three-phase protocol: "Phase 2 (Channel F
active, CHI_DECAY=0.020) → ring forms. Phase 3 (optional 1000 conservative
steps: no A, no F, no chi_decay) → mass measurement." Phase 3 is
EXPLICITLY conservative for measurement; the cached ring's M_ring=176.85
is exactly conserved under Phase-3 dynamics (CLAUDE.md: "Under Phase-3
dynamics, sum(sigma_m) is exactly conserved"), but NOT under Phase-2.

## 6. Critical implication — all bending measurements in this lineage used Phase-2 during T_track

GPU-021 (A-scan), GPU-022 (σ_m-scan), GPU-023 (wide-detector) all call:
```
yoshida4_step(state, DT, nb_idx, v_couple_on=True, chi_decay=CHI_DECAY_V7)
```
during T_track=250 lu.  This is **Phase-2 dynamics**, under which the
ring is unstable (this audit).  The bending measurement therefore does
NOT measure "α(pulse through static M=177 ring)". It measures
"α(pulse through chaotic time-varying ring whose initial condition has
M=177·s)".

**Why GPU-021/022/023 still produced coherent data**: the subtraction
`φ_pulse = φ_rp − φ_bg` cancels the ring's chaotic dynamics (present in
both runs) and isolates the pulse perturbation. The pulse is small (A=0.05),
so it does not significantly alter the ring's chaotic background. Thus
α_meas is a well-defined quantity — just NOT what the scalar theory
predicts it to be.

**The theoretical α_scalar_th** uses the INITIAL cached ring profile
(straight-line integral of Δ²·∂_y Δ). But during T_track, the actual ring
bears no resemblance to this profile. The ~20% narrow-detector bias
revealed in GPU-023 and the b>R sign puzzle may have a common root:
α_meas probes the time-averaged chaotic-ring response, which has little
to do with the static-ring scalar prediction.

## 7. What survives, what doesn't

| Claim | Status after this audit |
|-------|-------------------------|
| α_meas non-monotonic in initial s (GPU-022) | **Observed, mechanism unclear** — may reflect initial-condition-dependent attractor statistics, not any candidate mechanism |
| Low-s slope ≈ 2 (GPU-022 +2.09, GPU-023 +2.54) as H_tensorial corroboration | **Weakened** — the slope may reflect initial-condition sensitivity, not the DER-QNG-046 m_eff² ∝ Δ² law |
| Detector ±20% bias (GPU-023) | Stands — purely methodological, independent of ring dynamics |
| In-core eikonal bending PASS (k-scan) | **Likely survives** — λ < R, b ≤ R regime; pulse traverses core in short time; ring oscillation impact minimized (needs verification) |
| Shapiro delay PASS (DER-QNG-044) | **Likely survives** — delay was consistent across multiple probe configurations; single-ring state was cached similarly but pulse traversed through core in shorter time |
| CPU-081 m_eff²/ω² = 0.032 (evanescent candidate #2 ruled out) | Stands for the CACHED state. During actual dynamics, the instantaneous m_eff² is different. Conclusion (no evanescent barrier) unchanged |

## 8. Recommended next steps

1. **QNG-GPU-025 (highest priority)**: repeat GPU-022 σ_m-scan but with
   **Phase-3 conservative dynamics** during T_track (v_couple_off for ring
   background?; OR v_couple_on=True but chi_decay=0 AND Channel F off).
   Goal: stable-ring bending measurement. If α_meas(s) is monotonic and
   matches scalar §13 prediction, the GPU-022 saturation is an
   instability artefact. Requires adding a "measurement mode" to
   yoshida4_step or a separate Phase-3-compatible step function.

2. **Fix stability probe metric**: rerun with |delta|-weighted r_CM
   (QNG-GPU-024 v2) if r_CM displacement is needed for any future claim.
   Low priority — M_ring and RMS_drift already establish the finding.

3. **Ring-dynamics characterisation (CPU-077 territory)**:
   is the oscillation periodic, chaotic, or driven? Fourier-analyse
   M_ring(t) on longer runs (T ~ 2000 lu, sample every 1 lu) to find
   characteristic timescales. If ring has a clean oscillation period
   τ_ring, could one instead measure α_meas averaged over an integer
   multiple of τ_ring?

4. **Theory audit**: the v8 Hamiltonian H_v8 = T_g + T_m + T_φ + E_v7 + V_couple
   should have a true equilibrium for a ring state. If the cached state
   is only metastable under Phase-2 dynamics, what IS the true
   Hamiltonian equilibrium for a ring-like configuration? Does it even
   exist, or does the ring necessarily oscillate under symplectic evolution?
   This touches NOTE-QNG-014 (action principle) and Gap 8 (chi
   stability) — possibly re-opens them.

## 9. Status updates to propagate

- **DER-QNG-046 promotion item 2b** (s-scaling, "tensorial corroborated"):
  downgrade from "corroborated" to "**suspect** — observed slope may
  reflect ring-instability dynamics, not m_eff² ∝ Δ² law"
- **DER-QNG-046 promotion item 2d** (candidate #1 — detector clipping):
  remains RULED OUT
- **New item 2e** (ring instability under Phase-2): **OPEN** — the
  measurement protocol is structurally compromised; needs
  Phase-3-mode repeat
- **Candidate #3** (ring self-distortion, s-specific): **RULED OUT** in
  the s-specific sense; replaced by **finding 2e**: instability is
  s-independent
- **Candidates #4** (path-curvature lensing): still open but now even
  less useful to test until measurement protocol is fixed

## 10. Artifacts

- `report.json` — full M_ring(t) trajectories at 25 time samples per s
- `run.log` — console output including per-sample metrics
- `interpretation.md` — this file

Total runtime: 9.8 min (3 × 196 s evolutions).

---

## Appendix: scope of prior-claim correction needed

If Phase-3 mode re-runs (GPU-025) REPRODUCE α_meas values close to the
Phase-2 results, the instability was irrelevant (subtraction truly canceled
it) and all prior bending conclusions hold. If they DIFFER significantly,
GPU-021/022/023 data must be reinterpreted. Either way, **GPU-025 is the
load-bearing next test**.
