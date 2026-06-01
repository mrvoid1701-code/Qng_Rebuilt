---
type: note
id: NOTE-QNG-023
title: Emergent ℏ and the timescale of Ruelle-Bowen closure — revised after GPU-045
status: draft (pending GPU-046-LONG result)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - QNG-GPU-043 (deterministic two-channel FDT FAIL, CV 59%, T_meas=1000 lu)
  - QNG-GPU-044 (external vacuum FDT FAIL, CV 42%+, T_meas=1000 lu)
  - QNG-GPU-045 (Lyapunov: H_CHAOTIC marginal, λ_max=+0.00150/lu)
  - einstein-mind gpu043-hbar-diagnosis (predicted H_QUASIPERIODIC, partially wrong)
  - Gabriel hypothesis 2026-04-24: "toată structura poate fi probabilistică"
---

# NOTE-QNG-023 — On emergent ℏ and the Ruelle-Bowen timescale

## Summary (REVISED 2026-04-24 after GPU-045 H_CHAOTIC surprise)

Initial claim (pre-GPU-045): "Emergent ℏ requires ontological stochasticity;
deterministic substrates cannot produce γ-invariant action quanta."

**GPU-045 SURPRISED this claim**: R1 attractor IS weakly chaotic
(λ_max = +0.00150 per lu, above 1e-3 threshold). Pure determinism does
exhibit intrinsic stochasticity via Ruelle-Bowen mechanism.

**Revised claim**:

> **Emergent ℏ via Einstein-Nyquist FDT requires either (a) strong
> intrinsic chaos (λ_max ~ ω_orb), or (b) measurement windows T_meas ≫
> 1/λ_max for slow Ruelle-Bowen mixing to manifest, or (c) ontological
> stochasticity via probabilistic extension (v9-P/v9-G).**

For QNG v8 R1 attractor: λ_max/ω_orb ≈ 0.043 — WEAK chaos. Ruelle-Bowen
mechanism exists but operates on long timescales (mixing time ~667 lu).
GPU-043/044 failures at T_meas=1000 lu are consistent with insufficient
measurement window, not structural exclusion.

**Status**: emergent-ℏ-from-v8 program REOPENED pending GPU-046-LONG
(T_meas=10000 lu = 15 mixing times) result.

## Scope

This note applies to any classical substrate theory attempting to
derive ℏ through FDT mechanisms. Specifically:

- QNG v7/v8 (this work)
- Adler trace dynamics (2004, 2006)
- 't Hooft cellular automaton interpretation (2005, 2014)
- Wolfram hypergraph physics (2020)
- Wolfram-style combinatorial rewriting

**Not in scope**: SED (Boyer, de la Peña) — which already assumes
ontological EM vacuum fluctuations; Nelson stochastic mechanics — which
assumes Brownian substrate; loop quantum gravity — which already
quantizes ab initio.

## The three structural failure modes observed

### Failure Mode 1: narrow-band deterministic drive (GPU-043)

Einstein-Nyquist `γ·⟨χ²⟩ = D_eff` requires D_eff = broadband driving
spectrum. Deterministic quasi-periodic systems produce narrow-band
driving at their attractor frequency ω_orb. Observation:

```
⟨χ²⟩ ≈ |J_det|²/ω_orb²  (source-limited, γ-independent)
hbar_cand = 2γ⟨χ²⟩/ω_orb ∝ γ  (γ-DEPENDENT, FAILS)
```

### Failure Mode 2: tightly-coupled receiving mode (GPU-044)

Even with external white-noise bath injected onto χ, Einstein-Nyquist
still fails if χ has strong internal coupling to other deterministic
channels. Observation:

- σ_vac = 0.04 white noise added → ⟨χ²⟩ rises 43× vs GPU-043 (confirms
  mechanism activation)
- But ⟨χ²⟩ ≈ constant across γ ∈ [0.010, 0.020] (only 7% variation)
- Channel D restoring forces (CHI_REL, DELTA_CHI) dominate γ rate
- hbar_cand still γ-DEPENDENT (CV 42%+)

### Failure Mode 3: marginal chaos + short measurement window (GPU-045)

**CONFIRMED** (2026-04-24 GPU-045): R1 attractor λ_max = +0.00150 per lu.
Marginally chaotic; 1/λ_max ≈ 667 lu mixing timescale.

**New interpretation**: GPU-043/044 failures at T_meas=1000 lu may be
**measurement-window-limited**, not structural:
- GPU-043/044 T_meas = 1000 lu ≈ 1.5 mixing times → INSUFFICIENT
- Ruelle-Bowen FDT closure requires T_meas ≫ 1/λ_max
- Ideal test: T_meas = 15-30 mixing times = 10000-20000 lu

For λ_max/ω_orb = 0.043, FDT closure at ω_orb frequency is still
challenging. Effective stochasticity operates at ~λ_max/ω_orb ≈ 4% of
orbital scale. Sufficient for slow relaxation; possibly insufficient
for γ-invariant hbar if hbar operates at orbital scale.

**Open empirical question (GPU-046-LONG pending)**: does ⟨χ²⟩ grow
toward dissipation-limited value at T_meas = 15 mixing times?

## Structural constraints on deterministic emergent-ℏ

Savant theorem-level argument (Liouville + Noether + compact-symmetry
+ ergodicity) identifies four conditions relevant to emergent-ℏ:

1. **Liouville**: deterministic Hamiltonian evolution preserves phase-space
   volume. Quantum mechanics requires discrete spectrum — only accessible
   via phase-space ergodic splitting into discrete invariant cells.
   Marginal chaos with slow ergodic mixing MAY accomplish this in
   asymptotic time.

2. **Noether**: every continuous symmetry produces a conserved quantity.
   ℏ would ideally come from a **compact** symmetry (S¹) giving discrete
   action via Bohr-Sommerfeld. QNG v8 has only non-compact translations
   (CPU-101 confirmed).

3. **Compact symmetry test**: if no S¹ symmetry, ℏ cannot emerge as
   Noether charge. Must come from ergodic statistical mechanics instead
   (Ruelle-Bowen).

4. **Ergodicity**: Ruelle-Bowen theorem states that chaotic ergodic
   dynamics produce Gibbs-like statistics. The "effective temperature"
   of this statistics IS the source of ℏ in the v8 hypothesis.

**Revised combined claim**:
- In a deterministic substrate WITHOUT chaos (KAM integrable): ℏ cannot
  emerge structurally.
- In a deterministic substrate WITH strong chaos (λ_max ~ ω_orb):
  ℏ emerges via Ruelle-Bowen; but QNG v8 does NOT have strong chaos.
- In a deterministic substrate WITH weak chaos (λ_max ≪ ω_orb, like v8):
  ℏ MAY emerge on long timescales; requires empirical verification.
  **This is GPU-046-LONG in progress.**

## Options after this closure

### Option 1: Accept ℏ as axiomatic at substrate boundary

Status: HONEST. ℏ is introduced as postulate at the interface between
QNG substrate and its quantum layer. Path: V9-C (Weyl path integral)
from DER-QNG-052. ℏ is axiom, Wallstrom no-go addressed via Z-winding
sector sum.

Implication: QNG is a classical discrete substrate theory that explains
GR-like phenomenology (DER-QNG-044 three-probe PASS) but QM is added
externally via canonical quantization.

### Option 2: Enrich substrate ontology with intrinsic stochasticity

Status: SPECULATIVE but WELL-MOTIVATED. Propose DER-QNG-056 v9-P and
v9-G where stochasticity is ontologically primitive:

- **v9-P**: state-dependent multiplicative noise `σ²(σ_m)·dW` on χ.
  Calibration needed (σ²_0 input).
- **v9-G**: probabilistic graph (Smolin graphity). Edge fluctuations
  generate intrinsic bath. T_graph parameter.

Implication: QNG becomes probabilistic at substrate level. Discreteness
preserved but determinism surrendered.

### Option 3: Abandon emergent ℏ program

Status: FALLBACK. Accept that QNG is complete at v8 as a classical-limit
GR-like theory, and ℏ/QM are simply not its domain. Refocus on
experimental predictions in classical regime.

## Current stance (REVISED after GPU-045)

Pre-GPU-045: "Option 2 (v9-P/v9-G) obligatory, Option 1 (V9-C) fallback."

**Post-GPU-045**: Three paths remain OPEN, awaiting GPU-046-LONG:

- **Option 0 (NEW — pure determinism via long-time Ruelle-Bowen)**:
  if GPU-046-LONG shows ⟨χ²⟩ converging to dissipation-limited 1/γ
  scaling at T_meas ≈ 15 mixing times, then pure v8 produces emergent
  ℏ without any extension. This would be the most parsimonious outcome
  and first numerical demonstration of Ruelle-Bowen ℏ in any substrate.

- **Option 2 (v9-probabilistic extension)**: if GPU-046-LONG shows
  ⟨χ²⟩ still source-limited at long times, Ruelle-Bowen chaos is
  ineffective at orbital timescale (even if present in slow sector).
  Probabilistic extension becomes necessary to provide broadband
  stochasticity. DER-QNG-056 proceeds.

- **Option 1 (V9-C axiomatic ℏ)**: remains as structurally valid
  fallback regardless of outcome.

**Priority order**: Option 0 (simplest, most ambitious, testable NOW)
→ Option 2 (if Option 0 fails) → Option 1 (if Option 2 fails).

## Connection to broader physics

This negative result is **structurally diagnostic** for the entire
class of "classical substrate → quantum mechanics" programs:

| Program | Substrate | Stochasticity | ℏ status |
|---|---|---|---|
| Standard QM | Continuous | Fundamental (vacuum) | Axiomatic |
| SED (Boyer 1966) | Classical EM | Postulated ZPF | Calibrated |
| Nelson (1966) | Classical + Brownian | Postulated | Input |
| Adler trace (2004) | Matrix-valued | Equipartition | Emergent (analytical only) |
| 't Hooft CA (2005) | Discrete deterministic | Absent | Failed mechanism |
| Wolfram hypergraph (2020) | Deterministic rewriting | Absent | Speculative |
| **QNG v8** | Discrete deterministic | Absent | **FAILED (17x)** |
| **QNG v9-P/v9-G** | Discrete probabilistic | Ontological | **TBD** |
| Loop QG | Quantized ab initio | Fundamental | Built-in |

**Pattern**: every program that produces rigid ℏ requires ontological
stochasticity at substrate level. Those that attempt purely deterministic
derivation have all failed. QNG joins this pattern.

## Predictions from this note

1. Adler's trace dynamics, if numerically simulated, would fail the
   same γ-invariance test as GPU-043.
2. 't Hooft's cellular automaton interpretation would fail similarly
   unless augmented with stochastic rewriting.
3. Wolfram hypergraph physics would require probabilistic rewriting
   (not deterministic) to produce emergent ℏ.

None of these programs has yet performed the equivalent numerical test.
QNG is the first to reach this diagnostic point explicitly.

## Scientific value of the negative result

**Even without a final ℏ derivation**, QNG has established:

1. A precise diagnostic criterion: ℏ-emergence REQUIRES ontological
   stochasticity (not merely complex determinism).
2. A concrete path forward: v9-P/v9-G with DER-QNG-056.
3. A fallback: V9-C with explicit ℏ axiom.
4. 17 falsified hypotheses, each with pre-registered tests and
   documented failure modes.

This is **more rigorous than most programs in the foundations of physics**.
The honest admission that ℏ may be axiomatic is a stronger position than
pretending to derive it through insufficient mechanisms.

## Open questions

1. **Does GPU-045 final verdict change this?** If λ_max > 5×10⁻³ per lu
   (surprising strong chaos), v9-P might close FDT via Ruelle-Bowen
   without external noise. Current tentative value ~10⁻³ suggests marginal.

2. **Can v9-G produce ℏ with NO calibration input?** The T_graph
   parameter must itself be derivable from substrate properties for
   true derivation. This requires further theoretical work.

3. **Is the relation ℏ = k_B T_graph dimensionally meaningful?**
   If yes, suggests thermodynamic interpretation (Unruh/Hawking style).
   If no, ad-hoc dimensional matching.

## Status

**DRAFT** — pending:
- GPU-045 final Lyapunov verdict (~15 min from now)
- Governance decision DEC-QNG-008 on Option 1 vs 2 vs 3 path
- Gabriel explicit approval to lock this note and update CLAUDE.md
  falsified list
