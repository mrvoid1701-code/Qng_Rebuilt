# 03 — Light Without a Gauge Field: the transverse edge mode

Type: `derivation` / `note`
Status: `Route A FALSIFIED by E5 (2026-06-01) — Route B promoted to primary`
Author: `C.D Gabriel`
Depends on: `02-phase-waves-and-lightcone.md`
Result: see `E5-RESULT-no-go.md`

---

> **⚠ UPDATE 2026-06-01 — E5 AND E7 have run. Both Route A and Route B are
> falsified; Route C (edge gauge field) is the forced answer.**
> - **E5:** Route A (pure scalar `φ`) FALSIFIED — `θ=∇φ` is curl-free, transverse
>   = 0 to machine precision. See `E5-RESULT-no-go.md`.
> - **E7:** Route B (`φ–χ` circulation) FALSIFIED — `χ` is also a node scalar, so
>   `curl(∇χ)=0` identically; no node scalars can source a transverse mode.
>   **But** a fundamental edge-vector field gives the photon exactly (2
>   transverse polarizations at `c_φ`, longitudinal frozen). See
>   `E7-RESULT-edge-photon.md`.
> - **Conclusion:** light is necessarily a **link/edge gauge field** (v12 `A_ij`)
>   — forced, not optional. Synthesis in `07-edges-carry-the-forces.md`.
>
> The Route-A/B analysis below stands as the reasoning that *led* to E5/E7.

---

## 0. The problem we must face honestly

Page 02 gave us a phase wave traveling at `c_φ`. Tempting to call it light. But
**a single scalar phase field cannot be electromagnetic light**, and the reason
is structural, not cosmetic:

- A scalar field `φ(x)` has a gradient `∇φ` that is **longitudinal** — it
  points along the direction of propagation. Compressions and rarefactions of
  phase travel *along* `k`, like **sound**.
- Real EM light is **transverse**: `E ⊥ k`, `B ⊥ k`, and it has **two
  polarizations**. Sound has none of this.

So "phase wave = light" is wrong as stated. A scalar phase wave is the QNG
analog of **sound**, not light. We need transverse structure.

Three routes have been considered. We reject the first two openly and pursue
the third.

- **Route C (rejected): bolt on a U(1) link field `A_ij`.** This is the v12
  move — add an edge-valued gauge field by hand. It *works* (CPU-136 gives a
  spin-1 photon, 2 polarizations), but it is **axiomatic**, not derived, and it
  sits uneasily with the substrate's true symmetry: the vacuum is
  **sine-Gordon with only discrete `Z` winding**, not continuous U(1). The
  "Tesla U(1) on χ" reading was outright **FALSIFIED** (`DER-QNG-044`). We will
  not claim a derived photon by importing the answer.

- **Route B (deferred): coupled φ–χ transverse mode** (the "v13 honest photon"
  direction). Identify `φ` (phase-rate) with an `E`-analog and the
  *circulation* of `χ` with a `B`-analog. This needs a dynamically nonzero
  `curl χ`, which has not been shown. Promising but not ready.

- **Route A (pursued here): light is already inside `φ`, in the edge field.**

## 1. The key move: `φ` lives on nodes, but its differences live on edges

Define the **edge field** — the phase difference across each link:

```
        θ_ij  ≡  φ_i − φ_j          (one number per edge of the graph)
```

On a cubic lattice each node has links in the `x, y, z` directions, so the set
`{θ_ij}` at a node assembles into a **vector**:
`θ⃗ = (θ_x, θ_y, θ_z) ≈ a ∇φ` in the continuum. **The edge field is a vector
field built from the scalar `φ` — no new degree of freedom added.**

This is the whole trick. We did not add a field. We *looked at the same `φ`
through its edges* and found a vector hiding in plain sight.

## 2. Helmholtz decomposition: sound + light

Any vector field splits uniquely (Helmholtz) into a curl-free (longitudinal)
part and a divergence-free (transverse) part:

```
        θ⃗  =  ∇α   +   ∇×Λ⃗
              └ longitudinal ┘   └ transverse ┘
              = the scalar      = the EM-light
                phase wave        candidate
                (page 02, sound)  (circulating, div-free)
```

- The **longitudinal** part `∇α` is exactly the page-02 scalar phase wave. For
  a pure gradient `θ⃗ = ∇φ` this is *all* of it — and indeed a naive `φ` wave is
  pure-longitudinal, which is why it looked like sound.
- The **transverse** part `∇×Λ⃗` is **divergence-free, circulating**. In 3-D a
  transverse vector field has exactly **2 independent polarizations**. *This is
  the structural signature of light.* If it exists and propagates, QNG has a
  photon **with no gauge field** — just the transverse sector of `θ_ij`, which
  the sine-Gordon `Z` vacuum has no reason to forbid.

## 3. The make-or-break question (→ Experiment E5)

For a *pure gradient* `θ⃗ = ∇φ`, the transverse part is identically zero — there
is no light. So the entire honest-photon program hinges on one question:

> **Does the substrate's dynamics ever generate, and then propagate, a
> transverse (`∇·θ⃗ = 0`, circulating) edge configuration — or is the
> transverse sector frozen / pure-gauge?**

Two possible outcomes:

1. **Transverse branch propagates** at its own dispersion (ideally at `c_φ`,
   matching the longitudinal cone). Then QNG hosts a genuine photon: 2
   polarizations, light-speed, from `φ` alone. **This is the prize.**
2. **Transverse branch is non-dynamical** (frozen, or pure-gauge with zero
   restoring force). Then `φ` alone gives only sound, and a real photon needs
   Route B (the φ–χ circulation coupling) or a genuine new field.

**Experiment E5** (see `06-experiments.md`) decides this directly:
Helmholtz-decompose `θ_ij` on the lattice, initialize a *purely transverse*
configuration, evolve under the v8 symplectic integrator, and watch whether the
transverse energy propagates at `c_φ` with 2 polarizations.

## 4. Why this would matter

If E5 passes, the picture unifies beautifully:

- **Sound = longitudinal `θ⃗`** = the scalar phase wave (page 02).
- **Light = transverse `θ⃗`** = the circulating phase wave (this page).
- Both ride the **same lightcone** `c_φ` (page 02), so light and the scalar
  sector are automatically causally consistent.
- **No symmetry was added.** The Z-winding sine-Gordon vacuum is untouched. The
  photon was always implicit in the difference of node phases — we just had to
  decompose it.

And it would explain why the v12 axiomatic `A_ij` *worked* even though it was
bolted on: `A_ij` and `θ_ij` live on the same edges. v12 may have been
re-discovering the transverse `θ_ij` sector through a gauge-field disguise.

## 5. Honesty contract for this page

- **Do NOT** write "QNG derives the photon" or "light is derived" anywhere
  until **E5 passes**. Until then the status is `candidate / gated`.
- Route C (`A_ij`) remains available as an **axiomatic** fallback, clearly
  labeled as such, exactly as in v12.
- The transverse-sector idea is **new and untested in this substrate.** Its
  appeal (no new field, 2 polarizations, vacuum-compatible) is a reason to run
  E5, not a reason to believe it yet.

## 6. What we have after page 03

- A scalar phase wave is **longitudinal = sound**, not light. Structural fact.
- The **edge field `θ_ij = φ_i − φ_j` is a vector** built from `φ` with no new
  d.o.f.; Helmholtz-split into longitudinal (sound) + **transverse (light
  candidate, 2 polarizations)**.
- Whether the transverse branch **propagates** is the open, decisive question —
  **Experiment E5**. Pass ⟹ honest photon from `φ` alone; fail ⟹ Route B or new
  field.

**Next** (`04`): assume light exists and ask the big question — *why is light
exactly the object that bridges GR and QM?*
