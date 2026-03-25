# QNG Native Update Law v1

Type: `derivation`
ID: `DER-QNG-005`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first concrete candidate native QNG update law that is still abstract enough to avoid premature phenomenological commitment.

## Inputs

- [qng-primitives-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-primitives-v1.md)
- [qng-state-space-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-state-space-v1.md)
- [qng-memory-structure-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-memory-structure-v1.md)
- [qng-history-summary-v1.md](C:/Users/tigan/Desktop/QNG-Theory%20Release-01/Relearning%20qng/04_qng_pure/qng-history-summary-v1.md)

## Candidate state split

We use the following working split:

- ontic node state `N_i(t)`
- native history summary `H_i(t)`
- optional local fluctuation input `Xi_i(t)`

The node state remains intentionally under-specified at the component level.

## Minimal law

The first concrete candidate form is:

`N_i(t+1) = U_local(N_i(t), mean_{j in Adj(i)} N_j(t), H_i(t), Xi_i(t))`

with a companion history update:

`H_i(t+1) = U_hist(H_i(t), N_i(t+1), mean_{j in Adj(i)} N_j(t+1))`

This is the first point where the rebuild makes a real native commitment:

- history is part of the substrate dynamics
- not merely a fitted correction term

## Structural components

The update law is assumed to have three channels.

### Channel A: local self-relaxation

Each node retains continuity with its own recent state.

### Channel B: local relational coupling

Each node reacts to its current neighborhood through local aggregation only.

### Channel C: history-sensitive correction

Each node reacts not only to the present neighborhood but also to how the present differs from its recent local history summary.

## Abstract decomposition

The update can be written schematically as:

`N_i(t+1) = Proj[ N_i(t) + Delta_self + Delta_rel + Delta_hist + Xi_i(t) ]`

where:

- `Delta_self` is self-relaxation
- `Delta_rel` is present-neighborhood coupling
- `Delta_hist` is memory correction
- `Proj` is a regularization or boundedness map

## Why this is stronger than v0

`v0` said only that memory exists.  
`v1` says where it lives in the update:

- not only in an effective field
- not only in phenomenological lag
- but directly in the native state transition

## Immediate theoretical consequences

From this form, a future coarse-grained delayed-response field becomes natural.

That is, effective lag can emerge from:

- native history summary
- plus neighborhood mismatch

rather than being inserted by hand.

## Deliberate non-choices

This file still does not decide:

- whether `Sigma` is primitive or derived
- whether `chi` is primitive or derived
- whether `Xi_i(t)` is fundamental noise or effective unresolved microstructure
- whether `Proj` is clipping, wrapping, bounded potential flow, or another mechanism

These remain separate decisions.

## What this already rules out

This update law already rules out the idea that QNG is fundamentally memoryless and only appears delayed at phenomenological level.

For this rebuild, memory is now a native structural ingredient.

## Near-term testable implications

Once a toy implementation exists, the first CPU tests should check:

1. locality
2. boundedness under `Proj`
3. dependence on history summary
4. separation between present-only and history-sensitive runs

GPU tests should later stress:

- robustness over seeds
- robustness over graph sizes
- robustness over history-window definitions
