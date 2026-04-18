# QNG Mass-Observable Exhaustion Note

Type: `note`
ID: `NOTE-QNG-016`
Status: `active`
Author: `C.D Gabriel`
Date: `2026-04-18`

## Purpose

Record the state after three consecutive falsifications of mass observables
in v5+Channel H (M_ring, full Hamiltonian H_v7, e_B sub-component), so that
future work does not repeat ad-hoc variations on the same exhausted path.

## The five-test chain (updated 2026-04-18)

| Observable | Motivation | Test | Verdict |
|---|---|---|---|
| M_ring = N·σ_ref - Σσ_m | depletion integral, original DER-QNG-038 | GPU-009..014 | FAIL — geometric 5/4 |
| H_v7 = T_g + E_v7 | total energy (conservation) | GPU-015 | FAIL — same IR pathology |
| e_B = (β/4)·Σ(∇σ)² | soliton rest-energy / Bogomolny / bag-model | GPU-016 | FAIL_GEOMETRIC |
| Hopfion Q=1 halo | topological confinement | GPU-017 | FAIL — α=1.89 (worse than ring) |
| V(σ_m) = (λ/4)(σ_m²-σ_ref²)² | GL confinement, λ=0.19 from marginal stability | GPU-018 | **FAIL_H3_STRUCTURAL** |

**Common failure mode:** all three diagnose the same underlying fact —
the field configurations that dominate a v5+Channel H ring at long times
are controlled by box-scale kinematics (IR-sensitive Goldstone halo),
and the R-dependence of any volume-integrated observable inherits the
5/4 ring-perimeter scaling unless localized. Localization removes the
drift (GPU-016 Gate 2 PASS at 0.004 spread) but the converged value is
~4.5 — neither SM (1.313) nor geometric (1.25).

## What localized-e_B tells us (positive content)

- The sigma-gradient IS physically localized at the ring core; the local
  profile stabilizes by L≈60 and is box-independent thereafter. This
  vindicates the Bogomolny / bag-model intuition STRUCTURALLY.
- But `M_ring(R=5)/M_ring(R=4) ≈ 1.04` at L=120 (nearly equal total
  sigma deficit), while the core-tube e_B ratio is 4.84. A larger ring
  packs the same deficit into a sharper gradient — the ring cross-section
  is NOT scale-invariant in R. Power-law fit gives `(R5/R4)^7`.
- Any future mass candidate must either (i) derive this R^7 scaling
  from a physical invariant (unlikely — no obvious topological meaning)
  or (ii) come from a different configuration entirely (Option C).

## What is forbidden (ad-hoc closure path)

- Trying further Hamiltonian sub-components (e_δ, e_A, e_φ, e_dis) as
  "the real mass" without theoretical justification. Rejected: Gate-4
  component scanning in GPU-015 was already informational; GPU-016
  converted the strongest candidate (e_B) into a falsification. Picking
  the next-best unconverged component would be post-hoc pattern matching.
- Extending L to 160, 200, ... expecting the e_B_global ratio to plateau
  above 1.28. Rejected: Model A fit already extrapolates to a=0.356.
- Adjusting Channel H parameters to "fix" the ratio. Rejected: parameters
  are frozen in GPU-011 and must remain so for v5 canonicity.
- Re-assigning baryons at different R values (e.g. R=5→N, R=7→Δ) to
  improve the ratio. Rejected: this is post-hoc pattern fitting.

## Remaining options (both require new theory before GPU time)

### Option B — sigma_m confinement mechanism

Hypothesis: a new substrate channel confines sigma_m, giving it an
intrinsic mass scale and breaking the ring-perimeter geometric scaling.

**Required before testing:**
1. Derivation of a sigma_m confinement term in the v7 Hamiltonian E_v7.
2. Demonstration that the confinement length scale is dynamically
   generated (not an imposed parameter). Otherwise it becomes a free
   knob.
3. Prediction that the resulting mass ratio is not purely geometric —
   i.e. explicit computation showing R-dependence is controlled by the
   confinement scale, not by ring perimeter.
4. CHI_DECAY and K_GM stability proof for the new Hamiltonian.

Until these exist, any Option B GPU test is ad-hoc.

### Option C — different mass carrier

Candidates (from existing lanes, not new):

- **Hopfion Q=1** (CPU-066..072): ~~mass scaling vs. Hopfion size
  parameter has been measured only at single L. Need L-convergence
  test analogous to GPU-009.~~ **UPDATE 2026-04-18, GPU-017 FAIL**:
  Hopfion disorder-profile L-scan (pre-reg QNG-GPU-017, artifacts
  `07_validation/audits/qng-hopfion-disorder-l-scan-v1/`) shows
  Hopfion alpha = 1.89 at L=80 (slower decay than the ring's 2.39).
  Topology does NOT cure the IR halo — it makes it worse. The extra
  toroidal winding creates additional Goldstone disorder at large r.
  Power-law wins over exponential (ΔR² = -0.025), so no mass gap.
  Option C Hopfion route **falsified at structural level**.
- **Excited ring modes** (orbital L=1, 2, ...): QNG-native construction
  of L>0 angular eigenstates not yet attempted. Would address Roper
  N*(1440) absence. **Still open**, but would inherit the same IR
  halo pathology since phi remains massless.
- **Two-ring composites** (CPU-050 Lennard-Jones potential): bound
  deuteron-like states. Has existing CPU data; needs GPU L-convergence.
  **Still open**, same pathology expected.

**After GPU-017, Option B becomes the ONLY remaining path.** The IR
halo is a universal property of the massless phi Goldstone, not of
any single topological sector.

## Decision

The baryon resonance ladder in DER-QNG-038 §2 is DOWNGRADED from
"CONFIRMED numerical pattern" to "coincidence at T_P2=1000/L=20
protocol convention". Section §2 must not be cited as evidence for
QNG predicting SM mass ratios. The isospin-from-parity finding
(even R → I=1/2, odd R → I=3/2) stays valid — it is topological
and does not depend on mass measurement.

Gap 4 (matter-source identification) is reopened as a primary open
problem, demoted from "substantially advanced" back to "open".

## Upstream / dependencies

- `07_validation/audits/qng-e-b-l-scan-v1/` — GPU-016 result
- `07_validation/audits/qng-hamiltonian-l-convergence-v1/` — GPU-015 result
- `04_qng_pure/qng-particle-mass-identification-v1.md` §1.1 — DER-QNG-038
  with GPU-015 and GPU-016 FAIL blocks
- `04_qng_pure/qng-vortex-ring-catalog-v1.md` Q1 — updated with GPU-016
- Savant physics review (2026-04-18) — refuted ADM analog, redirected to
  Bogomolny; Bogomolny now also falsified numerically.

## What would close this note

After GPU-017 falsified the Hopfion topology pivot, Option C is greatly
narrowed (remaining candidates have the same universal halo pathology).
**Option B has since been formalized in DER-QNG-040 (2026-04-18)**:

- `04_qng_pure/qng-sigma-m-potential-v1.md` derives
  `lambda = (gamma_phi - alpha_m) / (2*sigma_ref^2) = 0.19` via
  marginal-stability extension of DER-QNG-034 (Route a).
- `07_validation/prereg/QNG-GPU-018.md` commits lambda=0.19 and four
  non-riggable gates (A: halo >=3.5; B: FWHM≈4.52 R-independent;
  C: mass ratio L-converged in [1.25,1.40]; D: r_eff≈0.10).

Option B prerequisites status:
1. V(σ_m) term derived — DONE (DER-QNG-040)
2. Dynamically generated length scale (ξ=1.92 lu from primitives) — DONE
3. Non-geometric R-dependence proof — DEFERRED to GPU-018 Gate B
4. Stability proof — marginal-stability saturation is the derivation

**Closure pathways (GPU-018 decision rule):**
- PASS_H1: all four gates → DER-QNG-040 locked; this note closed.
- FAIL_H2_LAMBDA: structural form right, saturation wrong → Gap 9
  (Yukawa-analog). Re-register as GPU-018B with lambda as committed
  EFT parameter. Note remains open but redirected.
- FAIL_H3_STRUCTURAL: Gate A fails → V(σ_m) insufficient. Program halted
  pending new theory (no candidate identified).

## QUINTUPLE-FAIL (2026-04-18, GPU-018 verdict)

**GPU-018 returned FAIL_H3_STRUCTURAL.** V(σ_m) at the predicted
saturation value λ=0.19 fails three of four gates:

- **Gate A (halo)**: α = 2.49 at L=80, R=5 — unchanged from v5+H baseline.
  V(σ_m) does not cure the halo at all.
- **Gate B (FWHM)**: 1.00 lu everywhere — over-suppression collapses σ_m
  profile to a single lattice cell.
- **Gate C (ratio)**: 1.031 at L=120 (collapsing monotonically from 1.070
  at L=60). Mass observable becomes R-degenerate at large L.
- **Gate D (r_eff)**: 0.1055 PASS — linearized damping mathematics is
  correct; the potential just does not produce the right physics.

### Structural diagnosis (universal to GPU-009..018)

**The halo is a phi Goldstone boson.** The observable
`disorder(phi)·σ_m ∝ ⟨sin²(Δphi/2)⟩` is dominated by the phi field.
In v5+Channel H and in every variant tested, the global U(1) shift
symmetry `phi → phi + c` is unbroken. By Goldstone's theorem, phi is
massless, and its long-range correlations produce the power-law halo.

Every σ_m-sector modification (depletion integral, Hamiltonian,
Bogomolny gradient, topology, GL potential) leaves this symmetry
intact and therefore inherits the halo. **The five-test chain is not
a coincidence — it is a structural consequence of Goldstone's theorem.**

### What DER-QNG-040 FAIL forecloses

- Single-field potentials on σ_m cannot cure the halo (proven structurally).
- Topological sigma_m modifications (Hopfion and variants) cannot cure it
  (proven by GPU-017).
- Box-scale coarsening (larger L) only makes the ratio worse, not better.

### Only remaining structural direction

Explicitly break the U(1) shift symmetry of phi. The minimal realization
is a σ_m·phi Yukawa coupling of pion-analog form:

```
V_couple = g · σ_m · (1 - cos phi)
```

- Bulk (σ_m = σ_ref): expand `1 - cos phi ≈ phi²/2` → m²_phi = g·σ_ref
- Ring core (σ_m → 0): m²_phi → 0, vortex can form unimpeded
- Symmetry: `phi → phi + 2π` preserved; `phi → phi + c` broken — phi
  acquires a mass in the σ_m condensate (GMOR analog: m_π² ∝ m_q·⟨q̄q⟩)

This is DER-QNG-041 (candidate), pending 3-agent synthesis
(tesla-mind + einstein-mind + savant-physics-reviewer). If synthesis
converges and `g` can be derived from v7 primitives (not fit), the
hypothesis becomes a committed pre-registration (QNG-GPU-019). If
synthesis rejects it, Gap 4 is reopened as primary open structural
problem with no viable path and the program redirects to NOTE-QNG-013
(Lorentz covariance / conservative limit).
