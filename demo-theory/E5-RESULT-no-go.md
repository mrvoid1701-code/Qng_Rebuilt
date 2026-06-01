# E5 RESULT — Route A no-go: no propagating photon from φ alone

Type: `evidence`
Status: `RUN COMPLETE 2026-06-01 — verdict ROUTE_A_INSUFFICIENT`
Author: `C.D Gabriel`
Probe: `demo-theory/tests/e5_transverse_light_probe.py`
Artifact: `07_validation/audits/demo-e5-transverse-light-v1/report.json`
Gates: the claim in `03-light-without-a-gauge-field.md` ("light from φ alone")

---

## What E5 asked

Page `03` proposed **Route A**: light = the *transverse* part of the edge field
`θ_ij = φ_i − φ_j`, with no bolted-on gauge field. E5 was declared make-or-break:
*does the transverse sector propagate at `c_φ` with 2 polarizations?*

## What E5 found

| Test | Quantity | Result | Reading |
|---|---|---|---|
| **E5a** smooth single-valued φ | transverse fraction | **9.4×10⁻³²** | machine zero — `θ=∇φ` is purely longitudinal, *exactly* |
| **E5b** vortex line (winding 2π) | transverse fraction | **0.256** | topology *does* create transverse content (holonomy = real curl) |
| **E5c** evolve + transverse kick | rms-radius growth / `c_φ` | **−0.30** | transverse content does **not** radiate; it collapses to ~0 after one sample step |

Reference `c_φ`: measured 0.303 vs small-`k` theory 0.265 (finite-`k` lattice
dispersion; consistent).

## Verdict: **ROUTE_A_INSUFFICIENT**

> **A single scalar phase field `φ` cannot host a propagating transverse
> photon.** For single-valued `φ`, the edge vector `θ⃗ = ∇φ` is curl-free by
> construction (`d∘d = 0`), so the transverse sector is identically zero
> (E5a, machine precision). Topological winding creates a transverse component
> (E5b, 25.6%), but it is **bound to the defect and not dynamically sustained**
> — under φ-evolution the transverse energy collapses to ~10⁻⁷ within one
> sampling interval (E5c). There is no second, freely-propagating transverse
> mode.

## Why this is the *expected* answer (counting argument)

This is not a numerical accident — it is a theorem the simulation merely
confirms:

- A scalar field has **one** field component → **one** propagating mode
  (longitudinal). EM light needs **two transverse** polarizations.
- You cannot extract two independent dynamical polarizations from one scalar
  d.o.f. The "vector" `θ⃗` looks like it has 3 components, but they are all
  slaved to the single `φ` (`θ̂ ∝ D(k)·φ̂` exactly).
- By Hodge decomposition a 1-form `= dα + δβ + harmonic`; `θ = dφ` is *purely*
  the `dα` (exact/longitudinal) piece. The `δβ` (co-exact/transverse) piece
  requires an **independent edge 1-form** that is not `dφ`.

## This mirrors two earlier QNG findings

Route A's failure is the *same structural lesson* the main theory hit twice:

- **Gap 12 (tensor graviton):** a per-node *scalar* `σ_g` gives a spin-0 quantum,
  not the spin-2 graviton; a genuine tensor mode needs a **rank-2 edge
  primitive**.
- **ℏ-edge program:** scalar edges were "structurally insufficient"; the missing
  ingredient was operator/edge structure, not a noise mechanism.

In all three cases: **scalar node fields are not enough; the missing physics
lives on the edges as an independent (vector/tensor) object.**

## Where light actually has to come from

E5 redirects the program cleanly. A genuine photon needs a **second dynamical
edge degree of freedom**:

- **Route B (now promoted to primary):** a coupled **φ–χ transverse mode**.
  Identify `φ` (phase-rate) as an `E`-analog and the **circulation of χ**
  (`∇×χ⃗ ≠ 0`) as a `B`-analog. χ is a *second* field, so it can carry the
  transverse polarizations that φ cannot. **Next test: E7** — does the substrate
  dynamically generate `curl χ ≠ 0`, and does a coupled φ–χ transverse wave
  propagate at `c_φ` with 2 polarizations?
- **Route C (axiomatic fallback):** re-add the v12 edge gauge field `A_ij`.
  Honest but bolted-on; keep labeled as an axiom, not a derivation.

## Status updates triggered by this result

- `03-light-without-a-gauge-field.md`: Route A status → **`FALSIFIED for pure
  scalar φ (E5)`**. Route B → **primary path**.
- `README.md` honesty contract: the E5 gate is now **closed for Route A**; the
  "no derived-photon claim" lock transfers to **E7** (Route B).
- No claim of a derived photon is made. QNG still has only the **axiomatic** v12
  photon until E7 (or a successor) passes.

## Honest scope

- E5c used a scalar velocity "kick," which is itself longitudinal; it cannot
  *create* transverse content, only probe whether existing (vortex) transverse
  content is sustained. The decisive evidence is **E5a (machine-zero) + the
  counting argument**, which are dynamics-independent. E5c is corroboration.
- The result says *"not from φ alone,"* **not** *"QNG has no photon."* Route B
  is open and, on the two-ledger logic of page `04`, well-motivated.
