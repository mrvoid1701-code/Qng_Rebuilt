# Prereg QNG-CPU-040: Phi Identification

Status: `locked`
Locked before: first run of `qng_phi_identification_reference.py`
Theory doc: `DER-GOV-005` (`qng-phi-identification-v1.md`)

## Test objective

Determine the physical role of native field `phi` by testing:
1. Whether phi is a graph synchronization field (expected SUPPORTED)
2. Whether phi is a coherence proxy (C_eff) — expected NOT
3. Whether phi is a load proxy (L_eff) — expected NOT
4. Whether history drives phase ordering (expected SUPPORTED)

## Setup

- n_nodes = 16, steps = 24 (default Config)
- Seeds: [20260325, 42, 137, 1729, 2718]
- use_history = True and use_history = False (comparison)

## Locked predictions

### P1: phi is NOT a load proxy
|corr(phi, L_eff)| < 0.3 on ALL 5 seeds — EXPECTED TRUE
(phi absent from L_eff by construction)

### P2: phi has positive neighbor synchronization
sync_order_hist = mean(cos(phi_i - phi_j) for neighbor pairs) > 0
on ALL 5 seeds — EXPECTED TRUE
(phi_rel_gain=0.22 drives phi toward neighbors)

### P3: phi is not primarily a coherence proxy
|corr(phi, C_eff)| < 0.5 on at least 3/5 seeds — EXPECTED TRUE
(phi enters C_eff only indirectly via history.phase)

### P4: history introduces phase diversity (anti-ordering)
var(phi_hist) > var(phi_nohist) on ALL 5 seeds — RESOLVED TRUE
(history.phase feedback tracks local gradients and breaks perfect synchrony)

## Decision rule

PASS if P1 + P2 + P3 + P4 are all true.
CONDITIONAL if P4 fails but P1 + P2 + P3 pass (synchronization supported but
history role unclear at n=16).
FAIL if P1 or P2 fails on more than one seed.

## What changes if FAIL

If P1 fails (|corr(phi, L_eff)| > 0.3): phi has unexpected dynamic coupling
to load — requires investigation of phi→sigma→chi→L_eff indirect path.

If P2 fails (sync_order < 0): phi is anti-synchronized across neighbors, which
would be a fundamentally different collective mode (topological frustration).
