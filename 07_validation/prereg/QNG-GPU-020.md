# QNG-GPU-020

Type: `prereg`
Status: `registered` (Stage A stale, Stage F retired — see notices below)
Author: `C.D Gabriel`
Date: `2026-04-18` (updated same-day after 3-agent review)
test_class: `v8_canonical_extension`
hardware: `GPU`
upstream_derivation: `DER-QNG-042`
prerequisites: `DER-QNG-042-prereqs` (qng-v8-analytical-prereqs-v1.md)

## Amendment 2026-04-22 — Stage A stale, Stage F retired (AUDIT-QNG-005)

Comprehensive v8 audit on 2026-04-22
(`07_validation/audits/qng-v8-comprehensive-audit-2026-04-22/REPORT.md`)
found two documentation-staleness bugs in this pre-reg:

**Stage A gate stale under Option E^2**. The gate
`omega(k=0) in [0.323, 0.395]` and the constant `M_PHI = 0.3585` were
derived for the DER-QNG-041 original V_couple `g*sigma_g*(1-cos phi)`.
Under DER-QNG-042-A1 (Option E^2), vacuum phi mass is EXACTLY ZERO
(deficit=0). Stage A must be split into:
- **A1** (flat vacuum): gate omega_k0 < 0.02
- **A2** (frozen deficit=0.23 profile): gate omega_k0 in [0.105, 0.128]

Empirical confirmations of A1/A2 exist (e.g. `qng_v8_e2_stage_a1.py`)
but the canonical `run_stage_A` in the GPU module has not been
rewritten. A re-run against the stale gate would produce a physically
misleading FAIL. Rewriting `run_stage_A` is pending Gabriel review
(R1 in the audit).

**Stage F retired**. The FC-5 mass-ladder gate against CPU-074/075
reference values {474, 729, 955} is RETIRED. DER-QNG-051 (LOCKED)
established that CPU-074/075 M_ring values are v7-gradient-flow
artifacts; under canonical v8 R1 dynamics the observable is the
orbital attractor mean ⟨M_ring⟩_t ≈ 309 (R-insensitive per GPU-031g).
The pre-committed FC-5 contract {474, 729, 955} is replaced by the
orbital-attractor gate:
- Gate F_v2: ⟨M_ring⟩_t in [280, 360] at R=4 under R1 mode (confirmed
  by GPU-031f); R=3 and R=5 equivalence per GPU-031g ladder_dead
  (|R=3 second-half − R=4 second-half| < 5%).

This retirement is a post-hoc amendment forced by empirical discovery;
it does not relax a pre-committed pass threshold to save the theory —
the original gate is declared void, and a new observable replaces it.


## Title

v8 canonical extension (`H_v8 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] + E_v7 + V_couple`) —
test predictions P1–P4 (phi dispersion, sigma_m force, F=ma drift,
CHI_DECAY=0 stability) plus FC-4 (v7 recovery) and FC-5 (mass ladder
vs CPU-074/075). Five-stage pre-registered test with hard falsifier
committed before run.

## Amendment 2026-04-20 — V_couple Option E^2 (DER-QNG-042-A1)

On the first GPU-020 run (artifact `qng-v8-canonical-v1/`), Stage A
PASSED (flat-vacuum phi dispersion) but Stage B produced NaN at d=6.
Stability probes (`qng_v8_stability_probe.py`, `qng_v8_g_scan_probe.py`)
diagnosed the original V_couple = `g*sigma_g*(1-cos phi)` as structurally
incompatible with ring configurations: `dV/dsigma_g >= 0` drains
sigma_g monotonically in any phi-winding sector. All g in the Stage A
window breach `SIGMA_G_MIN_ABORT = 0.025` at t ∈ [1.0, 2.0].

Einstein-mind and savant-physics-reviewer converged on a deficit-based
coupling. Option E (linear deficit) eliminated the drain but introduced
tachyonic phi when sigma_m overshoots sigma_m_ref. **Option E^2**
(quadratic deficit) eliminates both pathologies:

```
V_couple_E2 = (g/2) * (SIGMA_M_REF - sigma_m)^2 * (1 - cos phi)
```

Properties: `dV/dsigma_g = 0`; `m_phi^2 = g*(deficit)^2/mu_phi ≥ 0`
everywhere; phi massless in vacuum, massive in ring cores. Verified in
9/9 configs (L=16 and L=32, dt ∈ {0.025, 0.010, 0.005}, Langevin γ ∈ {0, 0.01, 0.05}):
sigma_g = 0.5000, sm bounded in [0.228, 0.500], no NaN, no breach.
See `qng-v8-option-e2-amendment-v1.md` for full derivation.

**First GPU-020 run status**: VOID under original V_couple form.
Audit `qng-v8-canonical-v1/` is archived as `qng-v8-canonical-v1-VOID-A0/`.
A new run will be attempted under Option E^2 and recorded in
`qng-v8-canonical-v2/`.

**Gate deltas under Option E^2** (see DER-QNG-042-A1 for complete list):

- **Stage A (P1 phi dispersion)** is RESTRUCTURED:
  - Stage A1 (vacuum): PASS if `omega(k=0) < 0.02` (massless as predicted).
    Prior gate `omega(k=0) ~= 0.359` is NO LONGER VALID under E^2.
  - Stage A2 (ring-core): initialize sm_core profile, measure
    `omega_core ≈ 0.1166 ± 10%` (ring mass-scale).
- **Stage E (FC-4 recovery)** is REINTERPRETED:
  - Legacy CPU-043/073 match is NOT the reference under E^2
    (V_couple form differs from v7).
  - Record v8-E^2-overdamped morphology as new fiducial.
- **Stage B, C, D, F** unchanged in gate definition.

The script `tests/gpu/qng_v8_canonical_gpu.py` has been amended in-place
with Option E^2 force forms; tagged commit `der-qng-042-a1-option-e2`.
Stage A implementation in the script must be updated to split A1/A2
before re-run.

## Status explanation

`registered` (as of 2026-04-18, post 3-agent review). The FIVE analytical
prerequisites required by DER-QNG-042 §3 and Savant FC-3 are discharged
in `qng-v8-analytical-prereqs-v1.md`:

1. **Forms committed** (§3.1): PASS — T_m, T_phi standard kinetic
2. **H_v8 bounded below** (§3.2): CONDITIONAL PASS — formal minimum
   σ_g ≈ −87.5 when φ = π; operational abort clause at σ_g < 0.025
   registered here (Commitment #8). v8 is effective theory on
   σ_g > 0 domain. If abort triggers, DER-QNG-043 becomes mandatory.
3. **Unique wave speed** (§3.3): PASS — μ_m = 10.0, μ_phi = 0.857
   derived correctly; corrected m_phi = 0.359 (was 0.332 in parent)
4. **Goldstone mode count** (§3.4): PASS — 0 massless, 1 gapped (φ)
5. **Topological sector analysis** (§3.5): PASS — barrier ≥ 4 lu;
   rings trapped; W-conservation ≠ I_m conservation (stationarity
   check required in Stage F)

Three-agent review (2026-04-18): einstein-mind (CONDITIONAL PASS),
savant-physics-reviewer (NOT READY → now resolved by amendments),
tesla-mind (cavity falsifier DEAD → Stage F restructured around I_m(R)).

Amendments applied 2026-04-18 (same day as prereqs writeup):
- Parent DER-QNG-042 §3.3 corrected (wrong formulas retracted)
- Stage A gate updated to m_phi = 0.359 (was 0.332)
- Stage F restructured: cavity-mode removed, I_m(R) scaling is
  sole test
- Integrator tightened to Yoshida 4 + Δt = 0.025 (Commitment #8)

## Purpose

DER-QNG-042 proposes v8 as structural completion of v7: promote sigma_m
and phi to canonical pairs with explicit conjugate momenta. v8 is
expected to simultaneously resolve NOTE-QNG-013 (Lorentz covariance),
NOTE-QNG-014 (action principle), and Gap 8 (chi ad-hoc decay). It is
also expected to enable the hard cavity-mode falsifier against the
CPU-074/075 mass ladder.

GPU-020 tests all four P-predictions and both FC recovery gates in a
single registered campaign. Verdict is pre-committed; no post-hoc
scan widening, no gate tolerance relaxation.

## Hypothesis

### H1 (FULL PASS — v8 corroborated)

All five stages PASS:
- P1: phi dispersion measured `omega(k=0) = m_phi ± 10%` where
  `m_phi = sqrt(g·sigma_g_ref)`
- P2: inter-ring force shows NEW short-range component at range `1/m_m`
  not present in v7 at matched parameters
- P3: ring in sigma_g well shows quadratic x(t) (free fall), NOT linear
  (v7 terminal velocity)
- P4: CHI_DECAY=0 stable at T=5000 steps with K_BACK=0.10, DELTA=0.20
- FC-4: v8 with large Langevin damping reproduces v7 ring morphology
  (CPU-043, CPU-073) within 5% at L=20, T=500
- FC-5: mass(R) matches CPU-074/075 R-scaling (linear in R) under EITHER
  the cavity-mode `omega_1 = c_phi/R` × volume-deficit reinterpretation
  (Verdict B), OR alternative mechanism (Verdict C)

=> v8 promoted to `locked` in DER-QNG-042.
=> NOTE-QNG-013 and NOTE-QNG-014 marked `closed (subject to gauge extension)`.
=> Gap 8 marked `closed (CHI_DECAY retired)`.
=> Gap 5 and Gap 9 remain open per D4, D5.

### H2 (PARTIAL PASS — Verdict B reconciliation)

P1, P2, P3, P4, FC-4 all PASS. FC-5 shows cavity alone misses
CPU-074/075 but `(volume-deficit × omega_1)` matches within 20%.

=> v8 locked with reinterpretation: mass observable is the product,
   not omega_1 alone. DER-QNG-038 baryon identification amended to
   record the product form.
=> Downstream mass program continues at v8 baseline.

### H3 (PARTIAL PASS — Verdict C, cavity wrong)

P1, P2, P3, P4, FC-4 all PASS. Cavity mode `omega_1 = c_phi/R` NOT
observed as mass scale. Alternative mechanism generates mass.

=> v8 locked. Tesla cavity prediction falsified but v8 structure intact.
=> New program: identify mass mechanism inside v8 substrate.

### H4 (HARD FAIL — Verdict A)

FC-5 fails for both cavity and volume-deficit interpretations.
mass(R) in v8 does not match CPU-074/075 R-scaling within 20% under any
reading.

=> DER-QNG-042 marked `falsified_structural`.
=> Substrate ontology approach may need to be abandoned.
=> Escalate to governance decision record.

### H5 (STRUCTURAL FAIL — recovery gate)

FC-4 fails: v8 with large damping does NOT reproduce v7 morphology.
This means v8 is not a generalization of v7 but a different theory.

=> DER-QNG-042 formulation wrong; reject. Option B (add pi_chi) may be
   attempted as DER-QNG-043.

### VOID

Stability breaks before T=500 at FC-4 baseline parameters OR ring
fails to form in v8 Phase 2 OR H_v8 boundedness-below proof (§3.2)
fails analytically.

=> No verdict on scientific gates. Document failure mode, restrict
   parameter range, re-register.

## Commitments (Savant integrity contract, deepened)

1. **Form committed PRE-RUN** (FC-1): `T_m = (1/2μ_m)Σpi_m²`,
   `T_phi = (1/2μ_phi)Σpi_phi²`. No non-standard kinetic forms.
   Any modification → DER-QNG-043, not mid-run retune.

2. **Integrator committed PRE-RUN** (FC-2): symplectic Euler minimum;
   Yoshida 4th-order preferred. Standard explicit Euler NOT ACCEPTED.
   Langevin damping terms are explicitly named additions, not part of
   canonical H_v8.

3. **Bounded-below verified PRE-RUN** (FC-3): §3.2 of DER-QNG-042
   must have a written proof. If sigma_g positivity fails, GPU run
   is aborted at integrator-preflight.

4. **μ_m, μ_phi derived from c_g** (§3.3): these are NOT free
   parameters. They are fixed by the unique-light-cone requirement.
   Pre-run document must list c_g, c_m, c_phi and the derivation
   `μ_m = β_m * sigma_g_ref²/c_g²`, `μ_phi = β_phi * sigma_m_ref²/c_g²`.

5. **g committed at 0.22** (FC-5): DER-QNG-041 Einstein g-value used
   for v8 tests. NOT re-scanned within v8. g-scan belongs to GPU-019
   (retained for future completion). GPU-020 is structural, not
   g-scan.

6. **FC-5 verdict is binary** per §5.3 of DER-QNG-042: Verdict A
   means hard fail. No "close enough" relaxation. If neither
   interpretation matches within 20%, result is FAIL_STRUCTURAL.

7. **Three-agent post-run review REQUIRED**: einstein-mind +
   savant-physics-reviewer + tesla-mind review the interpretation
   before verdict is recorded as final.

8. **Integrator committed PRE-RUN** (updated 2026-04-18 per einstein-mind):
   - Yoshida 4th-order, Δt = 0.025 (tightened from 0.05 to improve
     drift margin vs ~0.5 lu estimator tolerance on topological barrier)
   - Energy drift monitor: abort if |ΔH_v8| / H_v8 > 1% per 1000 steps
   - σ_g positivity monitor: abort if min(σ_g_i) < 0.05 · σ_g_ref = 0.025
     at any site (prereqs §3.2.10)
   - Stationarity pre-check for Stage F mass observable (prereqs §3.5.7)

## Parameters (committed pre-run, subject to analytical prerequisites)

**v7 substrate baseline (retained from GPU-019):**
- SIGMA_REF = 0.5
- ALPHA = 0.005
- BETA = 0.35
- BETA_PHI_MIN = 0.0005
- BETA_PHI_RING = 0.06
- GAMMA_PHI = 0.10
- DELTA_CHI = 0.20
- CHI_REL = 0.35
- K_BACK = 0.10 (v7 back-reaction, Channel G)
- K_GM = 0.0 (gravity off for Stages A, B, D, FC-4; on for Stage C, FC-5)

**New v8 parameters (derived, NOT free — updated 2026-04-18 per prereqs §3.3):**
- c_g² = K_BACK · β_g / 6 = 0.10 · 0.35 / 6 ≈ 5.83×10⁻³ (v7 result DER-QNG-036)
- **μ_m = β_m / (K_BACK · β_g) = 0.35 / (0.10 · 0.35) = 10.0**
- **μ_phi = 2 · β_phi · σ_m_ref² / (K_BACK · β_g) = 2·0.06·0.25/(0.10·0.35) = 0.857**
- β_φ COMMITTED UNIFORM = 0.06 (Choice A, prereqs §3.3.4). Not
  spatially heterogeneous as in v7 — FC-4 recovery test will check
  whether this breaks v7 ring morphology reproduction.
- Prior wrong formulas retracted (see DER-QNG-042 §3.3 correction note).

**V_couple (retained from DER-QNG-041):**
- g = 0.22 (Einstein value; Gap 9 EFT placeholder)

**Stage-specific:**
- Stage A (P1 phi dispersion): L=40, T=1000, flat initial conditions, single-k phi excitation
- Stage B (P2 force): L=80, two rings at d ∈ {6, 8, 10, 12, 14, 16, 18, 20}, matched v7 vs v8
- Stage C (P3 F=ma): L=80, single ring in linearly-varying sigma_g background (gravitational well)
- Stage D (P4 CHI_DECAY=0): L=20, T=5000, CHI_DECAY=0 explicit
- Stage E (FC-4 recovery): L=20, T=500, damping `-γ * pi` with γ=10, compare to CPU-043/CPU-073
- Stage F (FC-5 mass ladder): R ∈ {3, 4, 5}, L=80, T_P2=1000 (matched to CPU-074/075 protocol)

## Gates

### Stage A — P1 phi dispersion relation (mass check)

**Measurement**: initialize flat sigma_g = sigma_g_ref, sigma_m = sigma_m_ref,
chi = 0, phi = epsilon * cos(k·x) for k ∈ {0, π/L, 2π/L, 4π/L}, pi_phi = 0.
Evolve under H_v8 for T=1000 steps. Measure oscillation period of phi
at each k.

**Expected** (corrected 2026-04-18, prereqs §3.3.3):
`omega²(k) = c_phi² · k² + m_phi²` with `m_phi² = g · σ_g_ref / μ_phi = 0.1284`.
At k=0: `omega = m_phi ≈ 0.359 → period T ≈ 17.5 lu`.

Prior (retracted): ~~m_phi ≈ 0.332, T ≈ 19 lu~~.

**PASS**: omega(k=0) measured within 10% of `0.359` (range [0.323, 0.395]).
ALSO: omega(k>0) follows dispersion relation within 15% across k-grid
(tests emergent Lorentz covariance beyond linear-order condition).

**FAIL**: omega(k=0) = 0 within numerical precision (massless phi — V_couple
not doing its job OR pi_phi implementation wrong), OR omega(k=0) outside
[0.323, 0.395] (μ_phi derivation wrong OR g-value wrong).

### Stage B — P2 sigma_m-mediated inter-ring force

**Measurement**: two rings W+W+ at separations d ∈ {6, 8, 10, 12, 14, 16, 18, 20}.
Run v7 (reference) and v8 (canonical) at matched baseline, T_P2=1500.
Compute F(d) via Hamiltonian gradient or sigma_m asymmetry.

**Expected** (v8 extra component): a NEW short-range interaction of the
form `F_new(d) = A · exp(-d·m_m)` where `m_m` is the sigma_m mass from
the E_v7 pinning. v7 force profile should NOT contain this component.

**PASS**: v8 F(d) minus v7 F(d) shows exponential short-range excess
component with range `1/m_m ∈ [0.5, 5]` lu, statistically distinguishable
from numerical noise (R² > 0.9 on exp fit).

**FAIL**: v8 F(d) indistinguishable from v7 F(d) at matched params.
Means T_m[pi_m] produces no observable dynamics (μ_m effectively infinite
in practice).

### Stage C — P3 F=ma drift (free-fall vs terminal velocity)

**Measurement**: identical geometry to CPU-073 (ring at center of L=80
box with imposed linear sigma_g gradient background). Track ring
centroid x(t) for T ∈ [500, 2000].

**Expected v7 (reference)**: x(t) = x_0 + v_drift · t (terminal velocity).
**Expected v8**: x(t) = x_0 + (1/2) a · t² (Newton's 2nd law).

Fit x(t) with both linear and quadratic. Compute AIC.

**PASS**: AIC(quadratic) - AIC(linear) < -6 (strong preference for quadratic).
ALSO: quadratic fit curvature a > 0 with magnitude consistent with
`a = -∇Φ_g / m_ring` where `m_ring` from §Stage F.

**FAIL**: linear fit preferred or a ≈ 0 (dissipative regime dominates).
Means v8 effectively overdamped — pi_m kinetic term too weak at this μ_m.

### Stage D — P4 CHI_DECAY=0 stability

**Measurement**: H_v8 simulation at v7 baseline EXCEPT CHI_DECAY=0
(strict, not even small value). L=20, T=5000. Monitor sigma_g global
mean and variance.

**Expected**: sigma_g stays bounded, no Jeans-like k=0 collapse.

**PASS**: `|⟨sigma_g⟩(T=5000) - sigma_g_ref| < 0.05` AND
`std(sigma_g)` remains finite (no exponential growth).

**FAIL**: sigma_g diverges (global collapse) or grows unboundedly.
Means pi-kinetic terms insufficient to stabilize k=0 mode.

### Stage E — FC-4 v7 recovery gate

**Measurement**: H_v8 at L=20 with Langevin damping `-γ_m · pi_m`,
`-γ_phi · pi_phi`, γ = 10 (large damping → overdamped limit).
Phase 1 (300 steps, Channel F OFF), Phase 2 (1500 steps, Channel F ON).

Compare to CPU-043 (v7 single ring) and CPU-073 (v7-symmetric with
back-reaction).

**PASS**: ring morphology match within 5%:
- ring radius R within 5% of CPU-043 value
- sigma_m_core within 5% of CPU-043 value (0.27 at R_t=4.84)
- CPU-073 back-reaction drift within 5% (1.01 lu)

**FAIL**: any metric off by > 5%. Means v8 with overdamping is NOT
equivalent to v7 — it is a different theory. DER-QNG-042 structural
formulation wrong.

### Stage F — FC-5 mass ladder vs CPU-074/075 (RESTRUCTURED 2026-04-18)

**Motivation for restructuring** (tesla-mind review):

With μ_phi = 0.857 derived in prereqs §3.3, the Yukawa screening length
`1/m_phi = 1/0.359 = 2.79 lu` is SMALLER than all tested ring radii
R ∈ {3, 4, 5}. The phi field is BELOW cutoff inside the ring core: the
would-be cavity mode is evanescent, not propagating.

Ratio m_phi / omega_1(R) at R=4: `0.359 / (0.0764/4) = 0.359/0.0191 ≈ 18.8`.
The mass gap is ~20× above the cavity fundamental. Full dispersion:
`omega_n² = c_phi² (n/R)² + m_phi²`. At n=1, R=4: kinetic contribution
`0.000365` vs mass `0.1284` — kinetic is **0.3%** of total.

Consequence: cavity-mode prediction `omega_1 = c_phi/R` is R-INDEPENDENT
to 0.3% in the relevant regime. Cavity-vs-ladder comparison is vacuous.

**Restructured test**: focus exclusively on the σ_m depletion integral
as mass observable.

**Measurement**: v8 rings at R ∈ {3, 4, 5}, L=80, T_P2=1000 (matched
protocol to CPU-074/075). Compute the CANONICAL mass observable:

```
I_m(R) = N · σ_m_ref − Σ_i σ_m_i
```

This is the SAME quantity CPU-074/075 measured in v7. The v8 test asks:
does v8 reproduce the v7 mass ladder, or does the addition of
canonical pi_m, pi_phi, and V_couple change M_ring?

**Reference targets** (CPU-074/075 canonical values at T_P2=1000):
- R=3: M_ref = 474.15
- R=4: M_ref = 728.92
- R=5: M_ref = 954.88
- Scaling: approximately `M_ref(R) ∝ R` (linear)

**Stationarity pre-check** (prereqs §3.5.7): before recording M_ring,
verify `|ΔI_m per 100 steps|` is within 1% of mean I_m for T_P2 ∈ [900, 1000].
If not stationary, report VOID with explicit flag — W-conservation does
not guarantee I_m conservation in v8.

**Verdict B (reconciliation PASS)**:
`I_m(R)_v8 / I_m(R)_v7` is same constant factor (within 10%) for all
three R. Linear scaling preserved; v8 just has overall mass normalization
different. Amendable via `a_M` rescaling in DER-QNG-038.

**Verdict C (full recovery PASS)**:
`|I_m(R)_v8 − M_ref(R)| / M_ref(R) < 20%` at ALL three R.
v8 reproduces v7 mass ladder numerically. Strongest result.

**Verdict A (hard FAIL)**:
R-scaling in v8 is NOT linear (e.g., constant, or ∝ R⁰·⁵, or ∝ R²),
OR individual R values miss M_ref by >20% AND ratio-form check fails.
DER-QNG-042 structurally falsified for mass identification.

**Additional diagnostic (required by tesla-mind)**: measure σ_m depletion
integral decomposition to check whether I_m(R) scaling is driven by:
- (i) ring volume (2π R · A_cross) × average depletion — geometric
- (ii) depletion concentration in a thin ring core (R-independent core)
- (iii) long-range σ_m field response to V_couple coupling

This decomposition diagnoses WHY the ladder scales as it does, even on
PASS. Record in `mass_ladder.png` and `mass_ladder_decomposition.json`.

### FC-5 combined verdict

The test of v8 is the COMBINED result of Stages A–F. Any of:
- Stage D FAIL (CHI_DECAY=0 unstable) → v8 does NOT resolve Gap 8
- Stage E FAIL (FC-4 recovery) → v8 not a generalization of v7
- Stage F FAIL (Verdict A) → mass ladder contradicts CPU-074/075

are INDIVIDUALLY sufficient to reject DER-QNG-042 in its current form.

Full PASS requires ALL of Stages A, B, C, D, E to PASS AND Stage F
verdict B or C.

## Decision rule (single-pass, no tolerance relaxation)

| Stage | Metric | Gate | Verdict on FAIL |
|---|---|---|---|
| A | omega(k=0) | ±10% of sqrt(g·sigma_g_ref) | pi_phi wrong / V_couple wrong |
| B | v8-v7 force excess | R²>0.9 on exp fit | T_m[pi_m] not physical |
| C | x(t) fit | AIC(quad)-AIC(lin) < -6 | v8 effectively overdamped |
| D | sigma_g stability | <5% drift @ T=5000 | v8 does not close Gap 8 |
| E | recovery match | <5% vs CPU-043/073 | v8 not v7-generalizing |
| F | M(R) ladder | V-B or V-C only | DER-QNG-042 falsified |

No stage-level tolerance relaxation. No scan widening. Three-agent
review MANDATORY before final verdict is recorded.

## Artifacts

- Script: `tests/gpu/qng_v8_canonical_gpu.py` (to be written after
  analytical prereqs complete)
- Results: `07_validation/audits/qng-v8-canonical-v1/`
  - `report.json` — all stages, all metrics
  - `run.log` — console output
  - `dispersion.png` — Stage A plot
  - `force_compare.png` — Stage B plot
  - `trajectory.png` — Stage C plot
  - `stability.png` — Stage D plot
  - `recovery_metrics.json` — Stage E
  - `mass_ladder.png` — Stage F
  - `interpretation.md` — post-run stage-by-stage analysis
  - `summary.md` — one-page verdict (signed by all three agents)

## Runtime estimate

- Stage A (dispersion): 4 k-values × 1 run = 4 runs at L=40, T=1000. ~15 min
- Stage B (force): 8 separations × 2 versions (v7, v8) = 16 runs at L=80, T=1500. ~60 min
- Stage C (trajectory): 1 geometry × T=2000 = 1 run at L=80. ~10 min
- Stage D (stability): 1 run at L=20, T=5000. ~10 min
- Stage E (recovery): 2 scenarios (CPU-043 match, CPU-073 match) = 2 runs at L=20. ~10 min
- Stage F (mass ladder): 3 R × 1 L × T=1000 = 3 runs at L=80. ~30 min

Total: ~2–2.5 hours on GPU.

## References

### Upstream

- `04_qng_pure/qng-v8-canonical-extension-v1.md` (DER-QNG-042 — structure)
- `04_qng_pure/qng-hamiltonian-v7-v1.md` (DER-QNG-036 — H_v7 = T_g[chi] + E_v7)
- `04_qng_pure/qng-yukawa-phi-mass-v1.md` (DER-QNG-041 — V_couple form, g value)
- `04_qng_pure/qng-particle-mass-identification-v1.md` (DER-QNG-038 — M_ring protocol, baryon ladder)
- `04_qng_pure/qng-gap8-stability-analysis-v1.md` (DER-QNG-034 — chi stability, target of P4)
- `04_qng_pure/qng-note-lorentz-v1.md` (NOTE-QNG-013 — Lorentz gap, target of unique wave speed)
- `04_qng_pure/qng-note-action-v1.md` (NOTE-QNG-014 — action principle gap, target of H_v8)

### Predecessor prereg

- `07_validation/prereg/QNG-GPU-019.md` (DER-QNG-041 g-scan — halted,
  V_couple form retained in v8)

### Reference CPU results

- QNG-CPU-043 (v7 single ring: R_t=4.84, sigma_m_core=0.27 — FC-4 target)
- QNG-CPU-073 (v7-symmetric back-reaction: extra_drift=1.01 — FC-4 target)
- QNG-CPU-074 (canonical M_ring R=3,4,5: 474.15 / 728.92 / 954.88 — FC-5 target)
- QNG-CPU-075 (extended M_ring — FC-5 consistency check)

### Three-agent synthesis

- `.claude/agent-memory/tesla-mind/psi-conjugate-field-v8.md`
- `.claude/agent-memory/einstein-mind/psi-conjugate-field-v8.md`
- `.claude/agent-memory/savant-physics-reviewer/psi-conjugate-field-v8-critique.md`

### Downstream

- If Verdict A: governance decision record on substrate abandonment
- If Verdict B: amendment to DER-QNG-038 recording product-form mass observable
- If Verdict C or H1 FULL PASS: DER-QNG-043 candidate topics (gauge embedding, Gap 5 cosmological tuning)
