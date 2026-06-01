---
id: AUDIT-QNG-CPU-100
type: audit
title: CPU-100 Verlinde-entropic probe — VERLINDE-PARTIAL (R-universal classical action, not hbar)
version: v1
date: 2026-04-22
status: locked
scope: QNG-GPU-100 reduced_series + snapshots; entropy / area / action candidates across R in {3, 4, 5}
---

# CPU-100 Verlinde-Entropic Probe — Verdict

## Summary: VERLINDE-PARTIAL

A classical R-universal action candidate is identified, **but it is not
an integer-quantized hbar**. The ACTION-INVARIANT finding extends the
NOTE-QNG-017 family of classical orbital invariants; it closes the
Verlinde/holographic category for hbar but opens one new classical
invariant for further study.

15th hbar program within v8 closed.

## Per-R observables

| R | T_cycle | ⟨H⟩ | S_sm (nats) | S_phi (nats) | \|H\|·T_cycle | S_sm·T_cycle |
|---|---|---|---|---|---|---|
| 3 | 176.32 | −226.07 | 5.046 | 4.529 | 39858 | 889.8 |
| 4 | 178.22 | −225.02 | 5.175 | 4.389 | 40102 | 922.3 |
| 5 | 182.69 | −223.78 | 4.918 | 3.776 | 40886 | 898.5 |

## Cross-R universality rankings (sorted by across-R CV)

| Candidate | CV | Action-dim? | Status |
|---|---|---|---|
| \|H\|·T_cycle | **1.09%** | YES (energy·time) | universal, classical |
| S_sm·T_cycle | 1.52% | no (nat·time) | universal, dimensional mismatch |
| S_sm·\|H\|·T_cycle / N | 1.49% | ambiguous | universal, no fixed meaning |
| S_sm·\|H\| | 2.32% | no (nat·energy) | universal, dim mismatch |
| S_sm (pooled) | 2.08% | no (dimensionless) | universal Shannon entropy |
| (S_sm + S_phi)·\|H\|·T / N | 3.43% | ambiguous | universal |
| S_phi (pooled) | 7.72% | no | weakly universal |
| sigma_prod_per_lu | 31.7% | — | not universal |
| rho1 = S_sm / A_ring | 41.9% | no | **NO Bekenstein law** |
| rho2 = S_phi / A_ring | 47.1% | no | **NO Bekenstein law** |

## Within-R cycle-to-cycle stability of \|H\|·T_cycle

| R | n_cycles | mean | std | within-R CV |
|---|---|---|---|---|
| 3 | 28 | 39857 | 5065 | **12.71%** |
| 4 | 27 | 40100 | 3584 | **8.94%** |
| 5 | 26 | 40886 | 3344 | **8.18%** |

## Integer-ladder check on \|H\|·T_cycle

Tested theta_0 in {100, 200, 500, 660, 1000, 2000, 5000, 10000}.
Best fit at theta_0 = 100: ratios {398.57, 401.00, 408.86} → integers
{399, 401, 409}. Integer-differences {2, 8} are not a constant step,
so no Einstein-Brillouin n·h = ∮H dt ladder with uniform step.
Even if we accept the ~0.1% integer-matching error, the integer spacing
itself is R-dependent. No rigid hbar scale emerges.

## Bekenstein/holographic verdict

The ratio S_sm / A_ring scales with R^{-2} (expected: 4π²R² growth of
torus area dwarfs R-weak entropy change). No S ∝ A law. No horizon.
No hbar from surface area.

## Interpretation

The v8 orbital attractor under R1 has several **classical** quantities
that are universal across R:

1. ⟨L⟩_universal = N·β_φ/2 = 660 (CV 0.11%, NOTE-QNG-017)
2. ⟨H⟩ ≈ −225 (CV 0.5%, this probe)
3. \|H\|·T_cycle ≈ 40000 (CV 1.09%, NEW this probe)
4. S_sm ≈ 5.05 nats (CV 2.08%, NEW this probe)
5. Orbital period T_cycle ≈ 179 lu (CV 1.8%)

These are all manifestations of a single structural fact: the R1
orbital attractor at L=20 has self-similar statistics across R.
Nothing among them is an integer-quantized action step of fixed
size — they are continuous R-universal classical numbers, consistent
with Liouville-Noether's prediction (classical H cannot produce
rigid action scale).

## Decision flow

Per `project_v9_launch_2026_04_22.md`:

- VERLINDE-PASS (dimensionally interpretable) → would have opened
  DER-QNG-053 thermodynamic hbar path.
- VERLINDE-MARGINAL → partial promotion.
- VERLINDE-FAIL → another closed category.

Formally VERLINDE-PASS on the S_sm gate (2.08%), but that quantity
is dimensionless. Formally VERLINDE-PASS on the \|H\|·T_cycle
action-dimensional gate (1.09%), but that value is not integer-
quantized.

**Verdict: VERLINDE-PARTIAL** — R-universal classical action exists,
hbar mechanism does not. **Sub-finding**: the \|H\|·T_cycle adiabatic
invariant is a new classical orbital invariant worth documenting
alongside ⟨L⟩.

## Consequences

1. V9-entropic category closed as hbar mechanism.
2. Two new classical R-universal invariants added to NOTE-QNG-017
   supplementary list: \|H\|·T_cycle ≈ 40000 and S_sm_pooled ≈ 5.05 nats.
3. Next (CPU-101 Dirac analysis) is final unexplored category.
4. Wallstrom+Liouville+Noether blockade stands; V9-C path remains
   obligatory residual unless CPU-101 surprises.

## Artifacts

- Script: `tests/cpu/qng_cpu100_verlinde_entropic.py`
- Machine-readable: `report.json`
- Data source: `07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/`

Signed: autonomous assistant (main context)
Locked: 2026-04-22
