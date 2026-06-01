---
type: test
test_id: QNG-CPU-103
category: analytical_verification
hardware: CPU
status: preregistered
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-062 (v10 foundational reformulation)
  - DER-QNG-060 (quantum requirements)
  - DER-QNG-061 (connection map, ⟨L⟩ insight)
---

# QNG-CPU-103 — v10 harmonic oscillator spectrum test

## Purpose

Verify that v10 Hamiltonian, in the free-field harmonic limit, produces
the discrete spectrum `E_n = ℏ_lattice ω (n + 1/2)`.

This is the **minimum test** that v10 axioms are internally consistent.
Any lattice quantum theory with canonical commutation must give this
spectrum in the harmonic limit. If it doesn't, the axiomatization is
broken.

## Setup (minimal)

Consider a SINGLE site with:
```
Ĥ = (1/2μ) π̂†_Ψ π̂_Ψ + (μ ω²/2) Ψ̂†_Ψ Ψ̂_Ψ
  = ℏ_lattice ω (Ψ̂† Ψ̂ / ℏ_lattice + 1/2)
  = ℏ_lattice ω (N̂ + 1/2)
```

where `[Ψ̂, Ψ̂†] = ℏ_lattice`.

Eigenvalues of N̂ = Ψ̂†Ψ̂/ℏ are non-negative integers. Therefore:
```
E_n = ℏ_lattice ω (n + 1/2),   n = 0, 1, 2, ...
```

## Numerical implementation

Use N-dimensional truncated Fock basis (`N = 50` levels). Matrix form
of Ψ̂, Ψ̂†:

```python
Psi_hat = np.zeros((N, N))
for n in range(N-1):
    Psi_hat[n, n+1] = np.sqrt((n+1) * hbar_lattice)
Psi_dag = Psi_hat.T
H = (1/(2*mu)) @ Psi_dag @ Psi_hat + (mu * omega**2 / 2) @ Psi_hat @ Psi_dag
# Note: Psi_hat Psi_dag != Psi_dag Psi_hat due to [Psi, Psi†] = ℏ
```

Actually, use canonical quadrature `x̂ = (Ψ̂ + Ψ̂†)/sqrt(2)`, `p̂ = (Ψ̂ - Ψ̂†)/(i sqrt(2))`.

Diagonalize H numerically and check first 5 eigenvalues vs prediction.

## Parameters (for test)

```
mu = 1.0
omega = 1.0
hbar_lattice = 1.0  (or 0.5, or β_φ/2=0.03 — multiple values)
N_truncation = 50
```

## Gates

### `HO_PASS` (primary)
- First 5 eigenvalues `E_n` match `ℏ_lattice ω (n + 1/2)` within 1%
- Level spacing `E_{n+1} - E_n = ℏ_lattice ω` constant within 0.1%
→ v10 axioms consistent; quantization works.

### `HO_MARGINAL`
- First 3 levels OK but higher levels deviate
→ truncation issue; increase N.

### `HO_FAIL`
- Level spacing not constant OR non-integer eigenvalues
→ axiomatization broken; re-examine A3 algebra.

## Tolerances

- Eigenvalue precision: 1e-10 (numerical linear algebra precision)
- Truncation tolerance: error from N_truncation dropping from 50 to 20
  should be <1% for first 5 levels.

## Runtime estimate

~1 second on CPU for N=50 eigenvalue problem. Trivial.

## Falsifiability

If HO_FAIL → v10 axioms A3 (Heisenberg algebra) are not correctly
implemented. Must revise before proceeding.

## Dependencies

Requires NumPy. No GPU. Analytical verification only.

## Outputs

- `07_validation/audits/qng-cpu103-v10-harmonic-spectrum-v1/`
  - `spectrum.csv` — first 20 eigenvalues
  - `REPORT.md` — verdict + comparison with theory
  - `plot.png` — spectrum visualization (optional)
