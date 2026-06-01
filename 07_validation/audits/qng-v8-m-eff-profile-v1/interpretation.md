# QNG-CPU-081 m_eff² profile — Interpretation (evanescent candidate ruled out)

Type: `note`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-20`
Audit: `qng-v8-m-eff-profile-v1`
Upstream: `DER-QNG-046` promotion item 3
Companion: `qng_v8_m_eff_profile_reference.py`, `report.json`, `run.log`

---

## 1. Pre-registered question

The σ_m-scan (QNG-GPU-022) revealed a high-s saturation at s=1.4:
α_meas decreased from +1.825e−02 (s=1.0) to +1.645e−02 (s=1.4),
non-monotonic in the ring amplitude. Four candidate mechanisms
were identified. This analysis targets candidate #2 (m_eff²
saturation → evanescent tunneling) by mapping the numerical
effective-mass profile directly along the pulse path.

DER-QNG-046 §1–§4:
`m_eff²(x, y, z) = (g/(2μ_φ))·Δ²·cos(φ_bg)` with `Δ = SIGMA_M_REF − σ_m`.

Pulse: k = 3π/4, ω² = c_φ²·k² = 0.0648. Evanescent regime onset
when m_eff² ≥ ω²/2 = 0.0324; strong evanescence at m_eff² ≥ ω².

## 2. Configuration

- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz` (M_ring=176.85)
- v8 constants: SIGMA_M_REF=0.5, g=0.22, μ_φ=0.857, BETA_PHI=0.06
- Paths: x ∈ [4, 24], y_path = L/2 + b, z_path = L/2
- b ∈ {4, 6}; s ∈ {0.7, 1.0, 1.4} (deficit scaling, same as GPU-022)

**Important correction during execution**: initial run used
SIGMA_M_REF=1.0 (incorrect); verification via
`inspect.getsource` on the GPU module found SIGMA_M_REF=0.5.
M_ring sanity check confirms: with SIGMA_M_REF=0.5, computed
M_ring=176.85 matches GPU-reported value. All numerics below
use the corrected constant.

## 3. Results

| b | s    | max m_eff² | ratio/ω² | frac_evan | WKB R | x_max |
|---|------|------------|----------|-----------|-------|-------|
| 4 | 0.70 | +2.11e−03  | 0.033    | 0.000     | 0.000 | 4     |
| 4 | 1.00 | +4.31e−03  | 0.066    | 0.000     | 0.000 | 4     |
| 4 | 1.40 | +8.44e−03  | 0.130    | 0.000     | 0.000 | 4     |
| 6 | 0.70 | +5.14e−04  | 0.008    | 0.000     | 0.000 | 6     |
| 6 | 1.00 | +1.05e−03  | 0.016    | 0.000     | 0.000 | 6     |
| 6 | 1.40 | +2.06e−03  | 0.032    | 0.000     | 0.000 | 6     |

s² scaling sanity: 0.00% deviation across all (b, s) pairs — algebraic
identity m_eff² ∝ Δ² ∝ s² confirmed.

cos(φ_bg) sign structure: positive everywhere on both paths (100%
positive, 0 sign flips). No interference from φ-winding effects.

## 4. Primary verdict

**H_transparent** (ratio 0.032 at the target b=6, s=1.4 config).

Even at the extreme scaled ring (s=1.4, M_ring=247.59), m_eff²
reaches at most 3.2% of ω² along the out-of-core path. No evanescent
regime at any tested config. Candidate #2 (evanescent tunneling /
m_eff² saturation) is **RULED OUT**.

The highest in-core value (b=4, s=1.4) reaches 13% of ω², which is
in the H_intermediate band for in-core only, but this is well below
the ω²/2 onset and does not trigger barrier reflection.

## 5. What this implies for the saturation mystery

Surviving candidates (not separated by this test):
- **#1 Detector window clipping** — strong deflection at s=1.4 sends
  the pulse beyond the detector window (15 y-bins centred on y_pulse).
  Testable via widened detector.
- **#3 Ring self-distortion** — post-cache s-scaling leaves the
  ring non-equilibrium; at s=1.4 it may distort during T_track and
  contaminate α_meas via imperfect bg subtraction. Testable via
  alternative ring-formation protocol (direct ring cache at target M).
- **#4 Path-curvature lensing** — the scalar prediction's
  straight-line integral misses self-consistent path correction at
  high deflection. σ_m-scan showed slope ≤ 2 throughout, ruling
  out path-curvature as the DOMINANT mechanism, but it may still
  subtract from α_meas at the strong-lensing limit.

Most likely: #1 + #3 compound effect. Widened-detector GPU run is
the direct test.

## 6. Secondary finding — scalar §13 approximation is valid at natural ring

At s=1.0, b=6: m_eff²/ω² = 0.016, i.e. scalar §13 operates at <2%
correction to free-wave dispersion. The approximation `ω² ≫ m_eff²`
(required for the Hamilton-Jacobi ray-deflection formula) is well
satisfied.

**Consequence**: the sign discrepancy between α_scalar_th (−1.44e−02)
and α_meas (+1.83e−02) at s=1.0 is **NOT** explained by scalar
approximation breakdown. The scalar §13 formula is technically
valid in its domain; its failure at b > R must come from either
(a) the path-integration geometry (straight-line assumption) or
(b) a different physical channel not captured by the single-mode
V_couple reduction.

This reopens a sub-question: **what is the correct closed form for
α at b > R if m_eff² is small but the scalar prediction is still
wrong?** One possibility: the scalar §13 prediction `α = -(g/(2μω²))
∫ Δ·∂_y Δ dx` = `-(g/(4μω²)) × d/dy (∫ Δ² dx)` captures only the
y-gradient of a single scalar potential, while the actual deflection
responds to additional geometric couplings from the tensorial §1–§4
EOM that are distinct from the scalar amplitude.

## 7. Promotion-checklist update

| # | Condition | Before | After |
|---|-----------|--------|-------|
| 1 | True 2π-winding test | Retracted | Retracted |
| 2 | Eikonal/diffraction separation | PARTIAL | unchanged |
| 2a | A-scaling (H1, H2 ruled out) | closed | unchanged |
| 2b | s-scaling (tensorial corroborated; H_path out) | partial | unchanged |
| 2c | Evanescent candidate | OPEN | **RULED OUT** (this audit) |
| 3 | Numerical m_eff²(x) | Pending | **EXECUTED** — H_transparent |
| 4 | Closed-form α from tensorial EOM | Pending | Open; sign puzzle narrowed (not from m_eff² saturation) |

Item 3 is closed: numerical m_eff²(x) measurement done, saturation
origin NOT in evanescence. Item 2c (newly opened) is closed at
"ruled out". Item 4 remains the central open derivation.

## 8. Recommended next steps

1. **QNG-GPU-023** (to be pre-registered): widened-detector re-run
   of σ_m-scan at s=1.4 (y-window extended from 15 bins to ~25). If
   α_meas(s=1.4, wide) ≫ α_meas(s=1.4, narrow), candidate #1
   confirmed. If not, candidate #3 (ring self-distortion) becomes
   the lead.
2. **Alternative ring formation** (longer term): form rings at
   different target M_ring by varying Phase-2 duration or K_BACK,
   instead of post-cache rescaling. Eliminates #3 non-equilibrium
   artifact.
3. **Closed-form α (item 4)**: now known to require more than scalar
   §13 path-integral — the sign puzzle at b > R persists even when
   m_eff² ≪ ω². Candidate formula: use full tensorial EOM with
   second-order path correction.

## 9. What this means for theory status

- **Corroborated**: scalar §13 approximation is valid at natural ring
  size (m_eff² < 2% ω²). The earlier conclusion that "§13 is
  structurally invalid at b > R" was partially wrong — it fails
  quantitatively, not from breakdown of the linearization.
- **Ruled out**: evanescent tunneling as the saturation mechanism
  (candidate #2).
- **Strengthened**: need for a more complete closed-form derivation
  at b > R that does not rely on straight-line path integration.
- **Unchanged**: DER-QNG-046 §1–§4 tensorial EOM as the correct
  framework; all other locked correspondences.

## 10. Artifacts

- `report.json` — max/mean m_eff², evanescent fractions, WKB R, cos φ
  sign structure for each (b, s)
- `run.log` — console output
- `interpretation.md` — this file

Total runtime: < 10 s on CPU (post-processing only, no simulation).
