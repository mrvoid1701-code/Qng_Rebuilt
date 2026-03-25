# Prereg QNG-CPU-041: Complex Amplitude Proxy

Status: `locked`
Locked before: first run of `qng_complex_amplitude_proxy_reference.py`
Theory doc: `DER-BRIDGE-023` (`qng-qm-complex-amplitude-proxy-v1.md`)

## Test objective

Construct ψ_i = C_eff_i * exp(i*phi_i) from native fields and test whether
the resulting density ρ = |ψ|² and current J = Im(ψ* · ∇ψ) satisfy a
proxy-level continuity balance.

## Setup

- n_nodes = 16, steps = 24 (default Config)
- Seeds: [20260325, 42, 137, 1729, 2718]
- Two consecutive time points: state at step 23 and step 24
- use_history = True and use_history = False (comparison)

## Locked predictions

### P1: ψ is well-defined
C_eff > 0 and phi ∈ [-π, π] on all nodes, all seeds — EXPECTED TRUE (trivial)

### P2: current has correct sign
corr(Δρ, -div(J)) > 0 on ≥3/5 seeds — OPEN
(phi anti-ordering from history creates nonzero gradients)

### P3: current reduces imbalance
rms(Δρ + div(J)) < rms(Δρ) on ≥3/5 seeds — OPEN
(current partially cancels density change)

### P4: history-driven currents are nonzero
mean|div(J)_hist| > mean|div(J)_nohist| on ≥3/5 seeds — EXPECTED TRUE
(history anti-ordering → larger phase gradients → larger currents)

## Decision rule

PASS if P2 + P3 + P4 all pass.
CONDITIONAL if P2 passes but P3 fails (current has right direction but
insufficient magnitude for balance).
FAIL if P2 fails on more than 2 seeds (current sign wrong).

## What changes if FAIL

If P2 fails: corr(Δρ, -div(J)) ≤ 0 — the current points in the wrong direction
relative to density change. This would mean the ψ = C_eff*exp(i*phi)
construction is not the right QM amplitude, and an alternative must be sought.

If P4 fails: history does not increase phase gradients — the anti-ordering
effect does not translate into larger currents. This would suggest the
phi gradient structure is more subtle than expected.
