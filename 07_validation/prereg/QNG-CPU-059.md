# QNG-CPU-059

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
Date: `2026-04-07`
test_class: `matter_source_identification`

## Title

Conservative Hamiltonian ring dynamics — does the ring survive without dissipation?

## Purpose

CPU-056 showed Channel G destroys the v5 ring (dissipative stability requires k_back < 0.0015).
CPU-057/058 showed the snapshot H is positive (ring has positive mass IF evaluated conservatively).

Einstein's question (NOTE-QNG-017, Gap 7): is the v5 ring a genuine soliton of H?
In other words, does the ring survive under PURE Hamiltonian dynamics (no dissipation)?

The v5 ring is an attractor of DISSIPATIVE gradient flow of E. The snapshot Hamiltonian
(CPU-057) evaluated H on this attractor. But a stable particle requires a soliton of the
CONSERVATIVE dynamics — a stationary or periodic solution of Hamilton's equations.

If the ring dissolves under conservative dynamics: it is NOT a soliton of H.
The CPU-057/058 snapshot mass is "energy of a dissipative attractor", not "rest mass".
Gap 7 is confirmed as a fundamental structural problem.

If the ring survives under conservative dynamics: surprising — need to understand why
Derrick scaling argument (H ~ R² → dH/dR > 0 → ring wants to shrink) fails.

## Conservative dynamics (Hamilton's equations)

H = k_back/2 × Σchi² + E[sigma, chi, phi]

Hamilton's equations (continuous limit):
  σ̇_i = +∂H/∂chi_i = k_back × chi_i + chi_rel/2 × (sbar - si) + delta × (si - sref) + chi_decay × chi_i
  χ̇_i = -∂H/∂sigma_i = -alpha × (si - sref) + beta × z × (sbar - si) - delta × chi_i + phi_terms

phi conservative update (XY-model dynamics):
  φ̇_i = -∂H/∂phi_i = beta_phi/6 × Σ_nb sigma_i × sigma_j × sin(phi_j - phi_i)

Implemented as explicit Euler with dt=0.005.
NO Channel A (dissipative sigma restoring), NO Channel F (phi disorder depletion),
NO chi_decay dissipation. Only the conservative channels.

## Experimental design

**Phase 0:** Form v5 ring (Phase1=300 + Phase2=1500 steps), record state at T=1000.
**Phase H:** Run conservative Hamilton dynamics for 500 steps with dt=0.005.
**k_back:** 0.10 (same as CPU-058 reference; snapshot H was positive at this k_back)

**Measurements every 25 Hamiltonian steps:**
```
M_ring(t) = Σ max(0, sigma_ref - sigma_i)
H_total(t) = T(k_back) + E[sigma,chi,phi] - E_vac   [should be ~conserved]
chi_rms(t) = sqrt(Σchi² / N)
```

H_total should stay approximately constant (test of integration stability).
M_ring decay rate measures ring lifetime.

## Checks

**Check 1 — Ring dissolves under conservative dynamics (expected):**
```
M_ring(t=500) < M_ring(t=0) / 2   [ring lost >50% of depletion in 500 Hamiltonian steps]
```

**Check 2 — H is approximately conserved (integration stability):**
```
|H_total(t=500) - H_total(t=0)| / |H_total(t=0)| < 0.20   [H conserved to 20%]
```

**Check 3 — Ring lifetime (informational):**
Report t_half: the Hamiltonian step at which M_ring first drops below M_ring(t=0)/2.

## Decision rule

**PASS** if Check 2 passes (integration stable) regardless of Check 1.
- Check 1 PASS: ring dissolves → confirms Gap 7, ring is NOT a H-soliton
- Check 1 FAIL (ring survives): unexpected finding — ring IS stable under H dynamics

If Check 2 FAIL: integration unstable, reduce dt and re-run.

## Artifact paths

- `07_validation/audits/qng-ring-conservative-v1/report.json`
- `07_validation/audits/qng-ring-conservative-v1/summary.md`
