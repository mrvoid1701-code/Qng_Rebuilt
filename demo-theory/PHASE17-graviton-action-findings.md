# Phase 17 (Gap 12 core) — the graviton action is substrate-derived

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01 — master key substantially advanced`
Probe: `demo-theory/tests/t_phase17_graviton_action_from_substrate.py`
Artifact: `07_validation/audits/demo-phase17-graviton-action-v1/`
Builds on: theory-v2 ch.28 (Einstein eq derivation), Phase 16 (dynamical graviton)

---

## The attack on the master key

The remaining core of Gap 12: derive the graviton action from the substrate.
theory-v2 ch.28 already had the **linearized** piece (v11 graviton action +
coefficient match). Phase 17 (a) **corrects its derivation target** using the
demo edge/node ontology and (b) **quantifies** the substrate-derived coefficient.

## T1 — the coefficient IS substrate-derived (matches GR to ~15%)

The v11 graviton (Fierz-Pauli) action coefficient is fixed by substrate
parameters (DER-QNG-042):

```
   μ_h = β_g · μ_φ / β_φ = 0.35·0.857/0.06 = 5.00   (substrate)
   μ_h = 32π G_QNG       = 32π·0.0583       = 5.86   (linearized-GR match)
   ratio = 0.852  →  agreement to ~15%
```

> The graviton action is **not postulated** — its coefficient is **fixed by
> substrate parameters** (β_g, μ_φ, β_φ), and it matches the value linearized GR
> requires to **~15%** — a parameter-free structural match. The "16πG" coefficient
> itself originates as `z/(16π β_g)` from substrate parameters.

## T3 — the ONTOLOGICAL CORRECTION (the demo contribution)

theory-v2 ch.28 §4.1 aimed to **coarse-grain σ_g (a node scalar) → √(−g)R**. The
demo program shows this target is **wrong for the tensor sector**:

- **DER-QNG-101 (Hodge no-go) + Phase 16:** a node scalar gives only **spin-0**
  (scalar / Newtonian-trace gravity). The **tensor graviton** (TT, gravitational
  waves) is the **EDGE rank-2 object h_ij**, which Phase 16 proved is the
  gauge-invariant, 2-dof dynamical graviton.

> **Corrected split:** σ_g (node scalar) → the **scalar / Newtonian-trace** part
> of gravity; the **EDGE rank-2 h_ij** → the **tensor / TT (gravitational-wave)**
> part. v11's h_ij action IS the edge graviton's action. ch.28's "σ_g → R" was
> conflating the scalar and tensor sectors; the demo ontology separates them.

## Status of the master key (Gap 12) after Phase 17

The graviton-action-from-substrate now has THREE of its pieces in hand:

| Piece | Status | Source |
|---|---|---|
| **FORM** (Fierz-Pauli / linearized Einstein) | ✓ | Phase 16 (works on edge h_ij) |
| **GAUGE INVARIANCE** (diffeomorphism) | ✓ (4.5e-16) | Phase 16 |
| **COEFFICIENT** (μ_h substrate-derived) | ✓ to ~15% | Phase 17 + ch.28 |
| **derivation TARGET** (edge, not σ_g) | ✓ corrected | DER-QNG-101 + Phase 16 |
| exact coefficient (close the 15%) | open | convention / higher-order / Sakharov ~4% |
| **full nonlinear** (edge action → full R_μν) | **open core** | multi-week EFT program |

## Honest scope

- The **linearized** graviton action is substrate-derived (form + gauge +
  coefficient to 15%) — this is real and parameter-free.
- The **15% coefficient gap** is not closed; candidates (ch.28 §6.3): sign/gauge
  conventions, higher-order, the Sakharov-induced ~4% of G. Not resolved here.
- The **full nonlinear** coarse-graining (edge h_ij action → full R_μν[g]) is the
  genuine remaining core — a multi-week EFT derivation, unchanged in difficulty.
- The ontological correction (edge vs σ_g) is the solid new contribution: it
  fixes *what to coarse-grain* (the edge sector for the tensor graviton).

## Bottom line

The master key is **substantially advanced, not turned**: the linearized edge
graviton action is now established to be **substrate-derived in form,
gauge-invariant, and coefficient-matched to GR within ~15%**, with the
derivation target **corrected to the edge sector**. The two genuinely remaining
pieces — closing the 15% and the full nonlinear coarse-graining — are clearly
bounded. This is as far as the master key can be honestly turned without the
multi-week nonlinear EFT program; everything up to the linearized,
substrate-coefficient'd, gauge-invariant edge graviton is in hand.
