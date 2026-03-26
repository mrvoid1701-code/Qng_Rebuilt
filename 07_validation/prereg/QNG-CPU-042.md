# Prereg QNG-CPU-042: Calibrated Continuity Balance

Status: `locked`
Locked before: first run of `qng_calibrated_continuity_reference.py`
Theory doc: `DER-BRIDGE-024` (`qng-qm-calibrated-continuity-v1.md`)

## Test objective

Find the optimal coupling constant α* such that Δρ + α*·div(J) ≈ 0, and
measure the explained variance R²_calib = corr(Δρ, -div(J))².

## Setup

- n_nodes = 16, steps = 24 (default Config)
- Seeds: [20260325, 42, 137, 1729, 2718]
- Two consecutive time points: steps 23 and 24
- use_history = True and use_history = False (comparison)
- α* = -Σ(Δρ·divJ) / Σ(divJ²) — OLS optimal coupling

## Locked predictions

### P1: α* > 0 on ≥4/5 seeds
Continuity Δρ + α*·divJ = 0 requires α* > 0 when Δρ ≈ -divJ (outflow = density decrease).
Follows from QNG-CPU-041 corr(Δρ,-divJ)>0 on 4/5 seeds.
EXPECTED TRUE on ≥4/5 seeds (seed 2718 had negative corr — exception expected)

### P2: R²_calib > 0.05 on ≥3/5 seeds
Non-trivial balance — at least 5% variance explained
EXPECTED TRUE (follows from QNG-CPU-041 corr values)

### P3: R²_calib > 0.5 on ≥1 seed
Strong signal — seed 137 expected R² ≈ 0.57 (corr²)
EXPECTED TRUE

### P4: cv(|α*|) < 1.5 across 5 seeds
Coupling is not wildly unstable
OPEN — Tier-1 vs Tier-2 question

## Decision rule

PASS if P1 (≥4/5) + P2 + P3 all true.
CONDITIONAL if P3 fails but P2 passes on all 5 seeds.
FAIL if P1 fails on more than 2 seeds (current direction wrong).

## What changes if FAIL

If P1 fails: the coupling α* is positive on some seeds — current points in
wrong direction for those topologies. Would require reconsidering whether
ψ = C_eff·exp(i·phi) is the right amplitude.

If P4 fails (cv > 1.5): α* is strongly topology-dependent (Tier-2) — the
coupling constant is not a universal property of the substrate.
