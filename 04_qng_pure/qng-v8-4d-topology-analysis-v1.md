# QNG v8: topology of phi solitons in 4D cubic — theoretical prereq for GPU-027

Type: `derivation`
ID: `DER-QNG-048`
Status: `candidate` (pencil work; no code)
Author: `C.D Gabriel`
Date: `2026-04-21`

---

## Objective

GPU-026 (2026-04-21) confirmed that v8 substrate wave physics is
dimension-robust at the linear level: the phi dispersion scales
correctly as `c² ∝ 1/z` from 3D (z=6) to 4D (z=8). DER-QNG-047 (2026-
04-21) confirmed that v8 in 3D admits no static ring soliton.

Open: does v8 on a 4D cubic lattice admit a stable topological
soliton? Before running a 4D analog of GPU-024d (gradient-flow static
search), we need to answer:

1. What topological classes of defects exist in 4D for a U(1)-valued
   phi field? (In practice: the broken-symmetry group is Z, not U(1),
   because V_couple breaks U(1)→Z; but topology classes survive to
   the symmetry-breaking case for integer winding.)
2. Which classes transfer from the 3D vortex ring, and which do not?
3. For those that do, what is the minimal 4D field configuration on a
   cubic lattice that represents each class?

Without answering (1)–(3), a "4D ring search" has no well-defined
initial condition.

---

## Basic topology recap

For a phi field valued in S¹ (the unit circle), defects are
classified by the homotopy group π_n(S¹) where n is the codimension
of the defect minus one (i.e., n = dim(encircling sphere)).

| n | π_n(S¹) | meaning |
|---|---|---|
| 0 | Z₂ (trivial for smooth) | domain wall (codim 1) |
| 1 | Z | vortex line (codim 2) |
| 2 | 0 | (codim 3): no topologically protected defect |
| 3 | 0 | (codim 4): no topologically protected defect |

For a vortex defect, phi winds by 2π·n around a circle that links
once with the defect. The codim of the defect is `d_ambient - d_defect`:

- 3D, vortex point (codim 3): π_2(S¹) = 0 → no 3D-point vortex exists
- 3D, vortex line/ring (codim 2): π_1(S¹) = Z → **the 3D ring**
- 4D, codim 2 defect (2D sheet/torus): π_1(S¹) = Z → analog exists
- 4D, codim 3 defect (1D curve/ring): π_2(S¹) = 0 → **no such defect**
- 4D, codim 4 defect (point): π_3(S¹) = 0 → no such defect

**Immediate consequence**: a "ring" in 4D defined as a 1D closed curve
(direct analog of the 3D ring embedding) has codim 3 and supports NO
phi winding. Building a 4D curve initial condition and hoping for a
"3D ring in 4D" is topologically impossible for the phi field alone.

---

## Candidate classes for a 4D soliton in v8

### Class A: codim-2 2-torus T² (π_1(S¹) = Z)

A 2-dimensional torus embedded in 4D has codim 2. Any circle
surrounding it in the transverse plane links once, so phi can wind
by 2π·n along that circle. This is the direct topological analog of
the 3D ring (1D circle × codim 2 = π_1 winding).

**Minimal realization on 4D cubic L⁴**:
Parametrize (x, y) as the "transverse" plane around a torus whose
meridian lives in (x, y) and axis in (z, w). For a torus of major
radius R centered at origin in the (z, w) plane and minor radius ρ in
(x, y):

    phi(x, y, z, w) = arctan2(y - y₀(z, w), x - x₀(z, w))

where (x₀(z, w), y₀(z, w)) = R·(cos θ, sin θ) with θ = arctan2(w, z).

Energy scales as the 2D vortex energy times the length of the T²:
`E(T²) ~ σ_string · 4π²·R·ρ`. Assuming v7 ring mass m₃D(R) on 3D gives
the ring-energy-per-unit-transverse-area, the torus mass scales as
4π²R (ratio of torus circumference to ring circumference). For R=ρ=4
on L⁴=16⁴, expect M(T²) ≈ (2π·R) × m_3D_ring ≈ 25× M_3D at same R.

**Problem**: v8 V_couple still breaks U(1)→Z, so the 2π winding still
has a Z-vacuum obstruction. If GPU-024d v2 dissolved the 3D ring via
sine-Gordon unwinding, the same mechanism will act on any 4D torus
slab-by-slab. The codim-2 T² does not escape V_couple's verdict.

**Tentative prediction**: Class A probably dissolves under v8 gradient
flow in 4D, for the same V_couple-related reason as GPU-024d. The 4D
embedding doesn't change the locally 2D problem of a vortex line cross-
section.

### Class B: codim-2 2-sphere S² with Hopf map (π_3(S¹) = 0)

Wait: π_3(S¹) = 0, so a point-like Hopf-type defect is not
protected for a U(1)-valued phi. This class does NOT work.

However: for a higher-target field (e.g., a 2-component unit vector
n ∈ S²) the Hopf invariant π_3(S²) = Z lives. In QNG, phi is a single
angle (target S¹), so Hopf doesn't apply directly to phi. The hopfion
program (CPU-066..072) used a different construction involving a
fake 2-vector built from (sg, phi) — that was always a proxy, not a
strict Hopf texture.

**Class B is structurally ruled out for phi.**

### Class C: σ_m-only lump, no phi winding

Abandon phi topology entirely. The soliton is a localized
mass-deficit lump (sigma_m < sigma_m_ref) held together by Channel F
or alternative mechanism. Phi sits at Z-vacuum (phi = 0) throughout.

**Minimal realization**:
    sigma_m(r) = sigma_m_ref · (1 - A·sech²(r/ρ))
    phi(r) = 0 everywhere
    pi_m = 0, pi_phi = 0

where r is Euclidean 4D radius and ρ is the lump scale.

**V_couple contribution**: V_couple = (g/2)·(sigma_m_ref - sigma_m)²·(1-cos 0) = 0. So V_couple is INACTIVE — no sine-Gordon force on phi, phi stays at 0. **This removes the GPU-024d dissolution mechanism entirely.**

**Issue**: without phi winding, what holds the lump against diffusion?
- Channel F requires phi disorder to pump sigma_m down; with phi=0
  everywhere, disorder = 0 and Channel F is also INACTIVE.
- Left with pure ALPHA*(sigma_m_ref - sigma_m) + BETA_M diffusion.
  These are restoring forces that drive sigma_m back to sigma_m_ref.
  A σ_m lump with no phi winding has NO stabilizing mechanism in v8.

So Class C dissolves even faster than Class A, because the competing
mechanism (Channel F) is absent.

### Class D: domain wall (codim 1) in 4D — π_0(S¹/Z) ≠ trivial

A codim-1 defect in 4D is a 3D hypersurface. For a phi field valued
in S¹/Z (after V_couple breaks U(1)→Z), π_0 = Z/Z = trivial (walls
not topologically protected unless V_couple creates multiple vacua).
Since V_couple = (g/2)·Δ²·(1-cos φ) has a unique vacuum at φ=0 for
Δ > 0, there is no wall defect.

**Class D structurally does not exist.**

### Class E: topological soliton in the (σ_g, σ_m) sector alone

Could there be a topological object that doesn't use phi at all? The
sigma fields are real-valued, not S¹-valued. They admit no topological
classes in the π_n sense. Any "lump" in sigma_g or sigma_m is a
non-topological soliton (boundary at infinity is in the same sector
as the bulk), and standard no-go theorems (Derrick's theorem) apply.

On a finite lattice with periodic BCs, Derrick's theorem is modified
but the conclusion stands: without topology, a sigma-only lump is
unstable to scale change.

**Class E unlikely to yield stable objects.**

---

## Verdict of this analysis

| Class | Works topologically | Survives V_couple? | Has stabilizing mechanism? |
|---|---|---|---|
| A: codim-2 T² with π_1 winding | YES | Probably NO (V_couple unwinds slab-by-slab) | Channel F (inherited from 3D) |
| B: codim-2 Hopf | NO (π_3(S¹)=0) | n/a | n/a |
| C: σ_m lump, no winding | No topology needed | V_couple silent (φ=0) | NO (Channel F also silent) |
| D: domain wall | NO (single φ vacuum) | n/a | n/a |
| E: σ-only non-topological | NO (Derrick) | n/a | n/a |

**Only Class A is empirically worth testing.** It's the topological
analog of the 3D ring, and the mechanism by which v8 might stabilize
it (or fail to) is structurally distinct from the 3D case only in
that the defect is now 2-dimensional rather than 1-dimensional.

---

## Prediction for GPU-027 (if it proceeds)

If Class A (codim-2 2-torus) is built on 4D cubic L=16 (say) and run
through gradient flow, the most likely outcome based on the 3D finding:

1. **Local behavior**: at each cross-section (transverse (x, y) plane
   intersecting the torus sheet), the 2D vortex sees V_couple locally
   as in 3D. Sine-Gordon unwinding proceeds slab-by-slab.
2. **Global behavior**: the 4D extent of the torus (in (z, w) coset)
   adds no new stabilizing term because V_couple and Channel F are
   local in the transverse plane.
3. **Expected verdict**: DISSOLVE (analogous to 3D, possibly slower
   because the T² has twice the phi-gradient content per core radius
   to dissipate).

If the prediction is wrong — the 4D torus survives — then dimension
matters in a non-trivial way for soliton stability, and v8 becomes
preferentially "higher-dimensional". This would be a major structural
finding.

If the prediction is right — the 4D torus also dissolves — then the
obstruction is V_couple itself (or Channel F + sine-Gordon), not a
dimension issue. Conclusion: v8 as currently formulated admits no
topological soliton in any accessible dimension, and the program must
pivot to either:

- (P1) a different V_couple (double-Yukawa, gauge-invariant, etc.)
  that doesn't break U(1)→Z
- (P2) dynamic soliton interpretation (bounded orbits in phase space
  rather than equilibria) — already implicit in DER-QNG-047

---

## Recommendation

Before coding GPU-027:
1. **Settle the V_couple question first**. If the 3D sine-Gordon
   obstruction is generic (applies in any dimension), then a 4D torus
   test is just confirmation, not insight. Resolve whether a different
   V_couple form can restore static rings in 3D. This is a much
   cheaper experiment: modify `F_phi_full` and `F_sm_full`, re-run
   `qng_v8_static_ring_search_v2` with the new coupling.
2. If a modified V_couple DOES admit 3D rings: then GPU-027 (4D torus)
   becomes interesting — both dimensions stabilize with the right
   coupling.
3. If no V_couple form admits 3D rings: GPU-027 at best gives a
   consistency check and at worst a redundant confirmation. Pivot to
   P2 (dynamic soliton) ontology.

**Concrete proposed next experiment**:
`qng_v8_static_ring_search_v3.py` — re-run the GPU-024d v2 protocol on
the cached L=28 R=4 3D ring with four alternate V_couple forms:

- (a) pure phi-mass: V = (m²/2)·(g/2)·(σ_m_ref-σ_m)²·φ² (no sine, preserves U(1))
- (b) doubled pitch: V = (g/2)·Δ²·(1-cos 2φ) — π₁(S¹/Z₂) = Z₂, partial
- (c) quartic: V = (g/4)·Δ²·(1-cos φ)² — weaker local pull
- (d) zero (baseline control, already done in GPU-024d v2 B)

Each takes ~60 s (30000 iter, v2 timing). Total ~4 minutes.

If any of (a)–(c) preserves M_ring > 50 after 30000 iter, the 3D
ring is rescued by an alternative potential. That result alone is
worth pursuing over a 4D probe.

---

## Status

**Candidate — theoretical prereq for GPU-027.** No code written yet.

Upstream dependencies:
- `DER-QNG-042` — v8 canonical extension (defines V_couple)
- `DER-QNG-047` — no static ring in 3D
- `GPU-026` — dimension-robust linear dispersion confirmed

Downstream decision points (contingent):
- **GPU-027** — 4D codim-2 T² stability test
- **GPU-028** (newly proposed) — alternate V_couple forms in 3D
  (cheaper, more informative)

Recommendation is to pursue GPU-028 before GPU-027.
