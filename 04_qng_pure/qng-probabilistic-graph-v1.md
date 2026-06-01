---
type: derivation
id: DER-QNG-056
title: v9-probabilistic graph substrate — extending QNG with intrinsic stochasticity
status: v9-P variant FALSIFIED (GPU-046 preliminary); v9-G remains as design DER-QNG-058
author: C.D Gabriel
date: 2026-04-24
last_updated: 2026-04-24 (post GPU-046 v9-P Part A)
upstream:
  - QNG-GPU-043 (deterministic two-channel FDT FAILED)
  - QNG-GPU-044 (stochastic-vacuum layer FAILED)
  - QNG-GPU-045 (Lyapunov H_CHAOTIC marginal, λ=+0.00150/lu)
  - QNG-GPU-046-LONG (extended determinism FAILED)
  - QNG-GPU-046 v9-P (state-dependent noise FAILED preliminary, CV 56%)
  - einstein-mind gpu043-hbar-diagnosis
  - Gabriel hypothesis 2026-04-24: "toată structura poate fi probabilistică"
downstream:
  - DER-QNG-058 (v9-G graphity full design — surviving probabilistic path)
---

# PRELIMINARY UPDATE 2026-04-24 — v9-P FALSIFIED

**GPU-046 Part A (γ-scan at n=1) verdict**: V9P_FAIL.

| γ | ⟨χ²⟩_core | ⟨χ²⟩_vacuum | hbar_core |
|---|---|---|---|
| 0.010 | 6.80e-03 | 6.80e-03 | 3.93e-03 |
| 0.020 | 6.31e-03 | 6.31e-03 | 7.30e-03 |
| 0.040 | 5.53e-03 | 5.51e-03 | 1.28e-02 |

**CV(hbar across γ) = 55.9%** (threshold FAIL: 10%).

**Two unexpected findings**:

1. **⟨χ²⟩_core ≈ ⟨χ²⟩_vacuum (<0.3% diff)**: state-dependent noise
   `σ²(σ_m)` with n=1 did NOT produce spatially distinct χ² values.
   χ diffuses faster than local noise injection via CHI_REL Laplacian
   term in Channel D. The "state-local hbar" prediction FAILS.

2. **hbar_cand still γ-proportional** (ratio 1 : 1.86 : 3.26 ≈ 1 : γ/γ₀):
   State-dependent noise does NOT close Einstein-Nyquist. Mechanism
   same as GPU-044 failure — Channel D rigidity absorbs noise.

**Conclusion**: v9-P as formulated (multiplicative noise on χ with
fixed graph) is **NOT a viable path to emergent ℏ**. Surviving paths:

- **v9-G (full graphity)** — see `qng-graphity-design-v1.md` (DER-QNG-058):
  noise on graph edges, not on χ; bypasses diffusion homogenization
  because noise enters through the Laplacian OPERATOR, not through
  χ directly.
- **v9-E (intermediate edge-only noise)** — `QNG-GPU-048` preregistered:
  cheap test of edge-Laplacian noise on fixed graph. Faster alternative
  to v9-G full implementation; ~2 hours on GPU.
- **V9-C (axiomatic ℏ)** — DER-QNG-052 fallback if all probabilistic
  paths fail.

Final GPU-046 verdict pending Part B (n-scan) + Part C (control) —
~55 minutes remaining at time of this note.

---

# DER-QNG-056 — v9-probabilistic: extending QNG with intrinsic graph stochasticity

## Motivation

Sixteen consecutive hbar-emergence programs on deterministic classical
substrate have failed:

- GPU-042 Berry phase (V9-A: V9A-MARGINAL)
- CPU-099 graph winding topology (LOCAL_DEFECTS_ONLY)
- CPU-100 Verlinde entropic (VERLINDE-PARTIAL)
- CPU-101 Dirac constraint (DIRAC-NO-CONSTRAINT)
- CPU-092/093/094/095/096/097 edge-stochastic family (CLOSED — universal)
- CPU-082/082-v2 eta invariants (eps^4 / eps^2 trivial)
- CPU-083 action universality (R-DEPENDENT)
- H_DISPERSION, H2 Onsager (FALSIFIED)
- GPU-043 two-channel FDT (VACUUM_FDT_FAIL, CV=59%)
- GPU-044 stochastic-vacuum layer (VACUUM_FDT_FAIL, CV=42%+ stopped)

The diagnostic pattern is now structural: **deterministic substrate +
external noise cannot produce Einstein-Nyquist γ-invariance** because
dissipative modes (χ) are tightly coupled to deterministic channels
(A, D, G cross-terms), suppressing the noise-induced OU statistics
required for FDT closure.

Einstein-mind verdict (2026-04-24):
> "After 16 failures, this outcome must be seriously entertained, not
> dismissed: hbar may be axiomatic at the substrate boundary."

## Gabriel's hypothesis (2026-04-24)

> *"Cred ca miam dat seama de ceva, am facut teoria prea simpla. Nici macar
> nam pus intrebarea ce probabilitate are chi... chi e un regulator de
> informatie, unde-i mult da putin, unde-i putin da mult, dar cu ce
> probabilitate o face... din cauza spatiului peste tot sunt structuri
> ce se distrug se refac."*

And extending:

> *"Dar si conectivitatea trebuie sa aibe o probabilitate sa se intample,
> cam toata structura o putem face probabilistica."*

**Key insight**: the substrate itself should be probabilistic — not just
χ values, not just edge creation/destruction, but the **full architecture**
(states + connectivity + update transitions).

## Formal extension — v9-P (probabilistic fields) and v9-G (graphity)

### v9-P (minimal variant): probabilistic state fields on fixed graph

Replace deterministic real values with probability distributions:

```
v8:  chi_i(t) ∈ ℝ        (single real number per node)
v9-P: chi_i(t) ~ P_i(χ)   (distribution per node)
```

Distribution parameters depend on local structure:
```
P_i(χ) = N(μ_i(state_local), σ²_i(state_local))
```

where `σ²_i = f(σ_m_i, σ_m_neighbors)` — noise amplitude state-dependent.

**Specific proposal**: `σ²(σ_m) = σ²_0 · (1 - σ_m/σ_m_ref)` — noise is
maximal where matter density is lowest (vacuum), minimal inside dense
structures (rings). This matches Gabriel's "unde-i mult da putin,
unde-i putin da mult" — where structure is dense, noise is suppressed.

### v9-G (radical variant): probabilistic graph itself

Graph edges E_ij are themselves random variables:
```
P(edge_ij exists) = f(state_i, state_j, distance_ij)
```

At each Markov step, the graph is re-sampled; states update conditionally
on the current graph configuration. This is **quantum graphity** à la
Konopka-Markopoulou-Smolin (2006).

**State space**:
```
|Ψ_v9G⟩ = Σ_G P(G) · ⊗_i ρ_i(state_i | G)
```

which has the formal structure of a quantum Fock state — superposition
over graph configurations.

## Why this should close Einstein-Nyquist

Both variants introduce **intrinsic** stochasticity:

- v9-P: multiplicative noise Langevin on χ with state-dependent amplitude
- v9-G: edge fluctuations create a "graph heat bath" that drives all fields

In either case, the driving source on χ becomes **broadband** (not narrow
at ω_orb as in v8). Einstein-Nyquist cancellation requires such broadband
driving. Formally:

```
v9-P:  dχ = [deterministic] + σ(state)·dW(t)     (Langevin)
        -> <χ²> ∝ σ²/γ  with σ state-dependent
        -> hbar_cand_i = σ²(state_i)·dt/ω        (state-local hbar)

v9-G:  dG = [graph rewriting]                     (Markov chain)
        -> effective noise on all node fields
        -> hbar emerges from graph ensemble temperature T_graph
```

**Prediction**: ℏ is no longer universal — it is **local, state-dependent**:
```
ℏ_QNG(x) = ℏ_base · g(σ_m(x))
```

where `g` is a modulation function. In laboratory conditions (σ_m ≈ σ_m_ref),
`g ≈ 1` and `ℏ_QNG ≈ ℏ_SI`. In extreme conditions (black hole interior,
early universe, ring core), `g` deviates.

## Analytical derivation of σ(σ_m) — self-consistency argument

We derive the state-dependent noise amplitude from requiring
**FDT closure at each node locally**.

### Langevin equation for χ at node i

Starting from v8 Channel D deterministic drive with added multiplicative noise:
```
dχ_i/dt = -γ·χ_i + J_i(state) + σ(σ_m_i)·ξ_i(t)
```

where:
- γ = CHI_DECAY (Channel D dissipation rate, nominal 0.02)
- J_i = CHI_REL·(σ_g_bar - σ_g) + DELTA_CHI·(σ_ref - σ_g) (deterministic)
- ξ_i(t) = white Gaussian noise with `<ξ_i(t)ξ_j(t')> = δ_ij·δ(t-t')`
- σ(σ_m_i) = state-dependent noise amplitude (TO BE DERIVED)

### Stationary distribution (Ornstein-Uhlenbeck)

Assuming J_i fluctuates on timescales slower than 1/γ, the stationary
distribution of χ_i is Gaussian:
```
P_stat(χ_i) = exp[-(χ_i - χ_i^(eq))² / (2·<χ_i²>)]
```

with equilibrium mean:
```
χ_i^(eq) = J_i / γ
```

and equilibrium variance (Einstein-Nyquist form):
```
<χ_i²>_eq = σ²(σ_m_i) / (2·γ)
```

### FDT closure requirement

Einstein-Nyquist action quantum at orbital frequency ω_orb:
```
ℏ_cand,i = 2·γ·<χ_i²> / ω_orb = σ²(σ_m_i) / ω_orb
```

This is **γ-INVARIANT by construction** — the γ cancels exactly, regardless
of its value. Einstein-Nyquist cancellation closes for ANY σ(σ_m_i) > 0.

### Functional form from self-consistency

The specific form of σ(σ_m) must satisfy:

**Constraint C1** (vacuum limit): as σ_m → σ_m_ref (no matter deficit),
ℏ_cand should approach a universal base value ℏ_base:
```
σ²(σ_m_ref) = ℏ_base · ω_orb
```

**Constraint C2** (dense structure limit): as σ_m → 0 (maximum matter
deficit, dense ring core), noise should be suppressed (matter "stiffens"
the substrate):
```
σ²(0) < σ²(σ_m_ref)
```

**Constraint C3** (smoothness): σ²(σ_m) should be continuous and
monotonically increasing in σ_m.

**Simplest form satisfying C1-C3**:
```
σ²(σ_m) = σ²_0 · (σ_m / σ_m_ref)^n    for n > 0
```

or **Gaussian**:
```
σ²(σ_m) = σ²_0 · (1 - exp[-(σ_m/σ_m_c)²])
```

with `σ²_0 = ℏ_base · ω_orb` (calibration) and `σ_m_c` a structural scale.

### Honest limitation

**This is CALIBRATION, not derivation.** σ²_0 is set to match ℏ_base.

For TRUE derivation, σ²_0 must emerge from substrate structure alone,
independent of ℏ. This requires v9-G, where σ_0 is determined by:
- Graph ensemble temperature T_graph
- Edge fluctuation rate
- Substrate connectivity density

In v9-G:
```
σ²_0 ~ k_B · T_graph · (edge_density)
```

where k_B·T_graph is the "temperature" of graph fluctuations. This is
ANALOGOUS to thermal fluctuations in statistical mechanics — not
identical, but structurally similar.

**The DEEPER question**: what sets T_graph itself? Three possibilities:
1. **Axiomatic**: T_graph postulated (same status as ℏ in standard QM)
2. **Self-consistent**: T_graph determined by ensemble convergence
   (requires detailed graph-Markov-chain analysis)
3. **Emergent from deeper theory**: T_graph from pre-graph ontology
   (Wheeler "it from bit" style derivation)

Current status: we have NO derivation path from (3). (2) is plausible
but unproven. (1) is the honest admission.

## Testable distinction between v9-P and v9-G

- **v9-P predicts**: ℏ_local(x) = σ²(σ_m_x)·dt/ω_orb — varies with local
  matter density.
- **v9-G predicts**: ℏ_local(x) = (same form) + corrections of order
  T_graph to c, G, α.

Experiment: measure ℏ at lab (σ_m ≈ σ_m_ref) vs deep space (σ_m_vacuum).
v9-P predicts <5% deviation; v9-G predicts additional c, G variation
that can be crosschecked against gravitational-wave timing.

## Critical check against Einstein's concern

Einstein-mind verdict: "σ_vac IS ℏ, relabeled — accommodates ≠ predicts."

**v9-P answer**: partially valid — σ²_0 is an input calibration.
Does NOT satisfy Einstein's higher bar.

**v9-G answer**: potentially answers Einstein's challenge — σ²_0 emerges
from T_graph, which itself could be derived from substrate consistency.
Requires rigorous development; currently open.

**Practical path**: v9-P as stepping stone (demonstrate mechanism works),
v9-G as ontological goal (derive ℏ from substrate).

## Preservation of v8 results

Both v9-P and v9-G reduce to v8 in the "classical limit":

```
v9-P:  σ(state) → 0  ⇒  deterministic v8 with chi as real field
v9-G:  T_graph → 0   ⇒  classical graph frozen to minimum energy configuration
```

All 91 pre-registered tests from v7/v8 remain valid in this limit.

**Specifically preserved**:
- DER-QNG-044 Einstein correspondence (KG, Shapiro, tensorial coupling)
- DER-QNG-038 baryon mass ladder (ensemble expectation values)
- DER-QNG-043 emergent Lorentz
- ⟨L⟩=660 universal invariant (as graph ensemble mean)
- GRAV-C1, GRAV-C2 Newtonian potential conventions

## New predictions unique to v9

### v9-P (state-dependent local ℏ)

1. **Ring-core ℏ deviation**: inside dense ring regions (σ_m local deviation
   ~0.3 from ref), ℏ should differ from vacuum ℏ by ~10-30%. Testable in
   extremum cosmology: early universe primordial fluctuations.

2. **Black-hole interior** (extreme σ_m deficit): ℏ diverges or collapses?
   QNG prediction distinguishable from standard QM.

3. **Casimir-like effects modified**: vacuum zero-point energy depends on
   local matter density. Predicts corrections to Casimir force in crystalline
   materials.

### v9-G (graphity)

1. **Emergent Planck length** from graph connectivity: ℓ_P ~ (edge density)^(-1/d)
   where d is effective spatial dimension.

2. **Topological phase transition** at critical temperature: graph "melts"
   from ordered (spacetime-like) to disordered (pre-geometric) — potentially
   observable at black hole horizons.

3. **Discrete spectrum of spacetime intervals** at Planck scale: not
   continuum but discrete distribution P(Δs).

## Experimental roadmap

**Stage 1 — v9-P formalization** (analytical, 1-2 weeks):
- Derive state-dependent σ(σ_m) from self-consistency requirement
- Verify Einstein-Nyquist closure analytically for multiplicative noise
- Compute predicted ℏ_local(σ_m) curve

**Stage 2 — v9-P numerical** (GPU-046, ~1 week):
- Implement multiplicative noise Langevin for χ
- γ-scan at R=4: hbar_cand should be γ-invariant per local σ_m
- R-scan: hbar_cand at ring core vs vacuum — distinct values predicted

**Stage 3 — v9-G design** (theory, 1 month):
- Define Markov transitions for edge rewriting
- Compute graph partition function and ensemble ℏ
- Connect to Konopka-Markopoulou-Smolin graphity partition functions

**Stage 4 — v9-G numerical** (GPU-047, ~2-3 weeks implementation + 1 week
compute):
- Metropolis-Hastings sampling over graph configurations
- Verify ℏ emerges from ensemble temperature T_graph
- Compare with quantum graphity analytical predictions

## Relation to established physics

| Program | Approach | Result |
|---|---|---|
| Stochastic Electrodynamics (Boyer 1966) | Classical EM + vacuum noise | ℏ accommodated, not derived |
| Nelson stochastic mechanics (1966) | Brownian motion on vacuum field | Schrödinger recovered, ℏ input |
| Trace dynamics (Adler 2004) | Matrix-valued classical fields | hbar from equipartition, no numeric demo |
| 't Hooft CA (2005+) | Discrete deterministic cells | Conceptual only, no concrete mechanism |
| Quantum Graphity (Smolin et al. 2006) | Probabilistic graph thermodynamics | Conceptual, no baryon mass predictions |
| Causal Dynamical Triangulations | Random simulplicial complex | GR emergence verified, QM partial |
| Wolfram hypergraph (2020) | Deterministic rewriting rules | Speculative, few concrete predictions |
| **QNG v8** (2026) | Discrete deterministic substrate | GR-like 3/6 PASS; hbar FAILED 16x |
| **QNG v9-P/v9-G** (proposed) | Probabilistic QNG extension | Untested — combines SED structure + graphity + baryon predictions |

**Unique contribution of QNG v9**:
- Concrete numerical demonstrator (existing codebase)
- Baryon mass predictions preserved (DER-QNG-038)
- Einstein correspondence preserved (DER-QNG-044)
- State-dependent ℏ makes NEW, FALSIFIABLE predictions

## Falsifiability

v9-P makes experimental predictions distinguishable from standard QM:

1. **ℏ_lab** measured at σ_m ≈ σ_m_ref should match CODATA ℏ_SI within
   experimental error
2. **ℏ_vacuum(deep-space)** may differ by factor g_vacuum ≠ 1 — testable
   via precision interferometry at extreme vacuum
3. **Casimir force anomaly** in materials with unusual σ_m density

If none of these match prediction → v9-P falsified.

## Dependencies (reverse trace)

This derivation depends on NO prior QNG result being CHANGED. It
adds structure on top of v8 without modifying any established claim.

- All CLAIM-QNG-### remain valid in low-T limit
- All DER-QNG-### 001-055 remain valid
- No retractions required

Therefore, v9-P/v9-G is a PURE EXTENSION, not a replacement.

## Implementation priority

**High priority** (do first):
1. GPU-045 Lyapunov result — tells us if ergodic mixing is available
2. Formalize σ(σ_m) functional form for v9-P
3. Write `tests/gpu/qng_gpu046_v9p_langevin.py` — multiplicative-noise probe

**Medium priority** (do after GPU-046 proof-of-concept):
4. v9-G Markov chain design
5. Graph rewriting kernel
6. Ensemble partition function estimator

**Low priority** (distant):
7. Black-hole interior v9 predictions
8. Casimir anomaly prediction paper
9. Peer review submission strategy

## Open questions

1. **What determines σ(σ_m) form?** First-principles derivation or
   phenomenological fit to experimental ℏ_lab? Prefer first-principles.

2. **Can v9-G avoid infinite regress?** The graph thermal bath has a
   temperature — where does ITS temperature come from? (Possible answer:
   self-consistency from ensemble sampling converges to fixed-point T*.)

3. **Is v9-P a true extension or just calibration?** If σ_0 is free
   parameter, then v9-P "calibrates" ℏ but doesn't derive it.
   Resolution: require σ_0 to emerge from v9-G ensemble consistency.

4. **How does Born rule emerge?** ⟨χ²⟩ = FDT expectation ≠ |ψ|² in
   general. Need additional mechanism (possibly Ruelle-Bowen ergodicity
   on the probabilistic attractor).

## Status

Draft — awaiting:
- GPU-045 Lyapunov result to decide Hypothesis B viability
- Analytical derivation of σ(σ_m) functional form
- Design of GPU-046 for v9-P numerical proof-of-concept

If GPU-045 confirms λ_max > 0 → proceed with v9-P (simpler)
If GPU-045 confirms λ_max ≈ 0 → v9-P may still work but v9-G becomes
essential (can't rely on intrinsic chaos for mixing)
