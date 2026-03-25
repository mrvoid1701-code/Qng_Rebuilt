# QNG History Summary v1

Type: `definition`
ID: `DEF-QNG-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first concrete candidate for the local history summary `H_i(t)` used in the native QNG update law.

## Why this object matters

The rebuild has already isolated native memory as one of the most plausible core ideas in QNG.

But native memory must not be identified too quickly with:

- phenomenological `tau`
- trajectory lag amplitude
- or one specific kernel fit

So we define a substrate-level history object first.

## Candidate definition

For each node `i`, define the local history summary:

`H_i(t) = (M_i(t), D_i(t), P_i(t))`

where:

- `M_i(t)` is a bounded memory amplitude
- `D_i(t)` is a local mismatch or tension accumulator
- `P_i(t)` is a local phase-memory component

## Intended roles

`M_i(t)`:

- summarizes how strongly past local updates still influence node `i`

`D_i(t)`:

- summarizes how far the present local neighborhood is from recent local history

`P_i(t)`:

- summarizes retained local phase coherence from recent steps

## Layer status

This object is:

- native to QNG
- but still more primitive than any effective field such as `Sigma_effective`

## Hard rule

`H_i(t)` is not the same thing as `tau`.

At most, a future effective lag parameter may be derived from `H_i(t)` after coarse-graining.

## Next use

The first concrete QNG update law will use:

`N_i(t+1) = U(N_i(t), H_i(t), Adj(i,t), Xi_i(t))`

with `H_i(t)` given by this file.
