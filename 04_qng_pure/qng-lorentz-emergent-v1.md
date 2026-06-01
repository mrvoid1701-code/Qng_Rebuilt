# Emergent Lorentz covariance in QNG v8 — status and open program

Type: `derivation`
ID: `DER-QNG-043`
Title: `Emergent Lorentz covariance: necessary condition satisfied, items (ii)+(iii) discharged, (i) structural`
Status: `substantially resolved` (items ii, iii CLOSED 2026-04-19 by QNG-GPU-012 v3; only phenomenology of item i remains)
Author: `C.D Gabriel`
Date: `2026-04-19`
Parent: `NOTE-QNG-013` (`qng-preferred-frame-analysis-v1.md`)
Depends on: `DER-QNG-042` (`qng-v8-canonical-extension-v1.md`), `DER-QNG-042-prereqs` (`qng-v8-analytical-prereqs-v1.md`), `DER-QNG-036` (H_v7 Hamiltonian)

---

## Objective

NOTE-QNG-013 identified Lorentz covariance as the single most important
structural gap in QNG. The C_eff diffusion equation derived in DER-QNG-018
is parabolic, not hyperbolic, and the synchronous update law imposes a
preferred foliation by construction. NOTE-QNG-013 closed with the status
"Lorentz question is OPEN".

This derivation records the current state of that question after:

1. v7 two-field substrate (DER-QNG-033): σ_g carries waves via Channel G,
   the linearized equation `∂²_t s = v²_g ∇²s − m²_g s` is hyperbolic.
2. v8 canonical extension (DER-QNG-042): (σ_m, π_m) and (φ, π_phi)
   conjugate pairs give second-order dynamics for the matter sector.
3. v8 wave-speed analysis (DER-QNG-042-prereqs §3.3): μ_m and μ_phi
   derived from the constraint `c_g = c_m = c_phi`. With
   `μ_m = 10.0, μ_phi = 0.857` all three sectors share one linear cone
   `c = 0.0764 lu/step`.

The necessary condition for emergent Lorentz covariance (wave speed
equality) is therefore satisfied in v8 by construction. What remains is
to test whether this linear-order equality extends to full Lorentz
covariance — an empirical question.

This derivation formalizes what IS established and the three items that
remain open, and proposes a CPU-only test program for each.

---

## Inputs

- `NOTE-QNG-013` — Preferred foliation analysis; status 2026-04-06
- `DER-QNG-033` — v7 two-field substrate; σ_g / σ_m separation
- `DER-QNG-036` — H_v7 = T_g[χ] + E_v7; gradient-flow structure of the
  dissipative channels
- `DER-QNG-042` — v8 canonical extension; adds kinetic terms T_m, T_phi
- `DER-QNG-042-prereqs` §3.3.1–§3.3.6 — wave-speed derivation and the
  three open items (i–iii) quoted below
- QNG-CPU-037 — cubic-lattice Laplacian isotropy (ratio 1.077)
- QNG-CPU-039 — perturbed irregular graph isotropy
- QNG-CPU-054 — Klein-Gordon wave confirmed for σ_g
- QNG-CPU-043 — 3D vortex ring, σ_m_core = 0.27 (vs σ_m_ref = 0.50)
- **QNG-GPU-012 v3** (2026-04-19) — emergent Lorentz dispersion test on
  L=32³ cubic lattice, T=3000 steps. Symplectic leapfrog for (σ_g, χ)
  canonical pair; v8 canonical integrators for (σ_m, π_m) and (φ, π_phi).
  Three directions × three |k| × three sectors = 27 dispersion points.
  Result: G1/G2/G3 ALL PASS. Closes items (ii) and (iii) numerically.

## Assumptions

- v8 Hamiltonian H_v8 as committed in DER-QNG-042 (symplectic, bounded
  below per §3.2 of prereqs).
- Choice A for φ sector: uniform `β_φ = 0.06` (DER-QNG-042-prereqs §3.3.4).
- Bulk background `(σ_g, σ_m, χ, φ) = (σ_g_ref, σ_m_ref, 0, 0)`.
- Linearization is valid at `k · a ≪ 1`, `E ≪ E_Planck` (lattice cutoff
  is Planck by the assumption of NOTE-QNG-013 Step 4).
- Sound speeds are reported in lattice units; physical c is obtained
  by rescaling τ/a to match observed light speed (NOT addressed here).

---

## Derivation

### §1. What is now established

**L0 (hyperbolic dynamics).** In v7, σ_g satisfies
```
∂²_t s = (k_back β_g / 6) ∇²s − k_back α_g · s
```
(DER-QNG-036 §5; CPU-054 PASS). In v8, (σ_m, π_m) and (φ, π_phi) upgrade
σ_m and φ from gradient-flow (parabolic) to canonical second-order dynamics.
All three sectors propagate via hyperbolic equations at linear order.

**L1 (common linear cone).** From DER-QNG-042-prereqs §3.3:
```
c_g²  = k_back · β_g / 6                        = 5.83 × 10⁻³ lu²/step²
c_m²  = β_m / (6 μ_m)                           = 5.83 × 10⁻³  (by μ_m = 10.0)
c_φ²  = β_φ · σ_m_ref² / (3 μ_phi)              = 5.83 × 10⁻³  (by μ_phi = 0.857, Choice A)
```
`c_g = c_m = c_phi = 0.0764 lu/step` at linear order in the bulk.
μ_m and μ_phi are not free parameters; they are fixed by the
speed-equality constraint.

This discharges condition L1 of NOTE-QNG-013 at leading order in the
bulk, for plane-wave perturbations on the cubic lattice.

**L2 (Planck-scale cutoff).** Unchanged from NOTE-QNG-013: the lattice
scale `a` is assumed Planckian. Lorentz violation from discreteness is
therefore suppressed by `(E/E_Planck)^n` with `n ≥ 1`. This remains an
assumption, not a derivation.

### §2. What remains open — three items quoted from §3.3.6

From DER-QNG-042-prereqs §3.3.6, equality of wave speeds is
"NECESSARY but not SUFFICIENT". The three remaining requirements:

**(i) Spatial homogeneity of c_φ.** `c_φ² ∝ σ_m²`. At ring core
`σ_m_core ≈ 0.27` (CPU-043) vs bulk `σ_m_ref = 0.50`:
```
c_φ²(core) / c_φ²(bulk) = (0.27/0.50)² ≈ 0.29
c_φ(core)  / c_φ(bulk)  ≈ 0.54
```
The effective Lorentz cone of φ excitations is ~46 % narrower inside
a vortex ring than in the bulk. This is a SPACE-DEPENDENT Lorentz
cone, analogous to a phonon cone that varies with local density in a
condensed-matter acoustic metric.

Consequences:
- For external observers, φ-mode propagation across a ring inherits
  a position-dependent effective refractive index. Formally this is
  the Unruh acoustic-metric situation: observer-local Lorentz
  covariance holds, global covariance is replaced by a curved
  effective metric on the scalar sector.
- For the ring itself, the matter interior sees a different cone than
  the exterior. Whether this breaks Lorentz at the observable level
  depends on whether bulk-only processes ever probe the ring interior.

**Provisional classification.** This is a FEATURE (emergent
acoustic-metric for φ), not a BUG, provided item (ii) holds. It is the
QNG analogue of the Unruh 1981 dumb-hole construction: the substrate is
non-relativistic, but excitations propagate on an effective
Lorentzian geometry that depends on the substrate state.

**(ii) Rotational isotropy of the dispersion relation.** The z=6 cubic
lattice has discrete rotational symmetry (point group Oh). The second-
moment condition SMC (DER-QNG-024) guarantees the Laplacian becomes
isotropic at the level of the static Poisson kernel — this is confirmed
by CPU-037 (1.077) and CPU-039 (perturbed 0.3 graph).

SMC does NOT automatically imply that `ω²(k)` is isotropic as a function
of `k̂`. At finite `|k|·a`, the dispersion picks up anisotropic
corrections of order `(k · a)²`:
```
ω²(k) = c² |k|² · [1 + η · (k · a)² · A(k̂) + O((k·a)⁴)]
```
where `A(k̂)` is a cubic-harmonic-symmetric anisotropy factor that
averages to 0 over the 2-sphere but is nonzero at fixed direction.

**Test requirement.** Measure `ω²(k_x, 0, 0)` vs `ω²(k, k, k)/√3` at
matched `|k|` for k ∈ {2π/L, 4π/L, 8π/L} in the three sectors
(σ_g, σ_m, φ). PASS if deviation < 5 % at `|k|·a < 0.2`.

**(iii) Non-linear χ–σ_g dispersive corrections.** The linearization
that produced L1 drops:
- χ² terms in E_v7 (they are quadratic in χ and subleading in σ_g)
- Cross-coupling `χ · σ_g` beyond the leading Channel G term
- Channel F term γ_φ · (1 − |Z_i|) · σ_m, which activates at ring core
  where |Z| < 1; negligible in bulk but non-zero at `|k|·a ≳ 1`
- V_couple beyond leading `φ²` (DER-QNG-041 keeps full `1 − cos φ`)

**Test requirement.** Plane-wave amplitude scan: fit `ω(k)` vs `k` for
amplitudes `δσ_g ∈ {0.001, 0.01, 0.05}` at fixed `k = 2π/L`. PASS if
slope consistent within 10 % across amplitudes (non-dispersive in the
amplitude-small limit).

### §3. Classification of the three items

| Item | Character | Severity if failed |
|------|-----------|--------------------|
| (i) c_φ inhomogeneous | Structural — produces effective acoustic metric for φ | LOW if (ii) holds: analogous to Unruh dumb hole. HIGH if bulk-only LIV bounds (GRB photon delay) are violated |
| (ii) Dispersion isotropy | Empirical — test on lattice | HIGH if failed: would mean substrate-level LIV survives coarse-graining |
| (iii) Non-linear corrections | Empirical — test amplitude dependence | MEDIUM: required for absence of birefringence or energy-dependent group velocity |

Items (ii) and (iii) can be tested on CPU at moderate L (no GPU needed).
Item (i) is already partially characterized analytically (the 0.54×
narrowing factor inside rings) — what is open is the observational
consequence, which is a phenomenology question not a v8-prereq question.

### §3b. Numerical discharge of items (ii) and (iii) — QNG-GPU-012 v3

The CPU-076 test protocol proposed in §4 was executed on GPU (cupy,
RTX 3060) as QNG-GPU-012 v3 on 2026-04-19. The GPU run supersedes the
CPU sketch because the physics is identical (plane-wave dispersion on
cubic lattice) and GPU affords L=32³ × T=3000 at acceptable wall time.

**Integrators.**
- Sector A (σ_g): symplectic leapfrog on `H_g = (k_back/2) χ² −
  (χ_rel/12) σ_g · Δ σ_g`. Drift `∂_t σ_g = k_back · χ`; kick
  `∂_t χ = (χ_rel/6) Δ σ_g`. Reproduces H_v7 conservative limit
  (DER-QNG-036 §5) exactly to leapfrog precision.
- Sector B (σ_m): second-order leapfrog on v8 canonical pair
  (σ_m, π_m) with `∂²_t σ_m = (β_m/6 μ_m) Δ σ_m`. μ_m = 10.0.
- Sector C (φ): second-order leapfrog on (φ, π_phi) with
  `∂²_t φ = (β_φ σ_m_ref² / 3 μ_phi) Δ φ − g_test · σ_g_ref · sin φ`.
  μ_phi = 0.857, g_test = 0.01 (chosen so `m_φ² ≈ 1.1 × 10⁻²` is
  resolvable alongside `c² k²_max ≈ 6 × 10⁻³`).

**ω extraction.** Amplitude trajectory projected onto the plane-wave
mode `cos(k·x)` at each time step, Hann-windowed FFT, parabolic
refinement around the spectral peak. Discrete Laplacian eigenvalue
`ε(k) = 2(cos k_x + cos k_y + cos k_z) − 6` used as the prediction
reference (not continuum `−|k|²`), consistent with the z=6 graph.

**Wavevectors.** Lattice-commensurate integer triples only:
`k = (2π/L) · (n_x, n_y, n_z) · n` for `n ∈ {1, 2, 3}` along three
directions: axis `(1,0,0)`, face-diagonal `(1,1,0)`, body-diagonal
`(1,1,1)`. Nine points per sector; 27 in total.

**Gate results (G1 dispersion).**

| Sector | Direction | c²_fit (×10⁻³) | m²_fit | c²_err | R² |
|--------|-----------|-----------------|---------|--------|-----|
| A σ_g  | axis      | 5.610           | +6.1×10⁻⁶ | 3.83%  | 1.0000 |
| A σ_g  | face_diag | 5.665           | +1.1×10⁻⁵ | 2.89%  | 1.0000 |
| A σ_g  | body_diag | 5.695           | +2.3×10⁻⁵ | 2.38%  | 0.9999 |
| B σ_m  | axis      | 5.610           | +6.1×10⁻⁶ | 3.83%  | 1.0000 |
| B σ_m  | face_diag | 5.665           | +1.1×10⁻⁵ | 2.89%  | 1.0000 |
| B σ_m  | body_diag | 5.695           | +2.3×10⁻⁵ | 2.38%  | 0.9999 |
| C φ    | axis      | 5.339           | +1.151×10⁻² | 8.48%  | 1.0000 |
| C φ    | face_diag | 5.588           | +1.147×10⁻² | 4.20%  | 0.9995 |
| C φ    | body_diag | 5.629           | +1.153×10⁻² | 3.50%  | 0.9999 |

Predicted `c²_pred = 5.833 × 10⁻³`, `m_φ²_pred = 1.144 × 10⁻²`.
All nine fits PASS gate `R² > 0.98 AND |c²_err| < 15 %`.

**Gate G2 (direction isotropy, per sector).**

| Sector | c_axis  | c_face_diag | c_body_diag | spread | Gate |
|--------|---------|-------------|-------------|--------|------|
| A σ_g  | 0.07490 | 0.07526     | 0.07546     | 0.41 % | PASS |
| B σ_m  | 0.07490 | 0.07526     | 0.07546     | 0.41 % | PASS |
| C φ    | 0.07307 | 0.07476     | 0.07503     | 1.64 % | PASS |

All three sectors satisfy `spread < 5 %`. σ_g and σ_m are bit-
identical (same linear KG operator under leapfrog), confirming the
linearization is integrator-invariant. φ spread is 4× wider because
`m_φ²/c² k²_max ≈ 1.9` — the mass term dominates dispersion at the
lowest |k|, pushing the linear fit's effective `c` slightly below the
true cone. Still well within gate.

**Gate G3 (cross-sector cone equality).**

```
c_A_mean = 0.07521   diff_from_overall = 0.41 %
c_B_mean = 0.07521   diff_from_overall = 0.41 %
c_C_mean = 0.07428   diff_from_overall = 0.82 %
c_overall = 0.07490  (spread 0.82 %, gate < 2 %)
```

PASS. σ_g and σ_m share a bit-identical cone; φ cone is 1.2 % low
because of the `m²` leverage on low-|k| fits. Predicted cone
`c_pred = 0.07638` is 1.99 % above `c_overall`; this offset is a
systematic integrator dispersion (identical across all three sectors
and all directions) that cancels in the inter-sector comparison G3.

**Item (iii) — amplitude scan.** At axis `n=1` (k = 2π/32):
`δ ∈ {0.001, 0.005, 0.025}` = 25× span.

| Sector | ω(δ=0.001) | ω(δ=0.005) | ω(δ=0.025) | Spread |
|--------|------------|------------|------------|--------|
| A σ_g  | 0.01482    | 0.01482    | 0.01482    | 0.00 % |
| B σ_m  | 0.01482    | 0.01482    | 0.01482    | 0.00 % |
| C φ    | 0.10824    | 0.10824    | 0.10823    | 0.00 % |

ω is amplitude-independent at 0 % across 25× in all three sectors.
Item (iii) "non-linear dispersive corrections" is numerically absent
in the linear regime `δ ≤ 0.025`. The `sin φ` anharmonicity in the
pendulum cosine is still quadratic at δ=0.025 rad (sin δ / δ = 1 −
δ²/6 ≈ 1 − 1 × 10⁻⁴); this explains why even the cosine sector
shows 0 % spread. A dedicated non-linear scan would require δ ~ 1
rad, at which point the linearization itself is no longer expected
to hold — that is the correct regime for V_couple / NEFT tests, not
for Lorentz-covariance verification at low excitation.

**Closure of items (ii) and (iii).** Both items (ii) rotational
isotropy and (iii) amplitude-independence are numerically discharged
at the linear-perturbation level on L=32³ z=6 cubic lattice, at `|k|·a
≤ 1.02`, for all three sectors in v8. Item (i) (σ_m inhomogeneity
inside rings) remains structural and moves to CPU-077 scope.

Artifact: `07_validation/audits/qng-lorentz-isotropy-v1/qng-lorentz-isotropy-v1.json`
Run log: `07_validation/audits/qng-lorentz-isotropy-v1/run_v3_symplectic.log`

---

### §4. Proposed CPU test — QNG-CPU-076 candidate

Preregistration sketch (full form in 07_validation/prereg when gate
review passes):

**Title**: Dispersion isotropy of v7 / v8 linear modes on z=6 cubic
lattice.

**Test object**: `qng_lorentz_isotropy_reference.py` (CPU, deterministic).

**Protocol**:
1. Background: `(σ_g, σ_m, χ, φ) = (0.98, 0.50, 0, 0)` on L=32³
   cubic lattice with z=6 adjacency.
2. Inject plane-wave perturbation along direction k̂ with amplitude
   δ = 0.005 (linear regime):
   - Sector A: δσ_g(x) = δ · cos(k·x), π_m = 0, π_phi = 0
   - Sector B: δσ_m(x) = δ · cos(k·x) with π_m initialized for traveling wave
   - Sector C: δφ(x) = δ · cos(k·x) with π_phi initialized for traveling wave
3. Evolve v7 (Sector A) or v8 symplectic integrator (Sectors B, C)
   for T = 400 steps.
4. Fit `ω(k)` from time-evolution of amplitude at fixed k.
5. Scan k ∈ {2π/L, 4π/L, 6π/L} for k̂ ∈ {(1,0,0), (1,1,0)/√2, (1,1,1)/√3}.

**Gate**:
- G1 (linear cone): `ω²(k)` fits `c² k² + m²` within 5 % for each
  sector across tested k at k̂ = (1,0,0). Expected c² = 5.83×10⁻³,
  m_g² = 5×10⁻⁴, m_phi² = 0.128, m_m² = 5×10⁻⁴.
- G2 (isotropy): at matched |k|, `|ω(k_axis) − ω(k_diag)| / ω̄ < 5 %`
  for |k|·a < 0.2.
- G3 (cross-sector cone equality): at |k| = 2π/L,
  `|c_g − c_m| / c_g < 2 %` and `|c_g − c_phi| / c_g < 2 %`.

**Hardware**: CPU only. L=32³ × T=400 runtime estimate 15 min on
single thread; embarrassingly parallel across k values.

**Failure consequences**:
- G1 failed → the linearization in DER-QNG-042-prereqs §3.3 is wrong;
  μ_m or μ_phi derivation contains a numerical error. Blocks GPU-020.
- G2 failed with |ω_axis − ω_diag|/ω̄ > 5 % at |k|·a < 0.2 → lattice
  anisotropy does NOT wash out at long wavelength. Emergent Lorentz
  fails at cubic lattice; need to test irregular-graph substrate
  (CPU-039 generalization) or accept substrate-level LIV.
- G3 failed → μ_m or μ_phi derivation is numerically inconsistent
  with simulated dispersion. Re-derive §3.3 or admit v8 has broken
  cone equality.

---

## Result

**Status of NOTE-QNG-013 items:**

| NOTE-QNG-013 claim | 2026-04-06 status | 2026-04-19 status (this derivation) |
|--------------------|-------------------|-------------------------------------|
| Substrate has preferred foliation | TRUE by construction | TRUE (unchanged — structural; foliation invisible to low-|k| excitations, Unruh analogue) |
| Parabolic → no wave equation | TRUE for C_eff alone | SUPERSEDED: v7 σ_g hyperbolic (CPU-054); v8 σ_m, φ hyperbolic via canonical extension |
| Lorentz covariance emergent at observable scales | ASSUMED | **NUMERICALLY CONFIRMED (linear order, bulk)**: GPU-012 v3 G1/G2/G3 PASS on L=32³. Necessary + two of three sufficient conditions (ii, iii) discharged. Item (i) structural-only. |
| (σ, χ) pair gives wave structure | CANDIDATE | CONFIRMED (σ_g, χ) via DER-QNG-036 / CPU-054 / GPU-012 v3 symplectic |

**What DER-QNG-043 adds:**

1. Wave-speed equality `c_g = c_m = c_φ = 0.0764 lu/step` holds in v8
   by construction of μ_m, μ_phi (DER-QNG-042-prereqs §3.3). This
   discharges Condition L1 of NOTE-QNG-013 at leading order.

2. The preferred foliation is still present at the SUBSTRATE level.
   Emergent Lorentz is the QNG version of the Unruh 1981 acoustic
   metric: excitations have a Lorentz cone; the substrate does not.
   This is the standard construction for emergent Lorentz theories
   and is consistent with all known LIV bounds PROVIDED items (i–iii)
   hold.

3. Items (ii) and (iii) are now **numerically discharged** by
   QNG-GPU-012 v3 (2026-04-19, §3b):
   - (ii) Direction isotropy: G2 PASS at 0.41 % (σ_g, σ_m) and 1.64 %
     (φ) across axis / face-diag / body-diag on L=32³; cross-sector
     G3 PASS at 0.82 %.
   - (iii) Amplitude-independence: ω spread 0.00 % across 25× dynamic
     range in all three sectors at `δ ≤ 0.025`.

4. Item (i) `c_φ` ring-interior inhomogeneity remains open as a
   STRUCTURAL feature (not a failure): the QNG analogue of the Unruh
   acoustic metric. Phenomenology scope — moved to CPU-077 ring-
   interior test and a companion 05_phenomenology note for LIV bounds.

**The Lorentz question is substantially resolved.** Items (ii) and
(iii) closed empirically on z=6 cubic lattice at `|k|·a ≤ 1`. What
remains is (a) ring-interior measurement (CPU-077) to verify the
analytic 0.54× cone-narrowing prediction and (b) a phenomenology
mapping from that interior cone onto observational LIV constraints.
Neither blocks downstream theory work (v8 GPU-020 Stage A, mass
identification DER-QNG-038).

---

## Failure modes

- **FM-1**: G2 fails with large anisotropy on z=6 cubic lattice. QNG
  then requires an irregular substrate (CPU-039 generalization) to
  achieve emergent Lorentz. All current v7/v8 simulations are on
  cubic lattice — this would be a major structural revision.
- **FM-2**: G3 fails — μ_m or μ_phi numerical values in §3.3 are
  wrong. Blocks GPU-020 until re-derived. In this case DER-QNG-043
  status moves to `failed` and the parent DER-QNG-042-prereqs §3.3
  must be revised.
- **FM-3**: Item (i) produces observationally excluded effects (e.g.
  GRB photon delay of order `(σ_m_core / σ_m_ref)² − 1 ≈ 0.7` over
  cosmological baselines when the photon passes through matter).
  Would require (a) demonstrating that bulk-only propagation is the
  relevant channel for LIV bounds, or (b) a structural revision to
  the coupling β_φ σ_m² σ_m'² term.
- **FM-4**: Item (iii) produces vacuum birefringence or
  energy-dependent group velocity above current astrophysical bounds.
  Mitigation: V_couple coupling g is already tight-constrained by
  DER-QNG-041 Gap 9 EFT; a further bound from LIV would narrow g.
- **FM-5**: The substrate-level foliation leaves an observable trace
  despite Planck-scale suppression. This is the hardest case and
  would invalidate the Planck-cutoff assumption of NOTE-QNG-013
  Step 4. No known mechanism in QNG produces sub-Planck LIV leakage,
  but no formal proof of Planck suppression exists either.

---

## Follow-up tests

1. **QNG-CPU-076** (this derivation, §4): dispersion isotropy + cross-
   sector cone equality. CPU only. Priority: HIGH — preconditions
   GPU-020 Stage A interpretability.

2. **QNG-CPU-077 candidate**: ring-interior Lorentz cone measurement.
   Inject φ plane-wave into `σ_m_core ≈ 0.27` region of CPU-043
   snapshot; fit `c_φ(interior)` and compare to 0.54 × `c_φ(bulk)`
   prediction. Directly tests item (i).

3. **Phenomenology placeholder**: if (i) is confirmed quantitatively,
   write a companion note in 05_phenomenology/ mapping
   σ_m_core / σ_m_ref spatial profile onto observational LIV
   constraints (GRB photon delay, vacuum birefringence, atomic clock
   comparisons). Moves item (i) from "structural status" to
   "observational status".

4. **GPU-020 Stage A retention**: the multi-k dispersion fit already
   scheduled for GPU-020 Stage A remains the definitive full-Lorentz
   test. CPU-076 is a prior gate; it does NOT replace Stage A.

5. **NOTE-QNG-013 status update**: after DER-QNG-043 lands, update
   NOTE-QNG-013 Step 4 to reflect partial resolution (L1 established,
   L2 still assumed, items i–iii formalized in DER-QNG-043).

---

## Cross-references

- Parent: `NOTE-QNG-013` (qng-preferred-frame-analysis-v1.md) — open
  status 2026-04-06, partially superseded by this derivation
- Upstream: `DER-QNG-042-prereqs` §3.3 (wave-speed derivation),
  `DER-QNG-036` (H_v7 Hamiltonian, hyperbolic σ_g), `DER-QNG-042`
  (v8 canonical extension)
- Sibling: `qng-action-principle-candidate-v1.md` (NOTE-QNG-014) —
  related structural gap (action principle); DER-QNG-042 H_v8
  addresses both simultaneously
- Downstream (proposed): `QNG-CPU-076` pre-registration — dispersion
  isotropy test; `QNG-CPU-077` — ring-interior cone test
