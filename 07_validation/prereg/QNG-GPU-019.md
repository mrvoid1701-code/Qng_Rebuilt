# QNG-GPU-019

Type: `prereg`
Status: `registered`
Author: `C.D Gabriel`
Date: `2026-04-18`
test_class: `yukawa_phi_mass_form`
hardware: `GPU`

## Title

V_couple = g · σ_g · (1 - cos phi) added to E_v7 — test whether the
pion-analog Yukawa FORM produces a Yukawa halo (Gate A), a self-consistent
phi screening length from halo and inter-ring force (Gate C), and an
L-converged mass ratio (Gate E). Pre-registered 5-point g-scan with
lowest-g-passing-all-gates decision rule (Savant's falsification
integrity contract).

## Purpose

After the quintuple falsification chain GPU-009..018 (capped by
DER-QNG-040 FAIL_H3_STRUCTURAL), the structural diagnosis is that the
IR halo is a phi Goldstone mode produced by the unbroken global U(1)
shift symmetry `phi → phi + c`. No σ_m-only modification can cure it.

DER-QNG-041 (`04_qng_pure/qng-yukawa-phi-mass-v1.md`) proposes the
minimal explicit breaking via a pion-analog coupling
`V_couple = g · σ_g · (1 - cos phi)`, with σ_g as carrier (condensate,
not soliton — per Tesla + Einstein consensus refined by Savant).

**The coupling FORM is the subject of the test. The value `g` is a
pre-registered EFT coupling (Gap 9), not a derived primitive.**

Three independent agents (tesla-mind, einstein-mind, savant-physics-reviewer)
were consulted. Tesla derived g=0.009 (breathing-mode match, dimensionally
suspect). Einstein derived g=0.22 (topological λ_φ=R_min match,
self-referential using emergent R_min as input). Savant rejected both as
rigorous derivations and required a log-spaced pre-committed scan with
the lowest-g-passing rule. This pre-reg adopts Savant's contract.

## Hypothesis

### H1 (PASS — DER-QNG-041 form confirmed)

At some g* in {0.009, 0.03, 0.08, 0.22, 0.6}, with g* the LOWEST value
satisfying ALL of Gate A, Gate C, Gate E:

- Halo fits exponential (Yukawa) rather than power-law
- λ_φ from halo = λ_F from inter-ring force (self-consistency)
- Mass ratio M(R=5)/M(R=4) L-converged inside [1.18, 1.45] with last-3-L
  spread < 3%

=> DER-QNG-041 form locked; g* recorded as current-best EFT value;
   Gap 9 open as "derive g* from v8 primitives"; baryon mass program
   re-advanced.

### H2 (PARTIAL — Gate A passes, Gate C or E fails at all g)

Form correct but incomplete. Suggests Yukawa screens halo locally but
doesn't deliver ring-ratio convergence. Likely augmentation needed
(e.g., Anderson-Higgs `|σ_m ∇phi|²` coupling). Re-register as GPU-019B
with DER-QNG-042 extension.

### H3 (FAIL — Gate A fails at all g)

Yukawa form structurally wrong. Advance directly to DER-QNG-042
(Anderson-Higgs covariant derivative) as Savant's proposed alternative.

### VOID

Stability breaks or ring fails to form at some g — document the g
threshold; restrict scan range; do not claim a verdict on scientific
gates.

## Commitments (Savant's 5-commitment contract)

1. **g-scan values committed PRE-RUN**: g ∈ {0.009, 0.03, 0.08, 0.22, 0.6}.
   Five log-spaced points bracketing Tesla's derivation (0.0089), Einstein's
   derivation (0.22), plus one above and one above-Einstein for slope.

2. **Lowest-g rule**: If any g passes all three gates, the lowest such g
   is the verdict g*. No cherry-picking g that best fits secondary
   metrics (e.g., choosing g=0.22 because it makes Gate E nicer even if
   g=0.03 already passes all three).

3. **All three gates required**: PASS requires Gate A AND Gate C AND
   Gate E at the chosen g. One-of-three is FAIL_PARTIAL.

4. **g labeled Gap 9**: Explicit statement in results that g is an EFT
   coupling, not derived from v7 primitives. GPU-019 tests the COUPLING
   FORM, not the VALUE of g.

5. **FAIL triggers DER-QNG-042**: If no g passes all gates, verdict is
   FAIL and next candidate is Anderson-Higgs `|σ_m ∇phi|²`. No post-hoc
   scan widening, no gate tolerance relaxation, no re-derivation of
   acceptance window.

## Parameters (committed pre-run)

**Substrate (v7, fixed at established values):**
- SIGMA_REF = 0.5
- ALPHA = 0.005 (σ_m drift)
- BETA = 0.35 (σ_m relational smoothing)
- BETA_PHI_MIN = 0.0005 (phi bulk)
- BETA_PHI_RING = 0.06 (phi in ring core — enables vortex)
- GAMMA_PHI = 0.10 (Channel F depletion strength)
- DELTA_CHI = 0.20 (Channel D cross-coupling)
- CHI_DECAY = 0.020 (v7 stability margin)
- CHI_REL = 0.35
- K_GM = 0.0 (gravity off for this test; only cares about phi sector)

**New coupling (DER-QNG-041):**
- g ∈ {0.009, 0.03, 0.08, 0.22, 0.6} (5-point log scan)

**Protocol:**
- PHASE1 = 300 (seed vortex, V_couple OFF)
- PHASE2 = 1500 (mature ring, V_couple ON at committed g)

## Gates (Savant rigor, tightened from Tesla/Einstein proposals)

### Gate A — halo exponential gap

**Measurement**: at L=80, R=5, T_P2=1500, compute
`D(r) = ⟨dis(r) · σ_m⟩` averaged over shells of radius r around the
ring axis, for r ∈ [3, 37] lu.

Fit two models:
- M1 (power-law): `D(r) = A · r^(-α)`
- M2 (Yukawa): `D(r) = A · exp(-r/λ_φ) / r`

**PASS** requires BOTH:
- AIC(M2) - AIC(M1) < -6 (strong preference for Yukawa)
- M1 fit α_effective > 3.5 (above non-diagnostic band [2.5, 3.0])

**FAIL** if α_effective ≤ 3.0 OR AIC prefers power-law.

**Rationale (Savant)**: raising the bar to α > 3.5 puts the PASS threshold
above the "possible lattice artifact of stronger decay" band. AIC test
requires genuine exponential, not steepened power.

### Gate C — Yukawa self-consistency

**Measurement**: 
- C1: extract λ_φ from Gate A Model 2 fit (single ring)
- C2: set up two rings (W+W-) separated by d ∈ {6, 8, 10, 12, 14, 16, 18, 20} at
  L=80; measure inter-ring force F(d) via σ_m asymmetry or Hamiltonian
  gradient; fit `F(d) = A · exp(-d/λ_F) / d²`

**PASS** requires: `|λ_φ - λ_F| / λ_φ < 0.20`.

**FAIL** if discrepancy > 20%. Phi would be quasi-Goldstone, not a
true Yukawa scalar.

**Rationale (Savant)**: halo and inter-ring force are algebraically
independent observations of the same lambda_phi if phi is a massive
scalar with standard propagator. Disagreement means phi is something
else.

### Gate E — mass ratio L-convergence

**Measurement**: at R=4 and R=5, L ∈ {60, 80, 100}, T_P2=1500, compute
M_ring(R, L) = N · σ_m_ref - Σ σ_m (with σ_m_ref = σ_g_ref = 0.5).

Compute:
- ratio(L) = M(R=5, L) / M(R=4, L)
- spread = |ratio(L=100) - ratio(L=60)| / ratio(L=80)

**PASS** requires BOTH:
- spread < 0.03 (3% L-convergence)
- ratio(L=100) ∈ [1.18, 1.45] (delta/nucleon SM ratio 1.313 ± ~10%)

**FAIL** if spread ≥ 0.03 OR ratio outside window.

**Rationale (Savant)**: this is the actual baryon identification test
that the whole five-test chain has failed. Gate A cures the phi halo but
doesn't force the mass ratio; Gate E tests whether fixing phi ALSO
fixes the mass observable.

## Decision rule

For each g in the scan, compute pass/fail on A, C, E. Tabulate:

| g | Gate A | Gate C | Gate E |
|---|---|---|---|
| 0.009 | ? | ? | ? |
| 0.03 | ? | ? | ? |
| 0.08 | ? | ? | ? |
| 0.22 | ? | ? | ? |
| 0.6 | ? | ? | ? |

Verdict rules:

- **PASS_H1** @ g*: g* = min{g : A AND C AND E all PASS}.
  Record g*, update DER-QNG-041 status to `locked`, begin Gap 9
  investigation (find v8 primitive from which g* follows).
- **FAIL_H2_PARTIAL**: some g passes A but none passes all three.
  Record which gate fails at the best-halo g. Re-register as GPU-019B
  with Anderson-Higgs augmentation.
- **FAIL_H3_STRUCTURAL**: no g passes Gate A.
  Direct advance to DER-QNG-042 (Anderson-Higgs).
- **VOID**: stability or ring-formation fails at some g values.
  Document the failure mode and restrict the legitimate scan range.

## Artifacts

- Script: `tests/gpu/qng_yukawa_phi_mass_gpu.py`
- Results: `07_validation/audits/qng-yukawa-phi-mass-v1/`
  - `report.json` — all g, all gate values
  - `run.log` — console output
  - `interpretation.md` — post-run gate-by-gate analysis
  - `summary.md` — one-page verdict

## Runtime estimate

- Stage A (halo): 4 L values × 5 g values = 20 runs at L=80, T_P2=1500.
  ~30-40 min on GPU.
- Stage C (force): 8 separations × 5 g values = 40 runs at L=80.
  ~60-80 min on GPU.
- Stage E (ratio): 2 R × 3 L × 5 g = 30 runs.
  ~40-60 min on GPU.

Total: ~2.5-3 hours on GPU. Acceptable for overnight run.

## References

- DER-QNG-041: `04_qng_pure/qng-yukawa-phi-mass-v1.md`
- Agent critiques:
  - `.claude/agent-memory/tesla-mind/critique-yukawa-phi-mass.md`
  - `.claude/agent-memory/einstein-mind/critique-phi-mass-yukawa.md`
  - `.claude/agent-memory/savant-physics-reviewer/der041-yukawa-critique.md`
- Predecessor failure (DER-QNG-040): `04_qng_pure/qng-sigma-m-potential-v1.md`
- Exhaustion note: `04_qng_pure/qng-mass-observable-exhaustion-v1.md`
