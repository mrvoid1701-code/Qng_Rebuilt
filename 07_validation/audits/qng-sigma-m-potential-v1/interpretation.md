# QNG-GPU-018 Interpretation — V(sigma_m) Falsified

Type: `note`
ID: `INTERP-QNG-018`
Status: `final`
Author: `C.D Gabriel`
Date: `2026-04-18`

## Verdict: FAIL_H3_STRUCTURAL

Pre-registered gates:

| Gate | Metric | Predicted | Observed | Verdict |
|---|---|---|---|---|
| A | α(L=80,R=5) | ≥ 3.5 (or ≤ 3.0 clear FAIL) | **2.49** (spread 0.17, L=40→100) | **FAIL clear** |
| B | FWHM(R) R-indep, within 30% of 4.52 | 4.52±0.15 | **1.00** (R∈{4,5,6,7}, spread 0.0) | **FAIL** (R-indep, wrong magnitude) |
| C | M(R=5)/M(R=4) L-converged in [1.25, 1.40] | 1.32±0.04 | **1.048** (1.070→1.031 at L=60→120) | **FAIL** (diverging downward) |
| D | r_eff linearized damping | 0.100 | **0.1055** (R²=1.000) | **PASS** (5.5% discrete correction) |

## Physical interpretation

### Gate A: V(σ_m) does NOT cure the IR halo

Adding a Ginzburg-Landau potential to σ_m leaves the power-law halo
`dis(r)·σ_m ~ r^(-α)` **unchanged at α ≈ 2.49** — identical to the
v5+Channel H baseline. This is the cleanest structural falsification
in the GPU-009..018 chain.

**Root cause: the halo is a phi Goldstone, not a σ_m mode.**

- `disorder = ⟨sin²(Δφ/2)⟩` — a phi-field observable
- V(σ_m) couples to σ_m only; commutes with the global U(1) shift
  `phi → phi + c`
- By Goldstone's theorem, a massless mode persists as long as the shift
  symmetry is unbroken
- V(σ_m) cannot break this symmetry, therefore cannot cure the halo

**Implication:** every observable on v5+Channel H that is built from
`disorder(phi)` inherits the IR pathology (confirmed: GPU-009..017 all
FAIL; GPU-018 confirms the mechanism structurally).

### Gate B: V(σ_m) over-suppresses σ_m depletion

The potential pulls σ_m → σ_ref strongly, restoring it to bulk value
within a single lattice cell of the ring core. FWHM collapses to 1.00
(R-independent: that part is geometric — a one-cell hole).

Predicted healing length ξ = sqrt(β_m/(2λσ_ref²)) = 1.92 lu is the
**linearized** prediction (small-field around the vacuum). At the
nonlinear core where σ_m → 0, the potential restoring force scales as
`λ·σ_ref²·σ_m` (derivative near zero), which is 0.0475 — much larger
than the available gradient energy from β·(sigma_mb - σ_m).

**Implication:** V(σ_m) with saturation-predicted λ=0.19 destroys the
ring-depletion profile. Even if Gate A had passed, the mass observable
would be degenerate (no R-dependent ring core).

### Gate C: catastrophic ratio collapse

The mass ratio M(R=5)/M(R=4) **decreases monotonically** with L:

| L | M(R=4) | M(R=5) | ratio |
|---|---|---|---|
| 60 | 388.18 | 415.31 | 1.0699 |
| 80 | 620.66 | 652.14 | 1.0507 |
| 100 | 912.22 | 947.81 | 1.0390 |
| 120 | 1263.04 | 1302.62 | 1.0313 |

Extrapolating a simple power-law fit: ratio → ~1.00 at large L.
The mass observable becomes **R-independent** in the thermodynamic
limit — the opposite of a useful mass identification.

**Interpretation:** the linear scaling of M_ring with L³ (box volume)
dominates both numerator and denominator because V(σ_m) restores σ_m
to σ_ref everywhere except a one-cell core; the R-dependent contribution
is negligible relative to the bulk term.

### Gate D PASS: the mathematics of V(σ_m) is correct

The linearized damping rate r_eff = α_m + 2λσ_ref² = 0.10 is measured
at 0.1055 (5.5% error). This is the expected discrete-lattice correction
from `log(1 - r) ≈ -r - r²/2 = -0.1054`. The potential is implemented
correctly; it just is not the right potential.

## The five-test chain (updated)

| Test | Observable | Hypothesis | Verdict |
|---|---|---|---|
| GPU-009..014 | M_ring on v5+H | depletion integral | FAIL (geometric 5/4) |
| GPU-015 | H_v7 Hamiltonian | energy conservation | FAIL (same IR pathology) |
| GPU-016 | e_B Bogomolny | soliton rest-energy | FAIL_GEOMETRIC |
| GPU-017 | Hopfion Q=1 | topological confinement | FAIL (α=1.89, worse) |
| **GPU-018** | **V(σ_m) at λ=0.19** | **σ_m confinement via GL potential** | **FAIL_H3_STRUCTURAL** |

**Universal failure mode confirmed:** the phi Goldstone halo is
structural. No σ_m-sector modification can cure it. Any future fix
must directly break the global U(1) shift symmetry of phi.

## What is forbidden going forward

- Further ad-hoc tuning of λ downward (e.g. λ=0.01) to preserve core:
  this falls into the Gap-9 (Yukawa EFT) regime where λ is fit, not
  derived. Savant's prediction was that this would happen; it is
  now the actual outcome if we keep V(σ_m).
- Re-running GPU-018 with different gate widths: gates were
  pre-registered with explicit FAIL_CLEAR thresholds; moving the
  goalposts violates the falsification contract.
- Inventing a new single-field potential for σ_m alone: the Goldstone
  theorem forbids it by construction.

## What is structurally motivated

The halo is a phi mode. The only way to give phi a mass is to break
the global U(1) shift symmetry `phi → phi + c`. Two candidates:

### Candidate 1 — σ_m·phi Yukawa (pion analog)

Add `V_couple = g·σ_m·(1 - cos phi)` to E_v7. This breaks the shift
symmetry explicitly (the `cos phi` term is not invariant under
`phi → phi + c`). In the bulk where σ_m = σ_ref:

- Expand `1 - cos phi ≈ phi²/2` for small phi
- Effective phi mass: m²_phi ≈ g · σ_ref

In the ring core where σ_m → 0: m²_phi → 0, vortex can still form.

**Pion analog (GMOR):** m_π² ∝ m_q · ⟨q̄q⟩ — the phi mass is generated
by a condensate (σ_m) coupling to an explicit symmetry breaking (g).
This is the standard path in QCD; well-motivated structurally.

### Candidate 2 — background σ_ref gradient (Higgs analog)

Add a density-dependent phi mass via `|∇σ_m|²` coupling. Less natural;
would require lattice data to motivate.

## Closure of DER-QNG-040

DER-QNG-040 (V(σ_m) via marginal-stability saturation) is **falsified
at structural level**. The derivation's internal logic is consistent
(Gate D PASS), but the physical assumption — that σ_m confinement
would cure the halo — is wrong. The halo is not a σ_m observable; it
is a phi observable.

**Savant's critique was correct**: saturation of the marginal-stability
inequality is a *convention*, not a *derivation*. Einstein's route (a)
gives a candidate λ, not the unique physical λ. The committed test
showed that the candidate value produces a physically wrong result.

**This does NOT invalidate DER-QNG-034** (marginal-stability for σ_g).
σ_g is the gravitational sigma coupled to chi; it has a physically
motivated energetic saturation via the chi kinetic term T_g. σ_m has
no such kinetic term (overdamped in v7), and Einstein's routine
extension was based on an analogy that does not hold.

## Next step

Formalize Candidate 1 (σ_m·phi Yukawa) as DER-QNG-041 if agent
synthesis (tesla-mind + einstein-mind + savant-physics-reviewer) converges
on this direction. Pre-register as QNG-GPU-019 with `g` committed
BEFORE running — no post-hoc fitting.

If agents do NOT converge, reopen Gap 4 as "primary open structural
problem" with no viable path identified, and redirect the program
to the Lorentz-covariance question (the Hamiltonian conservative
limit, NOTE-QNG-013).
