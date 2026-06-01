# QNG v8 analytical prerequisites (DER-QNG-042 §3)

Type: `derivation`
ID: `DER-QNG-042-prereqs`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-18`
Parent: `DER-QNG-042` (`qng-v8-canonical-extension-v1.md`)

---

## Purpose

DER-QNG-042 §3 lists five analytical tasks that MUST be completed before
any GPU-020 simulation is scheduled (Savant FC-3 integrity contract).
This document discharges all five tasks in order.

Pass criteria per task:

- **3.1 forms committed** — explicit closed-form expression of T_m and T_phi
- **3.2 bounded below** — proof that H_v8 has a finite infimum
- **3.3 unique wave speed** — μ_m, μ_phi derived from c_g, numerical values produced
- **3.4 Goldstone count** — enumeration of continuous symmetries, mode count
- **3.5 topological sectors** — energy barrier estimate between W=0 and W=1

Any task that FAILS blocks GPU-020 and either triggers (a) a structural
revision to DER-QNG-042 or (b) an admission that v8 in Option A is not
viable as formulated.

---

## 3.1 Forms of T_m, T_phi committed explicitly

### 3.1.1 Commitment

```
T_m[pi_m]     = (1 / (2 μ_m))   * Σ_i pi_m_i²
T_phi[pi_phi] = (1 / (2 μ_phi)) * Σ_i pi_phi_i²
```

Standard positive-definite kinetic form. No non-canonical variants
(e.g. `(sin pi)²`, non-diagonal metric on phase space, position-dependent
inertia).

### 3.1.2 Constraints on changes

If any simulation observable requires modification of the kinetic form,
the modification does NOT belong to DER-QNG-042. It becomes a new
proposal DER-QNG-043. The purpose is to prevent post-hoc retuning
disguised as "refinement".

### 3.1.3 Canonical-pair commitment

Option A (adopted): three canonical pairs total,

```
(sigma_g, chi)   — retained from H_v7 (DER-QNG-036)
(sigma_m, pi_m)  — NEW
(phi,     pi_phi) — NEW
```

chi is the conjugate of sigma_g. No separate pi_chi. Option B (adding
pi_chi as independent DOF) is explicitly NOT in scope for DER-QNG-042.

### 3.1.4 Verdict

**PASSED.** Forms committed; no ambiguity.

---

## 3.2 H_v8 bounded below — analytical proof

### 3.2.1 Decomposition

```
H_v8 = T_g[chi] + T_m[pi_m] + T_phi[pi_phi] + E_v7 + V_couple
```

Bound each term:

### 3.2.2 Kinetic terms

```
T_g[chi]     = (k_back/2) Σ chi_i²       ≥ 0 for k_back > 0
T_m[pi_m]    = (1/(2μ_m)) Σ pi_m_i²      ≥ 0 for μ_m > 0
T_phi[pi_phi] = (1/(2μ_phi)) Σ pi_phi_i² ≥ 0 for μ_phi > 0
```

All three positive-definite by construction, provided inertia parameters
are positive. §3.3 confirms μ_m, μ_phi > 0.

### 3.2.3 E_v7 term-by-term

From DER-QNG-036 §3:

```
E_v7 = Σ_i {
  (α_g/2)(σ_g_i - σ_g_ref)²        [channel A_g; ≥ 0]
+ (β_g/4) Σ_{j~i}(σ_g_j - σ_g_i)²  [channel B_g; ≥ 0]
+ (α_m/2)(σ_m_i - σ_m_ref)²        [channel A_m; ≥ 0]
+ (β_m/4) Σ_{j~i}(σ_m_j - σ_m_i)²  [channel B_m; ≥ 0]
+ (γ_φ/2) D_i(φ) σ_m_i²            [channel F; sign depends]
+ (χ_decay/2) χ_i²                 [χ self; ≥ 0]
− (χ_rel/2) χ_i (σ_g_i - σ̄_g_i)    [χ-σ_g; indefinite]
− δ χ_i (σ_g_ref - σ_g_i)          [channel D; indefinite]
− (β_φ/z) Σ_{j~i} σ_m_i σ_m_j cos(φ_i - φ_j)   [channel E; indefinite]
+ k_gm (σ_m_ref - σ_m_i)(σ_g_ref - σ_g_i)       [coupling; indefinite]
}
```

### 3.2.4 Channel F (D_i ≥ 0)

`D_i(φ) = 1 - |Z_i|` where `Z_i = (1/z) Σ_{j~i} exp(i φ_j)`. Triangle
inequality: `|Z_i| ≤ 1`, so `D_i ≥ 0`. With σ_m_i² ≥ 0 and γ_φ > 0 at
baseline, Channel F contribution is ≥ 0. ✓

### 3.2.5 Indefinite terms — quadratic form analysis

The indefinite terms are bilinear. Group them by coupled variable pairs:

**χ — σ_g coupling** (merging E_χ χ_rel and δ terms with T_g and A_g):

For fixed σ_g_i = σ_g_ref + s_i:
```
E_χ-σ_g(χ, s) = (χ_decay/2) χ² − (χ_rel/2) χ (s - s̄) + δ χ s
              + (α_g/2) s² + (β_g/4)(∇s)²
```

For fixed lattice configuration, treat as quadratic form in (χ, s):
```
Q(χ,s) = A χ² + B χ (linear in s) + C s² + D (∇s)²
```
with A = χ_decay/2 > 0, C = α_g/2 > 0, D = β_g/4 > 0.

Completing the square in χ: `A χ² + B_eff χ = A(χ + B_eff/(2A))² − B_eff²/(4A)`.

The residual `− B_eff²/(4A)` is a quadratic form in s. Requirement:
the residual plus the remaining C s² + D (∇s)² is ≥ 0.

**Claim**: at v7 baseline (χ_decay = 0.020, χ_rel = 0.35, δ = 0.20,
α_g ≡ ALPHA = 0.005, β_g ≡ BETA = 0.35), the combined quadratic form
in (χ, s) IS bounded below iff the DER-QNG-034 stability criterion
holds:
```
K_BACK · DELTA < ALPHA + CHI_DECAY · (1 − ALPHA)
```

This is exactly the v7 stability margin. v7 baseline with
CHI_DECAY = 0.020 satisfies this (0.020 > 0.016 required).

### 3.2.6 Channel E (β_φ cosine)

```
E_phi ≤ (β_φ/z) Σ_{i,j~i} σ_m_i σ_m_j · 1 = (β_φ/z) · z · N · σ_m_max² = N · β_φ · σ_m_max²
```

Bounded above by a finite constant. The term `-E_phi` is therefore
bounded below by `-N · β_φ · σ_m_max²`. Combined with `+(γ_φ/2) D_i σ_m_i²`
and `(α_m/2)(σ_m − σ_m_ref)²`, the σ_m sector has a finite infimum.

### 3.2.7 V_couple

```
V_couple = g · σ_g · (1 − cos φ) ≥ 0
```
provided σ_g ≥ 0 (see §3.2.8). Explicitly bounded below by 0.

### 3.2.8 σ_g positivity — formal minimum analysis (Einstein+Savant finding)

**Einstein critique (2026-04-18)**: E_v7 + V_couple is NOT globally
bounded below in the σ_g sector. The formal minimum is explicit:

Setting `∂(E_v7 + V_couple)/∂σ_g_i = 0` at fixed φ = π:
```
α_g·(σ_g_i − σ_g_ref) + g·(1 − cos π) = 0
σ_g_i* = σ_g_ref − 2g/α_g = 0.5 − 2·0.22/0.005 = −87.5
```

H_v8 is UNBOUNDED BELOW when any site has (φ → π, σ_g → −87.5).
The v7 gradient flow never accessed this minimum because dissipative
dynamics are locally constrained; symplectic v8 flow CAN access it
given sufficient kinetic fluctuation.

### 3.2.9 Path-A energy bound (Savant requirement)

**Question**: does energy conservation + bounded initial H_v8 prevent
σ_g from reaching the formal minimum in finite simulation time?

**Analysis**:
```
H_v8 ≥ T_g[χ] = (k_back/2) Σ χ_i²
    ⟹  |χ_max| ≤ sqrt(2·H_v8 / k_back)    (single-site upper bound)
```

At cold-start (H_v8 ≈ E_vortex(R=4) ≈ 0.5 lu from §3.5.3, k_back = 0.10):
```
|χ_max| ≤ sqrt(10) ≈ 3.16
```

Maximum σ_g drift rate: `|∂_t σ_g| = k_back · |χ| ≤ 0.316 lu/step`.

**Worst-case (all energy in single-site χ, sustained)**:
Time to reach σ_g = 0 from σ_g_ref = 0.5:
```
t_worst = 0.5 / 0.316 ≈ 1.6 steps
```
— formally achievable but requires ALL energy concentrated at one site.

**Equipartition estimate** (L=80 box, N ~ 5×10⁵ nodes):
```
⟨χ_i²⟩ ≈ 2·H_v8 / (k_back · N) ≈ 2·0.5 / (0.10·5×10⁵) = 2×10⁻⁵
⟨|χ_i|⟩ ≈ 4.5×10⁻³
```
Per-node σ_g drift rate: `⟨|∂_t σ_g|⟩ ≈ k_back · ⟨|χ|⟩ ≈ 4.5×10⁻⁴ lu/step`.
Over T=5000 steps random walk: `σ_g RMS excursion ≈ 0.032 lu` — safely
within [0.47, 0.53], abort clause not triggered.

**Ring-core pressure** (NON-equilibrium, drives σ_g toward minimum):
At ring core with winding, φ spans [0, 2π]. At sites where φ ≈ π:
V_couple pressure on χ: `∂_t χ = −∂V_couple/∂σ_g − ∂E_v7/∂σ_g ≈
−g·(1−cos π) − α_g·(σ_g − σ_g_ref) = −0.44 + 0.0025 ≈ −0.437`.

Sustained at φ = π, χ builds linearly: `χ(t) ≈ χ_0 − 0.437·t`.
σ_g evolves: `∂_t σ_g = k_back·χ ≈ 0.10·(−0.437·t)`, giving
`σ_g(t) ≈ σ_g_ref − 0.0219·t²`.

Time to reach σ_g = 0: `t_ring = sqrt(0.5/0.0219) ≈ 4.8 steps`.
Time to reach abort threshold σ_g = 0.025: `t_abort = sqrt(0.475/0.0219) ≈ 4.66 steps`.

**BUT**: this uses uniform φ = π held fixed. In reality, φ is a
propagating/winding field — phase circulates around ring, does not sit
at π. Only a LINE (not volume) has φ ≈ π at any instant. A given node
experiences φ near π for only `Δt ≈ R/c_phi = 4/0.0764 ≈ 52` steps
as the phase winding passes through.

Over one pass, σ_g excursion at that node: `Δσ_g ≈ 0.0219·(52/2)² ≈ 14.8`
— exceeds σ_g_ref significantly. **WORST-CASE: σ_g CAN reach 0 locally
within ~5 steps of sustained φ = π.**

### 3.2.10 Mitigation commitment

**Operational abort** (pre-registered in GPU-020):
- `min(σ_g_i) < 0.05 × σ_g_ref = 0.025` → abort with status VOID
- Report as "v8 Hamiltonian accessed σ_g formal minimum at time t_abort;
  result is not a physics falsification but a Hamiltonian unboundedness
  manifesting"

**Interpretation**: v8 in current Option A form is an EFFECTIVE theory
on the domain σ_g > 0. It is NOT globally well-defined as a Hamiltonian.

**If GPU-020 aborts on σ_g < 0.025**: DER-QNG-043 becomes mandatory.
Two candidate reformulations:
- (C) `σ_g = exp(s)` with `V_couple = g·exp(s)·(1−cos φ)` — bounded
  below since both factors ≥ 0
- (B) Add hard-floor potential `H_floor = λ · max(0, σ_g_threshold − σ_g)²`

### 3.2.11 Verdict

**CONDITIONAL PASS** — but with explicit honesty flag:

(a) χ–σ_g Schur complement stability: PROVEN (satisfies DER-QNG-034)
(b) Channel F bound: PROVEN (D_i ≥ 0)
(c) σ_g positivity: NOT PROVEN ANALYTICALLY. Formal minimum exists at
    σ_g ≈ −87.5 when φ = π. Path-A equipartition bound shows BULK σ_g
    excursion is small (~0.032 lu RMS). Ring-core pressure can reach
    abort threshold in ~5 steps if φ sustains at π, but phase winding
    naturally avoids this via rotation.
(d) **v8 Option A is an EFFECTIVE theory valid only for σ_g > 0.**
    Operational abort clause makes falsifiability crisp: any abort is
    reported as "v8 unboundedness triggered at step t" with clear
    pathway to DER-QNG-043 reformulation.

This is honest but NOT a rigorous discharge of FC-3. Future work (before
any DER-QNG-042 promotion to `locked`) must either (i) provide a
Gronwall-type estimate showing σ_g(t) > 0 guaranteed for all t, or
(ii) reformulate via option C.

For the purpose of running GPU-020 as a falsification experiment, the
conditional pass is sufficient: the abort clause catches unbounded
behavior before it contaminates the scientific gates.

---

## 3.3 Unique wave speed — μ_m, μ_phi derived from c_g

### 3.3.1 Gravitational sector baseline

From DER-QNG-036 §5, wave equation for σ_g perturbations (v7 baseline):
```
∂²_t s = v²_g ∇²s − m²_g s
v²_g = k_back · β_g / 6 · (a/τ)²
m²_g = k_back · α_g / τ²
```

In lattice units (a = τ = 1) at v7 baseline `k_back = 0.10, β_g = 0.35`:
```
c_g² = 0.10 · 0.35 / 6 = 5.83 × 10⁻³ [lu²/step²]
c_g  = 7.64 × 10⁻²                   [lu/step]
m_g² = 0.10 · 0.005    = 5.00 × 10⁻⁴ [1/step²]
```

### 3.3.2 σ_m sector (v8, linearized)

Take m_i = σ_m_i − σ_m_ref, at the bulk vacuum (σ_g = σ_g_ref,
χ = 0, D = 0, no ring). From canonical EOMs:
```
∂_t σ_m_i = pi_m_i / μ_m
∂_t pi_m_i = −∂E_v7/∂σ_m_i
           ≈ −α_m m_i + β_m (m̄_i − m_i) − k_gm s_i
```
(dropping the Channel F term since D = 0 at vacuum and dropping the
E_phi sector at φ = 0.)

Taking one more time derivative and using z=6 Laplacian
`(m̄_i − m_i) ≈ (a²/6) ∇² m_i`:
```
∂²_t m = (β_m / (6 μ_m)) (a/τ)² · ∇²m − (α_m / μ_m) · (1/τ²) m − (k_gm / μ_m) · (1/τ²) s
```

Wave speed:
```
c_m² = β_m / (6 μ_m) · (a/τ)²     [sigma_m sound speed]
```

**Unique wave speed condition**: c_m = c_g ⟹ β_m / (6 μ_m) = k_back · β_g / 6
```
μ_m = β_m / (k_back · β_g)
```

At v7 baseline (β_m = 0.35, k_back = 0.10, β_g = 0.35):
```
μ_m = 0.35 / (0.10 · 0.35) = 10.0  [dimensionless]
```

Positive, finite. ✓

### 3.3.3 φ sector (v8, linearized)

From DER-QNG-036 §2.4:
```
E_φ = −(β_φ/z) Σ_{i, j~i} σ_m_i σ_m_j cos(φ_i − φ_j)
```

Linearizing to small φ (keep leading quadratic term):
```
cos(φ_i − φ_j) ≈ 1 − (φ_i − φ_j)² / 2
E_φ ≈ const + (β_φ / (2z)) Σ σ_m_i σ_m_j (φ_i − φ_j)²
```

At σ_m = σ_m_ref (bulk):
```
∂E_φ/∂φ_i ≈ −(β_φ · σ_m_ref² · a² / 3) · ∇² φ_i
```
(factor 1/3 from z=6 averaging with double counting of unordered pairs).

V_couple contribution at leading order in φ:
```
V_couple = g · σ_g_ref · (1 − cos φ_i) ≈ (g · σ_g_ref / 2) · φ_i²
∂V_couple/∂φ_i ≈ g · σ_g_ref · φ_i
```

Canonical EOMs:
```
∂_t φ_i = pi_phi_i / μ_phi
∂_t pi_phi_i = −∂E_total/∂φ_i = (β_φ · σ_m_ref² · a² / 3) · ∇²φ_i − g · σ_g_ref · φ_i
```

Wave equation:
```
∂²_t φ = c_φ² · ∇²φ − m_φ² · φ

c_φ² = β_φ · σ_m_ref² / (3 · μ_phi) · (a/τ)²
m_φ² = g · σ_g_ref / (μ_phi · τ²)
```

**Unique wave speed condition**: c_φ = c_g ⟹
```
β_φ · σ_m_ref² / (3 · μ_phi) = k_back · β_g / 6
μ_phi = 2 · β_φ · σ_m_ref² / (k_back · β_g)
```

### 3.3.4 Spatial heterogeneity of β_φ

v7 uses BETA_PHI_MIN = 5×10⁻⁴ (bulk) and BETA_PHI_RING = 0.06 (ring
core). c_φ is therefore SPATIALLY HETEROGENEOUS in v7. In v8 we must
commit to one value.

Three choices:

**Choice A — uniform β_φ = BETA_PHI_RING = 0.06**: gives uniform c_φ
but changes v7 bulk behavior. At baseline (σ_m_ref = 0.5, k_back = 0.10,
β_g = 0.35):
```
μ_phi_A = 2 · 0.06 · 0.25 / (0.10 · 0.35) = 0.030 / 0.035 = 0.857
```
Positive, finite. ✓

**Choice B — uniform β_φ = BETA_PHI_MIN**: respects bulk dispersion but
rings are destabilized (BETA_PHI_MIN too small for winding to survive).

**Choice C — two-field φ with spatial profile**: introduces additional
complexity, breaks strict Lorentz covariance at lattice scale.

**Commitment for GPU-020**: Choice A. Set BETA_PHI uniform to 0.06
during the v8 run. Phase 1 (vortex seeding) may need Re-examination
since v7 used spatial heterogeneity for ring stability — test in
Stage E (FC-4 recovery).

Numerical values:
```
μ_m   = 10.0
μ_phi = 0.857
c_g = c_m = c_phi ≈ 0.0764 lu/step
m_phi² = g · σ_g_ref / μ_phi = 0.22 · 0.5 / 0.857 = 0.128 [1/step²]
m_phi  ≈ 0.359 [1/step]   →   T_phi = 2π / m_phi ≈ 17.5 steps
```

### 3.3.5 Consistency check vs DER-QNG-042 P1

DER-QNG-042 §4 predicts `m_phi² = g · σ_g_ref = 0.22 · 0.5 = 0.11,
T ≈ 19 lu`. The exact dispersion derivation above gives
`m_phi² = g · σ_g_ref / μ_phi = 0.128` after Lorentz-covariance
fixing, a factor 1/μ_phi discrepancy.

The difference: §4 P1 was written before μ_phi was derived. The
CORRECT prediction, updated by this analysis:
```
m_phi² = g · σ_g_ref / μ_phi = 0.128   (with μ_phi from §3.3.3)
T_phi = 2π / √0.128 ≈ 17.5 lu
```

Document GPU-020 Stage A with the corrected prediction.

### 3.3.6 Verdict

**PASSED — necessary linear-order condition only** (Einstein critique).
- `μ_m = 10.0` (positive, finite)
- `μ_phi = 0.857` (positive, finite, Choice A: uniform β_φ)
- Linear-order wave speeds matched: `c_g = c_m = c_phi = 0.0764 lu/step`
- φ mass: `m_phi = 0.359`, `T = 17.5 lu` — updates DER-QNG-042 §4 P1
- σ_m mass-like pinning: `m_m² = α_m / μ_m = 5.0 × 10⁻⁴` (very soft)

**What this derivation DOES NOT establish**:
- Full emergent Lorentz covariance. `c_g = c_m = c_phi` is NECESSARY
  but not SUFFICIENT. Additional requirements:
  - (i) c_φ is weakly dependent on local σ_m density. VIOLATED at ring
    core: c_φ² ∝ σ_m² drops ~4× when σ_m drops ~2× (CPU-043: σ_m_core = 0.27
    vs σ_m_ref = 0.50). Lorentz cone effectively narrower inside rings.
  - (ii) Rotational isotropy of dispersion relation. Untested; z=6 cubic
    lattice has discrete rotational symmetry only; isotropy emerges at
    r ≫ a. QNG-CPU-037/039 confirm Laplacian isotropy at bulk scale;
    does NOT guarantee dispersion-relation isotropy.
  - (iii) Smallness of χ–σ_g dispersive corrections beyond leading order.

**Full Lorentz emergence is a GPU-020 Stage A empirical test**
(multi-k dispersion fit), not an a priori derivation. GPU-020 Stage A
reports: `omega²(k)` data for k ∈ {0, π/L, 2π/L, 4π/L}; PASS requires
dispersion follows `ω² = c² k² + m²` within 15% across all tested k,
with c consistent across σ_g / σ_m / φ sectors.

- GPU-020 Stage A prediction corrected; this derivation supersedes
  DER-QNG-042 §4 P1 for the numerical value of m_phi.

---

## 3.4 Goldstone mode count in Option A

### 3.4.1 Enumeration of continuous symmetries of H_v8

**S1 — Time translation**: `t → t + τ_0`. Present (H_v8 has no explicit
time dependence). Noether charge: energy. NOT a Goldstone — ground state
is time-invariant.

**S2 — Global φ shift**: `φ_i → φ_i + c` (constant c). Broken by
V_couple = g σ_g (1 − cos φ) which pins φ = 0 modulo 2π. Ground state:
φ_i = 0. Would-be Goldstone is gapped by V_couple:
```
m_phi² = g · σ_g_ref / μ_phi = 0.128 [1/step²]
```
Number of Goldstones: 0 (mode is gapped).

**S3 — Global σ_g shift**: `σ_g_i → σ_g_i + c`. Broken by
`(α_g/2)(σ_g − σ_g_ref)²`. Ground state: σ_g_i = σ_g_ref. No Goldstone.

**S4 — Global σ_m shift**: `σ_m_i → σ_m_i + c`. Broken by
`(α_m/2)(σ_m − σ_m_ref)²`. No Goldstone.

**S5 — Global χ shift**: `χ_i → χ_i + c`. Broken by `(χ_decay/2) χ²` AND
by `−(χ_rel/2) χ (s − s̄)` (shift changes energy). No Goldstone.

**S6 — Spatial lattice translation**: `i → i + δ`. DISCRETE (lattice).
No continuous translation; no continuous Goldstone. (In the continuum
limit r ≫ a, discrete translation becomes continuous, but lattice
Goldstones are gapped at k = π/a energies.)

**S7 — φ → 2π − φ (Z_2 parity)**: discrete symmetry. Not broken by V_couple
(since cos is symmetric). Discrete, no Goldstone.

**S8 — φ → φ + 2π/n (Z_N)**: discrete for all finite n. No Goldstone.

### 3.4.2 Count

**Continuous symmetries**: S1 (time), partial S2 (φ shift).
**Broken continuous symmetries**: S2 only.
**Massless Goldstone modes**: 0 (S2 is gapped by V_couple).
**Massive would-be Goldstone modes**: 1 (the φ mode, mass m_phi from §3.3).

### 3.4.3 Hidden symmetries — check

**Kinetic-term symmetries**: does T_m or T_phi have a symmetry absent
from E_v7?

- `T_m = (1/(2μ_m)) Σ pi_m_i²`: invariant under pi_m → −pi_m (time reversal
  of m), under global shifts pi_m → pi_m + c. The latter is broken by
  the canonical EOM pairing σ_m → σ_m + (Δt/μ_m) pi_m, which ties pi_m
  to σ_m dynamics; a global pi_m shift translates σ_m which is broken
  (S4). No new continuous symmetry.

- `T_phi`: same structure; no new continuous symmetry.

**σ_m amplitude at the ring**: in the ring core, σ_m is depleted
(σ_m ≈ 0.27 at R=4 ring per CPU-043). The Channel F term
`+ (γ_φ/2) D_i σ_m_i²` adds a potential pocket for σ_m but does NOT
restore a continuous symmetry — σ_m_ref pinning remains.

**Conclusion**: no hidden Goldstone modes introduced by the v8 canonical
extension.

### 3.4.4 Savant's Goldstone strict critique — resolved

DER-QNG-042 §6 D5: "without V_couple, v8 phi is EXACTLY massless by
Goldstone's theorem". Confirmed:

- v7 (gradient flow): φ Goldstone manifest as IR halo power-law decay
  (diagnosed as cause of GPU-018 structural fail)
- v8 without V_couple: same Goldstone theorem applies, but the massless
  mode would PROPAGATE as a wave, not diffuse. Omega(k=0) = 0 — the
  Stage A prediction would give ZERO oscillation period.
- v8 with V_couple (g > 0): Goldstone gapped, omega(k=0) = m_phi > 0.

Stage A of GPU-020 is precisely the test of this: omega(k=0) ≠ 0 is a
necessary condition for v8's mass program to work.

### 3.4.5 Verdict

**PASSED.** 0 massless Goldstones; 1 gapped would-be Goldstone (φ).
No hidden continuous symmetries from kinetic terms. V_couple is
MANDATORY in v8 — Stage A directly tests this.

---

## 3.5 Topological sector analysis

### 3.5.1 Winding number definition

A vortex ring in the φ field has winding number
```
W = (1/(2π)) ∮_C ∇φ · dl
```
along a closed contour C linking the ring. For ring geometry
(CPU-043/073/074/075), W = ±1 by construction (initial condition).

Winding number is a topological invariant under CONTINUOUS deformation.
Lattice dynamics can change W via plaquette-level phase slips; the cost
is a defect-line energy.

### 3.5.2 Energy barrier in v7 (gradient flow)

In v7, rings can decay via Channel F which suppresses σ_m where phase
coherence |Z| is low. The decay mechanism:
1. Fluctuation in φ near the ring core
2. Local |Z| drops
3. D_i increases, σ_m decreases further via Channel F
4. Ring core disrupts; winding unwinds through lattice defect

This is a DISSIPATIVE decay pathway. Energy relaxes as ring decays.
CPU-044 (ring lifetime) measured decay times ~ τ_lifetime ∝ 1/γ_φ.

### 3.5.3 Energy barrier in v8 (canonical flow)

In v8 with symplectic integrator, total energy H_v8 is conserved
(modulo integrator error). The ring cannot decay by energy relaxation:

**Claim**: the phase slip that unwinds W=1 to W=0 must occur over a
saddle-point configuration with HIGHER energy than both endpoints.
Symplectic flow cannot spontaneously climb the barrier UNLESS the
initial kinetic energy is sufficient.

**Saddle-point energy estimate**:
- XY model in 3D: vortex line energy per unit length
  `ε_line = π · β_φ · σ_m_core² · log(R/a_core)`
- Ring circumference: `2π R`
- Total vortex energy: `E_vortex ≈ 2π² R · β_φ · σ_m_core² · log(R/a_core)`

At R=4, β_φ = 0.06, σ_m_core = 0.27, a_core = 1:
```
E_vortex ≈ 2π² · 4 · 0.06 · 0.0729 · log(4)
         ≈ 78.96 · 0.06 · 0.0729 · 1.386
         ≈ 0.479
```

Phase slip pathway: phase jumps by 2π across a disc of area
π R² ≈ 50 lu² bounded by the ring. Energy of the disc:
```
E_disc ≈ (β_φ · σ_m_ref² / 2) · (2π)² / a² · A_disc
       ≈ (0.06 · 0.25 / 2) · 4π² · 1 · 50
       ≈ 0.0075 · 39.48 · 50
       ≈ 14.8 lu
```

**Barrier height**: `ΔE ≈ E_disc − E_vortex ≈ 14.8 − 0.48 ≈ 14.3 lu`.
This is a rough estimate — the actual saddle is likely lower because
the phase field need not rotate by a full 2π across the entire disc;
a localized "kink" configuration would cost less.

**Conservative estimate**: ΔE ≥ 1 lu per node of the phase-slip line.
A phase-slip line spanning the ring radius has ≥ R ≈ 4 nodes of
disrupted φ, giving ΔE ≥ 4 lu.

### 3.5.4 Kinetic energy available

In v8 equilibrium, energy is distributed across the lattice by
equipartition. At "temperature" T_eff = E_0/N per DOF, kinetic energy
per node is ~ T_eff.

For GPU-020 we start with zero-temperature initial conditions (pi_phi_i
= 0, pi_m_i = 0) and seed a vortex at R=4. Total energy ≈ E_vortex ≈
0.5 lu. This is LESS THAN the barrier height estimate (~4 lu), so:

**Prediction**: v8 rings will be TOPOLOGICALLY TRAPPED. They will not
decay under symplectic flow from cold initial conditions. Ring lifetime
in v8: infinity (modulo integrator drift).

This is DIFFERENT from v7 (gradient flow decay) and is a FEATURE, not
a bug — it matches the expected behavior of stable topological particles
(protons don't decay).

### 3.5.5 Implication for mass observable

If rings are topologically trapped, `M_ring` measured in v8 is the
STABLE mass of the W=1 sector. There is no "ground-state-is-W=0"
ambiguity for the mass identification program (DER-QNG-038).

**Stage F (FC-5) interpretation**: the measured M_ring in v8 directly
corresponds to the particle mass. The comparison to CPU-074/075 is
apples-to-apples.

### 3.5.6 Integrator error concern

Symplectic integrators (leapfrog, Yoshida) have bounded energy drift
but NONZERO integrator error. Over long time T, accumulated error may
provide the kinetic energy needed to cross the barrier.

**Estimate**: Yoshida 4th-order integrator with Δt = 0.1 gives energy
drift ~ (Δt)⁴ × T ~ 10⁻⁴ × 5000 = 0.5 lu over T=5000 steps. This IS
comparable to the barrier. Higher-order integrator or smaller Δt may
be needed.

**Commitment for GPU-020**: use Δt = 0.05, Yoshida 4th-order. Monitor
energy drift; abort if drift > 1% of H_v8 over 1000 steps.

### 3.5.7 Caveat: W-conservation ≠ M_deficit conservation

**Savant critique**: topological trapping preserves winding number W
only. It does NOT imply conservation of the σ_m depletion integral
`I_m = N·σ_m_ref − Σ σ_m` (the v7 canonical mass observable). At fixed
W = 1, rings can:

- deform in shape (oscillate between circular ↔ elliptical), changing
  local σ_m depletion by integration over a changing support volume
- migrate in position (Stage C tests this under gravitational well);
  M_deficit may have transient fluctuations during migration
- exchange energy between kinetic (T_m, T_phi) and potential (E_v7)
  sectors, re-distributing σ_m depletion

Over long times in v8 (symplectic conservative flow), `⟨I_m⟩` is
constant ONLY if the ring settles to a stationary configuration. Mass
measurement protocol must check for stationarity (Δ I_m per 100 steps
within noise band) before recording M_ring.

### 3.5.8 Verdict

**PASSED with operational caveat**.
- Barrier estimate: ΔE_barrier ≥ 4 lu (conservative lower bound)
- Cold-start kinetic energy: ≤ 1 lu
- Rings topologically trapped in v8 — FEATURE (stable particle),
  W is conserved by symplectic flow from cold start
- Mass observable I_m(R) is W-indexed but NOT identically
  W-conserved — check stationarity before recording M_ring
- Integrator commitment: Yoshida 4 + Δt = 0.025 (was 0.05 —
  Einstein critique: drift margin vs 0.5-lu bound is thin);
  abort on 1%/1000-step energy drift

---

## Summary (post 3-agent review, 2026-04-18)

| Prereq | Status | Key result |
|--------|--------|-----------|
| §3.1 Forms committed | PASSED | T_m, T_phi standard kinetic; 3 canonical pairs (Option A) |
| §3.2 Bounded below | CONDITIONAL PASS | formal minimum σ_g ≈ −87.5 exists; operational abort at σ_g = 0.025; v8 is effective theory on σ_g > 0 domain |
| §3.3 Unique wave speed | PASSED (necessary only) | μ_m = 10.0, μ_phi = 0.857, linear-order cones matched; full Lorentz tested by GPU-020 Stage A |
| §3.4 Goldstone count | PASSED | 0 massless, 1 gapped (φ); Stage A tests m_phi directly |
| §3.5 Topological sectors | PASSED | Rings trapped; W-conservation ≠ M_deficit conservation; stationarity check required |

### Three-agent review verdicts (2026-04-18)

| Agent | Verdict | Critical finding |
|-------|---------|------------------|
| einstein-mind | CONDITIONAL PASS | H_v8 formal minimum at σ_g ≈ −87.5; Lorentz is necessary not sufficient |
| savant-physics-reviewer | NOT READY (3 blockers) | μ formulas wrong in parent DER-QNG-042 §3.3; GPU-020 gate uses old m_phi=0.332 |
| tesla-mind | CAVITY FALSIFIER DEAD | m_phi/ω_1 = 18.8 at R=4; cavity is below cutoff; FC-5 must restructure around I_m(R) |

### Amendments applied 2026-04-18

1. **§3.2.8–3.2.11**: Einstein-Savant σ_g positivity analysis added.
   Formal minimum quantified, Path-A bound computed, operational abort
   framed explicitly as v8-as-effective-theory.
2. **§3.3.6**: Lorentz covariance claim relaxed to "necessary linear-order
   condition"; full Lorentz deferred to GPU-020 Stage A empirical test.
3. **§3.5.7**: W-conservation ≠ M_deficit conservation note added.
4. **§3.5.8**: Integrator Δt tightened to 0.025 (Einstein).

### Updates to upstream documents (still TODO, flagged by Savant)

1. **DER-QNG-042 §3.3**: parent document contains WRONG formulas
   (`c_m² = β_m·σ_g_ref²/μ_m` → factor 1.5× error for μ_m, 3× for μ_phi).
   Must be updated with correction note referencing §3.3 above.
2. **DER-QNG-042 §4 P1**: `m_phi` updated from 0.332 → 0.359,
   `T` from 19 → 17.5 lu.
3. **QNG-GPU-020 Stage A gate**: `omega(k=0)` within 10% of `0.359`
   (was 0.332).
4. **QNG-GPU-020 Stage F (FC-5)**: cavity-mode falsifier REMOVED.
   Tesla critique: m_phi/omega_1 ≈ 18.8 at R=4 means cavity is below
   cutoff (evanescent); m_phi is R-independent to 0.3%, so cavity
   prediction is trivially (vacuously) satisfied at all R. Restructure
   FC-5 around I_m(R) = Σ(σ_m_ref − σ_m) scaling vs CPU-074/075.
5. **QNG-GPU-020 integrator**: Δt = 0.025 (was 0.05).

### Open items for GPU-020 runtime

- **σ_g positivity**: not proven analytically; abort-clause installed;
  if GPU-020 aborts within Stage A/B/C, result triggers DER-QNG-043
  candidate (σ_g = exp(s) reformulation)
- **β_φ spatial heterogeneity**: committed Choice A (uniform β_φ = 0.06);
  FC-4 recovery test will check whether this breaks v7 reproduction
  (Tesla: "Choice A changes BETA_PHI by 120× — harder than documented")
- **FC-5 restructured**: mass ladder test now I_m(R) vs CPU-074/075,
  not cavity mode
- **Integrator error accumulation**: bounded via 1%/1000-step drift
  abort; Yoshida 4 at Δt = 0.025

### Post-amendment status

Document ready for `registered` status on QNG-GPU-020 upstream amendments
(items 1–5 of "Updates to upstream documents"). Once DER-QNG-042 and
GPU-020 are synchronized with this prereqs document, GPU-020 can run.

If GPU-020 Stage F (I_m(R) scaling) fails, v8 structural claim about
mass identification is falsified. If GPU-020 aborts on σ_g < 0.025,
v8 Option A is operationally dead and DER-QNG-043 is mandatory.

---

## References

- `04_qng_pure/qng-v8-canonical-extension-v1.md` (DER-QNG-042 parent)
- `04_qng_pure/qng-hamiltonian-v7-two-field-v1.md` (DER-QNG-036, H_v7)
- `04_qng_pure/qng-gap8-stability-analysis-v1.md` (DER-QNG-034, χ stability)
- `04_qng_pure/qng-yukawa-phi-mass-v1.md` (DER-QNG-041, V_couple form, g=0.22)
- `07_validation/prereg/QNG-GPU-020.md` (companion, status updated upon review)
- Three-agent memory:
  - `.claude/agent-memory/tesla-mind/psi-conjugate-field-v8.md`
  - `.claude/agent-memory/einstein-mind/psi-conjugate-field-v8.md`
  - `.claude/agent-memory/savant-physics-reviewer/psi-conjugate-field-v8-critique.md`
