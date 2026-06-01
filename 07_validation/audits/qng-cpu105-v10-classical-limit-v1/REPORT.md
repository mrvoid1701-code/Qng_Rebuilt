---
type: evidence
test_id: QNG-CPU-105
category: analytical_verification
hardware: CPU
status: completed (minimum version — single-site harmonic)
verdict: CL_PASS (coherent states reproduce classical trajectory exactly)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-062 (v10 foundational, corrected)
  - DER-QNG-063 (classical limit analysis)
---

# QNG-CPU-105 v10 classical limit (minimum version) REPORT

## Verdict: **CL_PASS** — coherent state evolution matches classical trajectory

Ehrenfest theorem verified: for harmonic oscillator v10, `⟨Ψ̂(t)⟩` equals
classical `α₀·e^{-iωt}` EXACTLY (0.0000% error) across all tested
`(ℏ, α₀)` combinations.

## Results

| ℏ | α₀ | Semiclassical param |α|²/ℏ | Max rel error (t ∈ {π/4, π/2, π, 2π}) |
|---|---|---|---|
| 1.00 | 2.0 | 4.0 | 0.0000% |
| 1.00 | 5.0 | 25.0 | 0.0000% |
| 0.50 | 5.0 | 50.0 | 0.0000% |
| 0.10 | 5.0 | 250.0 | 0.0000% |
| 0.01 | 5.0 | 2500.0 | 0.0000% |

**Observation**: error is 0 at all semiclassical parameters, confirming
that harmonic oscillator coherent states satisfy Ehrenfest theorem
EXACTLY (due to linearity of Ĥ in â, â†).

## Interpretation

This test confirms:
1. v10 canonical operator implementation is correct
2. Coherent state construction is correct
3. Schrödinger time evolution works
4. `⟨Ψ̂(t)⟩` behaves classically for coherent states
5. No numerical artifact from truncation (N=100 sufficient for |α|=5)

## Scope (minimum version)

This test covers the **simplest case only**: single-site harmonic
oscillator. The Ehrenfest theorem guarantees exact classical evolution
for any quadratic Hamiltonian, so this test is REGARDLESS trivial
mathematically. It serves as a **sanity check** on implementation.

## What this does NOT test

More stringent tests needed to validate v10 fully:

1. **Anharmonic oscillator** (CPU-105-v2): with V(|Ψ|⁴) or similar,
   classical and quantum trajectories diverge at late times. Expected
   divergence scale: `t_classical_breakdown ~ 1/(ℏ × ω_anharmonic)`.

2. **Multi-site v10** (CPU-105-v3): lattice with hopping + V_couple.
   Test that coherent state `|{α_i}⟩` evolves like v8 Yoshida4 on `(σ_m, φ, π_m, π_φ)`.

3. **Full v8 Hamiltonian** (CPU-105-v4): test that v8 ring attractor
   evolution recovered from v10 coherent state at large |α|.

These are Phase II-III tests requiring substantial implementation effort.

## Combined v10 consistency status

After CPU-103, CPU-104, CPU-105 (all PASS):

**v10 axioms verified**:
- A1 graph substrate: trivially
- A2 complex amplitude: coherent states constructed correctly
- A3 canonical algebra: [Ψ̂, Π̂†] = iℏ verified
- A4 Hilbert space: Fock basis works
- A5 unitary evolution: exp(-iĤt/ℏ) gives classical limit

**All 8 quantum requirements from DER-QNG-060 addressed**:
- 1 non-commutativity: CPU-104
- 2 complex amplitude: CPU-105
- 3-7: follow from axioms (standard QM)
- 8 discrete spectrum: CPU-103

## Files

- Script: `tests/cpu/qng_cpu105_v10_classical_limit.py`
- Report JSON: `report.json`

## Next steps

**CPU-105-v2** (pre-register): anharmonic oscillator, look for quantum
deviations from classical.

**CPU-106** (design): ℏ identification — does v10 ground state energy
impose constraint on ℏ_lattice?

**CPU-107** (future): interference test with two coherent states
superposed — Born rule in action.
