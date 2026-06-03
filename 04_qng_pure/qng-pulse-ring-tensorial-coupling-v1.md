# DER-QNG-046: Pulse–ring tensorial coupling from v8 action — resolves anisotropy, bending, and scalar-channel failure

Type: `derivation`
ID: `DER-QNG-046`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-20`
Upstream: `DER-QNG-042` (v8 canonical), `DER-QNG-045` (torus scalar — downgraded), `DER-QNG-044` Tests 3e/3f (anisotropy + bending measurements)

---

## Inputs

- [qng-v8-canonical-extension-v1.md](qng-v8-canonical-extension-v1.md) — DER-QNG-042 (v8 canonical)
- [qng-torus-gravity-v1.md](qng-torus-gravity-v1.md) — DER-QNG-045 (torus scalar profile)
- [qng-einstein-correspondence-v1.md](qng-einstein-correspondence-v1.md) — DER-QNG-044 (anisotropy/bending tests)
- [qng-lorentz-emergent-v1.md](qng-lorentz-emergent-v1.md) — DER-QNG-043 (Lorentz emergent)

---

## Purpose

Derive the tensorial / kinetic-cross-term coupling between a phi-wave
pulse and a background phi-vortex ring directly from the v8 action,
without assuming a scalar gravitational potential mediator. Establishes
`m_eff²(x) = (g/(2μ_φ)) · deficit²(x) · cos φ_bg(x)` as the exact
pulse-background coupling in linear order, and explains three
previously puzzling results:

1. **Scalar bending channels FAIL by factor 10²–10⁶** (CPU-078):
   because the scalar prediction ignores the `cos φ_bg` modulation.
2. **Anisotropy P/T = 4.00** (Test 3e): parallel (on-axis) path has
   `cos φ_bg ≈ 1` throughout; transverse (rim-plane) path sweeps
   `cos φ_bg ∈ [−1, +1]` — partial cancellation.
3. **Small measured α(b) ≪ scalar prediction** (Test 3f): residual
   after u → −u antisymmetric cancellation of thin-ring contribution.

---

## 1. Setup — v8 action for phi sector

In the v8 canonical Hamiltonian (DER-QNG-042), the phi sector has
Lagrangian density (after Legendre transform of the π_φ kinetic term):

```
L_φ = (μ_φ/2) (∂_t φ)²  −  (μ_φ c_φ²/2) |∇φ|²
      − V_couple(σ_m, φ)
```

with

```
V_couple(σ_m, φ) = (g/2) · (σ_m,ref − σ_m)² · (1 − cos φ)
                 ≡ (g/2) · Δ²(x) · (1 − cos φ)
```

where Δ(x) = σ_m,ref − σ_m(x) is the σ_m deficit field. At v8 default
parameters: g = 0.22, μ_φ = 0.857, c_φ² = 0.01167, σ_m,ref = 1.0.

---

## 2. Background–pulse split

Split the phi field into a **static background** and a **small pulse**:

```
φ(x, t) = φ_bg(x) + φ_p(x, t),      |φ_p| ≪ 1
```

where φ_bg is the ring's winding solution (time-independent, satisfies
its own EOM). The pulse φ_p is a small perturbation.

### 2.1 Kinetic expansion

```
|∇φ|² = |∇φ_bg|² + 2 ∇φ_bg · ∇φ_p + |∇φ_p|²
```

The **kinetic cross-term** 2·∇φ_bg·∇φ_p was flagged by the CPU theory
suite (anisotropy_theory.log) as the signature of direction-dependent
coupling. We treat it rigorously below.

### 2.2 V_couple expansion to quadratic order in φ_p

Using cos(a + b) = cos a cos b − sin a sin b and sin(a + b) = sin a cos b + cos a sin b,
and Taylor-expanding `cos φ_p ≈ 1 − φ_p²/2`, `sin φ_p ≈ φ_p`:

```
1 − cos φ = 1 − cos φ_bg · cos φ_p + sin φ_bg · sin φ_p
          ≈ (1 − cos φ_bg)            [background term]
           + sin φ_bg · φ_p            [linear tadpole]
           + (cos φ_bg / 2) · φ_p²     [effective mass for pulse]
```

So:

```
V_couple ≈ (g/2) Δ²(x)·[(1 − cos φ_bg)  +  sin φ_bg · φ_p  +  (cos φ_bg/2) · φ_p²]
```

---

## 3. Euler–Lagrange equation for φ_p

Varying the full Lagrangian with respect to φ_p:

```
μ_φ ∂_t² φ_p  −  μ_φ c_φ² ∇² φ_p  +  (g/2) Δ²·[sin φ_bg + cos φ_bg · φ_p]
  − μ_φ c_φ² ∇² φ_bg = 0
```

The last term arises from the `2 ∇φ_bg · ∇φ_p` kinetic cross-term
through integration by parts. But φ_bg solves its own static EOM:

```
μ_φ c_φ² ∇² φ_bg  =  (g/2) Δ²(x) · sin φ_bg(x)      (background EOM)
```

So the `∇² φ_bg` term **exactly cancels** the `sin φ_bg` tadpole in
the pulse equation. The clean remaining EOM for φ_p is:

```
┌─────────────────────────────────────────────────────────────────┐
│   ∂_t² φ_p  −  c_φ² ∇² φ_p  +  m_eff²(x) · φ_p  =  0            │
│                                                                  │
│   with   m_eff²(x) = (g/(2 μ_φ)) · Δ²(x) · cos φ_bg(x)           │
└─────────────────────────────────────────────────────────────────┘
```

This is a **Klein–Gordon wave equation with position-dependent
effective mass**, where the mass is modulated by the **winding phase
cos φ_bg** through the coupling to the σ_m deficit.

---

## 4. Tensorial structure

The effective mass squared `m_eff²(x)` is NOT a scalar gravitational
potential. Its structure is:

- **Δ²(x)**: scalar, peaked at the ring rim.
- **cos φ_bg(x)**: directional, oscillates between ±1 across the ring.

For a vortex ring with winding number n = 1, φ_bg is approximately
the azimuthal angle around the ring axis in the ring plane:

```
φ_bg(x, y, z) ≈ arctan((y − y_c)/(x − x_c))     (in ring plane, z = z_c)
```

so `cos φ_bg` varies as `(x − x_c)/√((x − x_c)² + (y − y_c)²)` — it
is **odd in (x − x_c) at fixed y**.

This is the origin of the **kinetic-mode / tensorial** coupling: the
pulse does not see a scalar potential Φ(r) but a phase-modulated
potential whose sign flips across the ring.

---

## 5. Bending angle from eikonal approximation

For a pulse wavepacket with central frequency ω ≈ k·c_φ propagating
along +x at impact b in the ring plane, the effective index of
refraction is:

```
n²(x, y) = 1 − m_eff²(x, y) c_φ² / ω²
```

and the transverse deflection accumulates as:

```
α(b) ≈ −(1 / (2 ω²)) · ∫_{x_s}^{x_d}  ∂_y m_eff²(x, y_c + b, z_c) dx
```

Substituting m_eff² = (g/(2μ_φ)) · Δ² · cos φ_bg:

```
∂_y m_eff² = (g/(2 μ_φ)) · [2 Δ · ∂_y Δ · cos φ_bg  −  Δ² · sin φ_bg · ∂_y φ_bg]
```

So α decomposes into two contributions:

```
α(b) = α_scalar(b) + α_winding(b)
```

with

```
α_scalar(b) = −(g / (2 μ_φ ω²)) · ∫ Δ · ∂_y Δ · cos φ_bg  dx

α_winding(b) = +(g / (4 μ_φ ω²)) · ∫ Δ² · sin φ_bg · ∂_y φ_bg  dx
```

### 5.1 Thin-ring in-plane: BOTH terms vanish

For a stationary, thin vortex ring centered at (x_c, y_c, z_c), in
the ring plane (z = z_c), parameterize pulse by u = x − x_c.

At impact b, the integrand contains:
- Δ² peaked at u = ±√(R² − b²) for b < R (two rim crossings)
- cos φ_bg(u, b) = u / √(u² + b²) — **odd in u**
- sin φ_bg(u, b) = b / √(u² + b²) — even in u
- ∂_y Δ ∝ b / √(u² + b²) · δ'(...)  — even in u
- ∂_y φ_bg = u / (u² + b²)  — **odd in u**

Therefore:
- `Δ · ∂_y Δ · cos φ_bg` ∝ (even)(even)(odd) = **odd in u**
- `Δ² · sin φ_bg · ∂_y φ_bg` ∝ (even)(even)(odd) = **odd in u**

**Both integrands are odd in u.** Integrated over u ∈ [−U, +U]
symmetric, both α_scalar and α_winding **vanish identically**
for the continuum thin-ring in-plane geometry.

This **explains why the measured α(b) is so small** (10⁻³ to 10⁻²
rad) compared to the scalar-Poisson prediction (10¹ rad from
DER-QNG-045 §3.1): **the leading continuum prediction is zero**,
and the measured residue is the symmetry-breaking correction.

### 5.2 Residual α from symmetry-breaking

In the actual lattice simulation, u → −u symmetry is broken by:

1. **Finite pulse extent**: the Gaussian wavepacket with width σ_p ≈ 2
   causes the integrand to be sampled asymmetrically.
2. **Lattice discretization**: integer x spacing introduces an O(1/L)
   asymmetry in the sum over u.
3. **Pulse back-reaction**: the pulse's own amplitude modifies Δ(x)
   slightly asymmetrically along its trajectory (O(A²) = O(2.5×10⁻³)
   for A = 0.05).
4. **Finite path x ∈ [x_s, x_d]**: limits the u range to |u| ≤ 10, so
   the symmetric cancellation is incomplete if the ring sits near
   the center.

The measured α(b) ~ 10⁻²–10⁻³ rad at path L = 20 is the accumulated
residual from these sources. Extrapolating to continuum + infinite
path, α would tend to zero (for in-plane paths).

### 5.3 Anisotropy P/T = 4 (Test 3e) explained

For the **parallel path** (along ring axis, z direction at ρ_⊥ = 0):
- Δ² ≈ 0 near axis (ring deficit is at rim, not axis)
- cos φ_bg is ambiguous at axis (phase singularity)
- But the *gradient* of Δ² along z at rim crossings is non-trivial
- Effective coupling does not cancel by symmetry

For the **transverse path** (in ring plane, across rim):
- Both α_scalar and α_winding integrate to zero by u symmetry.

Therefore Δt_parallel ≠ 0 (no cancellation) and Δt_transverse ~ 0
(leading-order cancellation). The measured ratio **P / T = 4.00** is
a lower bound on the cancellation strength; the true continuum ratio
could be arbitrarily large.

**This is the mathematical origin of the 120% anisotropy excess
beyond scalar theory** (3.06× over scalar prediction 1.31).

### 5.4 CPU-078 scalar-failure explained

The DER-QNG-045 scalar formula used a structurally different coupling
(σ_g Poisson) that does NOT contain the `cos φ_bg` modulation.
Without cos φ_bg, there is no u → −u cancellation, and the integral
gives the large naive Einstein-1911 value (α ~ 30 rad). The physical
system has `cos φ_bg` present, which forces cancellation, leaving
only O(10⁻³) residue. The factor 10³–10⁴ mismatch between CPU-078
scalar prediction and measurement is exactly this cancellation
absent from the scalar framework.

---

## 6. Predictions

### 6.1 Direction-dependent Shapiro delay

For a pulse path P with unit tangent t̂ and a ring centered at R_c,
the scalar Shapiro delay integral is:

```
Δt(P) = (1/c_φ) · ∫_P  m_eff²(x) · c_φ² · (1 / (2 ω²))  ds
     = (c_φ / (2 ω²)) · ∫_P Δ²(x) · cos φ_bg(x) · (g/(2 μ_φ))  ds
```

**Falsifiable prediction**: the delay Δt(P) is extremal when the path
aligns with a direction where cos φ_bg is predominantly positive
along the path (axis direction for a vortex ring).

Quantitative estimate:
- Parallel (axis) path: ∫ Δ² cos φ_bg ds ≈ ∫ Δ² ds (cos φ_bg ≈ 1 on axis by symmetry of winding around axis direction)
- Transverse (rim) path: ∫ Δ² cos φ_bg ds ≈ 0 (leading-order cancellation)

**Measured**: Δt_∥ / Δt_⊥ = 4.00. Prediction: ratio → ∞ in continuum
limit for symmetric thin ring; the finite 4.00 reflects finite-path
cutoff + lattice + back-reaction residuals, ALL small corrections.

### 6.2 Bending near but not in ring plane

For a pulse slightly above the ring plane at z = z_c + Δz, the
u → −u symmetry is broken by the z-dependence of φ_bg. Predicted:
α(b, Δz) = O(Δz/R) times the broken-symmetry residue. **Falsifiable
prediction**: increasing Δz from 0 to 2 should monotonically
increase |α(b)| by factor ~Δz/R.

### 6.3 Bending with counter-winding ring (W− instead of W+)

A counter-winding ring has cos φ_bg → cos(−φ_bg) = cos φ_bg
(invariant). So α should be **identical** for W+ and W− rings —
unlike a charged analog where the sign would flip. **Falsifiable
prediction**: W+ and W− produce identical α(b) within noise.

### 6.4 Bending with n=2 (doubly-wound) ring

For n=2 winding, cos(2·φ_bg) oscillates twice as fast around the
ring. The cancellation is STRONGER (finer oscillation ⇒ faster
destructive interference). **Falsifiable prediction**: α(b) for n=2
ring is **smaller** than α(b) for n=1 ring at same b.

### 6.5 Explicit symmetry-breaking test

Inject an asymmetric perturbation (e.g., pulse offset in x) and
measure bending. If the measured α scales linearly with the
perturbation amplitude, this confirms the cancellation mechanism.
**Falsifiable prediction**: α ∝ x_offset at small offset.

---

## 7. Relation to Einstein correspondence program

- **Einstein 1911 scalar gravity**: α ∝ 1/b far-field for scalar
  Poisson. QNG v8 does NOT match this because m_eff² has cos φ_bg
  that cancels the scalar result. CPU-078 confirmed the far-field
  1/b is not recovered on the L=20 path.

- **Einstein 1915 GR (Eddington)**: α_GR = 2 α_1911 from metric
  curvature of space. QNG v8 does not produce GR-like tensorial
  coupling either — its tensorial structure is from winding phase,
  not metric curvature.

- **QNG's unique tensorial**: the cos φ_bg modulation is distinct
  from GR's spacetime curvature. It is a **phase-field tensorial
  coupling** — closer in spirit to Aharonov–Bohm than to
  gravitational lensing. This is a genuinely new category of
  gravitational bending.

This is **not** Einstein, **not** Nordström, **not** gauge-coupled.
It is a new class: **winding-modulated mass coupling**.

---

## 8. Numerical verification plan (CPU-079 candidate)

The following tests can verify DER-QNG-046 quantitatively:

1. **Measure cos φ_bg(x) along pulse path** at each b ∈ {3, 4, 6, 8}
   from the cached ring state. Integrate:
   ```
   α_predicted(b) = (g c_φ²/(μ_φ ω²)) · ∫ Δ · ∂_y Δ · cos φ_bg dx
   ```
   Compare to measured α(b). If cancellation is O(10⁻³) of naive
   result, this verifies the mechanism.

2. **Measure along axis vs in-plane** integral of `Δ² · cos φ_bg`
   from the cached ring. Predicted ratio axis/plane → much larger
   than measured Δt P/T = 4 in the continuum limit.

3. **Inject explicit x-offset in pulse** and measure whether α
   scales linearly with offset. If yes, the residual α measurement
   is explained by finite-size/lattice symmetry breaking.

---

## 9. Open items

1. **Quantitative closed form**: α_scalar and α_winding integrals
   involve elliptic integrals (like magnetic vector potential of a
   current loop). Writing out the integrals in terms of K(k), E(k)
   remains outstanding.

2. **Second-order corrections**: the linear expansion around φ_bg
   misses O(φ_p²) back-reaction. At pulse amplitude A = 0.05, this
   is O(2.5×10⁻³). Non-trivial for precision measurements.

3. **Dynamical background**: φ_bg was treated as static. If the
   ring is drifting (CPU-045 found viscous-regime drift), then
   time-dependent ∂_t φ_bg couples to ∂_t φ_p, adding a velocity-
   dependent term. Relevant for moving sources.

4. **Beyond small-pulse linearization**: full non-linear sine–Gordon
   solutions around a vortex ring are not known. Large-amplitude
   probes (A > 0.1) would test non-linear corrections.

---

## 10. Implications for theory status

- **DER-QNG-045** (scalar torus-Poisson) is **downgraded** to
  "qualitative skeleton"; its quantitative predictions FAIL
  (CPU-078 diagnostic).
- **DER-QNG-046** (this document) is the correct quantitative
  framework for v8 pulse–ring bending.
- The "Einstein correspondence" (DER-QNG-044 Test 3f bending) must
  be re-interpreted: v8 bending is **not** scalar Einstein 1911, not
  metric Einstein 1915 — it is **winding-modulated phase coupling**
  that gives ANTI-Einstein behavior (cancellation instead of
  monotonic deflection).
- This resolves the CPU-078 scalar-failure, Test 3e anisotropy, and
  Test 3f small-α mystery simultaneously.

---

## 11. Postscript (2026-04-20) — CPU-079 results and open question

CPU-079 (`tests/cpu/qng_tensorial_cancellation_reference.py`) evaluated
the DER-QNG-046 integrals against the cached L=28 R=4 ring. All three
diagnostic gates FAILED:

- **G1 cancellation**: cancellation factor (|integ without cos| /
  |integ with cos|) is 1.01–1.07, not >> 10. The cos(φ_bg) modulation
  is essentially constant along the pulse path, so it does NOT
  produce the predicted cancellation.
- **G2 tensorial magnitude**: α_tensorial still 2–6 rad (vs measured
  10⁻² rad). Still 100× over.
- **G3 anisotropy**: axis/trans (with cos) = 0.72 (not > 2); actual
  anisotropy comes from a different source.

**Root cause**: the cached ring's φ profile is **NOT an arctan vortex
winding**. Inspection of φ[:,:, z=14] shows a quadrupolar pattern with
amplitude |φ| ≤ 1.1 and a minimum of −1.07 at the ring center —
clearly a diffuse phase structure, not a topological singularity with
2π winding. The assumption φ_bg(x,y) ≈ arctan((y−y_c)/(x−x_c)) in §5.1
is violated in the actual v8 ring formation.

### Revised understanding

The **structural EOM derivation** (§1–§4) remains correct: pulse sees
m_eff²(x) = (g/(2μ_φ))·Δ²(x)·cos(φ_bg(x)) by clean Lagrangian
manipulation. This is theoretically rigorous.

The **cancellation mechanism** (§5) relied on assumed winding
structure that the actual v8 ring does NOT have. So the mechanism
is theoretically consistent for a true vortex but NOT applicable to
the CPU-074/bending-probe rings as cached.

### Why is measured α still 100× smaller than scalar V_couple channel?

Given:
- cached ring has cos(φ_bg) ≈ 0.88 (mean along path), not oscillating
- so m_eff² ≈ 0.88 × scalar V_couple prediction (still ~10 rad)
- measured α ~ 10⁻² rad

The 100× gap between prediction (10 rad) and measurement (10⁻² rad) is
**not** explained by cos(φ_bg) cancellation. Candidate mechanisms:

1. **Eikonal breakdown**: the pulse is NOT a geometric-optics ray.
   Wavelength λ ≈ 2π/k_pkt = 8 lu; ring radius R = 4. We are in the
   **diffraction** regime where ray bending ≠ centroid shift.
   Centroid shift is order wavelength·kick-angle = 8·0.04 = 0.3
   which is what's measured, but "kick-angle" here is not α = ∂Φ/∂y·t.

2. **Second-order amplitude**: measured Δy between vac and ring pulses
   includes AMPLITUDE modulation (vac amp 0.035 → ring amp 0.040).
   This is pulse scattering, not pure deflection. Pure deflection
   would preserve amplitude.

3. **Back-reaction suppression**: pulse amplitude A = 0.05 is small,
   so back-reaction on φ_bg is O(A²) = 2.5×10⁻³, matching the order
   of measured α.

**Provisional conclusion**: the measured α(b) from Test 3f is not a
geometric-optics bending in any simple sense. It combines diffraction,
amplitude modulation, and back-reaction into a single "Δy centroid
shift" metric. Extracting a clean "gravitational deflection angle"
from this requires longer path, higher frequency (smaller wavelength),
and separation of the diffraction from the kick.

### Implications

1. **DER-QNG-046 EOM (§3) is theoretically correct** — m_eff² =
   (g/2μ_φ)·Δ²·cos(φ_bg) is an exact linearized coupling.
2. **DER-QNG-046 §5 cancellation mechanism** only applies to TRUE
   vortex rings with 2π winding. The v8 cached "ring" is a quadrupolar
   phase pattern, not a pure vortex.
3. **A true vortex ring test** would require enforcing a 2π winding
   initial condition and verifying it persists. This is a further
   open test (CPU-080 candidate).
4. **The bending probe measurement** should be re-cast. Test 3f
   measures pulse-centroid shift in a diffraction + scattering regime,
   not pure gravitational deflection. Recasting requires longer path
   and/or higher-k pulse.

## Status

`candidate-partial-eikonal` — §1–§4 structural EOM corroborated in
eikonal in-core regime (k-scan, §13); §5 cancellation retracted for v8
(§12, QNG-CPU-080); out-of-core residual unresolved.

**Domain of validity (established by §13 k-scan):**
- Eikonal in-core: λ < R AND b ≤ R ⇒ scalar prediction quantitative
  (within 16% at k=3π/4, b=4)
- Diffraction: λ ≳ 2R ⇒ scalar fails by 1–2 orders, sign unreliable
- Out-of-core (b > R): magnitude recovers in eikonal limit but **sign
  disagrees** — additional mechanism present

Further promotion of §1–§4 to `derivation` (locked) requires:

1. ~~Test on a true 2π-winding vortex ring (CPU-080 candidate)~~
   **Retracted 2026-04-20.** CPU-080 measured the winding number
   directly and confirmed v8 dynamics destroy the 2π topology
   (sine-Gordon vacuum is Z, not U(1)). A "winding-preserving" test
   would require adding a U(1) gauge sector to v8, which contradicts
   DER-QNG-042.
2. ~~Diffraction/eikonal separation in bending probe (new GPU test) —
   isolate the geometric-optics bending from wavelength-scale
   diffraction.~~ **PARTIAL CLOSURE 2026-04-20** — see §13 (k-scan).
   Eikonal recovery confirmed at b=4 (in-core); sign residual at b=6
   (out-of-core) opens new sub-item 2a.

   2a. **(NEW)** Distinguish back-reaction (O(A²)) from amplitude-
   modulation / kinetic-mode coupling for the positive b > R bending
   residual. Pre-registered as A-scan probe candidate (CPU-081 or
   GPU-021): vary pulse amplitude A ∈ {0.025, 0.05, 0.10} at fixed
   k=3π/4, b=6.
3. Direct numerical verification of m_eff²(x) = (g/(2μ_φ))·Δ²·cos(φ_bg)
   on the cached quadrupolar φ_bg, with k_pkt >> 1/R pulses.
4. Closed-form expression of α in terms of the actual relaxed φ_bg
   profile (not the idealized arctan2 winding).

## §12 Postscript (2026-04-20): §5 cancellation mechanism retracted

**CPU-080 winding diagnostic** (`07_validation/prereg/QNG-CPU-080.md`,
`07_validation/audits/qng-ring-winding-diag-v1/summary.md`) measured
the winding number of the cached L=28 R=4 ring's φ field on closed
poloidal loops using angle-safe interpolation (cos, sin separately,
then arctan2 — needed to avoid the ±π branch-cut artifact).

**Result:**
- Initial condition `init_phi_single_ring(28,4)`: |W| = 1.000 on all
  r_loop ∈ {1.0, 1.5, 2.0, 2.5} (algorithm validated).
- Cached ring after Phase-1 + Phase-2 (1300 lu total): |W| = 0.000
  on all r_loop. Global `|φ|_max = 2.31 < π` — the field is fully in
  the principal branch.

**Conclusion: the v8 evolution destroys the 2π winding.** This is not
a diagnostic artifact; it is consistent with the sine-Gordon structure
of V_couple = (g/2)·Δ²·(1 − cos φ), whose vacuum manifold is the
discrete Z set {φ = 0 mod 2π}, not a U(1) circle. A 2π winding
configuration is smoothly deformable to φ = 0 by paying a finite
gradient + potential energy — which is exactly what Phase-1 relaxation
does.

**Implications for this derivation:**

- §1–§4 (Lagrangian → EOM, m_eff²(x) = (g/(2μ_φ))·Δ²·cos(φ_bg))
  **remain correct**. The EOM is structural.
- §5 thin-ring in-plane cancellation via u → −u antisymmetry of
  cos(φ_bg) with φ_bg = arctan2(dy, dx) is **retracted for v8**. The
  cached φ_bg is a quadrupolar soft pattern with |φ|<1.1, cos(φ_bg) ~
  0.5–0.88 along in-plane paths, no sign changes. Cancellation does
  not occur.
- §5.4 attribution of the 100× α gap to cos(φ_bg) cancellation is
  **falsified**.
- §6.3 and §6.4 predictions (W+/W− identical, n=2 winding smaller α)
  are **untestable in v8** because no n ≠ 0 configuration is stable.

**The 100× gap is now carried entirely by the alternative mechanisms:**
eikonal breakdown (λ ~ R), amplitude modulation, O(A²) back-reaction.

**For DER-QNG-038 (baryon ladder):** the conserved charge is the
Channel-F-balanced σ_m deficit (Noether charge of the σ_m sector),
not the phase topology. The spin/isospin identification from ring
radius R must be rewritten without appealing to phase winding.

---

## References

### Parent derivations
- `DER-QNG-042` (qng-v8-canonical-extension-v1.md) — full action
- `DER-QNG-045` (qng-torus-gravity-v1.md) — scalar Poisson (downgraded)
- `DER-QNG-044` (qng-einstein-correspondence-v1.md) — Tests 3e, 3f
  data

### Related
- `DER-QNG-043` (qng-lorentz-emergent-v1.md) — Lorentz structure of
  v8, kinetic terms compatible with this coupling
- `qng-chi-status-v1.md` — phi as winding phase, not gauge
- `qng-tesla-gauge-falsified-v1.md` (if exists) — confirms phi is
  Z-winding, not U(1), consistent with cos(n·φ) periodicity

### Evidence
- `07_validation/audits/qng-torus-bending-analytic-v1/summary.md`
  (CPU-078 diagnostic FAIL)
- `07_validation/audits/qng-v8-stability-probe-v1/bending.log`
  (Test 3f measured α(b))
- `07_validation/audits/qng-v8-stability-probe-v1/anisotropy.log`
  (Test 3e P/T = 4)
- `07_validation/audits/qng-v8-bending-k-scan-v1/interpretation.md`
  (k-scan: in-core eikonal PASS, out-of-core sign residual)

---

## §13 Postscript (2026-04-20): k-scan eikonal/diffraction separation

`tests/gpu/qng_v8_bending_k_scan_probe.py` ran the pre-registered
k-scan to test the §11 candidate "eikonal breakdown" mechanism for the
100× α gap from CPU-078 / Test 3f. Identical geometry to the bending
probe (L=28, R=4, ring cache HIT, M_ring=176.85), pulse k swept across
{π/4, π/2, 3π/4} → λ ∈ {8, 4, 2.67} lu, b ∈ {4, 6}.

**Result at b=4 (in-core path)**: monotonic recovery `ratio = α_meas /
α_scalar_th` from −0.038 (k=π/4) → +0.144 (k=π/2) → **+1.154**
(k=3π/4). At λ=2.67 < R=4 the scalar DER-QNG-046 prediction is
quantitative within 16% — the eikonal limit recovers cleanly.
Pre-registered flag `hyp_eikonal_confirmed_k_3pi_4 = true`.

**Result at b=6 (out-of-core path)**: magnitude recovers
(|ratio|=+1.264 at k=3π/4) but **sign is opposite to scalar prediction
across the full k-range**. Measured α stays positive (+5e−3 to
+1.8e−2) while scalar flips between +0.31, −0.13, −0.014. There IS a
real residual at b > R that the scalar DER-QNG-046 EOM does not
capture.

**Conclusions**:

1. The 100× gap from CPU-078 is **largely a domain-of-validity
   artefact** (scalar applied at λ ~ 2R, far from eikonal). DER-QNG-046
   §1–§4 EOM is indirectly corroborated by eikonal-limit recovery.
2. DER-QNG-046's quantitative claim is restricted to **λ < R AND
   b ≤ R**. Outside that domain it is qualitative or wrong.
3. The b > R sign residual is a **new open program**: candidates are
   (i) O(A²) back-reaction, (ii) amplitude modulation / pulse
   scattering, (iii) kinetic-mode coupling not in the V_couple-only
   scalar reduction. An A-scan at fixed (k=3π/4, b=6) would
   distinguish (i) from (ii)+(iii).
4. None of the other DER-QNG-044 verdicts move: E=mc² FAIL, Tesla U(1)
   FALSIFIED, Shapiro 1/b RULED OUT, WEP/Pound-Rebka INCONCLUSIVE.

Full interpretation: `07_validation/audits/qng-v8-bending-k-scan-v1/
interpretation.md`. Raw data: `report.json`. Status promoted from
`candidate-partial` → `candidate-partial-eikonal` to record domain.
