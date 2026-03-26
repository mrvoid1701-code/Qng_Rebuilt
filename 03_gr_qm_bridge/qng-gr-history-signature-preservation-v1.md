# DER-BRIDGE-043 — History Signature Preservation: Anti-Ordering N-Scaling

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-042 (CPU-060), DER-BRIDGE-041 (CPU-059)
**Addresses**: Problem 6 (Lorentzian signature recovery — history mechanism)

---

## Motivation

CPU-060 established the with-history decay law: Δ_hist ~ N^(−0.87).

CPU-059 showed history consistently preserves stronger |corr| than no-history (P2
passed 5/5). But the no-history decay law was not measured.

**Open questions**:

1. What is the no-history decay rate Δ_nohist(N)?
2. Does history benefit (Δ_nohist − Δ_hist) increase or decrease with N?
3. At large N (64), does no-history signature still collapse or does it stabilize
   (because large-N dynamics are naturally slower)?

---

## Theoretical predictions

**Prediction A — No-history decay faster at all N**:
Without history, phi synchronizes toward global coherence (kuramoto → 1).
At each N, more phi-sync → more signature decay → Δ_nohist > Δ_hist.

**Prediction B — Two scenarios for N-scaling of benefit**:

Scenario 1 (history more important at small N): at small N, without-history
phi syncs quickly (few nodes, fast consensus). With history, anti-ordering kicks in.
The history benefit is LARGE at small N, shrinks at large N as both channels
slow down naturally.
→ benefit = Δ_nohist − Δ_hist DECREASES with N.

Scenario 2 (history more important at large N): at large N, without-history phi
also slows (many nodes). But history's anti-ordering creates structured local
diversity that GROWS with N (more phi patterns possible). The benefit could INCREASE.
→ benefit INCREASES with N.

**Prediction C — No-history power law**: Δ_nohist ~ N^β with β < 0
(decay decreases with N for the same sparse-graph reason, but with larger
prefactor than history version).

---

## Protocol

For each N in {8, 16, 32, 64} and seed in {20260325, 42, 137, 1729, 2718}:

1. Run 24-step rollout WITH history → |corr_1_hist|, |corr_24_hist|
2. Run 24-step rollout WITHOUT history → |corr_1_nohist|, |corr_24_nohist|
3. Compute:
   - decay_hist   = |corr_1_hist|   − |corr_24_hist|
   - decay_nohist = |corr_1_nohist| − |corr_24_nohist|
   - benefit      = decay_nohist − decay_hist  (positive = history helps)

Pass criteria:

- P1: decay_nohist > decay_hist at each N (history always preserves better)
- P2: |corr_24_hist| > |corr_24_nohist| at each N (final state better with history)
- P3: Δ_nohist follows power law across N (log-log linear fit R² > 0.9)
- P4: benefit (Δ_nohist − Δ_hist) is consistent in sign across seeds at N=32 (≥ 4/5)

---

## Theoretical significance

The ratio Δ_nohist / Δ_hist measures how much faster no-history decays vs history.
If this ratio is universal (N-independent), history provides a multiplicative
signature preservation factor. If the ratio grows with N, history becomes
increasingly important at large N.

Combined with CPU-060 (Δ_hist ~ N^(−0.87)):

    Δ_nohist(N) = [Δ_nohist/Δ_hist](N) × Δ_hist(N)

If Δ_nohist ~ N^(−β) with β < 0.87: no-history decays SLOWER than history at large N
(convergence from above — both reach same continuum limit).

If Δ_nohist ~ N^(−β) with β > 0.87: no-history decays FASTER — both converge to
zero but from different directions.
