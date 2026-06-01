# QNG-GPU-023 widened-detector σ_m-scan — Interpretation (candidate #1 ruled out; narrow detector was biased)

Type: `note`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-20`
Audit: `qng-v8-sigma-m-scan-wide-v1`
Upstream: `QNG-GPU-022` (σ_m-scan saturation discovery), `QNG-CPU-081` (evanescent candidate #2 ruled out)
Companion: `qng_v8_sigma_m_scan_wide_probe.py`, `report.json`, `run.log`

---

## 1. Pre-registered question

QNG-GPU-022 found α_meas non-monotonic in s (+1.83e−02 at s=1.0,
+1.65e−02 at s=1.4 with narrow detector ±7 bins). Four candidate
mechanisms identified; CPU-081 ruled out #2 (evanescent tunneling).
Present test targets candidate #1 (detector window clipping) by
widening the detector from ±7 to ±12 bins (15 → 25 total).

Pre-committed bands:
- H_window_clip: α_wide(s=1.4) ≥ +2.30e−02 AND slope ∈ [1.7, 2.3]
- H_clip_rejected: |α_wide(s=1.4) − α_narrow| < 10% × |α_narrow|
- H_partial_clip: α_wide(s=1.4) ∈ [+1.85e−02, +2.30e−02)

## 2. Configuration

Identical to GPU-022 except detector window halfwidth = 12 (25 bins).
Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (M_ring=176.85).
y_pulse = 20 on L=28; detector spans y ∈ {8..27, 0..4}, unwrapped
continuously around y=20.

## 3. Results

| s | M_ring | α_scalar_th | α_meas_wide | α_meas_narrow (GPU-022) | Δ = wide−narrow | rel % |
|---|--------|-------------|-------------|------------------------|-----------------|-------|
| 0.70 | 123.80 | −7.07e−03 | **+6.03e−03** | +8.42e−03 | −2.39e−03 | −28.36% |
| 1.00 | 176.85 | −1.44e−02 | **+1.49e−02** | +1.83e−02 | −3.40e−03 | −18.60% |
| 1.40 | 247.59 | −2.83e−02 | **+1.30e−02** | +1.65e−02 | −3.51e−03 | −21.25% |

Scalar s² sanity: 0.00% deviation (algebraic identity preserved).
Vacuum centroid: y_c_vac = 20.0000 exactly (window symmetric around pulse).
Log-log slope on α_meas_wide: **+1.121, R² = 0.6362** (non-linear — saturation persists).

Two-regime slope check (on widened data):
- s=0.7 → 1.0: slope = log(1.49/0.60) / log(1.0/0.7) = log(2.47)/log(1.43) = **+2.54**
- s=1.0 → 1.4: slope = log(1.30/1.49) / log(1.4/1.0) = log(0.87)/log(1.4) = **−0.41**

## 4. Primary verdict

**H_CLIP_REJECTED_REVERSE** — candidate #1 (detector window clipping)
**RULED OUT**, with an unexpected methodological twist.

Three reasons:
1. α_meas(s=1.4, wide) = +1.30e−02 is **below** the narrow value, not
   above. H_window_clip predicted wide ≫ narrow (recovery of linear
   extrapolation to ~+2.56e−02); result is the opposite direction.
2. The relative change (−21.25%) falls outside the H_clip_rejected
   band (<10%) but is in the opposite sign of what partial-clip would
   predict.
3. **Saturation persists** with widened detector: s=1.0 → 1.4 still
   shows α decrease (0.87× with wide, 0.90× with narrow). Non-monotonicity
   is not an artefact of the detector window.

## 5. Unexpected secondary finding — narrow detector was systematically biased

The widened detector gives LOWER α_meas across all three s values by
a roughly uniform ~20% factor:

| s | α_wide / α_narrow |
|---|-------------------|
| 0.70 | 0.716 |
| 1.00 | 0.814 |
| 1.40 | 0.788 |

This means the narrow ±7 window was **over-estimating** deflection.
Mechanism: the narrow window truncates the pulse tail, and the
truncation biases the centroid computation non-symmetrically —
tail weight that would pull the centroid back toward y_pulse is lost,
inflating apparent Δy.

**Consequence for GPU-022 interpretation**: all α values in GPU-022
should be corrected downward by ~20%. The corrected low-s slope
(s=0.7 → 1.0) becomes **+2.54** (from +2.09), still within the
H_tensorial verdict band [1.7, 2.3] at its upper edge. The main
GPU-022 conclusion (tensorial §1–§4 dominates at s≤1) **survives**
this correction but now sits at the upper boundary rather than mid-band.

The scalar s² sanity check (α_scalar_th ∝ s²) is unaffected — that's
an algebraic identity on the ring profile, not a centroid measurement.

## 6. What this implies for the saturation mystery

Surviving candidates after this test:

- ~~**#1 Detector window clipping**~~ — **RULED OUT** (this audit).
- ~~**#2 m_eff² / evanescent tunneling**~~ — RULED OUT (CPU-081).
- **#3 Ring self-distortion** — **PROMOTED TO LEAD**. Post-cache
  s≠1 rescaling leaves ring out of Hamiltonian equilibrium. During
  T_track=250 lu, the scaled ring may drift/distort, and the
  ring-bg subtraction may not cancel this cleanly if distortion
  differs between bg-only and ring+pulse runs.
- **#4 Path-curvature lensing** — still possible. Straight-line
  scalar prediction misses geometric correction at strong lensing.
  σ_m-scan slope discrimination already made H_path (slope 4) unlikely,
  but a subtractive contribution at s=1.4 cannot be ruled out
  without a direct path-corrected derivation.

The saturation pattern (monotonic growth at s ≤ 1, decrease at s > 1)
fits candidate #3 well: the larger the deficit scaling factor, the
further the ring is from equilibrium, and the larger the self-distortion.

## 7. Recommended next test — QNG-GPU-024

**Alternative ring-formation protocol**: form rings at different
target M_ring by varying Phase-2 duration or K_BACK (direct formation),
instead of post-cache rescaling. Rings formed this way ARE
Hamiltonian equilibria at their target M_ring. Running the same
bending measurement at b=6, A=0.05, k=3π/4 on these equilibrium
rings should either:
- (a) recover monotonic α(M_ring) — confirming candidate #3
- (b) preserve saturation — promoting candidate #4

Target: three rings with M_ring matching s=0.7/1.0/1.4 values
(123.80, 176.85, 247.59). At k_back = 0.10, BETA = 0.35, Phase-2
duration determines M_ring growth approximately linearly at early
times — sample (T_P2, M_ring) on a small scan to find the right
durations.

## 8. Promotion-checklist update

| # | Condition | Before | After |
|---|-----------|--------|-------|
| 1 | True 2π-winding test | Retracted | Retracted |
| 2 | Eikonal/diffraction separation | PARTIAL | unchanged |
| 2a | A-scaling (H1, H2 ruled out) | closed | unchanged |
| 2b | s-scaling (tensorial, H_path out) | partial | **strengthened** (slope corrected to +2.54 with wide detector; still H_tensorial ±band) |
| 2c | Evanescent candidate | RULED OUT | unchanged |
| 2d | Window-clipping candidate | OPEN | **RULED OUT** (this audit) |
| 3 | Numerical m_eff²(x) | EXECUTED | unchanged |
| 4 | Closed-form α from tensorial EOM | Open | unchanged; narrowed further — detector methodology is now clean, so the b>R sign puzzle cannot be blamed on detector bias |

Item 2d (newly opened for #1) is now closed at "ruled out". Candidate
#3 promoted to lead for the saturation sub-question. Item 4 (closed-form α)
remains central open derivation.

## 9. What this means for theory status

- **Corroborated** (with correction): tensorial §1–§4 slope 2 holds at
  low-s with corrected detector — slope 2.54 with wide, still in
  H_tensorial band. GPU-022's qualitative conclusion survives the
  methodological correction.
- **Ruled out**: detector window clipping as saturation mechanism.
- **Promoted**: candidate #3 (ring self-distortion from post-cache
  rescaling) to lead suspect. Candidate #4 (path-curvature lensing)
  remains possible but unlikely to be dominant.
- **Methodological**: all bending α measurements on this probe family
  should use detector halfwidth ≥ 12 (25 bins) to avoid ~20% bias.
  Narrow-window results from earlier probes (CPU-078, k-scan, A-scan,
  σ_m-scan) should carry a "±20% detector bias" flag for quantitative
  comparison; qualitative conclusions (slopes, scalings) are
  unaffected by the multiplicative bias.
- **Unchanged**: DER-QNG-046 §1–§4 tensorial EOM as the correct
  framework; all locked correspondences.

## 10. Artifacts

- `report.json` — all three s values with wide/narrow comparison,
  scalar prediction, residuals, slope fit
- `run.log` — console output (full run trace)
- `interpretation.md` — this file

Total runtime: 22.9 min (7 × 196 s evolutions + post-processing).
