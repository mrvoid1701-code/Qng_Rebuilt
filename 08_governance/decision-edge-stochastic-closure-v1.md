---
id: DEC-QNG-006
type: decision
title: Formal closure of edge-stochastic hbar program; v9 charter opened
date: 2026-04-22
author: C.D Gabriel (autonomous execution)
status: locked
upstream:
  - NOTE-QNG-018 (edge-stochastic program)
  - CPU-092, CPU-093, CPU-094 (scalar i.i.d. family closure)
  - CPU-095, CPU-096, CPU-097 (temporal OU, spatial correlation, compact U(1) LGT)
  - DEC-QNG-005 (Option C for (σ_g, χ) sub-theory)
---

# DEC-QNG-006: Closure of edge-stochastic program, v9 charter opened

## Decision

**1. The edge-stochastic hbar program (NOTE-QNG-018) is formally CLOSED
with a complete negative result.** All four structural options
enumerated in §8 closure statement have been empirically falsified on
2026-04-22:

- Scalar i.i.d. edge noise (original formulation) — CPU-092, CPU-093, CPU-094
- Option (b') temporal correlation (OU process) — CPU-095
- Option (b') spatial correlation (FFT Gaussian kernel) — CPU-096
- Option (a) dynamical edge gauge field (compact U(1) LGT) — CPU-097

**Thirteen ℏ programs now dead in v8 canonical**: α, β, γ, δ, θ,
Tesla-cavity, Bohr-Sommerfeld, Hessian-RMT, edge-scalar-Gaussian,
edge-scalar-discrete/non-Gaussian, edge-temporal, edge-spatial,
edge-gauge.

**2. The substrate-emergence route for ℏ is exhausted at the classical
Hamiltonian level.** Consistent with Wallstrom 1994 theorem
(independent agent audit 2026-04-22) forbidding "ℏ from classical
noise alone" in any Madelung+noise formulation.

**3. Option (c) — external canonical quantization of H_v8 — becomes
the residual structural path.** This is not a failure of QNG but a
reassignment of ℏ from "emergent from substrate" to "imposed by the
measurement/quantization postulate."

**4. v9 DESIGN CHARTER opened** (charter only — NOT implementation):
any v9 extension must respect the aesthetic constraints expressed by
Gabriel 2026-04-22: "mai delicat si mai frumos decat ar trebuii"
(more delicately and more beautifully than should be necessary).
Specifically:

- No bolt-on: v9 must be a structural extension with clear physical
  motivation, not an ad hoc ℏ-injection.
- Fluctuation-dissipation or topological protection as organizing
  principle: the proposed ℏ scale must be structurally PROTECTED
  against continuous tuning (unlike the 13 failed programs).
- Preserve the v8 locked layer: Jackiw-Rebbi mass (GPU-035),
  KG dispersion (GPU-012), Lorentz isotropy (DER-QNG-043), Shapiro
  delay (DER-QNG-044) must survive intact.
- Wallstrom compatibility audit: any v9 proposal must be shown to
  NOT be equivalent to Madelung+noise (which is blocked).

## Rationale

Before committing effort to v9, the exhaustion of v8-internal options
had to be documented. CPU-095/096/097 close that question definitively
within scan ranges reasonably expected to cover the phenomenon. A
continued search inside v8 canonical for emergent ℏ would be effort
against evidence; the 13-program negative record is load-bearing.

The decision does NOT retract v8 itself. v8 remains the locked
classical substrate with correct matter (Jackiw-Rebbi), gauge
structure (sine-Gordon Z), Einstein correspondences (Shapiro,
dispersion, Lorentz), and orbital attractor mass scale (CPU-074/075
as topological-charge identifications).

## Action items

1. NOTE-QNG-018 §8 updated with CPU-095/096/097 closure statements (done 2026-04-22).
2. THEORY_STATE.md falsified-candidates table updated with 11th/12th/13th programs (done 2026-04-22).
3. v9 charter document drafted: `08_governance/v9-charter-v1.md` (to follow).
4. Pending Gabriel review before any v9 implementation begins.

## Counterfactual (what would change this decision)

- If Gabriel identifies a structural ingredient in v8 that was not
  probed (e.g., non-abelian gauge, continuum limit coupling
  constant, or explicit integrability structure), CPU-092..097 do not
  close that; such an ingredient would be a new program.
- If an agent-audit identifies a formal flaw in the Wallstrom
  argument as applied to QNG's substrate, option (c) may be
  downgraded from "residual only" to "one of several."
- A v9 proposal that demonstrably does not reduce to Madelung+noise
  AND shows emergent ℏ in simulation would supersede this decision.

## Cross-references

- NOTE-QNG-018 §8 (detailed closure narrative, per-test verdicts)
- MEMORY.md entries `project_cpu092_edge_stochastic_debye_waller`,
  `project_cpu093_094_edge_noise_universality`,
  `project_cpu095_096_097_edge_program_closed`
- Agent consultation transcripts (savant, einstein-mind, tesla-mind, quantum-node-theory-professor) 2026-04-22
- Wallstrom 1994 "Inequivalence between the Schrödinger equation and the Madelung hydrodynamic equations"

## Signature

C.D Gabriel (theory owner, autonomous execution mode granted
2026-04-22 11:45); executed by Claude Opus 4.7. Locked 2026-04-22.
