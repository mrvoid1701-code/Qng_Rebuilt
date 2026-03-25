# QNG QM Multi-Channel Continuity Large-N Probe v1

Type: `derivation`
ID: `DER-BRIDGE-029`
Status: `proxy-supported` (partial: 2/4 — structural universality confirmed, N-weakening identified)
Author: `C.D Gabriel`
Prereq: `DER-BRIDGE-028` (multi-channel current — law established at N=16)

## Objective

Test whether the multi-channel continuity law established at N=16 (QNG-CPU-046)
is N-stable: does the law hold, and do the structural features of the coupling
coefficients persist, at N=8, N=16, N=32?

## Background

QNG-CPU-046 established the effective continuity law at N=16 (default):

```
∂_t(C_eff²) + α_phi·div(J_phi) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0
mean R²_combined = 0.405 > 0.256 (best single), universally (5/5 seeds)
```

The hard-open-problems list (Problem 9, Problem 2) cites "large-N limit behavior"
as open for all identified fields and laws. The multi-channel continuity law is
the first concrete QM-recovery result that can be probed for N-scaling.

## Why N-scaling matters

1. **Topology density scales with N**: `build_graph` creates a ring + Erdos-Renyi
   edges (p=0.18). Expected edges:
   - N=8:  ring 8 + ~0.18·C(7,2)=~3.8 extra → mean degree ~3.0
   - N=16: ring 16 + ~0.18·C(14,2)=~17.6 extra → mean degree ~4.2
   - N=32: ring 32 + ~0.18·C(30,2)=~81.3 extra → mean degree ~7.1

2. **Phi synchronization increases with degree**: More neighbors → stronger
   pulling toward consensus → smaller phi differences → weaker phi channel

3. **Mismatch/mem channels scale with neighbor count**: More neighbors →
   larger div(J_mis) and div(J_mem) signals → potentially stronger
   mismatch-memory channels

4. **Large-N limit identification**: Whether R²_combined grows, saturates, or
   degrades with N tells us whether the law is a genuine thermodynamic limit
   law or a finite-size artifact.

## Predictions summary

### Expected structural changes from N=8 to N=32

- phi channel weaker (more synchronization, smaller sin(Δφ)):
  |α_phi / α_mis| expected to decrease with N

- mismatch/mem channels stronger (more neighbors → larger gradient accumulation)

- R²_combined: unclear direction — more signal from mismatch/mem but also
  more cancellation from summing over more neighbors

## Claims

### Claim A: R²_combined > R²_best_single at all N and ≥4/5 seeds

Prediction: OPEN

Argument: If the multi-channel law is a genuine structural property of QNG
substrate, it should hold regardless of system size. A failure at any N would
indicate the law is a finite-size artifact.

### Claim B: mean R²_combined ≥ 0.30 at N=8, N=16, N=32

Prediction: OPEN

Argument: R²=0.405 at N=16. Whether this improves or degrades at other N
is an open question, but if the law is N-stable, it should stay above 0.30
(the Tier-1 threshold established at N=16).

### Claim C: |α_phi| < |α_mis| universally across N and seeds

Prediction: OPEN

Argument: At N=16, α_mis is 10-20x larger than α_phi on most seeds.
If the phi channel is near-zero due to synchronization (which strengthens
with N), this ratio should hold or strengthen.

### Claim D: mean R²_combined increases from N=8 to N=32

Prediction: OPEN

Argument: Larger systems have more statistics (more nodes) and potentially
stronger mismatch gradient signals. But increased synchronization may
counteract this. Direction uncertain.

## Physical interpretation

If R²_combined is N-stable (≥0.30 at all N, multi-channel beats single-channel):
- The multi-channel continuity law is a genuine large-N property of QNG substrate
- The mismatch-driven diffusion is robust: it does not require fine-tuning of N
- This supports upgrading the law from "proxy-supported at N=16" to
  "N-stable proxy-supported"

If R²_combined degrades at large N:
- The law is finite-size artifact at N=16
- The effective density evolution changes character at large N
- The large-N limit requires a different analytical approach

If R²_combined improves at large N:
- The law becomes stronger in the thermodynamic limit
- This is the strongest possible outcome for QM recovery

## Validation

Test: `QNG-CPU-047` — `qng_multichannel_large_n_reference.py`
Decision: PARTIAL (2/4 predictions)

Results:
- P1: R²_comb > best at N=32, ≥4/5 — PASS (5/5)
- P2: mean R²_comb ≥ 0.30 at N=8 AND N=32 — FAIL (N=32: 0.269 < 0.30)
- P3: |α_phi/α_mis| decreases N=8→32 on ≥3/5 — PASS (4/5)
- P4: best_N ≠ N=8 on ≥4/5 — FAIL (only seeds 137, 1729 have best_N ≠ 8)

Key findings:
- Multi-channel beats single-channel at ALL N (15/15 = 5 seeds × 3 N values): Tier-1
- R² decreases monotonically with N: 0.586 (N=8) → 0.405 (N=16) → 0.269 (N=32)
  Cause: denser graph → more cancellation in divergence sums (mean_deg 3.2→4.3→6.9)
- phi channel absent at large N: |α_phi| < 0.0004 at N=32 universally
- Large-N limit: ∂_t(C_eff²) + α_mis·div(J_mis) + α_mem·div(J_mem) ≈ 0 (phi absent)
- N=8 strong: R²=0.909 (seed 42), R²=0.823 (seed 20260325) — sparse-graph law
- gain (R²_comb - R²_best_single) persists at all N: 0.168 → 0.149 → 0.112
- Identified: degree-normalized current may restore N-stability (open for CPU-048)
