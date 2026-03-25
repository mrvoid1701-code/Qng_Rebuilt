# QNG Phi Identification v1

Type: `derivation`
ID: `DER-GOV-005`
Status: `proxy-supported`
Author: `C.D Gabriel`
Prereq: `DER-GOV-004` (sigma identification), `DER-GOV-002` (chi identification)

## Objective

Determine the physical role of the native field `phi` and test whether it is
a synchronization field, a coherence proxy, or a load proxy.

This completes the native state identification quadruple: chi → tau → sigma → phi.

## Background

From the simulation kernel:

```
phi update:
  phi_new = wrap_angle(
      phi_i
      + phi_rel_gain * angle_diff(phi_neigh, phi_i)    # sync toward neighbors (0.22)
      + phi_hist_gain * history.phase[i]                # history feedback (0.10)
  )

history.phase update:
  phase_new = wrap_angle(
      (1 - hist_p_rate) * phase[i]                     # decay (0.65)
      + hist_p_rate * angle_diff(phi_new, phi_neigh)    # track angular gradient (0.35)
  )
```

Key structural facts:
- `phi` is a proper angle (U(1) symmetry), initialized uniformly in [-π, π]
- `phi` SYNCHRONIZES toward neighbor phi with gain 0.22 per step
- `history.phase[i]` tracks the local ANGULAR GRADIENT (phi_i vs phi_neigh)
- `phi` enters `C_eff` ONLY INDIRECTLY via `history.phase`:
  `C_eff = 0.45*sigma + 0.35*(1-mismatch) + 0.20*(1+cos(history.phase))/2`
- `phi` does NOT appear in `L_eff` at all

## Claims

### Claim A: phi ≠ history.phase

Prediction: SUPPORTED

Argument: `phi` is the running angle; `history.phase` is its angular gradient
(difference to neighbors). They are related but not equal. After a rollout,
corr(phi, history.phase) should be significantly less than 1.0.

### Claim B: phi is a synchronization field

Prediction: SUPPORTED

Argument: The `phi_rel_gain * angle_diff(phi_neigh, phi_i)` term drives phi
toward neighbor values at every step. Over time, phi should converge toward
a synchronized state where variance decreases. History feedback (phi_hist_gain)
should further drive ordering.

### Claim C: corr(phi, C_eff) is weak

Prediction: SUPPORTED (weak correlation, topology-dependent)

Argument: phi→C_eff requires two steps: phi drives history.phase (gradient),
and history.phase enters C_eff via cos(history.phase). This is a nonlinear
indirect path. The resulting corr(phi, C_eff) should be below 0.5 on most seeds,
and its sign should be topology-dependent.

### Claim D: corr(phi, L_eff) is weak

Prediction: SUPPORTED (low correlation)

Argument: phi does not appear in `L_eff = 0.60*mem + 0.40*|chi|`.
Any correlation would only come from dynamical entanglement (phi→sigma→chi→L_eff
via neighbor coupling). This path is long and should produce weak correlation.

### Claim E: history introduces phase diversity (anti-ordering)

Prediction: SUPPORTED (QNG-CPU-040) — unexpected direction

Finding: Without history, phi converges almost perfectly toward global synchrony
(sync_order_nohist ≈ 0.999). With history, the history.phase feedback actively
drives phi AWAY from perfect synchrony, creating structured local phase gradients.
This is anti-ordering: history introduces phase diversity, not phase alignment.

var(phi_hist) > var(phi_nohist) on ALL 5 seeds.

## Physical reidentification (proxy-level)

From QNG-CPU-040 results:

- phi is a **near-perfectly synchronized phase field**:
  sync_order_hist ∈ [0.941, 0.986] — always > 0.94 across all seeds
- WITHOUT history, phi achieves near-perfect global synchrony (sync ≈ 0.999)
- WITH history, phi retains high sync but with structured local diversity
  (anti-ordering: history.phase feedback breaks perfect alignment)
- phi-L_eff coupling: weak AND sign-unstable (Tier-2 topology-dependent)
  |corr(phi,L_eff)| ∈ [0.17, 0.46], sign changes across seeds
- phi→C_eff coupling: indirect and topology-dependent (Tier-2)
  |corr(phi,C_eff)| < 0.5 on 3/5 seeds; high on seeds 137 and 2718
- phi is NOT a coherence proxy (C_eff) or load proxy (L_eff)

Physical picture:
- phi is the native phase oscillation / synchronization mode of the QNG substrate
- it achieves near-global coherence driven by neighbor synchronization
- history.phase acts as a local gradient memory that opposes perfect sync
- the combination (phi, history.phase) forms a phase oscillator + gradient pair,
  analogous to a phase field theory with a symmetry-breaking memory term
- phi's role in QM recovery: the phase field is the natural carrier of U(1) structure

## Open questions

- Does phi synchronize to a single global phase, or to a topology-dependent
  cluster structure?
- Is there a nontrivial winding number or topological invariant in the phi field?
- What is the relationship between phi synchronization and the mode/spectrum proxy
  (QM side)?
- Can phi serve as the argument of a U(1)-valued complex amplitude ψ = r * exp(i*phi)?

## Validation

Test: `QNG-CPU-040` — `qng_phi_identification_reference.py`
Decision: PASS

Pass criteria:
- P1: `|corr(phi, L_eff)|` < 0.5 on all K=5 seeds — PASS (max = 0.46, sign-unstable)
- P2: sync_order_hist > 0.9 on all K=5 seeds — PASS (min = 0.941)
- P3: `|corr(phi, C_eff)|` < 0.5 on ≥3/5 seeds — PASS (3/5 seeds below threshold)
- P4: var(phi_hist) > var(phi_nohist) on all 5 seeds — PASS (history = anti-ordering)
