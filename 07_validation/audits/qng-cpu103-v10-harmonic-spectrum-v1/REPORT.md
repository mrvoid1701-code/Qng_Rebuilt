---
type: evidence
test_id: QNG-CPU-103
category: analytical_verification
hardware: CPU
status: completed
verdict: HO_PASS (v10 axioms A3 consistent)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-062 (v10 foundational)
  - DER-QNG-060 (quantum requirements)
---

# QNG-CPU-103 v10 harmonic oscillator spectrum REPORT

## Verdict: **HO_PASS** — v10 axioms internally consistent

First test of v10 foundational axioms. The harmonic oscillator spectrum
E_n = ℏ·ω·(n+1/2) is recovered to machine precision across three test
configurations.

## Results

### Test 1: Standard parameters (ℏ=1, ω=1, μ=1)
```
E_n:        0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, ...
Predicted:  0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, ...
Max rel diff: 0.000% (machine precision ~1e-14)
```

### Test 2: QNG prediction (ℏ=β_φ/2=0.03, ω=1, μ=1)
```
E_n:        0.015, 0.045, 0.075, 0.105, ...
Predicted:  0.015, 0.045, 0.075, 0.105, ...
Max rel diff: 0.000%
```

### Test 3: Scale invariance (ℏ=0.03, ω=0.2, μ=0.857)
```
E_n:        0.003, 0.009, 0.015, 0.021, 0.027, ...
Predicted:  0.003, 0.009, 0.015, 0.021, 0.027, ...
Max rel diff: 0.000% (up to machine precision)
```

### Truncation check
Maximum difference between N_truncation=50 and N_truncation=200 in
first 5 eigenvalues: **0.00e+00** — no truncation sensitivity.

### Commutator verification
```
|[Ψ̂, Ψ̂†] - ℏ·I|_max < 1e-13 (first 90 rows of 100-dim truncated basis)
```

Canonical commutation relation exact to machine precision.

## Interpretation

This test confirms:

1. **Axiom A3 (Heisenberg algebra)** is correctly implemented in the
   truncated Fock basis representation.

2. **Requirement #1 (non-commutativity)** from DER-QNG-060 is satisfied:
   `[x̂, p̂] = i·ℏ_lattice` is operational.

3. **Requirement #8 (discrete spectrum)** is satisfied: energy eigenvalues
   form an integer ladder with constant spacing ℏω.

4. **QNG prediction ℏ_lattice = β_φ/2 = 0.03** gives self-consistent
   spectrum (Test 2 — no internal contradiction).

## What this does NOT prove

This is a **minimum consistency check**, not a physics verification:

- Any canonical quantization of a harmonic oscillator gives E_n = ℏω(n+½)
  by construction
- This test shows that v10 matrix representations agree with the standard
  QM formula
- It does NOT show that v10 correctly describes QNG physics; that requires
  CPU-105 (classical limit check) and CPU-106 (ℏ_lattice identification)

## Next tests

- QNG-CPU-104: Uncertainty principle ΔxΔp ≥ ℏ/2
- QNG-CPU-105: Classical limit (coherent state → v8 trajectory)
- QNG-CPU-106: ℏ_lattice = β_φ/2 identification via ground state energy
- QNG-CPU-107: Interference test (requires multi-site)

## Files

- `report.json` — numerical spectra + verdicts
- `../../../../tests/cpu/qng_cpu103_v10_harmonic_spectrum.py` — executable
