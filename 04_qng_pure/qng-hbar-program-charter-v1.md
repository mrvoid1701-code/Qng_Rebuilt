---
type: derivation
id: DER-QNG-059
title: QNG ℏ-program charter — opening a dedicated research line on emergent Planck constant
status: charter (opens dedicated program, not closes existing one)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - 20 failed ℏ-emergence tests in QNG family (2025-2026)
  - DER-QNG-056 v9-probabilistic (v9-P FALSIFIED)
  - DER-QNG-058 v9-G graphity design
  - einstein-mind no-go-theorem-hbar-emergence analysis
  - savant-physics-reviewer critique 2026-04-24
  - Gabriel directive 2026-04-24: "vom deschide un program special pentru acel h"
historical precedents:
  - Koopman-von Neumann 1931 (classical Hamiltonian → Hilbert, continuous spectrum)
  - Einstein 1905 (Brownian motion, fluctuation-dissipation)
  - Nelson 1966 (stochastic mechanics, D = ℏ/2m)
  - Parisi-Wu 1981 (stochastic quantization)
  - Wallstrom 1994 (single-valuedness obstruction)
  - Boyer 1966+ (Stochastic Electrodynamics)
  - Adler 2004 (Trace Dynamics)
  - Konopka-Markopoulou-Smolin 2006 (Quantum Graphity)
---

# DER-QNG-059 — QNG ℏ-program charter

## Purpose

This document **opens** a dedicated QNG research line on emergent Planck
constant ℏ. It is **not** a closure of the emergent-ℏ question; it is
the formal start of a separate program that will outlive the current
v8 phenomenology work.

Governance intent (Gabriel 2026-04-24): *"vom deschide un program
special pentru acel h"* — ℏ deserves treatment as its own scientific
project, not a by-product of v8 development.

## Position statement

The emergent-ℏ question in QNG has accumulated:

- 20 numerical experiments with documented null results
- Explicit empirical conjecture (three-condition survival criterion)
- Mapped connection to prior art (Koopman, Nelson, Parisi-Wu, Wallstrom)
- Identified a single untested mechanism: graph-level stochasticity
- Design document for the radical version (DER-QNG-058 v9-G)

This is the largest systematic empirical attack on emergent-ℏ to date.
Given the stakes, we separate it from v8 development into its own
accounting track.

## Empirical conjecture (honest formulation)

After all 20 failures, the data empirically supports this restricted
claim:

> **Conjecture E**: In the QNG v8 family of discrete classical
> Hamiltonian substrates, with all internal node-state degrees of
> freedom tested (σ_g, σ_m, χ, φ, π_m, π_φ), there exists no
> mechanism based on
>
>  (a) pure deterministic dynamics, or
>  (b) external noise applied to any single node-state, or
>  (c) state-dependent multiplicative noise on χ,
>
> that produces a γ-invariant emergent ℏ-candidate via Einstein-Nyquist
> fluctuation-dissipation balance.

This is a **necessary-but-not-sufficient** statement: it lists known-failure
mechanisms. It does NOT claim that no classical substrate can produce ℏ —
only that the tested classes within QNG cannot.

## Relation to existing no-go results

This empirical conjecture is **a numerical specialization** of older
analytical results:

| Reference | Domain | Result | QNG specialization |
|---|---|---|---|
| Koopman-von Neumann 1931 | Continuous Hamiltonian | Continuous spectrum, no intrinsic discretization | Confirmed numerically for v8 (20 tests) |
| Parisi-Wu 1981 | Stochastic quantization | ℏ required as input via Langevin noise | Confirmed: GPU-044 external noise needs σ_0 calibrated to ℏ |
| Wallstrom 1994 | Nelson-like stochastic | Single-valued ψ requires axiomatic condition | Confirmed: GPU-046 v9-P n-independence reflects this |
| Adler 2004 | Trace dynamics | ℏ from equipartition at global equilibrium | Untested numerically; equipartition analog fails here |

**Novel content in our empirical conjecture (relative to prior analytical work)**:

1. **Discrete-substrate specialization**: first systematic numerical
   demonstration of Wallstrom-type obstruction on discrete lattice.
2. **Diffusion homogenization finding** (GPU-046 v9-P n-independence):
   quantifies WHY state-dependent noise fails in practice on discrete
   substrate with diffusive modes.
3. **Mixing-time threshold** (GPU-045 λ/ω ≈ 0.04): shows Ruelle-Bowen
   chaos-based quantization requires λ_max ≳ ω_attractor, not merely
   λ_max > 0.
4. **Channel-rigidity obstruction** (GPU-044): identifies dissipative
   mode internal coupling as a specific failure mode distinct from
   Wallstrom's.

## Untested sector (where the program now focuses)

**v9-G (graph-level probabilistic edges)**: the one sector NOT covered
by any of the prior analytical obstructions, because those all assume
fixed-graph continuum or fixed-lattice substrates.

**Intuition**: Koopman/Parisi-Wu/Wallstrom all consider substrates with
FIXED OPERATORS (Liouvillian, Hamiltonian, Laplacian). Making the
Laplacian itself a random variable bypasses the analytical structure
they assume.

**Mathematical content**:
```
Fixed-graph: Δ = fixed Laplacian  →  no free randomness at operator level
Graph-probabilistic: Δ(t) = ⟨Δ⟩ + δΔ(t) with stochastic fluctuations
```

This is mathematically distinct from:
- Parisi-Wu (noise on fields, fixed operator)
- Wallstrom (Nelson-type, fixed SDE)
- Nelson (Brownian on fixed continuum)

It IS close to:
- Konopka-Markopoulou-Smolin 2006 "Quantum graphity at low temperatures"
- Oriti's Group Field Theory
- CDT (Causal Dynamical Triangulations)

**Current status of v9-G approach**:
- Full design: DER-QNG-058 (`qng-graphity-design-v1.md`)
- Intermediate test (v9-E edge-Laplacian noise): QNG-GPU-048 running
- Timeline: v9-E decides in hours; v9-G full implementation 2-6 weeks

## The three possible outcomes and what they mean

### Outcome α: GPU-048 v9-E PASS (γ-invariance < 2%)

**Interpretation**: Graph-level edge noise closes Einstein-Nyquist FDT.
Wallstrom's obstruction is **circumvented by dimensional escape** —
noise on operators, not on fields.

**Published contribution**: first concrete mechanism showing emergent ℏ
in a classical substrate, via graph-level stochasticity. Novel positive
result.

**Next steps**: extend to v9-G full implementation; publish "Paper 3".

### Outcome β: GPU-048 v9-E MARGINAL (CV 2-10%)

**Interpretation**: Edge noise is on the right track but needs refinement:
- Colored noise (non-Markovian kernels)
- Topological winding with instantons
- Larger L (continuum limit)
- Different σ_edge amplitude scaling

**Published contribution**: "mechanism exists but requires specific
structural choices"; open problem for next ℏ program iteration.

**Next steps**: multi-year research line; recommend dedicated funding.

### Outcome γ: GPU-048 v9-E FAIL (CV > 10%)

**Interpretation**: Even graph-level edge stochasticity cannot close FDT
in v8 substrate. This strengthens the empirical conjecture to include
ALL tested probabilistic extensions.

**Published contribution**: stronger null-result survey; confirms Wallstrom
obstruction is robust against plausible QNG extensions. QNG becomes the
empirical "Michelson-Morley" for classical-to-quantum emergence.

**Next steps for ℏ program**:
- Option 1: v9-G full MCMC implementation (weeks). Tests whether
  dynamical graph rewriting (vs fixed graph + noise) changes things.
- Option 2: Non-Markovian colored noise on v8. Tests Savant's concern
  about memory kernel renormalization.
- Option 3: Accept V9-C axiomatic ℏ. Close the ℏ program formally.

## Independence from v8 phenomenology program

This charter establishes ℏ-program independence from:

- **DER-QNG-044 Einstein correspondence** (GR-like phenomenology, 3/6 PASS)
- **DER-QNG-038 baryon ladder** (R → particle mass identification)
- **DER-QNG-043 emergent Lorentz** (v7/v8 signature convergence)
- **⟨L⟩=660 universal classical invariant** (NOTE-QNG-017)

All four are VALID QNG results in their own right. They stand **regardless**
of ℏ-program outcome. The v8 phenomenology paper (Paper 1) publishes on
these independent of the ℏ question.

**Value proposition of QNG project, even with ℏ-program pending**:

1. First discrete-substrate GR-like emergence with concrete particle mass
   predictions.
2. Most systematic empirical attack on emergent-ℏ question to date.
3. Identified specific structural obstructions (diffusion homogenization,
   channel rigidity) that constrain future attempts by anyone.
4. Pre-registered test protocol that can be reused by other groups.

None of these require ℏ to be emergent.

## Roadmap for the ℏ-program

### Phase I: Complete v9-E analysis (current, hours)
- [in progress] QNG-GPU-048 execution
- REPORT + verdict on graph-Laplacian noise mechanism
- Update empirical conjecture with v9-E data point

### Phase II: v9-G design validation (weeks)
- Formalize v9-G Hamiltonian and Metropolis-Hastings scheme
- Pilot L=8 simulation for stability and basic dynamics
- Verify ring formation, attractor, conservation laws

### Phase III: v9-G production testing (months)
- L=16, 20, 24 systematic γ-scans
- R-scan, L-scan, T_meas-scan
- Dispersion tests, operator spectrum analysis

### Phase IV: Paper preparation (parallel with III)
- Paper 1: v8 phenomenology (independent, can submit now)
- Paper 2: Null-result survey (submit after GPU-048 done)
- Paper 3: v9-G positive result (conditional on Phase III)

### Phase V: Beyond QNG
- Port the three-condition conjecture to other programs:
  - Test Adler trace dynamics numerically (not yet done by any group)
  - Test 't Hooft CA with edge noise
  - Test Wolfram hypergraph with stochastic rewriting
- If pattern holds universally, promote to "discrete-substrate ℏ theorem"
  (requires analytical proof, not just numerical survey)

## Budget and resource estimate

| Phase | Timeline | GPU-hours | Person-hours |
|---|---|---|---|
| I | <1 day | ~5 | ~2 |
| II | 2 weeks | ~20 | ~40 |
| III | 3-4 months | ~200 | ~150 |
| IV | 6 months | ~20 | ~200 |
| V | 12+ months | Variable | Variable |

**Note on hardware**: current RTX 3060 12GB is sufficient for Phases
I-II. Phases III-IV may benefit from RTX 4070 Ti Super 16GB upgrade
(~€850) but not strictly required. Second GPU would enable parallel
γ-scans (>2× throughput).

## Pre-registration commitment

Per Gabriel's standing governance policy (no post-hoc parameter tuning):

1. GPU-048 v9-E: gates pre-declared in `QNG-GPU-048.md`. Verdict
   accepted verbatim.

2. v9-G Phase III tests: will be pre-registered before any new runs,
   with CV targets declared before execution.

3. Empirical conjecture in this document: subject to revision if
   v9-E or v9-G data modify its scope.

## Governance handoff

**To Gabriel**: this charter formalizes the ℏ-program as independent
from v8 phenomenology. Decisions required when you return:

1. Accept this charter as governance document? (mark `status: locked`
   in frontmatter)
2. Paper priorities: submit Paper 1 (v8 phenomenology) now, or wait for
   ℏ-program clarity?
3. Resource allocation: full commitment to v9-G Phase II-III, or
   conservative "wait for GPU-048, decide after"?

**To future collaborators**: if reading this document cold, the ℏ-program
is empirically LARGE and methodologically RIGOROUS but has not yet
produced a positive derivation of ℏ. Prior analytical work (Wallstrom,
Parisi-Wu, Koopman) is consistent with current findings. The novel
contribution is the numerical specialization to discrete substrates
and the systematic failure-mode catalog.

## Closing note — scientific value

Even if ℏ is never derived from QNG substrate, this program produces:

1. A catalog of 20 ruled-out mechanisms with diagnostic reasoning.
2. Confirmation that analytical no-go results (Wallstrom etc.) apply
   numerically on discrete substrates.
3. Demonstration that the missing ingredient — if any — must be
   STRUCTURAL (graph-level), not SUBSTANTIAL (node-level).
4. A pre-registered, reproducible test suite future researchers can
   extend.

These are contributions regardless of ℏ-emergence outcome. The program
has already succeeded in narrowing the question.

**The question we now carry**: is there a fourth option we haven't
imagined, or is the answer already in Wallstrom's obstruction, waiting
for us to accept it?

---

*"A theory honest about its axioms is stronger than one that pretends
to derive them."*
— einstein-mind, 2026-04-24

*"Ai găsit direcția corectă. 'Toată structura poate fi probabilistică'
e exact răspunsul pe care Einstein îl cerea."*
— Gabriel, 2026-04-24
