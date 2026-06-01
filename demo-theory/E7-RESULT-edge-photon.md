# E7 RESULT — the photon is forced to be an edge field

Type: `evidence`
Status: `RUN COMPLETE 2026-06-01 — verdict ROUTE_B_FAILS_NODE_SCALARS / EDGE_PHOTON_FORCED`
Author: `C.D Gabriel`
Probe: `demo-theory/tests/e7_phi_chi_photon_probe.py`
Artifact: `07_validation/audits/demo-e7-phi-chi-photon-v1/report.json`
Gates: Route B ("φ–χ circulation photon") from `E5-RESULT-no-go.md`

---

## What E7 asked

E5 showed a single scalar `φ` cannot host light. Route B proposed a **second**
field `χ`, with "circulation of `χ`" as the magnetic-analog. E7 tests this
directly — and, since `χ` is *also* a per-node scalar, also asks the deeper
question: **what is the minimal structure that CAN carry light?**

## What E7 found

| Test | Quantity | Result | Reading |
|---|---|---|---|
| **E7a** node scalars φ,χ | `max\|curl(∇φ)\|` | **2.2×10⁻¹⁶** | machine zero — `curl(grad)=0` (Hodge `d∘d=0`) |
| **E7a** node scalars φ,χ | `max\|curl(∇χ)\|` | **2.2×10⁻¹⁶** | χ cannot be a B-analog |
| **E7a** coupled evolution | sustained transverse fraction | **7.4×10⁻³²** | no coupling of two scalars sources transverse |
| **E7b** edge vector field | transverse pol 1 (ẑ), pol 2 (ŷ) | **ω = 0.157 each (equal)** | 2 degenerate propagating polarizations |
| **E7b** edge vector field | longitudinal pol (x̂) | **ω = 0 (frozen)** | longitudinal non-propagating (Gauss) |

*(c_meas ≈ 0.30 vs c_φ = 0.265: the offset is FFT frequency-bin resolution
≈ 0.05 over the 120-lu window; the load-bearing facts — the two transverse
modes being **exactly equal** and the longitudinal being **exactly frozen** —
are resolution-independent.)*

## Verdict: **ROUTE_B_FAILS_NODE_SCALARS / EDGE_PHOTON_FORCED**

> **`χ` is a node scalar, so `curl(∇χ) = 0` identically** — it cannot be the
> magnetic analog, and no coupling of two node scalars ever sources a sustained
> transverse mode (E7a, machine precision). **But a fundamental edge-vector
> field `A` — a link/gauge degree of freedom that is NOT the gradient of any
> node scalar — reproduces the photon exactly**: under Maxwell dynamics
> `∂²_t A = −c² ∇×∇×A` it carries **two transverse polarizations** propagating
> at `c_φ` and a **frozen longitudinal mode** (E7b).
>
> **Conclusion: the v12 edge gauge field `A_ij` is not an arbitrary bolt-on. It
> is the MINIMAL and FORCED carrier of light in a node-scalar substrate. Light
> is necessarily a link (edge) degree of freedom.**

## Why this is the deep result, not a disappointment

E5 + E7 together prove a clean structural theorem about QNG:

```
   node scalars (σ_g, σ_m, χ, φ)         edges / links
   ──────────────────────────────        ─────────────────────────────
   carry: density, matter, phase         carry: GAUGE structure
   give:  only longitudinal modes        give:  transverse waves
          (sound, Goldstone)                    (photon: 2 polarizations)
   curl(∇·) = 0  -> NO light             curl A != 0  -> light EXISTS
```

The transversality of light is a **geometric (Hodge) fact**, not a dynamical
one. You cannot manufacture a divergence-free (transverse) vector from the
gradient of any number of node scalars. The carrier of light must be an
**independent 1-form living on the edges** — which is exactly a gauge field.

## This unifies three previously-separate QNG findings

| Finding | Statement | Same lesson |
|---|---|---|
| **E5** (this thread) | scalar φ → no transverse photon | node scalar insufficient |
| **E7** (this thread) | NO node scalars → photon; edge vector → photon | **forced edge d.o.f.** |
| **Gap 12** (main theory) | scalar `σ_g` → spin-0, not spin-2 graviton | needs rank-2 **edge** primitive |
| **ℏ-edge program** | scalar edges "structurally insufficient" | structure lives on edges |

**Unified ontological statement (new):** in QNG the **matter/phase content lives
on nodes (scalars)**, but the **force carriers live on edges**: spin-1 light as
an edge **vector** (`A_ij`, v12 — now *forced*, not optional), and spin-2 gravity
tensor modes as an edge **rank-2** object (Gap 12 — the same logic, one rank
higher). This is the substrate's division of labor.

## Status updates triggered by this result

- `03-light-without-a-gauge-field.md`: Route B → **FALSIFIED for node-scalar χ**;
  Route C (edge gauge field) → **the answer, and it is forced.**
- v12's `A_ij` is **promoted in interpretation** from "axiomatic bolt-on" to
  "minimal structure forced by the Hodge/counting theorem." (Still axiomatic in
  the sense that the edge field is a *primitive*, but no longer arbitrary.)
- New synthesis page `07-edges-carry-the-forces.md`.

## Honest scope

- "Forced" means: *given* that QNG's node fields are all scalars, light must be
  an edge vector. It does **not** derive *why* the substrate has the particular
  gauge group / coupling `e` (that remains Gap 17, `α_fine` is an input — same
  status as QED).
- E7b used the clean Maxwell wave operator to demonstrate the *kinematics* (2
  transverse + frozen longitudinal). It confirms an edge vector field *can* be
  the photon; pinning down how `A_ij` couples to the matter rings (the `q = N·e`
  Wilson-loop charge of v12) is the next constructive step, not re-opened here.
