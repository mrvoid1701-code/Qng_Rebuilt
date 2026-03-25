# QNG Chi Identification v1

Type: `derivation`
ID: `DER-GOV-002`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Test the legacy claim `chi = m/c` in the rebuilt framework and identify
what `chi` actually tracks among the available proxy fields.

## Inputs

- [qng-covariance-stability-v1.md](qng-covariance-stability-v1.md)
- [qng-light-cone-proxy-v1.md](../04_lorentzian/qng-light-cone-proxy-v1.md)

## The legacy claim

In the old QNG project, `chi` was proposed to encode a mass-to-speed ratio:

`chi(i) ≈ k * m(i) / c`

where `m` is some mass-like quantity and `c` is the speed of light.

In the rebuilt framework, this translates to:

`chi(i) ≈ k * m_eff(i) / c_eff(i)`

where `m_eff` is from the matter proxy and `c_eff` is from the light cone proxy.

## Probe results (default seed 20260325)

Correlations with chi across all available fields:

| Field | corr(chi, field) |
|---|---|
| L_eff | **+0.822** |
| q_src | +0.200 |
| m_eff | +0.191 |
| m/c | +0.190 |
| h_tt | +0.191 |
| kappa | −0.246 |
| h_xx | −0.245 |
| C_eff | −0.124 |
| sigma | +0.094 |
| phi | +0.056 |

`L_eff` is by far the dominant correlate. `m/c` ranks equal with `m_eff`
(since `c_eff ≈ 1`, dividing by it adds nothing).

## Universality probe across 5 seeds

| seed | corr(chi, L_eff) | corr(chi, m/c) |
|---|---|---|
| 20260325 | 0.822 | +0.190 |
| 42 | 0.735 | +0.394 |
| 137 | 0.703 | +0.126 |
| 1729 | 0.653 | −0.118 |
| 2718 | 0.551 | −0.100 |

`corr(chi, L_eff)` is positive and > 0.5 on all seeds.

`corr(chi, m/c)` varies from −0.12 to +0.39 and changes sign.

## Physical interpretation

`chi` is not `m/c`. The legacy claim is falsified at proxy level.

`chi` is the coherence field of the native state. Its dominant correlate
is `L_eff` — the effective Lyapunov/lag field that encodes the
history-accumulated mismatch structure of the substrate.

This makes physical sense: `chi` measures how much a node's dynamics
are coherent with its neighbours, and `L_eff` measures how accumulated
lag/mismatch the node has. Both are memory-driven quantities.

The correct rebuilt identification is:

**`chi ∝ L_eff`** (not `chi = m/c`)

The proportionality constant from the default seed:
`k_chi = sum(chi * L_eff) / sum(L_eff^2) ≈ 0.82 / (std_Leff/std_chi)`

## What this changes

- The claim `chi = m/c` should be retired from the rebuilt workspace
- `chi` should be interpreted as a coherence-memory field, not a mass proxy
- Future claims involving `chi` as a mass carrier should not be made without
  new evidence

## What remains open

- why `L_eff` is the dominant correlate (structural derivation not given)
- whether the proportionality `chi ∝ L_eff` is exact or approximate
- whether there is a dynamical law that enforces this relation
- the physical meaning of `L_eff` beyond the proxy definition
