# QNG-GPU-021 A-SCAN — Interpretation (DER-QNG-046 out-of-core sign residual)

Type: `note`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-20`
Audit: `qng-v8-bending-a-scan-v1`
Upstream: `DER-QNG-046` §11 (candidate mechanisms), promotion-checklist sub-item 2a
Companion: `qng_v8_bending_a_scan_probe.py`, `report.json`, `run.log`

---

## 1. Pre-registered question

The k-scan audit (`qng-v8-bending-k-scan-v1`, 2026-04-20) confirmed
eikonal recovery at b=4 (in-core) but exposed a residual at b=6:
measured α stays positive across k while scalar prediction flips sign.
Three candidate mechanisms were listed in DER-QNG-046 §11:

- **H1** — O(A²) back-reaction (pulse modulates σ_m)
- **H2** — linear amplitude modulation / kinetic-mode coupling
- **H3** — mixed / saturated
- **H4** — VOID (sign flip across A range)

The A-scan fixes (k=3π/4, b=6) and varies the pulse amplitude
A ∈ {0.025, 0.050, 0.100} to exploit different A-scalings.

## 2. Configuration

- L = 28, R = 4, T_track = 250 lu, DT = 0.025 (Yoshida4 symplectic)
- c_φ = 0.10801, path = 20.0 lu (x_src=4, x_det=24)
- Pulse: σ = 2.0, k = 3π/4 (λ = 2.67 lu), b = 6 (out-of-core)
- Cached ring `ring_L28_R4_P1_300_P2_1000_9218625ef1cb.npz`, M_ring = 176.85
- α_scalar_th = −1.4437e−02 (A-independent, computed once)

Runtime: 7 evolutions × 196 s = 22.9 min (ring-bg reuse).

## 3. Results

| A     | α_meas     | α_resid    | sign |
|-------|------------|------------|------|
| 0.025 | +1.8043e−02 | +3.2480e−02 | +    |
| 0.050 | +1.8250e−02 | +3.2687e−02 | +    |
| 0.100 | +1.9214e−02 | +3.3650e−02 | +    |

**Log-log fit** (|α_resid| vs A):
- slope = **+0.026**
- R² = **0.88**

**Verdict**: `H3_MIXED_LOW_R2` (automatic), but the physically
informative reading is **slope ≈ 0**, not "mixed" — see §4.

## 4. Physical interpretation — α_resid is A-INDEPENDENT

The pre-registered slope bands for H1/H2/H3/H4 assumed the residual
scales with amplitude in some definite way. The measured slope is
+0.026 — essentially flat across a 4× change in A. α_resid drifts from
+3.248e−02 to +3.365e−02, a 3.6% change over a 400% change in
amplitude.

Interpretation: the b > R bending residual is **not** back-reaction
(would require slope=2) and **not** linear kinetic-mode coupling
(would require slope=1). It is an **A-independent geometric effect**
of the ring σ_m profile on the pulse — linear in A (so cancels in
α_resid/A ratio for infinitesimal A) but **not captured by the
scalar approximation** used in DER-QNG-046 §13.

Magnitude check: |α_resid| / |α_scalar_th| ≈ 2.25 at all three A.
This is not a perturbative correction to the scalar formula — it is
the same order of magnitude as the scalar prediction itself, with
opposite sign. The scalar formula is structurally **wrong** at b > R,
not "correct to leading order with corrections".

## 5. What this rules out, what it leaves open

**Ruled out (this audit):**
- H1 — O(A²) back-reaction as the dominant b > R residual mechanism
- H2 — linear kinetic-mode coupling as the dominant mechanism
- H4 — no sign flip observed (all three A give positive α_meas)

**Surviving candidates** (not separated by this scan):
- **Tensorial EOM § 1–4** (DER-QNG-046 full form, not §13 scalar
  reduction) — predicts an A-independent geometric contribution from
  the ring's far-field σ_m curvature that the scalar approximation
  integrates out incorrectly along a straight-line path.
- **Path-curvature feedback** — the scalar prediction assumes the
  pulse travels in a straight line. At b > R, the pulse's own
  deflection brings it closer to the ring, sampling a different σ_m
  profile than the straight-line integral assumes.

Both are A-independent at leading order and consistent with the
observed slope ≈ 0.

## 6. Domain of validity for DER-QNG-046 (updated)

| Regime | Scalar §13 validity | Evidence |
|---|---|---|
| λ < R AND b ≤ R (eikonal in-core) | **quantitative** (16% agreement) | k-scan b=4, k=3π/4 |
| λ < R AND b > R (eikonal out-of-core) | **structurally wrong** (sign + magnitude) | this A-scan |
| λ ≳ 2R (diffraction) | fails by 1–2 orders | k-scan b=4, k=π/4 |

DER-QNG-046 remains a `candidate-partial-eikonal` derivation.
The scalar §13 closed form is usable only for λ < R **and** b ≤ R.

## 7. Promotion-checklist update

| # | Condition | Before A-scan | After A-scan |
|---|-----------|---------------|--------------|
| 1 | True 2π-winding test | Retracted (CPU-080) | Retracted |
| 2 | Eikonal/diffraction separation | PARTIAL (in-core PASS) | unchanged |
| 2a | b > R mechanism identification | OPEN | **back-reaction & linear-kinetic ruled out**; residual is A-independent → tensorial / path-curvature |
| 3 | Numerical m_eff²(x) on cached φ_bg | Pending | unchanged |
| 4 | Closed-form α from relaxed φ_bg | Pending | unchanged — but must use tensorial EOM, not §13 scalar |

The A-scan does not close item 2a definitively — it eliminates H1 and
H2 and points to an A-independent mechanism (tensorial or path-
curvature). A follow-up scan varying σ_m amplitude (scale the ring
deficit) would distinguish tensorial geometric coupling from path-
curvature feedback; registered as DER-QNG-046 item 2b candidate.

## 8. What this means for theory status

- **Falsified**: the H1 back-reaction interpretation of the b > R
  residual. DER-QNG-046 §13 scalar is structurally invalid at b > R,
  not "missing an O(A²) term".
- **Not falsified**: DER-QNG-046 §1–§4 tensorial EOM.
- **Strengthened**: the case for tensorial (not scalar) derivation of
  the closed-form α (item 4 of promotion checklist).
- **Unchanged**: DER-QNG-044 Einstein correspondence verdicts;
  eikonal in-core PASS from k-scan; all other locked correspondences.

## 9. Artifacts

- `report.json` — raw measurements (3 A values, α_meas, α_resid, slope, R²)
- `run.log` — full console output
- `run_log.txt` — tee'd runtime log
- `interpretation.md` — this file

Total runtime: 22.9 minutes on GPU (7 evolutions × 195–196 s each,
via ring-bg reuse from cached ring).
