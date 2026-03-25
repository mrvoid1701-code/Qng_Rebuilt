# QNG Tau Identification v1

Type: `derivation`
ID: `DER-GOV-003`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test the legacy claim that a universal scalar `tau` governs the QNG
substrate, and identify what per-node effective timescale emerges from
the rebuilt dynamics.

## Inputs

- [qng-chi-identification-v1.md](qng-chi-identification-v1.md)
- [qng-covariance-stability-v1.md](qng-covariance-stability-v1.md)

## The legacy claim

The old project proposed a universal `tau` — a single timescale
governing memory, lag, and phenomenological delays throughout the theory.

In the rebuilt framework, `tau` would need to satisfy:

`tau = tau_p = tau_m = tau_d`

where:
- `tau_p = 1/hist_p_rate` — phase memory timescale
- `tau_m = 1/hist_m_rate` — magnitude memory timescale
- `tau_d = 1/hist_d_rate` — differential memory timescale

## Config-level falsification

The three timescales from the default config:

- `tau_p = 1/0.35 = 2.857 steps`
- `tau_m = 1/0.30 = 3.333 steps`
- `tau_d = 1/0.25 = 4.000 steps`

Coefficient of variation: `cv = 0.169`

The three timescales differ by 40% (range 2.86–4.00). A universal
scalar tau is not supported even at the config level.

## Per-node timescale proxy

Define the per-node effective timescale:

`tau_eff(i) = L_eff(i) / C_eff(i)`

where `C_eff` is the coherence field and `L_eff` is the lag/mismatch
accumulation field. Since `C_eff` scales the node's coupling strength
and `L_eff` accumulates temporal mismatch, their ratio is a natural
effective relaxation time.

## Probe results across 5 seeds

| seed | mean(tau_hist) | mean(tau_nohist) | ratio | corr(tau, mem) |
|---|---|---|---|---|
| 20260325 | 0.107 | 0.035 | 3.05x | 0.833 |
| 42 | 0.117 | 0.044 | 2.64x | 0.682 |
| 137 | 0.099 | 0.023 | 4.25x | 0.830 |
| 1729 | 0.099 | 0.022 | 4.62x | 0.715 |
| 2718 | 0.102 | 0.026 | 3.91x | 0.767 |

Key observations:

1. History amplifies mean(tau) by factor 2.6x–4.6x
2. `corr(tau_eff, mem) > 0.68` on all seeds — tau tracks memory accumulation
3. `mean(tau_hist)` is relatively stable: range [0.099, 0.117], cv ≈ 7%
4. Per-node cv is 11–17% — tau is NOT constant across nodes

## Physical interpretation

The universal scalar `tau` is falsified at proxy level:

- Config timescales are not equal (cv = 0.169)
- Per-node timescale varies across nodes (cv = 11–17%)

The correct rebuilt identification:

**`tau_eff(i) = L_eff(i) / C_eff(i)`** — a per-node relaxation timescale
driven by the history sector. Memory triples the effective timescale.
The dominant correlate is the magnitude memory field `mem`.

`tau` should be treated as a **per-node history-driven field**, not a
universal scalar.

## What remains open

- dynamical law that determines tau_eff
- whether a universal tau emerges in a continuum or large-N limit
- connection between tau_eff and phenomenological delay observations
- why phase memory decays faster than magnitude/differential memory
